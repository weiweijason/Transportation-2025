#!/usr/bin/env python3
"""
資料遷移腳本：將 friends_pending 從陣列轉換為子集合
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
import firebase_admin.firestore
from datetime import datetime

def migrate_friends_pending():
    """將 friends_pending 從陣列遷移到子集合"""
    
    print("開始遷移 friends_pending 資料...")
    firebase_service = FirebaseService()
    
    # 獲取所有用戶
    users_ref = firebase_service.firestore_db.collection('users')
    users = users_ref.get()
    
    migrated_count = 0
    error_count = 0
    
    for user_doc in users:
        try:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            
            # 檢查是否有 friends_pending 陣列
            friends_pending = user_data.get('friends_pending', [])
            
            if friends_pending:
                print(f"處理用戶 {user_data.get('username', 'Unknown')} (ID: {user_data.get('player_id', user_id)})")
                print(f"  待處理申請: {friends_pending}")
                
                # 為每個 pending friend 在子集合中創建文件
                for requester_player_id in friends_pending:
                    try:
                        # 獲取申請者的用戶名稱
                        requester_query = firebase_service.firestore_db.collection('users')\
                            .where('player_id', '==', requester_player_id).limit(1).get()
                        
                        requester_username = '未知用戶'
                        if requester_query:
                            requester_data = requester_query[0].to_dict()
                            requester_username = requester_data.get('username', '未知用戶')
                        
                        # 在子集合中新增申請記錄
                        firebase_service.firestore_db.collection('users').document(user_id)\
                            .collection('friends_pending').add({
                                'requester_player_id': requester_player_id,
                                'requester_username': requester_username,
                                'requested_at': firebase_admin.firestore.SERVER_TIMESTAMP,
                                'status': 'pending',
                                'migrated_from_array': True  # 標記為從陣列遷移
                            })
                        
                        print(f"    已遷移申請: {requester_player_id} ({requester_username})")
                        
                    except Exception as e:
                        print(f"    遷移申請失敗 {requester_player_id}: {str(e)}")
                        error_count += 1
                
                # 移除舊的 friends_pending 陣列
                try:
                    firebase_service.firestore_db.collection('users').document(user_id).update({
                        'friends_pending': firebase_admin.firestore.DELETE_FIELD
                    })
                    print(f"  已移除舊的 friends_pending 陣列")
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"  移除陣列失敗: {str(e)}")
                    error_count += 1
                    
            else:
                print(f"用戶 {user_data.get('username', 'Unknown')} 沒有待處理的好友申請")
                
        except Exception as e:
            print(f"處理用戶 {user_doc.id} 失敗: {str(e)}")
            error_count += 1
    
    print(f"\n遷移完成！")
    print(f"成功遷移的用戶: {migrated_count}")
    print(f"錯誤次數: {error_count}")

def verify_migration():
    """驗證遷移結果"""
    print("\n驗證遷移結果...")
    firebase_service = FirebaseService()
    
    users_ref = firebase_service.firestore_db.collection('users')
    users = users_ref.get()
    
    users_with_old_format = 0
    users_with_new_format = 0
    
    for user_doc in users:
        user_data = user_doc.to_dict()
        user_id = user_doc.id
        
        # 檢查是否還有舊格式的 friends_pending
        if 'friends_pending' in user_data:
            users_with_old_format += 1
            print(f"警告：用戶 {user_data.get('username', 'Unknown')} 仍有舊格式的 friends_pending")
        
        # 檢查新格式的子集合
        pending_requests = firebase_service.firestore_db.collection('users').document(user_id)\
            .collection('friends_pending').get()
        
        if pending_requests:
            users_with_new_format += 1
            print(f"用戶 {user_data.get('username', 'Unknown')} 有 {len(pending_requests)} 個待處理申請（新格式）")
    
    print(f"\n驗證結果：")
    print(f"使用舊格式的用戶: {users_with_old_format}")
    print(f"使用新格式的用戶: {users_with_new_format}")

if __name__ == '__main__':
    try:
        migrate_friends_pending()
        verify_migration()
    except Exception as e:
        print(f"遷移失敗: {str(e)}")
        sys.exit(1)
