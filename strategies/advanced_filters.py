from datetime import timedelta

class IVRankFilter:

    def __init__(self, algo):
        self.algo = algo
        self.iv_history = {}

    def should_enter_trade(self, ticker, min_rank, max_rank, data=None):
        try:
            current_iv = self._calculate_current_iv(ticker, data)
            if current_iv is None:
                self.algo.Log("[!] IV Rank: no IV data, passing")
                return True

            if ticker not in self.iv_history:
                self.iv_history[ticker] = []

            self.iv_history[ticker].append(current_iv)
            if len(self.iv_history[ticker]) > 252:
                self.iv_history[ticker] = self.iv_history[ticker][-252:]

            if len(self.iv_history[ticker]) < 20:
                self.algo.Log(f"[!] IV Rank: warming up ({len(self.iv_history[ticker])}/20 days), passing")
                return True

            iv_rank = self._calculate_rank(current_iv, self.iv_history[ticker])

            if min_rank <= iv_rank <= max_rank:
                self.algo.Log(f"[+] IV Rank: {iv_rank:.1f}% (IV={current_iv:.3f}) - PASS ({min_rank}-{max_rank}%)")
                return True
            else:
                self.algo.Log(f"[X] IV Rank: {iv_rank:.1f}% (IV={current_iv:.3f}) - SKIP (outside {min_rank}-{max_rank}%)")
                return False

        except Exception as e:
            self.algo.Log(f"[!] IV Rank error: {e}")
            return True

    def _calculate_current_iv(self, ticker, data=None):
        try:
            if data is not None and data.OptionChains:
                for chain in data.OptionChains:
                    contracts = [c for c in chain.Value]
                    if not contracts:
                        continue
                    underlying_price = chain.Value.Underlying.Price
                    atm = [c for c in contracts
                           if abs(c.Strike - underlying_price) <= underlying_price * 0.01]
                    if not atm:
                        strikes = sorted(set(c.Strike for c in contracts))
                        atm_strike = min(strikes, key=lambda s: abs(s - underlying_price))
                        atm = [c for c in contracts if c.Strike == atm_strike]
                    ivs = [c.ImpliedVolatility for c in atm if c.ImpliedVolatility > 0]
                    if ivs:
                        return sum(ivs) / len(ivs)
            return None
        except:
            return None

    def _calculate_rank(self, current, history):
        if not history:
            return 50
        min_iv = min(history)
        max_iv = max(history)
        if max_iv == min_iv:
            return 50
        rank = ((current - min_iv) / (max_iv - min_iv)) * 100
        return max(0, min(100, rank))


class VIXFilter:

    def __init__(self, algo):
        self.algo = algo
        try:
            self.vix = algo.AddIndex("VIX", Resolution.Daily).Symbol
            self.algo.Log("[+] VIX filter initialized")
        except Exception as e:
            self.algo.Log(f"[!] VIX init error: {e}")
            self.vix = None

    def should_enter_trade(self, min_vix, max_vix, data=None):
        try:
            if self.vix is None:
                return True
            vix_value = 0
            if data is not None:
                try:
                    if self.vix in data and data[self.vix] is not None:
                        vix_value = float(data[self.vix].Close)
                except Exception:
                    pass
            if vix_value <= 0 and self.vix in self.algo.Securities:
                vix_value = self.algo.Securities[self.vix].Price
            if vix_value <= 0:
                self.algo.Log("[!] VIX filter: no price data, passing")
                return True
            if min_vix <= vix_value <= max_vix:
                self.algo.Log(f"[+] VIX: {vix_value:.1f} - PASS ({min_vix}-{max_vix})")
                return True
            else:
                self.algo.Log(f"[X] VIX: {vix_value:.1f} - SKIP (outside {min_vix}-{max_vix})")
                return False
        except Exception as e:
            self.algo.Log(f"[!] VIX error: {e}")
            return True

    def get_current_vix(self):
        try:
            if self.vix and self.vix in self.algo.Securities:
                return self.algo.Securities[self.vix].Price
        except:
            pass
        return None


class MarketProfileIndicator:
    """Market Profile (TPO) indicator"""
    
    def __init__(self, algo, lookback_days=20):
        self.algo = algo
        self.lookback_days = lookback_days
    
    def calculate_profile(self, ticker):
        """Calculate Market Profile levels"""
        try:
            history = self.algo.History(ticker, self.lookback_days, Resolution.Hour)
            if history.empty:
                return None
            
            prices = []
            for bar in history.itertuples():
                prices.extend([bar.Open, bar.High, bar.Low, bar.Close])
            
            if not prices:
                return None
            
            price_min = min(prices)
            price_max = max(prices)
            tick_size = 0.50
            
            tpo_counts = {}
            current_tick = price_min
            while current_tick <= price_max:
                tpo_counts[current_tick] = 0
                current_tick += tick_size
            
            for price in prices:
                tick = round(price / tick_size) * tick_size
                if tick in tpo_counts:
                    tpo_counts[tick] += 1
            
            poc = max(tpo_counts, key=tpo_counts.get)
            
            sorted_ticks = sorted(tpo_counts.items(), key=lambda x: x[1], reverse=True)
            total_tpo = sum(tpo_counts.values())
            target_tpo = total_tpo * 0.70
            
            cumulative = 0
            value_area_ticks = []
            for tick, count in sorted_ticks:
                cumulative += count
                value_area_ticks.append(tick)
                if cumulative >= target_tpo:
                    break
            
            val = min(value_area_ticks) if value_area_ticks else poc
            vah = max(value_area_ticks) if value_area_ticks else poc
            
            return {
                'poc': poc,
                'val': val,
                'vah': vah
            }
            
        except Exception as e:
            self.algo.Log(f"[!] Market Profile error: {e}")
            return None
    
    def get_signal(self, current_price, profile, signal_type):
        """Check if price is at target MP level"""
        if not profile:
            return True
        
        tolerance = 1.0
        
        if signal_type == 'poc':
            target = profile['poc']
        elif signal_type == 'val':
            target = profile['val']
        elif signal_type == 'vah':
            target = profile['vah']
        else:
            return True
        
        if abs(current_price - target) <= tolerance:
            self.algo.Log(f"[+] Price ${current_price:.2f} at {signal_type.upper()} ${target:.2f}")
            return True
        else:
            self.algo.Log(f"[X] Price ${current_price:.2f} not at {signal_type.upper()} ${target:.2f}")
            return False


class VolatilityRegimeFilter:
    """Detect volatility regime using ATR"""
    
    def __init__(self, algo, period=14):
        self.algo = algo
        self.period = period
        self.atr_history = {}
    
    def should_enter_trade(self, ticker, regime_type):
        """Check if current regime matches target"""
        
        if regime_type == 'any':
            return True
        
        try:
            current_regime = self.detect_regime(ticker)
            
            if current_regime == regime_type:
                self.algo.Log(f"[+] Vol Regime: {current_regime} - MATCH")
                return True
            else:
                self.algo.Log(f"[X] Vol Regime: {current_regime} - SKIP (want {regime_type})")
                return False
                
        except Exception as e:
            self.algo.Log(f"[!] Vol Regime filter error: {e}")
            return True
    
    def detect_regime(self, ticker):
        """Detect current volatility regime"""
        try:
            history = self.algo.History(ticker, 60, Resolution.Daily)
            if history.empty:
                return 'medium'
            
            atr_values = []
            for i in range(self.period, len(history)):
                period_data = history.iloc[i-self.period:i]
                tr = max(
                    period_data['high'].max() - period_data['low'].min(),
                    abs(period_data['high'].max() - period_data['close'].iloc[-2]),
                    abs(period_data['low'].min() - period_data['close'].iloc[-2])
                )
                atr_values.append(tr)
            
            if not atr_values:
                return 'medium'
            
            current_atr = atr_values[-1]
            percentile_30 = sorted(atr_values)[int(len(atr_values) * 0.30)]
            percentile_70 = sorted(atr_values)[int(len(atr_values) * 0.70)]
            
            if current_atr < percentile_30:
                return 'low'
            elif current_atr > percentile_70:
                return 'high'
            else:
                return 'medium'
                
        except Exception as e:
            self.algo.Log(f"[!] Regime detection error: {e}")
            return 'medium'


class ExpirationFilter:
    """Filter by expiration cycle type"""
    
    @staticmethod
    def filter_expiries(expiries, cycle_type):
        """Filter expiration dates by cycle type"""
        from datetime import timedelta
        
        if cycle_type == 'any':
            return expiries
        
        filtered = {}
        
        for exp_date, contracts in expiries.items():
            if cycle_type == 'monthly':
                if exp_date.day >= 15 and exp_date.day <= 21 and exp_date.weekday() == 4:
                    filtered[exp_date] = contracts
            
            elif cycle_type == 'weekly':
                if exp_date.weekday() == 4:
                    filtered[exp_date] = contracts
            
            elif cycle_type == 'eom':
                next_month = (exp_date.replace(day=28) + timedelta(days=4)).replace(day=1)
                last_day = (next_month - timedelta(days=1)).day
                if exp_date.day >= last_day - 2:
                    filtered[exp_date] = contracts
            
            elif cycle_type == 'quarterly':
                if exp_date.month in [3, 6, 9, 12]:
                    if exp_date.day >= 15 and exp_date.day <= 21 and exp_date.weekday() == 4:
                        filtered[exp_date] = contracts
        
        return filtered


class LiquidityFilter:
    """Filter by bid-ask spread and open interest"""

    @staticmethod
    def check_liquidity(contract, max_spread_pct, min_open_interest):
        """Check if contract meets liquidity requirements"""

        try:
            bid = contract.BidPrice
            ask = contract.AskPrice
            oi = contract.OpenInterest

            if bid <= 0 or ask <= 0:
                return False

            mid_price = (bid + ask) / 2
            if mid_price == 0:
                return False

            spread_pct = ((ask - bid) / mid_price) * 100

            if spread_pct > max_spread_pct:
                return False

            if oi < min_open_interest:
                return False

            return True

        except Exception as e:
            return False


class PortfolioGreeksFilter:
    """Filter trades based on portfolio-level Greeks exposure limits"""

    def __init__(self, algo):
        self.algo = algo
        self.max_portfolio_delta = None
        self.max_portfolio_gamma = None
        self.max_portfolio_vega = None
        self.target_portfolio_theta = None

    def configure(self, max_delta=None, max_gamma=None, max_vega=None, target_theta=None):
        """Configure portfolio Greeks limits"""
        self.max_portfolio_delta = max_delta
        self.max_portfolio_gamma = max_gamma
        self.max_portfolio_vega = max_vega
        self.target_portfolio_theta = target_theta
        self.algo.Log(f"[+] Portfolio Greeks limits: Delta={max_delta}, Gamma={max_gamma}, Vega={max_vega}, Theta={target_theta}")

    def should_enter_trade(self, new_position_greeks):
        """Check if adding new position would exceed portfolio Greeks limits"""

        try:
            # Calculate current portfolio Greeks
            current_greeks = self._calculate_portfolio_greeks()

            # Calculate projected Greeks after adding new position
            projected_delta = current_greeks['delta'] + new_position_greeks.get('delta', 0)
            projected_gamma = current_greeks['gamma'] + new_position_greeks.get('gamma', 0)
            projected_vega = current_greeks['vega'] + new_position_greeks.get('vega', 0)
            projected_theta = current_greeks['theta'] + new_position_greeks.get('theta', 0)

            # Check Delta limit
            if self.max_portfolio_delta and abs(projected_delta) > self.max_portfolio_delta:
                self.algo.Log(f"[X] Portfolio Delta limit exceeded: {projected_delta:.2f} > {self.max_portfolio_delta}")
                return False

            # Check Gamma limit
            if self.max_portfolio_gamma and abs(projected_gamma) > self.max_portfolio_gamma:
                self.algo.Log(f"[X] Portfolio Gamma limit exceeded: {projected_gamma:.4f} > {self.max_portfolio_gamma}")
                return False

            # Check Vega limit
            if self.max_portfolio_vega and abs(projected_vega) > self.max_portfolio_vega:
                self.algo.Log(f"[X] Portfolio Vega limit exceeded: {projected_vega:.2f} > {self.max_portfolio_vega}")
                return False

            # Check Theta target (optional - may want minimum theta for income strategies)
            if self.target_portfolio_theta and projected_theta < self.target_portfolio_theta:
                self.algo.Log(f"[X] Portfolio Theta below target: {projected_theta:.2f} < {self.target_portfolio_theta}")
                return False

            self.algo.Log(f"[+] Portfolio Greeks OK: Δ={projected_delta:.2f}, Γ={projected_gamma:.4f}, ν={projected_vega:.2f}, Θ={projected_theta:.2f}")
            return True

        except Exception as e:
            self.algo.Log(f"[!] Portfolio Greeks filter error: {e}")
            return True

    def _calculate_portfolio_greeks(self):
        """Calculate total Greeks across all open positions"""
        total_delta = 0
        total_gamma = 0
        total_vega = 0
        total_theta = 0

        try:
            for symbol, holding in self.algo.Portfolio.items():
                if holding.Invested and holding.Type == SecurityType.Option:
                    # Get option contract
                    option = self.algo.Securities[symbol]

                    # Sum Greeks (multiplied by quantity and contract multiplier)
                    quantity = holding.Quantity
                    multiplier = 100  # Standard options contract multiplier

                    total_delta += option.Delta * quantity * multiplier
                    total_gamma += option.Gamma * quantity * multiplier
                    total_vega += option.Vega * quantity * multiplier
                    total_theta += option.Theta * quantity * multiplier
        except Exception as e:
            self.algo.Log(f"[!] Error calculating portfolio Greeks: {e}")

        return {
            'delta': total_delta,
            'gamma': total_gamma,
            'vega': total_vega,
            'theta': total_theta
        }


class DynamicPositionSizer:
    """Calculate position size based on various methods"""

    def __init__(self, algo):
        self.algo = algo
        self.sizing_method = 'fixed_fractional'
        self.risk_pct = 2.0  # Default 2% risk per trade
        self.kelly_fraction = 0.5  # Half Kelly for safety

    def configure(self, method='fixed_fractional', risk_pct=2.0, kelly_fraction=0.5):
        """Configure position sizing method"""
        self.sizing_method = method
        self.risk_pct = risk_pct
        self.kelly_fraction = kelly_fraction
        self.algo.Log(f"[+] Position sizing: {method}, risk={risk_pct}%")

    def calculate_position_size(self, max_loss_per_contract, win_rate=None, avg_win=None, avg_loss=None, current_volatility=None, position_greeks=None):
        """Calculate optimal position size"""

        try:
            portfolio_value = self.algo.Portfolio.TotalPortfolioValue

            if self.sizing_method == 'fixed_fractional':
                # Risk fixed % of capital
                risk_amount = portfolio_value * (self.risk_pct / 100)
                num_contracts = int(risk_amount / max_loss_per_contract)
                self.algo.Log(f"[+] Fixed Fractional: Risk ${risk_amount:.2f} = {num_contracts} contracts")

            elif self.sizing_method == 'kelly_criterion':
                # Kelly Criterion: f = (bp - q) / b
                # where b = odds, p = win prob, q = loss prob
                if win_rate and avg_win and avg_loss:
                    b = avg_win / abs(avg_loss)  # Odds
                    p = win_rate
                    q = 1 - win_rate
                    kelly_f = (b * p - q) / b

                    # Apply fraction for safety (typically 0.5 = half Kelly)
                    safe_f = kelly_f * self.kelly_fraction
                    safe_f = max(0, min(safe_f, 0.25))  # Cap at 25% of portfolio

                    risk_amount = portfolio_value * safe_f
                    num_contracts = int(risk_amount / max_loss_per_contract)
                    self.algo.Log(f"[+] Kelly Criterion: f={kelly_f:.3f}, safe_f={safe_f:.3f}, contracts={num_contracts}")
                else:
                    # Fallback to fixed fractional
                    num_contracts = self._fixed_fractional_fallback(portfolio_value, max_loss_per_contract)

            elif self.sizing_method == 'volatility_based':
                # Scale position size inversely with volatility
                if current_volatility:
                    baseline_vol = 0.15  # 15% baseline volatility
                    vol_adjustment = baseline_vol / current_volatility
                    vol_adjustment = max(0.5, min(vol_adjustment, 2.0))  # Limit adjustment

                    base_risk = portfolio_value * (self.risk_pct / 100)
                    adjusted_risk = base_risk * vol_adjustment
                    num_contracts = int(adjusted_risk / max_loss_per_contract)
                    self.algo.Log(f"[+] Volatility-Based: Vol={current_volatility:.2f}, Adjustment={vol_adjustment:.2f}, Contracts={num_contracts}")
                else:
                    num_contracts = self._fixed_fractional_fallback(portfolio_value, max_loss_per_contract)

            elif self.sizing_method == 'greeks_based':
                # Scale position size based on Greeks risk
                if position_greeks:
                    # Higher gamma/vega = smaller position
                    gamma_factor = 1.0 / (1.0 + abs(position_greeks.get('gamma', 0)) * 100)
                    vega_factor = 1.0 / (1.0 + abs(position_greeks.get('vega', 0)) / 10)
                    risk_adjustment = gamma_factor * vega_factor

                    base_risk = portfolio_value * (self.risk_pct / 100)
                    adjusted_risk = base_risk * risk_adjustment
                    num_contracts = int(adjusted_risk / max_loss_per_contract)
                    self.algo.Log(f"[+] Greeks-Based: Γ factor={gamma_factor:.2f}, ν factor={vega_factor:.2f}, Contracts={num_contracts}")
                else:
                    num_contracts = self._fixed_fractional_fallback(portfolio_value, max_loss_per_contract)
            else:
                # Default to fixed fractional
                num_contracts = self._fixed_fractional_fallback(portfolio_value, max_loss_per_contract)

            # Ensure at least 1 contract
            return max(1, num_contracts)

        except Exception as e:
            self.algo.Log(f"[!] Position sizing error: {e}")
            return 1

    def _fixed_fractional_fallback(self, portfolio_value, max_loss_per_contract):
        """Fallback to fixed fractional sizing"""
        risk_amount = portfolio_value * (self.risk_pct / 100)
        return int(risk_amount / max_loss_per_contract)


class CorrelationFilter:
    """Filter trades to avoid highly correlated positions"""

    def __init__(self, algo):
        self.algo = algo
        self.max_correlation = 0.7
        self.correlation_lookback = 60  # Days
        self.correlation_cache = {}

    def configure(self, max_correlation=0.7, lookback=60):
        """Configure correlation limits"""
        self.max_correlation = max_correlation
        self.correlation_lookback = lookback
        self.algo.Log(f"[+] Correlation filter: max={max_correlation}, lookback={lookback} days")

    def should_enter_trade(self, new_ticker):
        """Check if new ticker is too correlated with existing positions"""

        try:
            # Get all tickers in current portfolio
            existing_tickers = []
            for symbol, holding in self.algo.Portfolio.items():
                if holding.Invested:
                    # Extract underlying ticker from option symbol
                    underlying = self._get_underlying_ticker(symbol)
                    if underlying and underlying not in existing_tickers:
                        existing_tickers.append(underlying)

            # If no existing positions, allow trade
            if not existing_tickers:
                self.algo.Log(f"[+] Correlation: No existing positions")
                return True

            # Check correlation with each existing position (skip same ticker)
            for existing_ticker in existing_tickers:
                if new_ticker == existing_ticker:
                    continue
                correlation = self._calculate_correlation(new_ticker, existing_ticker)

                if correlation is not None and abs(correlation) > self.max_correlation:
                    self.algo.Log(f"[X] High correlation: {new_ticker} vs {existing_ticker} = {correlation:.2f}")
                    return False

            self.algo.Log(f"[+] Correlation OK: {new_ticker} vs existing positions")
            return True

        except Exception as e:
            self.algo.Log(f"[!] Correlation filter error: {e}")
            return True

    def _calculate_correlation(self, ticker1, ticker2):
        cache_key = f"{ticker1}_{ticker2}"
        if cache_key in self.correlation_cache:
            return self.correlation_cache[cache_key]

        try:
            bars1 = list(self.algo.History(ticker1, self.correlation_lookback, Resolution.Daily))
            bars2 = list(self.algo.History(ticker2, self.correlation_lookback, Resolution.Daily))

            if len(bars1) < 20 or len(bars2) < 20:
                return None

            closes1 = [b.Close for b in bars1]
            closes2 = [b.Close for b in bars2]

            def pct_changes(prices):
                return [(prices[i] - prices[i-1]) / prices[i-1]
                        for i in range(1, len(prices)) if prices[i-1] != 0]

            r1 = pct_changes(closes1)
            r2 = pct_changes(closes2)
            n = min(len(r1), len(r2))
            if n < 20:
                return None
            r1, r2 = r1[-n:], r2[-n:]

            m1 = sum(r1) / n
            m2 = sum(r2) / n
            cov = sum((r1[i] - m1) * (r2[i] - m2) for i in range(n)) / n
            std1 = (sum((x - m1)**2 for x in r1) / n) ** 0.5
            std2 = (sum((x - m2)**2 for x in r2) / n) ** 0.5
            if std1 == 0 or std2 == 0:
                return None
            correlation = cov / (std1 * std2)

            self.correlation_cache[cache_key] = correlation
            return correlation

        except Exception as e:
            self.algo.Log(f"[!] Correlation error: {e}")
            return None

    def _get_underlying_ticker(self, option_symbol):
        """Extract underlying ticker from option symbol"""
        try:
            # This depends on QuantConnect's symbol format
            # Typically option symbols include the underlying
            return option_symbol.Underlying.Value if hasattr(option_symbol, 'Underlying') else None
        except:
            return None



class MultiTimeframeFilter:

    def __init__(self, algo):
        self.algo = algo
        self.timeframes = []
        self.require_all = True

    def configure(self, timeframes, require_all=True):
        self.timeframes = timeframes
        self.require_all = require_all
        self.algo.Log(f"[+] Multi-timeframe filter: {len(timeframes)} timeframes, require_all={require_all}")

    def should_enter_trade(self, ticker):
        try:
            results = []
            for tf_config in self.timeframes:
                resolution = self._parse_resolution(tf_config['resolution'])
                indicator = tf_config['indicator']
                condition = tf_config['condition']
                is_met = self._check_timeframe_condition(ticker, resolution, indicator, condition, tf_config)
                results.append(is_met)
                status = "+" if is_met else "X"
                self.algo.Log(f"[{status}] {tf_config['resolution']} {indicator}({tf_config.get('period',50)}): {condition}")
            if self.require_all:
                allowed = all(results)
                self.algo.Log(f"[+] Multi-timeframe: All conditions met" if allowed else f"[X] Multi-timeframe: Not all conditions met")
            else:
                allowed = any(results)
                self.algo.Log(f"[+] Multi-timeframe: At least one condition met" if allowed else f"[X] Multi-timeframe: No conditions met")
            return allowed
        except Exception as e:
            self.algo.Log(f"[!] Multi-timeframe filter error: {e}")
            return True

    def _check_timeframe_condition(self, ticker, resolution, indicator, condition, config):

        try:
            price = self.algo.Securities[ticker].Price

            if indicator == 'SMA':
                period = config.get('period', 50)
                bars = list(self.algo.History(ticker, period + 5, Resolution.Daily))
                if len(bars) < period:
                    return False
                closes = [b.Close for b in bars]
                sma_value = sum(closes[-period:]) / period
                if condition == 'above':
                    return price > sma_value
                elif condition == 'below':
                    return price < sma_value

            elif indicator == 'EMA':
                period = config.get('period', 50)
                bars = list(self.algo.History(ticker, period * 2, Resolution.Daily))
                if len(bars) < period:
                    return False
                closes = [b.Close for b in bars]
                k = 2.0 / (period + 1)
                ema = closes[0]
                for c in closes[1:]:
                    ema = c * k + ema * (1 - k)
                if condition == 'above':
                    return price > ema
                elif condition == 'below':
                    return price < ema

            elif indicator == 'RSI':
                period = config.get('period', 14)
                bars = list(self.algo.History(ticker, period + 10, Resolution.Daily))
                if len(bars) < period + 1:
                    return False
                closes = [b.Close for b in bars]
                gains = [max(closes[i] - closes[i-1], 0) for i in range(1, len(closes))]
                losses = [max(closes[i-1] - closes[i], 0) for i in range(1, len(closes))]
                avg_gain = sum(gains[-period:]) / period
                avg_loss = sum(losses[-period:]) / period
                if avg_loss == 0:
                    rsi_val = 100.0
                else:
                    rs = avg_gain / avg_loss
                    rsi_val = 100 - (100 / (1 + rs))
                if condition == 'oversold':
                    return rsi_val < 30
                elif condition == 'overbought':
                    return rsi_val > 70
                elif condition == 'neutral':
                    return 30 <= rsi_val <= 70

            elif indicator == 'ADX':
                period = config.get('period', 14)
                bars = list(self.algo.History(ticker, period * 2, Resolution.Daily))
                if len(bars) < period + 1:
                    return False
                highs = [b.High for b in bars]
                lows = [b.Low for b in bars]
                closes = [b.Close for b in bars]
                tr_list, pdm_list, ndm_list = [], [], []
                for i in range(1, len(bars)):
                    tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
                    pdm = max(highs[i] - highs[i-1], 0) if highs[i] - highs[i-1] > lows[i-1] - lows[i] else 0
                    ndm = max(lows[i-1] - lows[i], 0) if lows[i-1] - lows[i] > highs[i] - highs[i-1] else 0
                    tr_list.append(tr)
                    pdm_list.append(pdm)
                    ndm_list.append(ndm)
                atr = sum(tr_list[-period:]) / period
                if atr == 0:
                    return False
                pdi = (sum(pdm_list[-period:]) / period) / atr * 100
                ndi = (sum(ndm_list[-period:]) / period) / atr * 100
                adx_val = abs(pdi - ndi) / (pdi + ndi) * 100 if (pdi + ndi) > 0 else 0
                if condition == 'strong':
                    return adx_val > 25
                elif condition == 'weak':
                    return adx_val < 20

            return False

        except Exception as e:
            self.algo.Log(f"[!] Timeframe condition check error: {e}")
            return False

    def _parse_resolution(self, resolution_str):
        m = {'Tick': Resolution.Tick, 'Second': Resolution.Second,
             'Minute': Resolution.Minute, 'M': Resolution.Minute,
             'Hour': Resolution.Hour, '1H': Resolution.Hour, '4H': Resolution.Hour, 'H': Resolution.Hour,
             'Daily': Resolution.Daily, 'Day': Resolution.Daily, 'D': Resolution.Daily,
             'Weekly': Resolution.Daily, 'W': Resolution.Daily}
        return m.get(resolution_str, Resolution.Daily)


class AdvancedGreeksFilter:
    """
    Filter option contracts based on Gamma at entry time.

    This is different from PortfolioGreeksFilter which limits portfolio-level exposure.
    This filter checks individual contracts before they are selected for a trade.

    Greeks filtered:
    - Gamma: Rate of change of Delta (avoid high-gamma ATM zones)
    """

    def __init__(self, algo):
        self.algo = algo
        # Greek thresholds (None = disabled)
        self.max_gamma = None

    def configure(self, max_gamma=None):
        """Configure Greek thresholds - only Gamma is supported (native QC data)"""
        self.max_gamma = max_gamma

        enabled = []
        if max_gamma is not None:
            enabled.append(f"Gamma<{max_gamma}")

        self.algo.Log(f"[+] Advanced Greeks filter: {', '.join(enabled) if enabled else 'none'}")

    def should_enter_contract(self, contract):
        """
        Check if individual option contract passes Greek thresholds.
        Returns True if contract passes all enabled filters, False otherwise.
        """
        try:
            # Get Greeks from contract
            if not hasattr(contract, 'Greeks') or contract.Greeks is None:
                # No Greeks available, allow trade (conservative approach)
                return True

            greeks = contract.Greeks

            # Check Gamma (most commonly available)
            if self.max_gamma is not None:
                gamma = abs(greeks.Gamma) if hasattr(greeks, 'Gamma') and greeks.Gamma else 0
                if gamma > self.max_gamma:
                    self.algo.Log(f"[X] Gamma too high: {gamma:.4f} > {self.max_gamma}")
                    return False

            return True

        except Exception as e:
            self.algo.Log(f"[!] Advanced Greeks filter error: {e}")
            return True  # Allow on error (conservative)

    def filter_contracts(self, contracts):
        """
        Filter a list of contracts, returning only those that pass Greek thresholds.
        Useful for batch filtering in StrikeSelector.
        """
        filtered = []
        for contract in contracts:
            if self.should_enter_contract(contract):
                filtered.append(contract)

        if len(filtered) < len(contracts):
            self.algo.Log(f"[+] Greeks filter: {len(contracts)} -> {len(filtered)} contracts")

        return filtered


class EarningsFilter:
    """Skip trade entries within N days of an earnings announcement"""

    def __init__(self, algo):
        self.algo = algo

    def should_enter_trade(self, ticker, skip_days):
        """Return False if earnings are within skip_days"""
        try:
            security = self.algo.Securities[ticker]
            # QuantConnect exposes earnings date via Fundamentals
            fundamentals = getattr(security, 'Fundamentals', None)
            if fundamentals is None:
                return True

            earnings_dates = getattr(
                getattr(getattr(fundamentals, 'EarningReports', None), 'EarningsDate', None),
                'Value', None
            )
            if not earnings_dates:
                return True

            # earnings_dates may be a single datetime or a list
            if not hasattr(earnings_dates, '__iter__') or isinstance(earnings_dates, str):
                earnings_dates = [earnings_dates]

            current_date = self.algo.Time.date()
            for ed in earnings_dates:
                try:
                    if hasattr(ed, 'date'):
                        ed = ed.date()
                    days_diff = abs((ed - current_date).days)
                    if days_diff <= skip_days:
                        self.algo.Log(
                            f"[X] Earnings filter: {ticker} earnings on {ed} "
                            f"({days_diff}d away, skip={skip_days}d)"
                        )
                        return False
                except Exception:
                    continue

            return True

        except Exception as e:
            self.algo.Log(f"[!] Earnings filter error: {e}")
            return True  # fail open — don't block trade on error
