#!/usr/bin/env python3
"""
簡單測試道館子集合功能
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple():
    try:
        print("開始測試...")
        
        # 導入 Firebase 服務
        from app.services.firebase_service import FirebaseService
        print("✅ Firebase 服務導入成功")
        
        # 初始化服務
        firebase_service = FirebaseService()
        print("✅ Firebase 服務初始化成功")
        
        # 測試用戶ID
        test_user_id = "test_simple_user_001"
        
        # 測試道館數據
        gym_data = {
            'gym_id': 'test-simple-gym',
            'gym_name': '簡單測試道館',
            'gym_level': 2,
            'lat': 25.03556,
            'lng': 121.51972,
            'guardian_creature': {
                'id': 'test_creature_001',
                'name': '測試精靈',
                'power': 80,
                'type': 'electric'
            }
        }
        
        print(f"測試保存道館到用戶 {test_user_id}...")
        
        # 先確保用戶存在
        user_ref = firebase_service.firestore_db.collection('users').document(test_user_id)
        user_ref.set({
            'player_id': 'TEST_SIMPLE_001',
            'username': '簡單測試用戶',
            'email': 'test_simple@example.com'
        })
        print("✅ 測試用戶創建成功")
        
        # 保存道館
        result = firebase_service.save_user_base_gym(test_user_id, gym_data)
        
        if result['status'] == 'success':
            print("✅ 道館保存成功")
            
            # 檢查是否保存到用戶子集合
            user_arenas = user_ref.collection('user_arenas').get()
            if len(user_arenas) > 0:
                print("✅ 確認：道館已保存到用戶的 user_arenas 子集合")
                arena_data = user_arenas[0].to_dict()
                print(f"   道館名稱: {arena_data.get('gym_name')}")
                print(f"   道館等級: {arena_data.get('gym_level')}")
            else:
                print("❌ 道館未保存到用戶子集合")
                  # 檢查是否還有保存到獨立集合（應該沒有）
            try:
                base_gym_doc = firebase_service.firestore_db.collection('user_base_gyms').document(test_user_id).get()
                if base_gym_doc.exists:
                    print("⚠️  警告：道館仍保存在獨立的 user_base_gyms 集合中")
                else:
                    print("✅ 確認：沒有保存到獨立的 user_base_gyms 集合")
            except Exception as e:
                print(f"檢查獨立集合時出錯: {e}")
            
            # 檢查是否還有保存為 base_gym 字段（應該沒有）
            try:
                user_doc_check = user_ref.get()
                user_data = user_doc_check.to_dict()
                if 'base_gym' in user_data:
                    print("⚠️  警告：道館仍保存為用戶文檔的 base_gym 字段")
                else:
                    print("✅ 確認：沒有保存為用戶文檔的 base_gym 字段")
            except Exception as e:
                print(f"檢查用戶文檔時出錯: {e}")
                
        else:
            print(f"❌ 道館保存失敗: {result['message']}")
            
        # 清理測試數據
        print("清理測試數據...")
        try:
            # 刪除用戶子集合
            arenas = user_ref.collection('user_arenas').get()
            for arena in arenas:
                arena.reference.delete()
            
            # 刪除用戶文檔
            user_ref.delete()
            
            # 清理可能的獨立集合數據
            firebase_service.firestore_db.collection('user_base_gyms').document(test_user_id).delete()
            
            print("✅ 測試數據清理完成")
        except Exception as e:
            print(f"清理數據時出錯: {e}")
            
        print("\n🎉 測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple()
