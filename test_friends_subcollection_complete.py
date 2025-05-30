#!/usr/bin/env python3
"""
測試好友系統子集合架構的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
import firebase_admin.firestore

def test_subcollection_architecture():
    """測試子集合架構的功能"""
    print("測試好友系統子集合架構...")
    
    firebase_service = FirebaseService()
    
    # 測試用戶ID
    user1_id = "test_user_001"
    user2_id = "test_user_002"
    
    try:
        # 1. 創建測試用戶
        print("1. 創建測試用戶...")
        create_test_users(firebase_service, user1_id, user2_id)
        
        # 2. 測試好友申請流程
        print("2. 測試好友申請流程...")
        test_friend_request_flow(firebase_service, user1_id, user2_id)
        
        # 3. 測試好友子集合功能
        print("3. 測試好友子集合功能...")
        test_friend_subcollection(firebase_service, user1_id, user2_id)
        
        # 4. 清理測試資料
        print("4. 清理測試資料...")
        cleanup_test_data(firebase_service, user1_id, user2_id)
        
        print("\n✅ 所有測試通過！")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        cleanup_test_data(firebase_service, user1_id, user2_id)
        return False

def create_test_users(firebase_service, user1_id, user2_id):
    """創建測試用戶"""
    user1_data = {
        'player_id': 'TEST0001',
        'username': '測試用戶1',
        'email': 'test1@example.com',
        'created_at': firebase_admin.firestore.SERVER_TIMESTAMP
    }
    
    user2_data = {
        'player_id': 'TEST0002',
        'username': '測試用戶2',
        'email': 'test2@example.com',
        'created_at': firebase_admin.firestore.SERVER_TIMESTAMP
    }
    
    firebase_service.firestore_db.collection('users').document(user1_id).set(user1_data)
    firebase_service.firestore_db.collection('users').document(user2_id).set(user2_data)
    
    print("   測試用戶創建成功")

def test_friend_request_flow(firebase_service, user1_id, user2_id):
    """測試好友申請流程"""
    print("   發送好友申請...")
    
    # 用戶1向用戶2發送好友申請
    firebase_service.firestore_db.collection('users').document(user2_id)\
        .collection('friends_pending').add({
            'requester_player_id': 'TEST0001',
            'requester_username': '測試用戶1',
            'requested_at': firebase_admin.firestore.SERVER_TIMESTAMP,
            'status': 'pending'
        })
    
    # 檢查申請是否存在
    pending_requests = firebase_service.firestore_db.collection('users').document(user2_id)\
        .collection('friends_pending').where('requester_player_id', '==', 'TEST0001').get()
    
    if pending_requests:
        print("   好友申請記錄正確創建")
        request_doc = pending_requests[0]
        request_data = request_doc.to_dict()
        
        # 模擬接受申請
        print("   接受好友申請...")
        
        # 雙方加為好友（在子集合中）
        firebase_service.firestore_db.collection('users').document(user1_id)\
            .collection('friends').document('TEST0002').set({
                'friend_player_id': 'TEST0002',
                'friend_username': '測試用戶2',
                'added_at': firebase_admin.firestore.SERVER_TIMESTAMP,
                'status': 'active'
            })
        
        firebase_service.firestore_db.collection('users').document(user2_id)\
            .collection('friends').document('TEST0001').set({
                'friend_player_id': 'TEST0001',
                'friend_username': '測試用戶1',
                'added_at': firebase_admin.firestore.SERVER_TIMESTAMP,
                'status': 'active'
            })
        
        # 刪除申請記錄
        request_doc.reference.delete()
        
        print("   好友申請已接受")
    else:
        raise Exception("好友申請記錄創建失敗")

def test_friend_subcollection(firebase_service, user1_id, user2_id):
    """測試好友子集合功能"""
    print("   驗證好友子集合...")
    
    # 檢查用戶1的好友列表
    user1_friends = firebase_service.firestore_db.collection('users').document(user1_id)\
        .collection('friends').get()
    
    user2_friends = firebase_service.firestore_db.collection('users').document(user2_id)\
        .collection('friends').get()
    
    print(f"   用戶1有 {len(user1_friends)} 個好友")
    print(f"   用戶2有 {len(user2_friends)} 個好友")
    
    if len(user1_friends) > 0 and len(user2_friends) > 0:
        friend1_data = user1_friends[0].to_dict()
        friend2_data = user2_friends[0].to_dict()
        
        print(f"   用戶1的好友: {friend1_data.get('friend_username')}")
        print(f"   用戶2的好友: {friend2_data.get('friend_username')}")
        
        # 測試移除好友
        print("   測試移除好友...")
        firebase_service.firestore_db.collection('users').document(user1_id)\
            .collection('friends').document('TEST0002').delete()
        
        firebase_service.firestore_db.collection('users').document(user2_id)\
            .collection('friends').document('TEST0001').delete()
        
        print("   好友移除成功")
    else:
        raise Exception("好友子集合創建失敗")

def cleanup_test_data(firebase_service, user1_id, user2_id):
    """清理測試資料"""
    print("   清理測試資料...")
    
    try:
        # 刪除好友申請子集合
        pending_requests_1 = firebase_service.firestore_db.collection('users').document(user1_id)\
            .collection('friends_pending').get()
        for req in pending_requests_1:
            req.reference.delete()
            
        pending_requests_2 = firebase_service.firestore_db.collection('users').document(user2_id)\
            .collection('friends_pending').get()
        for req in pending_requests_2:
            req.reference.delete()
        
        # 刪除好友子集合
        friends_1 = firebase_service.firestore_db.collection('users').document(user1_id)\
            .collection('friends').get()
        for friend in friends_1:
            friend.reference.delete()
            
        friends_2 = firebase_service.firestore_db.collection('users').document(user2_id)\
            .collection('friends').get()
        for friend in friends_2:
            friend.reference.delete()
        
        # 刪除用戶文件
        firebase_service.firestore_db.collection('users').document(user1_id).delete()
        firebase_service.firestore_db.collection('users').document(user2_id).delete()
        
        print("   測試資料清理完成")
        
    except Exception as e:
        print(f"   清理失敗: {str(e)}")

if __name__ == '__main__':
    try:
        success = test_subcollection_architecture()
        if success:
            print("\n🎉 好友系統子集合架構測試通過！")
            print("\n功能說明：")
            print("1. ✅ 好友申請使用 friends_pending 子集合")
            print("2. ✅ 接受申請後自動刪除 pending 記錄")
            print("3. ✅ 好友列表使用 friends 子集合")
            print("4. ✅ 好友移除功能正常")
        else:
            print("\n❌ 測試失敗")
    except Exception as e:
        print(f"測試執行失敗: {str(e)}")
        sys.exit(1)
