"""
Results Tab - Analyze QuantConnect backtest results
Shows comprehensive metrics including MAE/MFE in percentages
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from pathlib import Path

from .theme import C, FONT, style_canvas, style_listbox, style_text

class ResultsTab:
    def __init__(self, parent, main_window):
        self.frame = ttk.Frame(parent)
        self.main_window = main_window
        self.current_results = None
        
        self.create_ui()
    
    def create_ui(self):
        """Create results analyzer interface"""
        
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=25, pady=15)
        
        ttk.Label(header_frame, text="Results Analyzer", 
                 style='Title.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Upload QuantConnect results CSV for comprehensive analysis", 
                 style='Subtitle.TLabel').pack(anchor='w', pady=(5, 0))
        
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', padx=25, pady=15)
        
        # Upload section
        upload_frame = ttk.LabelFrame(self.frame, text="Upload Results", padding=20)
        upload_frame.pack(fill='x', padx=25, pady=10)
        
        ttk.Label(upload_frame, text="Upload your QuantConnect backtest results CSV:", 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        btn_frame = ttk.Frame(upload_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Browse for CSV File",
                  command=self.browse_file,
                  style='Big.TButton').pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Load Sample Data (Demo)",
                  command=self.load_sample_data,
                  style='Big.TButton').pack(side='left', padx=5)
        
        # Recent files
        self.recent_frame = ttk.Frame(upload_frame)
        self.recent_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Label(self.recent_frame, text="Recent files:", 
                 style='Info.TLabel').pack(anchor='w')
        
        self.recent_listbox = tk.Listbox(self.recent_frame, height=3)
        style_listbox(self.recent_listbox)
        self.recent_listbox.pack(fill='x', pady=5)
        self.recent_listbox.bind('<Double-Button-1>', self.load_recent_file)
        
        self.load_recent_files()
        
        # Results display area (hidden until data loaded)
        self.results_frame = ttk.Frame(self.frame)
        # Don't pack yet - will pack when data is loaded
        
        self.create_results_display()
    
    def create_results_display(self):
        """Create the results display widgets"""
        
        # Scrollable container
        canvas = tk.Canvas(self.results_frame, highlightthickness=0)
        style_canvas(canvas)
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Results content
        self.results_content = scrollable

        # Enable trackpad scrolling
        from .scroll_helper import enable_scroll
        enable_scroll(canvas, scrollable)
    
    def browse_file(self):
        """Browse for CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select QuantConnect Results CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~/Desktop")
        )
        
        if file_path:
            self.load_and_analyze(file_path)
    
    def load_recent_file(self, event=None):
        """Load file from recent files list"""
        selection = self.recent_listbox.curselection()
        if selection:
            file_path = self.recent_listbox.get(selection[0])
            if os.path.exists(file_path):
                self.load_and_analyze(file_path)
            else:
                messagebox.showerror("Error", "File no longer exists")
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        try:
            from core.analyzer import ResultsAnalyzer
            
            # Create analyzer with no file (will use sample data)
            analyzer = ResultsAnalyzer(None)
            analyzer.df = []  # Empty to trigger sample generation
            analyzer.generate_sample_trades()
            
            # Calculate metrics
            results = analyzer.analyze()
            
            # Display results
            self.display_results(results, analyzer, "Sample Data (Demo)")
            
            self.main_window.update_status("Sample data loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sample data: {e}")
    
    def load_and_analyze(self, file_path):
        """Load CSV and run analysis"""
        try:
            self.main_window.update_status(f"Loading {os.path.basename(file_path)}...")
            
            from core.analyzer import ResultsAnalyzer
            
            # Create analyzer
            analyzer = ResultsAnalyzer(file_path)
            
            # Load CSV
            analyzer.load_csv()
            
            # Run analysis
            results = analyzer.analyze()
            
            # Store current results
            self.current_results = {
                'file_path': file_path,
                'metrics': results,
                'analyzer': analyzer
            }
            
            # Display results
            self.display_results(results, analyzer, os.path.basename(file_path))
            
            # Add to recent files
            self.add_recent_file(file_path)
            
            self.main_window.update_status(f"Analysis complete: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze results:\n{e}")
            self.main_window.update_status("Analysis failed")
    
    def display_results(self, metrics, analyzer, filename):
        """Display comprehensive results"""
        
        # Clear previous results
        for widget in self.results_content.winfo_children():
            widget.destroy()
        
        # Show results frame
        self.results_frame.pack(fill='both', expand=True, padx=25, pady=10)
        
        # Get theme settings
        theme = self.load_theme_settings()
        
        # Header
        header = ttk.Frame(self.results_content)
        header.pack(fill='x', pady=10, padx=20)
        
        ttk.Label(header, text=f"Results: {filename}", 
                 style='Title.TLabel').pack(anchor='w')
        
        # === OVERVIEW CARD ===
        overview = ttk.LabelFrame(self.results_content, text="Overview", padding=15)
        overview.pack(fill='x', padx=20, pady=10)
        
        overview_text = f"""
Total Trades:        {metrics.get('total_trades', 0)}
Winning Trades:      {metrics.get('winning_trades', 0)} ({metrics.get('win_rate', 0):.1f}%)
Losing Trades:       {metrics.get('losing_trades', 0)} ({metrics.get('loss_rate', 0):.1f}%)
Breakeven Trades:    {metrics.get('breakeven_trades', 0)}
        """.strip()
        
        ttk.Label(overview, text=overview_text, font=('Monaco', 11), 
                 justify='left').pack(anchor='w')
        
        # === P&L CARD ===
        pnl = ttk.LabelFrame(self.results_content, text="Profit & Loss", padding=15)
        pnl.pack(fill='x', padx=20, pady=10)
        
        total_pnl = metrics.get('total_pnl', 0)
        pnl_color = '#28a745' if total_pnl >= 0 else '#dc3545'
        
        pnl_text = f"""
Total P&L:           ${total_pnl:,.2f}
Total Return:        {metrics.get('total_return_pct', 0):.2f}%
Annualized Return:   {metrics.get('annualized_return_pct', 0):.2f}%

Average P&L:         ${metrics.get('avg_pnl', 0):,.2f}
Median P&L:          ${metrics.get('median_pnl', 0):,.2f}

Average Win:         ${metrics.get('avg_win', 0):,.2f}
Average Loss:        ${metrics.get('avg_loss', 0):,.2f}

Largest Win:         ${metrics.get('largest_win', 0):,.2f}
Largest Loss:        ${metrics.get('largest_loss', 0):,.2f}

Gross Profit:        ${metrics.get('gross_profit', 0):,.2f}
Gross Loss:          ${abs(metrics.get('gross_loss', 0)):,.2f}
        """.strip()
        
        ttk.Label(pnl, text=pnl_text, font=('Monaco', 11), 
                 justify='left').pack(anchor='w')
        
        # === MAE/MFE CARD (THE IMPORTANT ONE!) ===
        mae_mfe = ttk.LabelFrame(self.results_content, text="MAE / MFE Analysis", padding=15)
        mae_mfe.pack(fill='x', padx=20, pady=10)
        
        mae_mfe_text = f"""
AVERAGE MAE (Maximum Adverse Excursion):
  Percentage:        {metrics.get('avg_mae_pct', 0):.2f}% of max risk
  Dollar Amount:     ${metrics.get('avg_mae', 0):,.2f}

AVERAGE MFE (Maximum Favorable Excursion):
  Percentage:        {metrics.get('avg_mfe_pct', 0):.2f}% of max reward
  Dollar Amount:     ${metrics.get('avg_mfe', 0):,.2f}

MEDIAN MAE:          {metrics.get('median_mae_pct', 0):.2f}%  (${metrics.get('median_mae', 0):,.2f})
MEDIAN MFE:          {metrics.get('median_mfe_pct', 0):.2f}%  (${metrics.get('median_mfe', 0):,.2f})

WORST MAE:           {metrics.get('max_mae_pct', 0):.2f}%  (${metrics.get('max_mae', 0):,.2f})
BEST MFE:            {metrics.get('max_mfe_pct', 0):.2f}%  (${metrics.get('max_mfe', 0):,.2f})

Profit Capture Efficiency:  {metrics.get('avg_profit_capture', 0):.1f}%
(How much of MFE was actually captured as profit)
        """.strip()
        
        ttk.Label(mae_mfe, text=mae_mfe_text, font=('Monaco', 11), 
                 justify='left').pack(anchor='w')
        
        # === RISK METRICS CARD ===
        risk = ttk.LabelFrame(self.results_content, text="Risk Metrics", padding=15)
        risk.pack(fill='x', padx=20, pady=10)
        
        risk_text = f"""
Risk/Reward Ratio:   {metrics.get('risk_reward_ratio', 0):.2f}
Expectancy:          ${metrics.get('expectancy', 0):,.2f}
Profit Factor:       {metrics.get('profit_factor', 0):.2f}

Sharpe Ratio:        {metrics.get('sharpe_ratio', 0):.2f}
Sortino Ratio:       {metrics.get('sortino_ratio', 0):.2f}
Calmar Ratio:        {metrics.get('calmar_ratio', 0):.2f}

Max Drawdown:        {metrics.get('max_drawdown_pct', 0):.2f}%
Average Drawdown:    {metrics.get('avg_drawdown_pct', 0):.2f}%
Current Drawdown:    {metrics.get('current_drawdown_pct', 0):.2f}%
        """.strip()
        
        ttk.Label(risk, text=risk_text, font=('Monaco', 11), 
                 justify='left').pack(anchor='w')
        
        # === DURATION & STREAKS ===
        duration = ttk.LabelFrame(self.results_content, text="Duration & Streaks", padding=15)
        duration.pack(fill='x', padx=20, pady=10)
        
        duration_text = f"""
Average Hold:        {metrics.get('avg_hold_days', 0):.1f} days
Median Hold:         {metrics.get('median_hold_days', 0):.1f} days
Max Hold:            {metrics.get('max_hold_days', 0)} days
Min Hold:            {metrics.get('min_hold_days', 0)} days

Max Consecutive Wins:   {metrics.get('max_consecutive_wins', 0)}
Max Consecutive Losses: {metrics.get('max_consecutive_losses', 0)}
        """.strip()
        
        ttk.Label(duration, text=duration_text, font=('Monaco', 11), 
                 justify='left').pack(anchor='w')
        
        # === ACTION BUTTONS ===
        btn_frame = ttk.Frame(self.results_content)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame, text="Export Full Report",
                  command=lambda: self.export_report(metrics, filename)).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="View All Trades",
                  command=lambda: self.view_trades(analyzer)).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Save Results",
                  command=lambda: self.save_results(metrics, filename)).pack(side='left', padx=5)
    
    def export_report(self, metrics, filename):
        """Export full report to text file"""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"report_{filename.replace('.csv', '')}.txt"
        )
        
        if save_path:
            try:
                with open(save_path, 'w') as f:
                    f.write("="*80 + "\n")
                    f.write(f"  BACKTEST RESULTS REPORT: {filename}\n")
                    f.write("="*80 + "\n\n")
                    
                    for key, value in metrics.items():
                        if isinstance(value, dict):
                            f.write(f"\n{key}:\n")
                            for k, v in value.items():
                                f.write(f"  {k}: {v}\n")
                        else:
                            f.write(f"{key}: {value}\n")
                
                messagebox.showinfo("Success", f"Report exported to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {e}")
    
    def view_trades(self, analyzer):
        """View all trades in a table"""
        trades_window = tk.Toplevel(self.frame)
        trades_window.title("All Trades")
        trades_window.geometry("1000x600")
        
        # Get trades DataFrame
        df = analyzer.get_trades_dataframe()
        
        # Create text widget with trades
        text = scrolledtext.ScrolledText(trades_window, wrap='none', font=('Monaco', 10))
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Insert trades
        text.insert('1.0', df.to_string())
        text.config(state='disabled')
        
        ttk.Button(trades_window, text="Close", command=trades_window.destroy).pack(pady=10)
    
    def save_results(self, metrics, filename):
        """Save results to JSON"""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"results_{filename.replace('.csv', '')}.json",
            initialdir="results"
        )
        
        if save_path:
            try:
                # Convert numpy types to native Python
                serializable_metrics = {}
                for key, value in metrics.items():
                    if hasattr(value, 'item'):  # numpy type
                        serializable_metrics[key] = value.item()
                    else:
                        serializable_metrics[key] = value
                
                with open(save_path, 'w') as f:
                    json.dump(serializable_metrics, f, indent=2)
                
                messagebox.showinfo("Success", f"Results saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {e}")
    
    def load_recent_files(self):
        """Load recent files list"""
        # Check results folder for CSVs
        results_dir = Path("results")
        if results_dir.exists():
            csv_files = list(results_dir.glob("*.csv"))
            for csv_file in sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                self.recent_listbox.insert(tk.END, str(csv_file))
    
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        # Add to top of listbox
        self.recent_listbox.insert(0, file_path)
        
        # Keep only 5 most recent
        if self.recent_listbox.size() > 5:
            self.recent_listbox.delete(5, tk.END)
    
    def load_theme_settings(self):
        """Load theme settings from settings file"""
        try:
            with open('config/settings.json', 'r') as f:
                settings = json.load(f)
                return settings.get('display', {}).get('theme', 'light')
        except:
            return 'light'