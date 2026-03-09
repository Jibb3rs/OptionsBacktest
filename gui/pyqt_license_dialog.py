"""
License Activation Dialog — shown to users when no valid license is found.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .pyqt_theme import C


class LicenseDialog(QDialog):
    """
    Shown on startup when license is missing, invalid, or expired.
    User pastes their OB-... license key to activate.
    """

    def __init__(self, parent=None, mode='not_found', message=''):
        super().__init__(parent)
        self.setWindowTitle("OptionsBacktest — Activate")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setFixedWidth(520)
        self.setModal(True)

        self._build_ui(mode, message)

    # ── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self, mode, message):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(20)

        # Header
        header_row = QHBoxLayout()
        icon_lbl = QLabel("🔑" if mode != 'expired' else "⏰")
        icon_lbl.setStyleSheet("font-size: 28px;")
        icon_lbl.setFixedWidth(44)

        title_col = QVBoxLayout()
        title = QLabel(self._title_for(mode))
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {C['text']};")

        sub = QLabel(self._subtitle_for(mode))
        sub.setStyleSheet(f"font-size: 12px; color: {C['dim']};")
        sub.setWordWrap(True)

        title_col.addWidget(title)
        title_col.addWidget(sub)
        title_col.setSpacing(3)

        header_row.addWidget(icon_lbl)
        header_row.addLayout(title_col)
        layout.addLayout(header_row)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {C['card_border']};")
        layout.addWidget(div)

        # Status banner (for expired / invalid)
        if mode in ('expired', 'invalid') and message:
            banner = QFrame()
            banner_color = "#d29922" if mode == 'expired' else "#f85149"
            banner.setStyleSheet(
                f"QFrame {{ background: rgba({self._hex_to_rgb(banner_color)}, 0.10); "
                f"border: 1px solid rgba({self._hex_to_rgb(banner_color)}, 0.40); "
                f"border-left: 3px solid {banner_color}; border-radius: 4px; padding: 2px; }}"
            )
            banner_layout = QVBoxLayout(banner)
            banner_layout.setContentsMargins(10, 8, 10, 8)
            msg_lbl = QLabel(message)
            msg_lbl.setStyleSheet(f"color: {banner_color}; font-size: 12px; border: none; background: transparent;")
            msg_lbl.setWordWrap(True)
            banner_layout.addWidget(msg_lbl)
            layout.addWidget(banner)

        # Key input
        input_lbl = QLabel("Paste your license key below:")
        input_lbl.setStyleSheet(f"font-size: 12px; color: {C['dim']};")
        layout.addWidget(input_lbl)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("OB-eyJ1aWQiOi...")
        self.key_input.setMinimumHeight(36)
        self.key_input.setStyleSheet(
            f"QLineEdit {{ background: {C['input_bg']}; border: 1px solid {C['card_border']}; "
            f"border-radius: 4px; padding: 6px 10px; color: {C['text']}; "
            f"font-family: 'Courier New', monospace; font-size: 11px; }}"
            f"QLineEdit:focus {{ border-color: {C['accent']}; }}"
        )
        self.key_input.textChanged.connect(self._clear_error)
        layout.addWidget(self.key_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f85149; font-size: 11px;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.activate_btn = QPushButton("Activate")
        self.activate_btn.setMinimumHeight(36)
        self.activate_btn.setStyleSheet(
            f"QPushButton {{ background: {C['accent']}; color: {C['bg']}; border: none; "
            f"border-radius: 4px; font-weight: bold; padding: 6px 24px; }}"
            f"QPushButton:hover {{ background: #e6c800; }}"
            f"QPushButton:pressed {{ background: #c8a800; }}"
        )
        self.activate_btn.clicked.connect(self._activate)
        self.activate_btn.setDefault(True)

        exit_btn = QPushButton("Exit")
        exit_btn.setMinimumHeight(36)
        exit_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {C['dim']}; "
            f"border: 1px solid {C['card_border']}; border-radius: 4px; padding: 6px 16px; }}"
            f"QPushButton:hover {{ color: {C['text']}; border-color: {C['dim']}; }}"
        )
        exit_btn.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(exit_btn)
        btn_row.addWidget(self.activate_btn)
        layout.addLayout(btn_row)

        # Footer note
        footer = QLabel("Need a license? Contact your OptionsBacktest provider.")
        footer.setStyleSheet(f"font-size: 11px; color: {C['dim']};")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

    # ── Logic ────────────────────────────────────────────────────────────────

    def _activate(self):
        from licensing.validator import validate_key, save_license

        key_str = self.key_input.text().strip()
        if not key_str:
            self.error_label.setText("Please paste your license key.")
            return

        is_valid, message, payload = validate_key(key_str)

        if is_valid:
            save_license(key_str)
            self.accept()
        else:
            self.error_label.setText(f"✗  {message}")

    def _clear_error(self):
        self.error_label.setText("")

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _title_for(mode):
        return {
            'not_found': 'Activate OptionsBacktest',
            'expired':   'License Expired',
            'invalid':   'Invalid License',
        }.get(mode, 'Activate OptionsBacktest')

    @staticmethod
    def _subtitle_for(mode):
        return {
            'not_found': 'Enter your license key to get started.',
            'expired':   'Your license has expired. Enter a new key to continue.',
            'invalid':   'The stored license could not be verified. Please re-enter your key.',
        }.get(mode, 'Enter your license key to get started.')

    @staticmethod
    def _hex_to_rgb(hex_color):
        h = hex_color.lstrip('#')
        return ', '.join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))


class ExpiryWarningBanner(QFrame):
    """
    A dismissible warning banner shown inside the main window when
    the license expires within WARNING_DAYS days.
    """

    def __init__(self, days_left: int, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background: rgba(210, 153, 34, 0.12); "
            "border-bottom: 1px solid rgba(210, 153, 34, 0.40); }"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        msg = QLabel(
            f"⚠  Your license expires in {days_left} day{'s' if days_left != 1 else ''}. "
            "Contact your provider to renew."
        )
        msg.setStyleSheet("color: #d29922; font-size: 12px; background: transparent; border: none;")

        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.setFixedHeight(24)
        dismiss_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #d29922; "
            "border: 1px solid rgba(210, 153, 34, 0.5); border-radius: 3px; "
            "font-size: 11px; padding: 2px 10px; }"
            "QPushButton:hover { border-color: #d29922; }"
        )
        dismiss_btn.clicked.connect(self.hide)

        layout.addWidget(msg)
        layout.addStretch()
        layout.addWidget(dismiss_btn)
