# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for OptionsBacktest License Generator
# Build: pyinstaller keygen.spec

import sys

block_cipher = None

a = Analysis(
    ['licensing/keygen_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cryptography',
        'cryptography.hazmat.primitives.asymmetric.ed25519',
        'cryptography.hazmat.primitives.serialization',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'pandas', 'numpy'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LicenseGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    argv_emulation=False,
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
    name='LicenseGenerator',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='LicenseGenerator.app',
        icon='build/icon.icns',
        bundle_identifier='com.optionsbacktest.licensegenerator',
        info_plist={
            'NSHighResolutionCapable': True,
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleDisplayName': 'License Generator',
        },
    )
