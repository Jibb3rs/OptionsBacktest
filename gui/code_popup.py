"""
Code Popup - Shows generated QuantConnect code for copy-paste
COMPLETE VERSION with:
- Expiry range support (modular)
- Same expiry enforcement (Iron Condor fix)
- +/-50 strike range
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import webbrowser

from .theme import C, FONT, FONT_MONO, FONT_TITLE, FONT_SUBTITLE, style_text

def show_code_popup(parent, config, main_window):
    """Show popup with generated algorithm code and config"""

    popup = tk.Toplevel(parent)
    popup.title("QuantConnect Files Generated")
    popup.configure(bg=C["bg"])
    popup.transient(parent)
    popup.grab_set()

    # Center on screen
    width = 1100
    height = 800
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    popup.geometry(f'{width}x{height}+{x}+{y}')

    # Configure grid for proper centering
    popup.grid_rowconfigure(0, weight=1)
    popup.grid_columnconfigure(0, weight=1)

    # Main container - centered
    main_frame = ttk.Frame(popup, padding=30)
    main_frame.grid(row=0, column=0, sticky='nsew')
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Header
    header_frame = ttk.Frame(main_frame)
    header_frame.grid(row=0, column=0, pady=(0, 15))

    ttk.Label(header_frame, text="Files Generated Successfully!",
             style='Title.TLabel').pack()
    ttk.Label(header_frame, text="Copy these to QuantConnect and run your backtest",
             style='Subtitle.TLabel').pack(pady=(5, 0))

    # Notebook
    notebook = ttk.Notebook(main_frame)
    notebook.grid(row=1, column=0, sticky='nsew', pady=(0, 15))

    # === ALGORITHM TAB ===
    algo_frame = ttk.Frame(notebook)
    notebook.add(algo_frame, text="  1. Algorithm Code (main.py)  ")

    # Configure grid
    algo_frame.grid_rowconfigure(1, weight=1)
    algo_frame.grid_columnconfigure(0, weight=1)

    ttk.Label(algo_frame, text="Paste this into main.py in QuantConnect:",
             style='Header.TLabel').grid(row=0, column=0, sticky='w',
                                                  padx=20, pady=(15, 10))

    # Generate algorithm code
    algo_code = generate_algorithm_code(config)

    # Text widget frame
    algo_text_frame = ttk.Frame(algo_frame)
    algo_text_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 10))
    algo_text_frame.grid_rowconfigure(0, weight=1)
    algo_text_frame.grid_columnconfigure(0, weight=1)

    algo_text = scrolledtext.ScrolledText(algo_text_frame, wrap='none')
    style_text(algo_text, code=True)
    algo_text.grid(row=0, column=0, sticky='nsew')
    algo_text.insert('1.0', algo_code)
    algo_text.config(state='disabled')

    # Enable trackpad scrolling
    enable_mousewheel_scrolling(algo_text)

    # Copy button
    def copy_algorithm():
        popup.clipboard_clear()
        popup.clipboard_append(algo_code)
        messagebox.showinfo("Copied!",
                          "Algorithm code copied to clipboard!\n\n"
                          "Now paste it into QuantConnect's main.py file.",
                          parent=popup)

    ttk.Button(algo_frame, text="Copy Algorithm Code",
              command=copy_algorithm).grid(row=2, column=0, pady=(0, 15))

    # === INSTRUCTIONS TAB ===
    inst_frame = ttk.Frame(notebook)
    notebook.add(inst_frame, text="  2. Instructions  ")

    inst_frame.grid_rowconfigure(0, weight=1)
    inst_frame.grid_columnconfigure(0, weight=1)

    # Generate instructions
    instructions = generate_instructions(config)

    # Text widget frame
    inst_text_frame = ttk.Frame(inst_frame)
    inst_text_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=15)
    inst_text_frame.grid_rowconfigure(0, weight=1)
    inst_text_frame.grid_columnconfigure(0, weight=1)

    inst_text = scrolledtext.ScrolledText(inst_text_frame, wrap='word')
    style_text(inst_text, code=True)
    inst_text.grid(row=0, column=0, sticky='nsew')
    inst_text.insert('1.0', instructions)
    inst_text.config(state='disabled')

    # Enable trackpad scrolling
    enable_mousewheel_scrolling(inst_text)

    # === BOTTOM BUTTONS ===
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=2, column=0)

    ttk.Button(button_frame, text="Open QuantConnect",
              command=lambda: webbrowser.open('https://www.quantconnect.com/terminal'),
              width=25).pack(side='left', padx=5)

    ttk.Button(button_frame, text="Close",
              command=popup.destroy,
              width=15).pack(side='left', padx=5)

    main_window.update_status("QuantConnect files generated - ready to copy!")


def enable_mousewheel_scrolling(widget):
    """Enable trackpad/mousewheel scrolling for text widget"""

    def on_vertical_scroll(event):
        if event.num == 5 or event.delta < 0:
            widget.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            widget.yview_scroll(-1, "units")
        return "break"

    def on_horizontal_scroll(event):
        if event.num == 5 or event.delta < 0:
            widget.xview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            widget.xview_scroll(-1, "units")
        return "break"

    def on_enter(event):
        widget.bind_all("<MouseWheel>", on_vertical_scroll)
        widget.bind_all("<Button-4>", on_vertical_scroll)
        widget.bind_all("<Button-5>", on_vertical_scroll)
        widget.bind_all("<Shift-MouseWheel>", on_horizontal_scroll)
        widget.bind_all("<Shift-Button-4>", on_horizontal_scroll)
        widget.bind_all("<Shift-Button-5>", on_horizontal_scroll)

    def on_leave(event):
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")
        widget.unbind_all("<Shift-MouseWheel>")
        widget.unbind_all("<Shift-Button-4>")
        widget.unbind_all("<Shift-Button-5>")

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def format_delta_settings(config):
    """Format delta settings for display"""
    if config.get('strike_selection', {}).get('method') == 'delta':
        deltas = config.get('strike_selection', {}).get('deltas', {})
        lines = []
        for key, value in deltas.items():
            win_pct = ""
            if 'Short' in key:
                abs_delta = abs(value)
                win_pct = f" (~{int((1 - abs_delta) * 100)}% OTM probability)"
            lines.append(f"  - {key}: {value}{win_pct}")
        return '\n'.join(lines) if lines else "  N/A"
    return "  N/A (not using delta method)"


def generate_instructions(config):
    """Generate step-by-step instructions"""

    trading_rules = config.get('trading_rules', {})
    expiry_range = config.get('expiry_range', 5)

    instructions = f"""
STEP-BY-STEP GUIDE
============================================================

STEP 1: Open QuantConnect
   - Go to quantconnect.com/terminal
   - Log in
   - Click "Open QuantConnect" button below

STEP 2: Paste Algorithm
   - Click "Algorithm Code" tab
   - Click "Copy Algorithm Code"
   - In QuantConnect: Cmd+A (or Ctrl+A), then paste

STEP 3: Run Backtest
   - Click "Backtest" in QuantConnect
   - Wait 2-5 minutes
   - Watch logs for your trades

STEP 4: Download & Analyze
   - Download results CSV
   - Return to this app -> "Analyze Results" tab
   - Upload CSV for MAE/MFE analysis

============================================================
YOUR CONFIGURATION
============================================================

Strategy:     {config.get('strategy', 'N/A')}
Ticker:       {config.get('ticker', 'N/A')}
Expiry:       {config.get('expiry_days', 'N/A')} days (+/-{expiry_range} day range)
Period:       {config.get('start_date', 'N/A')} to {config.get('end_date', 'N/A')}
Method:       {config.get('strike_selection', {}).get('method', 'N/A')}
Indicators:   {len(config.get('indicators', {}))} enabled

TRADING RULES:
Resolution:              {trading_rules.get('resolution', 'Daily')}
Max Positions:           {trading_rules.get('max_positions', 5)}
Min Days Between:        {trading_rules.get('min_days_between_trades', 0)}
Profit Target:           {trading_rules.get('profit_target_pct', 50)}%
Stop Loss:               {trading_rules.get('stop_loss_pct', 200)}%

Delta Settings:
{format_delta_settings(config)}

============================================================
TROUBLESHOOTING
============================================================

- No trades: Check ticker (use SPY not SPX), reduce indicators
- Compilation errors: Verify all code pasted correctly
- Backtest fails: Check dates and expiry settings

Ready? Click "Open QuantConnect" below!
"""
    return instructions


def generate_algorithm_code(config):
    """Generate QuantConnect algorithm code - MODULAR VERSION"""

    strategy = config.get('strategy', 'Iron Condor')

    # Import the appropriate strategy module
    if strategy == 'Iron Condor':
        from strategies.iron_condor import IronCondor
        return IronCondor.generate_code(config)

    elif strategy == 'Iron Butterfly':
        from strategies.iron_butterfly import IronButterfly
        return IronButterfly.generate_code(config)

    elif strategy == 'Short Strangle':
        from strategies.short_strangle import ShortStrangle
        return ShortStrangle.generate_code(config)

    elif strategy == 'Short Straddle':
        from strategies.short_straddle import ShortStraddle
        return ShortStraddle.generate_code(config)

    elif strategy == 'Bull Put Spread':
        from strategies.bull_put_spread import BullPutSpread
        return BullPutSpread.generate_code(config)

    elif strategy == 'Bear Call Spread':
        from strategies.bear_call_spread import BearCallSpread
        return BearCallSpread.generate_code(config)

    elif strategy == 'Bull Call Spread':
        from strategies.bull_call_spread import BullCallSpread
        return BullCallSpread.generate_code(config)

    elif strategy == 'Bear Put Spread':
        from strategies.bear_put_spread import BearPutSpread
        return BearPutSpread.generate_code(config)

    else:
        raise ValueError(f"Unknown strategy: {strategy}")
