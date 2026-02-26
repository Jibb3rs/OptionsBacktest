"""
Base Strategy - Common logic shared by all strategies
"""

from datetime import timedelta

class BaseStrategy:
    """Base class for all options strategies"""
    
    @staticmethod
    def generate_imports():
        """Common imports for all strategies"""
        return """from AlgorithmImports import *
import numpy as np
from datetime import datetime, timedelta"""
    
    @staticmethod
    def generate_config_loader():
        """Embedded configuration loader"""
        return """
class Config:
    \"\"\"Embedded configuration\"\"\"
    def __init__(self, config_dict):
        for key, value in config_dict.items():
            setattr(self, key, value)

def load_config():
    \"\"\"Load embedded configuration\"\"\"
    config_dict = {CONFIG_PLACEHOLDER}
    return Config(config_dict)
"""
    
    @staticmethod
    def generate_indicator_manager(indicators_config, strategy_direction='neutral'):
        """
        Generate indicator manager code with strategy direction awareness

        Args:
            indicators_config: Dict of indicator settings from advanced_tab
            strategy_direction: 'bullish', 'bearish', or 'neutral'
        """

        # Check if any indicators are enabled
        enabled_indicators = {k: v for k, v in indicators_config.items()
                            if isinstance(v, dict) and v.get('enabled', False)}

        if not enabled_indicators:
            return """
class IndicatorManager:
    \"\"\"No indicators enabled\"\"\"
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def initialize_indicators(self, symbol):
        \"\"\"No indicators to initialize\"\"\"
        self.algorithm.Log("[+] No indicators enabled")

    def should_enter_trade(self, symbol):
        return True, "No indicator filters"
"""

        # Generate indicator initialization code
        init_code = []
        for indicator_key, config in enabled_indicators.items():
            init_line = BaseStrategy._generate_indicator_init(indicator_key, config)
            if init_line:
                init_code.append(init_line)

        # Generate condition checking code
        check_code = BaseStrategy._generate_indicator_checks(enabled_indicators, strategy_direction)

        return f"""
class IndicatorManager:
    \"\"\"Manages technical indicators for trade filtering\"\"\"
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.indicators = {{}}
        self.strategy_direction = '{strategy_direction}'

    def initialize_indicators(self, symbol):
        \"\"\"Initialize all enabled indicators\"\"\"
        self.algorithm.Log("[+] Initializing indicators...")

{chr(10).join('        ' + line for line in init_code)}

        self.algorithm.Log(f"[+] Initialized {{len(self.indicators)}} indicators\\n")

    def should_enter_trade(self, symbol):
        \"\"\"
        Check if indicator conditions allow trade entry
        Returns: (allowed: bool, reason: str)
        \"\"\"
        reasons = []

{check_code}

        # All checks passed
        return True, " | ".join(reasons) if reasons else "All indicators OK"
"""

    @staticmethod
    def _generate_indicator_init(indicator_key, config):
        """Generate initialization code for a specific indicator"""

        period = config.get('period', 14)

        # For MA, pick SMA or EMA based on ma_type config
        if indicator_key == 'MA':
            ma_func = 'EMA' if config.get('ma_type', 'SMA') == 'EMA' else 'SMA'
            return (f"self.indicators['MA'] = self.algorithm.{ma_func}(symbol, {period})\n"
                    f"        self.algorithm.Log('   +MA ({ma_func}-{period})')")

        init_map = {
            'RSI': f"self.indicators['RSI'] = self.algorithm.RSI(symbol, {period})",
            'ATR': f"self.indicators['ATR'] = self.algorithm.ATR(symbol, {period})",
            'MACD': f"self.indicators['MACD'] = self.algorithm.MACD(symbol, {config.get('fast', 12)}, {config.get('slow', 26)}, {config.get('signal', 9)})",
            'STOCHASTIC': f"self.indicators['STOCHASTIC'] = self.algorithm.STO(symbol, {period}, {config.get('k_smooth', 3)}, 3, Resolution.Daily)",
            'BBANDS': f"self.indicators['BBANDS'] = self.algorithm.BB(symbol, {period}, {config.get('std_dev', 2)})",
            'ADX': f"self.indicators['ADX'] = self.algorithm.ADX(symbol, {period})",
            'VWAP': f"self.indicators['VWAP'] = self.algorithm.VWAP(symbol)",
        }

        # VIX needs special handling
        if indicator_key == 'VIX':
            return """try:
            self.indicators['VIX'] = self.algorithm.AddIndex("VIX", 1)
            self.algorithm.Log("   +VIX")
        except:
            self.algorithm.Log("   [!]  VIX not available")"""

        if indicator_key in init_map:
            return f"{init_map[indicator_key]}\n        self.algorithm.Log('   +{indicator_key}')"

        return None

    @staticmethod
    def _generate_indicator_checks(enabled_indicators, strategy_direction):
        """Generate condition checking code based on strategy direction"""

        check_lines = []

        for indicator_key, config in enabled_indicators.items():
            if indicator_key == 'RSI':
                check_lines.append(BaseStrategy._generate_rsi_check(config, strategy_direction))
            elif indicator_key == 'MACD':
                check_lines.append(BaseStrategy._generate_macd_check(config, strategy_direction))
            elif indicator_key == 'STOCHASTIC':
                check_lines.append(BaseStrategy._generate_stochastic_check(config, strategy_direction))
            elif indicator_key == 'ATR':
                check_lines.append(BaseStrategy._generate_atr_check(config))
            elif indicator_key == 'BBANDS':
                check_lines.append(BaseStrategy._generate_bbands_check(config, strategy_direction))
            elif indicator_key == 'MA':
                check_lines.append(BaseStrategy._generate_ma_check(config, strategy_direction))
            elif indicator_key == 'ADX':
                check_lines.append(BaseStrategy._generate_adx_check(config))
            elif indicator_key == 'VWAP':
                check_lines.append(BaseStrategy._generate_vwap_check(config, strategy_direction))

        return '\n'.join('        ' + line for line in check_lines)

    @staticmethod
    def _generate_rsi_check(config, strategy_direction):
        """Generate RSI check code — condition is auto-determined from strategy direction"""
        oversold = config.get('oversold', 30)
        overbought = config.get('overbought', 70)

        if strategy_direction == 'bullish':
            return f"""# RSI Check (bullish: wait for oversold)
        if 'RSI' in self.indicators and self.indicators['RSI'].IsReady:
            rsi_value = self.indicators['RSI'].Current.Value
            if rsi_value < {oversold}:
                reasons.append(f"RSI oversold ({{rsi_value:.1f}} < {oversold}) - BUY SIGNAL")
            else:
                return False, f"RSI not oversold ({{rsi_value:.1f}} >= {oversold})"
"""
        elif strategy_direction == 'bearish':
            return f"""# RSI Check (bearish: wait for overbought)
        if 'RSI' in self.indicators and self.indicators['RSI'].IsReady:
            rsi_value = self.indicators['RSI'].Current.Value
            if rsi_value > {overbought}:
                reasons.append(f"RSI overbought ({{rsi_value:.1f}} > {overbought}) - SELL SIGNAL")
            else:
                return False, f"RSI not overbought ({{rsi_value:.1f}} <= {overbought})"
"""
        else:  # neutral strategy
            return f"""# RSI Check (neutral: require price within range)
        if 'RSI' in self.indicators and self.indicators['RSI'].IsReady:
            rsi_value = self.indicators['RSI'].Current.Value
            if {oversold} < rsi_value < {overbought}:
                reasons.append(f"RSI neutral ({{rsi_value:.1f}})")
            else:
                return False, f"RSI extreme ({{rsi_value:.1f}})"
"""

    @staticmethod
    def _generate_macd_check(config, strategy_direction):
        """Generate MACD check code — condition auto-determined from strategy direction"""
        if strategy_direction == 'bullish':
            return """# MACD Check (bullish: MACD above signal)
        if 'MACD' in self.indicators and self.indicators['MACD'].IsReady:
            macd = self.indicators['MACD'].Current.Value
            signal = self.indicators['MACD'].Signal.Current.Value
            if macd > signal:
                reasons.append(f"MACD bullish ({macd:.2f} > {signal:.2f}) - BUY SIGNAL")
            else:
                return False, f"MACD bearish ({macd:.2f} < {signal:.2f})"
"""
        elif strategy_direction == 'bearish':
            return """# MACD Check (bearish: MACD below signal)
        if 'MACD' in self.indicators and self.indicators['MACD'].IsReady:
            macd = self.indicators['MACD'].Current.Value
            signal = self.indicators['MACD'].Signal.Current.Value
            if macd < signal:
                reasons.append(f"MACD bearish ({macd:.2f} < {signal:.2f}) - SELL SIGNAL")
            else:
                return False, f"MACD bullish ({macd:.2f} > {signal:.2f})"
"""
        else:  # neutral
            return """# MACD Check (neutral: MACD close to signal)
        if 'MACD' in self.indicators and self.indicators['MACD'].IsReady:
            macd = self.indicators['MACD'].Current.Value
            signal = self.indicators['MACD'].Signal.Current.Value
            if abs(macd - signal) < 0.5:
                reasons.append(f"MACD neutral ({macd:.2f} vs {signal:.2f})")
            else:
                return False, f"MACD trending ({macd:.2f} vs {signal:.2f})"
"""

    @staticmethod
    def _generate_stochastic_check(config, strategy_direction):
        """Generate Stochastic check code"""
        oversold = config.get('oversold', 20)
        overbought = config.get('overbought', 80)

        if strategy_direction == 'bullish':
            return f"""# Stochastic Check
        if 'STOCHASTIC' in self.indicators and self.indicators['STOCHASTIC'].IsReady:
            stoch_value = self.indicators['STOCHASTIC'].Current.Value
            if stoch_value < {oversold}:
                reasons.append(f"Stochastic oversold ({{stoch_value:.1f}}) - BUY SIGNAL")
            else:
                return False, f"Stochastic not oversold ({{stoch_value:.1f}} >= {oversold})"
"""
        elif strategy_direction == 'bearish':
            return f"""# Stochastic Check
        if 'STOCHASTIC' in self.indicators and self.indicators['STOCHASTIC'].IsReady:
            stoch_value = self.indicators['STOCHASTIC'].Current.Value
            if stoch_value > {overbought}:
                reasons.append(f"Stochastic overbought ({{stoch_value:.1f}}) - SELL SIGNAL")
            else:
                return False, f"Stochastic not overbought ({{stoch_value:.1f}} <= {overbought})"
"""
        else:
            return f"""# Stochastic Check
        if 'STOCHASTIC' in self.indicators and self.indicators['STOCHASTIC'].IsReady:
            stoch_value = self.indicators['STOCHASTIC'].Current.Value
            if {oversold} < stoch_value < {overbought}:
                reasons.append(f"Stochastic neutral ({{stoch_value:.1f}})")
            else:
                return False, f"Stochastic extreme ({{stoch_value:.1f}})"
"""

    @staticmethod
    def _generate_atr_check(config):
        """Generate ATR check code"""
        threshold = config.get('threshold', 1.5)
        condition = config.get('condition', 'high')

        if condition == 'high':
            return f"""# ATR Check (High Volatility)
        if 'ATR' in self.indicators and self.indicators['ATR'].IsReady:
            atr_value = self.indicators['ATR'].Current.Value
            underlying_price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            atr_pct = (atr_value / underlying_price) * 100
            if atr_pct > {threshold}:
                reasons.append(f"ATR high ({{atr_pct:.2f}}%)")
            else:
                return False, f"ATR too low ({{atr_pct:.2f}}% < {threshold}%)"
"""
        else:  # low
            return f"""# ATR Check (Low Volatility)
        if 'ATR' in self.indicators and self.indicators['ATR'].IsReady:
            atr_value = self.indicators['ATR'].Current.Value
            underlying_price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            atr_pct = (atr_value / underlying_price) * 100
            if atr_pct < {threshold}:
                reasons.append(f"ATR low ({{atr_pct:.2f}}%)")
            else:
                return False, f"ATR too high ({{atr_pct:.2f}}% > {threshold}%)"
"""

    @staticmethod
    def _generate_bbands_check(config, strategy_direction):
        """Generate Bollinger Bands check code"""
        condition = config.get('condition', 'inside_bands')

        if strategy_direction == 'bullish' and condition == 'below_lower':
            return """# Bollinger Bands Check
        if 'BBANDS' in self.indicators and self.indicators['BBANDS'].IsReady:
            price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            lower_band = self.indicators['BBANDS'].LowerBand.Current.Value
            if price <= lower_band:
                reasons.append(f"Price below lower BB - BUY SIGNAL")
            else:
                return False, f"Price not below lower BB"
"""
        elif strategy_direction == 'bearish' and condition == 'above_upper':
            return """# Bollinger Bands Check
        if 'BBANDS' in self.indicators and self.indicators['BBANDS'].IsReady:
            price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            upper_band = self.indicators['BBANDS'].UpperBand.Current.Value
            if price >= upper_band:
                reasons.append(f"Price above upper BB - SELL SIGNAL")
            else:
                return False, f"Price not above upper BB"
"""
        else:  # inside_bands for neutral
            return """# Bollinger Bands Check
        if 'BBANDS' in self.indicators and self.indicators['BBANDS'].IsReady:
            price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            lower_band = self.indicators['BBANDS'].LowerBand.Current.Value
            upper_band = self.indicators['BBANDS'].UpperBand.Current.Value
            if lower_band < price < upper_band:
                reasons.append("Price inside Bollinger Bands")
            else:
                return False, f"Price outside Bollinger Bands"
"""

    @staticmethod
    def _generate_ma_check(config, strategy_direction):
        """Generate unified Moving Average check code (SMA or EMA based on ma_type in config)"""
        ma_label = config.get('ma_type', 'SMA')

        if strategy_direction == 'bullish':
            return f"""# MA Check (bullish: price above MA)
        if 'MA' in self.indicators and self.indicators['MA'].IsReady:
            price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            ma_value = self.indicators['MA'].Current.Value
            if price > ma_value:
                reasons.append(f"Price above {ma_label} ({{price:.2f}} > {{ma_value:.2f}}) - BUY SIGNAL")
            else:
                return False, f"Price below {ma_label} ({{price:.2f}} < {{ma_value:.2f}})"
"""
        elif strategy_direction == 'bearish':
            return f"""# MA Check (bearish: price below MA)
        if 'MA' in self.indicators and self.indicators['MA'].IsReady:
            price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            ma_value = self.indicators['MA'].Current.Value
            if price < ma_value:
                reasons.append(f"Price below {ma_label} ({{price:.2f}} < {{ma_value:.2f}}) - SELL SIGNAL")
            else:
                return False, f"Price above {ma_label} ({{price:.2f}} > {{ma_value:.2f}})"
"""
        else:
            return f"""# MA Check (neutral: log value)
        if 'MA' in self.indicators and self.indicators['MA'].IsReady:
            ma_value = self.indicators['MA'].Current.Value
            reasons.append(f"{ma_label}: {{ma_value:.2f}}")
"""

    @staticmethod
    def _generate_adx_check(config):
        """Generate ADX check code"""
        threshold = config.get('threshold', 25)
        condition = config.get('condition', 'strong')

        if condition == 'strong':
            return f"""# ADX Check (Strong Trend)
        if 'ADX' in self.indicators and self.indicators['ADX'].IsReady:
            adx_value = self.indicators['ADX'].Current.Value
            if adx_value > {threshold}:
                reasons.append(f"ADX strong trend ({{adx_value:.1f}})")
            else:
                return False, f"ADX weak trend ({{adx_value:.1f}} < {threshold})"
"""
        else:  # weak
            return f"""# ADX Check (Weak Trend)
        if 'ADX' in self.indicators and self.indicators['ADX'].IsReady:
            adx_value = self.indicators['ADX'].Current.Value
            if adx_value < {threshold}:
                reasons.append(f"ADX weak trend ({{adx_value:.1f}})")
            else:
                return False, f"ADX strong trend ({{adx_value:.1f}} > {threshold})"
"""

    @staticmethod
    def _generate_vwap_check(config, strategy_direction):
        """Generate VWAP check code using explicit condition from config"""
        # Use explicit user-selected condition; fall back to strategy direction
        condition = config.get('condition')
        if not condition:
            condition = 'above' if strategy_direction == 'bullish' else 'below'

        if condition == 'above':
            return """# VWAP Check (price above VWAP)
        if 'VWAP' in self.indicators and self.indicators['VWAP'].IsReady:
            price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            vwap_value = self.indicators['VWAP'].Current.Value
            if price > vwap_value:
                reasons.append(f"Price above VWAP ({price:.2f} > {vwap_value:.2f})")
            else:
                return False, f"Price below VWAP ({price:.2f} < {vwap_value:.2f})"
"""
        else:  # below
            return """# VWAP Check (price below VWAP)
        if 'VWAP' in self.indicators and self.indicators['VWAP'].IsReady:
            price = self.algorithm.Securities[self.algorithm.config.ticker].Price
            vwap_value = self.indicators['VWAP'].Current.Value
            if price < vwap_value:
                reasons.append(f"Price below VWAP ({price:.2f} < {vwap_value:.2f})")
            else:
                return False, f"Price above VWAP ({price:.2f} > {vwap_value:.2f})"
"""

    @staticmethod
    def generate_advanced_filters(advanced_config):
        """
        Generate advanced filter code based on configuration.
        Only includes filter classes that are actually needed to keep
        generated code within QuantConnect's 32KB file size limit.

        LiquidityFilter and ExpirationFilter are always included since
        they are referenced by the strike selector with default settings.
        """

        if advanced_config is None:
            advanced_config = {}

        # Map of filter flag -> class name(s) needed
        # LiquidityFilter and ExpirationFilter are always required
        always_needed = {'ExpirationFilter', 'LiquidityFilter'}

        optional_filters = {
            'vix_enabled': {'VIXFilter'},
            'iv_rank_enabled': {'IVRankFilter'},
            'market_profile_enabled': {'MarketProfileIndicator'},
            'vol_regime_enabled': {'VolatilityRegimeFilter'},
            'greeks_enabled': {'PortfolioGreeksFilter'},
            'dynamic_sizing_enabled': {'DynamicPositionSizer'},
            'correlation_enabled': {'CorrelationFilter'},
            'earnings_enabled': {'EarningsFilter'},
            'mtf_enabled': {'MultiTimeframeFilter'},
            'advanced_greeks_enabled': {'AdvancedGreeksFilter'},
        }

        needed_classes = set(always_needed)
        for flag, classes in optional_filters.items():
            if advanced_config.get(flag, False):
                needed_classes.update(classes)

        filters_code = "\nfrom datetime import timedelta\n\n"

        # Read advanced_filters.py and extract only needed classes
        try:
            from core.paths import resource_path
            filters_file = resource_path('strategies/advanced_filters.py')

            with open(filters_file, 'r') as f:
                all_lines = f.readlines()

            # Parse the file into class blocks
            class_blocks = {}
            current_class = None
            current_lines = []

            for line in all_lines:
                if line.startswith('class '):
                    # Save previous class block
                    if current_class:
                        class_blocks[current_class] = ''.join(current_lines)
                    # Start new class
                    current_class = line.split('(')[0].replace('class ', '').split(':')[0].strip()
                    current_lines = [line]
                elif current_class:
                    current_lines.append(line)

            # Save last class block
            if current_class:
                class_blocks[current_class] = ''.join(current_lines)

            # Include only needed classes
            for class_name in needed_classes:
                if class_name in class_blocks:
                    filters_code += class_blocks[class_name] + '\n\n'

        except Exception as e:
            # Fallback: return empty if file not found
            print(f"Warning: Could not load advanced_filters.py: {e}")
            return ""

        return filters_code

    @staticmethod
    def generate_advanced_config_string(advanced_config):
        """
        Generate the advanced configuration string for embedding in generated code
        This is used by all strategies in their _build_config_json() methods
        """
        if not advanced_config:
            advanced_config = {}

        config_str = "'advanced': {\n"

        # VIX Filter
        config_str += f"            'vix_enabled': {str(advanced_config.get('vix_enabled', False))},\n"
        config_str += f"            'vix_min': {advanced_config.get('vix_min', 15)},\n"
        config_str += f"            'vix_max': {advanced_config.get('vix_max', 50)},\n"

        # Existing filters
        config_str += f"            'iv_rank_enabled': {str(advanced_config.get('iv_rank_enabled', False))},\n"
        config_str += f"            'iv_rank_min': {advanced_config.get('iv_rank_min', 50)},\n"
        config_str += f"            'iv_rank_max': {advanced_config.get('iv_rank_max', 100)},\n"
        config_str += f"            'market_profile_enabled': {str(advanced_config.get('market_profile_enabled', False))},\n"
        config_str += f"            'market_profile_signal': '{advanced_config.get('market_profile_signal', 'poc')}',\n"
        config_str += f"            'market_profile_lookback': {advanced_config.get('market_profile_lookback', 20)},\n"
        config_str += f"            'vol_regime_enabled': {str(advanced_config.get('vol_regime_enabled', False))},\n"
        config_str += f"            'vol_regime_type': '{advanced_config.get('vol_regime_type', 'any')}',\n"
        config_str += f"            'expiration_cycle': '{advanced_config.get('expiration_cycle', 'any')}',\n"

        # Multi-Timeframe Filter
        config_str += f"            'mtf_enabled': {str(advanced_config.get('mtf_enabled', False))},\n"
        mtf_timeframes = advanced_config.get('mtf_timeframes', [])
        config_str += f"            'mtf_timeframes': {repr(mtf_timeframes)},\n"
        config_str += f"            'mtf_require_all': {str(advanced_config.get('mtf_require_all', True))},\n"

        # Dynamic Position Sizing
        config_str += f"            'dynamic_sizing_enabled': {str(advanced_config.get('dynamic_sizing_enabled', False))},\n"
        config_str += f"            'sizing_method': '{advanced_config.get('sizing_method', 'fixed_fractional')}',\n"
        config_str += f"            'sizing_risk_pct': {advanced_config.get('sizing_risk_pct', 2.0)},\n"

        # Portfolio Greeks
        config_str += f"            'greeks_enabled': {str(advanced_config.get('greeks_enabled', False))},\n"
        config_str += f"            'max_portfolio_delta': {advanced_config.get('max_portfolio_delta', 100.0)},\n"
        config_str += f"            'max_portfolio_gamma': {advanced_config.get('max_portfolio_gamma', 0.5)},\n"
        config_str += f"            'max_portfolio_vega': {advanced_config.get('max_portfolio_vega', 50.0)},\n"

        # Correlation Filter
        config_str += f"            'correlation_enabled': {str(advanced_config.get('correlation_enabled', False))},\n"
        config_str += f"            'max_correlation': {advanced_config.get('correlation_threshold', advanced_config.get('max_correlation', 0.7))},\n"
        config_str += f"            'correlation_lookback': {advanced_config.get('correlation_lookback', 60)},\n"

        # Liquidity Filter
        config_str += f"            'liquidity_enabled': {str(advanced_config.get('liquidity_enabled', True))},\n"
        config_str += f"            'max_spread_pct': {advanced_config.get('max_spread_pct', 5)},\n"
        config_str += f"            'min_open_interest': {advanced_config.get('min_open_interest', 100)},\n"

        # Advanced Greeks Filters (Contract-Level)
        config_str += f"            'advanced_greeks_enabled': {str(advanced_config.get('advanced_greeks_enabled', False))},\n"
        config_str += f"            'gamma_filter_enabled': {str(advanced_config.get('gamma_filter_enabled', False))},\n"
        config_str += f"            'max_gamma': {advanced_config.get('max_gamma', 0.05)}\n"

        config_str += "        }"

        return config_str

    @staticmethod
    def _parse_mtf_timeframes(raw, indicator='SMA', condition='above', base_period=None):
        """Convert GUI timeframe string to list of dicts for MultiTimeframeFilter."""
        res_map = {
            '1H': 'Hour', '4H': 'Hour', 'H': 'Hour',
            'Daily': 'Daily', 'D': 'Daily', 'Day': 'Daily',
            'Weekly': 'Daily', 'W': 'Daily',
            'Minute': 'Minute', 'M': 'Minute', 'Hour': 'Hour',
        }
        # Scale multiplier: shorter TF = 1x, longer TF = larger multiple
        scale_map = {'1H': 1, 'H': 1, '4H': 2, 'Daily': 1, 'D': 1, 'Day': 1, 'Weekly': 4, 'W': 4}
        default_period = {'SMA': 50, 'EMA': 50, 'RSI': 14, 'ADX': 14}.get(indicator, 50)
        if base_period is None:
            base_period = default_period

        if isinstance(raw, list):
            if raw and isinstance(raw[0], dict):
                return raw
            parts = [s.strip() for s in raw]
        elif isinstance(raw, str):
            parts = [p.strip() for p in raw.split('+')]
        else:
            return []

        scales = [scale_map.get(p, 1) for p in parts]
        min_scale = min(scales) if scales else 1
        result = []
        for part, scale in zip(parts, scales):
            period = int(base_period * scale / min_scale)
            result.append({'resolution': res_map.get(part, 'Daily'), 'indicator': indicator,
                           'period': period, 'condition': condition})
        return result

    @staticmethod
    def generate_filter_initialization(advanced_config):
        """
        Generate filter initialization code for __init__ method
        This is used by all strategies in their _generate_main_algorithm() methods
        """
        if not advanced_config:
            return ""

        filter_init = ""

        # VIX Filter
        if advanced_config.get('vix_enabled'):
            filter_init += "        self.vix_filter = VIXFilter(self)\n"
            filter_init += "        self.Log('[+] VIX filter enabled')\n"

        # Existing filters
        if advanced_config.get('iv_rank_enabled'):
            filter_init += "        self.iv_rank_filter = IVRankFilter(self)\n"
            filter_init += "        self.Log('[+] IV Rank filter enabled')\n"

        if advanced_config.get('market_profile_enabled'):
            lookback = advanced_config.get('market_profile_lookback', 20)
            filter_init += f"        self.market_profile = MarketProfileIndicator(self, {lookback})\n"
            filter_init += "        self.Log('[+] Market Profile filter enabled')\n"

        if advanced_config.get('vol_regime_enabled'):
            filter_init += "        self.vol_regime = VolatilityRegimeFilter(self)\n"
            filter_init += "        self.Log('[+] Volatility Regime filter enabled')\n"

        # New filters
        if advanced_config.get('greeks_enabled'):
            filter_init += "        self.greeks_filter = PortfolioGreeksFilter(self)\n"
            max_delta = advanced_config.get('max_portfolio_delta', 100.0)
            max_gamma = advanced_config.get('max_portfolio_gamma', 0.5)
            max_vega = advanced_config.get('max_portfolio_vega', 50.0)
            filter_init += f"        self.greeks_filter.configure(max_delta={max_delta}, max_gamma={max_gamma}, max_vega={max_vega})\n"
            filter_init += "        self.Log('[+] Portfolio Greeks filter enabled')\n"

        if advanced_config.get('dynamic_sizing_enabled'):
            filter_init += "        self.position_sizer = DynamicPositionSizer(self)\n"
            method = advanced_config.get('sizing_method', 'fixed_fractional')
            risk_pct = advanced_config.get('sizing_risk_pct', 2.0)
            filter_init += f"        self.position_sizer.configure(method='{method}', risk_pct={risk_pct})\n"
            filter_init += "        self.Log('[+] Dynamic position sizing enabled')\n"

        if advanced_config.get('correlation_enabled'):
            filter_init += "        self.correlation_filter = CorrelationFilter(self)\n"
            max_corr = advanced_config.get('max_correlation', 0.7)
            lookback = advanced_config.get('correlation_lookback', 60)
            filter_init += f"        self.correlation_filter.configure(max_correlation={max_corr}, lookback={lookback})\n"
            filter_init += "        self.Log('[+] Correlation filter enabled')\n"

        if advanced_config.get('mtf_enabled'):
            filter_init += "        self.mtf_filter = MultiTimeframeFilter(self)\n"
            timeframes_raw = advanced_config.get('mtf_timeframes', [])
            mtf_indicator = advanced_config.get('mtf_indicator', 'SMA')
            mtf_condition = advanced_config.get('mtf_condition', 'above')
            mtf_period = advanced_config.get('mtf_period', None)
            timeframes = BaseStrategy._parse_mtf_timeframes(timeframes_raw, mtf_indicator, mtf_condition, mtf_period)
            require_all = advanced_config.get('mtf_require_all', True)
            filter_init += f"        self.mtf_filter.configure(timeframes={repr(timeframes)}, require_all={require_all})\n"
            filter_init += "        self.Log('[+] Multi-timeframe filter enabled')\n"

        # Advanced Greeks Filter (Contract-Level)
        if advanced_config.get('advanced_greeks_enabled'):
            filter_init += "        self.advanced_greeks_filter = AdvancedGreeksFilter(self)\n"

            # Build configure call with only enabled Greeks
            configure_params = []
            if advanced_config.get('gamma_filter_enabled'):
                configure_params.append(f"max_gamma={advanced_config.get('max_gamma', 0.05)}")

            if configure_params:
                filter_init += f"        self.advanced_greeks_filter.configure({', '.join(configure_params)})\n"
            filter_init += "        self.Log('[+] Advanced Greeks filter enabled (contract-level)')\n"

        return filter_init

    @staticmethod
    def generate_filter_checks(advanced_config):
        """
        Generate filter check code for OnData method
        This is used by all strategies in their _generate_main_algorithm() methods
        """
        if not advanced_config:
            return ""

        filter_checks = ""

        # VIX Filter
        if advanced_config.get('vix_enabled'):
            vix_min = advanced_config.get('vix_min', 15)
            vix_max = advanced_config.get('vix_max', 50)
            filter_checks += f"""
            # VIX Filter
            if not self.vix_filter.should_enter_trade({vix_min}, {vix_max}, data):
                return
"""

        # Existing filters
        if advanced_config.get('iv_rank_enabled'):
            min_rank = advanced_config.get('iv_rank_min', 50)
            max_rank = advanced_config.get('iv_rank_max', 100)
            filter_checks += f"""
            # IV Rank Filter
            if not self.iv_rank_filter.should_enter_trade(
                self.config.ticker, {min_rank}, {max_rank}, data
            ):
                return
"""

        if advanced_config.get('market_profile_enabled'):
            signal = advanced_config.get('market_profile_signal', 'poc')
            filter_checks += f"""
            # Market Profile Filter
            profile = self.market_profile.calculate_profile(self.config.ticker)
            if profile:
                if not self.market_profile.get_signal(underlying_price, profile, '{signal}'):
                    return
"""

        if advanced_config.get('vol_regime_enabled'):
            regime = advanced_config.get('vol_regime_type', 'any')
            filter_checks += f"""
            # Volatility Regime Filter
            if not self.vol_regime.should_enter_trade(self.config.ticker, '{regime}'):
                return
"""

        # New filters
        if advanced_config.get('correlation_enabled'):
            filter_checks += """
            # Correlation Filter
            if not self.correlation_filter.should_enter_trade(self.config.ticker):
                return
"""

        if advanced_config.get('mtf_enabled'):
            filter_checks += """
            # Multi-Timeframe Filter
            if not self.mtf_filter.should_enter_trade(self.config.ticker):
                return
"""

        if advanced_config.get('greeks_enabled'):
            filter_checks += """
            # Portfolio Greeks Filter (check before entering position)
            # Note: Need to calculate new position Greeks first
            # This is a placeholder - implement in strategy-specific code
            # if not self.greeks_filter.should_enter_trade(new_position_greeks):
            #     return
"""

        # Advanced Greeks Filter note (contract-level filtering in StrikeSelector)
        if advanced_config.get('advanced_greeks_enabled'):
            filter_checks += """
            # Advanced Greeks Filter (Contract-Level)
            # Note: This filter is applied during contract selection in StrikeSelector.
            # Use: contracts = self.advanced_greeks_filter.filter_contracts(contracts)
            # Or check individual: if self.advanced_greeks_filter.should_enter_contract(contract)
"""

        return filter_checks
    
    @staticmethod
    def generate_initialize_base(config):
        """Common initialization code"""
        
        from datetime import datetime
        
        # Handle both flat and nested config safely
        ticker = config.get('ticker', 'SPY')
        start_date = config.get('start_date')
        end_date = config.get('end_date')
        initial_capital = config.get('initial_capital', 100000)
        resolution = config.get('resolution', 'Daily')
        expiry_days = config.get('expiry_days', 30)
        expiry_range = config.get('expiry_range', 5)
        
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        return f"""def Initialize(self):
        # Basic setup
        self.SetStartDate({start_date.year}, {start_date.month}, {start_date.day})
        self.SetEndDate({end_date.year}, {end_date.month}, {end_date.day})
        self.SetCash({initial_capital})
        self.SetWarmUp(50, Resolution.Daily)

        # Load config
        config = load_config()
        self.config = config

        # Add underlying
        self.equity = self.AddEquity(config.ticker, Resolution.{resolution.upper()})
        self.equity.SetDataNormalizationMode(DataNormalizationMode.Raw)

        # Add options
        option = self.AddOption(config.ticker, Resolution.{resolution.upper()})
        self.option_symbol = option.Symbol

        # Set option filter
        min_expiry = max(0, config.expiry_days - config.expiry_range)
        max_expiry = config.expiry_days + config.expiry_range
        option.SetFilter(lambda x: x.Strikes(-50, 50).Expiration(min_expiry, max_expiry))

        # Initialize tracking
        self.positions = {{}}
        self.position_counter = 0
        self.last_trade_date = None

        # Initialize indicators
        self.indicators = IndicatorManager(self)
        self.indicators.initialize_indicators(self.equity.Symbol)

        self.Log(f"[+] Config loaded")
        self.Log(f"Stop Loss Mode: {{config.stop_loss_mode}} ({{config.stop_loss_pct}}%)")"""

    @staticmethod
    def generate_position_tracking():
        """Common position tracking methods"""
        return """
    def update_positions(self, data):
        \"\"\"Update all open positions with current P&L and MAE/MFE\"\"\"

        for pos_id, pos in list(self.positions.items()):
            if pos['status'] != 'open':
                continue

            # Calculate current P&L (None = contracts not in chain, keep last valid value)
            current_pnl = self.calculate_pnl(pos, data)
            if current_pnl is not None:
                pos['current_pnl'] = current_pnl

                # Update MAE (Maximum Adverse Excursion)
                if current_pnl < pos['metrics']['mae']:
                    pos['metrics']['mae'] = current_pnl

                # Update MFE (Maximum Favorable Excursion)
                if current_pnl > pos['metrics']['mfe']:
                    pos['metrics']['mfe'] = current_pnl

            # Check for exit conditions
            exit_reason = self.check_exit_conditions(pos, data.Time)
            if exit_reason:
                self.close_position(pos_id, exit_reason, data.Time)
"""

    @staticmethod
    def generate_exit_logic(config):
        """Common exit condition checking"""
        
        # Safely get stop loss mode
        stop_loss_mode = config.get('stop_loss_mode', 'credit')
        
        # Build stop loss code with proper indentation
        if stop_loss_mode == 'credit' or stop_loss_mode not in ['max_loss', 'equal_dollar', 'price_distance']:
            stop_loss_block = """        # Credit-based stop loss
        stop_loss_amount = -(max_profit * (self.config.stop_loss_pct / 100))
        if current_pnl <= stop_loss_amount:
            return 'stop_loss'"""
        elif stop_loss_mode == 'max_loss':
            stop_loss_block = """        # Max loss-based stop loss
        stop_loss_amount = -(max_loss * (self.config.stop_loss_pct / 100))
        if current_pnl <= stop_loss_amount:
            return 'stop_loss'"""
        elif stop_loss_mode == 'equal_dollar':
            stop_loss_block = """        # Equal dollar stop loss
        profit_target_amount = max_profit * (self.config.profit_target_pct / 100)
        if current_pnl <= -profit_target_amount:
            return 'stop_loss'"""
        else:  # price_distance
            stop_loss_block = """        # Price distance stop loss
        entry_price = pos['entry_underlying_price']
        current_price = self.Securities[self.config.ticker].Price
        price_change_pct = abs((current_price - entry_price) / entry_price) * 100
        if price_change_pct >= self.config.stop_loss_pct:
            return 'stop_loss'"""
        
        return f"""
    def check_exit_conditions(self, pos, time):
        \"\"\"Check if position should be closed\"\"\"
        
        current_pnl = pos['current_pnl']
        max_profit = pos['metrics']['max_profit']
        max_loss = pos['metrics']['max_loss']
        
        # Check profit target
        profit_target = max_profit * (self.config.profit_target_pct / 100)
        if current_pnl >= profit_target:
            return 'profit_target'
        
        # Check stop loss
{stop_loss_block}
        
        # Check expiration (1 day before)
        expiry_date = pos['expiry_date']
        if time.date() >= (expiry_date - timedelta(days=1)):
            return 'expiration'
        
        return None
"""
