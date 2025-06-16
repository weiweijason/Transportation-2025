#!/usr/bin/env python3
"""
快速檢查道館等級問題
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_arena_api():
    """測試道館 API"""
    import requests
    
    print("🧪 測試道館 API...")
    
    try:
        # 測試獲取緩存等級
        response = requests.get('http://127.0.0.1:3001/game/api/arena/cached-levels')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('arenas'):
                arenas = data['arenas']
                print(f"✅ API 正常，找到 {len(arenas)} 個道館")
                
                # 檢查幾個道館的等級
                for i, (arena_id, arena) in enumerate(list(arenas.items())[:5]):
                    routes = arena.get('routes', [])
                    level = arena.get('level', 1)
                    expected_level = len(routes) if routes else 1
                    
                    status = "✅" if level == expected_level else "❌"
                    print(f"  {status} {arena.get('name', '未知')}: 等級 {level}, 路線數 {len(routes)} (應為 {expected_level})")
                    
                    if len(routes) > 0:
                        print(f"      路線: {', '.join(routes)}")
                
                return True
            else:
                print("❌ API 返回格式錯誤")
                return False
        else:
            print(f"❌ API 請求失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def main():
    print("🔍 快速道館等級檢查")
    print("=" * 30)
    
    success = test_arena_api()
    
    if success:
        print("\n💡 建議:")
        print("1. 如果看到等級不正確的道館，需要更新 Firebase 資料")
        print("2. 可以重新載入遊戲頁面查看前端顯示是否正確")
        print("3. 點擊道館進入戰鬥頁面時，應該顯示正確的等級")
    else:
        print("\n❌ 請確保遊戲伺服器正在運行")

if __name__ == "__main__":
    main()
