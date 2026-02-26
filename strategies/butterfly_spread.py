"""
Butterfly Spread Strategy
Buy 1 low strike, Sell 2 mid strike, Buy 1 high strike (same type)
Maximum profit at middle strike, limited risk
"""

from .base_strategy import BaseStrategy

class ButterflySpread(BaseStrategy):
    """Butterfly Spread - Neutral strategy with limited risk"""

    strategy_direction = 'neutral'

    @staticmethod
    def generate_code(config):
        """Generate complete Butterfly Spread algorithm"""

        trading_rules = config.get('trading_rules', {})
        strike_selection = config.get('strike_selection', {})
        indicators_config = config.get('indicators', {})
        advanced_config = config.get('advanced', {})

        # Butterfly uses wing width from underlying
        wing_width = strike_selection.get('wing_width', 5)

        formatted_deltas = {
            'center_delta': 0.50,  # ATM for center strikes
            'wing_width': wing_width
        }

        stop_loss_mode = trading_rules.get('stop_loss_mode', 'max_loss')
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
        stop_loss_mode = stop_loss_map.get(stop_loss_mode, 'max_loss')

        config_json = ButterflySpread._build_config_json(config, formatted_deltas, stop_loss_mode, advanced_config)

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
            'profit_target_pct': trading_rules.get('profit_target_pct', 100),
            'stop_loss_mode': stop_loss_mode,
            'stop_loss_pct': trading_rules.get('stop_loss_pct', 50),
            'deltas': formatted_deltas
        }

        imports = BaseStrategy.generate_imports()
        config_loader = BaseStrategy.generate_config_loader().replace('{CONFIG_PLACEHOLDER}', config_json)
        indicator_manager = BaseStrategy.generate_indicator_manager(indicators_config, ButterflySpread.strategy_direction)
        advanced_filters = BaseStrategy.generate_advanced_filters(advanced_config)
        strike_selector = ButterflySpread._generate_strike_selector(advanced_config)
        strategy_class = ButterflySpread._generate_strategy_class()
        main_algorithm = ButterflySpread._generate_main_algorithm(flat_config, advanced_config)

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
        config_str += f"        'strategy': 'Butterfly Spread',\n"
        config_str += f"        'expiry_days': {config.get('expiry_days', 30)},\n"
        config_str += f"        'expiry_range': {config.get('expiry_range', 5)},\n"
        config_str += f"        'resolution': '{trading_rules.get('resolution', 'Daily')}',\n"
        config_str += f"        'max_positions': {trading_rules.get('max_positions', 5)},\n"
        config_str += f"        'min_days_between_trades': {trading_rules.get('min_days_between_trades', 0)},\n"
        config_str += f"        'profit_target_pct': {trading_rules.get('profit_target_pct', 100)},\n"
        config_str += f"        'stop_loss_mode': '{stop_loss_mode}',\n"
        config_str += f"        'stop_loss_pct': {trading_rules.get('stop_loss_pct', 50)},\n"
        config_str += "        'deltas': {\n"
        config_str += f"            'center_delta': {formatted_deltas.get('center_delta', 0.50)},\n"
        config_str += f"            'wing_width': {formatted_deltas.get('wing_width', 5)}\n"
        config_str += "        },\n"

        config_str += "        " + BaseStrategy.generate_advanced_config_string(advanced_config) + "\n"
        config_str += "    }"

        return config_str

    @staticmethod
    def _generate_strike_selector(advanced_config):
        """Generate strike selection logic"""

        liquidity_enabled = advanced_config.get('liquidity_enabled', True)

        code = '''
class StrikeSelector:
    """Find strikes for Butterfly Spread"""

    @staticmethod
    def find_strikes_by_delta(option_chain, underlying_price, target_deltas, config, algo):
        """Find butterfly strikes (call butterfly by default)"""

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

            calls = expiries[best_expiry]['calls']

            algo.Log(f"[+] Selected expiry: {best_expiry} ({len(calls)} calls)")
'''

        if liquidity_enabled:
            code += '''
            # Filter by liquidity
            liquid_calls = [c for c in calls if LiquidityFilter.check_liquidity(
                c,
                config.advanced['max_spread_pct'],
                config.advanced['min_open_interest']
            )]

            if len(liquid_calls) < 10:
                algo.Log(f"[X] Insufficient liquid contracts (calls: {len(liquid_calls)})")
                return None

            calls = liquid_calls
            algo.Log(f"[+] Liquid contracts: {len(calls)} calls")
'''

        advanced_greeks_enabled = advanced_config.get('advanced_greeks_enabled', False)
        if advanced_greeks_enabled:
            code += '''
            # Advanced Greeks Filter (contract-level)
            if hasattr(algo, 'advanced_greeks_filter'):
                calls = algo.advanced_greeks_filter.filter_contracts(calls)
                if len(calls) < 10:
                    algo.Log(f"[X] Insufficient contracts after Greeks filter (calls: {len(calls)})")
                    return None
                algo.Log(f"[+] After Greeks filter: {len(calls)} calls")
'''

        code += '''
            # Get available strikes sorted
            available_strikes = sorted(set([c.Strike for c in calls]))
            wing_width = target_deltas.get('wing_width', 5)

            # Find ATM strike (closest to underlying)
            atm_strike = min(available_strikes, key=lambda x: abs(x - underlying_price))
            atm_idx = available_strikes.index(atm_strike)

            # Find wings that are equidistant
            lower_strike = None
            upper_strike = None

            # Look for strikes at wing_width apart
            for i, strike in enumerate(available_strikes):
                if strike < atm_strike and (atm_strike - strike) >= wing_width:
                    lower_strike = strike
                if strike > atm_strike and (strike - atm_strike) >= wing_width:
                    upper_strike = strike
                    break

            if not lower_strike or not upper_strike:
                # Fallback: use index-based selection
                if atm_idx >= 2 and atm_idx < len(available_strikes) - 2:
                    lower_strike = available_strikes[atm_idx - 2]
                    upper_strike = available_strikes[atm_idx + 2]
                else:
                    algo.Log("[X] Cannot find suitable butterfly strikes")
                    return None

            # Get contracts for each strike
            lower_call = None
            middle_call = None
            upper_call = None

            for c in calls:
                if c.Strike == lower_strike:
                    lower_call = c
                elif c.Strike == atm_strike:
                    middle_call = c
                elif c.Strike == upper_strike:
                    upper_call = c

            if lower_call and middle_call and upper_call:
                algo.Log(f"[+] Valid Butterfly! {lower_strike}/{atm_strike}/{upper_strike}")
                return {
                    'lower_call': lower_call,
                    'middle_call': middle_call,
                    'upper_call': upper_call
                }

            return None

        except Exception as e:
            algo.Log(f"[X] Strike selection error: {e}")
            return None
'''
        return code

    @staticmethod
    def _generate_strategy_class():
        """Generate strategy class"""

        code = '''
class ButterflySpreadStrategy:
    """Manage Butterfly Spread positions"""

    def __init__(self, algorithm):
        self.algo = algorithm

    def enter_position(self, strikes, underlying_price, time):
        """Enter new Butterfly Spread (DEBIT)"""

        try:
            if self.algo.IsWarmingUp:
                return None

            lower_price = (strikes['lower_call'].BidPrice + strikes['lower_call'].AskPrice) / 2
            middle_price = (strikes['middle_call'].BidPrice + strikes['middle_call'].AskPrice) / 2
            upper_price = (strikes['upper_call'].BidPrice + strikes['upper_call'].AskPrice) / 2

            # Buy 1 lower, Sell 2 middle, Buy 1 upper
            net_debit = (lower_price - 2 * middle_price + upper_price) * 100
            wing_width = strikes['middle_call'].Strike - strikes['lower_call'].Strike
            max_profit = (wing_width * 100) - net_debit
            max_loss = net_debit

            self.algo.Log("")
            self.algo.Log("=" * 60)
            self.algo.Log(">>> ENTERING BUTTERFLY SPREAD")
            self.algo.Log("=" * 60)
            self.algo.Log(f"Underlying: ${underlying_price:.2f}")
            self.algo.Log(f"Strikes: {strikes['lower_call'].Strike}/{strikes['middle_call'].Strike}/{strikes['upper_call'].Strike}")
            self.algo.Log(f"Net Debit: ${net_debit:.2f}")
            self.algo.Log(f"Max Profit: ${max_profit:.2f}")
            self.algo.Log(f"Max Loss: ${max_loss:.2f}")

            self.algo.MarketOrder(strikes['lower_call'].Symbol, 1)   # Buy lower wing
            self.algo.MarketOrder(strikes['middle_call'].Symbol, -2) # Sell 2 middle
            self.algo.MarketOrder(strikes['upper_call'].Symbol, 1)   # Buy upper wing

            self.algo.Log("[+] Orders placed")

            self.algo.position_counter += 1
            pos_id = self.algo.position_counter

            self.algo.positions[pos_id] = {
                'status': 'open',
                'entry_time': time,
                'entry_underlying_price': underlying_price,
                'expiry_date': strikes['lower_call'].Expiry.date(),
                'strikes': strikes,
                'current_pnl': 0,
                'metrics': {
                    'net_debit': net_debit,
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
                    if (contract.Strike == entry_strikes['lower_call'].Strike and
                        contract.Right == OptionRight.CALL and
                        contract.Expiry.date() == entry_strikes['lower_call'].Expiry.date()):
                        current_prices['lc'] = (contract.BidPrice + contract.AskPrice) / 2

                    if (contract.Strike == entry_strikes['middle_call'].Strike and
                        contract.Right == OptionRight.CALL and
                        contract.Expiry.date() == entry_strikes['middle_call'].Expiry.date()):
                        current_prices['mc'] = (contract.BidPrice + contract.AskPrice) / 2

                    if (contract.Strike == entry_strikes['upper_call'].Strike and
                        contract.Right == OptionRight.CALL and
                        contract.Expiry.date() == entry_strikes['upper_call'].Expiry.date()):
                        current_prices['uc'] = (contract.BidPrice + contract.AskPrice) / 2

                if len(current_prices) == 3:
                    current_value = (current_prices['lc'] - 2 * current_prices['mc'] + current_prices['uc']) * 100
                    entry_debit = pos['metrics']['net_debit']
                    return current_value - entry_debit

                break

            return 0

        except Exception as e:
            self.algo.Log(f"[X] P&L calc error: {e}")
            return 0

    def close_position(self, pos_id, reason, time):
        """Close position"""

        try:
            pos = self.algo.positions[pos_id]
            strikes = pos['strikes']

            self.algo.MarketOrder(strikes['lower_call'].Symbol, -1)
            self.algo.MarketOrder(strikes['middle_call'].Symbol, 2)
            self.algo.MarketOrder(strikes['upper_call'].Symbol, -1)

            final_pnl = pos['current_pnl']
            mae = pos['metrics']['mae']
            mfe = pos['metrics']['mfe']
            max_loss = pos['metrics']['max_loss']
            duration = (time.date() - pos['entry_time'].date()).days

            mae_pct = (mae / max_loss * 100) if max_loss > 0 else 0
            mfe_pct = (mfe / max_loss * 100) if mfe > 0 else 0

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

        filter_init = BaseStrategy.generate_filter_initialization(advanced_config)
        filter_checks = BaseStrategy.generate_filter_checks(advanced_config)

        code = f'''
class OptionsBacktest(QCAlgorithm):
    """Butterfly Spread Backtesting Algorithm"""

    {initialize_code}



        # Initialize advanced filters
{filter_init}

        self.Log("=" * 60)
        self.Log("Strategy: Butterfly Spread")
        self.Log(f"Ticker: {{config.ticker}}")
        self.Log(f"Expiry: {{config.expiry_days}} days (±{{config.expiry_range}} day window)")
        self.Log(f"Expiration Cycle: {{self.config.advanced['expiration_cycle']}}")
        self.Log(f"Resolution: {{config.resolution.upper()}}")
        self.Log(f"Max Positions: {{config.max_positions}}")
        self.Log(f"Profit Target: {{config.profit_target_pct}}%")
        self.Log(f"Stop Loss: {{config.stop_loss_mode}} mode ({{config.stop_loss_pct}}%)")
        self.Log(f"Wing Width: {{config.deltas.get('wing_width', 5)}} points")
        if self.config.advanced['liquidity_enabled']:
            self.Log(f"Liquidity Filter: Max Spread {{self.config.advanced['max_spread_pct']}}%, Min OI {{self.config.advanced['min_open_interest']}}")
        self.Log("=" * 60)
        self.Log("[+] Ready!")

        self.strategy = ButterflySpreadStrategy(self)

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
