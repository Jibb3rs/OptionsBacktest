# Options Backtesting System — Claude Onboarding Guide

> **Purpose of this file:** Cross-device context sync for Claude Code sessions. Read this first before making any changes.

---

## What This Project Is

A PyQt5 desktop application that lets traders configure options strategies through a GUI, then **generates complete QuantConnect Python algorithms** ready to paste and run. No manual coding required on the user's end.

**Stack:** Python, PyQt5, Apache ECharts (via QWebEngineView), QuantConnect cloud backend

**Entry point:** `main_pyqt.py` (run this — `main.py` is the old Tkinter version, ignore it)

---

## Workflow

```
GUI Config → Generate Code → Paste into QuantConnect → Run Backtest → Import CSV → Analyze Results
```

1. User picks strategy, ticker, dates, deltas in the **Configure Backtest** tab
2. Enables filters/indicators in **Advanced Filters** and **Indicators** tabs
3. Clicks Generate → copies the self-contained `.py` file to QuantConnect
4. Runs the backtest on QuantConnect cloud
5. Imports the results CSV into the **Trade Analysis** tab

---

## Project Structure

```
OptionsBacktest/
├── main_pyqt.py              ← Entry point (PyQt5)
├── test_all.py               ← Full test suite (run this to verify state)
├── requirements.txt
├── PROJECT_CONTEXT.txt       ← Master reference doc (1250+ lines, very detailed)
│
├── strategies/
│   ├── base_strategy.py      ← CODE GENERATION ENGINE (★ most critical file, ~1000 lines)
│   ├── advanced_filters.py   ← All filter classes (858 lines)
│   ├── iron_condor.py        ← 1 of 22 strategy files
│   └── ... (21 more strategy files)
│
├── gui/
│   ├── pyqt_main_window.py   ← Main window + tab manager
│   ├── pyqt_config_tab.py    ← Strategy/ticker/dates config
│   ├── pyqt_advanced_tab.py  ← Advanced filters UI
│   ├── pyqt_indicators_tab.py
│   ├── pyqt_analysis_tab.py  ← MAE/MFE charts, equity curve
│   ├── pyqt_compare_tab.py   ← Multi-strategy comparison
│   ├── pyqt_settings_tab.py
│   ├── echarts_widget.py     ← Apache ECharts wrapper
│   ├── advanced_filters.py   ← Filter UI logic (separate from strategies/)
│   ├── indicators.py         ← Indicator UI logic
│   └── assets/echarts.min.js
│
├── core/
│   ├── analyzer.py           ← MAE/MFE metrics
│   ├── indicators.py         ← Indicator implementations
│   ├── iron_condor.py
│   └── strike_selector.py
│
├── config/
│   ├── indicators.json       ← 15 indicator metadata entries
│   ├── strategies.json       ← 22 strategy definitions
│   └── settings.json
│
├── licensing/
│   ├── validator.py          ← Ed25519 license validation
│   └── keygen.py
│
├── presets/                  ← Saved configs (iron condor presets)
└── output/                   ← Generated QuantConnect .py files
```

---

## 22 Supported Strategies

| Category | Strategies |
|----------|-----------|
| Neutral | Iron Condor, Iron Butterfly, Short Strangle, Short Straddle, Butterfly Spread |
| Bullish | Bull Put Spread, Bull Call Spread, Long Call |
| Bearish | Bear Call Spread, Bear Put Spread, Long Put |
| Volatility | Long Strangle, Long Straddle |
| Time-based | Calendar Spread, Diagonal Spread |
| Advanced | Ratio Spread, Jade Lizard, Covered Call, Protective Put, Collar, Custom Strategy |

Each strategy lives in `strategies/<name>.py` as a class with a `generate_code(config)` static method.

---

## 16 Technical Indicators

**Momentum:** RSI, MACD, Stochastic, CCI, Williams %R
**Trend:** SMA, EMA, ADX, SuperTrend
**Volatility:** ATR, Bollinger Bands, Keltner Channels
**Volume:** VWAP, OBV, MFI

---

## 12 Advanced Filters

| Filter | Config Key | Notes |
|--------|-----------|-------|
| VIXFilter | `vix_*` | Min/max VIX levels |
| IVRankFilter | `ivr_*` | IV percentile |
| MarketProfileFilter | `mp_*` | TPO/VAL/VAH levels |
| VolatilityRegimeFilter | `vr_*` | Low/Med/High vol detection |
| ExpirationFilter | `exp_*` | Monthly/Weekly/EOM/Quarterly |
| LiquidityFilter | `liq_*` | Bid-ask spread + open interest |
| EarningsFilter | `earnings_*` | Avoid ±N days around earnings |
| PortfolioGreeksFilter | `pg_*` | **INCOMPLETE — see Known Issues** |
| CorrelationFilter | `corr_*` | Avoid correlated positions |
| MultiTimeframeFilter | `mtf_*` | Cross-timeframe alignment |
| AdvancedGreeksFilter | `ag_*` | **PARTIAL — only Gamma works** |
| DynamicPositionSizer | `dps_*` | Kelly/Vol/Greeks-based sizing |

---

## Current Test Status

Run `python3 test_all.py` to check.

```
Section 1:   Strategy Imports             21/21  PASS
Section 2:   Code Generation              21/21  PASS
Section 3:   Stop Loss Modes               4/4   PASS
Section 4:   Strike Selection              4/4   PASS
Section 5:   Individual Indicators        15/15  PASS
Section 6:   All Indicators Combined       1/1   PASS
Section 7:   Advanced Filters             17/17  PASS  (3 MTF variants)
Section 8:   All Filters Combined          1/1   PASS
Section 8b:  MTF Content Validation        4/4   PASS  (confirms dicts in generated code)
Section 9:   Kitchen Sink                  5/5   PASS
Section 10:  Edge Cases                    8/8   PASS
Section 11:  License System                2/2   WARN  (cryptography lib not installed)
Section 12:  Syntax Check                 21/21  PASS
Section 12:  Core Modules                  4/4   PASS
```

Last known state: **all core tests passing** — license section needs `pip install cryptography` (non-critical)

---

## Known Issues & Incomplete Features

### 0. Oscillator Conditions Not Strict — FIXED
RSI, Stochastic, CCI, Williams %R were all letting "neutral" readings through when a specific condition (overbought/oversold) was selected. E.g. RSI set to "overbought" was passing entries at RSI=41 and logging "RSI neutral" as a pass reason instead of blocking.

**Fix:** All four oscillators now strictly enforce the condition — if you pick "overbought", entries are blocked unless the indicator is actually above the overbought threshold. No more neutral pass-through.

Confirmed in QuantConnect logs (before fix): `[✓] Indicators: RSI neutral (41.0)` entering a Bear Put Spread — should have been blocked.

### 1. Multi-Timeframe Filter — FIXED
Root cause was in the GUI → code generation pipeline (not the filter itself):

- **GUI** (`gui/pyqt_advanced_tab.py`) sends a plain string like `"1H + 4H + Daily"` from a QComboBox
- **`base_strategy.py`** was doing raw `repr()` on it → generated code had `timeframes='1H + 4H + Daily'`
- **`MultiTimeframeFilter`** expected a **list of dicts** with `resolution/indicator/condition` keys → silent crash → filter bypassed entirely

**Fix applied:** `BaseStrategy._parse_mtf_timeframes()` now converts any format (string, list of strings, list of dicts) into proper list-of-dicts before embedding in generated code. `_parse_resolution()` in `advanced_filters.py` also extended to handle `'1H'`, `'4H'`, `'D'`, `'W'` abbreviations.

**Limitation remaining:** MTF only supports 5 indicators (SMA, EMA, RSI, MACD, ADX). The GUI uses SMA-50-above as default for all timeframe slots in the preset combos.

### 2. Portfolio Greeks Filter — NOT FUNCTIONAL
- Code is generated but the actual check logic is commented out / placeholder
- Location: `strategies/base_strategy.py` lines ~901–907
- Comment says "implement in strategy-specific code" — was never finished
- **Severity:** Medium — feature appears in UI but does nothing

### 3. Advanced Greeks Filter — INTENTIONAL (Gamma only)
- Only Max Gamma is implemented — this is by design, the others weren't useful
- Previously tested and confirmed working

### 4. Cryptography Library Missing
- `pip install cryptography>=41.0.0` to fix
- Only affects the licensing/key validation system
- Does not affect core functionality at all

---

## Code Generation Architecture

Understanding this is essential for any backend changes:

```
strategies/<strategy>.py
  └── generate_code(config: dict) → str
        └── calls BaseStrategy methods:
              generate_imports()
              generate_config_loader()
              generate_indicator_manager()
              generate_advanced_filters()      ← only includes enabled filters
              generate_initialize_base()
              generate_position_tracking()
```

The output is a **single self-contained Python string** (~30KB). No external imports. Designed to fit QuantConnect's file size limits.

Config dict keys are documented in `PROJECT_CONTEXT.txt`.

---

## GUI Architecture

Tabs are loaded into `gui/pyqt_main_window.py`. Each tab is a separate widget class in its own file. Communication between tabs goes through the main window or directly via the config dict built at generation time.

Theme/colors: `gui/pyqt_theme.py`
ECharts charting: `gui/echarts_widget.py` (wraps QWebEngineView)

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt
pip install cryptography>=41.0.0  # optional, for licensing

# Launch app
python main_pyqt.py

# Run tests
python test_all.py
```

---

## Where to Look for Specific Things

| Task | File |
|------|------|
| Fix multi-timeframe bug | `strategies/advanced_filters.py` + `gui/pyqt_advanced_tab.py` + `strategies/base_strategy.py` |
| Add a new strategy | Copy existing `strategies/bull_put_spread.py`, add to `config/strategies.json` |
| Add a new filter | Add class to `strategies/advanced_filters.py`, add UI to `gui/pyqt_advanced_tab.py`, hook into `base_strategy.py` |
| Add a new indicator | `strategies/indicators.py` (or `gui/indicators.py`), update `config/indicators.json` |
| Change chart behavior | `gui/echarts_widget.py` + ECharts JS in `gui/assets/echarts.min.js` |
| Understand full config schema | `PROJECT_CONTEXT.txt` |

---

## Developer Notes

- **DO NOT** modify `main.py` — it's the old Tkinter version, kept for reference only
- All generated code must remain self-contained (no pip imports) for QuantConnect compatibility
- The `strategies/` directory has a `advanced_filters.py` AND `gui/` has its own `advanced_filters.py` — these are different files with different responsibilities (code gen vs UI)
- Same for `indicators.py` — there's one in `strategies/`, one in `gui/`, one in `core/`
- Presets are stored as JSON in `presets/` and loaded at runtime
- Generated output goes to `output/` directory
