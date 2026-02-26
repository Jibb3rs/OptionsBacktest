"""
Technical Indicators for Entry Filtering
Implements RSI, ATR, VIX checks for Iron Condor entry
"""

class IndicatorManager:
    """
    Manages technical indicators for trade filtering
    """
    
    def __init__(self, algorithm):
        """
        Initialize indicator manager
        
        Args:
            algorithm: QCAlgorithm instance
        """
        self.algo = algorithm
        self.indicators = {}
    
    def initialize_indicators(self, symbol, enabled_indicators):
        """
        Set up indicators based on config
        
        Args:
            symbol: Underlying symbol
            enabled_indicators: Dict of enabled indicators from config
        """
        
        self.algo.Log("📈 Initializing indicators...")
        
        # RSI (Relative Strength Index)
        if 'RSI' in enabled_indicators:
            self.indicators['RSI'] = self.algo.RSI(symbol, 14, 0, 1)  # 14-period daily RSI
            self.algo.Log("   ✓ RSI (14)")
        
        # ATR (Average True Range)
        if 'ATR' in enabled_indicators:
            self.indicators['ATR'] = self.algo.ATR(symbol, 14, 0, 1)  # 14-period daily ATR
            self.algo.Log("   ✓ ATR (14)")
        
        # For VIX, we'll add it separately
        if 'VIX' in enabled_indicators:
            try:
                vix = self.algo.AddIndex("VIX", 1)  # Resolution.Daily = 1
                self.indicators['VIX'] = vix
                self.algo.Log("   ✓ VIX")
            except:
                self.algo.Log("   ⚠️  VIX not available")
        
        # MACD
        if 'MACD' in enabled_indicators:
            self.indicators['MACD'] = self.algo.MACD(symbol, 12, 26, 9, 0, 1)
            self.algo.Log("   ✓ MACD (12,26,9)")
        
        # Add more indicators as needed
        
        self.algo.Log("✅ Indicators initialized\n")
    
    def check_entry_conditions(self):
        """
        Check if all indicator conditions are met for entry
        
        Returns:
            Tuple (allowed: bool, reason: str)
        """
        
        reasons = []
        
        # RSI Check: Avoid overbought/oversold
        if 'RSI' in self.indicators:
            rsi = self.indicators['RSI']
            if rsi.IsReady:
                rsi_value = rsi.Current.Value
                
                if rsi_value > 70:
                    return False, f"RSI overbought ({rsi_value:.1f} > 70)"
                elif rsi_value < 30:
                    return False, f"RSI oversold ({rsi_value:.1f} < 30)"
                else:
                    reasons.append(f"RSI OK ({rsi_value:.1f})")
        
        # ATR Check: Avoid high volatility
        if 'ATR' in self.indicators:
            atr = self.indicators['ATR']
            if atr.IsReady:
                atr_value = atr.Current.Value
                
                # Get historical average (simplified)
                # In production, you'd compare to 20-day average
                if atr_value > 50:  # Example threshold
                    return False, f"ATR too high ({atr_value:.2f} > 50)"
                else:
                    reasons.append(f"ATR OK ({atr_value:.2f})")
        
        # VIX Check: Avoid fearful markets
        if 'VIX' in self.indicators:
            try:
                vix_price = self.algo.Securities["VIX"].Price
                
                if vix_price > 30:
                    return False, f"VIX too high ({vix_price:.1f} > 30)"
                else:
                    reasons.append(f"VIX OK ({vix_price:.1f})")
            except:
                pass
        
        # MACD Check: Trend confirmation
        if 'MACD' in self.indicators:
            macd = self.indicators['MACD']
            if macd.IsReady:
                # Check if MACD is positive (bullish) or negative (bearish)
                macd_value = macd.Current.Value
                signal = macd.Signal.Current.Value
                
                # For Iron Condor, we prefer neutral/range-bound
                # If too strong trend, skip
                if abs(macd_value - signal) > 2:  # Example threshold
                    return False, f"MACD trending too strong"
                else:
                    reasons.append("MACD neutral")
        
        # All checks passed
        return True, " | ".join(reasons) if reasons else "All indicators OK"
    
    def log_indicator_status(self):
        """Log current indicator values"""
        
        self.algo.Log("📊 INDICATOR STATUS:")
        
        if 'RSI' in self.indicators and self.indicators['RSI'].IsReady:
            rsi_value = self.indicators['RSI'].Current.Value
            self.algo.Log(f"   RSI: {rsi_value:.1f}")
        
        if 'ATR' in self.indicators and self.indicators['ATR'].IsReady:
            atr_value = self.indicators['ATR'].Current.Value
            self.algo.Log(f"   ATR: {atr_value:.2f}")
        
        if 'VIX' in self.indicators:
            try:
                vix_price = self.algo.Securities["VIX"].Price
                self.algo.Log(f"   VIX: {vix_price:.1f}")
            except:
                pass
        
        if 'MACD' in self.indicators and self.indicators['MACD'].IsReady:
            macd = self.indicators['MACD']
            self.algo.Log(f"   MACD: {macd.Current.Value:.2f}")
            self.algo.Log(f"   Signal: {macd.Signal.Current.Value:.2f}")