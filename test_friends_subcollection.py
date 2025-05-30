#!/usr/bin/env python3
"""
測試新的 friends_pending 子集合架構
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
import firebase_admin.firestore

def test_subcollection_architecture():
    """測試子集合架構的功能"""
    print("測試 friends_pending 子集合架構...")
    
    firebase_service = FirebaseService()
    
    # 測試用戶 ID
    test_user_1_id = "test_user_1"
    test_user_2_id = "test_user_2"
    
    # 清理測試資料
    cleanup_test_data(firebase_service, test_user_1_id, test_user_2_id)
    
    # 創建測試用戶
    create_test_users(firebase_service, test_user_1_id, test_user_2_id)
    
    # 測試好友申請流程
    test_friend_request_flow(firebase_service, test_user_1_id, test_user_2_id)
    
    # 清理測試資料
    cleanup_test_data(firebase_service, test_user_1_id, test_user_2_id)
    
    print("測試完成！")

def create_test_users(firebase_service, user1_id, user2_id):
    """創建測試用戶"""
    print("創建測試用戶...")
    
    # 用戶 1
    firebase_service.firestore_db.collection('users').document(user1_id).set({
        'player_id': 'TEST0001',
        'username': '測試用戶1',
        'email': 'test1@example.com',
        'friends': []
    })
    
    # 用戶 2
    firebase_service.firestore_db.collection('users').document(user2_id).set({
        'player_id': 'TEST0002', 
        'username': '測試用戶2',
        'email': 'test2@example.com',
        'friends': []
    })
    
    print("測試用戶創建完成")

def test_friend_request_flow(firebase_service, user1_id, user2_id):
    """測試好友申請流程"""
    print("測試好友申請流程...")
    
    # 1. 用戶1向用戶2發送好友申請
    print("1. 發送好友申請...")
    firebase_service.firestore_db.collection('users').document(user2_id)\
        .collection('friends_pending').add({
            'requester_player_id': 'TEST0001',
            'requester_username': '測試用戶1',
            'requested_at': firebase_admin.firestore.SERVER_TIMESTAMP,
            'status': 'pending'
        })
    
    # 2. 檢查申請是否已存在
    print("2. 檢查申請是否存在...")
    existing_requests = firebase_service.firestore_db.collection('users').document(user2_id)\
        .collection('friends_pending').where('requester_player_id', '==', 'TEST0001').get()
    
    if existing_requests:
        print(f"   找到 {len(existing_requests)} 個申請")
        for req in existing_requests:
            req_data = req.to_dict()
            print(f"   申請ID: {req.id}")
            print(f"   申請者: {req_data.get('requester_username')}")
            print(f"   狀態: {req_data.get('status')}")
    else:
        print("   未找到申請記錄")
        return
    
    # 3. 模擬接受申請
    print("3. 接受好友申請...")
    request_doc = existing_requests[0]
    request_data = request_doc.to_dict()
    
    # 刪除申請記錄
    request_doc.reference.delete()
    
    # 雙方加為好友
    firebase_service.firestore_db.collection('users').document(user1_id).update({
        'friends': firebase_admin.firestore.ArrayUnion(['TEST0002'])
    })
    
    firebase_service.firestore_db.collection('users').document(user2_id).update({
        'friends': firebase_admin.firestore.ArrayUnion(['TEST0001'])
    })
    
    print("   好友申請已接受")
    
    # 4. 驗證結果
    print("4. 驗證結果...")
    user1_doc = firebase_service.firestore_db.collection('users').document(user1_id).get()
    user2_doc = firebase_service.firestore_db.collection('users').document(user2_id).get()
    
    user1_friends = user1_doc.to_dict().get('friends', [])
    user2_friends = user2_doc.to_dict().get('friends', [])
    
    print(f"   用戶1的好友: {user1_friends}")
    print(f"   用戶2的好友: {user2_friends}")
    
    # 檢查申請是否已刪除
    remaining_requests = firebase_service.firestore_db.collection('users').document(user2_id)\
        .collection('friends_pending').get()
    
    print(f"   剩餘申請數量: {len(remaining_requests)}")

def cleanup_test_data(firebase_service, user1_id, user2_id):
    """清理測試資料"""
    print("清理測試資料...")
    
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
        
        # 刪除用戶文件
        firebase_service.firestore_db.collection('users').document(user1_id).delete()
        firebase_service.firestore_db.collection('users').document(user2_id).delete()
        
        print("測試資料清理完成")
        
    except Exception as e:
        print(f"清理資料時發生錯誤: {str(e)}")

def list_current_requests():
    """列出當前所有好友申請（用於調試）"""
    print("列出當前所有好友申請...")
    
    firebase_service = FirebaseService()
    users = firebase_service.firestore_db.collection('users').get()
    
    for user_doc in users:
        user_data = user_doc.to_dict()
        user_id = user_doc.id
        username = user_data.get('username', 'Unknown')
        player_id = user_data.get('player_id', user_id)
        
        # 檢查子集合
        pending_requests = firebase_service.firestore_db.collection('users').document(user_id)\
            .collection('friends_pending').get()
        
        if pending_requests:
            print(f"\n用戶: {username} ({player_id})")
            for req in pending_requests:
                req_data = req.to_dict()
                print(f"  申請ID: {req.id}")
                print(f"  申請者: {req_data.get('requester_username')} ({req_data.get('requester_player_id')})")
                print(f"  時間: {req_data.get('requested_at')}")
                print(f"  狀態: {req_data.get('status')}")

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'list':
            list_current_requests()
        else:
            test_subcollection_architecture()
    except Exception as e:
        print(f"測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
