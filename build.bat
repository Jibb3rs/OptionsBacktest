@echo off
setlocal

echo ============================================================
echo  Options Backtesting System - Build Script
echo ============================================================
echo.

:: Verify private key is NOT in the dist (safety check)
if exist "licensing\keys\private.key" (
    echo [OK] Private key found locally - will be excluded from build.
) else (
    echo [WARN] No private key found. Run: py licensing/keygen.py --setup
    echo        This is fine if the public key is already in validator.py.
)

echo.
echo [1/3] Installing PyInstaller...
py -m pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [2/3] Installing cryptography package...
py -m pip install cryptography --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install cryptography.
    pause
    exit /b 1
)

echo [3/3] Building executable...
echo.

:: Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "OptionsBacktest.spec" del /q OptionsBacktest.spec

:: Run PyInstaller
py -m PyInstaller ^
    --name "OptionsBacktest" ^
    --windowed ^
    --onedir ^
    --add-data "config;config" ^
    --add-data "presets;presets" ^
    --add-data "gui\assets;gui\assets" ^
    --hidden-import "licensing.validator" ^
    --hidden-import "cryptography.hazmat.primitives.asymmetric.ed25519" ^
    --hidden-import "cryptography.hazmat.primitives.serialization" ^
    --exclude-module "licensing.keygen" ^
    --exclude-module "tkinter" ^
    --noconfirm ^
    main_pyqt.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed. Check the output above for details.
    pause
    exit /b 1
)

:: Safety: make sure keygen.py and private.key are NOT in the dist
if exist "dist\OptionsBacktest\licensing\keygen.py" (
    del /q "dist\OptionsBacktest\licensing\keygen.py"
    echo [SAFE] Removed keygen.py from dist.
)
if exist "dist\OptionsBacktest\licensing\keys\private.key" (
    del /q "dist\OptionsBacktest\licensing\keys\private.key"
    echo [SAFE] Removed private.key from dist.
)

echo.
echo ============================================================
echo  Build complete!
echo  Output folder: dist\OptionsBacktest\
echo  Executable:    dist\OptionsBacktest\OptionsBacktest.exe
echo.
echo  Next step: Run Inno Setup on installer.iss to create
echo             the OptionsBacktestSetup.exe installer.
echo ============================================================
echo.
pause
endlocal
