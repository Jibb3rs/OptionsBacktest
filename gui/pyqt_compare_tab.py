"""
PyQt5 Compare Tab - Strategy Comparison with ECharts
"""

import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QSplitter, QAbstractItemView
)
from PyQt5.QtCore import Qt

from .pyqt_theme import C
from .pyqt_main_window import create_panel, create_section_header
from .echarts_widget import EChartsWidget, create_line_chart_option, create_bar_chart_option


class CompareTab(QWidget):
    """Strategy comparison tab"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.loaded_results = {}  # {filename: dataframe}

        self._create_ui()

    def _create_ui(self):
        """Create the tab UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Top section - file management
        file_panel, file_layout = create_panel("Load Results for Comparison")

        file_row = QHBoxLayout()
        file_row.setSpacing(12)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_list.setMinimumHeight(100)
        self.file_list.setMaximumHeight(120)
        file_row.addWidget(self.file_list, 1)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        add_btn = QPushButton("Add CSV")
        add_btn.setMinimumWidth(120)
        add_btn.setMinimumHeight(35)
        add_btn.clicked.connect(self._add_csv)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.setMinimumWidth(120)
        remove_btn.setMinimumHeight(35)
        remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(remove_btn)

        compare_btn = QPushButton("Compare")
        compare_btn.setObjectName("primary")
        compare_btn.setMinimumWidth(120)
        compare_btn.setMinimumHeight(35)
        compare_btn.clicked.connect(self._compare)
        btn_layout.addWidget(compare_btn)

        btn_layout.addStretch()
        file_row.addLayout(btn_layout)

        file_layout.addLayout(file_row)
        layout.addWidget(file_panel)

        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter, 1)

        # Charts panel
        charts_panel = QFrame()
        charts_panel.setObjectName("panel")
        charts_layout = QVBoxLayout(charts_panel)
        charts_layout.setContentsMargins(14, 12, 14, 12)
        charts_layout.setSpacing(12)

        charts_layout.addWidget(create_section_header("Equity Curves Comparison"))

        self.equity_chart = EChartsWidget()
        self.equity_chart.setMinimumHeight(220)
        charts_layout.addWidget(self.equity_chart)

        charts_layout.addWidget(create_section_header("Performance Metrics Comparison"))

        self.metrics_chart = EChartsWidget()
        self.metrics_chart.setMinimumHeight(220)
        charts_layout.addWidget(self.metrics_chart)

        splitter.addWidget(charts_panel)

        # Comparison table panel
        table_panel = QFrame()
        table_panel.setObjectName("panel")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(14, 12, 14, 12)
        table_layout.setSpacing(8)

        table_layout.addWidget(create_section_header("Detailed Comparison"))

        self.compare_table = QTableWidget()
        self.compare_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.compare_table)

        splitter.addWidget(table_panel)

        splitter.setSizes([500, 300])

        # Show empty state
        self._show_empty_state()

    def _add_csv(self):
        """Add CSV files for comparison"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Results CSV Files",
            os.path.join(os.getcwd(), "results"),
            "CSV Files (*.csv)"
        )

        for file_path in files:
            filename = os.path.basename(file_path)
            if filename not in self.loaded_results:
                try:
                    df = pd.read_csv(file_path)
                    self.loaded_results[filename] = df

                    item = QListWidgetItem(filename)
                    self.file_list.addItem(item)
                except Exception as e:
                    self.main_window.update_status(f"Error loading {filename}: {e}")

    def _remove_selected(self):
        """Remove selected files"""
        for item in self.file_list.selectedItems():
            filename = item.text()
            if filename in self.loaded_results:
                del self.loaded_results[filename]
            self.file_list.takeItem(self.file_list.row(item))

    def _compare(self):
        """Compare all loaded results"""
        if len(self.loaded_results) < 1:
            return

        self._update_equity_chart()
        self._update_metrics_chart()
        self._update_comparison_table()

    def _find_pnl_column(self, df):
        """Find the P&L column in a dataframe"""
        for col in ['PnL', 'P&L', 'pnl', 'profit', 'Profit', 'NetProfit']:
            if col in df.columns:
                return col
        return None

    def _update_equity_chart(self):
        """Update equity curves comparison chart"""
        series_data = []

        for name, df in self.loaded_results.items():
            pnl_col = self._find_pnl_column(df)
            if pnl_col:
                cumsum = df[pnl_col].cumsum().tolist()
                series_data.append({
                    'name': name,
                    'data': cumsum
                })

        if series_data:
            max_len = max(len(s['data']) for s in series_data)
            x_data = [str(i) for i in range(1, max_len + 1)]

            option = create_line_chart_option(
                "Equity Curves Comparison",
                x_data,
                series_data,
                "Cumulative P&L ($)"
            )
            self.equity_chart.set_option(option)

    def _update_metrics_chart(self):
        """Update metrics comparison bar chart"""
        metrics = {
            'Total P&L': [],
            'Win Rate': [],
            'Avg Win': [],
            'Avg Loss': [],
            'Profit Factor': []
        }
        names = []

        for name, df in self.loaded_results.items():
            pnl_col = self._find_pnl_column(df)
            if pnl_col:
                pnl = df[pnl_col]
                wins = pnl[pnl > 0]
                losses = pnl[pnl < 0]

                names.append(name.replace('.csv', ''))
                metrics['Total P&L'].append(round(pnl.sum(), 2))
                metrics['Win Rate'].append(round(len(wins)/len(df)*100 if len(df) > 0 else 0, 1))
                metrics['Avg Win'].append(round(wins.mean() if len(wins) > 0 else 0, 2))
                metrics['Avg Loss'].append(round(abs(losses.mean()) if len(losses) > 0 else 0, 2))
                metrics['Profit Factor'].append(
                    round(abs(wins.sum()/losses.sum()) if losses.sum() != 0 else 0, 2)
                )

        if names:
            # Normalize for comparison
            option = {
                'title': {'text': 'Performance Metrics Comparison', 'left': 'center'},
                'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
                'legend': {'data': list(metrics.keys()), 'top': 30},
                'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True},
                'xAxis': {'type': 'category', 'data': names},
                'yAxis': {'type': 'value'},
                'series': [
                    {'name': metric, 'type': 'bar', 'data': values}
                    for metric, values in metrics.items()
                    if metric in ['Total P&L', 'Win Rate', 'Profit Factor']
                ]
            }
            self.metrics_chart.set_option(option)

    def _update_comparison_table(self):
        """Update the comparison table"""
        if not self.loaded_results:
            return

        # Columns: Metric + one per strategy
        names = list(self.loaded_results.keys())
        self.compare_table.setColumnCount(len(names) + 1)
        self.compare_table.setHorizontalHeaderLabels(['Metric'] + [n.replace('.csv', '') for n in names])

        metrics = [
            'Total Trades',
            'Winners',
            'Losers',
            'Win Rate',
            'Total P&L',
            'Average P&L',
            'Avg Winner',
            'Avg Loser',
            'Max Win',
            'Max Loss',
            'Profit Factor',
            'Sharpe Ratio'
        ]

        self.compare_table.setRowCount(len(metrics))

        for row, metric in enumerate(metrics):
            self.compare_table.setItem(row, 0, QTableWidgetItem(metric))

            for col, (name, df) in enumerate(self.loaded_results.items(), 1):
                value = self._calculate_metric(df, metric)
                item = QTableWidgetItem(str(value))

                # Color code
                if 'P&L' in metric or metric in ['Profit Factor', 'Sharpe Ratio']:
                    try:
                        num = float(value.replace('$', '').replace(',', '').replace('%', ''))
                        if num > 0:
                            item.setForeground(Qt.GlobalColor.green)
                        elif num < 0:
                            item.setForeground(Qt.GlobalColor.red)
                    except:
                        pass

                self.compare_table.setItem(row, col, item)

    def _calculate_metric(self, df, metric):
        """Calculate a specific metric for a dataframe"""
        pnl_col = self._find_pnl_column(df)
        if not pnl_col:
            return 'N/A'

        pnl = df[pnl_col]
        wins = pnl[pnl > 0]
        losses = pnl[pnl < 0]

        calculations = {
            'Total Trades': len(df),
            'Winners': len(wins),
            'Losers': len(losses),
            'Win Rate': f"{len(wins)/len(df)*100:.1f}%" if len(df) > 0 else 'N/A',
            'Total P&L': f"${pnl.sum():,.2f}",
            'Average P&L': f"${pnl.mean():,.2f}",
            'Avg Winner': f"${wins.mean():,.2f}" if len(wins) > 0 else 'N/A',
            'Avg Loser': f"${losses.mean():,.2f}" if len(losses) > 0 else 'N/A',
            'Max Win': f"${wins.max():,.2f}" if len(wins) > 0 else 'N/A',
            'Max Loss': f"${losses.min():,.2f}" if len(losses) > 0 else 'N/A',
            'Profit Factor': f"{abs(wins.sum()/losses.sum()):.2f}" if losses.sum() != 0 else 'N/A',
            'Sharpe Ratio': f"{(pnl.mean()/pnl.std()):.2f}" if pnl.std() != 0 else 'N/A'
        }

        return calculations.get(metric, 'N/A')

    def _show_empty_state(self):
        """Show empty state"""
        option = {
            'title': {
                'text': 'Add CSV files to compare strategies',
                'left': 'center',
                'top': 'center',
                'textStyle': {'color': C['dim'], 'fontSize': 16}
            }
        }
        self.equity_chart.set_option(option)
        self.metrics_chart.set_option(option)
