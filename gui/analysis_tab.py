"""
Analysis Tab - ULTIMATE EDITION
Complete analysis with MAE/MFE scatter, heatmaps, advanced metrics, and more
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import json
from datetime import datetime
import numpy as np
import os

from .theme import C, FONT, style_canvas, style_text, chart_colors

# Configure matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
plt.ioff()

class AnalysisTab:
    def __init__(self, parent, main_window):
        self.frame = ttk.Frame(parent)
        self.main_window = main_window
        self.df = None
        self.pnl_column = None

        self.create_ui()

    def create_ui(self):
        """Create the ultimate analysis interface"""

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

        ttk.Label(header_frame, text="Advanced Trade Analysis",
                 style='Title.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Comprehensive analysis with MAE/MFE insights, heatmaps, and advanced metrics",
                 style='Subtitle.TLabel').pack(anchor='w', pady=(5, 0))

        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', padx=25, pady=15)

        # === IMPORT SECTION ===
        import_frame = ttk.LabelFrame(scrollable_frame, text="Import Results", padding=20)
        import_frame.pack(fill='x', padx=25, pady=10)

        ttk.Label(import_frame, text="Upload your QuantConnect results:",
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))

        button_frame = ttk.Frame(import_frame)
        button_frame.pack(fill='x')

        ttk.Button(button_frame, text="Browse CSV File",
                  command=self.import_csv,
                  style='Big.TButton').pack(side='left', padx=5)

        ttk.Button(button_frame, text="Generate Sample Data",
                  command=self.load_sample_data,
                  style='Big.TButton').pack(side='left', padx=5)

        self.file_label = ttk.Label(button_frame, text="No file loaded",
                                    style='Info.TLabel')
        self.file_label.pack(side='left', padx=15)

        # === TABS FOR DIFFERENT ANALYSIS VIEWS ===
        self.analysis_notebook = ttk.Notebook(scrollable_frame)
        self.analysis_notebook.pack(fill='both', expand=True, padx=25, pady=10)

        # Create tabs (empty until data loaded)
        self.overview_tab = ttk.Frame(self.analysis_notebook)
        self.charts_tab = ttk.Frame(self.analysis_notebook)
        self.mae_mfe_tab = ttk.Frame(self.analysis_notebook)
        self.heatmap_tab = ttk.Frame(self.analysis_notebook)
        self.advanced_tab = ttk.Frame(self.analysis_notebook)
        self.trades_tab = ttk.Frame(self.analysis_notebook)

        self.analysis_notebook.add(self.overview_tab, text="  Overview  ")
        self.analysis_notebook.add(self.charts_tab, text="  Basic Charts  ")
        self.analysis_notebook.add(self.mae_mfe_tab, text="  MAE/MFE Analysis  ")
        self.analysis_notebook.add(self.heatmap_tab, text="  Heatmaps  ")
        self.analysis_notebook.add(self.advanced_tab, text="  Advanced Metrics  ")
        self.analysis_notebook.add(self.trades_tab, text="  Trade History  ")

        # Placeholder labels
        self.create_placeholders()

    def create_placeholders(self):
        """Create placeholder labels for all tabs"""

        for tab, text in [
            (self.overview_tab, "Load a CSV to see overview metrics"),
            (self.charts_tab, "Load a CSV to see basic charts"),
            (self.mae_mfe_tab, "Load a CSV to see MAE/MFE analysis"),
            (self.heatmap_tab, "Load a CSV to see performance heatmaps"),
            (self.advanced_tab, "Load a CSV to see advanced metrics"),
            (self.trades_tab, "Load a CSV to see trade history")
        ]:
            ttk.Label(tab, text=text, style='Info.TLabel').pack(pady=50)

    def import_csv(self):
        """Import QuantConnect CSV file - FLEXIBLE VERSION"""

        file_path = filedialog.askopenfilename(
            title="Select QuantConnect Trades CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Read CSV
            df = pd.read_csv(file_path)
            self.df = df

            # Detect P&L column
            pnl_candidates = ['Net Profit', 'Profit Loss', 'PnL', 'P&L', 'Profit', 'Net P&L']
            self.pnl_column = None

            for col in pnl_candidates:
                if col in df.columns:
                    self.pnl_column = col
                    break

            if self.pnl_column is None:
                if 'Entry Price' in df.columns and 'Exit Price' in df.columns and 'Quantity' in df.columns:
                    self.df['Net Profit'] = (df['Exit Price'] - df['Entry Price']) * df['Quantity']
                    self.pnl_column = 'Net Profit'
                else:
                    messagebox.showerror("Error", "Cannot find P&L column")
                    return

            # Add missing columns
            if 'Total Fees' not in self.df.columns:
                self.df['Total Fees'] = 0

            # Parse dates
            for date_col in ['Entry Time', 'Exit Time']:
                if date_col in self.df.columns:
                    try:
                        self.df[date_col] = pd.to_datetime(self.df[date_col])
                    except:
                        pass

            # Calculate duration if not present
            if 'Duration' not in self.df.columns:
                if 'Entry Time' in self.df.columns and 'Exit Time' in self.df.columns:
                    self.df['Duration'] = (self.df['Exit Time'] - self.df['Entry Time']).dt.days

            # Update UI
            self.file_label.config(text=f"Loaded: {len(self.df)} trades")
            self.main_window.update_status(f"Imported {len(self.df)} trades")

            # Run all analyses
            self.analyze_all()

            messagebox.showinfo("Success", f"Loaded {len(self.df)} trades!\n\nExplore the tabs to see comprehensive analysis.")

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import:\n{e}")

    def load_sample_data(self):
        """Generate realistic sample data"""

        np.random.seed(42)
        n_trades = 100

        # Generate dates
        start_dates = pd.date_range('2024-01-01', periods=n_trades, freq='2D')

        data = {
            'Entry Time': start_dates,
            'Exit Time': start_dates + pd.Timedelta(days=np.random.randint(5, 30)),
            'Symbol': ['SPY'] * n_trades,
            'Quantity': [1] * n_trades,
        }

        self.df = pd.DataFrame(data)

        # Generate realistic P&L (70% win rate, realistic distribution)
        wins = int(n_trades * 0.7)
        pnls = []

        for i in range(n_trades):
            if i < wins:
                # Wins: $50-150, occasional big win
                if np.random.random() < 0.1:
                    pnls.append(np.random.uniform(200, 300))  # Big win
                else:
                    pnls.append(np.random.uniform(50, 150))
            else:
                # Losses: -$100 to -$300
                if np.random.random() < 0.15:
                    pnls.append(np.random.uniform(-500, -300))  # Big loss
                else:
                    pnls.append(np.random.uniform(-200, -100))

        np.random.shuffle(pnls)
        self.df['Net Profit'] = pnls
        self.df['Total Fees'] = np.random.uniform(1, 5, n_trades)
        self.df['Duration'] = (self.df['Exit Time'] - self.df['Entry Time']).dt.days

        # Add MAE/MFE for sample data
        mae_values = []
        mfe_values = []

        for pnl in pnls:
            if pnl > 0:  # Winning trade
                mae = np.random.uniform(-50, -5)  # Small drawdown
                mfe = pnl * np.random.uniform(1.0, 1.3)  # MFE > final
            else:  # Losing trade
                mae = pnl * np.random.uniform(1.0, 1.5)  # MAE worse than final
                mfe = np.random.uniform(5, 30)  # Was up before losing

            mae_values.append(mae)
            mfe_values.append(mfe)

        self.df['MAE'] = mae_values
        self.df['MFE'] = mfe_values

        self.pnl_column = 'Net Profit'

        self.file_label.config(text=f"Sample: {len(self.df)} trades")
        self.main_window.update_status("Sample data generated")

        self.analyze_all()

        messagebox.showinfo("Sample Data",
                          "Generated 100 realistic trades with:\n"
                          "- 70% win rate\n"
                          "- MAE/MFE tracking\n"
                          "- Realistic P&L distribution")

    def analyze_all(self):
        """Run all analyses and populate tabs"""

        if self.df is None or self.pnl_column is None:
            return

        # Clear all tabs
        for tab in [self.overview_tab, self.charts_tab, self.mae_mfe_tab,
                    self.heatmap_tab, self.advanced_tab, self.trades_tab]:
            for widget in tab.winfo_children():
                widget.destroy()

        # Populate each tab
        self.create_overview_tab()
        self.create_charts_tab()
        self.create_mae_mfe_tab()
        self.create_heatmap_tab()
        self.create_advanced_tab()
        self.create_trades_tab()

        self.main_window.update_status("Complete analysis finished")

    def create_overview_tab(self):
        """Create overview metrics tab"""

        # Scrollable container
        canvas = tk.Canvas(self.overview_tab, highlightthickness=0)
        style_canvas(canvas)
        scrollbar = ttk.Scrollbar(self.overview_tab, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        pnl_col = self.pnl_column

        # === QUICK STATS ===
        stats_frame = ttk.LabelFrame(scrollable, text="Quick Statistics", padding=20)
        stats_frame.pack(fill='x', padx=20, pady=10)

        total = len(self.df)
        wins = len(self.df[self.df[pnl_col] > 0])
        losses = len(self.df[self.df[pnl_col] < 0])
        win_rate = (wins / total * 100) if total > 0 else 0

        total_pnl = self.df[pnl_col].sum()
        avg_pnl = self.df[pnl_col].mean()

        stats_text = f"""Total Trades:        {total}
Winning Trades:      {wins} ({win_rate:.1f}%)
Losing Trades:       {losses} ({(losses/total*100):.1f}%)

Total P&L:           ${total_pnl:,.2f}
Average P&L:         ${avg_pnl:,.2f}"""

        color = C["up"] if total_pnl >= 0 else C["down"]
        ttk.Label(stats_frame, text=stats_text, font=('Monaco', 12, 'bold'),
                 foreground=color, justify='left').pack(anchor='w')

        # === P&L BREAKDOWN ===
        pnl_frame = ttk.LabelFrame(scrollable, text="P&L Analysis", padding=20)
        pnl_frame.pack(fill='x', padx=20, pady=10)

        wins_df = self.df[self.df[pnl_col] > 0]
        losses_df = self.df[self.df[pnl_col] < 0]

        avg_win = wins_df[pnl_col].mean() if len(wins_df) > 0 else 0
        avg_loss = losses_df[pnl_col].mean() if len(losses_df) > 0 else 0

        pnl_text = f"""Average Win:         ${avg_win:,.2f}
Average Loss:        ${avg_loss:,.2f}
Largest Win:         ${self.df[pnl_col].max():,.2f}
Largest Loss:        ${self.df[pnl_col].min():,.2f}

Gross Profit:        ${wins_df[pnl_col].sum():,.2f}
Gross Loss:          ${abs(losses_df[pnl_col].sum()):,.2f}"""

        ttk.Label(pnl_frame, text=pnl_text, font=('Monaco', 11),
                 justify='left').pack(anchor='w')

        # === RISK METRICS ===
        risk_frame = ttk.LabelFrame(scrollable, text="Risk Metrics", padding=20)
        risk_frame.pack(fill='x', padx=20, pady=10)

        gross_profit = wins_df[pnl_col].sum() if len(wins_df) > 0 else 0
        gross_loss = abs(losses_df[pnl_col].sum()) if len(losses_df) > 0 else 0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0

        risk_reward = (avg_win / abs(avg_loss)) if avg_loss != 0 else 0
        expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)

        # Max drawdown
        cumulative = self.df[pnl_col].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = cumulative - running_max
        max_dd = drawdown.min()
        max_dd_pct = (max_dd / running_max.max() * 100) if running_max.max() > 0 else 0

        # Calculate recovery factor properly
        recovery_factor = (total_pnl / abs(max_dd)) if max_dd != 0 else 0

        risk_text = f"""Profit Factor:       {profit_factor:.2f}
        Risk/Reward Ratio:   {risk_reward:.2f}
        Expectancy:          ${expectancy:,.2f}

        Max Drawdown:        ${max_dd:,.2f} ({max_dd_pct:.1f}%)
        Recovery Factor:     {recovery_factor:.2f}"""

        ttk.Label(risk_frame, text=risk_text, font=('Monaco', 11),
                 justify='left').pack(anchor='w')

        # === DURATION ===
        if 'Duration' in self.df.columns:
            dur_frame = ttk.LabelFrame(scrollable, text="Trade Duration", padding=20)
            dur_frame.pack(fill='x', padx=20, pady=10)

            avg_dur = self.df['Duration'].mean()
            median_dur = self.df['Duration'].median()

            dur_text = f"""Average Duration:    {avg_dur:.1f} days
Median Duration:     {median_dur:.1f} days
Shortest Trade:      {self.df['Duration'].min()} days
Longest Trade:       {self.df['Duration'].max()} days"""

            ttk.Label(dur_frame, text=dur_text, font=('Monaco', 11),
                     justify='left').pack(anchor='w')

    def create_charts_tab(self):
        """Create basic charts tab"""

        import matplotlib
        matplotlib.rcParams.update(chart_colors())

        pnl_col = self.pnl_column

        # Create figure
        fig = Figure(figsize=(10, 6), dpi=70)
        fig.patch.set_facecolor(C["bg"])

        # 1. Equity Curve
        ax1 = fig.add_subplot(3, 2, 1)
        ax1.set_facecolor(C["card_bg"])
        cumulative = self.df[pnl_col].cumsum()
        ax1.plot(cumulative.values, linewidth=2, color=C["accent"])
        ax1.axhline(y=0, color=C["down"], linestyle='--', alpha=0.3)
        ax1.fill_between(range(len(cumulative)), cumulative.values, 0,
                        where=(cumulative.values >= 0), alpha=0.3, color=C["up"])
        ax1.fill_between(range(len(cumulative)), cumulative.values, 0,
                        where=(cumulative.values < 0), alpha=0.3, color=C["down"])
        ax1.set_title('Equity Curve', fontsize=10, fontweight='bold', color=C["dim"])
        ax1.set_xlabel('Trade #', fontsize=8, color=C["dim"])
        ax1.set_ylabel('Cumulative P&L ($)', fontsize=8, color=C["dim"])
        ax1.tick_params(labelsize=7, colors=C["dim"])
        ax1.grid(True, alpha=0.3, color=C["card_border"])

        # 2. Win/Loss Distribution
        ax2 = fig.add_subplot(3, 2, 2)
        ax2.set_facecolor(C["card_bg"])
        wins = self.df[self.df[pnl_col] > 0][pnl_col]
        losses = self.df[self.df[pnl_col] < 0][pnl_col]

        if len(wins) > 0 or len(losses) > 0:
            ax2.hist([wins, losses], bins=20, label=['Wins', 'Losses'],
                    color=[C["up"], C["down"]], alpha=0.7)
            ax2.set_title('Win/Loss Distribution', fontsize=10, fontweight='bold', color=C["dim"])
            ax2.set_xlabel('P&L ($)', fontsize=8, color=C["dim"])
            ax2.set_ylabel('Frequency', fontsize=8, color=C["dim"])
            ax2.legend(fontsize=7)
            ax2.tick_params(labelsize=7, colors=C["dim"])
            ax2.grid(True, alpha=0.3, color=C["card_border"])

        # 3. Drawdown Chart
        ax3 = fig.add_subplot(3, 2, 3)
        ax3.set_facecolor(C["card_bg"])
        cumulative = self.df[pnl_col].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = cumulative - running_max
        ax3.fill_between(range(len(drawdown)), drawdown.values, 0,
                        color=C["down"], alpha=0.5)
        ax3.set_title('Drawdown', fontsize=10, fontweight='bold', color=C["dim"])
        ax3.set_xlabel('Trade #', fontsize=8, color=C["dim"])
        ax3.set_ylabel('Drawdown ($)', fontsize=8, color=C["dim"])
        ax3.tick_params(labelsize=7, colors=C["dim"])
        ax3.grid(True, alpha=0.3, color=C["card_border"])

        # 4. Trade Duration
        if 'Duration' in self.df.columns:
            ax4 = fig.add_subplot(3, 2, 4)
            ax4.set_facecolor(C["card_bg"])
            ax4.hist(self.df['Duration'], bins=20, color=C["accent"], alpha=0.7, edgecolor=C["card_border"])
            ax4.set_title('Trade Duration Distribution', fontsize=10, fontweight='bold', color=C["dim"])
            ax4.set_xlabel('Days', fontsize=8, color=C["dim"])
            ax4.set_ylabel('Frequency', fontsize=8, color=C["dim"])
            ax4.tick_params(labelsize=7, colors=C["dim"])
            ax4.grid(True, alpha=0.3, color=C["card_border"])

        # 5. P&L by Trade Number (colored)
        ax5 = fig.add_subplot(3, 2, 5)
        ax5.set_facecolor(C["card_bg"])
        colors = [C["up"] if x > 0 else C["down"] for x in self.df[pnl_col]]
        ax5.bar(range(len(self.df)), self.df[pnl_col], color=colors, alpha=0.7)
        ax5.axhline(y=0, color=C["dim"], linewidth=0.5)
        ax5.set_title('P&L by Trade', fontsize=10, fontweight='bold', color=C["dim"])
        ax5.set_xlabel('Trade #', fontsize=8, color=C["dim"])
        ax5.set_ylabel('P&L ($)', fontsize=8, color=C["dim"])
        ax5.tick_params(labelsize=7, colors=C["dim"])
        ax5.grid(True, alpha=0.3, color=C["card_border"])

        # 6. Cumulative Win/Loss Count
        ax6 = fig.add_subplot(3, 2, 6)
        ax6.set_facecolor(C["card_bg"])
        wins_cumsum = (self.df[pnl_col] > 0).cumsum()
        losses_cumsum = (self.df[pnl_col] < 0).cumsum()
        ax6.plot(wins_cumsum.values, color=C["up"], linewidth=2, label='Wins')
        ax6.plot(losses_cumsum.values, color=C["down"], linewidth=2, label='Losses')
        ax6.set_title('Cumulative Wins/Losses', fontsize=10, fontweight='bold', color=C["dim"])
        ax6.set_xlabel('Trade #', fontsize=8, color=C["dim"])
        ax6.set_ylabel('Count', fontsize=8, color=C["dim"])
        ax6.legend(fontsize=7)
        ax6.tick_params(labelsize=7, colors=C["dim"])
        ax6.grid(True, alpha=0.3, color=C["card_border"])

        fig.tight_layout()

        # Embed
        canvas = FigureCanvasTkAgg(fig, master=self.charts_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def create_mae_mfe_tab(self):
        """Create MAE/MFE analysis tab with scatter plot"""

        # Check if MAE/MFE exist
        mae_col = None
        mfe_col = None

        for col in self.df.columns:
            if 'mae' in col.lower() or 'adverse' in col.lower():
                mae_col = col
            if 'mfe' in col.lower() or 'favorable' in col.lower():
                mfe_col = col

        if not (mae_col and mfe_col):
            # No MAE/MFE data
            frame = ttk.Frame(self.mae_mfe_tab)
            frame.pack(fill='both', expand=True, padx=20, pady=20)

            text = """MAE/MFE DATA NOT FOUND

MAE (Maximum Adverse Excursion) and MFE (Maximum Favorable Excursion)
are not in your CSV file.

These metrics show:
- MAE: Worst point the trade reached before closing
- MFE: Best point the trade reached before closing

They help optimize exit strategies!

To get MAE/MFE data:
1. Your algorithm tracks them
2. Import the log file to extract them
3. Or generate sample data to see example"""

            ttk.Label(frame, text=text, font=('Monaco', 11),
                     justify='left').pack(pady=20)

            ttk.Button(frame, text="Import MAE/MFE from Logs",
                      command=self.import_logs_for_mae_mfe,
                      style='Big.TButton').pack(pady=10)

            return

        # Has MAE/MFE - create analysis
        import matplotlib
        matplotlib.rcParams.update(chart_colors())

        pnl_col = self.pnl_column

        # Create figure with multiple plots
        fig = Figure(figsize=(10, 6), dpi=70)
        fig.patch.set_facecolor(C["bg"])

        # 1. MAE/MFE Scatter Plot (Most Important!)
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_facecolor(C["card_bg"])

        wins = self.df[self.df[pnl_col] > 0]
        losses = self.df[self.df[pnl_col] < 0]

        if len(wins) > 0:
            ax1.scatter(wins[mfe_col], wins[mae_col],
                       c=C["up"], alpha=0.6, s=50, label='Wins', edgecolors=C["card_border"])
        if len(losses) > 0:
            ax1.scatter(losses[mfe_col], losses[mae_col],
                       c=C["down"], alpha=0.6, s=50, label='Losses', edgecolors=C["card_border"])

        ax1.axhline(y=0, color=C["dim"], linestyle='--', alpha=0.3)
        ax1.axvline(x=0, color=C["dim"], linestyle='--', alpha=0.3)
        ax1.set_title('MAE vs MFE Scatter Plot', fontsize=11, fontweight='bold', color=C["dim"])
        ax1.set_xlabel('MFE (Max Favorable $)', fontsize=9, color=C["dim"])
        ax1.set_ylabel('MAE (Max Adverse $)', fontsize=9, color=C["dim"])
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3, color=C["card_border"])
        ax1.tick_params(labelsize=8, colors=C["dim"])

        # 2. MAE Distribution
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.set_facecolor(C["card_bg"])
        ax2.hist(self.df[mae_col], bins=30, color=C["down"], alpha=0.7, edgecolor=C["card_border"])
        ax2.axvline(self.df[mae_col].mean(), color=C["down"],
                   linestyle='--', linewidth=2, label=f'Mean: ${self.df[mae_col].mean():.2f}')
        ax2.set_title('MAE Distribution', fontsize=11, fontweight='bold', color=C["dim"])
        ax2.set_xlabel('MAE ($)', fontsize=9, color=C["dim"])
        ax2.set_ylabel('Frequency', fontsize=9, color=C["dim"])
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3, color=C["card_border"])
        ax2.tick_params(labelsize=8, colors=C["dim"])

        # 3. MFE Distribution
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.set_facecolor(C["card_bg"])
        ax3.hist(self.df[mfe_col], bins=30, color=C["up"], alpha=0.7, edgecolor=C["card_border"])
        ax3.axvline(self.df[mfe_col].mean(), color=C["up"],
                   linestyle='--', linewidth=2, label=f'Mean: ${self.df[mfe_col].mean():.2f}')
        ax3.set_title('MFE Distribution', fontsize=11, fontweight='bold', color=C["dim"])
        ax3.set_xlabel('MFE ($)', fontsize=9, color=C["dim"])
        ax3.set_ylabel('Frequency', fontsize=9, color=C["dim"])
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3, color=C["card_border"])
        ax3.tick_params(labelsize=8, colors=C["dim"])

        # 4. Efficiency Analysis (Final P&L vs MFE)
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.set_facecolor(C["card_bg"])
        ax4.scatter(self.df[mfe_col], self.df[pnl_col],
                   c=[C["up"] if x > 0 else C["down"] for x in self.df[pnl_col]],
                   alpha=0.6, s=50, edgecolors=C["card_border"])

        # Add diagonal line (perfect capture)
        max_val = max(self.df[mfe_col].max(), self.df[pnl_col].max())
        ax4.plot([0, max_val], [0, max_val], color=C["dim"], linestyle='--', alpha=0.3, label='Perfect Capture')

        ax4.set_title('Exit Efficiency (P&L vs MFE)', fontsize=11, fontweight='bold', color=C["dim"])
        ax4.set_xlabel('MFE - Max Profit Potential ($)', fontsize=9, color=C["dim"])
        ax4.set_ylabel('Final P&L ($)', fontsize=9, color=C["dim"])
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3, color=C["card_border"])
        ax4.tick_params(labelsize=8, colors=C["dim"])

        fig.tight_layout()

        # Create container with stats and chart
        container = ttk.Frame(self.mae_mfe_tab)
        container.pack(fill='both', expand=True)

        # Stats on left
        stats_frame = ttk.LabelFrame(container, text="MAE/MFE Statistics", padding=15)
        stats_frame.pack(side='left', fill='y', padx=10, pady=10)

        avg_mae = self.df[mae_col].mean()
        avg_mfe = self.df[mfe_col].mean()
        median_mae = self.df[mae_col].median()
        median_mfe = self.df[mfe_col].median()

        # Calculate efficiency
        efficiency = (self.df[pnl_col] / self.df[mfe_col] * 100).mean()

        stats_text = f"""AVERAGE MAE: ${avg_mae:,.2f}
(Avg worst drawdown)

AVERAGE MFE: ${avg_mfe:,.2f}
(Avg best profit)

MEDIAN MAE: ${median_mae:,.2f}
MEDIAN MFE: ${median_mfe:,.2f}

EXIT EFFICIENCY: {efficiency:.1f}%
(How much of MFE captured)

INTERPRETATION:
- Points above diagonal = Left money on table
- Points below diagonal = Took profit early
- Green points = Profitable exits
- Red points = Stopped out"""

        ttk.Label(stats_frame, text=stats_text, font=('Monaco', 10),
                 justify='left').pack(anchor='w')

        # Chart on right
        chart_frame = ttk.Frame(container)
        chart_frame.pack(side='right', fill='both', expand=True)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_heatmap_tab(self):
        """Create performance heatmaps"""

        if 'Exit Time' not in self.df.columns:
            ttk.Label(self.heatmap_tab,
                     text="Heatmaps require date information (Exit Time column)",
                     style='Info.TLabel').pack(pady=50)
            return

        import matplotlib
        matplotlib.rcParams.update(chart_colors())

        pnl_col = self.pnl_column

        # Prepare data
        self.df['Exit Date'] = pd.to_datetime(self.df['Exit Time']).dt.date
        self.df['Year'] = pd.to_datetime(self.df['Exit Time']).dt.year
        self.df['Month'] = pd.to_datetime(self.df['Exit Time']).dt.month
        self.df['Week'] = pd.to_datetime(self.df['Exit Time']).dt.isocalendar().week
        self.df['DayOfWeek'] = pd.to_datetime(self.df['Exit Time']).dt.dayofweek

        fig = Figure(figsize=(10, 6), dpi=70)
        fig.patch.set_facecolor(C["bg"])

        # 1. Monthly Performance Heatmap
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.set_facecolor(C["card_bg"])

        try:
            monthly_pnl = self.df.pivot_table(
                values=pnl_col,
                index='Year',
                columns='Month',
                aggfunc='sum',
                fill_value=0
            )

            im1 = ax1.imshow(monthly_pnl.values, cmap='RdYlGn', aspect='auto')
            ax1.set_xticks(range(12))
            ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], fontsize=8)
            ax1.set_yticks(range(len(monthly_pnl.index)))
            ax1.set_yticklabels(monthly_pnl.index, fontsize=8)
            ax1.set_title('Monthly P&L Heatmap', fontsize=11, fontweight='bold', color=C["dim"])
            ax1.tick_params(colors=C["dim"])

            # Add values
            for i in range(len(monthly_pnl.index)):
                for j in range(12):
                    val = monthly_pnl.values[i, j]
                    if not np.isnan(val):
                        text = ax1.text(j, i, f'${val:.0f}',
                                       ha="center", va="center",
                                       color="black" if abs(val) < 100 else "white",
                                       fontsize=7)

            fig.colorbar(im1, ax=ax1, label='P&L ($)')
        except Exception as e:
            ax1.text(0.5, 0.5, f'Monthly heatmap unavailable',
                    ha='center', va='center', transform=ax1.transAxes, color=C["dim"])

        # 2. Day of Week Performance
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.set_facecolor(C["card_bg"])

        try:
            dow_pnl = self.df.groupby('DayOfWeek')[pnl_col].agg(['sum', 'mean', 'count'])

            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            x = range(len(dow_pnl))

            bars = ax2.bar(x, dow_pnl['sum'],
                          color=[C["up"] if v > 0 else C["down"] for v in dow_pnl['sum']],
                          alpha=0.7, edgecolor=C["card_border"])

            ax2.set_xticks(x)
            ax2.set_xticklabels([days[i] for i in dow_pnl.index], fontsize=9)
            ax2.set_title('P&L by Day of Week', fontsize=11, fontweight='bold', color=C["dim"])
            ax2.set_ylabel('Total P&L ($)', fontsize=9, color=C["dim"])
            ax2.axhline(y=0, color=C["dim"], linewidth=0.5)
            ax2.grid(True, alpha=0.3, axis='y', color=C["card_border"])
            ax2.tick_params(colors=C["dim"])

            # Add count labels
            for i, (bar, count) in enumerate(zip(bars, dow_pnl['count'])):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(count)} trades',
                        ha='center', va='bottom' if height > 0 else 'top',
                        fontsize=7, color=C["dim"])
        except Exception as e:
            ax2.text(0.5, 0.5, 'Day of week analysis unavailable',
                    ha='center', va='center', transform=ax2.transAxes, color=C["dim"])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.heatmap_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def create_advanced_tab(self):
        """Create advanced metrics tab"""

        import matplotlib
        matplotlib.rcParams.update(chart_colors())

        pnl_col = self.pnl_column

        fig = Figure(figsize=(10, 6), dpi=70)
        fig.patch.set_facecolor(C["bg"])

        # 1. Rolling Win Rate
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_facecolor(C["card_bg"])
        window = min(20, len(self.df) // 5)  # Adaptive window
        if window > 0:
            rolling_wins = (self.df[pnl_col] > 0).rolling(window=window).mean() * 100
            ax1.plot(rolling_wins.values, linewidth=2, color=C["accent"])
            ax1.axhline(y=50, color=C["down"], linestyle='--', alpha=0.5, label='50% Win Rate')
            ax1.set_title(f'Rolling Win Rate ({window}-trade window)', fontsize=10, fontweight='bold', color=C["dim"])
            ax1.set_xlabel('Trade #', fontsize=9, color=C["dim"])
            ax1.set_ylabel('Win Rate (%)', fontsize=9, color=C["dim"])
            ax1.legend(fontsize=8)
            ax1.grid(True, alpha=0.3, color=C["card_border"])
            ax1.tick_params(labelsize=8, colors=C["dim"])

        # 2. P&L vs Trade Duration
        if 'Duration' in self.df.columns:
            ax2 = fig.add_subplot(2, 2, 2)
            ax2.set_facecolor(C["card_bg"])
            colors = [C["up"] if x > 0 else C["down"] for x in self.df[pnl_col]]
            ax2.scatter(self.df['Duration'], self.df[pnl_col],
                       c=colors, alpha=0.6, s=50, edgecolors=C["card_border"])
            ax2.axhline(y=0, color=C["dim"], linestyle='--', alpha=0.3)
            ax2.set_title('P&L vs Trade Duration', fontsize=10, fontweight='bold', color=C["dim"])
            ax2.set_xlabel('Duration (days)', fontsize=9, color=C["dim"])
            ax2.set_ylabel('P&L ($)', fontsize=9, color=C["dim"])
            ax2.grid(True, alpha=0.3, color=C["card_border"])
            ax2.tick_params(labelsize=8, colors=C["dim"])

        # 3. Consecutive Wins/Losses
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.set_facecolor(C["card_bg"])

        # Calculate streaks
        is_win = (self.df[pnl_col] > 0).astype(int)
        streaks = []
        current_streak = 0

        for val in is_win:
            if val == 1:
                current_streak = max(0, current_streak) + 1
            else:
                current_streak = min(0, current_streak) - 1
            streaks.append(current_streak)

        colors_streak = [C["up"] if x > 0 else C["down"] if x < 0 else C["dim"] for x in streaks]
        ax3.bar(range(len(streaks)), streaks, color=colors_streak, alpha=0.7)
        ax3.axhline(y=0, color=C["dim"], linewidth=0.5)
        ax3.set_title('Win/Loss Streaks', fontsize=10, fontweight='bold', color=C["dim"])
        ax3.set_xlabel('Trade #', fontsize=9, color=C["dim"])
        ax3.set_ylabel('Consecutive Wins/Losses', fontsize=9, color=C["dim"])
        ax3.grid(True, alpha=0.3, color=C["card_border"])
        ax3.tick_params(labelsize=8, colors=C["dim"])

        # 4. Profit Factor Over Time
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.set_facecolor(C["card_bg"])
        window = min(30, len(self.df) // 3)

        if window > 0:
            rolling_pf = []
            for i in range(window, len(self.df) + 1):
                window_data = self.df[pnl_col].iloc[i-window:i]
                wins_sum = window_data[window_data > 0].sum()
                loss_sum = abs(window_data[window_data < 0].sum())
                pf = wins_sum / loss_sum if loss_sum > 0 else 0
                rolling_pf.append(pf)

            ax4.plot(range(window, len(self.df) + 1), rolling_pf,
                    linewidth=2, color=C["accent"])
            ax4.axhline(y=1.0, color=C["down"], linestyle='--', alpha=0.5, label='Break Even (PF=1.0)')
            ax4.axhline(y=2.0, color=C["up"], linestyle='--', alpha=0.5, label='Excellent (PF=2.0)')
            ax4.set_title(f'Rolling Profit Factor ({window}-trade window)', fontsize=10, fontweight='bold', color=C["dim"])
            ax4.set_xlabel('Trade #', fontsize=9, color=C["dim"])
            ax4.set_ylabel('Profit Factor', fontsize=9, color=C["dim"])
            ax4.legend(fontsize=7)
            ax4.grid(True, alpha=0.3, color=C["card_border"])
            ax4.tick_params(labelsize=8, colors=C["dim"])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.advanced_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def create_trades_tab(self):
        """Create trade history table - FULLY SCROLLABLE"""

        # Main container
        main_container = ttk.Frame(self.trades_tab)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Table container with BOTH scrollbars
        tree_container = ttk.Frame(main_container)
        tree_container.pack(fill='both', expand=True)

        # Create scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")

        # Position scrollbars
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        # Define columns
        columns = ['#', 'Entry', 'Exit', 'Days', 'P&L', 'Status']

        # Create treeview with SMALLER height
        tree = ttk.Treeview(tree_container, columns=columns, show='headings',
                        yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                        height=12)  # REDUCED from 20 to 12

        # Configure scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        # Pack tree
        tree.pack(fill='both', expand=True)

        # Configure columns with FIXED widths
        tree.heading('#', text='#')
        tree.column('#', width=50, minwidth=50, stretch=False)

        tree.heading('Entry', text='Entry')
        tree.column('Entry', width=100, minwidth=80, stretch=False)

        tree.heading('Exit', text='Exit')
        tree.column('Exit', width=100, minwidth=80, stretch=False)

        tree.heading('Days', text='Days')
        tree.column('Days', width=60, minwidth=50, stretch=False)

        tree.heading('P&L', text='P&L')
        tree.column('P&L', width=100, minwidth=80, stretch=False)

        tree.heading('Status', text='Status')
        tree.column('Status', width=70, minwidth=60, stretch=False)

        pnl_col = self.pnl_column

        # Populate data
        for i, row in self.df.iterrows():
            values = []

            # Trade number
            values.append(i + 1)

            # Entry date
            if 'Entry Time' in self.df.columns:
                entry = pd.to_datetime(row['Entry Time']).strftime('%Y-%m-%d') if pd.notnull(row['Entry Time']) else 'N/A'
                values.append(entry)
            else:
                values.append('N/A')

            # Exit date
            if 'Exit Time' in self.df.columns:
                exit_time = pd.to_datetime(row['Exit Time']).strftime('%Y-%m-%d') if pd.notnull(row['Exit Time']) else 'N/A'
                values.append(exit_time)
            else:
                values.append('N/A')

            # Duration
            if 'Duration' in self.df.columns:
                values.append(f"{row['Duration']:.0f}")
            else:
                values.append('N/A')

            # P&L
            pnl = f"${row[pnl_col]:.2f}"
            values.append(pnl)

            # Status
            status = 'WIN' if row[pnl_col] > 0 else 'LOSS' if row[pnl_col] < 0 else 'BE'
            values.append(status)

            # Insert with tags for coloring
            tags = ('win',) if row[pnl_col] > 0 else ('loss',) if row[pnl_col] < 0 else ()
            tree.insert('', 'end', values=values, tags=tags)

        # Configure row colors
        tree.tag_configure('win', foreground=C["up"])
        tree.tag_configure('loss', foreground=C["down"])

        # Summary and buttons below table
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill='x', pady=(10, 0))

        # Summary on left
        total_pnl = self.df[pnl_col].sum()
        wins = len(self.df[self.df[pnl_col] > 0])
        losses = len(self.df[self.df[pnl_col] < 0])

        summary = f"Total: {len(self.df)} trades | Wins: {wins} | Losses: {losses} | Total P&L: ${total_pnl:,.2f}"
        ttk.Label(bottom_frame, text=summary, font=('Helvetica', 10, 'bold')).pack(side='left')

        # Export buttons on right
        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(side='right')

        ttk.Button(btn_frame, text="Export Excel",
                command=self.export_excel).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Export CSV",
                command=self.export_csv).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="View All Details",
                command=self.view_full_details).pack(side='left', padx=2)

    def import_logs_for_mae_mfe(self):
        """Import MAE/MFE from logs"""

        file_path = filedialog.askopenfilename(
            title="Select QuantConnect Logs File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                log_content = f.read()

            import re

            mae_pattern = r'MAE:\s*\$?(-?\d+\.?\d*)'
            mfe_pattern = r'MFE:\s*\$?(-?\d+\.?\d*)'

            mae_matches = re.findall(mae_pattern, log_content)
            mfe_matches = re.findall(mfe_pattern, log_content)

            if mae_matches and mfe_matches and len(mae_matches) == len(mfe_matches):
                mae_values = [float(x) for x in mae_matches]
                mfe_values = [float(x) for x in mfe_matches]

                if len(mae_values) == len(self.df):
                    self.df['MAE'] = mae_values
                    self.df['MFE'] = mfe_values

                    messagebox.showinfo("Success",
                                      f"Extracted {len(mae_values)} MAE/MFE values!")

                    self.analyze_all()
                else:
                    messagebox.showwarning("Mismatch",
                                         f"Found {len(mae_values)} MAE/MFE but {len(self.df)} trades")
            else:
                messagebox.showerror("Not Found", "Could not find MAE/MFE in logs")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse logs:\n{e}")

    def export_excel(self):
        """Export to Excel"""

        if self.df is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if file_path:
            try:
                self.df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{e}")

    def export_csv(self):
        """Export to CSV"""

        if self.df is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{e}")
    def view_full_details(self):
        """View all trade details in popup"""

        if self.df is None:
            return

        # Create popup
        popup = tk.Toplevel(self.frame)
        popup.title("All Trade Details")
        popup.geometry("1200x700")
        popup.configure(bg=C["bg"])

        popup.transient(self.frame)
        popup.grab_set()

        # Create text widget with scrollbars
        text_frame = ttk.Frame(popup)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)

        vsb = ttk.Scrollbar(text_frame, orient="vertical")
        hsb = ttk.Scrollbar(text_frame, orient="horizontal")

        text = tk.Text(text_frame, wrap='none', font=('Monaco', 9),
                    yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        style_text(text)

        vsb.config(command=text.yview)
        hsb.config(command=text.xview)

        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill ='x')
        text.pack(fill='both', expand=True)

        # Insert full dataframe
        text.insert('1.0', self.df.to_string(max_rows=None, max_cols=None))
        text.config(state='disabled')

        # Close button
        ttk.Button(popup, text="Close", command=popup.destroy,
                style='Big.TButton').pack(pady=10)
