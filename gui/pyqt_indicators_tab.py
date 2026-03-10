"""
PyQt5 Indicators Tab - Technical Indicator Filters
Configure technical indicators that gate trade entries
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QFrame,
    QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt

from .pyqt_theme import C
from .pyqt_main_window import create_panel

LABEL_WIDTH = 180
INPUT_WIDTH = 130


def _form_row(label_text, widget, parent_layout):
    """Add a label + widget row to parent_layout"""
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
    """Technical indicator filter configuration tab"""

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

        # Auto-direction info banner
        banner = QFrame()
        acc = C['accent']
        r, g, b = int(acc[1:3], 16), int(acc[3:5], 16), int(acc[5:7], 16)
        banner.setStyleSheet(
            f"QFrame {{ background-color: rgba({r}, {g}, {b}, 0.08); "
            f"border: 1px solid rgba({r}, {g}, {b}, 0.35); "
            f"border-left: 3px solid {acc}; border-radius: 4px; }}"
        )
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(12, 10, 12, 10)
        banner_layout.setSpacing(4)

        banner_title = QLabel("Conditions are set automatically")
        banner_title.setStyleSheet(f"font-weight: bold; color: {C['accent']}; border: none; background: transparent;")
        banner_layout.addWidget(banner_title)

        banner_body = QLabel(
            "You do not need to configure indicator directions manually. "
            "Based on your selected strategy, the system will automatically apply the correct condition:\n"
            "  \u2022  Bullish strategies \u2014 oscillators wait for oversold, price must be above MA / VWAP\n"
            "  \u2022  Bearish strategies \u2014 oscillators wait for overbought, price must be below MA / VWAP\n"
            "  \u2022  Neutral strategies \u2014 oscillators require mid-range readings, price inside bands"
        )
        banner_body.setWordWrap(True)
        banner_body.setStyleSheet("color: #8b949e; border: none; background: transparent;")
        banner_layout.addWidget(banner_body)

        layout.addWidget(banner)

        # ---- Oscillators ----
        self._add_rsi(layout)
        self._add_macd(layout)
        self._add_stochastic(layout)

        # ---- Volatility ----
        self._add_atr(layout)
        self._add_bbands(layout)

        # ---- Trend / Moving Averages ----
        self._add_ma(layout)
        self._add_adx(layout)
        self._add_vwap(layout)

        # ---- Market Index ----
        self._add_vix(layout)

        layout.addStretch()

    # ------------------------------------------------------------------
    # Individual indicator builders
    # ------------------------------------------------------------------

    def _add_rsi(self, layout):
        panel, pl = create_panel("RSI  (Relative Strength Index)")
        layout.addWidget(panel)

        self.rsi_enabled = QCheckBox("Enable RSI Filter")
        pl.addWidget(self.rsi_enabled)

        note = QLabel(
            "Bullish strategies: waits for oversold. "
            "Bearish strategies: waits for overbought. "
            "Neutral: requires price within range."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        pl.addWidget(note)

        self.rsi_period = QSpinBox()
        self.rsi_period.setRange(2, 200)
        self.rsi_period.setValue(14)
        _form_row("Period:", self.rsi_period, pl)

        self.rsi_oversold = QSpinBox()
        self.rsi_oversold.setRange(1, 99)
        self.rsi_oversold.setValue(30)
        _form_row("Oversold Level:", self.rsi_oversold, pl)

        self.rsi_overbought = QSpinBox()
        self.rsi_overbought.setRange(1, 99)
        self.rsi_overbought.setValue(70)
        _form_row("Overbought Level:", self.rsi_overbought, pl)

    def _add_macd(self, layout):
        panel, pl = create_panel("MACD  (Moving Average Convergence Divergence)")
        layout.addWidget(panel)

        self.macd_enabled = QCheckBox("Enable MACD Filter")
        pl.addWidget(self.macd_enabled)

        note = QLabel(
            "Bullish strategies: requires MACD above signal. "
            "Bearish strategies: requires MACD below signal. "
            "Neutral: requires MACD close to signal line."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        pl.addWidget(note)

        self.macd_fast = QSpinBox()
        self.macd_fast.setRange(2, 100)
        self.macd_fast.setValue(12)
        _form_row("Fast Period:", self.macd_fast, pl)

        self.macd_slow = QSpinBox()
        self.macd_slow.setRange(2, 200)
        self.macd_slow.setValue(26)
        _form_row("Slow Period:", self.macd_slow, pl)

        self.macd_signal = QSpinBox()
        self.macd_signal.setRange(2, 50)
        self.macd_signal.setValue(9)
        _form_row("Signal Period:", self.macd_signal, pl)

    def _add_stochastic(self, layout):
        panel, pl = create_panel("Stochastic Oscillator")
        layout.addWidget(panel)

        self.stoch_enabled = QCheckBox("Enable Stochastic Filter")
        pl.addWidget(self.stoch_enabled)

        note = QLabel(
            "Bullish strategies: waits for oversold. "
            "Bearish strategies: waits for overbought. "
            "Neutral: requires price within range."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        pl.addWidget(note)

        self.stoch_period = QSpinBox()
        self.stoch_period.setRange(2, 100)
        self.stoch_period.setValue(14)
        _form_row("Period:", self.stoch_period, pl)

        self.stoch_k_smooth = QSpinBox()
        self.stoch_k_smooth.setRange(1, 20)
        self.stoch_k_smooth.setValue(3)
        _form_row("%K Smoothing:", self.stoch_k_smooth, pl)

        self.stoch_oversold = QSpinBox()
        self.stoch_oversold.setRange(1, 99)
        self.stoch_oversold.setValue(20)
        _form_row("Oversold Level:", self.stoch_oversold, pl)

        self.stoch_overbought = QSpinBox()
        self.stoch_overbought.setRange(1, 99)
        self.stoch_overbought.setValue(80)
        _form_row("Overbought Level:", self.stoch_overbought, pl)

    def _add_atr(self, layout):
        panel, pl = create_panel("ATR  (Average True Range)")
        layout.addWidget(panel)

        self.atr_enabled = QCheckBox("Enable ATR Filter")
        pl.addWidget(self.atr_enabled)

        self.atr_period = QSpinBox()
        self.atr_period.setRange(2, 200)
        self.atr_period.setValue(14)
        _form_row("Period:", self.atr_period, pl)

        self.atr_threshold = QDoubleSpinBox()
        self.atr_threshold.setRange(0.01, 50.0)
        self.atr_threshold.setValue(1.5)
        self.atr_threshold.setSingleStep(0.1)
        self.atr_threshold.setDecimals(2)
        _form_row("Threshold (%):", self.atr_threshold, pl)

        self.atr_condition = QComboBox()
        self.atr_condition.addItems(["high", "low"])
        self.atr_condition.setToolTip(
            "high = only enter when ATR% > threshold (volatile market)\n"
            "low  = only enter when ATR% < threshold (calm market)"
        )
        _form_row("Condition:", self.atr_condition, pl)

    def _add_bbands(self, layout):
        panel, pl = create_panel("Bollinger Bands")
        layout.addWidget(panel)

        self.bbands_enabled = QCheckBox("Enable Bollinger Bands Filter")
        pl.addWidget(self.bbands_enabled)

        note = QLabel(
            "Bullish strategies: price below lower band. "
            "Bearish strategies: price above upper band. "
            "Neutral: price inside bands."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        pl.addWidget(note)

        self.bbands_period = QSpinBox()
        self.bbands_period.setRange(2, 200)
        self.bbands_period.setValue(20)
        _form_row("Period:", self.bbands_period, pl)

        self.bbands_std_dev = QDoubleSpinBox()
        self.bbands_std_dev.setRange(0.5, 5.0)
        self.bbands_std_dev.setValue(2.0)
        self.bbands_std_dev.setSingleStep(0.5)
        self.bbands_std_dev.setDecimals(1)
        _form_row("Std Deviations:", self.bbands_std_dev, pl)

    def _add_ma(self, layout):
        panel, pl = create_panel("Moving Average  (SMA / EMA)")
        layout.addWidget(panel)

        self.ma_enabled = QCheckBox("Enable Moving Average Filter")
        pl.addWidget(self.ma_enabled)

        note = QLabel(
            "Bullish strategies: price above MA. "
            "Bearish strategies: price below MA. "
            "Neutral: logs MA value without blocking."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        pl.addWidget(note)

        self.ma_type = QComboBox()
        self.ma_type.addItems(["Simple (SMA)", "Exponential (EMA)"])
        _form_row("Type:", self.ma_type, pl)

        self.ma_period = QSpinBox()
        self.ma_period.setRange(2, 500)
        self.ma_period.setValue(50)
        _form_row("Period:", self.ma_period, pl)

    def _add_adx(self, layout):
        panel, pl = create_panel("ADX  (Average Directional Index)")
        layout.addWidget(panel)

        self.adx_enabled = QCheckBox("Enable ADX Filter")
        pl.addWidget(self.adx_enabled)

        self.adx_period = QSpinBox()
        self.adx_period.setRange(2, 100)
        self.adx_period.setValue(14)
        _form_row("Period:", self.adx_period, pl)

        self.adx_threshold = QSpinBox()
        self.adx_threshold.setRange(5, 60)
        self.adx_threshold.setValue(25)
        _form_row("Threshold:", self.adx_threshold, pl)

        self.adx_condition = QComboBox()
        self.adx_condition.addItems(["strong", "weak"])
        self.adx_condition.setToolTip(
            "strong = only enter when ADX > threshold (trending)\n"
            "weak   = only enter when ADX < threshold (ranging)"
        )
        _form_row("Condition:", self.adx_condition, pl)

    def _add_vwap(self, layout):
        panel, pl = create_panel("VWAP  (Volume Weighted Average Price)")
        layout.addWidget(panel)

        self.vwap_enabled = QCheckBox("Enable VWAP Filter")
        pl.addWidget(self.vwap_enabled)

        self.vwap_condition = QComboBox()
        self.vwap_condition.addItems(["above", "below"])
        self.vwap_condition.setToolTip(
            "above = only enter when price > VWAP\n"
            "below = only enter when price < VWAP"
        )
        _form_row("Price must be:", self.vwap_condition, pl)

    def _add_vix(self, layout):
        panel, pl = create_panel("VIX Indicator  (Market Volatility Index)")
        layout.addWidget(panel)

        self.vix_ind_enabled = QCheckBox("Enable VIX Indicator")
        pl.addWidget(self.vix_ind_enabled)

        note = QLabel(
            "Adds VIX to the indicator manager. "
            "Use the VIX Filter in Advanced Filters to set min/max VIX levels."
        )
        note.setObjectName("dim")
        note.setWordWrap(True)
        pl.addWidget(note)

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def get_config(self):
        """Return indicators config dict matching generate_indicator_manager() format"""
        # Determine MA type from combobox selection
        ma_type_text = self.ma_type.currentText()
        ma_type = 'EMA' if 'Exponential' in ma_type_text else 'SMA'

        return {
            'RSI': {
                'enabled': self.rsi_enabled.isChecked(),
                'period': self.rsi_period.value(),
                'oversold': self.rsi_oversold.value(),
                'overbought': self.rsi_overbought.value(),
            },
            'MACD': {
                'enabled': self.macd_enabled.isChecked(),
                'fast': self.macd_fast.value(),
                'slow': self.macd_slow.value(),
                'signal': self.macd_signal.value(),
            },
            'STOCHASTIC': {
                'enabled': self.stoch_enabled.isChecked(),
                'period': self.stoch_period.value(),
                'k_smooth': self.stoch_k_smooth.value(),
                'oversold': self.stoch_oversold.value(),
                'overbought': self.stoch_overbought.value(),
            },
            'ATR': {
                'enabled': self.atr_enabled.isChecked(),
                'period': self.atr_period.value(),
                'threshold': self.atr_threshold.value(),
                'condition': self.atr_condition.currentText(),
            },
            'BBANDS': {
                'enabled': self.bbands_enabled.isChecked(),
                'period': self.bbands_period.value(),
                'std_dev': self.bbands_std_dev.value(),
            },
            'MA': {
                'enabled': self.ma_enabled.isChecked(),
                'period': self.ma_period.value(),
                'ma_type': ma_type,
            },
            'ADX': {
                'enabled': self.adx_enabled.isChecked(),
                'period': self.adx_period.value(),
                'threshold': self.adx_threshold.value(),
                'condition': self.adx_condition.currentText(),
            },
            'VWAP': {
                'enabled': self.vwap_enabled.isChecked(),
                'condition': self.vwap_condition.currentText(),
            },
            'VIX': {
                'enabled': self.vix_ind_enabled.isChecked(),
            },
        }
