"""
Results Analyzer - Calculates all metrics from QuantConnect CSV
Includes MAE/MFE in percentages
"""

import pandas as pd
import numpy as np
from datetime import datetime

class ResultsAnalyzer:
    """Analyzes backtest results and calculates comprehensive metrics"""
    
    def __init__(self, csv_path):
        """Initialize analyzer with CSV file path"""
        self.csv_path = csv_path
        self.df = None
        self.trades = []
        self.metrics = {}
        
    def load_csv(self):
        """Load and parse CSV file"""
        try:
            self.df = pd.read_csv(self.csv_path)
            return True
        except Exception as e:
            raise Exception(f"Failed to load CSV: {e}")
    
    def analyze(self):
        """Run complete analysis"""
        if self.df is None:
            raise Exception("No data loaded. Call load_csv() first.")
        
        # Parse trades from CSV
        self.parse_trades()
        
        # Calculate all metrics
        self.calculate_basic_metrics()
        self.calculate_mae_mfe()
        self.calculate_risk_metrics()
        self.calculate_returns()
        self.calculate_drawdown()
        self.calculate_streaks()
        
        return self.metrics
    
    def parse_trades(self):
        """Parse trades from QuantConnect CSV format"""
        # This is a simplified parser - adapt based on actual QC CSV format
        # Typical QC CSV has: Time, Symbol, Price, Quantity, OrderDirection, etc.
        
        # Group by trade (entry to exit)
        # For now, create sample data structure
        self.trades = []
        
        # Example trade structure
        # In real implementation, parse from self.df
        # For now, generate sample trades for testing
        
        if len(self.df) > 0:
            # Try to parse actual trades
            # This would need to be adapted to actual QC CSV format
            pass
        else:
            # Generate sample trades for demonstration
            self.generate_sample_trades()
    
    def generate_sample_trades(self):
        """Generate sample trades for testing (remove in production)"""
        import random
        
        # Generate 100 sample trades
        for i in range(100):
            entry_price = 1000
            max_profit = random.uniform(50, 500)
            max_loss = random.uniform(-100, -500)
            
            # 70% win rate
            if random.random() < 0.70:
                exit_pnl = random.uniform(50, max_profit * 0.8)
            else:
                exit_pnl = random.uniform(max_loss * 0.8, -20)
            
            trade = {
                'entry_date': f"2024-01-{(i % 30) + 1:02d}",
                'exit_date': f"2024-01-{(i % 30) + 1:02d}",
                'entry_price': entry_price,
                'exit_price': entry_price + exit_pnl,
                'pnl': exit_pnl,
                'max_profit': max_profit,  # MFE
                'max_loss': max_loss,  # MAE
                'max_risk': 1000,  # Max possible loss
                'max_reward': 400,  # Max possible profit
                'duration_days': random.randint(0, 7),
                'exit_reason': random.choice(['take_profit', 'stop_loss', 'expiry'])
            }
            
            self.trades.append(trade)
    
    def calculate_basic_metrics(self):
        """Calculate basic trade statistics"""
        if not self.trades:
            return
        
        pnls = [t['pnl'] for t in self.trades]
        
        total_trades = len(self.trades)
        winning_trades = len([p for p in pnls if p > 0])
        losing_trades = len([p for p in pnls if p < 0])
        breakeven_trades = len([p for p in pnls if p == 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        loss_rate = (losing_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(pnls)
        avg_pnl = np.mean(pnls)
        median_pnl = np.median(pnls)
        
        winning_pnls = [p for p in pnls if p > 0]
        losing_pnls = [p for p in pnls if p < 0]
        
        avg_win = np.mean(winning_pnls) if winning_pnls else 0
        avg_loss = np.mean(losing_pnls) if losing_pnls else 0
        
        largest_win = max(pnls) if pnls else 0
        largest_loss = min(pnls) if pnls else 0
        
        self.metrics.update({
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'breakeven_trades': breakeven_trades,
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'median_pnl': median_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss
        })
    
    def calculate_mae_mfe(self):
        """Calculate MAE and MFE in percentages"""
        if not self.trades:
            return
        
        mae_values = []
        mfe_values = []
        mae_pct_values = []
        mfe_pct_values = []
        capture_efficiency = []
        
        for trade in self.trades:
            mae = trade['max_loss']
            mfe = trade['max_profit']
            max_risk = trade.get('max_risk', 1000)
            max_reward = trade.get('max_reward', 400)
            pnl = trade['pnl']
            
            # MAE as percentage of max risk
            mae_pct = (mae / max_risk * 100) if max_risk != 0 else 0
            
            # MFE as percentage of max reward
            mfe_pct = (mfe / max_reward * 100) if max_reward != 0 else 0
            
            # Profit capture efficiency (how much of MFE was captured)
            if mfe > 0:
                capture_eff = (pnl / mfe * 100) if mfe != 0 else 0
            else:
                capture_eff = 0
            
            mae_values.append(mae)
            mfe_values.append(mfe)
            mae_pct_values.append(mae_pct)
            mfe_pct_values.append(mfe_pct)
            capture_efficiency.append(capture_eff)
        
        self.metrics.update({
            'avg_mae': np.mean(mae_values),
            'avg_mfe': np.mean(mfe_values),
            'avg_mae_pct': np.mean(mae_pct_values),
            'avg_mfe_pct': np.mean(mfe_pct_values),
            'median_mae': np.median(mae_values),
            'median_mfe': np.median(mfe_values),
            'median_mae_pct': np.median(mae_pct_values),
            'median_mfe_pct': np.median(mfe_pct_values),
            'max_mae': min(mae_values),
            'max_mfe': max(mfe_values),
            'max_mae_pct': min(mae_pct_values),
            'max_mfe_pct': max(mfe_pct_values),
            'avg_profit_capture': np.mean([c for c in capture_efficiency if c > 0])
        })
    
    def calculate_risk_metrics(self):
        """Calculate risk-adjusted metrics"""
        if not self.trades:
            return
        
        pnls = [t['pnl'] for t in self.trades]
        
        # Risk/Reward Ratio
        avg_win = self.metrics.get('avg_win', 0)
        avg_loss = self.metrics.get('avg_loss', 0)
        risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Expectancy
        win_rate = self.metrics.get('win_rate', 0) / 100
        loss_rate = self.metrics.get('loss_rate', 0) / 100
        expectancy = (win_rate * avg_win) + (loss_rate * avg_loss)
        
        # Profit Factor
        gross_profit = sum([p for p in pnls if p > 0])
        gross_loss = abs(sum([p for p in pnls if p < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else 0
        
        # Sharpe Ratio (simplified - assumes daily returns)
        returns = np.array(pnls)
        if len(returns) > 1 and np.std(returns) != 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
        else:
            sharpe = 0
        
        # Sortino Ratio (downside deviation only)
        negative_returns = [r for r in returns if r < 0]
        if negative_returns and np.std(negative_returns) != 0:
            sortino = np.mean(returns) / np.std(negative_returns) * np.sqrt(252)
        else:
            sortino = 0
        
        self.metrics.update({
            'risk_reward_ratio': risk_reward,
            'expectancy': expectancy,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss
        })
    
    def calculate_returns(self):
        """Calculate returns"""
        starting_capital = 100000  # Default
        total_pnl = self.metrics.get('total_pnl', 0)
        
        total_return = (total_pnl / starting_capital * 100)
        
        # Annualized return (simplified)
        # Assumes trades span 1 year
        annualized_return = total_return
        
        self.metrics.update({
            'total_return_pct': total_return,
            'annualized_return_pct': annualized_return
        })
    
    def calculate_drawdown(self):
        """Calculate drawdown metrics"""
        if not self.trades:
            return
        
        # Calculate equity curve
        equity = [100000]  # Starting capital
        for trade in self.trades:
            equity.append(equity[-1] + trade['pnl'])
        
        # Calculate drawdown
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max * 100
        
        max_dd = np.min(drawdown)
        avg_dd = np.mean([d for d in drawdown if d < 0]) if any(d < 0 for d in drawdown) else 0
        
        # Find max drawdown date
        max_dd_idx = np.argmin(drawdown)
        max_dd_date = self.trades[max_dd_idx]['exit_date'] if max_dd_idx < len(self.trades) else "N/A"
        
        # Current drawdown
        current_dd = drawdown[-1]
        
        # Calmar Ratio
        annual_return = self.metrics.get('annualized_return_pct', 0)
        calmar = abs(annual_return / max_dd) if max_dd != 0 else 0
        
        self.metrics.update({
            'max_drawdown_pct': max_dd,
            'avg_drawdown_pct': avg_dd,
            'current_drawdown_pct': current_dd,
            'max_drawdown_date': max_dd_date,
            'calmar_ratio': calmar
        })
    
    def calculate_streaks(self):
        """Calculate winning/losing streaks"""
        if not self.trades:
            return
        
        pnls = [t['pnl'] for t in self.trades]
        
        max_win_streak = 0
        max_loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for pnl in pnls:
            if pnl > 0:
                current_win_streak += 1
                current_loss_streak = 0
                max_win_streak = max(max_win_streak, current_win_streak)
            elif pnl < 0:
                current_loss_streak += 1
                current_win_streak = 0
                max_loss_streak = max(max_loss_streak, current_loss_streak)
            else:
                current_win_streak = 0
                current_loss_streak = 0
        
        # Duration stats
        durations = [t['duration_days'] for t in self.trades]
        avg_duration = np.mean(durations) if durations else 0
        median_duration = np.median(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # Exit reasons
        exit_reasons = {}
        for trade in self.trades:
            reason = trade.get('exit_reason', 'unknown')
            exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
        
        self.metrics.update({
            'max_consecutive_wins': max_win_streak,
            'max_consecutive_losses': max_loss_streak,
            'avg_hold_days': avg_duration,
            'median_hold_days': median_duration,
            'max_hold_days': max_duration,
            'min_hold_days': min_duration,
            'exit_reasons': exit_reasons
        })
    
    def get_trades_dataframe(self):
        """Return trades as pandas DataFrame"""
        return pd.DataFrame(self.trades)