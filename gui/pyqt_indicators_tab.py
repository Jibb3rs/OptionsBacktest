"""
PyQt5 Indicators Tab - Technical Indicator Filters
Configure technical indicators that gate trade entries
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QDoubleSpinBox, QFrame, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt

from .pyqt_theme import C
from .pyqt_widgets import FilterSection

LABEL_WIDTH = 160
INPUT_WIDTH = 120


def _form_row(label_text, widget, parent_layout):
    """Add a label + widget row to parent_layout."""
    row = QHBoxLayout()
    row.setSpacing(10)
    lbl = QLabel(label_text)
    lbl.setFixedWidth(LABEL_WIDTH)
    row.addWidget(lbl)
    widget.setMinimumWidth(INPUT_WIDTH)
    widget.setMaximumWidth(INPUT_WIDTH + 30)
    row.addWidget(widget)
    row.addStretch()
    parent_layout.addLayout(row)


class IndicatorsTab(QWidget):
    """Technical indicator filter configuration — 2-per-row card grid"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._create_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setSpacing(14)
        layout.setContentsMargins(12, 12, 12, 12)

        # Info banner
        banner = QFrame()
        acc = C['accent']
        r, g, b = int(acc[1:3], 16), int(acc[3:5], 16), int(acc[5:7], 16)
        banner.setStyleSheet(
            f"QFrame {{ background-color: rgba({r},{g},{b},0.08); "
            f"border: 1px solid rgba({r},{g},{b},0.35); "
            f"border-left: 3px solid {acc}; border-radius: 4px; }}"
        )
        bl = QVBoxLayout(banner)
        bl.setContentsMargins(12, 10, 12, 10)
        bl.setSpacing(4)

        banner_title = QLabel("Conditions are set automatically")
        banner_title.setStyleSheet(
            f"font-weight: bold; color: {C['accent']}; border: none; background: transparent;"
        )
        bl.addWidget(banner_title)

        banner_body = QLabel(
            "You do not need to configure indicator directions manually. "
            "Based on your selected strategy, the system will automatically apply the correct condition:\n"
            "  \u2022  Bullish strategies \u2014 oscillators wait for oversold, price must be above MA / VWAP\n"
            "  \u2022  Bearish strategies \u2014 oscillators wait for overbought, price must be below MA / VWAP\n"
            "  \u2022  Neutral strategies \u2014 oscillators require mid-range readings, price inside bands"
        )
        banner_body.setWordWrap(True)
        banner_body.setStyleSheet("color: #8b949e; border: none; background: transparent;")
        bl.addWidget(banner_body)
        layout.addWidget(banner)

        # 2-column grid of indicator cards
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setAlignment(Qt.AlignTop)

        cards = [
            self._build_rsi_card(),
            self._build_macd_card(),
            self._build_stochastic_card(),
            self._build_atr_card(),
            self._build_bbands_card(),
            self._build_ma_card(),
            self._build_adx_card(),
            self._build_vwap_card(),
            self._build_vix_card(),
        ]

        for i, card in enumerate(cards):
            grid.addWidget(card, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch()

    # ------------------------------------------------------------------
    # Card builders — each returns a FilterSection
    # ------------------------------------------------------------------

    def _build_rsi_card(self):
        self.rsi_section = FilterSection("RSI  (Relative Strength Index)", initially_enabled=False)
        bl = self.rsi_section.body_layout()

        note = QLabel(
            "Bullish: waits for oversold.  Bearish: waits for overbought.  "
            "Neutral: requires price within range."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        bl.addWidget(note)

        self.rsi_period = QSpinBox()
        self.rsi_period.setRange(2, 200)
        self.rsi_period.setValue(14)
        _form_row("Period:", self.rsi_period, bl)

        self.rsi_oversold = QSpinBox()
        self.rsi_oversold.setRange(1, 99)
        self.rsi_oversold.setValue(30)
        _form_row("Oversold Level:", self.rsi_oversold, bl)

        self.rsi_overbought = QSpinBox()
        self.rsi_overbought.setRange(1, 99)
        self.rsi_overbought.setValue(70)
        _form_row("Overbought Level:", self.rsi_overbought, bl)

        return self.rsi_section

    def _build_macd_card(self):
        self.macd_section = FilterSection(
            "MACD  (Moving Average Convergence Divergence)", initially_enabled=False
        )
        bl = self.macd_section.body_layout()

        note = QLabel(
            "Bullish: requires MACD above signal.  "
            "Bearish: requires MACD below signal.  "
            "Neutral: requires MACD close to signal line."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        bl.addWidget(note)

        self.macd_fast = QSpinBox()
        self.macd_fast.setRange(2, 100)
        self.macd_fast.setValue(12)
        _form_row("Fast Period:", self.macd_fast, bl)

        self.macd_slow = QSpinBox()
        self.macd_slow.setRange(2, 200)
        self.macd_slow.setValue(26)
        _form_row("Slow Period:", self.macd_slow, bl)

        self.macd_signal = QSpinBox()
        self.macd_signal.setRange(2, 50)
        self.macd_signal.setValue(9)
        _form_row("Signal Period:", self.macd_signal, bl)

        return self.macd_section

    def _build_stochastic_card(self):
        self.stoch_section = FilterSection("Stochastic Oscillator", initially_enabled=False)
        bl = self.stoch_section.body_layout()

        note = QLabel(
            "Bullish: waits for oversold.  Bearish: waits for overbought.  "
            "Neutral: requires price within range."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        bl.addWidget(note)

        self.stoch_period = QSpinBox()
        self.stoch_period.setRange(2, 100)
        self.stoch_period.setValue(14)
        _form_row("Period:", self.stoch_period, bl)

        self.stoch_k_smooth = QSpinBox()
        self.stoch_k_smooth.setRange(1, 20)
        self.stoch_k_smooth.setValue(3)
        _form_row("%K Smoothing:", self.stoch_k_smooth, bl)

        self.stoch_oversold = QSpinBox()
        self.stoch_oversold.setRange(1, 99)
        self.stoch_oversold.setValue(20)
        _form_row("Oversold Level:", self.stoch_oversold, bl)

        self.stoch_overbought = QSpinBox()
        self.stoch_overbought.setRange(1, 99)
        self.stoch_overbought.setValue(80)
        _form_row("Overbought Level:", self.stoch_overbought, bl)

        return self.stoch_section

    def _build_atr_card(self):
        self.atr_section = FilterSection("ATR  (Average True Range)", initially_enabled=False)
        bl = self.atr_section.body_layout()

        self.atr_period = QSpinBox()
        self.atr_period.setRange(2, 200)
        self.atr_period.setValue(14)
        _form_row("Period:", self.atr_period, bl)

        self.atr_threshold = QDoubleSpinBox()
        self.atr_threshold.setRange(0.01, 50.0)
        self.atr_threshold.setValue(1.5)
        self.atr_threshold.setSingleStep(0.1)
        self.atr_threshold.setDecimals(2)
        _form_row("Threshold (%):", self.atr_threshold, bl)

        self.atr_condition = QComboBox()
        self.atr_condition.addItems(["high", "low"])
        self.atr_condition.setToolTip(
            "high = only enter when ATR% > threshold (volatile market)\n"
            "low  = only enter when ATR% < threshold (calm market)"
        )
        _form_row("Condition:", self.atr_condition, bl)

        return self.atr_section

    def _build_bbands_card(self):
        self.bbands_section = FilterSection("Bollinger Bands", initially_enabled=False)
        bl = self.bbands_section.body_layout()

        note = QLabel(
            "Bullish: price below lower band.  "
            "Bearish: price above upper band.  "
            "Neutral: price inside bands."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        bl.addWidget(note)

        self.bbands_period = QSpinBox()
        self.bbands_period.setRange(2, 200)
        self.bbands_period.setValue(20)
        _form_row("Period:", self.bbands_period, bl)

        self.bbands_std_dev = QDoubleSpinBox()
        self.bbands_std_dev.setRange(0.5, 5.0)
        self.bbands_std_dev.setValue(2.0)
        self.bbands_std_dev.setSingleStep(0.5)
        self.bbands_std_dev.setDecimals(1)
        _form_row("Std Deviations:", self.bbands_std_dev, bl)

        return self.bbands_section

    def _build_ma_card(self):
        self.ma_section = FilterSection("Moving Average  (SMA / EMA)", initially_enabled=False)
        bl = self.ma_section.body_layout()

        note = QLabel(
            "Bullish: price above MA.  "
            "Bearish: price below MA.  "
            "Neutral: logs MA value without blocking."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        bl.addWidget(note)

        self.ma_type = QComboBox()
        self.ma_type.addItems(["Simple (SMA)", "Exponential (EMA)"])
        _form_row("Type:", self.ma_type, bl)

        self.ma_period = QSpinBox()
        self.ma_period.setRange(2, 500)
        self.ma_period.setValue(50)
        _form_row("Period:", self.ma_period, bl)

        return self.ma_section

    def _build_adx_card(self):
        self.adx_section = FilterSection("ADX  (Average Directional Index)", initially_enabled=False)
        bl = self.adx_section.body_layout()

        self.adx_period = QSpinBox()
        self.adx_period.setRange(2, 100)
        self.adx_period.setValue(14)
        _form_row("Period:", self.adx_period, bl)

        self.adx_threshold = QSpinBox()
        self.adx_threshold.setRange(5, 60)
        self.adx_threshold.setValue(25)
        _form_row("Threshold:", self.adx_threshold, bl)

        self.adx_condition = QComboBox()
        self.adx_condition.addItems(["strong", "weak"])
        self.adx_condition.setToolTip(
            "strong = only enter when ADX > threshold (trending)\n"
            "weak   = only enter when ADX < threshold (ranging)"
        )
        _form_row("Condition:", self.adx_condition, bl)

        return self.adx_section

    def _build_vwap_card(self):
        self.vwap_section = FilterSection(
            "VWAP  (Volume Weighted Average Price)", initially_enabled=False
        )
        bl = self.vwap_section.body_layout()

        self.vwap_condition = QComboBox()
        self.vwap_condition.addItems(["above", "below"])
        self.vwap_condition.setToolTip(
            "above = only enter when price > VWAP\n"
            "below = only enter when price < VWAP"
        )
        _form_row("Price must be:", self.vwap_condition, bl)

        return self.vwap_section

    def _build_vix_card(self):
        self.vix_ind_section = FilterSection(
            "VIX Indicator  (Market Volatility Index)", initially_enabled=False
        )
        bl = self.vix_ind_section.body_layout()

        note = QLabel(
            "Adds VIX to the indicator manager. "
            "Use the VIX Filter in the Filters tab to set min/max VIX levels."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        bl.addWidget(note)

        return self.vix_ind_section

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def get_config(self):
        ma_type = 'EMA' if 'Exponential' in self.ma_type.currentText() else 'SMA'

        return {
            'RSI': {
                'enabled':    self.rsi_section.is_enabled(),
                'period':     self.rsi_period.value(),
                'oversold':   self.rsi_oversold.value(),
                'overbought': self.rsi_overbought.value(),
            },
            'MACD': {
                'enabled': self.macd_section.is_enabled(),
                'fast':    self.macd_fast.value(),
                'slow':    self.macd_slow.value(),
                'signal':  self.macd_signal.value(),
            },
            'STOCHASTIC': {
                'enabled':    self.stoch_section.is_enabled(),
                'period':     self.stoch_period.value(),
                'k_smooth':   self.stoch_k_smooth.value(),
                'oversold':   self.stoch_oversold.value(),
                'overbought': self.stoch_overbought.value(),
            },
            'ATR': {
                'enabled':   self.atr_section.is_enabled(),
                'period':    self.atr_period.value(),
                'threshold': self.atr_threshold.value(),
                'condition': self.atr_condition.currentText(),
            },
            'BBANDS': {
                'enabled': self.bbands_section.is_enabled(),
                'period':  self.bbands_period.value(),
                'std_dev': self.bbands_std_dev.value(),
            },
            'MA': {
                'enabled': self.ma_section.is_enabled(),
                'period':  self.ma_period.value(),
                'ma_type': ma_type,
            },
            'ADX': {
                'enabled':   self.adx_section.is_enabled(),
                'period':    self.adx_period.value(),
                'threshold': self.adx_threshold.value(),
                'condition': self.adx_condition.currentText(),
            },
            'VWAP': {
                'enabled':   self.vwap_section.is_enabled(),
                'condition': self.vwap_condition.currentText(),
            },
            'VIX': {
                'enabled': self.vix_ind_section.is_enabled(),
            },
        }
