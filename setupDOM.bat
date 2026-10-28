@echo off
chcp 65001 >nul
setlocal

echo [INFO]Python環境の確認中
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR]Pythonがインストールされていません
    pause
    exit /b 1
)

echo [INFO]pipの更新中
python -m pip install --upgrade pip

echo [INFO]ライブラリのインストール中
python -m pip install -r requirementsDOM.txt

if errorlevel 1 (
    echo [ERROR]インストールに失敗しました
    pause
    exit /b 1
)

echo.
echo [INFO]セットアップ完了
echo.
echo =========================================
set /p CHOICE="benesseDOM.pyを実行しますか？ (Y/N): "

if /i "%CHOICE%"=="Y" (
    echo 実行します
    py benesseDOM.py
) else (
    echo 終了します
)

echo.
pause
endlocal