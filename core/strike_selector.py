"""
Strike Selector - Delta-Based Strike Selection
Finds option contracts matching target delta values
"""

class StrikeSelector:
    """
    Selects option strikes based on delta values
    Delta represents probability of expiring ITM
    """
    
    def __init__(self, algorithm):
        """ 
        Initialize strike selector
        
        Args:
            algorithm: QCAlgorithm instance
        """
        self.algo = algorithm
    
    def find_strikes_by_delta(self, option_chain, target_deltas, underlying_price):
        """
        Find strikes matching target delta values
        
        Args:
            option_chain: List of option contracts
            target_deltas: Dict with keys: short_put, long_put, short_call, long_call
            underlying_price: Current price of underlying
            
        Returns:
            Dict with selected contracts or None if not found
        """
        
        # Separate puts and calls
        puts = [c for c in option_chain if c.Right == 0]  # 0 = Put
        calls = [c for c in option_chain if c.Right == 1]  # 1 = Call
        
        if not puts or not calls:
            self.algo.Log("⚠️  No puts or calls available")
            return None
        
        # Find strikes for each leg
        selected = {}
        
        # SHORT PUT (sell higher strike put)
        short_put = self.find_closest_delta(
            puts, 
            target_deltas.get('short_put', 0.16),
            'put'
        )
        
        # LONG PUT (buy lower strike put for protection)
        long_put = self.find_closest_delta(
            puts,
            target_deltas.get('long_put', 0.08),
            'put'
        )
        
        # SHORT CALL (sell lower strike call)
        short_call = self.find_closest_delta(
            calls,
            abs(target_deltas.get('short_call', -0.16)),  # Make positive for comparison
            'call'
        )
        
        # LONG CALL (buy higher strike call for protection)
        long_call = self.find_closest_delta(
            calls,
            abs(target_deltas.get('long_call', -0.08)),
            'call'
        )
        
        # Validate all found
        if not all([short_put, long_put, short_call, long_call]):
            self.algo.Log("⚠️  Could not find all 4 strikes")
            return None
        
        # Validate strike ordering
        if not self.validate_iron_condor_strikes(short_put, long_put, short_call, long_call):
            return None
        
        selected = {
            'short_put': short_put,
            'long_put': long_put,
            'short_call': short_call,
            'long_call': long_call
        }
        
        # Log selection
        self.log_selected_strikes(selected, underlying_price)
        
        return selected
    
    def find_closest_delta(self, contracts, target_delta, option_type):
        """
        Find contract with delta closest to target
        
        Args:
            contracts: List of option contracts
            target_delta: Target delta value (absolute)
            option_type: 'put' or 'call'
            
        Returns:
            Contract with closest delta or None
        """
        
        if not contracts:
            return None
        
        closest = None
        min_diff = float('inf')
        
        for contract in contracts:
            # Get Greeks
            if not contract.Greeks or not contract.Greeks.Delta:
                continue
            
            delta = abs(contract.Greeks.Delta)
            diff = abs(delta - target_delta)
            
            if diff < min_diff:
                min_diff = diff
                closest = contract
        
        return closest
    
    def validate_iron_condor_strikes(self, short_put, long_put, short_call, long_call):
        """
        Validate Iron Condor strike ordering
        
        Should be: long_put < short_put < short_call < long_call
        
        Returns:
            True if valid, False otherwise
        """
        
        strikes = {
            'long_put': long_put.Strike,
            'short_put': short_put.Strike,
            'short_call': short_call.Strike,
            'long_call': long_call.Strike
        }
        
        # Check ordering
        if not (strikes['long_put'] < strikes['short_put'] < 
                strikes['short_call'] < strikes['long_call']):
            self.algo.Log("❌ Invalid strike ordering:")
            self.algo.Log(f"   Long Put: {strikes['long_put']}")
            self.algo.Log(f"   Short Put: {strikes['short_put']}")
            self.algo.Log(f"   Short Call: {strikes['short_call']}")
            self.algo.Log(f"   Long Call: {strikes['long_call']}")
            return False
        
        return True
    
    def log_selected_strikes(self, strikes, underlying_price):
        """Log selected strikes with details"""
        
        self.algo.Log("="*60)
        self.algo.Log("✅ STRIKES SELECTED:")
        self.algo.Log(f"   Underlying: ${underlying_price:.2f}")
        self.algo.Log("")
        
        # Put spread
        short_put = strikes['short_put']
        long_put = strikes['long_put']
        put_width = short_put.Strike - long_put.Strike
        
        self.algo.Log("PUT SPREAD:")
        self.algo.Log(f"   Sell: ${short_put.Strike} put (Δ={short_put.Greeks.Delta:.3f})")
        self.algo.Log(f"   Buy:  ${long_put.Strike} put (Δ={long_put.Greeks.Delta:.3f})")
        self.algo.Log(f"   Width: ${put_width}")
        self.algo.Log("")
        
        # Call spread
        short_call = strikes['short_call']
        long_call = strikes['long_call']
        call_width = long_call.Strike - short_call.Strike
        
        self.algo.Log("CALL SPREAD:")
        self.algo.Log(f"   Sell: ${short_call.Strike} call (Δ={short_call.Greeks.Delta:.3f})")
        self.algo.Log(f"   Buy:  ${long_call.Strike} call (Δ={long_call.Greeks.Delta:.3f})")
        self.algo.Log(f"   Width: ${call_width}")
        self.algo.Log("="*60)
    
    def calculate_iron_condor_metrics(self, strikes):
        """
        Calculate max profit, max loss, breakevens for Iron Condor
        
        Args:
            strikes: Dict with all 4 strikes
            
        Returns:
            Dict with metrics
        """
        
        # Get prices
        short_put_credit = strikes['short_put'].BidPrice
        long_put_cost = strikes['long_put'].AskPrice
        short_call_credit = strikes['short_call'].BidPrice
        long_call_cost = strikes['long_call'].AskPrice
        
        # Net credit received
        net_credit = (short_put_credit - long_put_cost + 
                     short_call_credit - long_call_cost)
        
        # Spread widths
        put_width = strikes['short_put'].Strike - strikes['long_put'].Strike
        call_width = strikes['long_call'].Strike - strikes['short_call'].Strike
        
        # Max loss is widest spread minus credit
        max_loss_put = put_width - net_credit
        max_loss_call = call_width - net_credit
        max_loss = max(max_loss_put, max_loss_call)
        
        # Max profit is the credit
        max_profit = net_credit
        
        # Breakevens
        lower_breakeven = strikes['short_put'].Strike - net_credit
        upper_breakeven = strikes['short_call'].Strike + net_credit
        
        return {
            'max_profit': max_profit,
            'max_loss': max_loss,
            'net_credit': net_credit,
            'put_width': put_width,
            'call_width': call_width,
            'lower_breakeven': lower_breakeven,
            'upper_breakeven': upper_breakeven,
            'profit_probability': None  # Will calculate based on delta
        }