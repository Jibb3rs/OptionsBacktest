"""
Iron Condor Strategy Implementation
Handles entry, exit, and position management for Iron Condor trades
"""

from datetime import datetime, timedelta

class IronCondorStrategy:
    """
    Iron Condor: Sell OTM put spread + Sell OTM call spread
    Max profit = Net credit received
    Max loss = Width of wider spread - Net credit
    """
    
    def __init__(self, algorithm):
        """
        Initialize Iron Condor strategy
        
        Args:
            algorithm: QCAlgorithm instance
        """
        self.algo = algorithm
        self.positions = {}  # Track open positions
        self.position_id = 0
    
    def enter_trade(self, strikes, underlying_price):
        """
        Enter Iron Condor position
        
        Args:
            strikes: Dict with 4 selected strikes
            underlying_price: Current underlying price
            
        Returns:
            Position ID if successful, None otherwise
        """
        
        self.algo.Log("\n" + "="*60)
        self.algo.Log("🚀 ENTERING IRON CONDOR")
        self.algo.Log("="*60)
        
        # Calculate position metrics
        metrics = self.calculate_metrics(strikes)
        
        if not metrics:
            self.algo.Log("❌ Could not calculate metrics")
            return None
        
        # Log trade details
        self.log_entry_details(strikes, metrics, underlying_price)
        
        # Place orders (1 contract each leg for simplicity)
        quantity = 1
        
        try:
            # Sell put spread (credit)
            self.algo.MarketOrder(strikes['short_put'].Symbol, -quantity)  # Sell
            self.algo.MarketOrder(strikes['long_put'].Symbol, quantity)    # Buy
            
            # Sell call spread (credit)
            self.algo.MarketOrder(strikes['short_call'].Symbol, -quantity)  # Sell
            self.algo.MarketOrder(strikes['long_call'].Symbol, quantity)    # Buy
            
            self.algo.Log("✅ Orders placed successfully")
            
        except Exception as e:
            self.algo.Log(f"❌ Order placement failed: {e}")
            return None
        
        # Create position tracking
        self.position_id += 1
        position = {
            'id': self.position_id,
            'entry_time': self.algo.Time,
            'entry_price': underlying_price,
            'strikes': strikes,
            'metrics': metrics,
            'quantity': quantity,
            'status': 'open',
            'mae': 0,  # Maximum Adverse Excursion
            'mfe': 0,  # Maximum Favorable Excursion
            'current_pnl': 0,
            'exit_reason': None
        }
        
        self.positions[self.position_id] = position
        
        self.algo.Log(f"📊 Position #{self.position_id} opened")
        self.algo.Log("="*60 + "\n")
        
        return self.position_id
    
    def calculate_metrics(self, strikes):
        """Calculate Iron Condor metrics"""
        
        try:
            # Get mid prices (average of bid/ask)
            short_put_price = (strikes['short_put'].BidPrice + strikes['short_put'].AskPrice) / 2
            long_put_price = (strikes['long_put'].BidPrice + strikes['long_put'].AskPrice) / 2
            short_call_price = (strikes['short_call'].BidPrice + strikes['short_call'].AskPrice) / 2
            long_call_price = (strikes['long_call'].BidPrice + strikes['long_call'].AskPrice) / 2
            
            # Net credit received (what we collect)
            net_credit = (short_put_price - long_put_price + 
                         short_call_price - long_call_price)
            
            # Spread widths
            put_width = strikes['short_put'].Strike - strikes['long_put'].Strike
            call_width = strikes['long_call'].Strike - strikes['short_call'].Strike
            
            # Max loss (widest spread minus credit)
            max_loss_put = put_width - net_credit
            max_loss_call = call_width - net_credit
            max_loss = max(max_loss_put, max_loss_call)
            
            # Max profit is the credit
            max_profit = net_credit
            
            # Breakevens
            lower_breakeven = strikes['short_put'].Strike - net_credit
            upper_breakeven = strikes['short_call'].Strike + net_credit
            
            # Risk/Reward ratio
            risk_reward = max_profit / max_loss if max_loss > 0 else 0
            
            return {
                'max_profit': max_profit * 100,  # Convert to dollars (x100 multiplier)
                'max_loss': max_loss * 100,
                'net_credit': net_credit * 100,
                'put_width': put_width,
                'call_width': call_width,
                'lower_breakeven': lower_breakeven,
                'upper_breakeven': upper_breakeven,
                'risk_reward': risk_reward,
                'entry_prices': {
                    'short_put': short_put_price,
                    'long_put': long_put_price,
                    'short_call': short_call_price,
                    'long_call': long_call_price
                }
            }
            
        except Exception as e:
            self.algo.Log(f"❌ Error calculating metrics: {e}")
            return None
    
    def update_positions(self, data, underlying_price):
        """
        Update all open positions - check exits and track MAE/MFE
        
        Args:
            data: Current market data
            underlying_price: Current underlying price
        """
        
        for pos_id, position in list(self.positions.items()):
            if position['status'] != 'open':
                continue
            
            # Calculate current P&L
            current_pnl = self.calculate_current_pnl(position, data)
            position['current_pnl'] = current_pnl
            
            # Update MAE (worst unrealized loss)
            if current_pnl < position['mae']:
                position['mae'] = current_pnl
            
            # Update MFE (best unrealized profit)
            if current_pnl > position['mfe']:
                position['mfe'] = current_pnl
            
            # Check exit conditions
            exit_reason = self.check_exit_conditions(position, underlying_price)
            
            if exit_reason:
                self.exit_position(pos_id, exit_reason, current_pnl)
    
    def calculate_current_pnl(self, position, data):
        """
        Calculate current unrealized P&L for position
        
        Args:
            position: Position dict
            data: Current market data
            
        Returns:
            Current P&L (positive = profit, negative = loss)
        """
        
        try:
            strikes = position['strikes']
            quantity = position['quantity']
            
            # Get current prices
            short_put_current = (strikes['short_put'].BidPrice + strikes['short_put'].AskPrice) / 2
            long_put_current = (strikes['long_put'].BidPrice + strikes['long_put'].AskPrice) / 2
            short_call_current = (strikes['short_call'].BidPrice + strikes['short_call'].AskPrice) / 2
            long_call_current = (strikes['long_call'].BidPrice + strikes['long_call'].AskPrice) / 2
            
            # Current value of spreads (what it would cost to close)
            current_value = (short_put_current - long_put_current + 
                           short_call_current - long_call_current)
            
            # Entry credit
            entry_credit = position['metrics']['net_credit'] / 100  # Convert back from dollars
            
            # P&L = Entry credit - Current value (we want value to decrease)
            pnl = (entry_credit - current_value) * 100 * quantity
            
            return pnl
            
        except Exception as e:
            self.algo.Log(f"⚠️  Error calculating P&L: {e}")
            return 0
    
    def check_exit_conditions(self, position, underlying_price):
        """
        Check if position should be exited
        
        Args:
            position: Position dict
            underlying_price: Current underlying price
            
        Returns:
            Exit reason string or None
        """
        
        current_pnl = position['current_pnl']
        max_profit = position['metrics']['max_profit']
        max_loss = position['metrics']['max_loss']
        
        # Profit target: 50% of max profit
        profit_target = max_profit * 0.50
        if current_pnl >= profit_target:
            return 'profit_target'
        
        # Stop loss: 200% of max profit (2x the credit received)
        stop_loss = max_profit * -2.0
        if current_pnl <= stop_loss:
            return 'stop_loss'
        
        # Check if near expiration (within 1 day)
        time_to_expiry = position['strikes']['short_put'].Expiry - self.algo.Time
        if time_to_expiry.days <= 0:
            return 'expiration'
        
        # Breakeven breach check
        lower_be = position['metrics']['lower_breakeven']
        upper_be = position['metrics']['upper_breakeven']
        
        if underlying_price <= lower_be:
            return 'lower_breakeven_breach'
        
        if underlying_price >= upper_be:
            return 'upper_breakeven_breach'
        
        return None
    
    def exit_position(self, pos_id, reason, final_pnl):
        """
        Close position
        
        Args:
            pos_id: Position ID
            reason: Exit reason
            final_pnl: Final P&L
        """
        
        position = self.positions[pos_id]
        strikes = position['strikes']
        quantity = position['quantity']
        
        self.algo.Log("\n" + "="*60)
        self.algo.Log(f"🏁 EXITING POSITION #{pos_id}")
        self.algo.Log(f"   Reason: {reason}")
        self.algo.Log("="*60)
        
        try:
            # Close all legs (reverse the entry)
            self.algo.MarketOrder(strikes['short_put'].Symbol, quantity)   # Buy back
            self.algo.MarketOrder(strikes['long_put'].Symbol, -quantity)   # Sell
            self.algo.MarketOrder(strikes['short_call'].Symbol, quantity)  # Buy back
            self.algo.MarketOrder(strikes['long_call'].Symbol, -quantity)  # Sell
            
            self.algo.Log("✅ Exit orders placed")
            
        except Exception as e:
            self.algo.Log(f"❌ Exit failed: {e}")
        
        # Update position status
        position['status'] = 'closed'
        position['exit_time'] = self.algo.Time
        position['exit_reason'] = reason
        position['final_pnl'] = final_pnl
        
        # Calculate MAE/MFE as percentages
        max_profit = position['metrics']['max_profit']
        max_loss = position['metrics']['max_loss']
        
        mae_pct = (position['mae'] / max_loss * 100) if max_loss != 0 else 0
        mfe_pct = (position['mfe'] / max_profit * 100) if max_profit != 0 else 0
        
        # Log summary
        self.log_exit_summary(position, mae_pct, mfe_pct)
        
        self.algo.Log("="*60 + "\n")
    
    def log_entry_details(self, strikes, metrics, underlying_price):
        """Log detailed entry information"""
        
        self.algo.Log(f"📍 Underlying: ${underlying_price:.2f}")
        self.algo.Log("")
        self.algo.Log("PUT SPREAD:")
        self.algo.Log(f"   Sell ${strikes['short_put'].Strike} put @ ${metrics['entry_prices']['short_put']:.2f}")
        self.algo.Log(f"   Buy  ${strikes['long_put'].Strike} put @ ${metrics['entry_prices']['long_put']:.2f}")
        self.algo.Log("")
        self.algo.Log("CALL SPREAD:")
        self.algo.Log(f"   Sell ${strikes['short_call'].Strike} call @ ${metrics['entry_prices']['short_call']:.2f}")
        self.algo.Log(f"   Buy  ${strikes['long_call'].Strike} call @ ${metrics['entry_prices']['long_call']:.2f}")
        self.algo.Log("")
        self.algo.Log("POSITION METRICS:")
        self.algo.Log(f"   Net Credit: ${metrics['net_credit']:.2f}")
        self.algo.Log(f"   Max Profit: ${metrics['max_profit']:.2f}")
        self.algo.Log(f"   Max Loss: ${metrics['max_loss']:.2f}")
        self.algo.Log(f"   Risk/Reward: 1:{metrics['risk_reward']:.2f}")
        self.algo.Log(f"   Breakevens: ${metrics['lower_breakeven']:.2f} - ${metrics['upper_breakeven']:.2f}")
    
    def log_exit_summary(self, position, mae_pct, mfe_pct):
        """Log exit summary with MAE/MFE"""
        
        duration = position['exit_time'] - position['entry_time']
        
        self.algo.Log("POSITION SUMMARY:")
        self.algo.Log(f"   Entry: {position['entry_time']}")
        self.algo.Log(f"   Exit: {position['exit_time']}")
        self.algo.Log(f"   Duration: {duration.days} days")
        self.algo.Log("")
        self.algo.Log(f"   Final P&L: ${position['final_pnl']:.2f}")
        self.algo.Log(f"   Max Profit Possible: ${position['metrics']['max_profit']:.2f}")
        self.algo.Log(f"   Max Loss Possible: ${position['metrics']['max_loss']:.2f}")
        self.algo.Log("")
        self.algo.Log(f"   MAE: ${position['mae']:.2f} ({mae_pct:.1f}% of max loss)")
        self.algo.Log(f"   MFE: ${position['mfe']:.2f} ({mfe_pct:.1f}% of max profit)")