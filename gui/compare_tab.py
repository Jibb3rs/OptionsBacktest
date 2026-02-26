"""
Compare Tab - Side-by-side comparison of multiple backtest results
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path

from .theme import C, FONT, FONT_MONO, style_canvas, style_listbox, style_text

class CompareTab:
    def __init__(self, parent, main_window):
        self.frame = ttk.Frame(parent)
        self.main_window = main_window

        self.selected_files = []
        self.results_data = []

        self.create_ui()

    def create_ui(self):
        """Create comparison interface"""

        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=25, pady=15)

        ttk.Label(header_frame, text="Strategy Comparison",
                 style='Title.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Compare multiple backtest results side-by-side",
                 style='Subtitle.TLabel').pack(anchor='w', pady=(5, 0))

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', padx=25, pady=15)

        # File selection area
        selection_frame = ttk.LabelFrame(self.frame, text="Select Results to Compare", padding=20)
        selection_frame.pack(fill='x', padx=25, pady=10)

        ttk.Label(selection_frame, text="Add 2-5 result files to compare:",
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))

        # Buttons
        btn_frame = ttk.Frame(selection_frame)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(btn_frame, text="Add CSV File",
                  command=self.add_file).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Add JSON Results",
                  command=self.add_json_file).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Add Sample Data (Demo)",
                  command=self.add_sample_data).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Clear All",
                  command=self.clear_all).pack(side='left', padx=5)

        # Selected files list
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill='both', expand=True, pady=(10, 0))

        ttk.Label(list_frame, text="Selected files:", style='Info.TLabel').pack(anchor='w')

        # Scrollable listbox
        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill='both', expand=True, pady=5)

        list_scrollbar = ttk.Scrollbar(list_scroll_frame)
        list_scrollbar.pack(side='right', fill='y')

        self.files_listbox = tk.Listbox(list_scroll_frame, height=5,
                                        yscrollcommand=list_scrollbar.set)
        style_listbox(self.files_listbox)
        self.files_listbox.pack(side='left', fill='both', expand=True)
        list_scrollbar.config(command=self.files_listbox.yview)

        # Remove selected button
        ttk.Button(list_frame, text="Remove Selected",
                  command=self.remove_selected).pack(anchor='w', pady=5)

        # Compare button
        ttk.Button(selection_frame, text="Compare Results",
                  command=self.compare_results,
                  style='Big.TButton').pack(pady=10)

        # Comparison results area (hidden until comparison done)
        self.comparison_frame = ttk.Frame(self.frame)
        # Don't pack yet - will pack when comparison is done

        self.create_comparison_display()

    def create_comparison_display(self):
        """Create the comparison display area"""

        # Scrollable container
        canvas = tk.Canvas(self.comparison_frame, highlightthickness=0)
        style_canvas(canvas)
        scrollbar = ttk.Scrollbar(self.comparison_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Enable trackpad scrolling
        from .scroll_helper import enable_scroll
        enable_scroll(canvas, scrollable)

        self.comparison_content = scrollable

    def add_file(self):
        """Add CSV file to comparison"""
        file_path = filedialog.askopenfilename(
            title="Select Results CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~/Desktop")
        )

        if file_path:
            if len(self.selected_files) >= 5:
                messagebox.showwarning("Limit Reached", "Maximum 5 files can be compared at once")
                return

            self.selected_files.append(file_path)
            self.files_listbox.insert(tk.END, os.path.basename(file_path))
            self.main_window.update_status(f"Added {os.path.basename(file_path)}")

    def add_json_file(self):
        """Add JSON results file to comparison"""
        file_path = filedialog.askopenfilename(
            title="Select Results JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="results"
        )

        if file_path:
            if len(self.selected_files) >= 5:
                messagebox.showwarning("Limit Reached", "Maximum 5 files can be compared at once")
                return

            self.selected_files.append(file_path)
            self.files_listbox.insert(tk.END, os.path.basename(file_path))
            self.main_window.update_status(f"Added {os.path.basename(file_path)}")

    def add_sample_data(self):
        """Add sample data for demonstration"""
        if len(self.selected_files) >= 5:
            messagebox.showwarning("Limit Reached", "Maximum 5 files can be compared at once")
            return

        # Create sample data
        sample_name = f"Sample Data {len(self.selected_files) + 1}"
        self.selected_files.append(f"SAMPLE_{len(self.selected_files)}")
        self.files_listbox.insert(tk.END, sample_name)
        self.main_window.update_status(f"Added {sample_name}")

    def remove_selected(self):
        """Remove selected file from list"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.files_listbox.delete(index)
            del self.selected_files[index]
            self.main_window.update_status("File removed")

    def clear_all(self):
        """Clear all selected files"""
        if self.selected_files and messagebox.askyesno("Clear All", "Remove all selected files?"):
            self.files_listbox.delete(0, tk.END)
            self.selected_files.clear()
            self.results_data.clear()
            self.main_window.update_status("All files cleared")

    def compare_results(self):
        """Compare all selected results"""
        if len(self.selected_files) < 2:
            messagebox.showwarning("Not Enough Files",
                                 "Please select at least 2 files to compare")
            return

        try:
            self.main_window.update_status("Analyzing files for comparison...")

            # Load and analyze all files
            self.results_data = []
            for i, file_path in enumerate(self.selected_files):
                if file_path.startswith("SAMPLE_"):
                    # Generate sample data
                    metrics = self.generate_sample_metrics(i)
                    name = f"Sample {i+1}"
                else:
                    # Load actual file
                    if file_path.endswith('.json'):
                        metrics = self.load_json_results(file_path)
                    else:
                        metrics = self.load_csv_results(file_path)
                    name = os.path.basename(file_path)

                self.results_data.append({
                    'name': name,
                    'metrics': metrics
                })

            # Display comparison
            self.display_comparison()

            self.main_window.update_status(f"Compared {len(self.results_data)} results")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare results:\n{e}")
            self.main_window.update_status("Comparison failed")

    def load_csv_results(self, file_path):
        """Load and analyze CSV file"""
        from core.analyzer import ResultsAnalyzer

        analyzer = ResultsAnalyzer(file_path)
        analyzer.load_csv()
        return analyzer.analyze()

    def load_json_results(self, file_path):
        """Load JSON results"""
        with open(file_path, 'r') as f:
            return json.load(f)

    def generate_sample_metrics(self, index):
        """Generate sample metrics for demonstration"""
        import random

        # Vary metrics slightly for each sample
        base_win_rate = 70 - (index * 5)
        base_return = 40 + (index * 10)

        return {
            'total_trades': 100,
            'winning_trades': base_win_rate,
            'losing_trades': 100 - base_win_rate,
            'win_rate': base_win_rate,
            'total_pnl': base_return * 1000,
            'total_return_pct': base_return,
            'avg_win': 300 + (index * 50),
            'avg_loss': -150 - (index * 20),
            'avg_mae_pct': -1.2 - (index * 0.3),
            'avg_mfe_pct': 2.0 + (index * 0.5),
            'sharpe_ratio': 1.8 - (index * 0.2),
            'sortino_ratio': 2.3 - (index * 0.2),
            'max_drawdown_pct': -10 - (index * 2),
            'profit_factor': 2.1 - (index * 0.2),
            'expectancy': 150 + (index * 20),
            'max_consecutive_wins': 8 - index,
            'max_consecutive_losses': 3 + index
        }

    def display_comparison(self):
        """Display comparison table"""

        # Clear previous comparison
        for widget in self.comparison_content.winfo_children():
            widget.destroy()

        # Show comparison frame
        self.comparison_frame.pack(fill='both', expand=True, padx=25, pady=10)

        # Header
        header = ttk.Frame(self.comparison_content)
        header.pack(fill='x', pady=10, padx=20)

        ttk.Label(header, text="Comparison Results",
                 style='Title.TLabel').pack(anchor='w')
        ttk.Label(header, text=f"Comparing {len(self.results_data)} backtests",
                 style='Subtitle.TLabel').pack(anchor='w')

        # Comparison table
        table_frame = ttk.LabelFrame(self.comparison_content, text="Metrics Comparison", padding=15)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Create table with scrollbars
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill='both', expand=True)

        # Horizontal scrollbar
        h_scroll = ttk.Scrollbar(table_container, orient='horizontal')
        h_scroll.pack(side='bottom', fill='x')

        # Vertical scrollbar
        v_scroll = ttk.Scrollbar(table_container, orient='vertical')
        v_scroll.pack(side='right', fill='y')

        # Text widget for table
        table_text = tk.Text(table_container, wrap='none',
                            xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set,
                            height=25)
        style_text(table_text, code=True)
        table_text.pack(side='left', fill='both', expand=True)

        h_scroll.config(command=table_text.xview)
        v_scroll.config(command=table_text.yview)

        # Build comparison table
        metrics_to_compare = [
            ('Total Trades', 'total_trades', ''),
            ('Win Rate', 'win_rate', '%'),
            ('Total Return', 'total_return_pct', '%'),
            ('Average Win', 'avg_win', '$'),
            ('Average Loss', 'avg_loss', '$'),
            ('MAE (avg %)', 'avg_mae_pct', '%'),
            ('MFE (avg %)', 'avg_mfe_pct', '%'),
            ('Sharpe Ratio', 'sharpe_ratio', ''),
            ('Sortino Ratio', 'sortino_ratio', ''),
            ('Max Drawdown', 'max_drawdown_pct', '%'),
            ('Profit Factor', 'profit_factor', ''),
            ('Expectancy', 'expectancy', '$'),
            ('Max Win Streak', 'max_consecutive_wins', ''),
            ('Max Loss Streak', 'max_consecutive_losses', '')
        ]

        # Header row
        header_row = f"{'Metric':<20}"
        for result in self.results_data:
            name = result['name'][:15]  # Truncate long names
            header_row += f"{name:>15} "
        header_row += f"{'Winner':>10}"

        table_text.insert('1.0', header_row + '\n')
        table_text.insert('end', '=' * (20 + (15 * len(self.results_data)) + 10) + '\n\n')

        # Data rows
        for metric_name, metric_key, unit in metrics_to_compare:
            row = f"{metric_name:<20}"

            values = []
            for result in self.results_data:
                value = result['metrics'].get(metric_key, 0)
                values.append(value)

                if unit == '%':
                    row += f"{value:>14.1f}% "
                elif unit == '$':
                    row += f"${value:>13,.0f} "
                else:
                    row += f"{value:>14.2f} "

            # Determine winner (best value)
            if metric_name in ['Average Loss', 'MAE (avg %)', 'Max Drawdown', 'Max Loss Streak']:
                # Lower is better
                best_idx = values.index(max(values))  # Max because they're negative
                winner = "*"
            else:
                # Higher is better
                best_idx = values.index(max(values))
                winner = "*"

            row += f"{winner:>10}"

            # Highlight winner
            table_text.insert('end', row + '\n')

        table_text.config(state='disabled')

        # Summary
        summary_frame = ttk.LabelFrame(self.comparison_content, text="Overall Winner", padding=15)
        summary_frame.pack(fill='x', padx=20, pady=10)

        # Calculate which result won most metrics
        wins = [0] * len(self.results_data)
        for metric_name, metric_key, unit in metrics_to_compare:
            values = [r['metrics'].get(metric_key, 0) for r in self.results_data]
            if metric_name in ['Average Loss', 'MAE (avg %)', 'Max Drawdown', 'Max Loss Streak']:
                best_idx = values.index(max(values))
            else:
                best_idx = values.index(max(values))
            wins[best_idx] += 1

        winner_idx = wins.index(max(wins))
        winner_name = self.results_data[winner_idx]['name']
        winner_wins = wins[winner_idx]

        summary_text = f"""
OVERALL BEST PERFORMER: {winner_name}

Won {winner_wins} out of {len(metrics_to_compare)} metrics

Ranking:
"""

        # Sort by wins
        ranking = sorted(enumerate(wins), key=lambda x: x[1], reverse=True)
        for rank, (idx, win_count) in enumerate(ranking, 1):
            name = self.results_data[idx]['name']
            summary_text += f"  {rank}. {name}: {win_count} wins\n"

        ttk.Label(summary_frame, text=summary_text.strip(),
                 font=FONT_MONO, justify='left').pack(anchor='w')

        # Export button
        export_frame = ttk.Frame(self.comparison_content)
        export_frame.pack(fill='x', padx=20, pady=20)

        ttk.Button(export_frame, text="Export Comparison Report",
                  command=self.export_comparison).pack(side='left', padx=5)

    def export_comparison(self):
        """Export comparison to file"""
        if not self.results_data:
            messagebox.showwarning("No Data", "Run a comparison first")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")],
            initialfile="comparison_results.json"
        )

        if file_path:
            try:
                export_data = {
                    'comparison_date': str(Path().resolve()),
                    'results': self.results_data
                }

                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)

                messagebox.showinfo("Exported", f"Comparison saved to:\n{file_path}")
                self.main_window.update_status(f"Comparison exported to {os.path.basename(file_path)}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
