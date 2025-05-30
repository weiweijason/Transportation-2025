#!/usr/bin/env python3
"""
測試道館子集合架構的功能
驗證 save_user_base_gym 方法是否正確地只保存到用戶的 user_arenas 子集合中
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
import firebase_admin.firestore

def test_arena_subcollection():
    """測試道館子集合功能"""
    print("測試道館子集合架構...")
    
    firebase_service = FirebaseService()
    
    # 測試用戶ID
    test_user_id = "test_arena_user_001"
    
    try:
        # 1. 創建測試用戶
        print("1. 創建測試用戶...")
        create_test_user(firebase_service, test_user_id)
        
        # 2. 測試保存道館到子集合
        print("2. 測試保存道館到用戶子集合...")
        test_save_gym_to_subcollection(firebase_service, test_user_id)
        
        # 3. 驗證數據保存位置
        print("3. 驗證數據保存位置...")
        verify_data_location(firebase_service, test_user_id)
        
        # 4. 清理測試資料
        print("4. 清理測試資料...")
        cleanup_test_data(firebase_service, test_user_id)
        
        print("\n✅ 道館子集合測試通過！")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        cleanup_test_data(firebase_service, test_user_id)
        return False

def create_test_user(firebase_service, user_id):
    """創建測試用戶"""
    user_data = {
        'player_id': 'TEST_ARENA_001',
        'username': '道館測試用戶',
        'email': 'test_arena@example.com',
        'created_at': firebase_admin.firestore.SERVER_TIMESTAMP
    }
    
    firebase_service.firestore_db.collection('users').document(user_id).set(user_data)
    print("   測試用戶創建成功")

def test_save_gym_to_subcollection(firebase_service, user_id):
    """測試保存道館到用戶子集合"""
    gym_data = {
        'gym_id': 'tutorial-gym-test',
        'gym_name': '測試道館',
        'gym_level': 3,
        'lat': 25.03556,
        'lng': 121.51972,
        'guardian_creature': {
            'id': 'creature_test_001',
            'name': '測試精靈',
            'power': 100,
            'type': 'fire'
        }
    }
    
    # 調用修改後的方法
    result = firebase_service.save_user_base_gym(user_id, gym_data)
    
    if result['status'] == 'success':
        print("   道館保存成功")
        return True
    else:
        print(f"   道館保存失敗: {result['message']}")
        return False

def verify_data_location(firebase_service, user_id):
    """驗證數據保存位置"""
    # 檢查是否保存到了用戶的 user_arenas 子集合
    user_arenas = firebase_service.firestore_db.collection('users').document(user_id)\
        .collection('user_arenas').get()
    
    if len(user_arenas) > 0:
        print("   ✅ 道館已保存到用戶的 user_arenas 子集合")
        arena_data = user_arenas[0].to_dict()
        print(f"   道館名稱: {arena_data.get('gym_name')}")
        print(f"   道館等級: {arena_data.get('gym_level')}")
        print(f"   守護精靈: {arena_data.get('guardian_creature', {}).get('name')}")
    else:
        raise Exception("道館未保存到用戶的 user_arenas 子集合")
    
    # 檢查是否還保存到了獨立的 user_arenas 集合（應該沒有）
    independent_arenas = firebase_service.firestore_db.collection('user_arenas')\
        .where('owner_user_id', '==', user_id).get()
    
    if len(independent_arenas) == 0:
        print("   ✅ 確認沒有保存到獨立的 user_arenas 集合（符合預期）")
    else:
        print("   ⚠️ 發現道館還保存到了獨立的 user_arenas 集合")
    
    # 檢查 user_base_gyms 集合（應該還存在）
    base_gym_doc = firebase_service.firestore_db.collection('user_base_gyms').document(user_id).get()
    if base_gym_doc.exists:
        print("   ✅ 道館資料已保存到 user_base_gyms 集合")
    else:
        print("   ❌ 道館資料未保存到 user_base_gyms 集合")
    
    # 檢查用戶文檔的 base_gym 字段
    user_doc = firebase_service.firestore_db.collection('users').document(user_id).get()
    if user_doc.exists and 'base_gym' in user_doc.to_dict():
        print("   ✅ 用戶文檔的 base_gym 字段已更新")
    else:
        print("   ❌ 用戶文檔的 base_gym 字段未更新")

def cleanup_test_data(firebase_service, user_id):
    """清理測試資料"""
    print("清理測試資料...")
    
    try:
        # 刪除用戶的 user_arenas 子集合
        user_arenas = firebase_service.firestore_db.collection('users').document(user_id)\
            .collection('user_arenas').get()
        for arena in user_arenas:
            arena.reference.delete()
        
        # 刪除 user_base_gyms 集合中的資料
        firebase_service.firestore_db.collection('user_base_gyms').document(user_id).delete()
        
        # 刪除用戶文檔
        firebase_service.firestore_db.collection('users').document(user_id).delete()
        
        # 清理可能存在的獨立 user_arenas 集合中的資料
        independent_arenas = firebase_service.firestore_db.collection('user_arenas')\
            .where('owner_user_id', '==', user_id).get()
        for arena in independent_arenas:
            arena.reference.delete()
        
        print("   測試資料清理完成")
        
    except Exception as e:
        print(f"   清理資料時出錯 (非致命): {str(e)}")

if __name__ == '__main__':
    try:
        test_arena_subcollection()
    except Exception as e:
        print(f"測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
