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
        self.strategy_combo.setMinimumWidth(250)
        self.strategy_combo.addItems([s['name'] for s in self.strategies.values()])
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

        # Add stretch at bottom
        layout.addStretch()

        # Initialize
        self._on_strategy_changed()
        self._on_strike_method_changed()

    def _on_strategy_changed(self):
        """Handle strategy selection change"""
        strategy_keys = list(self.strategies.keys())
        idx = self.strategy_combo.currentIndex()
        if 0 <= idx < len(strategy_keys):
            key = strategy_keys[idx]
            strategy = self.strategies[key]
            self.strategy_desc.setText(strategy.get('description', ''))

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

            # Show code popup
            from .pyqt_code_popup import CodePopup
            popup = CodePopup(code, self)
            popup.exec_()

            self.main_window.update_status("Code generated successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate code: {str(e)}")

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
            'strike_selection': {
                'method': self.strike_method.currentText(),
                'deltas': deltas
            },
            'trading_rules': {
                'max_positions': self.max_positions.value(),
                'min_days_between_trades': self.min_days.value(),
                'profit_target_pct': self.profit_target.value(),
                'stop_loss_pct': self.stop_loss.value(),
                'stop_loss_mode': self.stop_loss_mode.currentText()
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
