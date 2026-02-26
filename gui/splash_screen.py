"""
License Activation Splash Screen - Options Backtesting System
Shown on first launch or when the stored license is invalid/expired.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette


class SplashScreen(QDialog):
    """
    Branded license activation dialog.
    Shown before the main window when no valid license is stored.
    """

    def __init__(self, initial_message=None):
        super().__init__()
        self._activated = False
        self._setup_window()
        self._build_ui(initial_message)

    def _setup_window(self):
        self.setWindowTitle("Options Backtesting System")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setModal(True)

        # Dark background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#0d1117"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
            }
            QLabel {
                background-color: transparent;
                color: #f0f6fc;
            }
            QLabel#title {
                color: #58a6ff;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#subtitle {
                color: #8b949e;
                font-size: 11px;
            }
            QLabel#section {
                color: #8b949e;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QLabel#status_ok {
                color: #3fb950;
                font-size: 11px;
            }
            QLabel#status_err {
                color: #f85149;
                font-size: 11px;
            }
            QLabel#footer {
                color: #8b949e;
                font-size: 10px;
            }
            QLineEdit {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 14px;
                color: #f0f6fc;
                font-family: Consolas, monospace;
                font-size: 11px;
                selection-background-color: #58a6ff;
            }
            QLineEdit:focus {
                border-color: #58a6ff;
            }
            QPushButton#activate {
                background-color: #238636;
                color: #f0f6fc;
                border: 1px solid #2ea043;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#activate:hover {
                background-color: #2ea043;
            }
            QPushButton#activate:pressed {
                background-color: #1a7f37;
            }
            QPushButton#activate:disabled {
                background-color: #21262d;
                color: #8b949e;
                border-color: #30363d;
            }
            QFrame#divider {
                background-color: #21262d;
                border: none;
                max-height: 1px;
            }
            QFrame#card {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)

    def _build_ui(self, initial_message):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 36, 40, 32)
        outer.setSpacing(0)

        # --- Header ---
        dot = QLabel("◆")
        dot.setStyleSheet("color: #58a6ff; font-size: 18px; background: transparent;")

        title = QLabel("Options Backtesting")
        title.setObjectName("title")

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_row.addWidget(dot)
        title_row.addWidget(title)
        title_row.addStretch()

        version = QLabel("v3.0")
        version.setStyleSheet("color: #30363d; font-size: 11px; background: transparent;")
        title_row.addWidget(version)

        outer.addLayout(title_row)
        outer.addSpacing(6)

        subtitle = QLabel("Professional Options Strategy Research Platform")
        subtitle.setObjectName("subtitle")
        outer.addWidget(subtitle)

        outer.addSpacing(28)

        # --- Divider ---
        div1 = QFrame()
        div1.setObjectName("divider")
        div1.setFrameShape(QFrame.HLine)
        outer.addWidget(div1)

        outer.addSpacing(28)

        # --- License card ---
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        section_label = QLabel("LICENSE KEY")
        section_label.setObjectName("section")
        card_layout.addWidget(section_label)

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("OB-xxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxx")
        self._key_input.setMinimumHeight(42)
        self._key_input.returnPressed.connect(self._on_activate)
        card_layout.addWidget(self._key_input)

        activate_btn = QPushButton("Activate License")
        activate_btn.setObjectName("activate")
        activate_btn.setMinimumHeight(40)
        activate_btn.setCursor(Qt.PointingHandCursor)
        activate_btn.clicked.connect(self._on_activate)
        card_layout.addWidget(activate_btn)

        outer.addWidget(card)
        outer.addSpacing(16)

        # --- Status message ---
        self._status_label = QLabel("")
        self._status_label.setObjectName("status_err")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setWordWrap(True)
        outer.addWidget(self._status_label)

        # Show initial message (e.g. "License expired")
        if initial_message:
            self._set_status(initial_message, error=True)

        outer.addStretch()

        # --- Footer divider ---
        div2 = QFrame()
        div2.setObjectName("divider")
        div2.setFrameShape(QFrame.HLine)
        outer.addWidget(div2)

        outer.addSpacing(12)

        footer = QLabel(
            "Your license key is emailed upon purchase. "
            "Contact support if you need assistance."
        )
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignCenter)
        footer.setWordWrap(True)
        outer.addWidget(footer)

    def _set_status(self, message, error=True):
        self._status_label.setText(message)
        self._status_label.setObjectName("status_err" if error else "status_ok")
        # Force stylesheet re-evaluation
        self._status_label.setStyleSheet(
            f"color: {'#f85149' if error else '#3fb950'}; font-size: 11px; background: transparent;"
        )

    def _on_activate(self):
        from licensing.validator import validate_key, save_license

        key_str = self._key_input.text().strip()

        if not key_str:
            self._set_status("Please enter your license key.", error=True)
            return

        self._set_status("Validating...", error=False)
        self.repaint()

        is_valid, message, payload = validate_key(key_str)

        if is_valid:
            save_license(key_str)
            self._set_status(message, error=False)
            self._activated = True
            self.accept()
        else:
            self._set_status(message, error=True)
            self._key_input.setFocus()
            self._key_input.selectAll()

    def was_activated(self):
        """Returns True if a valid license was entered and saved."""
        return self._activated
