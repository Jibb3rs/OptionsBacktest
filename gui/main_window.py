"""
Main Window - Options Backtesting System
Manages tabs and overall application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import subprocess
import os

from .theme import C, FONT, FONT_TITLE, FONT_MONO, style_text, style_menu


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Options Backtesting System")
        self.root.geometry("1300x850")
        self.root.minsize(1100, 750)
        self.root.configure(bg=C["bg"])

        # Create menu bar
        self.create_menu()

        # Initialize status label FIRST (create but don't pack yet)
        self.init_status_bar()

        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True)

        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, padx=16, pady=(12, 0))

        # Import and create tabs
        from .config_tab import ConfigTab
        from .advanced_tab import AdvancedTab
        from .compare_tab import CompareTab
        from .settings_tab import SettingsTab
        from .analysis_tab import AnalysisTab

        self.config_tab = ConfigTab(self.notebook, self)
        self.advanced_tab = AdvancedTab(self.notebook, self)
        self.compare_tab = CompareTab(self.notebook, self)
        self.settings_tab = SettingsTab(self.notebook, self)
        self.analysis_tab = AnalysisTab(self.notebook, self)

        # Add tabs to notebook
        self.notebook.add(self.config_tab.frame, text="  Configure Backtest  ")
        self.notebook.add(self.advanced_tab.frame, text="  Advanced Filters  ")
        self.notebook.add(self.compare_tab.frame, text="  Compare Strategies  ")
        self.notebook.add(self.analysis_tab.frame, text="  Trade Analysis  ")
        self.notebook.add(self.settings_tab.frame, text="  Settings  ")

        # NOW pack the status bar (after tabs are created)
        self.pack_status_bar()

        # Center window
        self.center_window()

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg=C["card_bg"], fg=C["text"],
                         activebackground=C["accent"], activeforeground=C["bg"],
                         font=(FONT, 10), relief="flat", borderwidth=0)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        style_menu(file_menu)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Configuration", command=lambda: self.notebook.select(0))
        file_menu.add_command(label="Load Results", command=lambda: self.notebook.select(1))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        style_menu(tools_menu)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Open QuantConnect",
                              command=lambda: webbrowser.open('https://www.quantconnect.com/terminal'))
        tools_menu.add_command(label="Open Output Folder", command=self.open_output_folder)
        tools_menu.add_command(label="Open Results Folder", command=self.open_results_folder)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        style_menu(help_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Understanding Delta (Win %)", command=self.show_delta_help)
        help_menu.add_command(label="About", command=self.show_about)

    def init_status_bar(self):
        """Initialize status bar"""
        self.status_frame = tk.Frame(self.root, bg=C["card_bg"], height=30)
        # Top border line
        border = tk.Frame(self.status_frame, bg=C["card_border"], height=1)
        border.pack(side='top', fill='x')

        self.status_label = tk.Label(self.status_frame, text="Ready",
                                    bg=C["card_bg"], fg=C["dim"],
                                    font=(FONT, 10), anchor='w', padx=16)
        self.status_label.pack(side='left', fill='x', expand=True)

        version_label = tk.Label(self.status_frame, text="v2.0",
                                bg=C["card_bg"], fg=C["dim"],
                                font=(FONT, 10), padx=16)
        version_label.pack(side='right')

    def pack_status_bar(self):
        """Pack the status bar frame to bottom"""
        self.status_frame.pack(side='bottom', fill='x')

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def get_config(self):
        """Collect configuration from all tabs"""
        config = self.config_tab.get_config()
        config['advanced'] = self.advanced_tab.get_config()
        return config

    # Menu command handlers
    def open_output_folder(self):
        """Open output folder"""
        path = os.path.expanduser("~/Desktop/QC_Upload")
        os.makedirs(path, exist_ok=True)
        try:
            os.startfile(path)
        except AttributeError:
            try:
                subprocess.call(["open", path])
            except:
                messagebox.showinfo("Output Folder", f"Folder: {path}")

    def open_results_folder(self):
        """Open results folder"""
        path = os.path.join(os.getcwd(), "results")
        os.makedirs(path, exist_ok=True)
        try:
            os.startfile(path)
        except AttributeError:
            try:
                subprocess.call(["open", path])
            except:
                messagebox.showinfo("Results Folder", f"Folder: {path}")

    def show_delta_help(self):
        """Show delta explanation window"""
        help_text = """UNDERSTANDING DELTA AND WIN PROBABILITY

Delta = Probability the option expires In-The-Money (ITM)

FOR SOLD OPTIONS (like Iron Condor short legs):

Delta     ITM Chance    OTM Chance (YOU WIN!)
------    ----------    ---------------------
0.05         5%             95%  <- Very safe
0.10        10%             90%  <- Conservative
0.16        16%             84%  <- Standard (Most common)
0.20        20%             80%  <- Moderate
0.25        25%             75%  <- Aggressive
0.30        30%             70%  <- Very aggressive

REAL EXAMPLE:
- SPX trading at 6000
- You sell a put with 0.16 delta
- System finds the 5900 put (100 points below)
- This put has 16% chance of expiring ITM
- Which means 84% chance it expires worthless
- If it expires worthless = YOU WIN!

WHY DELTA INSTEAD OF FIXED POINTS?

Delta automatically adjusts for volatility:

When VIX is LOW (market calm):
- 0.16 delta might be only 50 points away

When VIX is HIGH (market volatile):
- 0.16 delta might be 150 points away

SAME 84% WIN RATE, but different distances!

RECOMMENDATION FOR NEW TRADERS:
- Start with 0.10 delta (90% win rate)
- Move to 0.16 delta (84% win rate) when comfortable
- Only use 0.25+ delta (75% win) if very experienced"""

        help_window = tk.Toplevel(self.root)
        help_window.title("Understanding Delta & Win Probability")
        help_window.geometry("750x650")
        help_window.configure(bg=C["bg"])
        help_window.transient(self.root)
        help_window.grab_set()

        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - 375
        y = (help_window.winfo_screenheight() // 2) - 325
        help_window.geometry(f'+{x}+{y}')

        text = tk.Text(help_window, wrap='word', padx=20, pady=20)
        style_text(text, code=True)
        text.pack(fill='both', expand=True, padx=16, pady=(16, 0))
        text.insert('1.0', help_text)
        text.config(state='disabled')

        ttk.Button(help_window, text="Got It!",
                  command=help_window.destroy,
                  style='Big.TButton').pack(pady=16)

    def show_about(self):
        """Show about dialog"""
        about_text = """Options Backtesting System v2.0

A comprehensive tool for backtesting options strategies
using QuantConnect's historical data.

Features:
- 9 option strategies
- 16 technical indicators
- Delta-based strike selection
- Complete QuantConnect integration
- MAE/MFE analysis
- 30+ performance metrics
- Strategy comparison tool
- Advanced filters (IV Rank, Market Profile, etc.)"""

        messagebox.showinfo("About", about_text)
