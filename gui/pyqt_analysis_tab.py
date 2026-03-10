"""
PyQt5 Analysis Tab - Trade Analysis with ECharts
"""

import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QTableWidget, QTableWidgetItem,
    QSplitter, QComboBox, QGroupBox, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt

from .pyqt_theme import C
from .pyqt_main_window import create_panel, create_section_header
from .echarts_widget import (
    EChartsWidget, create_line_chart_option, create_bar_chart_option,
    create_scatter_chart_option
)


class AnalysisTab(QWidget):
    """Trade analysis tab with interactive charts"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.trades_df = None

        self._create_ui()

    def _create_ui(self):
        """Create the tab UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Upload section
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

        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter, 1)

        # Charts panel
        charts_panel = QFrame()
        charts_panel.setObjectName("panel")
        charts_layout = QVBoxLayout(charts_panel)
        charts_layout.setContentsMargins(14, 12, 14, 12)
        charts_layout.setSpacing(12)

        # Chart selector
        chart_selector = QHBoxLayout()
        chart_selector.setSpacing(12)

        chart_label = QLabel("Chart Type:")
        chart_label.setFixedWidth(100)
        chart_selector.addWidget(chart_label)

        self.chart_type = QComboBox()
        self.chart_type.setFixedWidth(200)
        self.chart_type.addItems([
            "Equity Curve",
            "P&L Distribution",
            "MAE/MFE Analysis",
            "Win Rate by Month",
            "Trade Duration"
        ])
        self.chart_type.currentIndexChanged.connect(self._update_chart)
        chart_selector.addWidget(self.chart_type)

        chart_selector.addStretch()
        charts_layout.addLayout(chart_selector)

        # Chart widget
        self.chart = EChartsWidget()
        self.chart.setMinimumHeight(300)
        charts_layout.addWidget(self.chart)

        splitter.addWidget(charts_panel)

        # Statistics panel
        stats_panel = QFrame()
        stats_panel.setObjectName("panel")
        stats_layout = QVBoxLayout(stats_panel)
        stats_layout.setContentsMargins(14, 12, 14, 12)
        stats_layout.setSpacing(8)

        stats_header = create_section_header("Performance Statistics")
        stats_layout.addWidget(stats_header)

        # Stats table
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Metric", "Value", "Metric ", "Value "])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_table.verticalHeader().hide()
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.stats_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stats_table.setFocusPolicy(Qt.NoFocus)
        stats_layout.addWidget(self.stats_table)

        splitter.addWidget(stats_panel)

        # Set splitter sizes
        splitter.setSizes([500, 300])

        # Show empty state
        self._show_empty_state()

    def _load_csv(self):
        """Load a results CSV file"""
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
        """Analyze loaded results"""
        if self.trades_df is None or self.trades_df.empty:
            return

        # Calculate statistics
        self._calculate_stats()

        # Update chart
        self._update_chart()

    def _calculate_stats(self):
        """Calculate performance statistics"""
        df = self.trades_df

        # Try to find P&L column
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

        stats = [
            ("Total Trades", len(df), "Win Rate", f"{len(wins)/len(df)*100:.1f}%" if len(df) > 0 else "N/A"),
            ("Winners", len(wins), "Losers", len(losses)),
            ("Total P&L", f"${pnl.sum():,.2f}", "Avg P&L", f"${pnl.mean():,.2f}"),
            ("Avg Win", f"${wins.mean():,.2f}" if len(wins) > 0 else "N/A",
             "Avg Loss", f"${losses.mean():,.2f}" if len(losses) > 0 else "N/A"),
            ("Max Win", f"${wins.max():,.2f}" if len(wins) > 0 else "N/A",
             "Max Loss", f"${losses.min():,.2f}" if len(losses) > 0 else "N/A"),
            ("Profit Factor", f"{abs(wins.sum()/losses.sum()):.2f}" if losses.sum() != 0 else "N/A",
             "Expectancy", f"${pnl.mean():,.2f}"),
        ]

        # Update table
        self.stats_table.setRowCount(len(stats))
        for row, (m1, v1, m2, v2) in enumerate(stats):
            self.stats_table.setItem(row, 0, QTableWidgetItem(str(m1)))
            self.stats_table.setItem(row, 1, QTableWidgetItem(str(v1)))
            self.stats_table.setItem(row, 2, QTableWidgetItem(str(m2)))
            self.stats_table.setItem(row, 3, QTableWidgetItem(str(v2)))

            # Color P&L values
            if isinstance(v1, str) and '$' in v1:
                item = self.stats_table.item(row, 1)
                if v1.startswith('$-'):
                    item.setForeground(Qt.GlobalColor.red)
                elif not v1.startswith('$0'):
                    item.setForeground(Qt.GlobalColor.green)

    def _update_chart(self):
        """Update the chart based on selection"""
        if self.trades_df is None or self.trades_df.empty:
            return

        chart_type = self.chart_type.currentText()
        df = self.trades_df

        # Find P&L column
        pnl_col = None
        for col in ['PnL', 'P&L', 'pnl', 'profit', 'Profit', 'NetProfit']:
            if col in df.columns:
                pnl_col = col
                break

        if pnl_col is None:
            return

        if chart_type == "Equity Curve":
            # Cumulative P&L
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
            # Histogram
            pnl = df[pnl_col].tolist()
            bins = 20
            import numpy as np
            hist, edges = np.histogram(pnl, bins=bins)

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
                            'type': 'linear',
                            'x': 0, 'y': 0, 'x2': 1, 'y2': 0,
                            'colorStops': [
                                {'offset': 0, 'color': C['down']},
                                {'offset': 0.5, 'color': C['yellow']},
                                {'offset': 1, 'color': C['up']}
                            ]
                        }
                    }
                }]
            }
            self.chart.set_option(option)

        elif chart_type == "MAE/MFE Analysis":
            # Scatter plot of MAE vs MFE
            mae_col = None
            mfe_col = None
            for col in df.columns:
                if 'mae' in col.lower():
                    mae_col = col
                if 'mfe' in col.lower():
                    mfe_col = col

            if mae_col and mfe_col:
                wins = df[df[pnl_col] > 0]
                losses = df[df[pnl_col] <= 0]

                option = create_scatter_chart_option(
                    "MAE vs MFE Analysis",
                    [
                        {'name': 'Winners', 'data': [[row[mae_col], row[mfe_col]] for _, row in wins.iterrows()]},
                        {'name': 'Losers', 'data': [[row[mae_col], row[mfe_col]] for _, row in losses.iterrows()]}
                    ],
                    "MAE ($)", "MFE ($)"
                )
                option['series'][0]['itemStyle'] = {'color': C['up']}
                option['series'][1]['itemStyle'] = {'color': C['down']}
                self.chart.set_option(option)

        elif chart_type == "Win Rate by Month":
            # Find date column
            date_col = None
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    date_col = col
                    break

            if date_col:
                df['_month'] = pd.to_datetime(df[date_col]).dt.to_period('M').astype(str)
                monthly = df.groupby('_month').agg({
                    pnl_col: ['count', lambda x: (x > 0).sum()]
                })
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
            # Find duration column or calculate
            duration_col = None
            for col in df.columns:
                if 'duration' in col.lower() or 'days' in col.lower():
                    duration_col = col
                    break

            if duration_col:
                durations = df[duration_col].tolist()
                x_data = list(range(1, len(durations) + 1))

                option = create_bar_chart_option(
                    "Trade Duration",
                    [str(x) for x in x_data],
                    [{'name': 'Duration (days)', 'data': durations}],
                    "Days"
                )
                self.chart.set_option(option)

    def _show_empty_state(self):
        """Show empty state chart"""
        option = {
            'title': {
                'text': 'Load a results CSV to view analysis',
                'left': 'center',
                'top': 'center',
                'textStyle': {
                    'color': C['dim'],
                    'fontSize': 16
                }
            }
        }
        self.chart.set_option(option)
