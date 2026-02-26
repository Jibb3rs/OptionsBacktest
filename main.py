#!/usr/bin/env python3
"""
Options Backtesting System - Main Entry Point
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui.main_window import MainWindow
    from gui.theme import apply_theme
except ImportError as e:
    print(f"Error importing GUI: {e}")
    print("Make sure all files are in place.")
    sys.exit(1)

def main():
    """Launch the application"""
    root = tk.Tk()

    try:
        # Apply HUD dark theme globally before building UI
        apply_theme(root)

        app = MainWindow(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application:\n{e}")
        raise

if __name__ == "__main__":
    main()
