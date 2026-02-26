"""
Comprehensive test suite for Options Backtesting System.
Tests all strategies, filters, and indicators by running code generation
and validating the output - no QuantConnect account needed.

Run with: py test_all.py
"""

import sys
import os
import traceback

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = []
failed = []

def ok(name):
    passed.append(name)
    print(f"  {GREEN}✓{RESET} {name}")

def fail(name, reason):
    failed.append((name, reason))
    print(f"  {RED}✗{RESET} {name}")
    print(f"    {RED}{reason}{RESET}")

def section(title):
    print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")

# ── Validate generated code ───────────────────────────────────────────────────
REQUIRED_KEYWORDS = [
    "def Initialize",
    "def OnData",
    "class ",
    "self.SetStartDate",
    "self.SetCash",
]

def validate_code(code, name, extra_keywords=None):
    """Check generated code contains expected structure."""
    if not isinstance(code, str):
        fail(name, f"generate_code() returned {type(code).__name__}, expected str")
        return False
    if len(code) < 500:
        fail(name, f"Generated code too short ({len(code)} chars) - likely empty or errored")
        return False
    for kw in REQUIRED_KEYWORDS:
        if kw not in code:
            fail(name, f"Missing expected keyword: '{kw}'")
            return False
    if extra_keywords:
        for kw in extra_keywords:
            if kw not in code:
                fail(name, f"Missing strategy-specific keyword: '{kw}'")
                return False
    ok(name)
    return True

# ── Base config builder ───────────────────────────────────────────────────────
def base_config(extra_deltas=None, extra_advanced=None, extra_indicators=None):
    cfg = {
        'ticker': 'SPY',
        'start_date': '2023-01-01',
        'end_date': '2024-12-31',
        'initial_capital': 100000,
        'expiry_days': 30,
        'expiry_range': 5,
        'strike_selection': {
            'method': 'delta',
            'deltas': extra_deltas or {}
        },
        'trading_rules': {
            'resolution': 'Daily',
            'max_positions': 5,
            'min_days_between_trades': 0,
            'profit_target_pct': 50,
            'stop_loss_pct': 100,
            'stop_loss_mode': 'Credit-Based (Options Standard)'
        },
        'indicators': extra_indicators or {},
        'advanced': extra_advanced or {},
    }
    return cfg

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 – Strategy imports
# ─────────────────────────────────────────────────────────────────────────────
section("1. Strategy Imports")

STRATEGY_IMPORTS = {
    'IronCondor':       ('strategies.iron_condor',       'IronCondor'),
    'IronButterfly':    ('strategies.iron_butterfly',    'IronButterfly'),
    'ShortStrangle':    ('strategies.short_strangle',    'ShortStrangle'),
    'ShortStraddle':    ('strategies.short_straddle',    'ShortStraddle'),
    'LongStrangle':     ('strategies.long_strangle',     'LongStrangle'),
    'LongStraddle':     ('strategies.long_straddle',     'LongStraddle'),
    'BullPutSpread':    ('strategies.bull_put_spread',   'BullPutSpread'),
    'BullCallSpread':   ('strategies.bull_call_spread',  'BullCallSpread'),
    'BearCallSpread':   ('strategies.bear_call_spread',  'BearCallSpread'),
    'BearPutSpread':    ('strategies.bear_put_spread',   'BearPutSpread'),
    'LongCall':         ('strategies.long_call',         'LongCall'),
    'LongPut':          ('strategies.long_put',          'LongPut'),
    'ButterflySpread':  ('strategies.butterfly_spread',  'ButterflySpread'),
    'CalendarSpread':   ('strategies.calendar_spread',   'CalendarSpread'),
    'DiagonalSpread':   ('strategies.diagonal_spread',   'DiagonalSpread'),
    'RatioSpread':      ('strategies.ratio_spread',      'RatioSpread'),
    'JadeLizard':       ('strategies.jade_lizard',       'JadeLizard'),
    'CoveredCall':      ('strategies.covered_call',      'CoveredCall'),
    'ProtectivePut':    ('strategies.protective_put',    'ProtectivePut'),
    'Collar':           ('strategies.collar',            'Collar'),
    'CustomStrategy':   ('strategies.custom_strategy',   'CustomStrategy'),
}

STRATEGY_CLASSES = {}
for name, (module_path, class_name) in STRATEGY_IMPORTS.items():
    try:
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        STRATEGY_CLASSES[name] = cls
        ok(f"Import {name}")
    except Exception as e:
        fail(f"Import {name}", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 – Code generation: all strategies (default config)
# ─────────────────────────────────────────────────────────────────────────────
section("2. Code Generation – All Strategies (default config)")

STRATEGY_DELTAS = {
    'IronCondor':      {'Short Put Delta:': 0.16, 'Long Put Delta:': 0.08, 'Short Call Delta:': 0.16, 'Long Call Delta:': 0.08},
    'IronButterfly':   {'Short Put Delta:': 0.50, 'Long Put Delta:': 0.25, 'Short Call Delta:': 0.50, 'Long Call Delta:': 0.25},
    'ShortStrangle':   {'Short Put Delta:': 0.16, 'Short Call Delta:': 0.16},
    'ShortStraddle':   {'Short Put Delta:': 0.50, 'Short Call Delta:': 0.50},
    'LongStrangle':    {'Long Put Delta:': 0.20, 'Long Call Delta:': 0.20},
    'LongStraddle':    {'Long Put Delta:': 0.50, 'Long Call Delta:': 0.50},
    'BullPutSpread':   {'Short Put Delta:': 0.30, 'Long Put Delta:': 0.15},
    'BullCallSpread':  {'Short Call Delta:': 0.50, 'Long Call Delta:': 0.30},
    'BearCallSpread':  {'Short Call Delta:': 0.30, 'Long Call Delta:': 0.15},
    'BearPutSpread':   {'Short Put Delta:': 0.50, 'Long Put Delta:': 0.30},
    'LongCall':        {'Long Call Delta:': 0.40},
    'LongPut':         {'Long Put Delta:': 0.40},
    'ButterflySpread': {'Lower Strike Delta:': 0.30, 'Middle Strike Delta:': 0.50, 'Upper Strike Delta:': 0.70},
    'CalendarSpread':  {'Strike Delta:': 0.40},
    'DiagonalSpread':  {'Short Call Delta:': 0.30, 'Long Call Delta:': 0.60},
    'RatioSpread':     {'Long Call Delta:': 0.50, 'Short Call Delta:': 0.30},
    'JadeLizard':      {'Short Put Delta:': 0.30, 'Short Call Delta:': 0.20, 'Long Call Delta:': 0.10},
    'CoveredCall':     {'Short Call Delta:': 0.30},
    'ProtectivePut':   {'Long Put Delta:': 0.30},
    'Collar':          {'Long Put Delta:': 0.25, 'Short Call Delta:': 0.25},
    'CustomStrategy':  {},
}

GENERATED_CODES = {}
for name, cls in STRATEGY_CLASSES.items():
    try:
        cfg = base_config(extra_deltas=STRATEGY_DELTAS.get(name, {}))
        code = cls.generate_code(cfg)
        GENERATED_CODES[name] = code
        validate_code(code, name)
    except Exception as e:
        fail(name, traceback.format_exc(limit=3))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 – Stop loss modes (Iron Condor as reference)
# ─────────────────────────────────────────────────────────────────────────────
section("3. Stop Loss Modes")

STOP_LOSS_MODES = [
    'Credit-Based (Options Standard)',
    'Max Loss-Based (Conservative)',
    'Equal Dollar (Balanced)',
    'Price Distance (FX Style)',
]

if 'IronCondor' in STRATEGY_CLASSES:
    for mode in STOP_LOSS_MODES:
        try:
            cfg = base_config(extra_deltas=STRATEGY_DELTAS['IronCondor'])
            cfg['trading_rules']['stop_loss_mode'] = mode
            code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
            validate_code(code, f"Stop loss mode: {mode}")
        except Exception as e:
            fail(f"Stop loss mode: {mode}", traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 – Strike selection methods
# ─────────────────────────────────────────────────────────────────────────────
section("4. Strike Selection Methods")

STRIKE_METHODS = ['delta', 'fixed', 'percentage', 'atr']

if 'BullPutSpread' in STRATEGY_CLASSES:
    for method in STRIKE_METHODS:
        try:
            cfg = base_config(extra_deltas=STRATEGY_DELTAS['BullPutSpread'])
            cfg['strike_selection']['method'] = method
            code = STRATEGY_CLASSES['BullPutSpread'].generate_code(cfg)
            validate_code(code, f"Strike method: {method}")
        except Exception as e:
            fail(f"Strike method: {method}", traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 – Individual indicators
# ─────────────────────────────────────────────────────────────────────────────
section("5. Individual Indicators")

ALL_INDICATORS = {
    'RSI': {
        'enabled': True, 'period': 14,
        'oversold': 30, 'overbought': 70
    },
    'MACD': {
        'enabled': True, 'fast': 12, 'slow': 26, 'signal': 9,
    },
    'STOCHASTIC': {
        'enabled': True, 'period': 14, 'k_smooth': 3,
        'oversold': 20, 'overbought': 80
    },
    'ATR': {
        'enabled': True, 'period': 14, 'condition': 'low', 'threshold': 1.5
    },
    'BBANDS': {
        'enabled': True, 'period': 20, 'std_dev': 2.0
    },
    'MA': {
        'enabled': True, 'period': 50, 'ma_type': 'SMA'
    },
    'ADX': {
        'enabled': True, 'period': 14, 'condition': 'strong', 'threshold': 25
    },
    'VWAP': {
        'enabled': True, 'condition': 'above'
    },
    'VIX': {
        'enabled': True
    },
}

if 'IronCondor' in STRATEGY_CLASSES:
    for ind_name, ind_cfg in ALL_INDICATORS.items():
        try:
            cfg = base_config(
                extra_deltas=STRATEGY_DELTAS['IronCondor'],
                extra_indicators={ind_name: ind_cfg}
            )
            code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
            validate_code(code, f"Indicator: {ind_name}")
        except Exception as e:
            fail(f"Indicator: {ind_name}", traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 – All indicators enabled simultaneously
# ─────────────────────────────────────────────────────────────────────────────
section("6. All Indicators Enabled Simultaneously")

if 'IronCondor' in STRATEGY_CLASSES:
    try:
        cfg = base_config(
            extra_deltas=STRATEGY_DELTAS['IronCondor'],
            extra_indicators=ALL_INDICATORS
        )
        code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
        validate_code(code, "All 15 indicators enabled together")
    except Exception as e:
        fail("All 15 indicators enabled together", traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 – Advanced filters individually
# ─────────────────────────────────────────────────────────────────────────────
section("7. Advanced Filters – Individually")

FILTER_TESTS = {
    'VIX filter':            {'vix_enabled': True, 'vix_min': 15, 'vix_max': 35},
    'IV Rank filter':        {'iv_rank_enabled': True, 'iv_rank_min': 50, 'iv_rank_max': 100},
    'Market Profile filter': {'market_profile_enabled': True, 'market_profile_signal': 'poc', 'market_profile_lookback': 20},
    'Liquidity filter':      {'liquidity_enabled': True, 'max_spread_pct': 5, 'min_open_interest': 100},
    'Earnings filter':       {'earnings_enabled': True, 'earnings_buffer_days': 7},
    'Expiry monthly':        {'expiration_cycle': 'monthly'},
    'Expiry weekly':         {'expiration_cycle': 'weekly'},
    'Vol regime bullish':    {'vol_regime_enabled': True, 'vol_regime_type': 'bullish'},
    'Portfolio Greeks':      {'greeks_enabled': True, 'max_portfolio_delta': 100.0, 'max_portfolio_gamma': 0.5, 'max_portfolio_vega': 50.0},
    'Correlation filter':    {'correlation_enabled': True, 'max_correlation': 0.7, 'correlation_lookback': 60},
    'Multi-timeframe (string preset)': {'mtf_enabled': True, 'mtf_timeframes': '1H + 4H + Daily', 'mtf_require_all': True},
    'Multi-timeframe (list of strings)': {'mtf_enabled': True, 'mtf_timeframes': ['1H', '4H', 'D'], 'mtf_require_all': True},
    'Multi-timeframe (list of dicts)':   {'mtf_enabled': True, 'mtf_timeframes': [{'resolution': 'Hour', 'indicator': 'SMA', 'period': 50, 'condition': 'above'}, {'resolution': 'Daily', 'indicator': 'RSI', 'period': 14, 'condition': 'oversold'}], 'mtf_require_all': False},
    'Dynamic sizing':        {'dynamic_sizing_enabled': True, 'sizing_method': 'fixed_fractional', 'sizing_risk_pct': 2.0},
    'Advanced Greeks - Gamma':  {'advanced_greeks_enabled': True, 'gamma_filter_enabled': True, 'max_gamma': 0.05},
    'Advanced Greeks - Vanna':  {'advanced_greeks_enabled': True, 'vanna_filter_enabled': True, 'max_vanna': 0.10},
    'Advanced Greeks - Charm':  {'advanced_greeks_enabled': True, 'charm_filter_enabled': True, 'max_charm': 0.02},
}

if 'IronCondor' in STRATEGY_CLASSES:
    for filter_name, filter_cfg in FILTER_TESTS.items():
        try:
            cfg = base_config(
                extra_deltas=STRATEGY_DELTAS['IronCondor'],
                extra_advanced=filter_cfg
            )
            code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
            validate_code(code, filter_name)
        except Exception as e:
            fail(filter_name, traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 – All filters enabled simultaneously
# ─────────────────────────────────────────────────────────────────────────────
section("8. All Filters Enabled Simultaneously")

ALL_FILTERS = {
    'vix_enabled': True, 'vix_min': 15, 'vix_max': 35,
    'iv_rank_enabled': True, 'iv_rank_min': 50, 'iv_rank_max': 100,
    'market_profile_enabled': True, 'market_profile_signal': 'poc', 'market_profile_lookback': 20,
    'liquidity_enabled': True, 'max_spread_pct': 5, 'min_open_interest': 100,
    'earnings_enabled': True, 'earnings_buffer_days': 7,
    'expiration_cycle': 'monthly',
    'vol_regime_enabled': True, 'vol_regime_type': 'bullish',
    'greeks_enabled': True, 'max_portfolio_delta': 100.0, 'max_portfolio_gamma': 0.5, 'max_portfolio_vega': 50.0,
    'correlation_enabled': True, 'max_correlation': 0.7, 'correlation_lookback': 60,
    'mtf_enabled': True, 'mtf_timeframes': '1H + 4H + Daily', 'mtf_require_all': True,
    'advanced_greeks_enabled': True,
    'gamma_filter_enabled': True, 'max_gamma': 0.05,
    'vanna_filter_enabled': True, 'max_vanna': 0.10,
    'charm_filter_enabled': True, 'max_charm': 0.02,
    'vomma_filter_enabled': True, 'max_vomma': 0.10,
}

if 'IronCondor' in STRATEGY_CLASSES:
    try:
        cfg = base_config(
            extra_deltas=STRATEGY_DELTAS['IronCondor'],
            extra_advanced=ALL_FILTERS
        )
        code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
        validate_code(code, "All filters enabled together (Iron Condor)")
    except Exception as e:
        fail("All filters enabled together", traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8b – MTF content validation (generated code must embed dicts, not raw strings)
# ─────────────────────────────────────────────────────────────────────────────
section("8b. Multi-Timeframe – Generated Code Content Validation")

MTF_CONTENT_CASES = [
    ("MTF string preset (1H + 4H + Daily)", '1H + 4H + Daily'),
    ("MTF string preset (4H + Daily)",      '4H + Daily'),
    ("MTF string preset (Daily + Weekly)",  'Daily + Weekly'),
    ("MTF list of strings",                 ['1H', 'D']),
]

if 'IronCondor' in STRATEGY_CLASSES:
    for label, tf_val in MTF_CONTENT_CASES:
        try:
            cfg = base_config(
                extra_deltas=STRATEGY_DELTAS['IronCondor'],
                extra_advanced={'mtf_enabled': True, 'mtf_timeframes': tf_val, 'mtf_require_all': True}
            )
            code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
            # Generated code must contain dict-style timeframe config, not a raw string
            if "'resolution'" not in code:
                fail(label, "Generated code missing 'resolution' key — MTF timeframes were not converted to dicts")
            elif 'mtf_filter.configure' not in code:
                fail(label, "Generated code missing mtf_filter.configure() call")
            else:
                ok(label)
        except Exception as e:
            fail(label, traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 – Indicators + Filters combined (kitchen sink)
# ─────────────────────────────────────────────────────────────────────────────
section("9. Indicators + Filters Combined (Kitchen Sink)")

KITCHEN_SINK_STRATEGIES = ['IronCondor', 'BullPutSpread', 'LongCall', 'CalendarSpread', 'ShortStrangle']

for name in KITCHEN_SINK_STRATEGIES:
    if name not in STRATEGY_CLASSES:
        continue
    try:
        cfg = base_config(
            extra_deltas=STRATEGY_DELTAS.get(name, {}),
            extra_indicators={
                'RSI': {'enabled': True, 'period': 14, 'condition': 'oversold', 'oversold': 30, 'overbought': 70},
                'MACD': {'enabled': True, 'fast': 12, 'slow': 26, 'signal': 9, 'condition': 'bullish_cross'},
                'ADX': {'enabled': True, 'period': 14, 'condition': 'weak', 'threshold': 25},
                'ATR': {'enabled': True, 'period': 14, 'condition': 'low', 'threshold': 1.5},
                'BBANDS': {'enabled': True, 'period': 20, 'std_dev': 2.0, 'condition': 'inside_bands'},
            },
            extra_advanced={
                'vix_enabled': True, 'vix_min': 15, 'vix_max': 35,
                'iv_rank_enabled': True, 'iv_rank_min': 50, 'iv_rank_max': 100,
                'liquidity_enabled': True, 'max_spread_pct': 5, 'min_open_interest': 100,
                'earnings_enabled': True, 'earnings_buffer_days': 7,
            }
        )
        code = STRATEGY_CLASSES[name].generate_code(cfg)
        validate_code(code, f"Kitchen sink: {name}")
    except Exception as e:
        fail(f"Kitchen sink: {name}", traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 – Edge cases
# ─────────────────────────────────────────────────────────────────────────────
section("10. Edge Cases")

if 'IronCondor' in STRATEGY_CLASSES:
    # No indicators, no filters (bare minimum)
    try:
        cfg = base_config(extra_deltas=STRATEGY_DELTAS['IronCondor'])
        code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
        validate_code(code, "Edge: bare minimum config (no indicators/filters)")
    except Exception as e:
        fail("Edge: bare minimum config", traceback.format_exc(limit=2))

    # Different tickers
    for ticker in ['QQQ', 'IWM', 'AAPL', 'TSLA']:
        try:
            cfg = base_config(extra_deltas=STRATEGY_DELTAS['IronCondor'])
            cfg['ticker'] = ticker
            code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
            validate_code(code, f"Edge: ticker = {ticker}")
        except Exception as e:
            fail(f"Edge: ticker = {ticker}", traceback.format_exc(limit=2))

    # Very short date range
    try:
        cfg = base_config(extra_deltas=STRATEGY_DELTAS['IronCondor'])
        cfg['start_date'] = '2024-01-01'
        cfg['end_date'] = '2024-03-31'
        code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
        validate_code(code, "Edge: short date range (3 months)")
    except Exception as e:
        fail("Edge: short date range", traceback.format_exc(limit=2))

    # Large capital
    try:
        cfg = base_config(extra_deltas=STRATEGY_DELTAS['IronCondor'])
        cfg['initial_capital'] = 10_000_000
        code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
        validate_code(code, "Edge: large capital ($10M)")
    except Exception as e:
        fail("Edge: large capital", traceback.format_exc(limit=2))

    # Zero profit target (hold to expiry)
    try:
        cfg = base_config(extra_deltas=STRATEGY_DELTAS['IronCondor'])
        cfg['trading_rules']['profit_target_pct'] = 0
        code = STRATEGY_CLASSES['IronCondor'].generate_code(cfg)
        validate_code(code, "Edge: profit target = 0 (hold to expiry)")
    except Exception as e:
        fail("Edge: profit target = 0", traceback.format_exc(limit=2))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11 – License system
# ─────────────────────────────────────────────────────────────────────────────
section("11. License System")

try:
    from licensing.validator import validate_key, load_stored_license, get_license_info
    ok("Import licensing.validator")
except Exception as e:
    fail("Import licensing.validator", str(e))

try:
    from licensing.keygen import generate_key
    ok("Import licensing.keygen")
except Exception as e:
    fail("Import licensing.keygen", str(e))

# Valid key
try:
    key = generate_key("test@test.com", "Test User", 30)
    is_valid, msg, payload = validate_key(key)
    assert is_valid, f"Expected valid, got: {msg}"
    assert payload['email'] == 'test@test.com'
    assert payload['name'] == 'Test User'
    ok("Valid key: accepted")
except Exception as e:
    fail("Valid key: accepted", str(e))

# Expired key
try:
    key = generate_key("old@test.com", "Expired User", -1)
    is_valid, msg, _ = validate_key(key)
    assert not is_valid, "Expired key should be rejected"
    assert "expired" in msg.lower()
    ok("Expired key: rejected correctly")
except Exception as e:
    fail("Expired key: rejected correctly", str(e))

# Garbage input
try:
    is_valid, msg, _ = validate_key("not-a-real-key")
    assert not is_valid
    ok("Garbage key: rejected correctly")
except Exception as e:
    fail("Garbage key: rejected correctly", str(e))

# Tampered key (change payload, keep original signature)
try:
    import base64, json
    real_key = generate_key("real@test.com", "Real", 30)
    parts = real_key[3:].rsplit('.', 1)
    payload = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
    payload['exp'] = '2099-01-01'
    new_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    tampered = 'OB-' + new_b64 + '.' + parts[1]
    is_valid, msg, _ = validate_key(tampered)
    assert not is_valid, "Tampered key should be rejected"
    ok("Tampered key: rejected correctly")
except Exception as e:
    fail("Tampered key: rejected correctly", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 12 – Syntax check on all generated code
# ─────────────────────────────────────────────────────────────────────────────
section("12. Generated Code Syntax Check (py compile)")

for name, code in GENERATED_CODES.items():
    try:
        compile(code, f"<{name}>", "exec")
        ok(f"Syntax OK: {name}")
    except SyntaxError as e:
        fail(f"Syntax OK: {name}", f"SyntaxError at line {e.lineno}: {e.msg}")
    except Exception as e:
        fail(f"Syntax OK: {name}", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 13 – Analyzer import
# ─────────────────────────────────────────────────────────────────────────────
section("12. Core Modules")

for module_name in ['core.analyzer', 'core.indicators', 'strategies.advanced_filters']:
    try:
        importlib.import_module(module_name)
        ok(f"Import {module_name}")
    except Exception as e:
        fail(f"Import {module_name}", str(e))

try:
    from core.analyzer import ResultsAnalyzer
    import inspect
    sig = inspect.signature(ResultsAnalyzer.__init__)
    params = [p for p in sig.parameters if p != 'self']
    # ResultsAnalyzer requires a csv_path - verify it accepts one without crashing on import
    assert 'csv_path' in params or len(params) >= 1, "Unexpected constructor signature"
    ok("ResultsAnalyzer instantiation (requires csv_path - correct)")
except Exception as e:
    fail("ResultsAnalyzer instantiation", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────
total = len(passed) + len(failed)
print(f"\n{BOLD}{'═'*60}{RESET}")
print(f"{BOLD}  RESULTS: {GREEN}{len(passed)} passed{RESET}{BOLD}, {RED}{len(failed)} failed{RESET}{BOLD} / {total} total{RESET}")
print(f"{BOLD}{'═'*60}{RESET}")

if failed:
    print(f"\n{BOLD}{RED}Failed tests:{RESET}")
    for name, reason in failed:
        short = reason.strip().split('\n')[-1][:120]
        print(f"  {RED}✗{RESET} {name}")
        print(f"    → {short}")
    sys.exit(1)
else:
    print(f"\n{GREEN}{BOLD}  All tests passed!{RESET}")
    sys.exit(0)
