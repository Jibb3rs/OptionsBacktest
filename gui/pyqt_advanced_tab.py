"""
PyQt5 Advanced Tab - Advanced Filters and Indicators
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QPushButton, QFrame,
    QScrollArea, QGroupBox, QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt

from .pyqt_theme import C
from .pyqt_main_window import create_panel, create_form_row

# Constants for consistent form layout
LABEL_WIDTH = 180
INPUT_WIDTH = 150


class AdvancedTab(QWidget):
    """Advanced filters and indicators tab"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self._create_ui()

    def _create_ui(self):
        """Create the tab UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll)

        # Content widget
        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(12, 12, 12, 12)

        # VIX Filter Section
        vix_panel, vix_layout = create_panel("VIX Filter")
        layout.addWidget(vix_panel)

        self.vix_enabled = QCheckBox("Enable VIX Filter")
        vix_layout.addWidget(self.vix_enabled)

        vix_range_layout = QHBoxLayout()
        vix_range_layout.setSpacing(12)
        vix_label = QLabel("VIX Range:")
        vix_label.setFixedWidth(LABEL_WIDTH)
        vix_range_layout.addWidget(vix_label)

        self.vix_min = QSpinBox()
        self.vix_min.setRange(0, 100)
        self.vix_min.setValue(15)
        self.vix_min.setMinimumWidth(80)
        self.vix_min.setMaximumWidth(100)
        vix_range_layout.addWidget(self.vix_min)

        vix_range_layout.addWidget(QLabel("to"))

        self.vix_max = QSpinBox()
        self.vix_max.setRange(0, 100)
        self.vix_max.setValue(50)
        self.vix_max.setMinimumWidth(80)
        self.vix_max.setMaximumWidth(100)
        vix_range_layout.addWidget(self.vix_max)

        vix_range_layout.addStretch()
        vix_layout.addLayout(vix_range_layout)

        # IV Rank Filter Section
        iv_panel, iv_layout = create_panel("IV Rank Filter")
        layout.addWidget(iv_panel)

        self.iv_enabled = QCheckBox("Enable IV Rank Filter")
        self.iv_enabled.setChecked(True)
        iv_layout.addWidget(self.iv_enabled)

        iv_note = QLabel("Credit spreads perform best when IV Rank > 30 — you're selling relatively expensive options")
        iv_note.setStyleSheet(f"color: {C['dim']}; font-size: 12px; padding: 2px 0 6px 0;")
        iv_note.setWordWrap(True)
        iv_layout.addWidget(iv_note)

        iv_range_layout = QHBoxLayout()
        iv_range_layout.setSpacing(12)
        iv_label = QLabel("IV Rank Range:")
        iv_label.setFixedWidth(LABEL_WIDTH)
        iv_range_layout.addWidget(iv_label)

        self.iv_min = QSpinBox()
        self.iv_min.setRange(0, 100)
        self.iv_min.setValue(30)
        self.iv_min.setMinimumWidth(80)
        self.iv_min.setMaximumWidth(100)
        self.iv_min.setSuffix("%")
        iv_range_layout.addWidget(self.iv_min)

        iv_range_layout.addWidget(QLabel("to"))

        self.iv_max = QSpinBox()
        self.iv_max.setRange(0, 100)
        self.iv_max.setValue(100)
        self.iv_max.setMinimumWidth(80)
        self.iv_max.setMaximumWidth(100)
        self.iv_max.setSuffix("%")
        iv_range_layout.addWidget(self.iv_max)

        iv_range_layout.addStretch()
        iv_layout.addLayout(iv_range_layout)

        # Liquidity Filter Section
        liq_panel, liq_layout = create_panel("Liquidity Filter")
        layout.addWidget(liq_panel)

        self.liquidity_enabled = QCheckBox("Enable Liquidity Filter")
        self.liquidity_enabled.setChecked(True)
        liq_layout.addWidget(self.liquidity_enabled)

        self.max_spread = QDoubleSpinBox()
        self.max_spread.setRange(0.1, 50)
        self.max_spread.setValue(10)
        self.max_spread.setSuffix("%")
        self.max_spread.setMinimumWidth(INPUT_WIDTH)
        self.max_spread.setMaximumWidth(200)
        create_form_row("Max Spread:", self.max_spread, liq_layout, LABEL_WIDTH)

        self.min_oi = QSpinBox()
        self.min_oi.setRange(0, 10000)
        self.min_oi.setValue(100)
        self.min_oi.setMinimumWidth(INPUT_WIDTH)
        self.min_oi.setMaximumWidth(200)
        create_form_row("Min Open Interest:", self.min_oi, liq_layout, LABEL_WIDTH)

        # Advanced Greeks Filter Section
        greeks_panel, greeks_layout = create_panel("Advanced Greeks Filters (Contract-Level)")
        layout.addWidget(greeks_panel)

        self.greeks_enabled = QCheckBox("Enable Advanced Greeks Filters")
        greeks_layout.addWidget(self.greeks_enabled)

        # Greeks grid
        greeks_grid = QGridLayout()
        greeks_grid.setSpacing(12)
        greeks_grid.setColumnMinimumWidth(0, 120)
        greeks_grid.setColumnMinimumWidth(1, 100)
        greeks_grid.setColumnMinimumWidth(2, 120)
        greeks_grid.setColumnMinimumWidth(3, 100)

        self.greek_filters = {}
        greek_configs = [
            ('gamma', 'Max Gamma:', 0.05),
        ]

        row = 0
        col = 0
        for key, label, default in greek_configs:
            checkbox = QCheckBox(label)
            greeks_grid.addWidget(checkbox, row, col)

            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0001, 1.0)
            spinbox.setValue(default)
            spinbox.setDecimals(4)
            spinbox.setSingleStep(0.001)
            spinbox.setMinimumWidth(100)
            spinbox.setMaximumWidth(120)
            greeks_grid.addWidget(spinbox, row, col + 1)

            self.greek_filters[key] = (checkbox, spinbox)

            col += 2
            if col >= 4:
                col = 0
                row += 1

        greeks_layout.addLayout(greeks_grid)

        # Expiration Cycle Filter
        exp_panel, exp_layout = create_panel("Expiration Cycle Filter")
        layout.addWidget(exp_panel)

        self.exp_cycle = QComboBox()
        self.exp_cycle.addItems(["Any", "Monthly Only", "Weekly Only", "Quarterly Only"])
        self.exp_cycle.setMinimumWidth(INPUT_WIDTH)
        self.exp_cycle.setMaximumWidth(200)
        create_form_row("Expiration Cycle:", self.exp_cycle, exp_layout, LABEL_WIDTH)

        # Correlation Filter
        corr_panel, corr_layout = create_panel("Correlation Filter")
        layout.addWidget(corr_panel)

        self.corr_enabled = QCheckBox("Enable Correlation Filter")
        corr_layout.addWidget(self.corr_enabled)

        self.corr_ticker = QLineEdit()
        self.corr_ticker.setPlaceholderText("e.g. SPY, QQQ, IWM")
        self.corr_ticker.setText("SPY")
        self.corr_ticker.setMinimumWidth(INPUT_WIDTH)
        self.corr_ticker.setMaximumWidth(200)
        create_form_row("Correlation Asset:", self.corr_ticker, corr_layout, LABEL_WIDTH)

        self.corr_threshold = QDoubleSpinBox()
        self.corr_threshold.setRange(-1, 1)
        self.corr_threshold.setValue(0.7)
        self.corr_threshold.setSingleStep(0.1)
        self.corr_threshold.setMinimumWidth(INPUT_WIDTH)
        self.corr_threshold.setMaximumWidth(200)
        create_form_row("Min Correlation:", self.corr_threshold, corr_layout, LABEL_WIDTH)

        # Multi-Timeframe Filter
        mtf_panel, mtf_layout = create_panel("Multi-Timeframe Confirmation")
        layout.addWidget(mtf_panel)

        self.mtf_enabled = QCheckBox("Enable Multi-Timeframe Confirmation")
        mtf_layout.addWidget(self.mtf_enabled)

        self.mtf_timeframes = QComboBox()
        self.mtf_timeframes.addItems(["Daily + Weekly", "4H + Daily", "1H + 4H + Daily"])
        self.mtf_timeframes.setMinimumWidth(INPUT_WIDTH)
        self.mtf_timeframes.setMaximumWidth(250)
        create_form_row("Timeframes:", self.mtf_timeframes, mtf_layout, LABEL_WIDTH)

        self.mtf_indicator = QComboBox()
        self.mtf_indicator.addItems(["SMA", "EMA", "RSI", "ADX"])
        self.mtf_indicator.setMinimumWidth(INPUT_WIDTH)
        self.mtf_indicator.setMaximumWidth(250)
        self.mtf_indicator.currentTextChanged.connect(self._update_mtf_conditions)
        create_form_row("Indicator:", self.mtf_indicator, mtf_layout, LABEL_WIDTH)

        self.mtf_condition = QComboBox()
        self.mtf_condition.addItems(["above", "below"])
        self.mtf_condition.setMinimumWidth(INPUT_WIDTH)
        self.mtf_condition.setMaximumWidth(250)
        create_form_row("Condition:", self.mtf_condition, mtf_layout, LABEL_WIDTH)

        self.mtf_period = QSpinBox()
        self.mtf_period.setRange(2, 500)
        self.mtf_period.setValue(50)
        self.mtf_period.setMinimumWidth(INPUT_WIDTH)
        self.mtf_period.setMaximumWidth(250)
        create_form_row("Period (shorter TF):", self.mtf_period, mtf_layout, LABEL_WIDTH)

        # Earnings Avoidance Filter
        earnings_panel, earnings_layout = create_panel("Earnings Avoidance")
        layout.addWidget(earnings_panel)

        self.earnings_enabled = QCheckBox("Skip trades near earnings announcements")
        self.earnings_enabled.setChecked(True)
        earnings_layout.addWidget(self.earnings_enabled)

        earnings_note = QLabel(
            "Earnings cause overnight gap risk that destroys credit spreads. "
            "Skipping entries within the window below protects against sudden moves."
        )
        earnings_note.setStyleSheet(f"color: {C['dim']}; font-size: 12px; padding: 2px 0 6px 0;")
        earnings_note.setWordWrap(True)
        earnings_layout.addWidget(earnings_note)

        self.earnings_skip_days = QSpinBox()
        self.earnings_skip_days.setRange(1, 30)
        self.earnings_skip_days.setValue(7)
        self.earnings_skip_days.setSuffix(" days")
        self.earnings_skip_days.setMinimumWidth(INPUT_WIDTH)
        self.earnings_skip_days.setMaximumWidth(200)
        create_form_row("Skip window (±):", self.earnings_skip_days, earnings_layout, LABEL_WIDTH)

        # Add stretch at bottom
        layout.addStretch()

    def _update_mtf_conditions(self, indicator):
        """Update condition options based on selected indicator"""
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
        """Get current configuration"""
        config = {
            # VIX
            'vix_enabled': self.vix_enabled.isChecked(),
            'vix_min': self.vix_min.value(),
            'vix_max': self.vix_max.value(),

            # IV Rank
            'iv_rank_enabled': self.iv_enabled.isChecked(),
            'iv_rank_min': self.iv_min.value(),
            'iv_rank_max': self.iv_max.value(),

            # Liquidity
            'liquidity_enabled': self.liquidity_enabled.isChecked(),
            'max_spread_pct': self.max_spread.value(),
            'min_open_interest': self.min_oi.value(),

            # Advanced Greeks
            'advanced_greeks_enabled': self.greeks_enabled.isChecked(),

            # Expiration
            'expiration_cycle': self.exp_cycle.currentText().lower().replace(' ', '_'),

            # Correlation
            'correlation_enabled': self.corr_enabled.isChecked(),
            'correlation_ticker': self.corr_ticker.text().strip().upper(),
            'correlation_threshold': self.corr_threshold.value(),

            # MTF
            'mtf_enabled': self.mtf_enabled.isChecked(),
            'mtf_timeframes': self.mtf_timeframes.currentText(),
            'mtf_indicator': self.mtf_indicator.currentText(),
            'mtf_condition': self.mtf_condition.currentText(),
            'mtf_period': self.mtf_period.value(),

            # Earnings avoidance
            'earnings_enabled': self.earnings_enabled.isChecked(),
            'earnings_skip_days': self.earnings_skip_days.value(),
        }

        # Add individual Greek filters
        for key, (checkbox, spinbox) in self.greek_filters.items():
            config[f'{key}_filter_enabled'] = checkbox.isChecked()
            config[f'max_{key}'] = spinbox.value()

        return config
