import os
import sys
import subprocess
import time

# 獲取當前腳本的路徑
script_dir = os.path.dirname(os.path.abspath(__file__))

# 設定專案根目錄
project_root = script_dir  # 腳本直接放在專案根目錄下

# 檢查是否在虛擬環境中運行
in_venv = sys.prefix != sys.base_prefix
if not in_venv:
    print("警告: 未檢測到虛擬環境。強烈建議在虛擬環境中運行此應用。")
    response = input("是否繼續? (y/n): ")
    if response.lower() != 'y':
        sys.exit(0)

# 設定 Python 解釋器路徑
python_exe = sys.executable

def start_app():
    """啟動 Flask 應用"""
    app_path = os.path.join(project_root, "app.py")
    print(f"啟動 Flask 應用 ({app_path})...")
    return subprocess.Popen([python_exe, app_path])

def start_creature_generator():
    """啟動精靈生成器服務"""
    generator_path = os.path.join(project_root, "scripts", "creature_generator.py")
    print(f"啟動精靈生成器 ({generator_path})...")
    return subprocess.Popen([python_exe, generator_path])

def main():
    print("======================================")
    print("=== 貓空公車精靈捕捉遊戲啟動器 ===")
    print("======================================")
    print(f"使用 Python: {python_exe}")
    print(f"專案目錄: {project_root}")
    print("--------------------------------------")
    
    try:
        # 啟動 Flask 應用
        flask_process = start_app()
        print("Flask 應用啟動中，請稍待...")
        time.sleep(2)  # 給 Flask 一些時間來初始化
        
        # 啟動精靈生成器
        generator_process = start_creature_generator()
        print("精靈生成器啟動中，請稍待...")
        time.sleep(1)
        
        print("\n兩個服務已成功啟動！")
        print("- Flask 應用通常在 http://localhost:5000 運行")
        print("- 精靈生成器在背景運行中")
        print("\n按 Ctrl+C 可以結束兩個服務")
        
        # 等待直到用戶按下 Ctrl+C
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n接收到中斷信號，正在關閉服務...")
    finally:
        # 結束進程
        try:
            if 'flask_process' in locals():
                flask_process.terminate()
                print("已停止 Flask 應用")
            
            if 'generator_process' in locals():
                generator_process.terminate()
                print("已停止精靈生成器")
                
            print("所有服務已關閉")
        except Exception as e:
            print(f"關閉服務時發生錯誤: {e}")

if __name__ == "__main__":
    main()