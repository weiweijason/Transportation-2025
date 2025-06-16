#!/usr/bin/env python3
"""
道館等級檢查和修復工具
通過 API 檢查道館等級是否正確
"""

import requests
import json

# 配置
API_BASE_URL = "http://127.0.0.1:3001"

def test_api_connection():
    """測試 API 連接"""
    try:
        print("🧪 測試道館 API...")
        response = requests.get(f'{API_BASE_URL}/game/api/arena/cached-levels', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API 連接成功")
            print(f"   找到 {len(data.get('arenas', {}))} 個道館")
            return True
        else:
            print(f"❌ API 返回錯誤狀態: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API 連接失敗: {e}")
        return False

def check_arena_levels():
    """檢查道館等級是否正確"""
    try:
        print("\n🔍 檢查道館等級...")
        
        # 獲取所有道館
        response = requests.get(f'{API_BASE_URL}/game/api/arena/cached-levels')
        if response.status_code != 200:
            print(f"❌ 無法獲取道館資料: {response.status_code}")
            return
        
        data = response.json()
        arenas = data.get('arenas', {})
        
        print(f"\n📊 道館等級統計:")
        level_stats = {}
        incorrect_arenas = []
        
        for arena_id, arena in arenas.items():
            routes = arena.get('routes', [])
            stored_level = arena.get('level', 1)
            correct_level = len(routes) if routes else 1
            
            # 統計等級分布
            if correct_level not in level_stats:
                level_stats[correct_level] = 0
            level_stats[correct_level] += 1
            
            # 檢查等級是否正確
            if stored_level != correct_level:
                incorrect_arenas.append({
                    'id': arena_id,
                    'name': arena.get('name', '未知'),
                    'stored_level': stored_level,
                    'correct_level': correct_level,
                    'routes': routes
                })
        
        # 顯示統計
        for level in sorted(level_stats.keys()):
            count = level_stats[level]
            print(f"   等級 {level}: {count} 個道館")
        
        # 顯示需要修復的道館
        if incorrect_arenas:
            print(f"\n⚠️  發現 {len(incorrect_arenas)} 個等級不正確的道館:")
            for arena in incorrect_arenas[:10]:  # 只顯示前10個
                print(f"   {arena['name']}: 儲存等級 {arena['stored_level']} → 應為 {arena['correct_level']} (路線: {len(arena['routes'])})")
                if len(arena['routes']) > 0:
                    print(f"     路線: {', '.join(arena['routes'])}")
            
            if len(incorrect_arenas) > 10:
                print(f"   ... 還有 {len(incorrect_arenas) - 10} 個道館需要修復")
        else:
            print("\n✅ 所有道館等級都正確！")
            
        return incorrect_arenas
        
    except Exception as e:
        print(f"❌ 檢查道館等級時出錯: {e}")
        return []

def get_sample_arena_details():
    """獲取一些樣本道館的詳細資料"""
    try:
        print("\n🔍 檢查樣本道館詳細資料...")
        
        # 獲取幾個道館的詳細資料
        sample_names = [
            "政大道館",
            "動物園道館", 
            "木柵道館",
            "指南宮道館",
            "貓空道館"
        ]
        
        for arena_name in sample_names:
            try:
                response = requests.get(f'{API_BASE_URL}/game/api/arena/get-by-name/{arena_name}')
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') and result.get('arena'):
                        arena = result['arena']
                        routes = arena.get('routes', [])
                        level = arena.get('level', 1)
                        print(f"\n📍 {arena_name}:")
                        print(f"   等級: {level}")
                        print(f"   路線數: {len(routes)}")
                        print(f"   路線: {', '.join(routes) if routes else '無'}")
                        print(f"   等級正確: {'✅' if level == len(routes) else '❌'}")
                else:
                    print(f"   {arena_name}: 未找到")
            except Exception as e:
                print(f"   {arena_name}: 查詢錯誤 - {e}")
                
    except Exception as e:
        print(f"❌ 獲取樣本道館資料時出錯: {e}")

def main():
    print("🔧 道館等級檢查工具")
    print("=" * 40)
    
    # 測試 API 連接
    if not test_api_connection():
        print("\n❌ 無法連接到 API，請確保遊戲伺服器正在運行")
        return
    
    # 檢查道館等級
    incorrect_arenas = check_arena_levels()
    
    # 獲取樣本道館詳細資料
    get_sample_arena_details()
    
    # 總結
    print("\n" + "=" * 40)
    if incorrect_arenas:
        print(f"⚠️  發現 {len(incorrect_arenas)} 個道館等級需要修復")
        print("💡 建議: 使用道館管理後台手動修復，或聯繫開發人員")
    else:
        print("✅ 所有道館等級檢查完成，沒有發現問題")

if __name__ == "__main__":
    main()
