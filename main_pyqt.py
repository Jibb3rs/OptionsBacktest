#!/usr/bin/env python3
"""
Options Backtesting System - PyQt5 Version
Modern UI with Apache ECharts integration
"""

import sys
import os

# Add project root to path (works in both dev and PyInstaller bundle)
if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import json

from core.paths import settings_file
from gui.pyqt_main_window import MainWindow
from gui.pyqt_theme import FONT_FAMILY, FONT_SIZE, apply_theme


def _check_license(app):
    """
    Validate license on startup. Shows activation dialog if needed.
    Returns True to proceed, False to exit.
    """
    from licensing.validator import load_stored_license, is_expiring_soon
    from gui.pyqt_license_dialog import LicenseDialog

    is_valid, message, payload = load_stored_license()

    if is_valid:
        return True  # Proceed; expiry warning injected later via MainWindow

    # Determine dialog mode
    if 'expired' in message.lower():
        mode = 'expired'
    elif 'no license' in message.lower():
        mode = 'not_found'
    else:
        mode = 'invalid'

    dialog = LicenseDialog(mode=mode, message=message)
    result = dialog.exec_()
    return result == LicenseDialog.Accepted


def main():
    """Main entry point"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # Required for QtWebEngine
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

    # Create application
    app = QApplication(sys.argv)

    # Set application info
    app.setApplicationName("Options Backtesting System")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("OptionsBacktest")

    # Set default font
    font = QFont(FONT_FAMILY, FONT_SIZE)
    app.setFont(font)

    # Load saved theme preference
    try:
        with open(settings_file(), 'r') as f:
            settings = json.load(f)
        saved_theme = settings.get('theme', 'dark')
        apply_theme(saved_theme)
    except (FileNotFoundError, json.JSONDecodeError):
        apply_theme('dark')

    # License check — must pass before main window opens
    if not _check_license(app):
        sys.exit(0)

    # Create and show main window
    window = MainWindow()

    # Show expiry warning banner if license is close to expiring
    from licensing.validator import is_expiring_soon
    expiring, days_left = is_expiring_soon()
    if expiring:
        from gui.pyqt_license_dialog import ExpiryWarningBanner
        banner = ExpiryWarningBanner(days_left, window)
        # Insert banner at top of main window's central widget layout
        try:
            central_layout = window.centralWidget().layout()
            if central_layout:
                central_layout.insertWidget(0, banner)
        except Exception:
            pass

    window.show()

    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
