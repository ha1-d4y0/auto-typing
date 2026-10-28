@echo off
chcp 65001 >nul
setlocal

echo [INFO] Python環境の確認中
python --version >nul 2>&1

if errorlevel 1 (
    echo [ERROR] Pythonがインストールされていません
    pause
    exit /b 1
)

echo [INFO] pipの更新中
python -m pip install --upgrade pip

echo TesseractOCRをインストールしています。
powershell -Command "winget install UB-Mannheim.TesseractOCR"

echo [INFO]ライブラリのインストール中
python -m pip install -r requirementsWM.txt

if errorlevel 1 (
    echo [ERROR]インストール失敗
    pause
    exit /b 1
)

echo.
echo [INFO]セットアップ完了
echo.
echo =========================================

set /p CHOICE="benesseWin.pyを実行しますか？ (Y/N): "

if /i "%CHOICE%"=="Y" (
    echo 実行します
    py benesseWin.py
) else (
    echo 終了します
)

echo.
pause
endlocal