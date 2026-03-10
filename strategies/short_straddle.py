"""
Short Straddle Strategy
Sell ATM put + ATM call (credit strategy)
"""

from .base_strategy import BaseStrategy

class ShortStraddle(BaseStrategy):
    """Short Straddle - Sell ATM puts and calls for credit"""

    strategy_direction = 'neutral'  # Strategy expects neutral/range-bound conditions

    @staticmethod
    def generate_code(config):
        """Generate complete Short Straddle algorithm"""
        
        trading_rules = config.get('trading_rules', {})
        strike_selection = config.get('strike_selection', {})
        indicators_config = config.get('indicators', {})
        advanced_config = config.get('advanced', {})
        
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
        
        config_json = ShortStraddle._build_config_json(config, stop_loss_mode, advanced_config)
        
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
            'stop_loss_pct': trading_rules.get('stop_loss_pct', 200)
        }
        
        imports = BaseStrategy.generate_imports()
        config_loader = BaseStrategy.generate_config_loader().replace('{CONFIG_PLACEHOLDER}', config_json)
        indicator_manager = BaseStrategy.generate_indicator_manager(indicators_config, ShortStraddle.strategy_direction)
        advanced_filters = BaseStrategy.generate_advanced_filters(advanced_config)
        strike_selector = ShortStraddle._generate_strike_selector(advanced_config)
        strategy_class = ShortStraddle._generate_strategy_class()
        main_algorithm = ShortStraddle._generate_main_algorithm(flat_config, advanced_config)
        
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
        
        config_str = "{\n"
        config_str += f"        'ticker': '{config.get('ticker', 'SPY')}',\n"
        config_str += f"        'strategy': 'Short Straddle',\n"
        config_str += f"        'expiry_days': {config.get('expiry_days', 30)},\n"
        config_str += f"        'expiry_range': {config.get('expiry_range', 5)},\n"
        config_str += f"        'resolution': '{trading_rules.get('resolution', 'Daily')}',\n"
        config_str += f"        'max_positions': {trading_rules.get('max_positions', 5)},\n"
        config_str += f"        'min_days_between_trades': {trading_rules.get('min_days_between_trades', 0)},\n"
        config_str += f"        'profit_target_pct': {trading_rules.get('profit_target_pct', 50)},\n"
        config_str += f"        'stop_loss_mode': '{stop_loss_mode}',\n"
        config_str += f"        'stop_loss_pct': {trading_rules.get('stop_loss_pct', 200)},\n"
        config_str += f"        'sizing_mode': '{trading_rules.get('sizing_mode', 'fixed')}',\n"
        config_str += f"        'sizing_contracts': {trading_rules.get('sizing_contracts', 1)},\n"
        config_str += f"        'sizing_risk_pct': {trading_rules.get('sizing_risk_pct', 2.0)},\n"
        config_str += f"        'sizing_max_contracts': {trading_rules.get('sizing_max_contracts', 10)},\n"
        config_str += f"        'close_dte': {config.get('close_dte', 21)},\n"
        config_str += f"        'min_rr_ratio': {trading_rules.get('min_rr_ratio', 0.0)},\n"

        # Add advanced config using centralized method
        config_str += "        " + BaseStrategy.generate_advanced_config_string(advanced_config) + "\n"
        config_str += "    }"
        
        return config_str
    
    @staticmethod
    def _generate_strike_selector(advanced_config):
        """Generate strike selection logic"""
        
        liquidity_enabled = advanced_config.get('liquidity_enabled', True)
        
        code = '''
class StrikeSelector:
    """Find ATM strikes for Short Straddle"""
    
    @staticmethod
    def find_strikes_by_atm(option_chain, underlying_price, config, algo):
        """Find straddle strikes (ATM put + ATM call)"""
        
        try:
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
            
            if len(liquid_puts) < 3 or len(liquid_calls) < 3:
                algo.Log(f"[X] Insufficient liquid contracts (puts: {len(liquid_puts)}, calls: {len(liquid_calls)})")
                return None
            
            puts = liquid_puts
            calls = liquid_calls
            algo.Log(f"[+] Liquid contracts: {len(puts)} puts, {len(calls)} calls")
'''

        # Add Advanced Greeks filtering if enabled
        advanced_greeks_enabled = advanced_config.get('advanced_greeks_enabled', False)
        if advanced_greeks_enabled:
            code += '''
            # Filter by Advanced Greeks (contract-level)
            if hasattr(algo, 'advanced_greeks_filter'):
                puts = algo.advanced_greeks_filter.filter_contracts(puts)
                calls = algo.advanced_greeks_filter.filter_contracts(calls)

                if len(puts) < 2 or len(calls) < 2:
                    algo.Log(f"[X] Insufficient contracts after Greeks filter (puts: {len(puts)}, calls: {len(calls)})")
                    return None
'''

        code += '''
            # Find ATM strikes
            atm_put = StrikeSelector._find_atm_strike(puts, underlying_price, algo)
            atm_call = StrikeSelector._find_atm_strike(calls, underlying_price, algo)
            
            if atm_put and atm_call:
                if atm_put.Strike == atm_call.Strike:
                    if atm_put.Expiry.date() == atm_call.Expiry.date():
                        algo.Log(f"[+] Valid Short Straddle! ATM Strike: {atm_put.Strike}")
                        return {
                            'short_put': atm_put,
                            'short_call': atm_call
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
'''
        return code
    
    @staticmethod
    def _generate_strategy_class():
        """Generate strategy class"""
        
        code = '''
class ShortStraddleStrategy:
    """Manage Short Straddle positions"""
    
    def __init__(self, algorithm):
        self.algo = algorithm
    
    def enter_position(self, strikes, underlying_price, time):
        """Enter new Short Straddle (CREDIT)"""
        
        try:
            if self.algo.IsWarmingUp:
                return None
            
            short_put_price = (strikes['short_put'].BidPrice + strikes['short_put'].AskPrice) / 2
            short_call_price = (strikes['short_call'].BidPrice + strikes['short_call'].AskPrice) / 2
            
            net_credit = (short_put_price + short_call_price) * 100
            max_profit = net_credit
            max_loss = 999999  # Theoretically unlimited
            
            self.algo.Log("")
            self.algo.Log("=" * 60)
            self.algo.Log(">>> ENTERING SHORT STRADDLE")
            self.algo.Log("=" * 60)
            self.algo.Log(f"Underlying: ${underlying_price:.2f}")
            self.algo.Log(f"ATM Strike: {strikes['short_put'].Strike}")
            self.algo.Log(f"Net Credit: ${net_credit:.2f}")
            self.algo.Log(f"Max Profit: ${max_profit:.2f}")
            self.algo.Log(f"Max Loss: Unlimited")

            # Min R/R ratio enforcement
            if getattr(self.algo.config, 'min_rr_ratio', 0) > 0 and max_loss > 0:
                rr = max_profit / max_loss
                if rr < self.algo.config.min_rr_ratio:
                    self.algo.Log(f"[X] Skip: R/R {rr:.2f} < min {self.algo.config.min_rr_ratio:.1f}")
                    return None
            contracts = self.algo.calculate_contracts(max_loss)
            self.algo.Log(f"Contracts: {contracts}")

            self.algo.MarketOrder(strikes['short_put'].Symbol, -contracts)
            self.algo.MarketOrder(strikes['short_call'].Symbol, -contracts)

            self.algo.Log("[+] Orders placed")

            self.algo.position_counter += 1
            pos_id = self.algo.position_counter

            self.algo.positions[pos_id] = {
                'status': 'open',
                'contracts': contracts,
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
                    
                    if (contract.Strike == entry_strikes['short_call'].Strike and 
                        contract.Right == OptionRight.CALL and
                        contract.Expiry.date() == entry_strikes['short_call'].Expiry.date()):
                        current_prices['sc'] = (contract.BidPrice + contract.AskPrice) / 2
                
                if len(current_prices) == 2:
                    current_value = (current_prices['sp'] + current_prices['sc']) * 100
                    entry_credit = pos['metrics']['net_credit']
                    return entry_credit - current_value
                
                break
            
            return None
            
        except Exception as e:
            self.algo.Log(f"[X] P&L calc error: {e}")
            return 0
    
    def close_position(self, pos_id, reason, time):
        """Close position"""
        
        try:
            pos = self.algo.positions[pos_id]
            strikes = pos['strikes']
            pos_contracts = pos.get('contracts', 1)

            self.algo.MarketOrder(strikes['short_put'].Symbol, pos_contracts)
            self.algo.MarketOrder(strikes['short_call'].Symbol, pos_contracts)
            
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
        """Generate main algorithm"""
        
        initialize_code = BaseStrategy.generate_initialize_base(config)
        position_tracking = BaseStrategy.generate_position_tracking()
        exit_logic = BaseStrategy.generate_exit_logic(config)

        # Use centralized filter initialization and checks
        filter_init = BaseStrategy.generate_filter_initialization(advanced_config)
        filter_checks = BaseStrategy.generate_filter_checks(advanced_config)
        
        code = f'''
class OptionsBacktest(QCAlgorithm):
    """Short Straddle Backtesting Algorithm"""
    
    {initialize_code}
        

        
        # Initialize advanced filters
{filter_init}
        
        self.Log("=" * 60)
        self.Log("Strategy: Short Straddle")
        self.Log(f"Ticker: {{config.ticker}}")
        self.Log(f"Expiry: {{config.expiry_days}} days (±{{config.expiry_range}} day window)")
        self.Log(f"Expiration Cycle: {{self.config.advanced['expiration_cycle']}}")
        self.Log(f"Resolution: {{config.resolution.upper()}}")
        self.Log(f"Max Positions: {{config.max_positions}}")
        self.Log(f"Profit Target: {{config.profit_target_pct}}%")
        self.Log(f"Stop Loss: {{config.stop_loss_mode}} mode ({{config.stop_loss_pct}}%)")
        if self.config.advanced['liquidity_enabled']:
            self.Log(f"Liquidity Filter: Max Spread {{self.config.advanced['max_spread_pct']}}%, Min OI {{self.config.advanced['min_open_interest']}}")
        self.Log("=" * 60)
        self.Log("[+] Ready!")
        
        self.strategy = ShortStraddleStrategy(self)
    
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
