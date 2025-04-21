@echo off
echo ======================================
echo === 貓空公車精靈捕捉遊戲啟動器 ===
echo ======================================

REM 啟動虛擬環境
call venv\Scripts\activate

REM 檢查虛擬環境是否成功啟動
if errorlevel 1 (
    echo 警告: 虛擬環境啟動失敗，請確認 venv 資料夾存在
    pause
    exit /b
)

echo 虛擬環境已啟動

REM 在背景啟動精靈生成器
start "精靈生成器" cmd /c "python scripts/creature_generator.py"
echo 精靈生成器已在新視窗中啟動...

REM 稍待一下讓精靈生成器初始化
timeout /t 2 > nul

REM 在主視窗啟動 Flask 應用
echo 正在啟動 Flask 應用...
python app.py

REM 當 Flask 應用關閉後才會執行以下程式碼
echo 應用已關閉，按任意鍵結束
pause