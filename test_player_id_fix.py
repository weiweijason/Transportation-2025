#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修正後的好友申請功能
驗證 player_id 查詢是否正常工作
"""

from app.services.firebase_service import FirebaseService

def test_player_id_search():
    """測試根據 player_id 查詢用戶功能"""
    
    print("=" * 60)
    print("測試 player_id 查詢功能")
    print("=" * 60)
    
    # 初始化 Firebase 服務
    try:
        firebase_service = FirebaseService()
        print("✅ Firebase 服務初始化成功")
    except Exception as e:
        print(f"❌ Firebase 服務初始化失敗: {e}")
        return
    
    # 測試查詢功能
    def get_user_by_player_id(player_id):
        """根據 player_id 查詢用戶文件"""
        users_query = firebase_service.firestore_db.collection('users').where('player_id', '==', player_id).limit(1).get()
        if users_query:
            return users_query[0], users_query[0].id
        return None, None
    
    print("\n1. 獲取所有用戶以找到測試用的 player_id...")
    try:
        all_users = firebase_service.firestore_db.collection('users').limit(5).get()
        
        test_player_ids = []
        for user_doc in all_users:
            user_data = user_doc.to_dict()
            player_id = user_data.get('player_id')
            if player_id:
                test_player_ids.append(player_id)
                print(f"  找到用戶: {user_data.get('username', '未知')} (player_id: {player_id}) (文件ID: {user_doc.id})")
        
        if not test_player_ids:
            print("❌ 沒有找到具有 player_id 的用戶")
            return
        
        print(f"\n2. 測試 player_id 查詢功能...")
        
        for test_player_id in test_player_ids[:2]:  # 只測試前兩個
            print(f"\n測試 player_id: {test_player_id}")
            
            # 使用新的查詢方法
            user_doc, user_doc_id = get_user_by_player_id(test_player_id)
            
            if user_doc:
                user_data = user_doc.to_dict()
                print(f"✅ 查詢成功!")
                print(f"   文件ID: {user_doc_id}")
                print(f"   用戶名: {user_data.get('username', '未知')}")
                print(f"   player_id: {user_data.get('player_id')}")
                print(f"   好友列表: {user_data.get('friends', [])}")
                print(f"   待處理申請: {user_data.get('friends_pending', [])}")
            else:
                print(f"❌ 查詢失敗: 找不到 player_id 為 {test_player_id} 的用戶")
        
        print(f"\n3. 測試邀請碼驗證...")
        
        # 模擬好友申請流程
        if len(test_player_ids) >= 2:
            sender_id = test_player_ids[0]
            receiver_invite_code = test_player_ids[1]
            
            print(f"模擬: {sender_id} 向 {receiver_invite_code} 發送好友申請")
            
            # 查詢發送者
            sender_doc, sender_doc_id = get_user_by_player_id(sender_id)
            if sender_doc:
                print(f"✅ 發送者查詢成功: {sender_doc.to_dict().get('username')}")
            else:
                print(f"❌ 發送者查詢失敗")
            
            # 查詢接收者
            receiver_doc, receiver_doc_id = get_user_by_player_id(receiver_invite_code)
            if receiver_doc:
                print(f"✅ 接收者查詢成功: {receiver_doc.to_dict().get('username')}")
            else:
                print(f"❌ 接收者查詢失敗")
                
            if sender_doc and receiver_doc:
                print("✅ 好友申請流程驗證：雙方用戶都能正確查詢到")
            else:
                print("❌ 好友申請流程驗證失敗")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

def test_invite_code_format():
    """測試邀請碼格式"""
    print("\n" + "=" * 60)
    print("測試邀請碼格式")
    print("=" * 60)
    
    # 初始化 Firebase 服務
    try:
        firebase_service = FirebaseService()
        
        # 獲取一些用戶的 player_id 來檢查格式
        users = firebase_service.firestore_db.collection('users').limit(10).get()
        
        player_ids = []
        for user_doc in users:
            user_data = user_doc.to_dict()
            player_id = user_data.get('player_id')
            if player_id:
                player_ids.append(player_id)
        
        print(f"找到 {len(player_ids)} 個 player_id:")
        for pid in player_ids:
            length = len(pid)
            print(f"  {pid} (長度: {length})")
            
        # 檢查是否都是8位
        eight_char_ids = [pid for pid in player_ids if len(pid) == 8]
        print(f"\n8位長度的 player_id: {len(eight_char_ids)}/{len(player_ids)}")
        
        if eight_char_ids:
            print("✅ 找到符合8位格式的邀請碼")
        else:
            print("⚠️ 沒有找到8位格式的邀請碼，可能需要調整驗證邏輯")
        
    except Exception as e:
        print(f"❌ 測試邀請碼格式時發生錯誤: {e}")

if __name__ == "__main__":
    print("開始測試修正後的好友申請功能...")
    test_player_id_search()
    test_invite_code_format()
    print("\n測試完成！")
    print("\n重要提醒:")
    print("- 現在系統會根據 player_id 欄位查詢用戶，而不是文件 ID")
    print("- 確保你的邀請碼是用戶的 player_id，而不是 Firebase 文件 ID")
    print("- 如果仍然無法發送好友申請，請檢查日誌輸出以獲取詳細錯誤信息")
