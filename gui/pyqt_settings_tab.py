"""
PyQt5 Settings Tab - Application Settings
"""

import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QSpinBox, QPushButton, QFrame, QScrollArea,
    QMessageBox, QLineEdit, QGroupBox
)
from PyQt5.QtCore import Qt

from .pyqt_theme import C, apply_theme
from .pyqt_main_window import create_panel, create_form_row

# Constants for consistent form layout
LABEL_WIDTH = 180
INPUT_WIDTH = 150


class SettingsTab(QWidget):
    """Application settings tab"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        from core.paths import settings_file, presets_dir, output_dir
        self.settings_path = settings_file()
        self.presets_dir = presets_dir
        self.output_dir = output_dir

        self._load_settings()
        self._create_ui()

    def _load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_path, 'r') as f:
                self.settings = json.load(f)
        except:
            self.settings = {
                'theme': 'dark',
                'default_ticker': 'SPY',
                'default_capital': 100000,
                'default_expiry_days': 30,
                'output_folder': str(self.output_dir()),
                'auto_copy': True,
                'show_tooltips': True
            }

    def _save_settings(self):
        """Save settings to file"""
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            QMessageBox.information(self, "Saved", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def _create_ui(self):
        """Create the tab UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll)

        # Content widget
        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(12, 12, 12, 12)

        # Appearance Section
        appearance_panel, appearance_layout = create_panel("Appearance")
        layout.addWidget(appearance_panel)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'dark').title())
        self.theme_combo.setMinimumWidth(INPUT_WIDTH)
        self.theme_combo.setMaximumWidth(200)
        create_form_row("Theme:", self.theme_combo, appearance_layout, LABEL_WIDTH)

        # Tooltips checkbox with proper indent
        tooltip_row = QHBoxLayout()
        tooltip_spacer = QLabel("")
        tooltip_spacer.setFixedWidth(LABEL_WIDTH)
        tooltip_row.addWidget(tooltip_spacer)
        self.tooltips_check = QCheckBox("Show tooltips")
        self.tooltips_check.setChecked(self.settings.get('show_tooltips', True))
        tooltip_row.addWidget(self.tooltips_check)
        tooltip_row.addStretch()
        appearance_layout.addLayout(tooltip_row)

        # Default Values Section
        defaults_panel, defaults_layout = create_panel("Default Values")
        layout.addWidget(defaults_panel)

        self.default_ticker = QLineEdit(self.settings.get('default_ticker', 'SPY'))
        self.default_ticker.setMinimumWidth(INPUT_WIDTH)
        self.default_ticker.setMaximumWidth(200)
        create_form_row("Default Ticker:", self.default_ticker, defaults_layout, LABEL_WIDTH)

        self.default_capital = QSpinBox()
        self.default_capital.setRange(1000, 10000000)
        self.default_capital.setValue(self.settings.get('default_capital', 100000))
        self.default_capital.setSingleStep(10000)
        self.default_capital.setPrefix("$")
        self.default_capital.setMinimumWidth(INPUT_WIDTH)
        self.default_capital.setMaximumWidth(200)
        create_form_row("Default Capital:", self.default_capital, defaults_layout, LABEL_WIDTH)

        self.default_expiry = QSpinBox()
        self.default_expiry.setRange(1, 365)
        self.default_expiry.setValue(self.settings.get('default_expiry_days', 30))
        self.default_expiry.setSuffix(" days")
        self.default_expiry.setMinimumWidth(INPUT_WIDTH)
        self.default_expiry.setMaximumWidth(200)
        create_form_row("Default Expiry:", self.default_expiry, defaults_layout, LABEL_WIDTH)

        # Output Section
        output_panel, output_layout = create_panel("Output Settings")
        layout.addWidget(output_panel)

        output_row = QHBoxLayout()
        output_row.setSpacing(12)
        output_label = QLabel("Output Folder:")
        output_label.setFixedWidth(LABEL_WIDTH)
        output_row.addWidget(output_label)

        self.output_folder = QLineEdit(self.settings.get('output_folder', '~/Desktop/QC_Upload'))
        self.output_folder.setMinimumWidth(300)
        output_row.addWidget(self.output_folder, 1)

        browse_btn = QPushButton("Browse")
        browse_btn.setMinimumWidth(80)
        browse_btn.clicked.connect(self._browse_output)
        output_row.addWidget(browse_btn)

        output_layout.addLayout(output_row)

        # Auto copy checkbox with proper indent
        copy_row = QHBoxLayout()
        copy_spacer = QLabel("")
        copy_spacer.setFixedWidth(LABEL_WIDTH)
        copy_row.addWidget(copy_spacer)
        self.auto_copy = QCheckBox("Auto-copy code to clipboard")
        self.auto_copy.setChecked(self.settings.get('auto_copy', True))
        copy_row.addWidget(self.auto_copy)
        copy_row.addStretch()
        output_layout.addLayout(copy_row)

        # Presets Section
        presets_panel, presets_layout = create_panel("Strategy Presets")
        layout.addWidget(presets_panel)

        presets_info = QLabel(
            "Manage saved strategy configurations. Presets are stored in the 'presets' folder."
        )
        presets_info.setStyleSheet(f"color: {C['dim']}; padding: 4px 0;")
        presets_layout.addWidget(presets_info)

        preset_buttons = QHBoxLayout()
        open_presets_btn = QPushButton("Open Presets Folder")
        open_presets_btn.setMinimumWidth(150)
        open_presets_btn.clicked.connect(self._open_presets_folder)
        preset_buttons.addWidget(open_presets_btn)
        preset_buttons.addStretch()
        presets_layout.addLayout(preset_buttons)

        # About Section
        about_panel, about_layout = create_panel("About")
        layout.addWidget(about_panel)

        about_text = QLabel(
            "Options Backtesting System v4.0\n\n"
            "A comprehensive tool for backtesting options strategies\n"
            "using QuantConnect's historical data.\n\n"
            "Features:\n"
            "• 21 preset strategies + custom builder\n"
            "• 16 technical indicators\n"
            "• Advanced Greeks filters\n"
            "• Interactive ECharts visualizations\n"
            "• MAE/MFE analysis"
        )
        about_text.setStyleSheet(f"color: {C['dim']};")
        about_layout.addWidget(about_text)

        # Save button
        save_layout = QHBoxLayout()
        save_layout.addStretch()

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primary")
        save_btn.setMinimumWidth(150)
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self._apply_settings)
        save_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setMinimumWidth(150)
        reset_btn.setMinimumHeight(40)
        reset_btn.clicked.connect(self._reset_defaults)
        save_layout.addWidget(reset_btn)

        save_layout.addStretch()
        layout.addLayout(save_layout)

        # Add stretch
        layout.addStretch()

    def _browse_output(self):
        """Browse for output folder"""
        from PyQt5.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder.setText(folder)

    def _open_presets_folder(self):
        """Open presets folder"""
        import subprocess
        presets_path = self.presets_dir()

        try:
            if os.name == 'nt':
                os.startfile(presets_path)
            else:
                subprocess.call(['open', presets_path])
        except:
            QMessageBox.information(self, "Presets", f"Folder: {presets_path}")

    def _apply_settings(self):
        """Apply and save settings"""
        self.settings = {
            'theme': self.theme_combo.currentText().lower(),
            'show_tooltips': self.tooltips_check.isChecked(),
            'default_ticker': self.default_ticker.text(),
            'default_capital': self.default_capital.value(),
            'default_expiry_days': self.default_expiry.value(),
            'output_folder': self.output_folder.text(),
            'auto_copy': self.auto_copy.isChecked()
        }

        # Apply theme at runtime
        apply_theme(self.settings['theme'])

        self._save_settings()

    def _reset_defaults(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.theme_combo.setCurrentText("Dark")
            self.tooltips_check.setChecked(True)
            self.default_ticker.setText("SPY")
            self.default_capital.setValue(100000)
            self.default_expiry.setValue(30)
            self.output_folder.setText("~/Desktop/QC_Upload")
            self.auto_copy.setChecked(True)
