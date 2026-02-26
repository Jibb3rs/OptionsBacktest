"""
Bull Put Spread Strategy
Sell OTM put + Buy further OTM put (credit spread)
"""

from .base_strategy import BaseStrategy

class BullPutSpread(BaseStrategy):
    """Bull Put Spread - Bullish credit spread"""

    strategy_direction = 'bullish'  # Strategy expects bullish signals

    @staticmethod
    def generate_code(config):
        """Generate complete Bull Put Spread algorithm"""
        
        trading_rules = config.get('trading_rules', {})
        strike_selection = config.get('strike_selection', {})
        indicators_config = config.get('indicators', {})
        advanced_config = config.get('advanced', {})
        
        # Map delta keys
        deltas_raw = strike_selection.get('deltas', {})
        delta_mapping = {
            'Short Put Delta:': 'short_put',
            'Long Put Delta:': 'long_put'
        }
        
        formatted_deltas = {}
        for gui_key, code_key in delta_mapping.items():
            if gui_key in deltas_raw:
                formatted_deltas[code_key] = deltas_raw[gui_key]
        
        if not formatted_deltas:
            formatted_deltas = {
                'short_put': 0.30,
                'long_put': 0.16
            }
        
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
        
        config_json = BullPutSpread._build_config_json(config, formatted_deltas, stop_loss_mode, advanced_config)
        
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
            'deltas': formatted_deltas
        }
        
        imports = BaseStrategy.generate_imports()
        config_loader = BaseStrategy.generate_config_loader().replace('{CONFIG_PLACEHOLDER}', config_json)
        indicator_manager = BaseStrategy.generate_indicator_manager(indicators_config, BullPutSpread.strategy_direction)
        advanced_filters = BaseStrategy.generate_advanced_filters(advanced_config)
        strike_selector = BullPutSpread._generate_strike_selector(advanced_config)
        strategy_class = BullPutSpread._generate_strategy_class()
        main_algorithm = BullPutSpread._generate_main_algorithm(flat_config, advanced_config)
        
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
    def _build_config_json(config, formatted_deltas, stop_loss_mode, advanced_config):
        """Build configuration dictionary as string"""
        
        trading_rules = config.get('trading_rules', {})
        
        config_str = "{\n"
        config_str += f"        'ticker': '{config.get('ticker', 'SPY')}',\n"
        config_str += f"        'strategy': 'Bull Put Spread',\n"
        config_str += f"        'expiry_days': {config.get('expiry_days', 30)},\n"
        config_str += f"        'expiry_range': {config.get('expiry_range', 5)},\n"
        config_str += f"        'resolution': '{trading_rules.get('resolution', 'Daily')}',\n"
        config_str += f"        'max_positions': {trading_rules.get('max_positions', 5)},\n"
        config_str += f"        'min_days_between_trades': {trading_rules.get('min_days_between_trades', 0)},\n"
        config_str += f"        'profit_target_pct': {trading_rules.get('profit_target_pct', 50)},\n"
        config_str += f"        'stop_loss_mode': '{stop_loss_mode}',\n"
        config_str += f"        'stop_loss_pct': {trading_rules.get('stop_loss_pct', 100)},\n"
        config_str += "        'deltas': {\n"
        config_str += f"            'short_put': {abs(formatted_deltas.get('short_put', 0.30))},\n"
        config_str += f"            'long_put': {abs(formatted_deltas.get('long_put', 0.16))}\n"
        config_str += "        },\n"
        
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
    """Find strikes for Bull Put Spread"""
    
    @staticmethod
    def find_strikes_by_delta(option_chain, underlying_price, target_deltas, config, algo):
        """Find put spread strikes using delta"""
        
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
            
            algo.Log(f"[+] Selected expiry: {best_expiry} ({len(puts)} puts)")
'''
        
        if liquidity_enabled:
            code += '''
            # Filter by liquidity
            liquid_puts = [p for p in puts if LiquidityFilter.check_liquidity(
                p, 
                config.advanced['max_spread_pct'],
                config.advanced['min_open_interest']
            )]
            
            if len(liquid_puts) < 5:
                algo.Log(f"[X] Insufficient liquid contracts (puts: {len(liquid_puts)})")
                return None
            
            puts = liquid_puts
            algo.Log(f"[+] Liquid contracts: {len(puts)} puts")
'''

        # Add Advanced Greeks filtering
        advanced_greeks_enabled = advanced_config.get('advanced_greeks_enabled', False)
        if advanced_greeks_enabled:
            code += '''
            # Advanced Greeks Filter (contract-level)
            if hasattr(algo, 'advanced_greeks_filter'):
                puts = algo.advanced_greeks_filter.filter_contracts(puts)
                if len(puts) < 5:
                    algo.Log(f"[X] Insufficient contracts after Greeks filter (puts: {len(puts)})")
                    return None
                algo.Log(f"[+] After Greeks filter: {len(puts)} puts")
'''

        code += '''
            # Find short put (higher delta, closer to ATM)
            short_put = StrikeSelector._find_closest_delta(
                puts, target_deltas['short_put'], algo
            )
            
            # Find long put (lower delta, further OTM)
            long_put = StrikeSelector._find_closest_delta(
                puts, target_deltas['long_put'], algo
            )
            
            if short_put and long_put:
                if long_put.Strike < short_put.Strike < underlying_price:
                    if short_put.Expiry.date() == long_put.Expiry.date():
                        algo.Log(f"[+] Valid Bull Put Spread! {long_put.Strike}/{short_put.Strike}")
                        return {
                            'short_put': short_put,
                            'long_put': long_put
                        }
            
            return None
            
        except Exception as e:
            algo.Log(f"[X] Strike selection error: {e}")
            return None
    
    @staticmethod
    def _find_closest_delta(contracts, target_delta, algo):
        """Find contract with delta closest to target"""
        
        best_contract = None
        best_delta_diff = float('inf')
        
        for contract in contracts:
            if not contract.Greeks or not contract.Greeks.Delta:
                continue
            
            delta = abs(contract.Greeks.Delta)
            delta_diff = abs(delta - target_delta)
            
            if delta_diff < best_delta_diff:
                best_delta_diff = delta_diff
                best_contract = contract
        
        return best_contract
'''
        return code
    
    @staticmethod
    def _generate_strategy_class():
        """Generate strategy class"""
        
        code = '''
class BullPutSpreadStrategy:
    """Manage Bull Put Spread positions"""
    
    def __init__(self, algorithm):
        self.algo = algorithm
    
    def enter_position(self, strikes, underlying_price, time):
        """Enter new Bull Put Spread (CREDIT)"""
        
        try:
            if self.algo.IsWarmingUp:
                return None
            
            short_put_price = (strikes['short_put'].BidPrice + strikes['short_put'].AskPrice) / 2
            long_put_price = (strikes['long_put'].BidPrice + strikes['long_put'].AskPrice) / 2
            
            net_credit = (short_put_price - long_put_price) * 100
            spread_width = (strikes['short_put'].Strike - strikes['long_put'].Strike) * 100
            max_loss = spread_width - net_credit
            max_profit = net_credit
            
            self.algo.Log("")
            self.algo.Log("=" * 60)
            self.algo.Log(">>> ENTERING BULL PUT SPREAD")
            self.algo.Log("=" * 60)
            self.algo.Log(f"Underlying: ${underlying_price:.2f}")
            self.algo.Log(f"Put Spread: {strikes['long_put'].Strike}/{strikes['short_put'].Strike}")
            self.algo.Log(f"Net Credit: ${net_credit:.2f}")
            self.algo.Log(f"Max Profit: ${max_profit:.2f}")
            self.algo.Log(f"Max Loss: ${max_loss:.2f}")
            
            self.algo.MarketOrder(strikes['short_put'].Symbol, -1)
            self.algo.MarketOrder(strikes['long_put'].Symbol, 1)
            
            self.algo.Log("[+] Orders placed")
            
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
                
                if len(current_prices) == 2:
                    current_value = (current_prices['sp'] - current_prices['lp']) * 100
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
            
            self.algo.MarketOrder(strikes['short_put'].Symbol, 1)
            self.algo.MarketOrder(strikes['long_put'].Symbol, -1)
            
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

        # Use centralized filter methods
        filter_init = BaseStrategy.generate_filter_initialization(advanced_config)
        filter_checks = BaseStrategy.generate_filter_checks(advanced_config)
        
        code = f'''
class OptionsBacktest(QCAlgorithm):
    """Bull Put Spread Backtesting Algorithm"""
    
    {initialize_code}
        

        
        # Initialize advanced filters
{filter_init}
        
        self.Log("=" * 60)
        self.Log("Strategy: Bull Put Spread")
        self.Log(f"Ticker: {{config.ticker}}")
        self.Log(f"Expiry: {{config.expiry_days}} days (±{{config.expiry_range}} day window)")
        self.Log(f"Expiration Cycle: {{self.config.advanced['expiration_cycle']}}")
        self.Log(f"Resolution: {{config.resolution.upper()}}")
        self.Log(f"Max Positions: {{config.max_positions}}")
        self.Log(f"Profit Target: {{config.profit_target_pct}}%")
        self.Log(f"Stop Loss: {{config.stop_loss_mode}} mode ({{config.stop_loss_pct}}%)")
        self.Log(f"Deltas: {{config.deltas}}")
        if self.config.advanced['liquidity_enabled']:
            self.Log(f"Liquidity Filter: Max Spread {{self.config.advanced['max_spread_pct']}}%, Min OI {{self.config.advanced['min_open_interest']}}")
        self.Log("=" * 60)
        self.Log("[+] Ready!")
        
        self.strategy = BullPutSpreadStrategy(self)
    
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
            
            strikes = StrikeSelector.find_strikes_by_delta(
                chain.Value,
                underlying_price,
                self.config.deltas,
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
