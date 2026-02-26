"""
Technical Indicators - Complete Implementation
Supports 16 indicators across momentum, volatility, trend, and volume categories
"""

class IndicatorManager:
    """Manages all technical indicators for trade entry filtering"""
    
    def __init__(self, algorithm, config):
        self.algorithm = algorithm
        self.config = config
        self.indicators = {}
        self.history_cache = {}
        
        # Initialize enabled indicators
        self._initialize_indicators()
    
    def _initialize_indicators(self):
        """Initialize only the enabled indicators"""
        indicators_config = self.config.get('indicators', {})
        
        # Momentum Indicators
        if indicators_config.get('RSI', {}).get('enabled'):
            self.indicators['RSI'] = RSIIndicator(self.algorithm, indicators_config['RSI'])
        
        if indicators_config.get('MACD', {}).get('enabled'):
            self.indicators['MACD'] = MACDIndicator(self.algorithm, indicators_config['MACD'])
        
        if indicators_config.get('STOCHASTIC', {}).get('enabled'):
            self.indicators['STOCHASTIC'] = StochasticIndicator(self.algorithm, indicators_config['STOCHASTIC'])
        
        if indicators_config.get('CCI', {}).get('enabled'):
            self.indicators['CCI'] = CCIIndicator(self.algorithm, indicators_config['CCI'])
        
        if indicators_config.get('WILLIAMSR', {}).get('enabled'):
            self.indicators['WILLIAMSR'] = WilliamsRIndicator(self.algorithm, indicators_config['WILLIAMSR'])
        
        # Volatility Indicators
        if indicators_config.get('ATR', {}).get('enabled'):
            self.indicators['ATR'] = ATRIndicator(self.algorithm, indicators_config['ATR'])
        
        if indicators_config.get('BBANDS', {}).get('enabled'):
            self.indicators['BBANDS'] = BollingerBandsIndicator(self.algorithm, indicators_config['BBANDS'])
        
        if indicators_config.get('KELTNER', {}).get('enabled'):
            self.indicators['KELTNER'] = KeltnerChannelIndicator(self.algorithm, indicators_config['KELTNER'])
        
        # Trend Indicators
        if indicators_config.get('SMA', {}).get('enabled'):
            self.indicators['SMA'] = SMAIndicator(self.algorithm, indicators_config['SMA'])
        
        if indicators_config.get('EMA', {}).get('enabled'):
            self.indicators['EMA'] = EMAIndicator(self.algorithm, indicators_config['EMA'])
        
        if indicators_config.get('ADX', {}).get('enabled'):
            self.indicators['ADX'] = ADXIndicator(self.algorithm, indicators_config['ADX'])
        
        if indicators_config.get('SUPERTREND', {}).get('enabled'):
            self.indicators['SUPERTREND'] = SuperTrendIndicator(self.algorithm, indicators_config['SUPERTREND'])
        
        # Volume Indicators
        if indicators_config.get('VWAP', {}).get('enabled'):
            self.indicators['VWAP'] = VWAPIndicator(self.algorithm, indicators_config['VWAP'])
        
        if indicators_config.get('OBV', {}).get('enabled'):
            self.indicators['OBV'] = OBVIndicator(self.algorithm, indicators_config['OBV'])
        
        if indicators_config.get('MFI', {}).get('enabled'):
            self.indicators['MFI'] = MFIIndicator(self.algorithm, indicators_config['MFI'])
        
        self.algorithm.Log(f"[+] Initialized {len(self.indicators)} indicators")
    
    def should_enter_trade(self, symbol):
        """Check if all enabled indicators give entry signal"""
        
        if not self.indicators:
            return True  # No filters = always pass
        
        # Get history once for all indicators
        history = self._get_history(symbol)
        if history is None or history.empty:
            self.algorithm.Log("[!] No history data for indicators")
            return False
        
        # Check each indicator
        for name, indicator in self.indicators.items():
            try:
                if not indicator.check_signal(symbol, history):
                    self.algorithm.Log(f"[X] {name} filter FAILED")
                    return False
            except Exception as e:
                self.algorithm.Log(f"[!] {name} error: {e}")
                return False
        
        self.algorithm.Log(f"[+] All {len(self.indicators)} indicators PASSED")
        return True
    
    def _get_history(self, symbol):
        """Get history data with caching"""
        try:
            # Use cached history if available
            if symbol in self.history_cache:
                return self.history_cache[symbol]
            
            # Get max lookback needed
            max_lookback = 200  # Default safe value
            
            history = self.algorithm.History(symbol, max_lookback, Resolution.Daily)
            self.history_cache[symbol] = history
            
            return history
        except Exception as e:
            self.algorithm.Log(f"[!] History fetch error: {e}")
            return None


# ============================================================
# MOMENTUM INDICATORS
# ============================================================

class RSIIndicator:
    """Relative Strength Index - Overbought/Oversold momentum"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 14)
        self.condition = params.get('condition', 'oversold')
        self.oversold_level = params.get('oversold', 30)
        self.overbought_level = params.get('overbought', 70)
    
    def check_signal(self, symbol, history):
        """Check RSI signal"""
        if len(history) < self.period + 1:
            return False
        
        # Calculate RSI
        rsi = self._calculate_rsi(history['close'])
        
        if self.condition == 'oversold':
            return rsi < self.oversold_level
        elif self.condition == 'overbought':
            return rsi > self.overbought_level
        elif self.condition == 'neutral':
            return self.oversold_level <= rsi <= self.overbought_level
        
        return True
    
    def _calculate_rsi(self, prices):
        """Calculate RSI"""
        deltas = prices.diff()
        gain = deltas.where(deltas > 0, 0).rolling(window=self.period).mean()
        loss = -deltas.where(deltas < 0, 0).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]


class MACDIndicator:
    """MACD - Moving Average Convergence Divergence"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.fast = params.get('fast', 12)
        self.slow = params.get('slow', 26)
        self.signal = params.get('signal', 9)
        self.condition = params.get('condition', 'bullish_cross')
    
    def check_signal(self, symbol, history):
        """Check MACD signal"""
        if len(history) < self.slow + self.signal:
            return False
        
        macd_line, signal_line = self._calculate_macd(history['close'])
        
        if self.condition == 'bullish_cross':
            return macd_line > signal_line
        elif self.condition == 'bearish_cross':
            return macd_line < signal_line
        elif self.condition == 'positive':
            return macd_line > 0
        elif self.condition == 'negative':
            return macd_line < 0
        
        return True
    
    def _calculate_macd(self, prices):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=self.fast, adjust=False).mean()
        ema_slow = prices.ewm(span=self.slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal, adjust=False).mean()
        
        return macd_line.iloc[-1], signal_line.iloc[-1]


class StochasticIndicator:
    """Stochastic Oscillator - Momentum indicator"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 14)
        self.k_smooth = params.get('k_smooth', 3)
        self.condition = params.get('condition', 'oversold')
        self.oversold = params.get('oversold', 20)
        self.overbought = params.get('overbought', 80)
    
    def check_signal(self, symbol, history):
        """Check Stochastic signal"""
        if len(history) < self.period + self.k_smooth:
            return False
        
        k_value = self._calculate_stochastic(history)
        
        if self.condition == 'oversold':
            return k_value < self.oversold
        elif self.condition == 'overbought':
            return k_value > self.overbought
        elif self.condition == 'neutral':
            return self.oversold <= k_value <= self.overbought
        
        return True
    
    def _calculate_stochastic(self, history):
        """Calculate %K"""
        close = history['close']
        high = history['high']
        low = history['low']
        
        lowest_low = low.rolling(window=self.period).min()
        highest_high = high.rolling(window=self.period).max()
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        k_smooth = k.rolling(window=self.k_smooth).mean()
        
        return k_smooth.iloc[-1]


class CCIIndicator:
    """Commodity Channel Index"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 20)
        self.condition = params.get('condition', 'oversold')
        self.oversold = params.get('oversold', -100)
        self.overbought = params.get('overbought', 100)
    
    def check_signal(self, symbol, history):
        """Check CCI signal"""
        if len(history) < self.period:
            return False
        
        cci = self._calculate_cci(history)
        
        if self.condition == 'oversold':
            return cci < self.oversold
        elif self.condition == 'overbought':
            return cci > self.overbought
        elif self.condition == 'neutral':
            return self.oversold <= cci <= self.overbought
        
        return True
    
    def _calculate_cci(self, history):
        """Calculate CCI"""
        typical_price = (history['high'] + history['low'] + history['close']) / 3
        sma = typical_price.rolling(window=self.period).mean()
        mean_deviation = typical_price.rolling(window=self.period).apply(
            lambda x: abs(x - x.mean()).mean()
        )
        
        cci = (typical_price - sma) / (0.015 * mean_deviation)
        return cci.iloc[-1]


class WilliamsRIndicator:
    """Williams %R - Momentum oscillator"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 14)
        self.condition = params.get('condition', 'oversold')
        self.oversold = params.get('oversold', -80)
        self.overbought = params.get('overbought', -20)
    
    def check_signal(self, symbol, history):
        """Check Williams %R signal"""
        if len(history) < self.period:
            return False
        
        wr = self._calculate_williams_r(history)
        
        if self.condition == 'oversold':
            return wr < self.oversold
        elif self.condition == 'overbought':
            return wr > self.overbought
        elif self.condition == 'neutral':
            return self.oversold <= wr <= self.overbought
        
        return True
    
    def _calculate_williams_r(self, history):
        """Calculate Williams %R"""
        high = history['high'].rolling(window=self.period).max()
        low = history['low'].rolling(window=self.period).min()
        close = history['close']
        
        wr = -100 * (high - close) / (high - low)
        return wr.iloc[-1]


# ============================================================
# VOLATILITY INDICATORS
# ============================================================

class ATRIndicator:
    """Average True Range - Volatility measure"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 14)
        self.condition = params.get('condition', 'high')
        self.threshold = params.get('threshold', 1.5)
    
    def check_signal(self, symbol, history):
        """Check ATR signal"""
        if len(history) < self.period + 1:
            return False
        
        atr = self._calculate_atr(history)
        atr_ma = history['close'].rolling(window=self.period).std().mean()
        
        if self.condition == 'high':
            return atr > (atr_ma * self.threshold)
        elif self.condition == 'low':
            return atr < (atr_ma * self.threshold)
        
        return True
    
    def _calculate_atr(self, history):
        """Calculate ATR"""
        high = history['high']
        low = history['low']
        close = history['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()
        
        return atr.iloc[-1]


class BollingerBandsIndicator:
    """Bollinger Bands - Volatility bands"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 20)
        self.std_dev = params.get('std_dev', 2)
        self.condition = params.get('condition', 'below_lower')
    
    def check_signal(self, symbol, history):
        """Check Bollinger Bands signal"""
        if len(history) < self.period:
            return False
        
        upper, middle, lower = self._calculate_bbands(history['close'])
        current_price = history['close'].iloc[-1]
        
        if self.condition == 'below_lower':
            return current_price < lower
        elif self.condition == 'above_upper':
            return current_price > upper
        elif self.condition == 'inside_bands':
            return lower <= current_price <= upper
        elif self.condition == 'near_middle':
            return abs(current_price - middle) < (upper - lower) * 0.2
        
        return True
    
    def _calculate_bbands(self, prices):
        """Calculate Bollinger Bands"""
        middle = prices.rolling(window=self.period).mean()
        std = prices.rolling(window=self.period).std()
        
        upper = middle + (std * self.std_dev)
        lower = middle - (std * self.std_dev)
        
        return upper.iloc[-1], middle.iloc[-1], lower.iloc[-1]


class KeltnerChannelIndicator:
    """Keltner Channels - ATR-based bands"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 20)
        self.atr_multiplier = params.get('atr_mult', 2)
        self.condition = params.get('condition', 'below_lower')
    
    def check_signal(self, symbol, history):
        """Check Keltner Channel signal"""
        if len(history) < self.period + 14:
            return False
        
        upper, middle, lower = self._calculate_keltner(history)
        current_price = history['close'].iloc[-1]
        
        if self.condition == 'below_lower':
            return current_price < lower
        elif self.condition == 'above_upper':
            return current_price > upper
        elif self.condition == 'inside_bands':
            return lower <= current_price <= upper
        
        return True
    
    def _calculate_keltner(self, history):
        """Calculate Keltner Channels"""
        middle = history['close'].ewm(span=self.period, adjust=False).mean()
        
        # Calculate ATR
        atr_indicator = ATRIndicator(self.algorithm, {'period': 14})
        atr = atr_indicator._calculate_atr(history)
        
        upper = middle + (atr * self.atr_multiplier)
        lower = middle - (atr * self.atr_multiplier)
        
        return upper.iloc[-1], middle.iloc[-1], lower.iloc[-1]


# ============================================================
# TREND INDICATORS
# ============================================================

class SMAIndicator:
    """Simple Moving Average"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 50)
        self.condition = params.get('condition', 'above')
    
    def check_signal(self, symbol, history):
        """Check SMA signal"""
        if len(history) < self.period:
            return False
        
        sma = history['close'].rolling(window=self.period).mean().iloc[-1]
        current_price = history['close'].iloc[-1]
        
        if self.condition == 'above':
            return current_price > sma
        elif self.condition == 'below':
            return current_price < sma
        elif self.condition == 'cross_above':
            prev_price = history['close'].iloc[-2]
            prev_sma = history['close'].rolling(window=self.period).mean().iloc[-2]
            return prev_price <= prev_sma and current_price > sma
        elif self.condition == 'cross_below':
            prev_price = history['close'].iloc[-2]
            prev_sma = history['close'].rolling(window=self.period).mean().iloc[-2]
            return prev_price >= prev_sma and current_price < sma
        
        return True


class EMAIndicator:
    """Exponential Moving Average"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 50)
        self.condition = params.get('condition', 'above')
    
    def check_signal(self, symbol, history):
        """Check EMA signal"""
        if len(history) < self.period:
            return False
        
        ema = history['close'].ewm(span=self.period, adjust=False).mean().iloc[-1]
        current_price = history['close'].iloc[-1]
        
        if self.condition == 'above':
            return current_price > ema
        elif self.condition == 'below':
            return current_price < ema
        elif self.condition == 'cross_above':
            prev_price = history['close'].iloc[-2]
            prev_ema = history['close'].ewm(span=self.period, adjust=False).mean().iloc[-2]
            return prev_price <= prev_ema and current_price > ema
        elif self.condition == 'cross_below':
            prev_price = history['close'].iloc[-2]
            prev_ema = history['close'].ewm(span=self.period, adjust=False).mean().iloc[-2]
            return prev_price >= prev_ema and current_price < ema
        
        return True


class ADXIndicator:
    """Average Directional Index - Trend strength"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 14)
        self.condition = params.get('condition', 'strong')
        self.threshold = params.get('threshold', 25)
    
    def check_signal(self, symbol, history):
        """Check ADX signal"""
        if len(history) < self.period * 2:
            return False
        
        adx = self._calculate_adx(history)
        
        if self.condition == 'strong':
            return adx > self.threshold
        elif self.condition == 'weak':
            return adx < self.threshold
        
        return True
    
    def _calculate_adx(self, history):
        """Calculate ADX"""
        high = history['high']
        low = history['low']
        close = history['close']
        
        # Calculate +DM and -DM
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
        
        # Calculate ATR
        atr_indicator = ATRIndicator(self.algorithm, {'period': self.period})
        atr = atr_indicator._calculate_atr(history)
        
        # Calculate +DI and -DI
        plus_di = 100 * (plus_dm.rolling(window=self.period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=self.period).mean() / atr)
        
        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=self.period).mean()
        
        return adx.iloc[-1]


class SuperTrendIndicator:
    """SuperTrend - ATR-based trend indicator"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 10)
        self.multiplier = params.get('multiplier', 3)
        self.condition = params.get('condition', 'bullish')
    
    def check_signal(self, symbol, history):
        """Check SuperTrend signal"""
        if len(history) < self.period + 14:
            return False
        
        trend = self._calculate_supertrend(history)
        
        if self.condition == 'bullish':
            return trend == 1
        elif self.condition == 'bearish':
            return trend == -1
        
        return True
    
    def _calculate_supertrend(self, history):
        """Calculate SuperTrend"""
        # Calculate ATR
        atr_indicator = ATRIndicator(self.algorithm, {'period': self.period})
        atr = atr_indicator._calculate_atr(history)
        
        # Calculate basic bands
        hl2 = (history['high'] + history['low']) / 2
        upper_band = hl2 + (self.multiplier * atr)
        lower_band = hl2 - (self.multiplier * atr)
        
        # Determine trend
        close = history['close'].iloc[-1]
        
        if close > upper_band:
            return 1  # Bullish
        elif close < lower_band:
            return -1  # Bearish
        else:
            return 0  # Neutral


# ============================================================
# VOLUME INDICATORS
# ============================================================

class VWAPIndicator:
    """Volume Weighted Average Price"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.condition = params.get('condition', 'above')
    
    def check_signal(self, symbol, history):
        """Check VWAP signal"""
        if len(history) < 20:
            return False
        
        vwap = self._calculate_vwap(history)
        current_price = history['close'].iloc[-1]
        
        if self.condition == 'above':
            return current_price > vwap
        elif self.condition == 'below':
            return current_price < vwap
        
        return True
    
    def _calculate_vwap(self, history):
        """Calculate VWAP"""
        typical_price = (history['high'] + history['low'] + history['close']) / 3
        vwap = (typical_price * history['volume']).cumsum() / history['volume'].cumsum()
        return vwap.iloc[-1]


class OBVIndicator:
    """On-Balance Volume - Volume momentum"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.condition = params.get('condition', 'rising')
        self.period = params.get('period', 20)
    
    def check_signal(self, symbol, history):
        """Check OBV signal"""
        if len(history) < self.period + 1:
            return False
        
        obv = self._calculate_obv(history)
        obv_ma = obv.rolling(window=self.period).mean()
        
        if self.condition == 'rising':
            return obv.iloc[-1] > obv_ma.iloc[-1]
        elif self.condition == 'falling':
            return obv.iloc[-1] < obv_ma.iloc[-1]
        
        return True
    
    def _calculate_obv(self, history):
        """Calculate OBV"""
        obv = (history['volume'] * (~history['close'].diff().le(0) * 2 - 1)).cumsum()
        return obv


class MFIIndicator:
    """Money Flow Index - Volume-weighted RSI"""
    
    def __init__(self, algorithm, params):
        self.algorithm = algorithm
        self.period = params.get('period', 14)
        self.condition = params.get('condition', 'oversold')
        self.oversold = params.get('oversold', 20)
        self.overbought = params.get('overbought', 80)
    
    def check_signal(self, symbol, history):
        """Check MFI signal"""
        if len(history) < self.period + 1:
            return False
        
        mfi = self._calculate_mfi(history)
        
        if self.condition == 'oversold':
            return mfi < self.oversold
        elif self.condition == 'overbought':
            return mfi > self.overbought
        elif self.condition == 'neutral':
            return self.oversold <= mfi <= self.overbought
        
        return True
    
    def _calculate_mfi(self, history):
        """Calculate MFI"""
        typical_price = (history['high'] + history['low'] + history['close']) / 3
        money_flow = typical_price * history['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(window=self.period).sum()
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(window=self.period).sum()
        
        mfi = 100 - (100 / (1 + positive_flow / negative_flow))
        return mfi.iloc[-1]
