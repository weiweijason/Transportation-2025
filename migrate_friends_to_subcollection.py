#!/usr/bin/env python3
"""
資料遷移腳本：將 friends 從陣列轉換為子集合
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
import firebase_admin.firestore
from datetime import datetime

def migrate_friends_to_subcollection():
    """將 friends 從陣列遷移到子集合"""
    
    print("開始遷移 friends 資料...")
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
            user_player_id = user_data.get('player_id', user_id)
            
            # 檢查是否有 friends 陣列
            friends = user_data.get('friends', [])
            
            if friends:
                print(f"處理用戶 {user_data.get('username', 'Unknown')} (ID: {user_player_id})")
                print(f"  朋友列表: {friends}")
                
                # 為每個好友在子集合中創建文件
                for friend_player_id in friends:
                    try:
                        # 獲取好友的用戶名稱
                        friend_query = firebase_service.firestore_db.collection('users')\
                            .where('player_id', '==', friend_player_id).limit(1).get()
                        
                        friend_username = '未知用戶'
                        if friend_query:
                            friend_data = friend_query[0].to_dict()
                            friend_username = friend_data.get('username', '未知用戶')
                        
                        # 在子集合中新增好友記錄
                        firebase_service.firestore_db.collection('users').document(user_id)\
                            .collection('friends').document(friend_player_id).set({
                                'friend_player_id': friend_player_id,
                                'friend_username': friend_username,
                                'added_at': firebase_admin.firestore.SERVER_TIMESTAMP,
                                'status': 'active',
                                'migrated_from_array': True  # 標記為從陣列遷移
                            })
                        
                        print(f"    已遷移好友: {friend_player_id} ({friend_username})")
                        
                    except Exception as e:
                        print(f"    遷移好友失敗 {friend_player_id}: {str(e)}")
                        error_count += 1
                
                # 移除舊的 friends 陣列
                try:
                    firebase_service.firestore_db.collection('users').document(user_id).update({
                        'friends': firebase_admin.firestore.DELETE_FIELD
                    })
                    print(f"  已移除舊的 friends 陣列")
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"  移除陣列失敗: {str(e)}")
                    error_count += 1
                    
            else:
                print(f"用戶 {user_data.get('username', 'Unknown')} 沒有好友資料，跳過")
                
        except Exception as e:
            print(f"處理用戶失敗: {str(e)}")
            error_count += 1
    
    print(f"\n遷移完成！")
    print(f"成功遷移: {migrated_count} 個用戶")
    print(f"錯誤數量: {error_count}")

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
        
        # 檢查是否還有舊格式的 friends
        if 'friends' in user_data:
            users_with_old_format += 1
            print(f"警告：用戶 {user_data.get('username', 'Unknown')} 仍有舊格式的 friends")
        
        # 檢查新格式的子集合
        friend_docs = firebase_service.firestore_db.collection('users').document(user_id)\
            .collection('friends').get()
        
        if friend_docs:
            users_with_new_format += 1
            print(f"用戶 {user_data.get('username', 'Unknown')} 有 {len(friend_docs)} 個好友（新格式）")
    
    print(f"\n驗證結果：")
    print(f"使用舊格式的用戶: {users_with_old_format}")
    print(f"使用新格式的用戶: {users_with_new_format}")

if __name__ == '__main__':
    try:
        migrate_friends_to_subcollection()
        verify_migration()
    except Exception as e:
        print(f"遷移失敗: {str(e)}")
        sys.exit(1)
