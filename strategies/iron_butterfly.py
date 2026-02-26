"""
Iron Butterfly Strategy
Sell ATM put + ATM call with OTM protection wings
"""

from .base_strategy import BaseStrategy

class IronButterfly(BaseStrategy):
    """Iron Butterfly - Narrow body ATM strategy"""

    strategy_direction = 'neutral'  # Strategy expects neutral/range-bound conditions

    @staticmethod
    def generate_code(config):
        """Generate complete Iron Butterfly algorithm for QuantConnect"""
        
        # Extract nested config safely
        trading_rules = config.get('trading_rules', {})
        strike_selection = config.get('strike_selection', {})
        indicators_config = config.get('indicators', {})
        advanced_config = config.get('advanced', {})
        
        # Map stop loss mode
        stop_loss_mode = trading_rules.get('stop_loss_mode', 'credit')
        stop_loss_map = {
            'Credit-Based (Options Standard)': 'credit',
            'Max Loss-Based (Conservative)': 'max_loss',
            'Equal Dollar (Balanced)': 'equal_dollar',
            'Price Distance (FX Style)': 'price_distance',
            'credit': 'credit',
            'max_loss': 'max_loss',
            'equal_dollar': 'equal_dollar',
            'price_distance': 'price_distance'
        }
        stop_loss_mode = stop_loss_map.get(stop_loss_mode, 'credit')
        
        # Build configuration JSON
        config_json = IronButterfly._build_config_json(config, stop_loss_mode, advanced_config)
        
        # Build flattened config
        flat_config = {
            'ticker': config.get('ticker', 'SPY'),
            'start_date': config.get('start_date'),
            'end_date': config.get('end_date'),
            'initial_capital': config.get('initial_capital', 100000),
            'expiry_days': config.get('expiry_days', 30),
            'expiry_range': config.get('expiry_range', 5),
            'resolution': trading_rules.get('resolution', 'Daily'),
            'max_positions': trading_rules.get('max_positions', 5),
            'min_days_between_trades': trading_rules.get('min_days_between_trades', 0),
            'profit_target_pct': trading_rules.get('profit_target_pct', 50),
            'stop_loss_mode': stop_loss_mode,
            'stop_loss_pct': trading_rules.get('stop_loss_pct', 100),
            'wing_width': strike_selection.get('wing_width', 10)
        }
        
        # Generate code sections
        imports = BaseStrategy.generate_imports()
        config_loader = BaseStrategy.generate_config_loader().replace('{CONFIG_PLACEHOLDER}', config_json)
        indicator_manager = BaseStrategy.generate_indicator_manager(indicators_config, IronButterfly.strategy_direction)
        advanced_filters = BaseStrategy.generate_advanced_filters(advanced_config)
        strike_selector = IronButterfly._generate_strike_selector(advanced_config)
        strategy_class = IronButterfly._generate_strategy_class()
        main_algorithm = IronButterfly._generate_main_algorithm(flat_config, advanced_config)
        
        # Combine all parts
        algorithm_code = f"""{imports}

{config_loader}

{indicator_manager}

{advanced_filters}

{strike_selector}

{strategy_class}

{main_algorithm}
"""
        
        return algorithm_code
    
    @staticmethod
    def _build_config_json(config, stop_loss_mode, advanced_config):
        """Build configuration dictionary as string"""
        
        trading_rules = config.get('trading_rules', {})
        strike_selection = config.get('strike_selection', {})
        
        config_str = "{\n"
        config_str += f"        'ticker': '{config.get('ticker', 'SPY')}',\n"
        config_str += f"        'strategy': 'Iron Butterfly',\n"
        config_str += f"        'expiry_days': {config.get('expiry_days', 30)},\n"
        config_str += f"        'expiry_range': {config.get('expiry_range', 5)},\n"
        config_str += f"        'resolution': '{trading_rules.get('resolution', 'Daily')}',\n"
        config_str += f"        'max_positions': {trading_rules.get('max_positions', 5)},\n"
        config_str += f"        'min_days_between_trades': {trading_rules.get('min_days_between_trades', 0)},\n"
        config_str += f"        'profit_target_pct': {trading_rules.get('profit_target_pct', 50)},\n"
        config_str += f"        'stop_loss_mode': '{stop_loss_mode}',\n"
        config_str += f"        'stop_loss_pct': {trading_rules.get('stop_loss_pct', 100)},\n"
        config_str += f"        'wing_width': {strike_selection.get('wing_width', 10)},\n"
        
        # Add advanced config using centralized method
        config_str += "        " + BaseStrategy.generate_advanced_config_string(advanced_config) + "\n"
        config_str += "    }"
        
        return config_str
    
    @staticmethod
    def _generate_strike_selector(advanced_config):
        """Generate strike selection logic for Iron Butterfly"""
        
        liquidity_enabled = advanced_config.get('liquidity_enabled', True)
        
        code = '''
class StrikeSelector:
    """Find ATM strikes for Iron Butterfly"""
    
    @staticmethod
    def find_strikes_by_atm(option_chain, underlying_price, wing_width, config, algo):
        """Find Iron Butterfly strikes (ATM body + OTM wings)"""
        
        try:
            # Group by expiration
            expiries = {}
            for contract in option_chain:
                exp_date = contract.Expiry.date()
                if exp_date not in expiries:
                    expiries[exp_date] = {'puts': [], 'calls': []}
                
                if contract.Right == OptionRight.Put:
                    expiries[exp_date]['puts'].append(contract)
                else:
                    expiries[exp_date]['calls'].append(contract)
            
            # Apply expiration cycle filter
            if config.advanced['expiration_cycle'] != 'any':
                expiries = ExpirationFilter.filter_expiries(
                    expiries, 
                    config.advanced['expiration_cycle']
                )
                
                if not expiries:
                    algo.Log("[X] No expiries match cycle filter")
                    return None
            
            best_expiry = max(expiries.keys(), 
                            key=lambda x: len(expiries[x]['puts']) + len(expiries[x]['calls']))
            
            puts = expiries[best_expiry]['puts']
            calls = expiries[best_expiry]['calls']
            
            algo.Log(f"[+] Selected expiry: {best_expiry} ({len(puts)} puts, {len(calls)} calls)")
'''
        
        if liquidity_enabled:
            code += '''
            # Filter by liquidity
            liquid_puts = [p for p in puts if LiquidityFilter.check_liquidity(
                p, 
                config.advanced['max_spread_pct'],
                config.advanced['min_open_interest']
            )]
            
            liquid_calls = [c for c in calls if LiquidityFilter.check_liquidity(
                c,
                config.advanced['max_spread_pct'],
                config.advanced['min_open_interest']
            )]
            
            if len(liquid_puts) < 5 or len(liquid_calls) < 5:
                algo.Log(f"[X] Insufficient liquid contracts (puts: {len(liquid_puts)}, calls: {len(liquid_calls)})")
                return None
            
            puts = liquid_puts
            calls = liquid_calls
            algo.Log(f"[+] Liquid contracts: {len(puts)} puts, {len(calls)} calls")
'''

        # Add Advanced Greeks filtering
        advanced_greeks_enabled = advanced_config.get('advanced_greeks_enabled', False)
        if advanced_greeks_enabled:
            code += '''
            # Advanced Greeks Filter (contract-level)
            if hasattr(algo, 'advanced_greeks_filter'):
                puts = algo.advanced_greeks_filter.filter_contracts(puts)
                calls = algo.advanced_greeks_filter.filter_contracts(calls)
                if len(puts) < 5 or len(calls) < 5:
                    algo.Log(f"[X] Insufficient contracts after Greeks filter (puts: {len(puts)}, calls: {len(calls)})")
                    return None
                algo.Log(f"[+] After Greeks filter: {len(puts)} puts, {len(calls)} calls")
'''

        code += '''
            # Find ATM strikes
            atm_put = StrikeSelector._find_atm_strike(puts, underlying_price, algo)
            atm_call = StrikeSelector._find_atm_strike(calls, underlying_price, algo)
            
            if not atm_put or not atm_call:
                return None
            
            # Find wing strikes
            long_put_strike = atm_put.Strike - wing_width
            long_call_strike = atm_call.Strike + wing_width
            
            long_put = StrikeSelector._find_strike(puts, long_put_strike, algo)
            long_call = StrikeSelector._find_strike(calls, long_call_strike, algo)
            
            if atm_put and long_put and atm_call and long_call:
                if (long_put.Strike < atm_put.Strike == atm_call.Strike < long_call.Strike):
                    if (atm_put.Expiry.date() == long_put.Expiry.date() == 
                        atm_call.Expiry.date() == long_call.Expiry.date()):
                        
                        algo.Log(f"[+] Valid Iron Butterfly! {long_put.Strike}/{atm_put.Strike}/{long_call.Strike}")
                        
                        return {
                            'short_put': atm_put,
                            'long_put': long_put,
                            'short_call': atm_call,
                            'long_call': long_call
                        }
            
            return None
            
        except Exception as e:
            algo.Log(f"[X] Strike selection error: {e}")
            return None
    
    @staticmethod
    def _find_atm_strike(contracts, underlying_price, algo):
        """Find ATM strike (closest to underlying)"""
        
        best_contract = None
        best_diff = float('inf')
        
        for contract in contracts:
            diff = abs(contract.Strike - underlying_price)
            if diff < best_diff:
                best_diff = diff
                best_contract = contract
        
        return best_contract
    
    @staticmethod
    def _find_strike(contracts, target_strike, algo):
        """Find exact strike"""
        
        for contract in contracts:
            if contract.Strike == target_strike:
                return contract
        
        return None
'''
        return code
    
    @staticmethod
    def _generate_strategy_class():
        """Generate strategy class"""
        
        code = '''
class IronButterflyStrategy:
    """Manage Iron Butterfly positions"""
    
    def __init__(self, algorithm):
        self.algo = algorithm
    
    def enter_position(self, strikes, underlying_price, time):
        """Enter new Iron Butterfly position"""
        
        try:
            if self.algo.IsWarmingUp:
                return None
            
            # Calculate prices
            short_put_price = (strikes['short_put'].BidPrice + strikes['short_put'].AskPrice) / 2
            long_put_price = (strikes['long_put'].BidPrice + strikes['long_put'].AskPrice) / 2
            short_call_price = (strikes['short_call'].BidPrice + strikes['short_call'].AskPrice) / 2
            long_call_price = (strikes['long_call'].BidPrice + strikes['long_call'].AskPrice) / 2
            
            # Calculate P&L metrics
            net_credit = (short_put_price - long_put_price + short_call_price - long_call_price) * 100
            wing_width = (strikes['short_put'].Strike - strikes['long_put'].Strike) * 100
            max_loss = wing_width - net_credit
            max_profit = net_credit
            
            # Log entry
            self.algo.Log("")
            self.algo.Log("=" * 60)
            self.algo.Log(">>> ENTERING IRON BUTTERFLY")
            self.algo.Log("=" * 60)
            self.algo.Log(f"Underlying: ${underlying_price:.2f}")
            self.algo.Log(f"ATM Strike: {strikes['short_put'].Strike}")
            self.algo.Log(f"Wings: {strikes['long_put'].Strike} / {strikes['long_call'].Strike}")
            self.algo.Log(f"Net Credit: ${net_credit:.2f}")
            self.algo.Log(f"Max Profit: ${max_profit:.2f}")
            self.algo.Log(f"Max Loss: ${max_loss:.2f}")
            
            # Place orders
            self.algo.MarketOrder(strikes['short_put'].Symbol, -1)
            self.algo.MarketOrder(strikes['long_put'].Symbol, 1)
            self.algo.MarketOrder(strikes['short_call'].Symbol, -1)
            self.algo.MarketOrder(strikes['long_call'].Symbol, 1)
            
            self.algo.Log("[+] Orders placed")
            
            # Track position
            self.algo.position_counter += 1
            pos_id = self.algo.position_counter
            
            self.algo.positions[pos_id] = {
                'status': 'open',
                'entry_time': time,
                'entry_underlying_price': underlying_price,
                'expiry_date': strikes['short_put'].Expiry.date(),
                'strikes': strikes,
                'current_pnl': 0,
                'metrics': {
                    'net_credit': net_credit,
                    'max_profit': max_profit,
                    'max_loss': max_loss,
                    'mae': 0,
                    'mfe': 0
                }
            }
            
            self.algo.Log(f"Position #{pos_id} opened")
            self.algo.Log("=" * 60)
            
            return pos_id
            
        except Exception as e:
            self.algo.Log(f"[X] Entry error: {e}")
            return None
    
    def calculate_pnl(self, pos, data):
        """Calculate current P&L"""
        
        try:
            if not data.OptionChains:
                return None
            
            for chain in data.OptionChains:
                contracts = list(chain.Value)
                entry_strikes = pos['strikes']
                current_prices = {}
                
                for contract in contracts:
                    if (contract.Strike == entry_strikes['short_put'].Strike and 
                        contract.Right == OptionRight.PUT and
                        contract.Expiry.date() == entry_strikes['short_put'].Expiry.date()):
                        current_prices['sp'] = (contract.BidPrice + contract.AskPrice) / 2
                    
                    if (contract.Strike == entry_strikes['long_put'].Strike and 
                        contract.Right == OptionRight.PUT and
                        contract.Expiry.date() == entry_strikes['long_put'].Expiry.date()):
                        current_prices['lp'] = (contract.BidPrice + contract.AskPrice) / 2
                    
                    if (contract.Strike == entry_strikes['short_call'].Strike and 
                        contract.Right == OptionRight.CALL and
                        contract.Expiry.date() == entry_strikes['short_call'].Expiry.date()):
                        current_prices['sc'] = (contract.BidPrice + contract.AskPrice) / 2
                    
                    if (contract.Strike == entry_strikes['long_call'].Strike and 
                        contract.Right == OptionRight.CALL and
                        contract.Expiry.date() == entry_strikes['long_call'].Expiry.date()):
                        current_prices['lc'] = (contract.BidPrice + contract.AskPrice) / 2
                
                if len(current_prices) == 4:
                    current_value = (current_prices['sp'] - current_prices['lp'] + 
                                   current_prices['sc'] - current_prices['lc']) * 100
                    entry_credit = pos['metrics']['net_credit']
                    return entry_credit - current_value
                
                break
            
            return None
            
        except Exception as e:
            self.algo.Log(f"[X] P&L calc error: {e}")
            return 0
    
    def close_position(self, pos_id, reason, time):
        """Close Iron Butterfly position"""
        
        try:
            pos = self.algo.positions[pos_id]
            strikes = pos['strikes']
            
            self.algo.MarketOrder(strikes['short_put'].Symbol, 1)
            self.algo.MarketOrder(strikes['long_put'].Symbol, -1)
            self.algo.MarketOrder(strikes['short_call'].Symbol, 1)
            self.algo.MarketOrder(strikes['long_call'].Symbol, -1)
            
            final_pnl = pos['current_pnl']
            mae = pos['metrics']['mae']
            mfe = pos['metrics']['mfe']
            max_profit = pos['metrics']['max_profit']
            duration = (time.date() - pos['entry_time'].date()).days
            
            mae_pct = (mae / max_profit * 100) if max_profit > 0 else 0
            mfe_pct = (mfe / max_profit * 100) if max_profit > 0 else 0
            
            self.algo.Log("")
            self.algo.Log("=" * 60)
            self.algo.Log(f"<<< EXITING #{pos_id} - {reason}")
            self.algo.Log("=" * 60)
            self.algo.Log("[+] Exit complete")
            self.algo.Log(f"Duration: {duration} days")
            self.algo.Log(f"P&L: ${final_pnl:.2f}")
            self.algo.Log(f"MAE: ${mae:.2f} ({mae_pct:.1f}%)")
            self.algo.Log(f"MFE: ${mfe:.2f} ({mfe_pct:.1f}%)")
            self.algo.Log("=" * 60)
            
            pos['status'] = 'closed'
            pos['exit_time'] = time
            pos['exit_reason'] = reason
            pos['final_pnl'] = final_pnl
            
        except Exception as e:
            self.algo.Log(f"[X] Exit error: {e}")
'''
        return code
    
    @staticmethod
    def _generate_main_algorithm(config, advanced_config):
        """Generate main algorithm class"""
        
        initialize_code = BaseStrategy.generate_initialize_base(config)
        position_tracking = BaseStrategy.generate_position_tracking()
        exit_logic = BaseStrategy.generate_exit_logic(config)

        # Use centralized filter methods
        filter_init = BaseStrategy.generate_filter_initialization(advanced_config)
        filter_checks = BaseStrategy.generate_filter_checks(advanced_config)
        
        code = f'''
class OptionsBacktest(QCAlgorithm):
    """Iron Butterfly Backtesting Algorithm"""
    
    {initialize_code}
        

        
        # Initialize advanced filters
{filter_init}
        
        self.Log("=" * 60)
        self.Log("Strategy: Iron Butterfly")
        self.Log(f"Ticker: {{config.ticker}}")
        self.Log(f"Expiry: {{config.expiry_days}} days (±{{config.expiry_range}} day window)")
        self.Log(f"Expiration Cycle: {{self.config.advanced['expiration_cycle']}}")
        self.Log(f"Wing Width: ${{config.wing_width}}")
        self.Log(f"Resolution: {{config.resolution.upper()}}")
        self.Log(f"Max Positions: {{config.max_positions}}")
        self.Log(f"Profit Target: {{config.profit_target_pct}}%")
        self.Log(f"Stop Loss: {{config.stop_loss_mode}} mode ({{config.stop_loss_pct}}%)")
        if self.config.advanced['liquidity_enabled']:
            self.Log(f"Liquidity Filter: Max Spread {{self.config.advanced['max_spread_pct']}}%, Min OI {{self.config.advanced['min_open_interest']}}")
        self.Log("=" * 60)
        self.Log("[+] Ready!")
        
        self.strategy = IronButterflyStrategy(self)
    
    def OnData(self, data):
        """Main data handler"""
        
        if self.IsWarmingUp:
            return
        
        if self.positions:
            self.update_positions(data)
        
        if not self.can_enter_new_trade():
            return
        
        if not data.OptionChains:
            return
        
        for chain in data.OptionChains:
            if chain.Key != self.option_symbol:
                continue
            
            underlying_price = self.Securities[self.config.ticker].Price
            
{filter_checks}
            
            strikes = StrikeSelector.find_strikes_by_atm(
                chain.Value,
                underlying_price,
                self.config.wing_width,
                self.config,
                self
            )
            
            if not strikes:
                continue

            # Check indicators
            allowed, reason = self.indicators.should_enter_trade(self.config.ticker)
            if not allowed:
                self.Log(f"[X] Indicators blocked entry: {{reason}}")
                continue
            else:
                self.Log(f"[✓] Indicators: {{reason}}")
            
            self.strategy.enter_position(strikes, underlying_price, data.Time)
            self.last_trade_date = data.Time.date()
            
            break
    
    def can_enter_new_trade(self):
        """Check if we can enter a new trade"""
        
        open_positions = sum(1 for p in self.positions.values() if p['status'] == 'open')
        if open_positions >= self.config.max_positions:
            return False
        
        if self.last_trade_date and self.config.min_days_between_trades > 0:
            days_since_last = (self.Time.date() - self.last_trade_date).days
            if days_since_last < self.config.min_days_between_trades:
                return False
        
        return True
    
{position_tracking}
    
    def calculate_pnl(self, pos, data):
        """Calculate position P&L"""
        return self.strategy.calculate_pnl(pos, data)
    
{exit_logic}
    
    def close_position(self, pos_id, reason, time):
        """Close a position"""
        self.strategy.close_position(pos_id, reason, time)
'''
        
        return code
