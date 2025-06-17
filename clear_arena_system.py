#!/usr/bin/env python3
"""
道館系統清空重製腳本
清空所有道館數據，包括 Firebase 中的道館和用戶道館佔領記錄
"""

import sys
import os
import json

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.firebase_service import FirebaseService
from datetime import datetime
import time

def clear_all_arenas(firebase_service):
    """清空所有道館"""
    try:
        print("🔄 開始清空所有道館...")
        
        # 獲取所有道館
        arenas_ref = firebase_service.firestore_db.collection('arenas')
        arenas = arenas_ref.get()
        
        deleted_count = 0
        for arena_doc in arenas:
            try:
                arena_doc.reference.delete()
                deleted_count += 1
                print(f"✅ 已刪除道館: {arena_doc.id}")
            except Exception as e:
                print(f"❌ 刪除道館 {arena_doc.id} 失敗: {e}")
        
        print(f"🎯 道館清空完成，共刪除 {deleted_count} 個道館")
        return deleted_count
        
    except Exception as e:
        print(f"❌ 清空道館失敗: {e}")
        return 0

def clear_all_user_arenas(firebase_service):
    """清空所有用戶的道館佔領記錄"""
    try:
        print("🔄 開始清空所有用戶道館記錄...")
        
        # 獲取所有用戶
        users_ref = firebase_service.firestore_db.collection('users')
        users = users_ref.get()
        
        cleared_users = 0
        cleared_records = 0
        
        for user_doc in users:
            try:
                user_id = user_doc.id
                
                # 獲取用戶的道館記錄
                user_arenas_ref = user_doc.reference.collection('user_arenas')
                user_arenas = user_arenas_ref.get()
                
                user_arena_count = 0
                for arena_doc in user_arenas:
                    try:
                        arena_doc.reference.delete()
                        user_arena_count += 1
                        cleared_records += 1
                    except Exception as e:
                        print(f"❌ 刪除用戶 {user_id} 的道館記錄 {arena_doc.id} 失敗: {e}")
                
                if user_arena_count > 0:
                    cleared_users += 1
                    print(f"✅ 已清空用戶 {user_id} 的 {user_arena_count} 個道館記錄")
                    
            except Exception as e:
                print(f"❌ 處理用戶 {user_doc.id} 失敗: {e}")
        
        print(f"🎯 用戶道館記錄清空完成，共清空 {cleared_users} 個用戶的 {cleared_records} 個記錄")
        return cleared_users, cleared_records
        
    except Exception as e:
        print(f"❌ 清空用戶道館記錄失敗: {e}")
        return 0, 0

def clear_arena_cache():
    """清空道館緩存檔案"""
    try:
        print("🔄 開始清空道館緩存...")
        
        cache_dir = os.path.join(project_root, 'app', 'data', 'arenas')
        cache_file = os.path.join(cache_dir, 'arena_levels.json')
        
        if os.path.exists(cache_file):
            # 備份原檔案
            backup_file = os.path.join(cache_dir, f'arena_levels_backup_{int(time.time())}.json')
            os.rename(cache_file, backup_file)
            print(f"✅ 已備份原緩存檔案到: {backup_file}")
            
            # 創建空的緩存檔案
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已清空道館緩存檔案: {cache_file}")
        else:
            print("ℹ️ 道館緩存檔案不存在，無需清空")
            
    except Exception as e:
        print(f"❌ 清空道館緩存失敗: {e}")

def reset_arena_system():
    """重設道館系統"""
    try:
        print("\n" + "="*60)
        print("🚀 開始道館系統完全重製")
        print("="*60)
        
        # 初始化 Firebase 服務
        firebase_service = FirebaseService()
        
        # 確認操作
        print("\n⚠️ 警告：此操作將完全清空所有道館數據！")
        print("包括：")
        print("  - 所有 Firebase 道館記錄")
        print("  - 所有用戶道館佔領記錄")
        print("  - 本地道館緩存檔案")
        
        confirm = input("\n您確定要繼續嗎？請輸入 'YES' 確認: ")
        
        if confirm != "YES":
            print("❌ 操作已取消")
            return
        
        print("\n開始清空程序...")
        
        # 1. 清空所有道館
        arena_count = clear_all_arenas(firebase_service)
        
        # 2. 清空所有用戶道館記錄
        user_count, record_count = clear_all_user_arenas(firebase_service)
        
        # 3. 清空道館緩存
        clear_arena_cache()
        
        print("\n" + "="*60)
        print("🎉 道館系統重製完成！")
        print("="*60)
        print(f"📊 清空統計：")
        print(f"  - 道館數量: {arena_count}")
        print(f"  - 用戶記錄: {user_count} 個用戶的 {record_count} 個記錄")
        print(f"  - 緩存檔案: 已清空並備份")
        
        print("\n💡 下一步建議：")
        print("  1. 執行 sync_arenas_to_firebase.py 重新創建道館")
        print("  2. 或者重新啟動應用程式，系統會自動創建道館")
        print("  3. 檢查應用程式運行狀況")
        
    except Exception as e:
        print(f"❌ 道館系統重製失敗: {e}")
        import traceback
        traceback.print_exc()

def create_basic_arenas():
    """創建基礎測試道館"""
    try:
        print("🔄 創建基礎測試道館...")
        
        firebase_service = FirebaseService()
        
        # 基礎測試道館
        test_arenas = [
            {
                'id': 'test-arena-level-1',
                'name': '新手測試道館',
                'level': 1,
                'owner': None,
                'owner_player_id': None,
                'owner_creature': None,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_battles': 0,
                'rewards': {
                    'last_collected': None,
                    'accumulated_hours': 0,
                    'available_rewards': []
                }
            },
            {
                'id': 'test-arena-level-2',
                'name': '進階測試道館',
                'level': 2,
                'owner': None,
                'owner_player_id': None,
                'owner_creature': None,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_battles': 0,
                'rewards': {
                    'last_collected': None,
                    'accumulated_hours': 0,
                    'available_rewards': []
                }
            },
            {
                'id': 'test-arena-level-3',
                'name': '高級測試道館',
                'level': 3,
                'owner': None,
                'owner_player_id': None,
                'owner_creature': None,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_battles': 0,
                'rewards': {
                    'last_collected': None,
                    'accumulated_hours': 0,
                    'available_rewards': []
                }
            }
        ]
        
        created_count = 0
        for arena_data in test_arenas:
            try:
                arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_data['id'])
                arena_ref.set(arena_data)
                created_count += 1
                print(f"✅ 已創建測試道館: {arena_data['name']} (等級 {arena_data['level']})")
            except Exception as e:
                print(f"❌ 創建測試道館 {arena_data['name']} 失敗: {e}")
        
        print(f"🎯 基礎測試道館創建完成，共創建 {created_count} 個道館")
        
    except Exception as e:
        print(f"❌ 創建基礎測試道館失敗: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create-test":
            create_basic_arenas()
        elif sys.argv[1] == "--clear-only":
            firebase_service = FirebaseService()
            clear_all_arenas(firebase_service)
            clear_all_user_arenas(firebase_service)
            clear_arena_cache()
        else:
            print("用法:")
            print("  python clear_arena_system.py              # 完全重製道館系統")
            print("  python clear_arena_system.py --clear-only  # 僅清空數據，不創建測試道館")
            print("  python clear_arena_system.py --create-test # 僅創建基礎測試道館")
    else:
        reset_arena_system()
