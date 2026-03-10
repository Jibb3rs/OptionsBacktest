"""
PyQt5 Analysis Tab - Trade Analysis with ECharts
"""

import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QTableWidget, QTableWidgetItem,
    QSplitter, QAbstractItemView, QHeaderView, QButtonGroup
)
from PyQt5.QtCore import Qt

from .pyqt_theme import C
from .pyqt_main_window import create_panel, create_metric_card
from .pyqt_widgets import CollapsibleSection
from .echarts_widget import (
    EChartsWidget, create_line_chart_option, create_bar_chart_option,
    create_scatter_chart_option
)

CHART_NAMES = [
    "Equity Curve",
    "P&L Distribution",
    "MAE/MFE Analysis",
    "Win Rate by Month",
    "Trade Duration",
]


class AnalysisTab(QWidget):
    """Trade analysis tab with interactive charts"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.trades_df = None
        self._current_chart = CHART_NAMES[0]
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── Load Results ──────────────────────────────────────────────────
        upload_panel, upload_layout = create_panel("Load Results")

        upload_row = QHBoxLayout()
        upload_row.setSpacing(12)

        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet(f"color: {C['dim']}; padding: 8px;")
        upload_row.addWidget(self.file_label, 1)

        upload_btn = QPushButton("Load CSV")
        upload_btn.setObjectName("primary")
        upload_btn.setMinimumWidth(120)
        upload_btn.setMinimumHeight(35)
        upload_btn.clicked.connect(self._load_csv)
        upload_row.addWidget(upload_btn)

        upload_layout.addLayout(upload_row)
        layout.addWidget(upload_panel)

        # ── 4 Summary Cards ───────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        self.card_pnl, self.lbl_pnl = create_metric_card("Total P&L", C['up'])
        self.card_winrate, self.lbl_winrate = create_metric_card("Win Rate", None)
        self.card_pf, self.lbl_pf = create_metric_card("Profit Factor", C['accent'])
        self.card_sharpe, self.lbl_sharpe = create_metric_card("Sharpe Ratio", None)

        cards_row.addWidget(self.card_pnl, 1)
        cards_row.addWidget(self.card_winrate, 1)
        cards_row.addWidget(self.card_pf, 1)
        cards_row.addWidget(self.card_sharpe, 1)
        layout.addLayout(cards_row)

        # ── Charts Panel ──────────────────────────────────────────────────
        charts_panel = QFrame()
        charts_panel.setObjectName("panel")
        charts_layout = QVBoxLayout(charts_panel)
        charts_layout.setContentsMargins(14, 12, 14, 12)
        charts_layout.setSpacing(12)

        # Pill chart selector
        pill_row = QHBoxLayout()
        pill_row.setSpacing(8)
        self._chart_btn_group = QButtonGroup(self)
        self._chart_btn_group.setExclusive(True)

        for i, name in enumerate(CHART_NAMES):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setObjectName("pillButton")
            btn.setChecked(i == 0)
            self._chart_btn_group.addButton(btn, i)
            pill_row.addWidget(btn)

        pill_row.addStretch()
        self._chart_btn_group.idClicked.connect(self._on_chart_btn)
        charts_layout.addLayout(pill_row)

        # Chart widget
        self.chart = EChartsWidget()
        self.chart.setMinimumHeight(300)
        charts_layout.addWidget(self.chart)

        layout.addWidget(charts_panel, 1)

        # ── Collapsible Stats Table ───────────────────────────────────────
        stats_section = CollapsibleSection("Performance Statistics", initially_expanded=True)

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Metric", "Value", "Metric ", "Value "])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_table.verticalHeader().hide()
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.stats_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stats_table.setFocusPolicy(Qt.NoFocus)
        stats_section.body_layout().addWidget(self.stats_table)

        layout.addWidget(stats_section)

        self._show_empty_state()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_chart_btn(self, idx):
        self._current_chart = CHART_NAMES[idx]
        self._update_chart()

    def _load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Results CSV",
            os.path.join(os.getcwd(), "results"),
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                self.trades_df = pd.read_csv(file_path)
                self.file_label.setText(os.path.basename(file_path))
                self._analyze_results()
                self.main_window.update_status(f"Loaded {len(self.trades_df)} trades")
            except Exception as e:
                self.file_label.setText(f"Error: {str(e)}")

    def _analyze_results(self):
        if self.trades_df is None or self.trades_df.empty:
            return
        self._calculate_stats()
        self._update_chart()

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def _calculate_stats(self):
        df = self.trades_df

        pnl_col = None
        for col in ['PnL', 'P&L', 'pnl', 'profit', 'Profit', 'NetProfit']:
            if col in df.columns:
                pnl_col = col
                break

        if pnl_col is None:
            return

        pnl = df[pnl_col]
        wins = pnl[pnl > 0]
        losses = pnl[pnl < 0]

        # Update summary cards
        total_pnl = pnl.sum()
        win_rate = len(wins) / len(df) * 100 if len(df) > 0 else 0
        profit_factor = abs(wins.sum() / losses.sum()) if losses.sum() != 0 else 0
        sharpe = (pnl.mean() / pnl.std()) if pnl.std() != 0 else 0

        pnl_color = C['up'] if total_pnl >= 0 else C['down']
        self.lbl_pnl.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {pnl_color};")
        self.lbl_pnl.setText(f"${total_pnl:,.0f}")
        self.lbl_winrate.setText(f"{win_rate:.1f}%")
        self.lbl_pf.setText(f"{profit_factor:.2f}")
        self.lbl_sharpe.setText(f"{sharpe:.2f}")

        # Stats table
        stats = [
            ("Total Trades", len(df), "Win Rate", f"{win_rate:.1f}%"),
            ("Winners", len(wins), "Losers", len(losses)),
            ("Total P&L", f"${pnl.sum():,.2f}", "Avg P&L", f"${pnl.mean():,.2f}"),
            (
                "Avg Win",
                f"${wins.mean():,.2f}" if len(wins) > 0 else "N/A",
                "Avg Loss",
                f"${losses.mean():,.2f}" if len(losses) > 0 else "N/A",
            ),
            (
                "Max Win",
                f"${wins.max():,.2f}" if len(wins) > 0 else "N/A",
                "Max Loss",
                f"${losses.min():,.2f}" if len(losses) > 0 else "N/A",
            ),
            (
                "Profit Factor",
                f"{profit_factor:.2f}",
                "Expectancy",
                f"${pnl.mean():,.2f}",
            ),
        ]

        self.stats_table.setRowCount(len(stats))
        for row, (m1, v1, m2, v2) in enumerate(stats):
            self.stats_table.setItem(row, 0, QTableWidgetItem(str(m1)))
            self.stats_table.setItem(row, 1, QTableWidgetItem(str(v1)))
            self.stats_table.setItem(row, 2, QTableWidgetItem(str(m2)))
            self.stats_table.setItem(row, 3, QTableWidgetItem(str(v2)))

            if isinstance(v1, str) and '$' in v1:
                item = self.stats_table.item(row, 1)
                if v1.startswith('$-'):
                    item.setForeground(Qt.GlobalColor.red)
                elif not v1.startswith('$0'):
                    item.setForeground(Qt.GlobalColor.green)

    # ------------------------------------------------------------------
    # Charts
    # ------------------------------------------------------------------

    def _update_chart(self):
        if self.trades_df is None or self.trades_df.empty:
            return

        df = self.trades_df
        pnl_col = None
        for col in ['PnL', 'P&L', 'pnl', 'profit', 'Profit', 'NetProfit']:
            if col in df.columns:
                pnl_col = col
                break

        if pnl_col is None:
            return

        chart_type = self._current_chart

        if chart_type == "Equity Curve":
            cumsum = df[pnl_col].cumsum().tolist()
            x_data = list(range(1, len(cumsum) + 1))
            option = create_line_chart_option(
                "Equity Curve",
                [str(x) for x in x_data],
                [{'name': 'Cumulative P&L', 'data': cumsum}],
                "P&L ($)"
            )
            self.chart.set_option(option)

        elif chart_type == "P&L Distribution":
            import numpy as np
            pnl = df[pnl_col].tolist()
            hist, edges = np.histogram(pnl, bins=20)
            option = {
                'title': {'text': 'P&L Distribution', 'left': 'center'},
                'tooltip': {'trigger': 'axis'},
                'xAxis': {
                    'type': 'category',
                    'data': [f'${int(edges[i])}-${int(edges[i+1])}' for i in range(len(hist))]
                },
                'yAxis': {'type': 'value', 'name': 'Count'},
                'series': [{
                    'type': 'bar',
                    'data': hist.tolist(),
                    'itemStyle': {
                        'color': {
                            'type': 'linear', 'x': 0, 'y': 0, 'x2': 1, 'y2': 0,
                            'colorStops': [
                                {'offset': 0, 'color': C['down']},
                                {'offset': 0.5, 'color': C['yellow']},
                                {'offset': 1, 'color': C['up']},
                            ]
                        }
                    }
                }]
            }
            self.chart.set_option(option)

        elif chart_type == "MAE/MFE Analysis":
            mae_col = next((c for c in df.columns if 'mae' in c.lower()), None)
            mfe_col = next((c for c in df.columns if 'mfe' in c.lower()), None)
            if mae_col and mfe_col:
                wins = df[df[pnl_col] > 0]
                losses = df[df[pnl_col] <= 0]
                option = create_scatter_chart_option(
                    "MAE vs MFE Analysis",
                    [
                        {'name': 'Winners', 'data': [[r[mae_col], r[mfe_col]] for _, r in wins.iterrows()]},
                        {'name': 'Losers', 'data': [[r[mae_col], r[mfe_col]] for _, r in losses.iterrows()]},
                    ],
                    "MAE ($)", "MFE ($)"
                )
                option['series'][0]['itemStyle'] = {'color': C['up']}
                option['series'][1]['itemStyle'] = {'color': C['down']}
                self.chart.set_option(option)

        elif chart_type == "Win Rate by Month":
            date_col = next(
                (c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()), None
            )
            if date_col:
                df['_month'] = pd.to_datetime(df[date_col]).dt.to_period('M').astype(str)
                monthly = df.groupby('_month').agg({pnl_col: ['count', lambda x: (x > 0).sum()]})
                monthly.columns = ['total', 'wins']
                monthly['win_rate'] = (monthly['wins'] / monthly['total'] * 100).round(1)
                option = create_bar_chart_option(
                    "Win Rate by Month",
                    monthly.index.tolist(),
                    [{'name': 'Win Rate %', 'data': monthly['win_rate'].tolist()}],
                    "Win Rate (%)"
                )
                self.chart.set_option(option)

        elif chart_type == "Trade Duration":
            duration_col = next(
                (c for c in df.columns if 'duration' in c.lower() or 'days' in c.lower()), None
            )
            if duration_col:
                durations = df[duration_col].tolist()
                option = create_bar_chart_option(
                    "Trade Duration",
                    [str(i) for i in range(1, len(durations) + 1)],
                    [{'name': 'Duration (days)', 'data': durations}],
                    "Days"
                )
                self.chart.set_option(option)

    def _show_empty_state(self):
        option = {
            'title': {
                'text': 'Load a results CSV to view analysis',
                'left': 'center',
                'top': 'center',
                'textStyle': {'color': C['dim'], 'fontSize': 16}
            }
        }
        self.chart.set_option(option)
