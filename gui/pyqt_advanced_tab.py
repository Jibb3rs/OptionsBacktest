"""
PyQt5 Advanced Tab - Advanced Filters and Indicators
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QDoubleSpinBox, QFrame, QScrollArea, QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt

from .pyqt_theme import C
from .pyqt_main_window import create_panel, create_form_row, create_category_divider
from .pyqt_widgets import FilterSection

LABEL_WIDTH = 180
INPUT_WIDTH = 150


class AdvancedTab(QWidget):
    """Advanced filters tab with collapsible FilterSection panels"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._create_ui()

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
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── Market Conditions ──────────────────────────────────────────────
        layout.addWidget(create_category_divider("Market Conditions"))

        # VIX Filter
        self.vix_section = FilterSection("VIX Filter", initially_enabled=False)
        bl = self.vix_section.body_layout()

        vix_range_row = QHBoxLayout()
        vix_range_row.setSpacing(12)
        lbl = QLabel("VIX Range:")
        lbl.setFixedWidth(LABEL_WIDTH)
        vix_range_row.addWidget(lbl)

        self.vix_min = QSpinBox()
        self.vix_min.setRange(0, 100)
        self.vix_min.setValue(15)
        self.vix_min.setMinimumWidth(80)
        vix_range_row.addWidget(self.vix_min)
        vix_range_row.addWidget(QLabel("to"))

        self.vix_max = QSpinBox()
        self.vix_max.setRange(0, 100)
        self.vix_max.setValue(50)
        self.vix_max.setMinimumWidth(80)
        vix_range_row.addWidget(self.vix_max)
        vix_range_row.addStretch()
        bl.addLayout(vix_range_row)

        layout.addWidget(self.vix_section)

        # IV Rank Filter
        self.iv_section = FilterSection("IV Rank Filter", initially_enabled=True)
        bl = self.iv_section.body_layout()

        iv_note = QLabel(
            "Credit spreads perform best when IV Rank > 30 — "
            "you're selling relatively expensive options"
        )
        iv_note.setStyleSheet(f"color: {C['dim']}; font-size: 12px; padding: 2px 0 6px 0;")
        iv_note.setWordWrap(True)
        bl.addWidget(iv_note)

        iv_range_row = QHBoxLayout()
        iv_range_row.setSpacing(12)
        lbl = QLabel("IV Rank Range:")
        lbl.setFixedWidth(LABEL_WIDTH)
        iv_range_row.addWidget(lbl)

        self.iv_min = QSpinBox()
        self.iv_min.setRange(0, 100)
        self.iv_min.setValue(30)
        self.iv_min.setMinimumWidth(80)
        self.iv_min.setSuffix("%")
        iv_range_row.addWidget(self.iv_min)
        iv_range_row.addWidget(QLabel("to"))

        self.iv_max = QSpinBox()
        self.iv_max.setRange(0, 100)
        self.iv_max.setValue(100)
        self.iv_max.setMinimumWidth(80)
        self.iv_max.setSuffix("%")
        iv_range_row.addWidget(self.iv_max)
        iv_range_row.addStretch()
        bl.addLayout(iv_range_row)

        layout.addWidget(self.iv_section)

        # ── Liquidity & Quality ────────────────────────────────────────────
        layout.addWidget(create_category_divider("Liquidity & Quality"))

        # Liquidity Filter
        self.liq_section = FilterSection("Liquidity Filter", initially_enabled=True)
        bl = self.liq_section.body_layout()

        self.max_spread = QDoubleSpinBox()
        self.max_spread.setRange(0.1, 50)
        self.max_spread.setValue(10)
        self.max_spread.setSuffix("%")
        self.max_spread.setMinimumWidth(INPUT_WIDTH)
        create_form_row("Max Spread:", self.max_spread, bl, LABEL_WIDTH)

        self.min_oi = QSpinBox()
        self.min_oi.setRange(0, 10000)
        self.min_oi.setValue(100)
        self.min_oi.setMinimumWidth(INPUT_WIDTH)
        create_form_row("Min Open Interest:", self.min_oi, bl, LABEL_WIDTH)

        layout.addWidget(self.liq_section)

        # Advanced Greeks Filter
        self.greeks_section = FilterSection(
            "Advanced Greeks Filters (Contract-Level)", initially_enabled=False
        )
        bl = self.greeks_section.body_layout()

        greeks_grid = QGridLayout()
        greeks_grid.setSpacing(12)
        greeks_grid.setColumnMinimumWidth(0, 130)
        greeks_grid.setColumnMinimumWidth(1, 110)
        greeks_grid.setColumnMinimumWidth(2, 130)
        greeks_grid.setColumnMinimumWidth(3, 110)

        self.greek_filters = {}
        greek_configs = [('gamma', 'Max Gamma:', 0.05)]

        row = 0
        col = 0
        for key, label, default in greek_configs:
            lbl = QLabel(label)
            greeks_grid.addWidget(lbl, row, col)

            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0001, 1.0)
            spinbox.setValue(default)
            spinbox.setDecimals(4)
            spinbox.setSingleStep(0.001)
            spinbox.setMinimumWidth(100)
            greeks_grid.addWidget(spinbox, row, col + 1)

            self.greek_filters[key] = spinbox

            col += 2
            if col >= 4:
                col = 0
                row += 1

        bl.addLayout(greeks_grid)
        layout.addWidget(self.greeks_section)

        # Expiration Cycle — plain panel, always visible (no toggle)
        exp_panel, exp_layout = create_panel("Expiration Cycle Filter")
        self.exp_cycle = QComboBox()
        self.exp_cycle.addItems(["Any", "Monthly Only", "Weekly Only", "Quarterly Only"])
        self.exp_cycle.setMinimumWidth(INPUT_WIDTH)
        self.exp_cycle.setMaximumWidth(220)
        create_form_row("Expiration Cycle:", self.exp_cycle, exp_layout, LABEL_WIDTH)
        layout.addWidget(exp_panel)

        # ── Technical ─────────────────────────────────────────────────────
        layout.addWidget(create_category_divider("Technical"))

        # Correlation Filter
        self.corr_section = FilterSection("Correlation Filter", initially_enabled=False)
        bl = self.corr_section.body_layout()

        self.corr_ticker = QLineEdit()
        self.corr_ticker.setPlaceholderText("e.g. SPY, QQQ, IWM")
        self.corr_ticker.setText("SPY")
        self.corr_ticker.setMinimumWidth(INPUT_WIDTH)
        self.corr_ticker.setMaximumWidth(200)
        create_form_row("Correlation Asset:", self.corr_ticker, bl, LABEL_WIDTH)

        self.corr_threshold = QDoubleSpinBox()
        self.corr_threshold.setRange(-1, 1)
        self.corr_threshold.setValue(0.7)
        self.corr_threshold.setSingleStep(0.1)
        self.corr_threshold.setMinimumWidth(INPUT_WIDTH)
        self.corr_threshold.setMaximumWidth(200)
        create_form_row("Min Correlation:", self.corr_threshold, bl, LABEL_WIDTH)

        layout.addWidget(self.corr_section)

        # Multi-Timeframe Filter
        self.mtf_section = FilterSection(
            "Multi-Timeframe Confirmation", initially_enabled=False
        )
        bl = self.mtf_section.body_layout()

        self.mtf_timeframes = QComboBox()
        self.mtf_timeframes.addItems(["Daily + Weekly", "4H + Daily", "1H + 4H + Daily"])
        self.mtf_timeframes.setMinimumWidth(INPUT_WIDTH)
        self.mtf_timeframes.setMaximumWidth(250)
        create_form_row("Timeframes:", self.mtf_timeframes, bl, LABEL_WIDTH)

        self.mtf_indicator = QComboBox()
        self.mtf_indicator.addItems(["SMA", "EMA", "RSI", "ADX"])
        self.mtf_indicator.setMinimumWidth(INPUT_WIDTH)
        self.mtf_indicator.setMaximumWidth(250)
        self.mtf_indicator.currentTextChanged.connect(self._update_mtf_conditions)
        create_form_row("Indicator:", self.mtf_indicator, bl, LABEL_WIDTH)

        self.mtf_condition = QComboBox()
        self.mtf_condition.addItems(["above", "below"])
        self.mtf_condition.setMinimumWidth(INPUT_WIDTH)
        self.mtf_condition.setMaximumWidth(250)
        create_form_row("Condition:", self.mtf_condition, bl, LABEL_WIDTH)

        self.mtf_period = QSpinBox()
        self.mtf_period.setRange(2, 500)
        self.mtf_period.setValue(50)
        self.mtf_period.setMinimumWidth(INPUT_WIDTH)
        self.mtf_period.setMaximumWidth(250)
        create_form_row("Period (shorter TF):", self.mtf_period, bl, LABEL_WIDTH)

        layout.addWidget(self.mtf_section)

        # Earnings Avoidance
        self.earnings_section = FilterSection("Earnings Avoidance", initially_enabled=True)
        bl = self.earnings_section.body_layout()

        earnings_note = QLabel(
            "Earnings cause overnight gap risk that destroys credit spreads. "
            "Skipping entries within the window below protects against sudden moves."
        )
        earnings_note.setStyleSheet(f"color: {C['dim']}; font-size: 12px; padding: 2px 0 6px 0;")
        earnings_note.setWordWrap(True)
        bl.addWidget(earnings_note)

        self.earnings_skip_days = QSpinBox()
        self.earnings_skip_days.setRange(1, 30)
        self.earnings_skip_days.setValue(7)
        self.earnings_skip_days.setSuffix(" days")
        self.earnings_skip_days.setMinimumWidth(INPUT_WIDTH)
        self.earnings_skip_days.setMaximumWidth(200)
        create_form_row("Skip window (\u00b1):", self.earnings_skip_days, bl, LABEL_WIDTH)

        layout.addWidget(self.earnings_section)

        layout.addStretch()

    def _update_mtf_conditions(self, indicator):
        self.mtf_condition.clear()
        if indicator in ('SMA', 'EMA'):
            self.mtf_condition.addItems(["above", "below"])
            self.mtf_period.setValue(50)
        elif indicator == 'RSI':
            self.mtf_condition.addItems(["oversold", "neutral", "overbought"])
            self.mtf_period.setValue(14)
        elif indicator == 'ADX':
            self.mtf_condition.addItems(["strong", "weak"])
            self.mtf_period.setValue(14)

    def get_config(self):
        config = {
            # VIX
            'vix_enabled':    self.vix_section.is_enabled(),
            'vix_min':        self.vix_min.value(),
            'vix_max':        self.vix_max.value(),

            # IV Rank
            'iv_rank_enabled': self.iv_section.is_enabled(),
            'iv_rank_min':     self.iv_min.value(),
            'iv_rank_max':     self.iv_max.value(),

            # Liquidity
            'liquidity_enabled':  self.liq_section.is_enabled(),
            'max_spread_pct':     self.max_spread.value(),
            'min_open_interest':  self.min_oi.value(),

            # Advanced Greeks
            'advanced_greeks_enabled': self.greeks_section.is_enabled(),

            # Expiration
            'expiration_cycle': self.exp_cycle.currentText().lower().replace(' ', '_'),

            # Correlation
            'correlation_enabled':   self.corr_section.is_enabled(),
            'correlation_ticker':    self.corr_ticker.text().strip().upper(),
            'correlation_threshold': self.corr_threshold.value(),

            # MTF
            'mtf_enabled':    self.mtf_section.is_enabled(),
            'mtf_timeframes': self.mtf_timeframes.currentText(),
            'mtf_indicator':  self.mtf_indicator.currentText(),
            'mtf_condition':  self.mtf_condition.currentText(),
            'mtf_period':     self.mtf_period.value(),

            # Earnings avoidance
            'earnings_enabled':    self.earnings_section.is_enabled(),
            'earnings_skip_days':  self.earnings_skip_days.value(),
        }

        for key, spinbox in self.greek_filters.items():
            config[f'max_{key}'] = spinbox.value()

        return config
