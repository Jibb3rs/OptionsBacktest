"""
PyQt5 Config Tab - Strategy Configuration
"""

import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QFrame,
    QScrollArea, QGroupBox, QGridLayout, QMessageBox, QDateEdit,
    QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate

from .pyqt_theme import C
from .pyqt_main_window import create_panel, create_form_row, create_section_header

# Constants for consistent form layout
LABEL_WIDTH = 180
INPUT_WIDTH = 150


class ConfigTab(QWidget):
    """Strategy configuration tab"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Load strategies
        self._load_strategies()

        # Create UI
        self._create_ui()

    def _load_strategies(self):
        """Load strategy definitions from JSON"""
        from core.paths import resource_path
        try:
            with open(resource_path('config/strategies.json'), 'r') as f:
                self.strategies = json.load(f)
        except:
            self.strategies = {}

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
        layout.setContentsMargins(8, 8, 8, 8)

        # Strategy Selection Section
        strategy_panel, strategy_layout = create_panel("Strategy Selection")
        layout.addWidget(strategy_panel)

        # Strategy dropdown
        self.strategy_combo = QComboBox()
        self.strategy_combo.setMinimumWidth(280)
        for s in self.strategies.values():
            spread_type = s.get('spread_type', '')
            if spread_type == 'credit':
                label = f"{s['name']}  (Credit)"
            elif spread_type == 'debit':
                label = f"{s['name']}  (Debit)"
            else:
                label = s['name']
            self.strategy_combo.addItem(label)
        self.strategy_combo.currentIndexChanged.connect(self._on_strategy_changed)
        create_form_row("Strategy:", self.strategy_combo, strategy_layout, LABEL_WIDTH)

        # Strategy description
        self.strategy_desc = QLabel()
        self.strategy_desc.setWordWrap(True)
        self.strategy_desc.setStyleSheet(f"color: {C['dim']}; padding: 8px;")
        strategy_layout.addWidget(self.strategy_desc)

        # Custom Strategy Builder Container (shown only for custom strategy)
        self.custom_container = QFrame()
        self.custom_container.setObjectName("panel")
        self.custom_container.setVisible(False)
        custom_layout = QVBoxLayout(self.custom_container)
        custom_layout.setContentsMargins(14, 12, 14, 12)

        custom_header = QLabel("Custom Strategy Builder")
        custom_header.setObjectName("header")
        custom_layout.addWidget(custom_header)

        # Number of legs
        self.custom_legs_count = QSpinBox()
        self.custom_legs_count.setRange(1, 10)
        self.custom_legs_count.setValue(2)
        self.custom_legs_count.setMinimumWidth(INPUT_WIDTH)
        self.custom_legs_count.setMaximumWidth(200)
        self.custom_legs_count.valueChanged.connect(self._update_custom_legs)
        create_form_row("Number of Legs:", self.custom_legs_count, custom_layout, LABEL_WIDTH)

        # Legs container
        self.custom_legs_widget = QWidget()
        self.custom_legs_layout = QVBoxLayout(self.custom_legs_widget)
        self.custom_legs_layout.setContentsMargins(0, 10, 0, 0)
        self.custom_legs_layout.setSpacing(8)
        custom_layout.addWidget(self.custom_legs_widget)

        # DTE Type for custom strategy
        self.custom_dte_type = QComboBox()
        self.custom_dte_type.addItems(["Standard DTE", "Weekly", "Monthly", "Quarterly", "End of Month"])
        self.custom_dte_type.setMinimumWidth(INPUT_WIDTH)
        self.custom_dte_type.setMaximumWidth(250)
        create_form_row("Expiration Type:", self.custom_dte_type, custom_layout, LABEL_WIDTH)

        # Initialize custom legs
        self.custom_legs = []
        self._update_custom_legs()

        layout.addWidget(self.custom_container)

        # Ticker and Dates Section
        basic_panel, basic_layout = create_panel("Basic Configuration")
        layout.addWidget(basic_panel)

        # Ticker
        self.ticker_input = QLineEdit("SPY")
        self.ticker_input.setMinimumWidth(INPUT_WIDTH)
        self.ticker_input.setMaximumWidth(200)
        create_form_row("Ticker:", self.ticker_input, basic_layout, LABEL_WIDTH)

        # Date range
        date_row = QHBoxLayout()
        date_row.setSpacing(12)

        date_label = QLabel("Date Range:")
        date_label.setFixedWidth(LABEL_WIDTH)
        date_row.addWidget(date_label)

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setMinimumWidth(INPUT_WIDTH)
        self.start_date.setMaximumWidth(200)
        date_row.addWidget(self.start_date)

        date_row.addWidget(QLabel("to"))

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setMinimumWidth(INPUT_WIDTH)
        self.end_date.setMaximumWidth(200)
        date_row.addWidget(self.end_date)

        date_row.addStretch()
        basic_layout.addLayout(date_row)

        # Initial capital
        self.capital_input = QSpinBox()
        self.capital_input.setRange(1000, 10000000)
        self.capital_input.setValue(100000)
        self.capital_input.setSingleStep(10000)
        self.capital_input.setPrefix("$")
        self.capital_input.setMinimumWidth(INPUT_WIDTH)
        self.capital_input.setMaximumWidth(200)
        create_form_row("Initial Capital:", self.capital_input, basic_layout, LABEL_WIDTH)

        # Expiry Settings Section
        expiry_panel, expiry_layout = create_panel("Expiration Settings")
        layout.addWidget(expiry_panel)

        # Days to expiry
        self.expiry_days = QSpinBox()
        self.expiry_days.setRange(1, 365)
        self.expiry_days.setValue(30)
        self.expiry_days.setMinimumWidth(INPUT_WIDTH)
        self.expiry_days.setMaximumWidth(200)
        self.expiry_days.setSuffix(" days")
        create_form_row("Days to Expiry:", self.expiry_days, expiry_layout, LABEL_WIDTH)

        # Expiry range
        self.expiry_range = QSpinBox()
        self.expiry_range.setRange(0, 30)
        self.expiry_range.setValue(5)
        self.expiry_range.setMinimumWidth(INPUT_WIDTH)
        self.expiry_range.setMaximumWidth(200)
        self.expiry_range.setSuffix(" days")
        create_form_row("Expiry Range (±):", self.expiry_range, expiry_layout, LABEL_WIDTH)

        # Close DTE — close position X days before expiry to avoid gamma blowup
        self.close_dte = QSpinBox()
        self.close_dte.setRange(0, 60)
        self.close_dte.setValue(21)
        self.close_dte.setMinimumWidth(INPUT_WIDTH)
        self.close_dte.setMaximumWidth(200)
        self.close_dte.setSuffix(" days before expiry")
        create_form_row("Close Position At:", self.close_dte, expiry_layout, LABEL_WIDTH)

        close_dte_note = QLabel("Pro tip: 21 DTE exits avoid gamma blowup and lock in most of the theta decay")
        close_dte_note.setStyleSheet(f"color: {C['dim']}; font-size: 12px; padding-left: 8px;")
        close_dte_note.setWordWrap(True)
        expiry_layout.addWidget(close_dte_note)

        # Strike Selection Section
        strike_panel, strike_layout = create_panel("Strike Selection")
        layout.addWidget(strike_panel)

        # Strike method
        self.strike_method = QComboBox()
        self.strike_method.addItems(["Delta-Based", "Fixed Points", "Percentage", "ATR-Based"])
        self.strike_method.setMinimumWidth(INPUT_WIDTH)
        self.strike_method.setMaximumWidth(200)
        self.strike_method.currentIndexChanged.connect(self._on_strike_method_changed)
        create_form_row("Selection Method:", self.strike_method, strike_layout, LABEL_WIDTH)

        # Delta inputs container
        self.delta_container = QWidget()
        self.delta_layout = QGridLayout(self.delta_container)
        self.delta_layout.setContentsMargins(0, 10, 0, 0)
        self.delta_layout.setHorizontalSpacing(20)
        self.delta_layout.setVerticalSpacing(10)
        strike_layout.addWidget(self.delta_container)

        # Trading Rules Section
        rules_panel, rules_layout = create_panel("Trading Rules")
        layout.addWidget(rules_panel)

        # Max positions
        self.max_positions = QSpinBox()
        self.max_positions.setRange(1, 100)
        self.max_positions.setValue(5)
        self.max_positions.setMinimumWidth(INPUT_WIDTH)
        self.max_positions.setMaximumWidth(200)
        create_form_row("Max Positions:", self.max_positions, rules_layout, LABEL_WIDTH)

        # Min days between trades
        self.min_days = QSpinBox()
        self.min_days.setRange(0, 30)
        self.min_days.setValue(0)
        self.min_days.setMinimumWidth(INPUT_WIDTH)
        self.min_days.setMaximumWidth(200)
        self.min_days.setSuffix(" days")
        create_form_row("Min Days Between:", self.min_days, rules_layout, LABEL_WIDTH)

        # Profit target
        self.profit_target = QSpinBox()
        self.profit_target.setRange(1, 500)
        self.profit_target.setValue(50)
        self.profit_target.setSuffix("%")
        self.profit_target.setMinimumWidth(INPUT_WIDTH)
        self.profit_target.setMaximumWidth(200)
        create_form_row("Profit Target:", self.profit_target, rules_layout, LABEL_WIDTH)

        # Stop loss
        self.stop_loss = QSpinBox()
        self.stop_loss.setRange(1, 1000)
        self.stop_loss.setValue(200)
        self.stop_loss.setSuffix("%")
        self.stop_loss.setMinimumWidth(INPUT_WIDTH)
        self.stop_loss.setMaximumWidth(200)
        create_form_row("Stop Loss:", self.stop_loss, rules_layout, LABEL_WIDTH)

        # Stop loss mode
        self.stop_loss_mode = QComboBox()
        self.stop_loss_mode.addItems([
            "Credit-Based (Options Standard)",
            "Max Loss-Based (Conservative)",
            "Equal Dollar (Balanced)",
            "Price Distance (FX Style)"
        ])
        self.stop_loss_mode.setMinimumWidth(250)
        self.stop_loss_mode.setMaximumWidth(350)
        create_form_row("Stop Loss Mode:", self.stop_loss_mode, rules_layout, LABEL_WIDTH)

        # Min R/R ratio enforcement
        self.min_rr_ratio = QDoubleSpinBox()
        self.min_rr_ratio.setRange(0.0, 10.0)
        self.min_rr_ratio.setValue(0.0)
        self.min_rr_ratio.setDecimals(1)
        self.min_rr_ratio.setSingleStep(0.1)
        self.min_rr_ratio.setMinimumWidth(INPUT_WIDTH)
        self.min_rr_ratio.setMaximumWidth(200)
        self.min_rr_ratio.setToolTip("Skip trades where reward/risk is below this ratio. 0 = disabled.")
        create_form_row("Min R/R Ratio:", self.min_rr_ratio, rules_layout, LABEL_WIDTH)

        min_rr_note = QLabel("Set > 0 to skip low-quality setups (e.g. 0.3 skips trades paying < $0.30 per $1.00 risk)")
        min_rr_note.setStyleSheet(f"color: {C['dim']}; font-size: 12px; padding-left: 8px;")
        min_rr_note.setWordWrap(True)
        rules_layout.addWidget(min_rr_note)

        # Position Sizing
        self.sizing_mode = QComboBox()
        self.sizing_mode.addItems([
            "Fixed Contracts",
            "% of Capital (Risk-Based)"
        ])
        self.sizing_mode.setMinimumWidth(250)
        self.sizing_mode.setMaximumWidth(350)
        self.sizing_mode.currentIndexChanged.connect(self._on_sizing_mode_changed)
        create_form_row("Position Sizing:", self.sizing_mode, rules_layout, LABEL_WIDTH)

        self.sizing_contracts = QSpinBox()
        self.sizing_contracts.setRange(1, 100)
        self.sizing_contracts.setValue(1)
        self.sizing_contracts.setSuffix(" contracts")
        self.sizing_contracts.setMinimumWidth(INPUT_WIDTH)
        self.sizing_contracts.setMaximumWidth(200)
        create_form_row("Contracts:", self.sizing_contracts, rules_layout, LABEL_WIDTH)

        self.sizing_risk_pct = QDoubleSpinBox()
        self.sizing_risk_pct.setRange(0.1, 100.0)
        self.sizing_risk_pct.setValue(2.0)
        self.sizing_risk_pct.setSuffix("% of capital")
        self.sizing_risk_pct.setDecimals(1)
        self.sizing_risk_pct.setMinimumWidth(INPUT_WIDTH)
        self.sizing_risk_pct.setMaximumWidth(200)
        self.sizing_risk_pct.setVisible(False)
        create_form_row("Risk Per Trade:", self.sizing_risk_pct, rules_layout, LABEL_WIDTH)

        self.sizing_max_contracts = QSpinBox()
        self.sizing_max_contracts.setRange(1, 100)
        self.sizing_max_contracts.setValue(10)
        self.sizing_max_contracts.setSuffix(" max")
        self.sizing_max_contracts.setMinimumWidth(INPUT_WIDTH)
        self.sizing_max_contracts.setMaximumWidth(200)
        self.sizing_max_contracts.setVisible(False)
        create_form_row("Max Contracts Cap:", self.sizing_max_contracts, rules_layout, LABEL_WIDTH)

        # Generate Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.generate_btn = QPushButton("Generate QuantConnect Code")
        self.generate_btn.setObjectName("primary")
        self.generate_btn.setMinimumWidth(250)
        self.generate_btn.setMinimumHeight(45)
        self.generate_btn.clicked.connect(self._generate_code)
        button_layout.addWidget(self.generate_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # R/R Estimate Panel (shown after Generate is clicked)
        self.rr_panel = QFrame()
        self.rr_panel.setObjectName("panel")
        self.rr_panel.setVisible(False)
        rr_outer = QVBoxLayout(self.rr_panel)
        rr_outer.setContentsMargins(16, 14, 16, 14)
        rr_outer.setSpacing(10)

        self.rr_header_label = QLabel("Estimated R/R per Trade")
        self.rr_header_label.setObjectName("header")
        rr_outer.addWidget(self.rr_header_label)

        self.rr_type_label = QLabel()
        self.rr_type_label.setStyleSheet(f"color: {C['dim']}; font-size: 12px;")
        rr_outer.addWidget(self.rr_type_label)

        # 2×2 metric card grid
        def make_metric_card(title, color=None):
            card = QFrame()
            card.setStyleSheet(
                f"QFrame {{ background-color: {C['alt_bg']}; border: 1px solid {C['card_border']}; "
                f"border-radius: 6px; }}"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 10, 14, 10)
            card_layout.setSpacing(4)
            val_lbl = QLabel("—")
            style = "font-size: 18px; font-weight: bold;"
            if color:
                style += f" color: {color};"
            val_lbl.setStyleSheet(style)
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"color: {C['dim']}; font-size: 12px;")
            card_layout.addWidget(val_lbl)
            card_layout.addWidget(title_lbl)
            return card, val_lbl

        win_card, self.rr_win_label = make_metric_card("Max Win", C['up'])
        loss_card, self.rr_loss_label = make_metric_card("Max Stop", C['down'])
        ratio_card, self.rr_ratio_label = make_metric_card("R/R Ratio", C['accent'])
        be_card, self.rr_breakeven_label = make_metric_card("Min Win Rate")

        rr_row1 = QHBoxLayout()
        rr_row1.setSpacing(12)
        rr_row1.addWidget(win_card, 1)
        rr_row1.addWidget(loss_card, 1)

        rr_row2 = QHBoxLayout()
        rr_row2.setSpacing(12)
        rr_row2.addWidget(ratio_card, 1)
        rr_row2.addWidget(be_card, 1)

        rr_outer.addLayout(rr_row1)
        rr_outer.addLayout(rr_row2)

        self.rr_note_label = QLabel()
        self.rr_note_label.setStyleSheet(f"color: {C['dim']}; font-size: 12px;")
        self.rr_note_label.setWordWrap(True)
        rr_outer.addWidget(self.rr_note_label)

        layout.addWidget(self.rr_panel)

        # Add stretch at bottom
        layout.addStretch()

        # Initialize
        self._on_strategy_changed()
        self._on_strike_method_changed()

    def _on_sizing_mode_changed(self):
        """Show/hide sizing controls based on mode"""
        is_pct = self.sizing_mode.currentIndex() == 1
        self.sizing_contracts.setVisible(not is_pct)
        self.sizing_risk_pct.setVisible(is_pct)
        self.sizing_max_contracts.setVisible(is_pct)

    def _on_strategy_changed(self):
        """Handle strategy selection change"""
        strategy_keys = list(self.strategies.keys())
        idx = self.strategy_combo.currentIndex()
        if 0 <= idx < len(strategy_keys):
            key = strategy_keys[idx]
            strategy = self.strategies[key]
            self.strategy_desc.setText(strategy.get('description', ''))

            # Auto-set stop loss mode based on spread type
            spread_type = strategy.get('spread_type', '')
            if spread_type == 'debit':
                self.stop_loss_mode.setCurrentIndex(1)  # Max Loss-Based (Conservative)
            elif spread_type == 'credit':
                self.stop_loss_mode.setCurrentIndex(0)  # Credit-Based (Options Standard)

            # Show/hide custom strategy builder
            is_custom = strategy.get('custom', False)
            self.custom_container.setVisible(is_custom)
            self.delta_container.setVisible(not is_custom)

            if not is_custom:
                self._update_delta_inputs(key)

    def _update_custom_legs(self):
        """Update custom leg inputs based on count"""
        # Clear existing legs
        for leg_widget in self.custom_legs:
            leg_widget.setParent(None)
            leg_widget.deleteLater()
        self.custom_legs = []

        num_legs = self.custom_legs_count.value()

        for i in range(num_legs):
            leg_frame = QFrame()
            leg_frame.setStyleSheet(f"background-color: {C['bg']}; border-radius: 4px; padding: 8px;")
            leg_layout = QHBoxLayout(leg_frame)
            leg_layout.setContentsMargins(10, 8, 10, 8)
            leg_layout.setSpacing(15)

            # Leg label
            leg_label = QLabel(f"Leg {i+1}:")
            leg_label.setFixedWidth(50)
            leg_label.setStyleSheet(f"color: {C['accent']}; font-weight: bold;")
            leg_layout.addWidget(leg_label)

            # Type (Call/Put/Stock)
            type_label = QLabel("Type:")
            leg_layout.addWidget(type_label)
            type_combo = QComboBox()
            type_combo.addItems(["Call", "Put", "Stock"])
            type_combo.setMinimumWidth(80)
            type_combo.setMaximumWidth(100)
            leg_layout.addWidget(type_combo)

            # Direction (Long/Short)
            dir_label = QLabel("Direction:")
            leg_layout.addWidget(dir_label)
            dir_combo = QComboBox()
            dir_combo.addItems(["Long", "Short"])
            dir_combo.setMinimumWidth(80)
            dir_combo.setMaximumWidth(100)
            leg_layout.addWidget(dir_combo)

            # Delta
            delta_label = QLabel("Delta:")
            leg_layout.addWidget(delta_label)
            delta_spin = QDoubleSpinBox()
            delta_spin.setRange(0.01, 0.99)
            delta_spin.setValue(0.30)
            delta_spin.setSingleStep(0.05)
            delta_spin.setDecimals(2)
            delta_spin.setMinimumWidth(80)
            delta_spin.setMaximumWidth(100)
            leg_layout.addWidget(delta_spin)

            # Quantity
            qty_label = QLabel("Qty:")
            leg_layout.addWidget(qty_label)
            qty_spin = QSpinBox()
            qty_spin.setRange(1, 100)
            qty_spin.setValue(1)
            qty_spin.setMinimumWidth(60)
            qty_spin.setMaximumWidth(80)
            leg_layout.addWidget(qty_spin)

            leg_layout.addStretch()

            # Store references
            leg_frame.type_combo = type_combo
            leg_frame.dir_combo = dir_combo
            leg_frame.delta_spin = delta_spin
            leg_frame.qty_spin = qty_spin

            self.custom_legs_layout.addWidget(leg_frame)
            self.custom_legs.append(leg_frame)

    def _on_strike_method_changed(self):
        """Handle strike method change"""
        # Update delta input labels based on method
        pass

    def _update_delta_inputs(self, strategy_key):
        """Update delta inputs based on selected strategy"""
        # Clear existing inputs
        while self.delta_layout.count():
            item = self.delta_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.delta_inputs = {}

        # Get strategy info
        strategy = self.strategies.get(strategy_key, {})
        is_custom = strategy.get('custom', False)

        if is_custom:
            return

        # Create delta inputs based on strategy type
        delta_configs = self._get_delta_config(strategy_key)

        row = 0
        col = 0
        for name, default in delta_configs.items():
            label = QLabel(f"{name}:")
            label.setFixedWidth(LABEL_WIDTH)
            self.delta_layout.addWidget(label, row, col)

            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.01, 0.99)
            spinbox.setValue(default)
            spinbox.setSingleStep(0.01)
            spinbox.setDecimals(2)
            spinbox.setMinimumWidth(INPUT_WIDTH)
            spinbox.setMaximumWidth(200)
            self.delta_layout.addWidget(spinbox, row, col + 1)

            self.delta_inputs[name] = spinbox

            # Two columns of delta inputs
            col += 2
            if col >= 4:
                col = 0
                row += 1

    def _get_delta_config(self, strategy_key):
        """Get delta configuration for a strategy"""
        configs = {
            'iron_condor': {
                'Short Put Delta': 0.16,
                'Long Put Delta': 0.08,
                'Short Call Delta': 0.16,
                'Long Call Delta': 0.08
            },
            'iron_butterfly': {
                'ATM Delta': 0.50,
                'Wing Width Delta': 0.16
            },
            'short_strangle': {
                'Short Put Delta': 0.16,
                'Short Call Delta': 0.16
            },
            'short_straddle': {
                'ATM Delta': 0.50
            },
            'long_strangle': {
                'Long Put Delta': 0.30,
                'Long Call Delta': 0.30
            },
            'long_straddle': {
                'Long Put Delta': 0.50,
                'Long Call Delta': 0.50
            },
            'bull_put_spread': {
                'Short Put Delta': 0.30,
                'Long Put Delta': 0.16
            },
            'bear_call_spread': {
                'Short Call Delta': 0.30,
                'Long Call Delta': 0.16
            },
            'bull_call_spread': {
                'Long Call Delta': 0.70,
                'Short Call Delta': 0.30
            },
            'bear_put_spread': {
                'Long Put Delta': 0.70,
                'Short Put Delta': 0.30
            },
            'long_call': {
                'Long Call Delta': 0.50
            },
            'long_put': {
                'Long Put Delta': 0.50
            },
            'butterfly_spread': {
                'Center Delta': 0.50,
                'Wing Width': 0.20
            },
            'calendar_spread': {
                'Strike Delta': 0.50
            },
            'diagonal_spread': {
                'Short Delta': 0.30,
                'Long Delta': 0.50
            },
            'ratio_spread': {
                'Long Delta': 0.50,
                'Short Delta': 0.30
            },
            'jade_lizard': {
                'Short Put Delta': 0.20,
                'Short Call Delta': 0.30,
                'Long Call Delta': 0.20
            },
            'covered_call': {
                'Short Call Delta': 0.30
            },
            'protective_put': {
                'Long Put Delta': 0.30
            },
            'collar': {
                'Long Put Delta': 0.30,
                'Short Call Delta': 0.30
            }
        }
        return configs.get(strategy_key, {'Delta': 0.30})

    def _generate_code(self):
        """Generate QuantConnect code"""
        try:
            config = self.main_window.get_config()

            # Get strategy class
            strategy_keys = list(self.strategies.keys())
            idx = self.strategy_combo.currentIndex()
            strategy_key = strategy_keys[idx]

            # Import the strategy
            from strategies import (
                IronCondor, IronButterfly, ShortStrangle, ShortStraddle,
                BullPutSpread, BearCallSpread, BullCallSpread, BearPutSpread,
                LongStrangle, LongCall, LongPut, LongStraddle, ButterflySpread,
                CalendarSpread, DiagonalSpread, RatioSpread, JadeLizard,
                CoveredCall, ProtectivePut, Collar, CustomStrategy
            )

            strategy_map = {
                'iron_condor': IronCondor,
                'iron_butterfly': IronButterfly,
                'short_strangle': ShortStrangle,
                'short_straddle': ShortStraddle,
                'bull_put_spread': BullPutSpread,
                'bear_call_spread': BearCallSpread,
                'bull_call_spread': BullCallSpread,
                'bear_put_spread': BearPutSpread,
                'long_strangle': LongStrangle,
                'long_call': LongCall,
                'long_put': LongPut,
                'long_straddle': LongStraddle,
                'butterfly_spread': ButterflySpread,
                'calendar_spread': CalendarSpread,
                'diagonal_spread': DiagonalSpread,
                'ratio_spread': RatioSpread,
                'jade_lizard': JadeLizard,
                'covered_call': CoveredCall,
                'protective_put': ProtectivePut,
                'collar': Collar,
                'custom_strategy': CustomStrategy
            }

            strategy_class = strategy_map.get(strategy_key)
            if not strategy_class:
                QMessageBox.warning(self, "Error", f"Strategy '{strategy_key}' not implemented")
                return

            # Generate code
            code = strategy_class.generate_code(config)

            # Show R/R estimate
            self._update_rr_estimate(strategy_key)

            # Show code popup
            from .pyqt_code_popup import CodePopup
            popup = CodePopup(code, self)
            popup.exec_()

            self.main_window.update_status("Code generated successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate code: {str(e)}")

    def _update_rr_estimate(self, strategy_key):
        """Calculate and display R/R estimate after code generation"""
        strategy = self.strategies.get(strategy_key, {})
        spread_type = strategy.get('spread_type', '')
        pt = self.profit_target.value()   # profit target %
        sl = self.stop_loss.value()       # stop loss %
        mode = self.stop_loss_mode.currentText()

        if 'Credit' in mode:
            # Both PT and SL are percentages of the credit received
            ratio = sl / pt
            breakeven = sl / (pt + sl) * 100
            self.rr_win_label.setText(f"+{pt}% of credit")
            self.rr_loss_label.setText(f"\u2212{sl}% of credit")
            self.rr_ratio_label.setText(f"1 : {ratio:.1f}")
            self.rr_breakeven_label.setText(f"{breakeven:.0f}%")
            self.rr_type_label.setText(
                f"Credit Spread \u2014 close at {pt}% profit, stop when loss = {sl}% of premium collected"
            )
            self.rr_note_label.setText(
                f"Example: collect $1.00 credit \u2192 target exit at +${pt/100:.2f} | stop at \u2212${sl/100:.2f} per contract"
            )

        elif 'Max Loss' in mode:
            # PT is % of max profit; SL is % of max loss (= debit paid for debit spreads)
            # Rough assumption: max_profit \u2248 50% of max_loss (varies by spread width & pricing)
            approx_gain_factor = 0.5
            approx_ratio = sl / (pt * approx_gain_factor)
            breakeven = sl / (pt * approx_gain_factor + sl) * 100
            self.rr_win_label.setText(f"+{pt}% of max gain")
            self.rr_loss_label.setText(f"\u2212{sl}% of debit")
            self.rr_ratio_label.setText(f"~1 : {approx_ratio:.1f}")
            self.rr_breakeven_label.setText(f"~{breakeven:.0f}%")
            self.rr_type_label.setText(
                f"Debit Spread \u2014 target {pt}% of max profit, stop at {sl}% of debit paid"
            )
            self.rr_note_label.setText(
                "Ratio is approximate \u2014 exact amounts depend on spread width & entry pricing in QuantConnect."
            )

        else:
            ratio = sl / pt if pt > 0 else 0
            breakeven = sl / (pt + sl) * 100 if (pt + sl) > 0 else 0
            self.rr_win_label.setText(f"+{pt}%")
            self.rr_loss_label.setText(f"\u2212{sl}%")
            self.rr_ratio_label.setText(f"~1 : {ratio:.1f}")
            self.rr_breakeven_label.setText(f"{breakeven:.0f}%")
            self.rr_type_label.setText(f"Mode: {mode}")
            self.rr_note_label.setText("")

        self.rr_panel.setVisible(True)

    def get_config(self):
        """Get current configuration"""
        strategy_keys = list(self.strategies.keys())
        idx = self.strategy_combo.currentIndex()
        strategy_key = strategy_keys[idx] if 0 <= idx < len(strategy_keys) else 'iron_condor'

        # Collect delta values
        deltas = {}
        for name, spinbox in getattr(self, 'delta_inputs', {}).items():
            deltas[name] = spinbox.value()

        config = {
            'strategy': strategy_key,
            'ticker': self.ticker_input.text().upper(),
            'start_date': self.start_date.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date.date().toString("yyyy-MM-dd"),
            'initial_capital': self.capital_input.value(),
            'expiry_days': self.expiry_days.value(),
            'expiry_range': self.expiry_range.value(),
            'close_dte': self.close_dte.value(),
            'strike_selection': {
                'method': self.strike_method.currentText(),
                'deltas': deltas
            },
            'trading_rules': {
                'max_positions': self.max_positions.value(),
                'min_days_between_trades': self.min_days.value(),
                'profit_target_pct': self.profit_target.value(),
                'stop_loss_pct': self.stop_loss.value(),
                'stop_loss_mode': self.stop_loss_mode.currentText(),
                'min_rr_ratio': self.min_rr_ratio.value(),
                'sizing_mode': 'pct_capital' if self.sizing_mode.currentIndex() == 1 else 'fixed',
                'sizing_contracts': self.sizing_contracts.value(),
                'sizing_risk_pct': self.sizing_risk_pct.value(),
                'sizing_max_contracts': self.sizing_max_contracts.value()
            }
        }

        # Add custom strategy configuration if applicable
        if strategy_key == 'custom_strategy':
            custom_legs_config = []
            for leg_widget in self.custom_legs:
                custom_legs_config.append({
                    'type': leg_widget.type_combo.currentText().lower(),
                    'direction': leg_widget.dir_combo.currentText().lower(),
                    'delta': leg_widget.delta_spin.value(),
                    'quantity': leg_widget.qty_spin.value()
                })
            config['custom_legs'] = custom_legs_config
            config['custom_dte_type'] = self.custom_dte_type.currentText()

        return config
