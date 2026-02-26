"""
Advanced Filters Tab - Tkinter Version WITH VIX AND TECHNICAL INDICATORS
"""

import tkinter as tk
from tkinter import ttk
import json
from .theme import C, FONT, style_canvas, style_listbox

class AdvancedTab:
    def __init__(self, notebook, main_window):
        self.main_window = main_window

        # Create main frame
        self.frame = ttk.Frame(notebook)

        # Create scrollable canvas
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        style_canvas(canvas)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable trackpad scrolling
        from .scroll_helper import enable_scroll
        enable_scroll(canvas, scrollable_frame)

        # Title
        title = ttk.Label(scrollable_frame, text="Advanced Filters",
                         style='Title.TLabel')
        title.pack(pady=20)

        subtitle = ttk.Label(scrollable_frame,
                            text="Professional-grade entry filters with VIX + 16 Technical Indicators",
                            style='Subtitle.TLabel')
        subtitle.pack(pady=(0, 20))

        # Container for all sections
        container = ttk.Frame(scrollable_frame)
        container.pack(fill='both', expand=True, padx=40, pady=10)

        # Load indicators metadata
        self.indicators_metadata = self.load_indicators_metadata()

        # Store indicator widgets
        self.indicator_widgets = {}

        # Create sections
        self.create_entry_filters(container)
        self.create_technical_indicators(container)
        self.create_advanced_greeks_section(container)
        self.create_expiration_section(container)
        self.create_risk_management(container)

    def load_indicators_metadata(self):
        """Load indicators from JSON file"""
        try:
            with open('config/indicators.json', 'r') as f:
                return json.load(f)
        except:
            # Fallback if file not found
            return {
                "RSI": {"name": "RSI", "category": "momentum", "desc": "Overbought >70, Oversold <30"},
                "MACD": {"name": "MACD", "category": "momentum", "desc": "Trend-following momentum"},
                "SMA": {"name": "SMA", "category": "trend", "desc": "Simple moving average"},
                "EMA": {"name": "EMA", "category": "trend", "desc": "Exponential moving average"}
            }

    def create_entry_filters(self, parent):
        """Entry Filters Section"""
        frame = ttk.LabelFrame(parent, text="Entry Filters", padding=15)
        frame.pack(fill='x', pady=10)

        # VIX Filter (NEW - TOP OF LIST) (Recommended)
        vix_frame = ttk.Frame(frame)
        vix_frame.pack(fill='x', pady=5)

        self.vix_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(vix_frame, text="VIX Filter (Fear/Greed) (Recommended)",
                       variable=self.vix_enabled).pack(side='left')

        ttk.Label(vix_frame, text="Min:").pack(side='left', padx=(20, 5))
        self.vix_min = tk.DoubleVar(value=15.0)
        ttk.Spinbox(vix_frame, from_=5, to=50, increment=0.5,
                   textvariable=self.vix_min, width=8).pack(side='left')

        ttk.Label(vix_frame, text="  Max:").pack(side='left', padx=(10, 5))
        self.vix_max = tk.DoubleVar(value=50.0)
        ttk.Spinbox(vix_frame, from_=5, to=80, increment=0.5,
                   textvariable=self.vix_max, width=8).pack(side='left')

        # VIX interpretation guide
        vix_help = ttk.Label(vix_frame,
                            text="  (<15=Calm  15-25=Normal  >25=Fear)",
                            font=(FONT, 9), foreground=C["dim"])
        vix_help.pack(side='left', padx=(10, 0))

        # Separator
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)

        # IV Rank Filter
        iv_frame = ttk.Frame(frame)
        iv_frame.pack(fill='x', pady=5)

        self.iv_rank_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(iv_frame, text="IV Rank Filter",
                       variable=self.iv_rank_enabled).pack(side='left')

        ttk.Label(iv_frame, text="Min:").pack(side='left', padx=(20, 5))
        self.iv_rank_min = tk.IntVar(value=50)
        ttk.Spinbox(iv_frame, from_=0, to=100, textvariable=self.iv_rank_min,
                   width=8).pack(side='left')

        ttk.Label(iv_frame, text="%   Max:").pack(side='left', padx=(10, 5))
        self.iv_rank_max = tk.IntVar(value=100)
        ttk.Spinbox(iv_frame, from_=0, to=100, textvariable=self.iv_rank_max,
                   width=8).pack(side='left')
        ttk.Label(iv_frame, text="%").pack(side='left', padx=(5, 0))

        # Market Profile Filter
        mp_frame = ttk.Frame(frame)
        mp_frame.pack(fill='x', pady=5)

        self.market_profile_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(mp_frame, text="Market Profile (TPO)",
                       variable=self.market_profile_enabled).pack(side='left')

        ttk.Label(mp_frame, text="Signal:").pack(side='left', padx=(20, 5))
        self.market_profile_signal = tk.StringVar(value='poc')
        ttk.Combobox(mp_frame, textvariable=self.market_profile_signal,
                    values=['poc', 'val', 'vah'], width=10,
                    state='readonly').pack(side='left')

        ttk.Label(mp_frame, text="Lookback:").pack(side='left', padx=(10, 5))
        self.market_profile_lookback = tk.IntVar(value=20)
        ttk.Spinbox(mp_frame, from_=5, to=100,
                   textvariable=self.market_profile_lookback,
                   width=8).pack(side='left')
        ttk.Label(mp_frame, text="days").pack(side='left', padx=(5, 0))

        # Volatility Regime Filter
        vol_frame = ttk.Frame(frame)
        vol_frame.pack(fill='x', pady=5)

        self.vol_regime_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(vol_frame, text="Volatility Regime",
                       variable=self.vol_regime_enabled).pack(side='left')

        ttk.Label(vol_frame, text="Type:").pack(side='left', padx=(20, 5))
        self.vol_regime_type = tk.StringVar(value='any')
        ttk.Combobox(vol_frame, textvariable=self.vol_regime_type,
                    values=['any', 'low', 'medium', 'high'], width=10,
                    state='readonly').pack(side='left')

        # Earnings Filter
        earnings_frame = ttk.Frame(frame)
        earnings_frame.pack(fill='x', pady=5)

        self.earnings_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(earnings_frame, text="Earnings Filter",
                       variable=self.earnings_enabled).pack(side='left')

        ttk.Label(earnings_frame, text="Buffer:").pack(side='left', padx=(20, 5))
        self.earnings_buffer_days = tk.IntVar(value=7)
        ttk.Spinbox(earnings_frame, from_=1, to=30,
                   textvariable=self.earnings_buffer_days,
                   width=8).pack(side='left')
        ttk.Label(earnings_frame, text="days before/after").pack(side='left', padx=(5, 0))

        # Multi-Timeframe Filter
        mtf_frame = ttk.Frame(frame)
        mtf_frame.pack(fill='x', pady=5)

        self.mtf_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(mtf_frame, text="Multi-Timeframe Confirmation",
                       variable=self.mtf_enabled,
                       command=self.toggle_mtf_config).pack(side='left')

        self.mtf_config_btn = ttk.Button(mtf_frame, text="Configure Timeframes",
                                        command=self.configure_multitimeframe,
                                        state='disabled', width=20)
        self.mtf_config_btn.pack(side='left', padx=(20, 0))

        # Store MTF configuration
        self.mtf_timeframes = []
        self.mtf_require_all = tk.BooleanVar(value=True)

        # VIX usage examples
        example_frame = ttk.Frame(frame)
        example_frame.pack(fill='x', pady=(15, 5))

        examples = ttk.Label(example_frame,
                            text="VIX Examples:\n" +
                                 "  - Sell premium (IC, Strangles): VIX 15-50 (any elevated volatility)\n" +
                                 "  - Buy options (Long Strangle): VIX 10-20 (before volatility spike)\n" +
                                 "  - High fear plays: VIX 25-80 (crisis/panic selling)",
                            font=(FONT, 9), foreground=C["accent"], justify='left')
        examples.pack(anchor='w')

    def create_technical_indicators(self, parent):
        """Technical Indicators Section - NEW"""
        frame = ttk.LabelFrame(parent, text="Technical Indicators (16 Available)", padding=15)
        frame.pack(fill='x', pady=10)

        # Info label
        info = ttk.Label(frame,
                        text="Enable indicators to filter trade entries. All enabled indicators must pass for trade to execute.",
                        font=(FONT, 10), foreground=C["accent"])
        info.pack(anchor='w', pady=(0, 10))

        # Group indicators by category
        categories = {
            'momentum': ('Momentum', []),
            'trend': ('Trend', []),
            'volatility': ('Volatility', []),
            'volume': ('Volume', [])
        }

        # Sort indicators into categories
        for key, meta in self.indicators_metadata.items():
            category = meta.get('category', 'momentum')
            if category in categories:
                categories[category][1].append((key, meta))

        # Create collapsible sections for each category
        for category, (label, indicators) in categories.items():
            if not indicators:
                continue

            # Category header frame
            cat_frame = ttk.LabelFrame(frame, text=label, padding=10)
            cat_frame.pack(fill='x', pady=5)

            for indicator_key, meta in indicators:
                self.create_indicator_widget(cat_frame, indicator_key, meta)

        # Quick actions
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', pady=(15, 0))

        ttk.Button(action_frame, text="Enable All",
                  command=self.enable_all_indicators).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Disable All",
                  command=self.disable_all_indicators).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Load Preset",
                  command=self.load_indicator_preset).pack(side='left', padx=5)

    def create_indicator_widget(self, parent, key, meta):
        """Create widget for a single indicator"""
        container = ttk.Frame(parent)
        container.pack(fill='x', pady=3)

        # Store widget references
        self.indicator_widgets[key] = {}

        # Checkbox
        enabled_var = tk.BooleanVar(value=False)
        self.indicator_widgets[key]['enabled'] = enabled_var

        cb = ttk.Checkbutton(container, text=meta['name'],
                            variable=enabled_var,
                            command=lambda k=key: self.toggle_indicator_config(k))
        cb.pack(side='left')

        # Description
        desc_label = ttk.Label(container, text=f"  ({meta['desc']})",
                              font=(FONT, 9), foreground=C["dim"])
        desc_label.pack(side='left')

        # Config button (initially disabled)
        config_btn = ttk.Button(container, text="Configure",
                               command=lambda k=key: self.configure_indicator(k),
                               state='disabled', width=12)
        config_btn.pack(side='right', padx=5)
        self.indicator_widgets[key]['config_btn'] = config_btn

        # Store default parameters
        self.indicator_widgets[key]['params'] = self.get_default_params(key)

    def toggle_indicator_config(self, key):
        """Enable/disable config button when checkbox toggled"""
        enabled = self.indicator_widgets[key]['enabled'].get()
        state = 'normal' if enabled else 'disabled'
        self.indicator_widgets[key]['config_btn'].config(state=state)

    def get_default_params(self, key):
        """Get default parameters for indicator"""
        defaults = {
            'RSI': {'period': 14, 'condition': 'oversold', 'oversold': 30, 'overbought': 70},
            'MACD': {'fast': 12, 'slow': 26, 'signal': 9, 'condition': 'bullish_cross'},
            'STOCHASTIC': {'period': 14, 'k_smooth': 3, 'condition': 'oversold', 'oversold': 20, 'overbought': 80},
            'CCI': {'period': 20, 'condition': 'oversold', 'oversold': -100, 'overbought': 100},
            'WILLIAMSR': {'period': 14, 'condition': 'oversold', 'oversold': -80, 'overbought': -20},
            'ATR': {'period': 14, 'condition': 'high', 'threshold': 1.5},
            'BBANDS': {'period': 20, 'std_dev': 2, 'condition': 'below_lower'},
            'KELTNER': {'period': 20, 'atr_mult': 2, 'condition': 'below_lower'},
            'SMA': {'period': 50, 'condition': 'above'},
            'EMA': {'period': 50, 'condition': 'above'},
            'ADX': {'period': 14, 'condition': 'strong', 'threshold': 25},
            'SUPERTREND': {'period': 10, 'multiplier': 3, 'condition': 'bullish'},
            'VWAP': {'condition': 'above'},
            'OBV': {'condition': 'rising', 'period': 20},
            'MFI': {'period': 14, 'condition': 'oversold', 'oversold': 20, 'overbought': 80}
        }
        return defaults.get(key, {})

    def configure_indicator(self, key):
        """Open configuration dialog for indicator"""
        popup = tk.Toplevel(self.main_window.root)
        popup.configure(bg=C["bg"])
        popup.title(f"Configure {self.indicators_metadata[key]['name']}")
        popup.geometry("450x400")
        popup.transient(self.main_window.root)
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 225
        y = (popup.winfo_screenheight() // 2) - 200
        popup.geometry(f'+{x}+{y}')

        # Main frame
        main_frame = ttk.Frame(popup, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Title
        ttk.Label(main_frame,
                 text=f"{self.indicators_metadata[key]['name']} Configuration",
                 font=(FONT, 14, 'bold')).pack(pady=(0, 10))

        ttk.Label(main_frame,
                 text=self.indicators_metadata[key]['desc'],
                 font=(FONT, 10), foreground=C["dim"]).pack(pady=(0, 15))

        # Parameter inputs
        param_frame = ttk.Frame(main_frame)
        param_frame.pack(fill='both', expand=True, pady=10)

        param_widgets = {}
        current_params = self.indicator_widgets[key]['params']

        # Create inputs based on indicator type
        row = 0
        for param_key, default_value in current_params.items():
            ttk.Label(param_frame, text=f"{param_key.replace('_', ' ').title()}:").grid(
                row=row, column=0, sticky='w', pady=5, padx=(0, 10))

            if isinstance(default_value, bool):
                var = tk.BooleanVar(value=default_value)
                ttk.Checkbutton(param_frame, variable=var).grid(row=row, column=1, sticky='w')
                param_widgets[param_key] = var
            elif isinstance(default_value, (int, float)):
                var = tk.DoubleVar(value=default_value)
                ttk.Entry(param_frame, textvariable=var, width=15).grid(row=row, column=1, sticky='w')
                param_widgets[param_key] = var
            else:  # String (condition dropdown)
                var = tk.StringVar(value=default_value)
                conditions = self.get_conditions_for_indicator(key, param_key)
                ttk.Combobox(param_frame, textvariable=var, values=conditions,
                            state='readonly', width=15).grid(row=row, column=1, sticky='w')
                param_widgets[param_key] = var

            row += 1

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))

        def save_config():
            # Update parameters
            for param_key, var in param_widgets.items():
                self.indicator_widgets[key]['params'][param_key] = var.get()
            popup.destroy()

        ttk.Button(button_frame, text="Save", command=save_config).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side='left', padx=5)

    def get_conditions_for_indicator(self, key, param_key):
        """Get available conditions for indicator"""
        if param_key != 'condition':
            return []

        conditions_map = {
            'RSI': ['oversold', 'overbought', 'neutral'],
            'MACD': ['bullish_cross', 'bearish_cross', 'positive', 'negative'],
            'STOCHASTIC': ['oversold', 'overbought', 'neutral'],
            'CCI': ['oversold', 'overbought', 'neutral'],
            'WILLIAMSR': ['oversold', 'overbought', 'neutral'],
            'ATR': ['high', 'low'],
            'BBANDS': ['below_lower', 'above_upper', 'inside_bands', 'near_middle'],
            'KELTNER': ['below_lower', 'above_upper', 'inside_bands'],
            'SMA': ['above', 'below', 'cross_above', 'cross_below'],
            'EMA': ['above', 'below', 'cross_above', 'cross_below'],
            'ADX': ['strong', 'weak'],
            'SUPERTREND': ['bullish', 'bearish'],
            'VWAP': ['above', 'below'],
            'OBV': ['rising', 'falling'],
            'MFI': ['oversold', 'overbought', 'neutral']
        }
        return conditions_map.get(key, [])

    def enable_all_indicators(self):
        """Enable all indicators"""
        for key, widgets in self.indicator_widgets.items():
            widgets['enabled'].set(True)
            widgets['config_btn'].config(state='normal')
        self.main_window.update_status("All indicators enabled")

    def disable_all_indicators(self):
        """Disable all indicators"""
        for key, widgets in self.indicator_widgets.items():
            widgets['enabled'].set(False)
            widgets['config_btn'].config(state='disabled')
        self.main_window.update_status("All indicators disabled")

    def load_indicator_preset(self):
        """Load a preset combination of indicators"""
        popup = tk.Toplevel(self.main_window.root)
        popup.configure(bg=C["bg"])
        popup.title("Load Indicator Preset")
        popup.geometry("500x400")
        popup.transient(self.main_window.root)
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 250
        y = (popup.winfo_screenheight() // 2) - 200
        popup.geometry(f'+{x}+{y}')

        main_frame = ttk.Frame(popup, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Select Preset Configuration",
                 font=(FONT, 14, 'bold')).pack(pady=(0, 20))

        presets = {
            "Conservative (High Win %)": ['RSI', 'SMA', 'ADX'],
            "Momentum Trader": ['RSI', 'MACD', 'STOCHASTIC', 'ADX'],
            "Trend Follower": ['SMA', 'EMA', 'ADX', 'SUPERTREND'],
            "Volatility Trader": ['ATR', 'BBANDS', 'KELTNER'],
            "Volume Focus": ['VWAP', 'OBV', 'MFI'],
            "Complete Strategy": ['RSI', 'MACD', 'SMA', 'BBANDS', 'ADX', 'VWAP']
        }

        for preset_name, indicators in presets.items():
            def apply_preset(inds=indicators, name=preset_name):
                self.disable_all_indicators()
                for ind_key in inds:
                    if ind_key in self.indicator_widgets:
                        self.indicator_widgets[ind_key]['enabled'].set(True)
                        self.indicator_widgets[ind_key]['config_btn'].config(state='normal')
                self.main_window.update_status(f"Loaded preset: {name}")
                popup.destroy()

            ttk.Button(main_frame, text=f"{preset_name}",
                      command=apply_preset).pack(fill='x', pady=5)

        ttk.Button(main_frame, text="Cancel", command=popup.destroy).pack(pady=(15, 0))

    def toggle_mtf_config(self):
        """Enable/disable multi-timeframe config button"""
        state = 'normal' if self.mtf_enabled.get() else 'disabled'
        self.mtf_config_btn.config(state=state)

    def create_advanced_greeks_section(self, parent):
        """Advanced Greeks Filters Section - Contract-level filtering"""
        frame = ttk.LabelFrame(parent, text="Advanced Greeks Filters (Contract-Level)", padding=15)
        frame.pack(fill='x', pady=10)

        # Info label
        info = ttk.Label(frame,
                        text="Filter individual option contracts by higher-order Greeks at entry time.\n"
                             "Different from Portfolio Greeks Limits - these filter contracts BEFORE selection.",
                        font=(FONT, 9), foreground=C["accent"])
        info.pack(anchor='w', pady=(0, 10))

        # Second-Order Greeks Header
        ttk.Label(frame, text="Second-Order Greeks", font=(FONT, 10, 'bold')).pack(anchor='w', pady=(5, 5))

        # Gamma Filter (most important)
        gamma_frame = ttk.Frame(frame)
        gamma_frame.pack(fill='x', pady=3)

        self.gamma_filter_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(gamma_frame, text="Max Gamma",
                       variable=self.gamma_filter_enabled).pack(side='left')

        ttk.Label(gamma_frame, text="Threshold:").pack(side='left', padx=(20, 5))
        self.max_gamma = tk.DoubleVar(value=0.05)
        ttk.Spinbox(gamma_frame, from_=0.001, to=1.0, increment=0.005,
                   textvariable=self.max_gamma, width=10).pack(side='left')

        ttk.Label(gamma_frame, text="  (avoid high-gamma ATM zones)",
                 font=(FONT, 9), foreground=C["dim"]).pack(side='left', padx=(10, 0))

        # Vanna Filter
        vanna_frame = ttk.Frame(frame)
        vanna_frame.pack(fill='x', pady=3)

        self.vanna_filter_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(vanna_frame, text="Max Vanna (dDelta/dIV)",
                       variable=self.vanna_filter_enabled).pack(side='left')

        ttk.Label(vanna_frame, text="Threshold:").pack(side='left', padx=(20, 5))
        self.max_vanna = tk.DoubleVar(value=0.10)
        ttk.Spinbox(vanna_frame, from_=0.01, to=1.0, increment=0.01,
                   textvariable=self.max_vanna, width=10).pack(side='left')

        # Charm Filter
        charm_frame = ttk.Frame(frame)
        charm_frame.pack(fill='x', pady=3)

        self.charm_filter_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(charm_frame, text="Max Charm (dDelta/dTime)",
                       variable=self.charm_filter_enabled).pack(side='left')

        ttk.Label(charm_frame, text="Threshold:").pack(side='left', padx=(20, 5))
        self.max_charm = tk.DoubleVar(value=0.02)
        ttk.Spinbox(charm_frame, from_=0.001, to=0.5, increment=0.005,
                   textvariable=self.max_charm, width=10).pack(side='left')

        # Vomma Filter
        vomma_frame = ttk.Frame(frame)
        vomma_frame.pack(fill='x', pady=3)

        self.vomma_filter_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(vomma_frame, text="Max Vomma (dVega/dIV)",
                       variable=self.vomma_filter_enabled).pack(side='left')

        ttk.Label(vomma_frame, text="Threshold:").pack(side='left', padx=(20, 5))
        self.max_vomma = tk.DoubleVar(value=0.10)
        ttk.Spinbox(vomma_frame, from_=0.01, to=1.0, increment=0.01,
                   textvariable=self.max_vomma, width=10).pack(side='left')

        # Veta Filter
        veta_frame = ttk.Frame(frame)
        veta_frame.pack(fill='x', pady=3)

        self.veta_filter_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(veta_frame, text="Max Veta (dVega/dTime)",
                       variable=self.veta_filter_enabled).pack(side='left')

        ttk.Label(veta_frame, text="Threshold:").pack(side='left', padx=(20, 5))
        self.max_veta = tk.DoubleVar(value=0.05)
        ttk.Spinbox(veta_frame, from_=0.001, to=0.5, increment=0.005,
                   textvariable=self.max_veta, width=10).pack(side='left')

        # Separator for third-order Greeks
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)

        # Third-Order Greeks Header
        ttk.Label(frame, text="Third-Order Greeks (Advanced)", font=(FONT, 10, 'bold')).pack(anchor='w', pady=(0, 5))

        # Speed Filter
        speed_frame = ttk.Frame(frame)
        speed_frame.pack(fill='x', pady=3)

        self.speed_filter_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(speed_frame, text="Max Speed (dGamma/dSpot)",
                       variable=self.speed_filter_enabled).pack(side='left')

        ttk.Label(speed_frame, text="Threshold:").pack(side='left', padx=(20, 5))
        self.max_speed = tk.DoubleVar(value=0.001)
        ttk.Spinbox(speed_frame, from_=0.0001, to=0.1, increment=0.0005,
                   textvariable=self.max_speed, width=10).pack(side='left')

        # Zomma Filter
        zomma_frame = ttk.Frame(frame)
        zomma_frame.pack(fill='x', pady=3)

        self.zomma_filter_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(zomma_frame, text="Max Zomma (dGamma/dIV)",
                       variable=self.zomma_filter_enabled).pack(side='left')

        ttk.Label(zomma_frame, text="Threshold:").pack(side='left', padx=(20, 5))
        self.max_zomma = tk.DoubleVar(value=0.001)
        ttk.Spinbox(zomma_frame, from_=0.0001, to=0.1, increment=0.0005,
                   textvariable=self.max_zomma, width=10).pack(side='left')

        # Color Filter
        color_frame = ttk.Frame(frame)
        color_frame.pack(fill='x', pady=3)

        self.color_filter_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(color_frame, text="Max Color (dGamma/dTime)",
                       variable=self.color_filter_enabled).pack(side='left')

        ttk.Label(color_frame, text="Threshold:").pack(side='left', padx=(20, 5))
        self.max_color = tk.DoubleVar(value=0.001)
        ttk.Spinbox(color_frame, from_=0.0001, to=0.1, increment=0.0005,
                   textvariable=self.max_color, width=10).pack(side='left')

        # Usage note
        note_frame = ttk.Frame(frame)
        note_frame.pack(fill='x', pady=(15, 5))

        note = ttk.Label(note_frame,
                        text="Tip: For Iron Condors, use Max Gamma to avoid high-gamma zones near ATM.\n"
                             "These filters apply to each leg's contract during strike selection.",
                        font=(FONT, 9), foreground=C["dim"], justify='left')
        note.pack(anchor='w')

    def configure_multitimeframe(self):
        """Configure multi-timeframe alignment"""
        popup = tk.Toplevel(self.main_window.root)
        popup.configure(bg=C["bg"])
        popup.title("Multi-Timeframe Configuration")
        popup.geometry("600x500")
        popup.transient(self.main_window.root)
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 300
        y = (popup.winfo_screenheight() // 2) - 250
        popup.geometry(f'+{x}+{y}')

        main_frame = ttk.Frame(popup, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Multi-Timeframe Configuration",
                 font=(FONT, 14, 'bold')).pack(pady=(0, 10))

        ttk.Label(main_frame, text="Require alignment across multiple timeframes for trade entry",
                 font=(FONT, 10), foreground=C["dim"]).pack(pady=(0, 15))

        # Require all checkbox
        ttk.Checkbutton(main_frame, text="Require ALL timeframes to agree (AND logic)",
                       variable=self.mtf_require_all).pack(anchor='w', pady=(0, 15))

        # Timeframe list
        ttk.Label(main_frame, text="Configured Timeframes:", font=(FONT, 11, 'bold')).pack(anchor='w')

        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill='both', expand=True, pady=10)

        # Scrollable listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        timeframe_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
        style_listbox(timeframe_list)
        timeframe_list.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=timeframe_list.yview)

        def refresh_list():
            timeframe_list.delete(0, tk.END)
            for i, tf in enumerate(self.mtf_timeframes):
                timeframe_list.insert(tk.END,
                    f"{i+1}. {tf['resolution']} {tf['indicator']} - {tf['condition']}")

        refresh_list()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))

        def add_timeframe():
            # Simple add dialog
            add_popup = tk.Toplevel(popup)
            add_popup.configure(bg=C["bg"])
            add_popup.title("Add Timeframe")
            add_popup.geometry("400x300")
            add_popup.transient(popup)
            add_popup.grab_set()

            add_frame = ttk.Frame(add_popup, padding=20)
            add_frame.pack(fill='both', expand=True)

            ttk.Label(add_frame, text="Resolution:").grid(row=0, column=0, sticky='w', pady=5)
            resolution_var = tk.StringVar(value='Daily')
            ttk.Combobox(add_frame, textvariable=resolution_var,
                        values=['Daily', 'Hour', 'Minute'], state='readonly',
                        width=15).grid(row=0, column=1, sticky='w', pady=5)

            ttk.Label(add_frame, text="Indicator:").grid(row=1, column=0, sticky='w', pady=5)
            indicator_var = tk.StringVar(value='SMA')
            ttk.Combobox(add_frame, textvariable=indicator_var,
                        values=['SMA', 'EMA', 'RSI', 'MACD', 'ADX'], state='readonly',
                        width=15).grid(row=1, column=1, sticky='w', pady=5)

            ttk.Label(add_frame, text="Condition:").grid(row=2, column=0, sticky='w', pady=5)
            condition_var = tk.StringVar(value='above')
            ttk.Combobox(add_frame, textvariable=condition_var,
                        values=['above', 'below', 'bullish', 'bearish', 'oversold', 'overbought', 'strong', 'weak'],
                        state='readonly', width=15).grid(row=2, column=1, sticky='w', pady=5)

            ttk.Label(add_frame, text="Period (if applicable):").grid(row=3, column=0, sticky='w', pady=5)
            period_var = tk.IntVar(value=50)
            ttk.Entry(add_frame, textvariable=period_var, width=15).grid(row=3, column=1, sticky='w', pady=5)

            def save_timeframe():
                self.mtf_timeframes.append({
                    'resolution': resolution_var.get(),
                    'indicator': indicator_var.get(),
                    'condition': condition_var.get(),
                    'period': period_var.get()
                })
                refresh_list()
                add_popup.destroy()

            ttk.Button(add_frame, text="Add", command=save_timeframe).grid(row=4, column=0, pady=15)
            ttk.Button(add_frame, text="Cancel", command=add_popup.destroy).grid(row=4, column=1, pady=15)

        def remove_timeframe():
            selection = timeframe_list.curselection()
            if selection:
                self.mtf_timeframes.pop(selection[0])
                refresh_list()

        ttk.Button(button_frame, text="Add Timeframe", command=add_timeframe).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=remove_timeframe).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Done", command=popup.destroy).pack(side='left', padx=5)

    def create_expiration_section(self, parent):
        """Expiration Cycle Section"""
        frame = ttk.LabelFrame(parent, text="Expiration Cycle", padding=15)
        frame.pack(fill='x', pady=10)

        exp_frame = ttk.Frame(frame)
        exp_frame.pack(fill='x')

        ttk.Label(exp_frame, text="Trade only:").pack(side='left')

        self.expiration_cycle = tk.StringVar(value='any')
        ttk.Combobox(exp_frame, textvariable=self.expiration_cycle,
                    values=['any', 'monthly', 'weekly', 'eom', 'quarterly'],
                    width=15, state='readonly').pack(side='left', padx=(10, 0))

        # Help text
        help_text = ttk.Label(frame,
                             text="Monthly = 3rd Friday  |  Weekly = Every Friday  |  EOM = Last trading day  |  Quarterly = Mar/Jun/Sep/Dec",
                             font=(FONT, 9), foreground=C["dim"])
        help_text.pack(anchor='w', pady=(10, 0))

    def create_risk_management(self, parent):
        """Risk Management Section"""
        frame = ttk.LabelFrame(parent, text="Risk Management", padding=15)
        frame.pack(fill='x', pady=10)

        # Dynamic Position Sizing
        sizing_frame = ttk.Frame(frame)
        sizing_frame.pack(fill='x', pady=5)

        self.dynamic_sizing_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(sizing_frame, text="Dynamic Position Sizing",
                       variable=self.dynamic_sizing_enabled).pack(side='left')

        ttk.Label(sizing_frame, text="Method:").pack(side='left', padx=(20, 5))
        self.sizing_method = tk.StringVar(value='fixed_fractional')
        ttk.Combobox(sizing_frame, textvariable=self.sizing_method,
                    values=['fixed_fractional', 'kelly_criterion', 'volatility_based', 'greeks_based'],
                    width=18, state='readonly').pack(side='left')

        ttk.Label(sizing_frame, text="  Risk %:").pack(side='left', padx=(10, 5))
        self.sizing_risk_pct = tk.DoubleVar(value=2.0)
        ttk.Spinbox(sizing_frame, from_=0.1, to=10.0, increment=0.1,
                   textvariable=self.sizing_risk_pct, width=8).pack(side='left')

        # Portfolio Greeks Limits
        greeks_frame = ttk.Frame(frame)
        greeks_frame.pack(fill='x', pady=5)

        self.greeks_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(greeks_frame, text="Portfolio Greeks Limits",
                       variable=self.greeks_enabled).pack(side='left')

        ttk.Label(greeks_frame, text="Max Delta:").pack(side='left', padx=(20, 5))
        self.max_portfolio_delta = tk.DoubleVar(value=100.0)
        ttk.Spinbox(greeks_frame, from_=10, to=1000, increment=10,
                   textvariable=self.max_portfolio_delta, width=8).pack(side='left')

        ttk.Label(greeks_frame, text="  Max Gamma:").pack(side='left', padx=(10, 5))
        self.max_portfolio_gamma = tk.DoubleVar(value=0.5)
        ttk.Spinbox(greeks_frame, from_=0.01, to=5.0, increment=0.01,
                   textvariable=self.max_portfolio_gamma, width=8).pack(side='left')

        ttk.Label(greeks_frame, text="  Max Vega:").pack(side='left', padx=(10, 5))
        self.max_portfolio_vega = tk.DoubleVar(value=50.0)
        ttk.Spinbox(greeks_frame, from_=5, to=500, increment=5,
                   textvariable=self.max_portfolio_vega, width=8).pack(side='left')

        # Correlation Filter
        corr_frame = ttk.Frame(frame)
        corr_frame.pack(fill='x', pady=5)

        self.correlation_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(corr_frame, text="Correlation Filter",
                       variable=self.correlation_enabled).pack(side='left')

        ttk.Label(corr_frame, text="Max Correlation:").pack(side='left', padx=(20, 5))
        self.max_correlation = tk.DoubleVar(value=0.7)
        ttk.Spinbox(corr_frame, from_=0.1, to=1.0, increment=0.05,
                   textvariable=self.max_correlation, width=8).pack(side='left')

        ttk.Label(corr_frame, text="  Lookback:").pack(side='left', padx=(10, 5))
        self.correlation_lookback = tk.IntVar(value=60)
        ttk.Spinbox(corr_frame, from_=20, to=250, increment=10,
                   textvariable=self.correlation_lookback, width=8).pack(side='left')
        ttk.Label(corr_frame, text="days").pack(side='left', padx=(5, 0))

        # Liquidity Filter (ENABLED BY DEFAULT)
        liq_frame = ttk.Frame(frame)
        liq_frame.pack(fill='x', pady=5)

        self.liquidity_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(liq_frame, text="Liquidity Filter (Recommended)",
                       variable=self.liquidity_enabled).pack(side='left')

        ttk.Label(liq_frame, text="Max Spread:").pack(side='left', padx=(20, 5))
        self.max_spread_pct = tk.DoubleVar(value=5.0)
        ttk.Spinbox(liq_frame, from_=0.1, to=20.0, increment=0.5,
                   textvariable=self.max_spread_pct, width=8).pack(side='left')
        ttk.Label(liq_frame, text="%").pack(side='left', padx=(5, 10))

        ttk.Label(liq_frame, text="Min Open Interest:").pack(side='left', padx=(10, 5))
        self.min_open_interest = tk.IntVar(value=100)
        ttk.Spinbox(liq_frame, from_=0, to=10000, increment=50,
                   textvariable=self.min_open_interest, width=8).pack(side='left')

        # Important note about liquidity
        note_frame = ttk.Frame(frame)
        note_frame.pack(fill='x', pady=(15, 5))

        note = ttk.Label(note_frame,
                        text="Liquidity Filter is HIGHLY RECOMMENDED to ensure realistic backtest results.\nWithout it, backtests may show unrealistic profits from illiquid strikes.",
                        font=(FONT, 10), foreground=C["accent"], justify='left')
        note.pack(anchor='w')

    def get_config(self):
        """Return advanced configuration dictionary including indicators"""

        # Collect enabled indicators with their parameters
        indicators_config = {}
        for key, widgets in self.indicator_widgets.items():
            if widgets['enabled'].get():
                indicators_config[key] = {
                    'enabled': True,
                    **widgets['params']
                }
            else:
                indicators_config[key] = {'enabled': False}

        return {
            # VIX Filter (NEW)
            'vix_enabled': self.vix_enabled.get(),
            'vix_min': self.vix_min.get(),
            'vix_max': self.vix_max.get(),

            # Other filters
            'iv_rank_enabled': self.iv_rank_enabled.get(),
            'iv_rank_min': self.iv_rank_min.get(),
            'iv_rank_max': self.iv_rank_max.get(),
            'market_profile_enabled': self.market_profile_enabled.get(),
            'market_profile_signal': self.market_profile_signal.get(),
            'market_profile_lookback': self.market_profile_lookback.get(),
            'vol_regime_enabled': self.vol_regime_enabled.get(),
            'vol_regime_type': self.vol_regime_type.get(),

            # Earnings Filter
            'earnings_enabled': self.earnings_enabled.get(),
            'earnings_buffer_days': self.earnings_buffer_days.get(),

            # Multi-Timeframe Filter
            'mtf_enabled': self.mtf_enabled.get(),
            'mtf_timeframes': self.mtf_timeframes,
            'mtf_require_all': self.mtf_require_all.get(),

            # Expiration
            'expiration_cycle': self.expiration_cycle.get(),

            # Dynamic Position Sizing
            'dynamic_sizing_enabled': self.dynamic_sizing_enabled.get(),
            'sizing_method': self.sizing_method.get(),
            'sizing_risk_pct': self.sizing_risk_pct.get(),

            # Portfolio Greeks Limits
            'greeks_enabled': self.greeks_enabled.get(),
            'max_portfolio_delta': self.max_portfolio_delta.get(),
            'max_portfolio_gamma': self.max_portfolio_gamma.get(),
            'max_portfolio_vega': self.max_portfolio_vega.get(),

            # Correlation Filter
            'correlation_enabled': self.correlation_enabled.get(),
            'max_correlation': self.max_correlation.get(),
            'correlation_lookback': self.correlation_lookback.get(),

            # Liquidity Filter
            'liquidity_enabled': self.liquidity_enabled.get(),
            'max_spread_pct': self.max_spread_pct.get(),
            'min_open_interest': self.min_open_interest.get(),

            # Advanced Greeks Filters (Contract-Level)
            'advanced_greeks_enabled': any([
                self.gamma_filter_enabled.get(),
                self.vanna_filter_enabled.get(),
                self.charm_filter_enabled.get(),
                self.vomma_filter_enabled.get(),
                self.veta_filter_enabled.get(),
                self.speed_filter_enabled.get(),
                self.zomma_filter_enabled.get(),
                self.color_filter_enabled.get()
            ]),
            'gamma_filter_enabled': self.gamma_filter_enabled.get(),
            'max_gamma': self.max_gamma.get(),
            'vanna_filter_enabled': self.vanna_filter_enabled.get(),
            'max_vanna': self.max_vanna.get(),
            'charm_filter_enabled': self.charm_filter_enabled.get(),
            'max_charm': self.max_charm.get(),
            'vomma_filter_enabled': self.vomma_filter_enabled.get(),
            'max_vomma': self.max_vomma.get(),
            'veta_filter_enabled': self.veta_filter_enabled.get(),
            'max_veta': self.max_veta.get(),
            'speed_filter_enabled': self.speed_filter_enabled.get(),
            'max_speed': self.max_speed.get(),
            'zomma_filter_enabled': self.zomma_filter_enabled.get(),
            'max_zomma': self.max_zomma.get(),
            'color_filter_enabled': self.color_filter_enabled.get(),
            'max_color': self.max_color.get(),

            # Technical Indicators
            'indicators': indicators_config
        }
