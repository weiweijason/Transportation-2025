#!/usr/bin/env python3
"""
同步棕3路線道館到Firebase
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService
from app.models.arena import load_arena_cache
import json

def sync_brown3_arenas_to_firebase():
    """同步棕3路線道館到Firebase"""
    print("開始同步棕3路線道館到Firebase...")
    
    try:
        # 載入本地道館緩存
        load_arena_cache()
        
        # 讀取道館緩存檔案
        cache_file = "app/data/arenas/arena_levels.json"
        
        if not os.path.exists(cache_file):
            print("❌ 道館緩存檔案不存在")
            return False
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            arenas = json.load(f)
        
        # 篩選出棕3路線的道館
        brown3_arenas = []
        for arena_id, arena in arenas.items():
            routes = arena.get('routes', [])
            if '棕3' in routes:
                brown3_arenas.append(arena)
        
        print(f"找到 {len(brown3_arenas)} 個棕3路線道館")
        
        if not brown3_arenas:
            print("❌ 沒有找到棕3路線道館")
            return False
        
        # 初始化Firebase服務
        firebase_service = FirebaseService()
        
        # 同步每個道館到Firebase
        synced_count = 0
        for arena in brown3_arenas:
            try:
                arena_id = arena['id']
                arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
                
                # 檢查道館是否已存在於Firebase
                arena_doc = arena_ref.get()
                
                if not arena_doc.exists:
                    # 道館不存在，創建新文檔
                    arena_ref.set(arena)
                    print(f"✅ 新增道館到Firebase: {arena.get('name', arena_id)}")
                    synced_count += 1
                else:
                    # 道館已存在，更新資料
                    arena_ref.update(arena)
                    print(f"🔄 更新Firebase中的道館: {arena.get('name', arena_id)}")
                    synced_count += 1
                    
            except Exception as e:
                print(f"❌ 同步道館失敗 {arena.get('name', arena_id)}: {e}")
                continue
        
        print(f"📊 同步完成!")
        print(f"   總共處理: {len(brown3_arenas)} 個道館")
        print(f"   成功同步: {synced_count} 個道館")
        
        return True
        
    except Exception as e:
        print(f"❌ 同步過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_firebase_arenas():
    """驗證Firebase中的道館資料"""
    print("\n驗證Firebase中的道館資料...")
    
    try:
        firebase_service = FirebaseService()
        
        # 獲取所有道館
        arenas_ref = firebase_service.firestore_db.collection('arenas')
        arenas_docs = arenas_ref.get()
        
        total_arenas = len(arenas_docs)
        brown3_arenas = []
        
        for doc in arenas_docs:
            arena_data = doc.to_dict()
            routes = arena_data.get('routes', [])
            if '棕3' in routes:
                brown3_arenas.append(arena_data)
        
        print(f"📊 Firebase驗證結果:")
        print(f"   Firebase中總道館數: {total_arenas}")
        print(f"   Firebase中棕3道館數: {len(brown3_arenas)}")
        
        if brown3_arenas:
            print(f"📍 Firebase中的棕3道館示例:")
            for i, arena in enumerate(brown3_arenas[:5]):
                print(f"   {i+1}. {arena.get('name', '未知')} - 路線: {', '.join(arena.get('routes', []))}")
        
        return len(brown3_arenas) > 0
        
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {e}")
        return False

def main():
    print("=== 棕3路線道館同步工具 ===")
    
    # 先驗證當前Firebase狀態
    has_brown3_before = verify_firebase_arenas()
    
    if not has_brown3_before:
        print("\n📤 開始同步棕3道館到Firebase...")
        success = sync_brown3_arenas_to_firebase()
        
        if success:
            print("\n🔍 同步後再次驗證...")
            verify_firebase_arenas()
        
        return success
    else:
        print("\n✅ Firebase中已有棕3道館資料，無需同步")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
