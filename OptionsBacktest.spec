# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for OptionsBacktest
# Build: pyinstaller OptionsBacktest.spec

import sys
from pathlib import Path

block_cipher = None

# Data files to bundle (source, dest-inside-bundle)
added_datas = [
    # Config files (read-only, bundled inside app)
    ('config/strategies.json',          'config'),
    ('config/indicators.json',          'config'),

    # ECharts JS library
    ('gui/assets/echarts.min.js',       'gui/assets'),

    # Strategy source files — read as TEXT at runtime for code generation
    ('strategies/advanced_filters.py',  'strategies'),
]

a = Analysis(
    ['main_pyqt.py'],
    pathex=['.'],
    binaries=[],
    datas=added_datas,
    hiddenimports=[
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebEngine',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtNetwork',
        'PyQt5.sip',
        'core.paths',
        'core.analyzer',
        'core.indicators',
        'core.strike_selector',
        'strategies.base_strategy',
        'strategies.advanced_filters',
        'licensing.validator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OptionsBacktest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='build/icon.icns' if sys.platform == 'darwin' else 'build/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OptionsBacktest',
)

# macOS: wrap COLLECT output into a .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='OptionsBacktest.app',
        icon='build/icon.icns',
        bundle_identifier='com.optionsbacktest.app',
        info_plist={
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'CFBundleShortVersionString': '4.0.0',
            'CFBundleVersion': '4.0.0',
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDisplayName': 'OptionsBacktest',
        },
    )
