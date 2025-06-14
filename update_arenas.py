#!/usr/bin/env python3
"""
更新道館緩存，包含棕3路線
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.arena import update_arena_cache_from_tdx

def main():
    print("開始更新道館緩存（包含棕3路線）...")
    
    try:
        result = update_arena_cache_from_tdx()
        
        if result:
            print("✅ 道館緩存更新成功！")
            
            # 檢查更新結果
            import json
            cache_file = "app/data/arenas/arena_levels.json"
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    arenas = json.load(f)
                
                total_arenas = len(arenas)
                brown3_arenas = []
                
                for arena_id, arena in arenas.items():
                    routes = arena.get('routes', [])
                    if '棕3' in routes:
                        brown3_arenas.append(arena)
                
                print(f"📊 更新統計:")
                print(f"   總道館數量: {total_arenas}")
                print(f"   包含棕3路線的道館: {len(brown3_arenas)}")
                
                if brown3_arenas:
                    print(f"📍 棕3路線道館示例:")
                    for i, arena in enumerate(brown3_arenas[:5]):
                        print(f"   {i+1}. {arena['name']} - 路線: {', '.join(arena['routes'])}")
                        
            return True
            
        else:
            print("❌ 道館緩存更新失敗")
            return False
            
    except Exception as e:
        print(f"❌ 更新過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
