#!/usr/bin/env python3
"""
OptionsBacktest License Generator
==================================
Standalone PyQt5 app for issuing license keys.
Run: python3 licensing/keygen_app.py

Requires your private key file (private.key) — store it in Google Drive
or any secure location and browse to it here.
"""

import sys
import os
import json
import base64
import uuid
from datetime import date, timedelta
from pathlib import Path

# Allow running from project root or from licensing/ dir
_here = Path(__file__).parent
sys.path.insert(0, str(_here.parent))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox,
    QFrame, QTextEdit, QFileDialog, QMessageBox, QGroupBox,
    QFormLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QClipboard, QColor, QPalette

# ── Dark theme colours (matches main app) ────────────────────────────────────
BG        = "#0d1117"
BG2       = "#161b22"
BG3       = "#21262d"
BORDER    = "#30363d"
TEXT      = "#e6edf3"
TEXT_DIM  = "#8b949e"
ACCENT    = "#58a6ff"
GREEN     = "#3fb950"
RED       = "#f85149"
ORANGE    = "#d29922"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: -apple-system, 'Segoe UI', sans-serif;
    font-size: 13px;
}}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 10px;
    padding: 12px 10px 10px 10px;
    font-size: 12px;
    color: {TEXT_DIM};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: {TEXT_DIM};
}}
QLineEdit, QSpinBox, QComboBox {{
    background: {BG3};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 8px;
    color: {TEXT};
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background: {BG3};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
    color: {TEXT};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {BG3};
    border: none;
    width: 16px;
}}
QPushButton {{
    background: {BG3};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 16px;
    color: {TEXT};
}}
QPushButton:hover {{ background: #2d333b; border-color: {ACCENT}; }}
QPushButton:pressed {{ background: {BG}; }}
QPushButton#primary {{
    background: {ACCENT};
    color: #0d1117;
    border-color: {ACCENT};
    font-weight: bold;
}}
QPushButton#primary:hover {{ background: #79b8ff; }}
QPushButton#copy {{
    background: {BG3};
    color: {ACCENT};
    border-color: {ACCENT};
}}
QTextEdit {{
    background: {BG3};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px;
    color: {TEXT};
    font-family: 'Courier New', monospace;
    font-size: 11px;
}}
QLabel#dim {{ color: {TEXT_DIM}; font-size: 11px; }}
QLabel#status_ok  {{ color: {GREEN}; font-size: 11px; }}
QLabel#status_err {{ color: {RED};   font-size: 11px; }}
QLabel#status_warn {{ color: {ORANGE}; font-size: 11px; }}
QFrame#divider {{
    background: {BORDER};
    max-height: 1px;
}}
"""

# ── Private key helpers ───────────────────────────────────────────────────────

def _load_private_key(path: str):
    """Load Ed25519 private key from file. Returns key object or raises."""
    from cryptography.hazmat.primitives.serialization import load_der_private_key
    with open(path, 'rb') as f:
        content = f.read().strip()
    priv_bytes = base64.b64decode(content)
    return load_der_private_key(priv_bytes, password=None)


def _generate_keypair():
    """Generate a new Ed25519 key pair. Returns (priv_b64, pub_b64_der)."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PublicFormat, PrivateFormat, NoEncryption
    )
    key = Ed25519PrivateKey.generate()
    priv_b64 = base64.b64encode(
        key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
    ).decode()
    pub_b64 = base64.b64encode(
        key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    ).decode()
    return priv_b64, pub_b64


def _embed_public_key(pub_b64: str):
    """Write the public key into licensing/validator.py."""
    validator_path = _here / 'validator.py'
    with open(validator_path, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith('PUBLIC_KEY_B64 ='):
            lines[i] = f'PUBLIC_KEY_B64 = "{pub_b64}"\n'
            with open(validator_path, 'w') as f:
                f.writelines(lines)
            return True
    return False


# ── Main window ───────────────────────────────────────────────────────────────

class KeygenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptionsBacktest — License Generator")
        self.setMinimumWidth(560)
        self.setStyleSheet(STYLESHEET)

        self._private_key = None
        self._private_key_path = ""

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("License Generator")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {TEXT};")
        subtitle = QLabel("OptionsBacktest")
        subtitle.setStyleSheet(f"font-size: 12px; color: {TEXT_DIM};")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        divider = QFrame(); divider.setObjectName("divider")
        layout.addWidget(divider)

        # ── Step 1: Private key ──────────────────────────────────────────────
        key_group = QGroupBox("Step 1 — Private Key")
        key_layout = QVBoxLayout(key_group)
        key_layout.setSpacing(8)

        key_row = QHBoxLayout()
        self.key_path_edit = QLineEdit()
        self.key_path_edit.setPlaceholderText("Path to private.key (e.g. Google Drive/OptionsBacktest/private.key)")
        self.key_path_edit.setReadOnly(True)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_key)

        key_row.addWidget(self.key_path_edit)
        key_row.addWidget(browse_btn)
        key_layout.addLayout(key_row)

        self.key_status = QLabel("No key loaded")
        self.key_status.setObjectName("status_err")
        key_layout.addWidget(self.key_status)

        # First-time setup link
        setup_btn = QPushButton("Generate new key pair (first-time setup)")
        setup_btn.setStyleSheet(f"color: {ACCENT}; background: transparent; border: none; text-align: left; padding: 0;")
        setup_btn.setCursor(Qt.PointingHandCursor)
        setup_btn.clicked.connect(self._run_setup)
        key_layout.addWidget(setup_btn)

        layout.addWidget(key_group)

        # ── Step 2: Customer details ─────────────────────────────────────────
        form_group = QGroupBox("Step 2 — Customer Details")
        form_layout = QFormLayout(form_group)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(10)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("John Smith")
        self.name_edit.textChanged.connect(self._update_preview)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("john@example.com")

        duration_row = QHBoxLayout()
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        self.days_spin.setFixedWidth(70)
        self.days_spin.valueChanged.connect(self._update_preview)

        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["30 days", "60 days", "90 days", "6 months", "1 year", "Custom"])
        self.duration_combo.setFixedWidth(120)
        self.duration_combo.currentTextChanged.connect(self._preset_duration)

        self.expiry_label = QLabel()
        self.expiry_label.setObjectName("dim")

        duration_row.addWidget(self.duration_combo)
        duration_row.addWidget(self.days_spin)
        duration_row.addWidget(QLabel("days"))
        duration_row.addWidget(self.expiry_label)
        duration_row.addStretch()

        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Duration:", duration_row)

        layout.addWidget(form_group)

        # ── Generate button ──────────────────────────────────────────────────
        gen_btn = QPushButton("Generate License Key")
        gen_btn.setObjectName("primary")
        gen_btn.setMinimumHeight(36)
        gen_btn.clicked.connect(self._generate)
        layout.addWidget(gen_btn)

        # ── Output ───────────────────────────────────────────────────────────
        out_group = QGroupBox("License Key — copy and send to customer")
        out_layout = QVBoxLayout(out_group)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setFixedHeight(80)
        self.output_edit.setPlaceholderText("Generated key will appear here…")
        out_layout.addWidget(self.output_edit)

        btn_row = QHBoxLayout()
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.setObjectName("copy")
        copy_btn.clicked.connect(self._copy_key)
        self.copy_status = QLabel("")
        self.copy_status.setObjectName("status_ok")

        btn_row.addWidget(copy_btn)
        btn_row.addWidget(self.copy_status)
        btn_row.addStretch()
        out_layout.addLayout(btn_row)

        layout.addWidget(out_group)
        layout.addStretch()

        self._update_preview()

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _browse_key(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Private Key File", str(Path.home()),
            "Key files (*.key *.pem);;All files (*)"
        )
        if not path:
            return
        try:
            self._private_key = _load_private_key(path)
            self._private_key_path = path
            self.key_path_edit.setText(path)
            self.key_status.setText("✓ Private key loaded")
            self.key_status.setObjectName("status_ok")
            self.key_status.setStyleSheet(f"color: {GREEN}; font-size: 11px;")
        except Exception as e:
            self._private_key = None
            self.key_status.setText(f"✗ Failed to load key: {e}")
            self.key_status.setObjectName("status_err")
            self.key_status.setStyleSheet(f"color: {RED}; font-size: 11px;")

    def _preset_duration(self, text):
        presets = {
            "30 days": 30, "60 days": 60, "90 days": 90,
            "6 months": 183, "1 year": 365
        }
        if text in presets:
            self.days_spin.setValue(presets[text])

    def _update_preview(self):
        days = self.days_spin.value()
        exp = date.today() + timedelta(days=days)
        self.expiry_label.setText(f"→ expires {exp.strftime('%b %d, %Y')}")

    def _run_setup(self):
        """Generate a brand-new key pair and save private key to user-chosen location."""
        reply = QMessageBox.question(
            self, "Generate New Key Pair",
            "This will generate a NEW private/public key pair.\n\n"
            "⚠ All existing license keys will become invalid.\n\n"
            "Only do this the very first time, or if you have lost your private key.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Private Key", str(Path.home() / "private.key"),
            "Key files (*.key);;All files (*)"
        )
        if not save_path:
            return

        try:
            priv_b64, pub_b64 = _generate_keypair()

            # Save private key
            with open(save_path, 'w') as f:
                f.write(priv_b64)

            # Embed public key into validator.py
            ok = _embed_public_key(pub_b64)

            msg = (
                f"Key pair generated!\n\n"
                f"Private key saved to:\n{save_path}\n\n"
                f"Store this file in Google Drive or another secure location.\n"
                f"Never share it or include it in the app installer.\n\n"
            )
            if ok:
                msg += "✓ Public key has been embedded in licensing/validator.py.\nRebuild the app before distributing."
            else:
                msg += f"⚠ Could not auto-update validator.py.\nManually set PUBLIC_KEY_B64 = \"{pub_b64}\""

            QMessageBox.information(self, "Setup Complete", msg)

            # Auto-load the key
            self._private_key = _load_private_key(save_path)
            self._private_key_path = save_path
            self.key_path_edit.setText(save_path)
            self.key_status.setText("✓ Private key loaded")
            self.key_status.setStyleSheet(f"color: {GREEN}; font-size: 11px;")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Setup failed:\n{e}")

    def _generate(self):
        if self._private_key is None:
            QMessageBox.warning(self, "No Key", "Load your private key first (Step 1).")
            return

        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        days = self.days_spin.value()

        if not name:
            QMessageBox.warning(self, "Missing Field", "Enter the customer's name.")
            self.name_edit.setFocus()
            return
        if not email or '@' not in email:
            QMessageBox.warning(self, "Missing Field", "Enter a valid customer email.")
            self.email_edit.setFocus()
            return

        try:
            exp_date = (date.today() + timedelta(days=days)).isoformat()
            uid = str(uuid.uuid4())[:8].upper()

            payload = {"uid": uid, "name": name, "email": email, "exp": exp_date}
            payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
            sig_bytes = self._private_key.sign(payload_bytes)

            payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode().rstrip('=')
            sig_b64 = base64.urlsafe_b64encode(sig_bytes).decode().rstrip('=')

            key = f"OB-{payload_b64}.{sig_b64}"
            self.output_edit.setPlainText(key)
            self.copy_status.setText("")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Key generation failed:\n{e}")

    def _copy_key(self):
        key = self.output_edit.toPlainText().strip()
        if not key:
            return
        QApplication.clipboard().setText(key)
        self.copy_status.setText("Copied!")
        QTimer.singleShot(2000, lambda: self.copy_status.setText(""))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OptionsBacktest License Generator")
    font = QFont("-apple-system", 13)
    app.setFont(font)
    window = KeygenWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
