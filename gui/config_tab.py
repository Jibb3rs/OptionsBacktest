"""
Configuration Tab - COMPLETE WITH EXPIRY RANGE CONTROL
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

from .theme import C, style_canvas

class ConfigTab:
    def __init__(self, parent, main_window):
        self.frame = ttk.Frame(parent)
        self.main_window = main_window
        
        self.load_configs()
        self.create_ui()
    
    def load_configs(self):
        """Load strategy and indicator configurations"""
        try:
            with open('config/strategies.json', 'r') as f:
                self.strategies = json.load(f)
        except Exception as e:
            self.strategies = {}
            messagebox.showerror("Error", f"Failed to load strategies: {e}")
        
        try:
            with open('config/indicators.json', 'r') as f:
                self.indicators = json.load(f)
        except Exception as e:
            self.indicators = {}
            messagebox.showerror("Error", f"Failed to load indicators: {e}")
    
    def create_ui(self):
        """Create the configuration interface"""
        
        # Main container with scrollbar
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
        
        scrollbar.pack(side="right", fill="y", padx=(0, 10))
        canvas.pack(side="left", fill="both", expand=True, padx=(50, 0), pady=10)
        
        # Enable scrolling
        from .scroll_helper import enable_scroll
        enable_scroll(canvas, scrollable_frame)
        
        # === HEADER ===
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill='x', padx=25, pady=15)
        
        ttk.Label(header_frame, text="Strategy Configuration", 
                 style='Title.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Configure your options backtest parameters", 
                 style='Subtitle.TLabel').pack(anchor='w', pady=(5, 0))
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', padx=25, pady=15)
        
        # === STRATEGY SELECTION ===
        strategy_frame = ttk.LabelFrame(scrollable_frame, text="Strategy Selection", padding=20)
        strategy_frame.pack(fill='x', padx=25, pady=10)
        
        ttk.Label(strategy_frame, text="Strategy:", style='Header.TLabel').grid(
            row=0, column=0, sticky='w', pady=8)
        
        self.strategy_var = tk.StringVar()
        strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.strategy_var, 
                                      state='readonly', width=40, font=('Helvetica', 11))
        strategy_combo['values'] = [s['name'] for s in self.strategies.values()]
        strategy_combo.grid(row=0, column=1, sticky='ew', pady=8, padx=10)
        
        if strategy_combo['values']:
            strategy_combo.current(0)
        
        strategy_combo.bind('<<ComboboxSelected>>', self.on_strategy_change)
        
        self.strategy_desc_var = tk.StringVar()
        ttk.Label(strategy_frame, textvariable=self.strategy_desc_var, 
                 style='Info.TLabel', wraplength=600).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        self.on_strategy_change()
        
        ttk.Label(strategy_frame, text="Ticker:", style='Header.TLabel').grid(
            row=2, column=0, sticky='w', pady=8)
        self.ticker_var = tk.StringVar(value="SPY")
        ttk.Entry(strategy_frame, textvariable=self.ticker_var, width=40, 
                 font=('Helvetica', 11)).grid(row=2, column=1, sticky='ew', pady=8, padx=10)
        
        # Target Expiry
        ttk.Label(strategy_frame, text="Target Expiry (days):", 
                 style='Header.TLabel').grid(row=3, column=0, sticky='w', pady=8)
        self.expiry_var = tk.IntVar(value=30)
        expiry_spin = ttk.Spinbox(strategy_frame, from_=0, to=365, 
                                  textvariable=self.expiry_var, width=38, 
                                  font=('Helvetica', 11))
        expiry_spin.grid(row=3, column=1, sticky='ew', pady=8, padx=10)
        
        ttk.Label(strategy_frame, text="(0 = same day, 30 = monthly, 365 = LEAP)", 
                 style='Info.TLabel').grid(row=4, column=1, sticky='w', padx=10)
        
        # Expiry Search Range
        ttk.Label(strategy_frame, text="Expiry Search Range (±days):", 
                 style='Header.TLabel').grid(row=5, column=0, sticky='w', pady=8)
        
        range_frame = ttk.Frame(strategy_frame)
        range_frame.grid(row=5, column=1, sticky='ew', pady=8, padx=10)
        
        self.expiry_range_var = tk.IntVar(value=5)
        range_spin = ttk.Spinbox(range_frame, from_=0, to=15, 
                                textvariable=self.expiry_range_var, 
                                width=10, font=('Helvetica', 11))
        range_spin.pack(side='left')
        
        # Tooltip button
        info_label = ttk.Label(range_frame, text=" [i]",
                              style='Info.TLabel', cursor="hand2")
        info_label.pack(side='left', padx=(5, 0))
        
        # Bind tooltip
        def show_range_tooltip(event):
            tooltip_text = """Expiry Search Range Explained:

Target Expiry: 30 days
Search Range: ±5 days

The algorithm will search for options expiring 
between 25-35 days from today.

Why use a range?
- Options don't expire every day
- Monthly options typically expire on 3rd Friday
- A range ensures we find available options

Recommended settings:
- ±5 days for monthly (30-45 DTE)
- ±3 days for weeklies (7-14 DTE)
- ±0 days for same-day (0 DTE with Minute resolution)

All 4 Iron Condor legs will use the SAME 
expiration date within this range."""
            
            messagebox.showinfo("Expiry Search Range", tooltip_text, parent=self.frame)
        
        info_label.bind("<Button-1>", show_range_tooltip)
        
        ttk.Label(strategy_frame, text="(Wider range = more flexibility, all 4 legs use SAME expiry)", 
                 style='Info.TLabel').grid(row=6, column=1, sticky='w', padx=10)
        
        strategy_frame.columnconfigure(1, weight=1)
        
        # === STRIKE SELECTION ===
        strike_frame = ttk.LabelFrame(scrollable_frame, text="Strike Selection Method", padding=20)
        strike_frame.pack(fill='x', padx=25, pady=10)
        
        self.strike_method_var = tk.StringVar(value="delta")
        
        methods = [
            ("Delta-Based (Recommended - Auto-adjusts for volatility)", "delta"),
            ("Fixed Points Offset (Static distance from price)", "fixed_points"),
            ("Percentage Offset (Static % from price)", "percentage"),
            ("ATR-Based (Volatility-adjusted)", "atr")
        ]
        
        for i, (text, value) in enumerate(methods):
            rb = ttk.Radiobutton(strike_frame, text=text, variable=self.strike_method_var, 
                                value=value, command=self.on_strike_method_change)
            rb.grid(row=i, column=0, sticky='w', pady=3)
        
        # Delta parameters
        self.delta_params_frame = ttk.LabelFrame(strike_frame, text="Delta Parameters", padding=15)
        self.delta_params_frame.grid(row=len(methods), column=0, sticky='ew', pady=15, padx=10)
        
        delta_params = [
            ("Short Put Delta:", 0.16, "Win probability: ~84%"),
            ("Long Put Delta:", 0.08, "Protection level"),
            ("Short Call Delta:", -0.16, "Win probability: ~84%"),
            ("Long Call Delta:", -0.08, "Protection level")
        ]
        
        self.delta_vars = {}
        for i, (label, default, info) in enumerate(delta_params):
            ttk.Label(self.delta_params_frame, text=label, style='Header.TLabel').grid(
                row=i, column=0, sticky='w', pady=5)
            var = tk.DoubleVar(value=default)
            ttk.Entry(self.delta_params_frame, textvariable=var, width=10).grid(
                row=i, column=1, padx=10, pady=5)
            ttk.Label(self.delta_params_frame, text=info, style='Info.TLabel').grid(
                row=i, column=2, sticky='w', pady=5)
            self.delta_vars[label] = var
        
        # === INDICATORS ===
        indicators_frame = ttk.LabelFrame(scrollable_frame, text="Technical Indicators", padding=20)
        indicators_frame.pack(fill='x', padx=25, pady=10)
        
        ttk.Label(indicators_frame, 
                 text="Select indicators to filter entry signals:", 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Scrollable indicator list
        ind_canvas = tk.Canvas(indicators_frame, height=250, highlightthickness=0)
        style_canvas(ind_canvas)
        ind_scrollbar = ttk.Scrollbar(indicators_frame, orient="vertical", command=ind_canvas.yview)
        ind_scrollable = ttk.Frame(ind_canvas)
        
        ind_scrollable.bind(
            "<Configure>",
            lambda e: ind_canvas.configure(scrollregion=ind_canvas.bbox("all"))
        )
        
        ind_canvas.create_window((0, 0), window=ind_scrollable, anchor="nw")
        ind_canvas.configure(yscrollcommand=ind_scrollbar.set)
        
        ind_scrollbar.pack(side="right", fill="y")
        ind_canvas.pack(side="left", fill="both", expand=True)
        
        # Enable scrolling for indicators
        from .scroll_helper import enable_scroll
        enable_scroll(ind_canvas, ind_scrollable)
        
        # Create indicator checkboxes
        self.indicator_vars = {}
        
        categories = {}
        for key, ind in self.indicators.items():
            cat = ind.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((key, ind))
        
        for cat_name, indicators in categories.items():
            cat_label = ttk.Label(ind_scrollable, 
                                 text=f"{cat_name.upper()}", 
                                 style='Header.TLabel')
            cat_label.pack(anchor='w', pady=(10, 5), padx=5)
            
            for key, ind in indicators:
                var = tk.BooleanVar(value=False)
                cb_text = f"{ind['name']} - {ind['desc']}"
                cb = ttk.Checkbutton(ind_scrollable, text=cb_text, variable=var)
                cb.pack(anchor='w', pady=2, padx=15)
                self.indicator_vars[key] = var
        
        # Enable defaults - NONE by default
        # for key in ['RSI', 'ATR']:
        #     if key in self.indicator_vars:
        #         self.indicator_vars[key].set(True)
        
        # === DATE RANGE ===
        date_frame = ttk.LabelFrame(scrollable_frame, text="Backtest Period", padding=20)
        date_frame.pack(fill='x', padx=25, pady=10)
        
        ttk.Label(date_frame, text="Start Date (YYYY-MM-DD):", 
                 style='Header.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.start_date_var = tk.StringVar(value="2024-01-01")
        ttk.Entry(date_frame, textvariable=self.start_date_var, width=20, 
                 font=('Helvetica', 11)).grid(row=0, column=1, sticky='w', padx=10, pady=8)
        
        ttk.Label(date_frame, text="End Date (YYYY-MM-DD):", 
                 style='Header.TLabel').grid(row=1, column=0, sticky='w', pady=8)
        self.end_date_var = tk.StringVar(value="2024-03-31")
        ttk.Entry(date_frame, textvariable=self.end_date_var, width=20, 
                 font=('Helvetica', 11)).grid(row=1, column=1, sticky='w', padx=10, pady=8)
        
        # === TRADING RULES ===
        rules_frame = ttk.LabelFrame(scrollable_frame, text="Trading Rules & Risk Management", padding=20)
        rules_frame.pack(fill='x', padx=25, pady=10)
        
        # Resolution
        ttk.Label(rules_frame, text="Resolution (How often to check):", 
                 style='Header.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.resolution_var = tk.StringVar(value="Daily")
        resolution_combo = ttk.Combobox(rules_frame, textvariable=self.resolution_var, 
                                       state='readonly', width=37, font=('Helvetica', 11))
        resolution_combo['values'] = ['Minute', 'Hour', 'Daily']
        resolution_combo.grid(row=0, column=1, sticky='ew', pady=8, padx=10)
        ttk.Label(rules_frame, text="(Minute for 0-3 DTE, Hour for 4-10 DTE, Daily for 11+ DTE)", 
                 style='Info.TLabel').grid(row=1, column=1, sticky='w', padx=10)
        
        # Max Positions
        ttk.Label(rules_frame, text="Max Concurrent Positions:", 
                 style='Header.TLabel').grid(row=2, column=0, sticky='w', pady=8)
        self.max_positions_var = tk.IntVar(value=5)
        ttk.Spinbox(rules_frame, from_=1, to=20, textvariable=self.max_positions_var, 
                   width=37, font=('Helvetica', 11)).grid(row=2, column=1, sticky='ew', pady=8, padx=10)
        ttk.Label(rules_frame, text="(How many Iron Condors can be open at once)", 
                 style='Info.TLabel').grid(row=3, column=1, sticky='w', padx=10)
        
        # Min Days Between Trades
        ttk.Label(rules_frame, text="Min Days Between New Trades:", 
                 style='Header.TLabel').grid(row=4, column=0, sticky='w', pady=8)
        self.min_days_var = tk.IntVar(value=0)
        ttk.Spinbox(rules_frame, from_=0, to=30, textvariable=self.min_days_var, 
                   width=37, font=('Helvetica', 11)).grid(row=4, column=1, sticky='ew', pady=8, padx=10)
        ttk.Label(rules_frame, text="(0 = No wait, enter new trades immediately)", 
                 style='Info.TLabel').grid(row=5, column=1, sticky='w', padx=10)
        
        # Profit Target
        ttk.Label(rules_frame, text="Profit Target (% of max profit):", 
                 style='Header.TLabel').grid(row=6, column=0, sticky='w', pady=8)
        self.profit_target_var = tk.IntVar(value=50)
        ttk.Spinbox(rules_frame, from_=10, to=100, textvariable=self.profit_target_var, 
                   width=37, font=('Helvetica', 11)).grid(row=6, column=1, sticky='ew', pady=8, padx=10)
        ttk.Label(rules_frame, text="(50 = Exit at 50% of max profit, 100 = Hold to expiration)", 
                 style='Info.TLabel').grid(row=7, column=1, sticky='w', padx=10)
        
        # Stop Loss Mode
        ttk.Label(rules_frame, text="Stop Loss Mode:", 
                style='Header.TLabel').grid(row=8, column=0, sticky='w', pady=8)

        mode_frame = ttk.Frame(rules_frame)
        mode_frame.grid(row=8, column=1, sticky='ew', pady=8, padx=10)

        self.stop_loss_mode_var = tk.StringVar(value="credit")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.stop_loss_mode_var, 
                                state='readonly', width=30, font=('Helvetica', 11))
        mode_combo['values'] = [
            'Credit-Based (Options Standard)',
            'Max Loss-Based (Conservative)', 
            'Equal Dollar (1:1 Risk/Reward)',
            'Price Distance (FX-Style)'
        ]
        mode_combo.current(0)
        mode_combo.pack(side='left')

        # Info button for stop loss mode
        mode_info = ttk.Label(mode_frame, text=" [i]",
                            style='Info.TLabel', cursor="hand2")
        mode_info.pack(side='left', padx=(5, 0))

        def show_mode_tooltip(event):
            tooltip = """Stop Loss Modes Explained:

        1. Credit-Based (Options Standard) [RECOMMENDED]
        - Stop loss as % of credit received
        - Example: 100% = risk 1x credit
        - If credit = $100, stop at -$100 loss
        - With 50% profit target → 1:2 risk/reward
        
        2. Max Loss-Based (Conservative)
        - Stop loss as % of maximum possible loss
        - Example: 50% = exit at half max loss
        - If max loss = $400, stop at -$200
        - Protects against catastrophic losses
        
        3. Equal Dollar (1:1 Risk/Reward)
        - Stop loss = Same $ as profit target
        - Example: Profit at +$50, stop at -$50
        - Simple 1:1 risk/reward ratio
        
        4. Price Distance (FX-Style)
        - Exit when underlying moves X% from entry
        - Example: 5% = exit if SPY moves 5%
        - Similar to forex stop losses"""
            
            messagebox.showinfo("Stop Loss Modes", tooltip, parent=self.frame)

        mode_info.bind("<Button-1>", show_mode_tooltip)

        ttk.Label(rules_frame, text="(Different traders use different methods - choose yours)", 
                style='Info.TLabel').grid(row=9, column=1, sticky='w', padx=10)

        # Stop Loss Value
        ttk.Label(rules_frame, text="Stop Loss Value (%):", 
                style='Header.TLabel').grid(row=10, column=0, sticky='w', pady=8)

        value_frame = ttk.Frame(rules_frame)
        value_frame.grid(row=10, column=1, sticky='ew', pady=8, padx=10)

        self.stop_loss_var = tk.IntVar(value=100)
        ttk.Spinbox(value_frame, from_=10, to=500, increment=10, 
                textvariable=self.stop_loss_var, width=15, 
                font=('Helvetica', 11)).pack(side='left')

        # Dynamic label based on mode
        self.stop_loss_label_var = tk.StringVar(value="(100% = risk 1x credit)")
        stop_label = ttk.Label(value_frame, textvariable=self.stop_loss_label_var,
                            style='Info.TLabel')
        stop_label.pack(side='left', padx=(10, 0))

        # Update label when mode changes
        def update_stop_label(*args):
            mode = self.stop_loss_mode_var.get()
            value = self.stop_loss_var.get()
            
            if 'Credit-Based' in mode:
                self.stop_loss_label_var.set(f"({value}% = risk {value/100:.1f}x credit)")
            elif 'Max Loss' in mode:
                self.stop_loss_label_var.set(f"({value}% = {value/100:.1f}x max loss)")
            elif 'Equal Dollar' in mode:
                self.stop_loss_label_var.set("(Matches profit target amount)")
            elif 'Price Distance' in mode:
                self.stop_loss_label_var.set(f"({value}% move in underlying price)")

        self.stop_loss_mode_var.trace_add('write', update_stop_label)
        self.stop_loss_var.trace_add('write', update_stop_label)        
        rules_frame.columnconfigure(1, weight=1)
        
        # === ACTION BUTTONS ===
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', padx=25, pady=25)
        
        ttk.Button(button_frame, text="Load Preset",
                  command=self.load_preset).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Save Preset",
                  command=self.save_preset).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Reset to Defaults",
                  command=self.reset).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Generate QuantConnect Files",
                  command=self.generate,
                  style='Big.TButton').pack(side='right', padx=5)
    
    def on_strategy_change(self, event=None):
        """Update strategy description"""
        selected = self.strategy_var.get()
        for key, strat in self.strategies.items():
            if strat['name'] == selected:
                self.strategy_desc_var.set(strat.get('description', ''))
                break
        self.main_window.update_status(f"Selected strategy: {selected}")
    
    def on_strike_method_change(self):
        """Handle strike method changes"""
        pass
    
    def get_config(self):
        """Get current configuration"""
        config = {
            "strategy": self.strategy_var.get(),
            "ticker": self.ticker_var.get(),
            "expiry_days": self.expiry_var.get(),
            "expiry_range": self.expiry_range_var.get(),
            "strike_selection": {
                "method": self.strike_method_var.get()
            },
            "start_date": self.start_date_var.get(),
            "end_date": self.end_date_var.get(),
            "indicators": {},
            "trading_rules": {
                "resolution": self.resolution_var.get(),
                "max_positions": self.max_positions_var.get(),
                "min_days_between_trades": self.min_days_var.get(),
                "profit_target_pct": self.profit_target_var.get(),
                "stop_loss_mode": self.stop_loss_mode_var.get(),  # ADD THIS
                "stop_loss_pct": self.stop_loss_var.get()
            }
        }
        
        if self.strike_method_var.get() == "delta":
            config["strike_selection"]["deltas"] = {
                k: v.get() for k, v in self.delta_vars.items()
            }
        
        config["indicators"] = {
            key: True for key, var in self.indicator_vars.items() if var.get()
        }
        
        return config
    
    def generate(self):
        """Generate QuantConnect files"""
        config = self.get_config()
        
        if not config['strategy']:
            messagebox.showwarning("Validation", "Please select a strategy")
            return
        
        from .code_popup import show_code_popup
        show_code_popup(self.frame, config, self.main_window)
    
    def load_preset(self):
        """Load preset"""
        file_path = filedialog.askopenfilename(
            initialdir="presets",
            title="Select Preset",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    preset = json.load(f)
                
                if 'ticker' in preset:
                    self.ticker_var.set(preset['ticker'])
                if 'expiry_days' in preset:
                    self.expiry_var.set(preset['expiry_days'])
                if 'expiry_range' in preset:
                    self.expiry_range_var.set(preset['expiry_range'])
                if 'start_date' in preset:
                    self.start_date_var.set(preset['start_date'])
                if 'end_date' in preset:
                    self.end_date_var.set(preset['end_date'])
                
                messagebox.showinfo("Success", f"Loaded preset: {preset.get('name', 'Unknown')}")
                self.main_window.update_status(f"Loaded preset")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load preset: {e}")
    
    def save_preset(self):
        """Save preset"""
        import tkinter.simpledialog as sd
        
        name = sd.askstring("Save Preset", "Enter preset name:")
        if name:
            config = self.get_config()
            config['name'] = name
            
            filename = f"presets/{name.lower().replace(' ', '_')}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Success", f"Preset saved: {filename}")
                self.main_window.update_status(f"Preset saved: {name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
    
    def reset(self):
        """Reset to defaults"""
        if messagebox.askyesno("Reset", "Reset all fields?"):
            self.ticker_var.set("SPY")
            self.expiry_var.set(30)
            self.expiry_range_var.set(5)
            self.strike_method_var.set("delta")
            self.delta_vars["Short Put Delta:"].set(0.16)
            self.delta_vars["Long Put Delta:"].set(0.08)
            self.delta_vars["Short Call Delta:"].set(-0.16)
            self.delta_vars["Long Call Delta:"].set(-0.08)
            self.start_date_var.set("2024-01-01")
            self.end_date_var.set("2024-03-31")
            
            # Reset trading rules
            self.resolution_var.set("Daily")
            self.max_positions_var.set(5)
            self.min_days_var.set(0)
            self.stop_loss_mode_var.set("credit")  # ADD THIS
            self.stop_loss_var.set(100)  # Changed from 200 to 100
            
            for var in self.indicator_vars.values():
                var.set(False)
            
            self.main_window.update_status("Reset to defaults")