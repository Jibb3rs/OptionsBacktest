"""
Calendar Spread Strategy
Sell near-term option + Buy far-term option at same strike
Profits from time decay difference between expirations
"""

from .base_strategy import BaseStrategy

class CalendarSpread(BaseStrategy):
    """Calendar Spread - Time decay play"""

    strategy_direction = 'neutral'

    @staticmethod
    def generate_code(config):
        """Generate complete Calendar Spread algorithm"""

        trading_rules = config.get('trading_rules', {})
        strike_selection = config.get('strike_selection', {})
        indicators_config = config.get('indicators', {})
        advanced_config = config.get('advanced', {})

        # Calendar spread parameters
        formatted_deltas = {
            'strike_delta': 0.50,  # ATM strike
            'near_expiry_days': 30,
            'far_expiry_days': 60
        }

        # Override with user settings if available
        deltas_raw = strike_selection.get('deltas', {})
        if 'Strike Delta:' in deltas_raw:
            formatted_deltas['strike_delta'] = deltas_raw['Strike Delta:']

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

        config_json = CalendarSpread._build_config_json(config, formatted_deltas, stop_loss_mode, advanced_config)

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
        indicator_manager = BaseStrategy.generate_indicator_manager(indicators_config, CalendarSpread.strategy_direction)
        advanced_filters = BaseStrategy.generate_advanced_filters(advanced_config)
        strike_selector = CalendarSpread._generate_strike_selector(advanced_config)
        strategy_class = CalendarSpread._generate_strategy_class()
        main_algorithm = CalendarSpread._generate_main_algorithm(flat_config, advanced_config)

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
        config_str += f"        'strategy': 'Calendar Spread',\n"
        config_str += f"        'expiry_days': {config.get('expiry_days', 30)},\n"
        config_str += f"        'expiry_range': {config.get('expiry_range', 5)},\n"
        config_str += f"        'resolution': '{trading_rules.get('resolution', 'Daily')}',\n"
        config_str += f"        'max_positions': {trading_rules.get('max_positions', 5)},\n"
        config_str += f"        'min_days_between_trades': {trading_rules.get('min_days_between_trades', 0)},\n"
        config_str += f"        'profit_target_pct': {trading_rules.get('profit_target_pct', 100)},\n"
        config_str += f"        'stop_loss_mode': '{stop_loss_mode}',\n"
        config_str += f"        'stop_loss_pct': {trading_rules.get('stop_loss_pct', 50)},\n"
        config_str += "        'deltas': {\n"
        config_str += f"            'strike_delta': {formatted_deltas.get('strike_delta', 0.50)},\n"
        config_str += f"            'near_expiry_days': {formatted_deltas.get('near_expiry_days', 30)},\n"
        config_str += f"            'far_expiry_days': {formatted_deltas.get('far_expiry_days', 60)}\n"
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
    """Find strikes for Calendar Spread"""

    @staticmethod
    def find_strikes_by_delta(option_chain, underlying_price, target_deltas, config, algo):
        """Find calendar spread strikes (same strike, different expiries)"""

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

            # Sort expiries by date
            sorted_expiries = sorted(expiries.keys())

            if len(sorted_expiries) < 2:
                algo.Log("[X] Need at least 2 expiry dates for calendar spread")
                return None

            # Find near-term and far-term expiries
            near_expiry = sorted_expiries[0]
            far_expiry = None

            # Find far expiry that is at least 20 days after near
            for exp in sorted_expiries[1:]:
                days_diff = (exp - near_expiry).days
                if days_diff >= 20:
                    far_expiry = exp
                    break

            if not far_expiry:
                far_expiry = sorted_expiries[-1]

            algo.Log(f"[+] Expiries: Near={near_expiry}, Far={far_expiry}")

            near_calls = expiries[near_expiry]['calls']
            far_calls = expiries[far_expiry]['calls']
'''

        if liquidity_enabled:
            code += '''
            # Filter by liquidity
            liquid_near = [c for c in near_calls if LiquidityFilter.check_liquidity(
                c,
                config.advanced['max_spread_pct'],
                config.advanced['min_open_interest']
            )]

            liquid_far = [c for c in far_calls if LiquidityFilter.check_liquidity(
                c,
                config.advanced['max_spread_pct'],
                config.advanced['min_open_interest']
            )]

            if len(liquid_near) < 5 or len(liquid_far) < 5:
                algo.Log(f"[X] Insufficient liquid contracts (near: {len(liquid_near)}, far: {len(liquid_far)})")
                return None

            near_calls = liquid_near
            far_calls = liquid_far
            algo.Log(f"[+] Liquid contracts: {len(near_calls)} near, {len(far_calls)} far")
'''

        advanced_greeks_enabled = advanced_config.get('advanced_greeks_enabled', False)
        if advanced_greeks_enabled:
            code += '''
            # Advanced Greeks Filter (contract-level)
            if hasattr(algo, 'advanced_greeks_filter'):
                near_calls = algo.advanced_greeks_filter.filter_contracts(near_calls)
                far_calls = algo.advanced_greeks_filter.filter_contracts(far_calls)
                if len(near_calls) < 5 or len(far_calls) < 5:
                    algo.Log(f"[X] Insufficient contracts after Greeks filter")
                    return None
'''

        code += '''
            # Find ATM strike that exists in both expiries
            near_strikes = set([c.Strike for c in near_calls])
            far_strikes = set([c.Strike for c in far_calls])
            common_strikes = near_strikes & far_strikes

            if not common_strikes:
                algo.Log("[X] No common strikes between expiries")
                return None

            # Find ATM strike
            atm_strike = min(common_strikes, key=lambda x: abs(x - underlying_price))

            # Get contracts
            short_call = None
            long_call = None

            for c in near_calls:
                if c.Strike == atm_strike:
                    short_call = c
                    break

            for c in far_calls:
                if c.Strike == atm_strike:
                    long_call = c
                    break

            if short_call and long_call:
                algo.Log(f"[+] Valid Calendar! Strike: {atm_strike}, Near: {near_expiry}, Far: {far_expiry}")
                return {
                    'short_call': short_call,
                    'long_call': long_call
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
class CalendarSpreadStrategy:
    """Manage Calendar Spread positions"""

    def __init__(self, algorithm):
        self.algo = algorithm

    def enter_position(self, strikes, underlying_price, time):
        """Enter new Calendar Spread (DEBIT)"""

        try:
            if self.algo.IsWarmingUp:
                return None

            short_call_price = (strikes['short_call'].BidPrice + strikes['short_call'].AskPrice) / 2
            long_call_price = (strikes['long_call'].BidPrice + strikes['long_call'].AskPrice) / 2

            # Buy far-term (long_call), Sell near-term (short_call)
            net_debit = (long_call_price - short_call_price) * 100
            max_loss = net_debit  # Max loss if stock moves significantly
            max_profit = 999999   # Theoretical (depends on IV and price)

            self.algo.Log("")
            self.algo.Log("=" * 60)
            self.algo.Log(">>> ENTERING CALENDAR SPREAD")
            self.algo.Log("=" * 60)
            self.algo.Log(f"Underlying: ${underlying_price:.2f}")
            self.algo.Log(f"Strike: {strikes['short_call'].Strike}")
            self.algo.Log(f"Near Expiry: {strikes['short_call'].Expiry.date()}")
            self.algo.Log(f"Far Expiry: {strikes['long_call'].Expiry.date()}")
            self.algo.Log(f"Net Debit: ${net_debit:.2f}")
            self.algo.Log(f"Max Loss: ${max_loss:.2f}")

            self.algo.MarketOrder(strikes['long_call'].Symbol, 1)   # Buy far-term
            self.algo.MarketOrder(strikes['short_call'].Symbol, -1) # Sell near-term

            self.algo.Log("[+] Orders placed")

            self.algo.position_counter += 1
            pos_id = self.algo.position_counter

            self.algo.positions[pos_id] = {
                'status': 'open',
                'entry_time': time,
                'entry_underlying_price': underlying_price,
                'expiry_date': strikes['short_call'].Expiry.date(),  # Track near-term expiry
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
                    # Short call (near-term)
                    if (contract.Strike == entry_strikes['short_call'].Strike and
                        contract.Right == OptionRight.CALL and
                        contract.Expiry.date() == entry_strikes['short_call'].Expiry.date()):
                        current_prices['sc'] = (contract.BidPrice + contract.AskPrice) / 2

                    # Long call (far-term)
                    if (contract.Strike == entry_strikes['long_call'].Strike and
                        contract.Right == OptionRight.CALL and
                        contract.Expiry.date() == entry_strikes['long_call'].Expiry.date()):
                        current_prices['lc'] = (contract.BidPrice + contract.AskPrice) / 2

                if len(current_prices) == 2:
                    current_value = (current_prices['lc'] - current_prices['sc']) * 100
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

            self.algo.MarketOrder(strikes['long_call'].Symbol, -1)
            self.algo.MarketOrder(strikes['short_call'].Symbol, 1)

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
    """Calendar Spread Backtesting Algorithm"""

    {initialize_code}



        # Initialize advanced filters
{filter_init}

        self.Log("=" * 60)
        self.Log("Strategy: Calendar Spread")
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

        self.strategy = CalendarSpreadStrategy(self)

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
