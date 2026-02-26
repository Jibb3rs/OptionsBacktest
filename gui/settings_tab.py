"""
Settings Tab - Configure defaults and themes
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import os

from .theme import C, FONT, FONT_MONO, style_canvas, style_text

class SettingsTab:
    def __init__(self, parent, main_window):
        self.frame = ttk.Frame(parent)
        self.main_window = main_window

        # Load current settings
        self.settings = self.load_settings()

        self.create_ui()

    def load_settings(self):
        """Load settings from file"""
        try:
            with open('config/settings.json', 'r') as f:
                return json.load(f)
        except:
            # Default settings
            return {
                "display": {
                    "theme": "dark",
                    "mae_mfe_format": "both",
                    "decimal_places": 2
                },
                "backtest": {
                    "default_capital": 100000,
                    "default_ticker": "SPX",
                    "risk_per_trade": 0.02
                },
                "strike_defaults": {
                    "method": "delta",
                    "short_put_delta": 0.16,
                    "long_put_delta": 0.08,
                    "short_call_delta": -0.16,
                    "long_call_delta": -0.08
                }
            }

    def create_ui(self):
        """Create settings interface"""

        # Scrollable container
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        style_canvas(canvas)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Enable trackpad scrolling
        from .scroll_helper import enable_scroll
        enable_scroll(canvas, scrollable)

        # Header
        header_frame = ttk.Frame(scrollable)
        header_frame.pack(fill='x', padx=25, pady=15)

        ttk.Label(header_frame, text="Settings", style='Title.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Customize defaults and appearance",
                 style='Subtitle.TLabel').pack(anchor='w', pady=(5, 0))

        ttk.Separator(scrollable, orient='horizontal').pack(fill='x', padx=25, pady=15)

        # === THEME SETTINGS ===
        theme_frame = ttk.LabelFrame(scrollable, text="Appearance & Theme", padding=20)
        theme_frame.pack(fill='x', padx=25, pady=10)

        ttk.Label(theme_frame, text="Code Editor Theme:",
                 style='Header.TLabel').grid(row=0, column=0, sticky='w', pady=10)

        self.theme_var = tk.StringVar(value=self.settings.get('display', {}).get('theme', 'dark'))

        themes = [
            ("Dark Mode (VS Code Style)", "dark"),
            ("Light Mode", "light"),
            ("Matrix (Green on Black)", "matrix"),
            ("Monokai", "monokai"),
            ("Solarized Dark", "solarized_dark"),
        ]

        for i, (label, value) in enumerate(themes):
            rb = ttk.Radiobutton(theme_frame, text=label, variable=self.theme_var, value=value)
            rb.grid(row=i+1, column=0, sticky='w', pady=3, padx=20)

        # Theme preview
        preview_frame = ttk.LabelFrame(theme_frame, text="Preview", padding=10)
        preview_frame.grid(row=0, column=1, rowspan=len(themes)+1, sticky='nsew', padx=20)

        ttk.Label(preview_frame, text="Sample code preview:").pack(anchor='w', pady=5)

        self.preview_text = tk.Text(preview_frame, height=10, width=40)
        style_text(self.preview_text, code=True)
        self.preview_text.pack(fill='both', expand=True)

        sample_code = '''def calculate_delta(price):
    """Calculate option delta"""
    if price > 0:
        return 0.16  # 84% win
    return 0.0'''

        self.preview_text.insert('1.0', sample_code)
        self.preview_text.config(state='disabled')

        # Bind theme change to preview update
        self.theme_var.trace('w', self.update_preview)
        self.update_preview()

        # MAE/MFE Format
        ttk.Label(theme_frame, text="MAE/MFE Display Format:",
                 style='Header.TLabel').grid(row=len(themes)+1, column=0, sticky='w', pady=(20, 5))

        self.mae_format_var = tk.StringVar(
            value=self.settings.get('display', {}).get('mae_mfe_format', 'both'))

        formats = [
            ("Show Both (% and $)", "both"),
            ("Percentage Only", "percentage"),
            ("Dollars Only", "dollars")
        ]

        for i, (label, value) in enumerate(formats):
            rb = ttk.Radiobutton(theme_frame, text=label,
                                variable=self.mae_format_var, value=value)
            rb.grid(row=len(themes)+2+i, column=0, sticky='w', pady=2, padx=20)

        theme_frame.columnconfigure(1, weight=1)

        # === DEFAULT VALUES ===
        defaults_frame = ttk.LabelFrame(scrollable, text="Default Values", padding=20)
        defaults_frame.pack(fill='x', padx=25, pady=10)

        ttk.Label(defaults_frame, text="Starting Capital:",
                 style='Header.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.capital_var = tk.IntVar(
            value=self.settings.get('backtest', {}).get('default_capital', 100000))
        ttk.Entry(defaults_frame, textvariable=self.capital_var, width=20).grid(
            row=0, column=1, sticky='w', padx=10, pady=8)

        ttk.Label(defaults_frame, text="Default Ticker:",
                 style='Header.TLabel').grid(row=1, column=0, sticky='w', pady=8)
        self.ticker_var = tk.StringVar(
            value=self.settings.get('backtest', {}).get('default_ticker', 'SPX'))
        ttk.Entry(defaults_frame, textvariable=self.ticker_var, width=20).grid(
            row=1, column=1, sticky='w', padx=10, pady=8)

        ttk.Label(defaults_frame, text="Risk Per Trade:",
                 style='Header.TLabel').grid(row=2, column=0, sticky='w', pady=8)
        self.risk_var = tk.DoubleVar(
            value=self.settings.get('backtest', {}).get('risk_per_trade', 0.02))
        ttk.Entry(defaults_frame, textvariable=self.risk_var, width=20).grid(
            row=2, column=1, sticky='w', padx=10, pady=8)
        ttk.Label(defaults_frame, text="(0.02 = 2% of capital per trade)",
                 style='Info.TLabel').grid(row=2, column=2, sticky='w', padx=5)

        # === STRIKE DEFAULTS ===
        strike_frame = ttk.LabelFrame(scrollable, text="Strike Selection Defaults", padding=20)
        strike_frame.pack(fill='x', padx=25, pady=10)

        ttk.Label(strike_frame, text="Default Strike Method:",
                 style='Header.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.strike_method_var = tk.StringVar(
            value=self.settings.get('strike_defaults', {}).get('method', 'delta'))
        methods = ['delta', 'fixed_points', 'percentage', 'atr']
        ttk.Combobox(strike_frame, textvariable=self.strike_method_var,
                    values=methods, state='readonly', width=17).grid(
            row=0, column=1, sticky='w', padx=10, pady=8)

        ttk.Label(strike_frame, text="Default Delta Values:",
                 style='Header.TLabel').grid(row=1, column=0, sticky='w', pady=(15, 5))

        delta_params = [
            ("Short Put Delta:", "short_put_delta", 0.16),
            ("Long Put Delta:", "long_put_delta", 0.08),
            ("Short Call Delta:", "short_call_delta", -0.16),
            ("Long Call Delta:", "long_call_delta", -0.08)
        ]

        self.delta_vars = {}
        for i, (label, key, default) in enumerate(delta_params):
            ttk.Label(strike_frame, text=label).grid(row=2+i, column=0, sticky='w', pady=5, padx=20)
            var = tk.DoubleVar(
                value=self.settings.get('strike_defaults', {}).get(key, default))
            ttk.Entry(strike_frame, textvariable=var, width=10).grid(
                row=2+i, column=1, sticky='w', padx=10, pady=5)
            self.delta_vars[key] = var

        # === ACTION BUTTONS ===
        button_frame = ttk.Frame(scrollable)
        button_frame.pack(fill='x', padx=25, pady=25)

        ttk.Button(button_frame, text="Save Settings",
                  command=self.save_settings).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Reset to Defaults",
                  command=self.reset_to_defaults).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Export Settings",
                  command=self.export_settings).pack(side='left', padx=5)

    def update_preview(self, *args):
        """Update theme preview"""
        theme = self.theme_var.get()

        themes = {
            'dark': ('#1e1e1e', '#d4d4d4'),
            'light': ('#ffffff', '#000000'),
            'matrix': ('#000000', '#00ff00'),
            'monokai': ('#272822', '#f8f8f2'),
            'solarized_dark': ('#002b36', '#839496'),
        }

        bg, fg = themes.get(theme, themes['dark'])

        self.preview_text.config(state='normal', bg=bg, fg=fg, insertbackground=fg)
        self.preview_text.config(state='disabled')

    def save_settings(self):
        """Save settings to file"""
        try:
            # Update settings dict
            self.settings['display']['theme'] = self.theme_var.get()
            self.settings['display']['mae_mfe_format'] = self.mae_format_var.get()

            self.settings['backtest']['default_capital'] = self.capital_var.get()
            self.settings['backtest']['default_ticker'] = self.ticker_var.get()
            self.settings['backtest']['risk_per_trade'] = self.risk_var.get()

            self.settings['strike_defaults']['method'] = self.strike_method_var.get()
            for key, var in self.delta_vars.items():
                self.settings['strike_defaults'][key] = var.get()

            # Save to file
            os.makedirs('config', exist_ok=True)
            with open('config/settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)

            messagebox.showinfo("Success",
                              "Settings saved successfully!\n\n"
                              "Theme changes will apply to new code generation windows.")

            self.main_window.update_status("Settings saved")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings",
                              "Reset all settings to defaults?\n\nThis cannot be undone."):
            # Reset to defaults
            self.theme_var.set('dark')
            self.mae_format_var.set('both')
            self.capital_var.set(100000)
            self.ticker_var.set('SPX')
            self.risk_var.set(0.02)
            self.strike_method_var.set('delta')

            self.delta_vars['short_put_delta'].set(0.16)
            self.delta_vars['long_put_delta'].set(0.08)
            self.delta_vars['short_call_delta'].set(-0.16)
            self.delta_vars['long_call_delta'].set(-0.08)

            self.main_window.update_status("Settings reset to defaults")

    def export_settings(self):
        """Export settings to JSON file"""
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="my_settings.json"
        )

        if file_path:
            try:
                # Get current settings
                current_settings = {
                    'display': {
                        'theme': self.theme_var.get(),
                        'mae_mfe_format': self.mae_format_var.get()
                    },
                    'backtest': {
                        'default_capital': self.capital_var.get(),
                        'default_ticker': self.ticker_var.get(),
                        'risk_per_trade': self.risk_var.get()
                    },
                    'strike_defaults': {
                        'method': self.strike_method_var.get(),
                        **{k: v.get() for k, v in self.delta_vars.items()}
                    }
                }

                with open(file_path, 'w') as f:
                    json.dump(current_settings, f, indent=2)

                messagebox.showinfo("Success", f"Settings exported to:\n{file_path}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
