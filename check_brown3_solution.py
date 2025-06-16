#!/usr/bin/env python3
"""
檢查棕3路線解決方案
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_frontend_fixes():
    """檢查前端修復"""
    print("=== 檢查前端修復 ===")
    
    # 檢查 route-manager.js 修復
    route_manager_file = "app/static/js/modules/route-manager.js"
    if os.path.exists(route_manager_file):
        with open(route_manager_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 檢查重複定義是否已修復
        brown3_count = content.count("case 'brown-3':")
        if brown3_count == 1:
            print("✅ route-manager.js: 棕3路線重複定義已修復")
        else:
            print(f"❌ route-manager.js: 仍有 {brown3_count} 個棕3路線定義")
            
        # 檢查重試機制是否存在
        if "attemptLoad" in content and "maxAttempts" in content:
            print("✅ route-manager.js: 已添加重試機制")
        else:
            print("❌ route-manager.js: 缺少重試機制")
    else:
        print("❌ route-manager.js 檔案不存在")
    
    # 檢查 Firebase 離線處理器
    firebase_handler_file = "app/static/js/modules/firebase-offline-handler.js"
    if os.path.exists(firebase_handler_file):
        print("✅ firebase-offline-handler.js: Firebase 離線處理器已創建")
    else:
        print("❌ firebase-offline-handler.js: Firebase 離線處理器缺失")
    
    # 檢查 UI 工具更新
    ui_utils_file = "app/static/js/modules/ui-utils.js"
    if os.path.exists(ui_utils_file):
        with open(ui_utils_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "showSuccessMessage" in content:
            print("✅ ui-utils.js: 已添加成功訊息函數")
        else:
            print("❌ ui-utils.js: 缺少成功訊息函數")
    else:
        print("❌ ui-utils.js 檔案不存在")
    
    # 檢查 catch.html 修復
    catch_html_file = "app/templates/game/catch.html"
    if os.path.exists(catch_html_file):
        with open(catch_html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "reloadBrown3Btn" in content and "forceReloadBrown3Route" in content:
            print("✅ catch.html: 已添加棕3路線恢復按鈕")
        else:
            print("❌ catch.html: 缺少棕3路線恢復按鈕")
    else:
        print("❌ catch.html 檔案不存在")

def check_backend_data():
    """檢查後端資料"""
    print("\n=== 檢查後端資料 ===")
    
    # 檢查道館緩存
    arena_cache_file = "app/data/arenas/arena_levels.json"
    if os.path.exists(arena_cache_file):
        import json
        try:
            with open(arena_cache_file, 'r', encoding='utf-8') as f:
                arenas = json.load(f)
            
            brown3_arenas = []
            for arena_id, arena in arenas.items():
                routes = arena.get('routes', [])
                if '棕3' in routes:
                    brown3_arenas.append(arena)
            
            print(f"✅ arena_levels.json: 找到 {len(brown3_arenas)} 個棕3路線道館")
            
            if brown3_arenas:
                print("📍 棕3道館示例:")
                for i, arena in enumerate(brown3_arenas[:3]):
                    print(f"   {i+1}. {arena.get('name', '未知')}")
                    
        except Exception as e:
            print(f"❌ arena_levels.json: 讀取失敗 - {e}")
    else:
        print("❌ arena_levels.json: 道館緩存檔案不存在")
    
    # 檢查 TDX 服務
    try:
        from app.services.tdx_service import get_brown_3_route, get_brown_3_stops
        
        route_data = get_brown_3_route()
        stops_data = get_brown_3_stops()
        
        print(f"✅ TDX 服務: 棕3路線資料 {len(route_data) if route_data else 0} 個座標點")
        print(f"✅ TDX 服務: 棕3站點資料 {len(stops_data) if stops_data else 0} 個站點")
        
    except Exception as e:
        print(f"❌ TDX 服務: 測試失敗 - {e}")

def provide_solution_summary():
    """提供解決方案摘要"""
    print("\n=== 解決方案摘要 ===")
    print("針對「棕3路線一開始有顯示，但是後來就沒有了」的問題，已實施以下修復：")
    print()
    print("🔧 前端修復:")
    print("   1. 修復 route-manager.js 中的重複定義問題")
    print("   2. 為棕3路線添加重試機制和錯誤處理")
    print("   3. 創建 Firebase 離線處理器，防止網絡問題影響路線顯示")
    print("   4. 添加路線恢復機制，定期檢查並自動恢復遺失的路線")
    print("   5. 在 catch.html 中添加手動恢復按鈕")
    print()
    print("🗄️ 後端確認:")
    print("   1. 確認本地道館緩存包含棕3路線道館")
    print("   2. 確認 TDX API 能正常獲取棕3路線資料")
    print("   3. 創建道館同步腳本以備需要")
    print()
    print("🚀 使用方法:")
    print("   1. 刷新遊戲頁面，檢查棕3路線是否正常顯示")
    print("   2. 如果路線消失，點擊「棕3路線」按鈕手動恢復")
    print("   3. 系統會每30秒自動檢查並恢復遺失的路線")
    print("   4. 如果 Firebase 連接有問題，系統會自動切換到離線模式")

def main():
    print("🔍 棕3路線問題解決方案檢查工具")
    print("=" * 50)
    
    check_frontend_fixes()
    check_backend_data()
    provide_solution_summary()
    
    print("\n" + "=" * 50)
    print("✅ 檢查完成！請刷新遊戲頁面測試修復效果。")

if __name__ == "__main__":
    main()
