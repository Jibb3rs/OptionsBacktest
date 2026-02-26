"""
PyQt5 Main Window - Options Backtesting System
Modern UI with Apache ECharts integration
"""

import os
import webbrowser
import subprocess
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QFrame, QStatusBar, QMenuBar, QMenu,
    QAction, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .pyqt_theme import C, STYLESHEET, FONT_FAMILY, FONT_SIZE


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Options Backtesting System")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Apply stylesheet
        self.setStyleSheet(STYLESHEET)

        # Create menu bar
        self._create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Import and create tabs
        from .pyqt_config_tab import ConfigTab
        from .pyqt_advanced_tab import AdvancedTab
        from .pyqt_indicators_tab import IndicatorsTab
        from .pyqt_analysis_tab import AnalysisTab
        from .pyqt_compare_tab import CompareTab
        from .pyqt_settings_tab import SettingsTab

        self.config_tab = ConfigTab(self)
        self.advanced_tab = AdvancedTab(self)
        self.indicators_tab = IndicatorsTab(self)
        self.analysis_tab = AnalysisTab(self)
        self.compare_tab = CompareTab(self)
        self.settings_tab = SettingsTab(self)

        # Add tabs
        self.tab_widget.addTab(self.config_tab, "Configure Backtest")
        self.tab_widget.addTab(self.advanced_tab, "Advanced Filters")
        self.tab_widget.addTab(self.indicators_tab, "Indicators")
        self.tab_widget.addTab(self.analysis_tab, "Trade Analysis")
        self.tab_widget.addTab(self.compare_tab, "Compare Strategies")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        # Create status bar
        self._create_status_bar()

        # Center window
        self._center_window()

    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Configuration", self)
        new_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        file_menu.addAction(new_action)

        load_action = QAction("Load Results", self)
        load_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        qc_action = QAction("Open QuantConnect", self)
        qc_action.triggered.connect(
            lambda: webbrowser.open('https://www.quantconnect.com/terminal'))
        tools_menu.addAction(qc_action)

        output_action = QAction("Open Output Folder", self)
        output_action.triggered.connect(self._open_output_folder)
        tools_menu.addAction(output_action)

        results_action = QAction("Open Results Folder", self)
        results_action.triggered.connect(self._open_results_folder)
        tools_menu.addAction(results_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        delta_action = QAction("Understanding Delta", self)
        delta_action.triggered.connect(self._show_delta_help)
        help_menu.addAction(delta_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label, 1)

        version_label = QLabel("v3.0")
        self.status_bar.addPermanentWidget(version_label)

    def _center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.setText(message)

    def get_config(self):
        """Collect configuration from all tabs"""
        config = self.config_tab.get_config()
        config['advanced'] = self.advanced_tab.get_config()
        config['indicators'] = self.indicators_tab.get_config()
        return config

    def _open_output_folder(self):
        """Open output folder"""
        path = os.path.expanduser("~/Desktop/QC_Upload")
        os.makedirs(path, exist_ok=True)
        self._open_folder(path)

    def _open_results_folder(self):
        """Open results folder"""
        path = os.path.join(os.getcwd(), "results")
        os.makedirs(path, exist_ok=True)
        self._open_folder(path)

    def _open_folder(self, path):
        """Open a folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(['open', path])
        except Exception as e:
            QMessageBox.information(self, "Folder", f"Folder: {path}")

    def _show_delta_help(self):
        """Show delta explanation"""
        help_text = """UNDERSTANDING DELTA AND WIN PROBABILITY

Delta = Probability the option expires In-The-Money (ITM)

FOR SOLD OPTIONS (like Iron Condor short legs):

Delta     ITM Chance    OTM Chance (YOU WIN!)
------    ----------    ---------------------
0.05         5%             95%  <- Very safe
0.10        10%             90%  <- Conservative
0.16        16%             84%  <- Standard (Most common)
0.20        20%             80%  <- Moderate
0.25        25%             75%  <- Aggressive
0.30        30%             70%  <- Very aggressive

REAL EXAMPLE:
- SPX trading at 6000
- You sell a put with 0.16 delta
- System finds the 5900 put (100 points below)
- This put has 16% chance of expiring ITM
- Which means 84% chance it expires worthless
- If it expires worthless = YOU WIN!

WHY DELTA INSTEAD OF FIXED POINTS?

Delta automatically adjusts for volatility:

When VIX is LOW (market calm):
- 0.16 delta might be only 50 points away

When VIX is HIGH (market volatile):
- 0.16 delta might be 150 points away

SAME 84% WIN RATE, but different distances!

RECOMMENDATION FOR NEW TRADERS:
- Start with 0.10 delta (90% win rate)
- Move to 0.16 delta (84% win rate) when comfortable
- Only use 0.25+ delta (75% win) if very experienced"""

        QMessageBox.information(self, "Understanding Delta", help_text)

    def _show_about(self):
        """Show about dialog"""
        about_text = """Options Backtesting System v3.0

A comprehensive tool for backtesting options strategies
using QuantConnect's historical data.

Features:
- 21 preset option strategies + custom builder
- 16 technical indicators
- Delta-based strike selection
- Complete QuantConnect integration
- MAE/MFE analysis
- 30+ performance metrics
- Strategy comparison tool
- Advanced filters (VIX, IV Rank, Greeks, etc.)
- Interactive ECharts visualizations"""

        QMessageBox.about(self, "About", about_text)


def create_panel(title=None):
    """Create a styled panel frame"""
    panel = QFrame()
    panel.setObjectName("panel")

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(10)

    if title:
        title_label = QLabel(title)
        title_label.setObjectName("header")
        layout.addWidget(title_label)

    return panel, layout


def create_form_row(label_text, widget, parent_layout, label_width=180):
    """Create a form row with label and widget"""
    row = QHBoxLayout()
    row.setSpacing(12)

    label = QLabel(label_text)
    label.setFixedWidth(label_width)
    row.addWidget(label)

    if widget:
        if widget.minimumWidth() < 100:
            widget.setMinimumWidth(150)
        row.addWidget(widget)

    row.addStretch()
    parent_layout.addLayout(row)
    return row


def create_section_header(text):
    """Create a section header label"""
    label = QLabel(text)
    label.setObjectName("header")
    return label


def create_dim_label(text):
    """Create a dim/muted label"""
    label = QLabel(text)
    label.setObjectName("dim")
    return label
