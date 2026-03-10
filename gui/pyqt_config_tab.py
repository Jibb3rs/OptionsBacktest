"""
PyQt5 Config Tab - Strategy Configuration
"""

import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QFrame,
    QScrollArea, QGridLayout, QMessageBox, QDateEdit,
    QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate

from .pyqt_theme import C
from .pyqt_main_window import (
    create_panel, create_form_row, create_section_header,
    create_two_column_widget
)

LABEL_WIDTH = 180
INPUT_WIDTH = 150


def _make_editable_card(title, widget):
    """Metric-style card with an editable widget inside."""
    card = QFrame()
    card.setObjectName("metricCard")
    cl = QVBoxLayout(card)
    cl.setContentsMargins(10, 8, 10, 8)
    cl.setSpacing(4)
    lbl = QLabel(title)
    lbl.setObjectName("dim")
    cl.addWidget(lbl)
    cl.addWidget(widget)
    return card


class ConfigTab(QWidget):
    """Strategy configuration tab"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._load_strategies()
        self._create_ui()

    def _load_strategies(self):
        from core.paths import resource_path
        try:
            with open(resource_path('config/strategies.json'), 'r') as f:
                self.strategies = json.load(f)
        except Exception:
            self.strategies = {}

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
        layout.setSpacing(16)
        layout.setContentsMargins(8, 8, 8, 8)

        # ── Strategy Selection ────────────────────────────────────────────
        strategy_panel, strategy_layout = create_panel("Strategy Selection")
        layout.addWidget(strategy_panel)

        self.strategy_combo = QComboBox()
        self.strategy_combo.setMinimumWidth(320)
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

        self.strategy_desc = QLabel()
        self.strategy_desc.setWordWrap(True)
        self.strategy_desc.setStyleSheet(f"color: {C['dim']}; padding: 8px;")
        strategy_layout.addWidget(self.strategy_desc)

        # ── Custom Strategy Builder ────────────────────────────────────────
        self.custom_container = QFrame()
        self.custom_container.setObjectName("panel")
        self.custom_container.setVisible(False)
        custom_layout = QVBoxLayout(self.custom_container)
        custom_layout.setContentsMargins(14, 12, 14, 12)

        custom_header = QLabel("Custom Strategy Builder")
        custom_header.setObjectName("header")
        custom_layout.addWidget(custom_header)

        self.custom_legs_count = QSpinBox()
        self.custom_legs_count.setRange(1, 10)
        self.custom_legs_count.setValue(2)
        self.custom_legs_count.setMinimumWidth(INPUT_WIDTH)
        self.custom_legs_count.setMaximumWidth(200)
        self.custom_legs_count.valueChanged.connect(self._update_custom_legs)
        create_form_row("Number of Legs:", self.custom_legs_count, custom_layout, LABEL_WIDTH)

        self.custom_legs_widget = QWidget()
        self.custom_legs_layout = QVBoxLayout(self.custom_legs_widget)
        self.custom_legs_layout.setContentsMargins(0, 10, 0, 0)
        self.custom_legs_layout.setSpacing(8)
        custom_layout.addWidget(self.custom_legs_widget)

        self.custom_dte_type = QComboBox()
        self.custom_dte_type.addItems(
            ["Standard DTE", "Weekly", "Monthly", "Quarterly", "End of Month"]
        )
        self.custom_dte_type.setMinimumWidth(INPUT_WIDTH)
        self.custom_dte_type.setMaximumWidth(250)
        create_form_row("Expiration Type:", self.custom_dte_type, custom_layout, LABEL_WIDTH)

        self.custom_legs = []
        self._update_custom_legs()
        layout.addWidget(self.custom_container)

        # ── Configuration (2-column) ──────────────────────────────────────
        config_panel, config_panel_layout = create_panel("Configuration")
        two_col, left_col, right_col = create_two_column_widget()
        config_panel_layout.addWidget(two_col)
        layout.addWidget(config_panel)

        # Left: Ticker, Date Range, Initial Capital
        self.ticker_input = QLineEdit("SPY")
        self.ticker_input.setMinimumWidth(INPUT_WIDTH)
        self.ticker_input.setMaximumWidth(200)
        create_form_row("Ticker:", self.ticker_input, left_col, LABEL_WIDTH)

        date_row = QHBoxLayout()
        date_row.setSpacing(12)
        date_lbl = QLabel("Date Range:")
        date_lbl.setFixedWidth(LABEL_WIDTH)
        date_row.addWidget(date_lbl)

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
        left_col.addLayout(date_row)

        self.capital_input = QSpinBox()
        self.capital_input.setRange(1000, 10000000)
        self.capital_input.setValue(100000)
        self.capital_input.setSingleStep(10000)
        self.capital_input.setPrefix("$")
        self.capital_input.setMinimumWidth(INPUT_WIDTH)
        self.capital_input.setMaximumWidth(200)
        create_form_row("Initial Capital:", self.capital_input, left_col, LABEL_WIDTH)

        # Right: Days to Expiry, Close At, Expiry Range
        self.expiry_days = QSpinBox()
        self.expiry_days.setRange(1, 365)
        self.expiry_days.setValue(30)
        self.expiry_days.setMinimumWidth(INPUT_WIDTH)
        self.expiry_days.setMaximumWidth(200)
        self.expiry_days.setSuffix(" days")
        create_form_row("Days to Expiry:", self.expiry_days, right_col, LABEL_WIDTH)

        self.close_dte = QSpinBox()
        self.close_dte.setRange(0, 60)
        self.close_dte.setValue(21)
        self.close_dte.setMinimumWidth(INPUT_WIDTH)
        self.close_dte.setMaximumWidth(200)
        self.close_dte.setSuffix(" days before expiry")
        create_form_row("Close At (DTE):", self.close_dte, right_col, LABEL_WIDTH)

        close_dte_note = QLabel(
            "Pro tip: 21 DTE exits avoid gamma blowup and lock in most of the theta decay"
        )
        close_dte_note.setStyleSheet(
            f"color: {C['dim']}; font-size: 12px; padding-left: 8px;"
        )
        close_dte_note.setWordWrap(True)
        right_col.addWidget(close_dte_note)

        self.expiry_range = QSpinBox()
        self.expiry_range.setRange(0, 30)
        self.expiry_range.setValue(5)
        self.expiry_range.setMinimumWidth(INPUT_WIDTH)
        self.expiry_range.setMaximumWidth(200)
        self.expiry_range.setSuffix(" days")
        create_form_row("Expiry Range (\u00b1):", self.expiry_range, right_col, LABEL_WIDTH)

        # ── Strike Selection ──────────────────────────────────────────────
        strike_panel, strike_layout = create_panel("Strike Selection")
        layout.addWidget(strike_panel)

        self.strike_method = QComboBox()
        self.strike_method.addItems(
            ["Delta-Based", "Fixed Points", "Percentage", "ATR-Based"]
        )
        self.strike_method.setMinimumWidth(INPUT_WIDTH)
        self.strike_method.setMaximumWidth(200)
        self.strike_method.currentIndexChanged.connect(self._on_strike_method_changed)
        create_form_row("Selection Method:", self.strike_method, strike_layout, LABEL_WIDTH)

        self.delta_container = QWidget()
        self.delta_layout = QGridLayout(self.delta_container)
        self.delta_layout.setContentsMargins(0, 10, 0, 0)
        self.delta_layout.setHorizontalSpacing(20)
        self.delta_layout.setVerticalSpacing(10)
        strike_layout.addWidget(self.delta_container)

        # ── Trading Rules ─────────────────────────────────────────────────
        rules_panel, rules_layout = create_panel("Trading Rules")
        layout.addWidget(rules_panel)

        # 5 editable metric cards
        self.max_positions = QSpinBox()
        self.max_positions.setRange(1, 100)
        self.max_positions.setValue(5)

        self.min_days = QSpinBox()
        self.min_days.setRange(0, 30)
        self.min_days.setValue(0)
        self.min_days.setSuffix(" days")

        self.profit_target = QSpinBox()
        self.profit_target.setRange(1, 500)
        self.profit_target.setValue(50)
        self.profit_target.setSuffix("%")

        self.stop_loss = QSpinBox()
        self.stop_loss.setRange(1, 1000)
        self.stop_loss.setValue(200)
        self.stop_loss.setSuffix("%")

        self.min_rr_ratio = QDoubleSpinBox()
        self.min_rr_ratio.setRange(0.0, 10.0)
        self.min_rr_ratio.setValue(0.0)
        self.min_rr_ratio.setDecimals(1)
        self.min_rr_ratio.setSingleStep(0.1)
        self.min_rr_ratio.setToolTip(
            "Skip trades where reward/risk is below this ratio. 0 = disabled."
        )

        cards_row = QHBoxLayout()
        cards_row.setSpacing(10)
        cards_row.addWidget(_make_editable_card("Max Positions", self.max_positions), 1)
        cards_row.addWidget(_make_editable_card("Min Days Between", self.min_days), 1)
        cards_row.addWidget(_make_editable_card("Profit Target", self.profit_target), 1)
        cards_row.addWidget(_make_editable_card("Stop Loss", self.stop_loss), 1)
        cards_row.addWidget(_make_editable_card("Min R/R Ratio", self.min_rr_ratio), 1)
        rules_layout.addLayout(cards_row)

        min_rr_note = QLabel(
            "Set Min R/R > 0 to skip low-quality setups "
            "(e.g. 0.3 skips trades paying < $0.30 per $1.00 risk)"
        )
        min_rr_note.setStyleSheet(f"color: {C['dim']}; font-size: 12px; padding-left: 4px;")
        min_rr_note.setWordWrap(True)
        rules_layout.addWidget(min_rr_note)

        # Stop Loss Mode
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

        # ── Generate Button (full width) ──────────────────────────────────
        self.generate_btn = QPushButton("Generate QuantConnect Code")
        self.generate_btn.setObjectName("primary")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.clicked.connect(self._generate_code)
        layout.addWidget(self.generate_btn)

        # ── R/R Estimate Panel (always visible) ───────────────────────────
        self.rr_panel = QFrame()
        self.rr_panel.setObjectName("panel")
        rr_outer = QVBoxLayout(self.rr_panel)
        rr_outer.setContentsMargins(16, 14, 16, 14)
        rr_outer.setSpacing(10)

        self.rr_header_label = QLabel("Estimated R/R per Trade")
        self.rr_header_label.setObjectName("header")
        rr_outer.addWidget(self.rr_header_label)

        self.rr_type_label = QLabel("Generate code to see R/R estimate")
        self.rr_type_label.setStyleSheet(f"color: {C['dim']}; font-size: 12px;")
        rr_outer.addWidget(self.rr_type_label)

        win_card, self.rr_win_label = self._make_rr_card("Max Win", C['up'])
        loss_card, self.rr_loss_label = self._make_rr_card("Max Stop", C['down'])
        ratio_card, self.rr_ratio_label = self._make_rr_card("R/R Ratio", C['accent'])
        be_card, self.rr_breakeven_label = self._make_rr_card("Min Win Rate", None)

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
        layout.addStretch()

        # Initialize
        self._on_strategy_changed()
        self._on_strike_method_changed()

    def _make_rr_card(self, title, color):
        from .pyqt_main_window import create_metric_card
        return create_metric_card(title, color)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_sizing_mode_changed(self):
        is_pct = self.sizing_mode.currentIndex() == 1
        self.sizing_contracts.setVisible(not is_pct)
        self.sizing_risk_pct.setVisible(is_pct)
        self.sizing_max_contracts.setVisible(is_pct)

    def _on_strategy_changed(self):
        strategy_keys = list(self.strategies.keys())
        idx = self.strategy_combo.currentIndex()
        if 0 <= idx < len(strategy_keys):
            key = strategy_keys[idx]
            strategy = self.strategies[key]
            self.strategy_desc.setText(strategy.get('description', ''))

            spread_type = strategy.get('spread_type', '')
            if spread_type == 'debit':
                self.stop_loss_mode.setCurrentIndex(1)
            elif spread_type == 'credit':
                self.stop_loss_mode.setCurrentIndex(0)

            is_custom = strategy.get('custom', False)
            self.custom_container.setVisible(is_custom)
            self.delta_container.setVisible(not is_custom)

            if not is_custom:
                self._update_delta_inputs(key)

    def _update_custom_legs(self):
        for leg_widget in self.custom_legs:
            leg_widget.setParent(None)
            leg_widget.deleteLater()
        self.custom_legs = []

        for i in range(self.custom_legs_count.value()):
            leg_frame = QFrame()
            leg_frame.setStyleSheet(
                f"background-color: {C['bg']}; border-radius: 4px; padding: 8px;"
            )
            leg_layout = QHBoxLayout(leg_frame)
            leg_layout.setContentsMargins(10, 8, 10, 8)
            leg_layout.setSpacing(15)

            leg_label = QLabel(f"Leg {i+1}:")
            leg_label.setFixedWidth(50)
            leg_label.setStyleSheet(f"color: {C['accent']}; font-weight: bold;")
            leg_layout.addWidget(leg_label)

            type_combo = QComboBox()
            type_combo.addItems(["Call", "Put", "Stock"])
            type_combo.setMinimumWidth(80)
            type_combo.setMaximumWidth(100)
            leg_layout.addWidget(QLabel("Type:"))
            leg_layout.addWidget(type_combo)

            dir_combo = QComboBox()
            dir_combo.addItems(["Long", "Short"])
            dir_combo.setMinimumWidth(80)
            dir_combo.setMaximumWidth(100)
            leg_layout.addWidget(QLabel("Direction:"))
            leg_layout.addWidget(dir_combo)

            delta_spin = QDoubleSpinBox()
            delta_spin.setRange(0.01, 0.99)
            delta_spin.setValue(0.30)
            delta_spin.setSingleStep(0.05)
            delta_spin.setDecimals(2)
            delta_spin.setMinimumWidth(80)
            delta_spin.setMaximumWidth(100)
            leg_layout.addWidget(QLabel("Delta:"))
            leg_layout.addWidget(delta_spin)

            qty_spin = QSpinBox()
            qty_spin.setRange(1, 100)
            qty_spin.setValue(1)
            qty_spin.setMinimumWidth(60)
            qty_spin.setMaximumWidth(80)
            leg_layout.addWidget(QLabel("Qty:"))
            leg_layout.addWidget(qty_spin)

            leg_layout.addStretch()

            leg_frame.type_combo = type_combo
            leg_frame.dir_combo = dir_combo
            leg_frame.delta_spin = delta_spin
            leg_frame.qty_spin = qty_spin

            self.custom_legs_layout.addWidget(leg_frame)
            self.custom_legs.append(leg_frame)

    def _on_strike_method_changed(self):
        pass

    def _update_delta_inputs(self, strategy_key):
        while self.delta_layout.count():
            item = self.delta_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.delta_inputs = {}

        strategy = self.strategies.get(strategy_key, {})
        if strategy.get('custom', False):
            return

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

            col += 2
            if col >= 4:
                col = 0
                row += 1

    def _get_delta_config(self, strategy_key):
        configs = {
            'iron_condor': {
                'Short Put Delta': 0.16, 'Long Put Delta': 0.08,
                'Short Call Delta': 0.16, 'Long Call Delta': 0.08
            },
            'iron_butterfly': {
                'ATM Delta': 0.50, 'Wing Width Delta': 0.16
            },
            'short_strangle': {
                'Short Put Delta': 0.16, 'Short Call Delta': 0.16
            },
            'short_straddle': {'ATM Delta': 0.50},
            'long_strangle': {
                'Long Put Delta': 0.30, 'Long Call Delta': 0.30
            },
            'long_straddle': {
                'Long Put Delta': 0.50, 'Long Call Delta': 0.50
            },
            'bull_put_spread': {
                'Short Put Delta': 0.30, 'Long Put Delta': 0.16
            },
            'bear_call_spread': {
                'Short Call Delta': 0.30, 'Long Call Delta': 0.16
            },
            'bull_call_spread': {
                'Long Call Delta': 0.70, 'Short Call Delta': 0.30
            },
            'bear_put_spread': {
                'Long Put Delta': 0.70, 'Short Put Delta': 0.30
            },
            'long_call': {'Long Call Delta': 0.50},
            'long_put': {'Long Put Delta': 0.50},
            'butterfly_spread': {'Center Delta': 0.50, 'Wing Width': 0.20},
            'calendar_spread': {'Strike Delta': 0.50},
            'diagonal_spread': {'Short Delta': 0.30, 'Long Delta': 0.50},
            'ratio_spread': {'Long Delta': 0.50, 'Short Delta': 0.30},
            'jade_lizard': {
                'Short Put Delta': 0.20, 'Short Call Delta': 0.30,
                'Long Call Delta': 0.20
            },
            'covered_call': {'Short Call Delta': 0.30},
            'protective_put': {'Long Put Delta': 0.30},
            'collar': {'Long Put Delta': 0.30, 'Short Call Delta': 0.30},
        }
        return configs.get(strategy_key, {'Delta': 0.30})

    def _generate_code(self):
        try:
            config = self.main_window.get_config()

            strategy_keys = list(self.strategies.keys())
            idx = self.strategy_combo.currentIndex()
            strategy_key = strategy_keys[idx]

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
                'custom_strategy': CustomStrategy,
            }

            strategy_class = strategy_map.get(strategy_key)
            if not strategy_class:
                QMessageBox.warning(self, "Error", f"Strategy '{strategy_key}' not implemented")
                return

            code = strategy_class.generate_code(config)
            self._update_rr_estimate(strategy_key)

            from .pyqt_code_popup import CodePopup
            popup = CodePopup(code, self)
            popup.exec_()

            self.main_window.update_status("Code generated successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate code: {str(e)}")

    def _update_rr_estimate(self, strategy_key):
        strategy = self.strategies.get(strategy_key, {})
        pt = self.profit_target.value()
        sl = self.stop_loss.value()
        mode = self.stop_loss_mode.currentText()

        if 'Credit' in mode:
            ratio = sl / pt
            breakeven = sl / (pt + sl) * 100
            self.rr_win_label.setText(f"+{pt}% of credit")
            self.rr_loss_label.setText(f"\u2212{sl}% of credit")
            self.rr_ratio_label.setText(f"1 : {ratio:.1f}")
            self.rr_breakeven_label.setText(f"{breakeven:.0f}%")
            self.rr_type_label.setText(
                f"Credit Spread \u2014 close at {pt}% profit, "
                f"stop when loss = {sl}% of premium collected"
            )
            self.rr_note_label.setText(
                f"Example: collect $1.00 credit \u2192 target exit at "
                f"+${pt/100:.2f} | stop at \u2212${sl/100:.2f} per contract"
            )

        elif 'Max Loss' in mode:
            approx_gain_factor = 0.5
            approx_ratio = sl / (pt * approx_gain_factor)
            breakeven = sl / (pt * approx_gain_factor + sl) * 100
            self.rr_win_label.setText(f"+{pt}% of max gain")
            self.rr_loss_label.setText(f"\u2212{sl}% of debit")
            self.rr_ratio_label.setText(f"~1 : {approx_ratio:.1f}")
            self.rr_breakeven_label.setText(f"~{breakeven:.0f}%")
            self.rr_type_label.setText(
                f"Debit Spread \u2014 target {pt}% of max profit, "
                f"stop at {sl}% of debit paid"
            )
            self.rr_note_label.setText(
                "Ratio is approximate \u2014 exact amounts depend on "
                "spread width & entry pricing in QuantConnect."
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

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def get_config(self):
        strategy_keys = list(self.strategies.keys())
        idx = self.strategy_combo.currentIndex()
        strategy_key = strategy_keys[idx] if 0 <= idx < len(strategy_keys) else 'iron_condor'

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
                'deltas': deltas,
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
                'sizing_max_contracts': self.sizing_max_contracts.value(),
            },
        }

        if strategy_key == 'custom_strategy':
            config['custom_legs'] = [
                {
                    'type': leg.type_combo.currentText().lower(),
                    'direction': leg.dir_combo.currentText().lower(),
                    'delta': leg.delta_spin.value(),
                    'quantity': leg.qty_spin.value(),
                }
                for leg in self.custom_legs
            ]
            config['custom_dte_type'] = self.custom_dte_type.currentText()

        return config
