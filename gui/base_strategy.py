"""
Base Strategy - Common logic shared by all strategies
"""

from datetime import timedelta

class BaseStrategy:
    """Base class for all options strategies"""
    
    @staticmethod
    def generate_imports():
        """Common imports for all strategies"""
        return """from AlgorithmImports import *
import numpy as np
from datetime import datetime, timedelta"""
    
    @staticmethod
    def generate_config_loader():
        """Embedded configuration loader"""
        return """
class Config:
    \"\"\"Embedded configuration\"\"\"
    def __init__(self, config_dict):
        for key, value in config_dict.items():
            setattr(self, key, value)

def load_config():
    \"\"\"Load embedded configuration\"\"\"
    config_dict = {CONFIG_PLACEHOLDER}
    return Config(config_dict)
"""
    
    @staticmethod
    def generate_indicator_manager(indicators_config):
        """Generate indicator manager code - COMPLETE VERSION"""
        
        # Check if any indicators are enabled
        has_indicators = False
        if indicators_config:
            for indicator_key, indicator_data in indicators_config.items():
                if isinstance(indicator_data, dict) and indicator_data.get('enabled'):
                    has_indicators = True
                    break
        
        if not has_indicators:
            return """
class IndicatorManager:
    \"\"\"No indicators enabled\"\"\"
    def __init__(self, algorithm, config):
        self.algorithm = algorithm
        self.config = config
    
    def should_enter_trade(self, symbol):
        return True  # No filters
"""
        
        # Read the indicators.py file and embed it
        try:
            from pathlib import Path
            indicators_file = Path(__file__).parent / 'indicators.py'
            
            with open(indicators_file, 'r') as f:
                indicators_code = f.read()
            
            # Remove module docstring
            lines = indicators_code.split('\n')
            code_lines = []
            in_docstring = False
            skip_until_class = True
            
            for line in lines:
                # Skip initial docstring
                if line.strip().startswith('"""') and skip_until_class:
                    if in_docstring:
                        in_docstring = False
                        continue
                    else:
                        in_docstring = True
                        continue
                
                if in_docstring:
                    continue
                
                # Start including from first class
                if line.startswith('class '):
                    skip_until_class = False
                
                if not skip_until_class:
                    code_lines.append(line)
            
            return '\n'.join(code_lines)
            
        except Exception as e:
            print(f"Warning: Could not load indicators.py: {e}")
            return """
class IndicatorManager:
    \"\"\"Indicator management - fallback\"\"\"
    def __init__(self, algorithm, config):
        self.algorithm = algorithm
        self.config = config
    
    def should_enter_trade(self, symbol):
        return True  # Indicators file not found
"""
    
    @staticmethod
    def generate_advanced_filters(advanced_config):
        """
        Generate advanced filter code based on configuration
        NEW METHOD - Embeds filter classes into generated algorithm
        """
        
        if not advanced_config:
            return ""
        
        # Check if any filters are enabled
        filters_enabled = (
            advanced_config.get('iv_rank_enabled', False) or
            advanced_config.get('market_profile_enabled', False) or
            advanced_config.get('vol_regime_enabled', False) or
            advanced_config.get('liquidity_enabled', False)
        )
        
        if not filters_enabled:
            return ""
        
        filters_code = """
# ====================================
# ADVANCED FILTERS
# ====================================

"""
        
        # Read advanced_filters.py content
        try:
            from pathlib import Path
            filters_file = Path(__file__).parent / 'advanced_filters.py'
            
            with open(filters_file, 'r') as f:
                all_filters_code = f.read()
            
            # Remove module docstring and imports
            lines = all_filters_code.split('\n')
            code_lines = []
            in_docstring = False
            skip_until_class = True
            
            for line in lines:
                # Skip initial docstring
                if line.strip().startswith('"""') and skip_until_class:
                    if in_docstring:
                        in_docstring = False
                        continue
                    else:
                        in_docstring = True
                        continue
                
                if in_docstring:
                    continue
                
                # Start including from first class
                if line.startswith('class '):
                    skip_until_class = False
                
                if not skip_until_class:
                    code_lines.append(line)
            
            filters_code += '\n'.join(code_lines)
            
        except Exception as e:
            # Fallback: return empty if file not found
            print(f"Warning: Could not load advanced_filters.py: {e}")
            return ""
        
        return filters_code
    
    @staticmethod
    def generate_initialize_base(config):
        """Common initialization code"""
        
        from datetime import datetime
        
        # Handle both flat and nested config safely
        ticker = config.get('ticker', 'SPY')
        start_date = config.get('start_date')
        end_date = config.get('end_date')
        initial_capital = config.get('initial_capital', 100000)
        resolution = config.get('resolution', 'Daily')
        expiry_days = config.get('expiry_days', 30)
        expiry_range = config.get('expiry_range', 5)
        
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        return f"""def Initialize(self):
        # Basic setup
        self.SetStartDate({start_date.year}, {start_date.month}, {start_date.day})
        self.SetEndDate({end_date.year}, {end_date.month}, {end_date.day})
        self.SetCash({initial_capital})
        
        # Load config
        config = load_config()
        self.config = config
        
        # Add underlying
        self.equity = self.AddEquity(config.ticker, Resolution.{resolution.upper()})
        self.equity.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
        # Add options
        option = self.AddOption(config.ticker, Resolution.{resolution.upper()})
        self.option_symbol = option.Symbol
        
        # Set option filter
        min_expiry = max(0, config.expiry_days - config.expiry_range)
        max_expiry = config.expiry_days + config.expiry_range
        option.SetFilter(lambda x: x.Strikes(-50, 50).Expiration(min_expiry, max_expiry))
        
        # Initialize tracking
        self.positions = {{}}
        self.position_counter = 0
        self.last_trade_date = None
        
        # Initialize indicators (pass full config)
        self.indicators = IndicatorManager(self, config)
        
        self.Log(f"[+] Config loaded")
        self.Log(f"Stop Loss Mode: {{config.stop_loss_mode}} ({{config.stop_loss_pct}}%)")"""

    @staticmethod
    def generate_position_tracking():
        """Common position tracking methods"""
        return """
    def update_positions(self, data):
        \"\"\"Update all open positions with current P&L and MAE/MFE\"\"\"
        
        for pos_id, pos in list(self.positions.items()):
            if pos['status'] != 'open':
                continue
            
            # Calculate current P&L
            current_pnl = self.calculate_pnl(pos, data)
            pos['current_pnl'] = current_pnl
            
            # Update MAE (Maximum Adverse Excursion)
            if current_pnl < pos['metrics']['mae']:
                pos['metrics']['mae'] = current_pnl
            
            # Update MFE (Maximum Favorable Excursion)
            if current_pnl > pos['metrics']['mfe']:
                pos['metrics']['mfe'] = current_pnl
            
            # Check for exit conditions
            exit_reason = self.check_exit_conditions(pos, data.Time)
            if exit_reason:
                self.close_position(pos_id, exit_reason, data.Time)
"""

    @staticmethod
    def generate_exit_logic(config):
        """Common exit condition checking"""
        
        # Safely get stop loss mode
        stop_loss_mode = config.get('stop_loss_mode', 'credit')
        
        # Build stop loss code with proper indentation
        if stop_loss_mode == 'credit' or stop_loss_mode not in ['max_loss', 'equal_dollar', 'price_distance']:
            stop_loss_block = """        # Credit-based stop loss
        stop_loss_amount = -(max_profit * (self.config.stop_loss_pct / 100))
        if current_pnl <= stop_loss_amount:
            return 'stop_loss'"""
        elif stop_loss_mode == 'max_loss':
            stop_loss_block = """        # Max loss-based stop loss
        stop_loss_amount = -(max_loss * (self.config.stop_loss_pct / 100))
        if current_pnl <= stop_loss_amount:
            return 'stop_loss'"""
        elif stop_loss_mode == 'equal_dollar':
            stop_loss_block = """        # Equal dollar stop loss
        profit_target_amount = max_profit * (self.config.profit_target_pct / 100)
        if current_pnl <= -profit_target_amount:
            return 'stop_loss'"""
        else:  # price_distance
            stop_loss_block = """        # Price distance stop loss
        entry_price = pos['entry_underlying_price']
        current_price = self.Securities[self.config.ticker].Price
        price_change_pct = abs((current_price - entry_price) / entry_price) * 100
        if price_change_pct >= self.config.stop_loss_pct:
            return 'stop_loss'"""
        
        return f"""
    def check_exit_conditions(self, pos, time):
        \"\"\"Check if position should be closed\"\"\"
        
        current_pnl = pos['current_pnl']
        max_profit = pos['metrics']['max_profit']
        max_loss = pos['metrics']['max_loss']
        
        # Check profit target
        profit_target = max_profit * (self.config.profit_target_pct / 100)
        if current_pnl >= profit_target:
            return 'profit_target'
        
        # Check stop loss
{stop_loss_block}
        
        # Check expiration (1 day before)
        expiry_date = pos['expiry_date']
        if time.date() >= (expiry_date - timedelta(days=1)):
            return 'expiration'
        
        return None
"""
