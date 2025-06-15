"""
API 文檔測試腳本

運行此腳本來啟動應用程式並測試 API 文檔功能
"""

import os
import sys

# 添加專案根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_api_docs():
    """測試 API 文檔功能"""
    try:
        # 導入並創建應用
        from app import create_app
        
        # 創建應用實例（不載入TDX資料以加快啟動）
        app = create_app('default', load_tdx=False)
        
        print("=== Spirit Bus API 文檔伺服器 ===")
        print("應用程式已成功建立！")
        print()
        print("API 文檔可在以下網址查看：")
        print("📚 主要文檔：http://localhost:5000/api-docs")
        print("🧪 測試介面：http://localhost:5000/api-docs/test")
        print()
        print("其他可用的端點：")
        print("🏠 首頁：http://localhost:5000/")
        print("🔑 登入：http://localhost:5000/auth/login")
        print("👤 註冊：http://localhost:5000/auth/register")
        print()
        print("按 Ctrl+C 停止伺服器")
        print("=" * 50)
        
        # 啟動開發伺服器
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ 導入錯誤：{e}")
        print("請確保已安裝所有必要的依賴包")
        return False
    except Exception as e:
        print(f"❌ 啟動失敗：{e}")
        return False

if __name__ == "__main__":
    test_api_docs()
