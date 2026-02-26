"""
PyQt5 Code Popup - Display Generated QuantConnect Code
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QApplication, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .pyqt_theme import C, FONT_FAMILY


class CodePopup(QDialog):
    """Dialog to display and copy generated code"""

    def __init__(self, code, parent=None):
        super().__init__(parent)
        self.code = code

        self.setWindowTitle("Generated QuantConnect Code")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)

        self._create_ui()

    def _create_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Generated QuantConnect Algorithm")
        header.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {C['accent']};
        """)
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(
            "Copy this code and paste it into QuantConnect's Algorithm Editor.\n"
            "Click 'Backtest' in QuantConnect to run the backtest."
        )
        instructions.setStyleSheet(f"color: {C['dim']};")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Code display
        self.code_display = QTextEdit()
        self.code_display.setPlainText(self.code)
        self.code_display.setReadOnly(True)
        self.code_display.setFont(QFont(FONT_FAMILY, 10))
        self.code_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {C['bg']};
                border: 1px solid {C['card_border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        layout.addWidget(self.code_display)

        # Line count
        line_count = len(self.code.split('\n'))
        count_label = QLabel(f"{line_count} lines of code")
        count_label.setStyleSheet(f"color: {C['dim']};")
        layout.addWidget(count_label)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # Copy button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.setObjectName("primary")
        copy_btn.setMinimumWidth(150)
        copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_btn)

        # Save button
        save_btn = QPushButton("Save to File")
        save_btn.setMinimumWidth(150)
        save_btn.clicked.connect(self._save_to_file)
        button_layout.addWidget(save_btn)

        button_layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _copy_to_clipboard(self):
        """Copy code to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code)
        QMessageBox.information(self, "Copied",
            "Code copied to clipboard!\n\n"
            "Now paste it into QuantConnect's Algorithm Editor.")

    def _save_to_file(self):
        """Save code to file"""
        # Default path
        default_path = os.path.expanduser("~/Desktop/QC_Upload")
        os.makedirs(default_path, exist_ok=True)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Algorithm",
            os.path.join(default_path, "main.py"),
            "Python Files (*.py);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.code)
                QMessageBox.information(self, "Saved",
                    f"Code saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                    f"Failed to save file: {str(e)}")
