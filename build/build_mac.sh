#!/bin/bash
# Local macOS build script
# Run from the project root: bash build/build_mac.sh

set -e

echo "=== OptionsBacktest macOS Build ==="

# 1. Install/upgrade build tools
echo "[1/5] Installing build dependencies..."
pip install --upgrade pyinstaller cryptography

# 2. Clean previous build
echo "[2/5] Cleaning previous build..."
rm -rf build/OptionsBacktest build/OptionsBacktest.app \
       build/LicenseGenerator build/LicenseGenerator.app \
       dist/OptionsBacktest dist/OptionsBacktest.app \
       dist/LicenseGenerator dist/LicenseGenerator.app \
       dist/*.dmg

# 3. Build main app
echo "[3/5] Building OptionsBacktest.app..."
pyinstaller OptionsBacktest.spec

# 4. Build keygen app
echo "[4/5] Building LicenseGenerator.app..."
pyinstaller keygen.spec

# 5. Create DMG (main app only — keygen stays private)
echo "[5/5] Creating .dmg installer..."
if ! command -v create-dmg &> /dev/null; then
    echo "Installing create-dmg..."
    brew install create-dmg
fi

create-dmg \
  --volname "OptionsBacktest" \
  --window-pos 200 120 \
  --window-size 560 300 \
  --icon-size 100 \
  --icon "OptionsBacktest.app" 140 150 \
  --hide-extension "OptionsBacktest.app" \
  --app-drop-link 420 150 \
  "dist/OptionsBacktest-macOS.dmg" \
  "dist/OptionsBacktest.app"

echo ""
echo "=== Build complete ==="
echo "Installer (send to users): dist/OptionsBacktest-macOS.dmg"
echo "Keygen app (keep private): dist/LicenseGenerator.app"
