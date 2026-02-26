"""
core/paths.py — Central path resolution for both dev and PyInstaller bundles.

Usage:
    from core.paths import resource_path, user_data_dir, output_dir, presets_dir, settings_file

Two categories of paths:

  resource_path(relative)  →  READ-ONLY assets bundled inside the app
                               (config JSON, echarts JS, strategy source files)

  user_data_dir() etc.     →  WRITABLE user data outside the app bundle
                               ~/Documents/OptionsBacktest/
"""

import sys
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Root resolution
# ---------------------------------------------------------------------------

def _bundle_root() -> Path:
    """Return the root directory of bundled resources (sys._MEIPASS when frozen)."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    # Development: two levels up from this file (core/ -> project root)
    return Path(__file__).parent.parent


def resource_path(relative: str) -> Path:
    """
    Resolve a path to a read-only resource that is bundled with the app.

    Works in both development and PyInstaller one-dir / one-file modes.

    Args:
        relative: Path relative to the project root, e.g. 'config/strategies.json'
                  or 'gui/assets/echarts.min.js'

    Returns:
        Absolute Path to the resource.
    """
    return _bundle_root() / relative


# ---------------------------------------------------------------------------
# User-writable data directory
# ---------------------------------------------------------------------------

def user_data_dir() -> Path:
    """
    Return (and create) the user-writable app data directory.

    macOS / Linux : ~/Documents/OptionsBacktest/
    Windows       : ~/Documents/OptionsBacktest/
    """
    d = Path.home() / "Documents" / "OptionsBacktest"
    d.mkdir(parents=True, exist_ok=True)
    return d


def output_dir() -> Path:
    """Directory where generated QuantConnect .py files are saved."""
    d = user_data_dir() / "output"
    d.mkdir(exist_ok=True)
    return d


def presets_dir() -> Path:
    """Directory where strategy preset JSON files are stored."""
    d = user_data_dir() / "presets"
    d.mkdir(exist_ok=True)
    return d


def settings_file() -> Path:
    """Path to the user settings JSON file."""
    return user_data_dir() / "settings.json"
