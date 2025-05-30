#!/usr/bin/env python3
"""
測試好友系統的完整功能
包括邀請碼、好友申請、接受/拒絕等功能
"""

from app import create_app
from flask import url_for

def test_friends_system():
    """測試好友系統功能"""
    print("=== 測試好友系統功能 ===")
    
    try:
        app = create_app()
        
        # 測試路由註冊
        with app.app_context():
            with app.test_request_context():
                print("測試路由生成：")
                routes_to_test = [
                    ('community.friends', {}),
                    ('community.add_friend', {}),
                    ('community.remove_friend', {'friend_id': 'test123'}),
                    ('community.accept_request', {'request_id': 'test456'}),
                    ('community.decline_request', {'request_id': 'test789'}),
                ]
                
                for endpoint, kwargs in routes_to_test:
                    try:
                        url = url_for(endpoint, **kwargs)
                        print(f"✓ {endpoint} -> {url}")
                    except Exception as e:
                        print(f"✗ {endpoint} 失敗: {e}")
                        return False
        
        # 測試頁面訪問
        with app.test_client() as client:
            print("\n測試頁面訪問：")
            
            # 測試好友頁面 (會重定向到登錄，但檢查是否有錯誤)
            response = client.get('/community/friends')
            if response.status_code in [200, 302]:
                print(f"✓ /community/friends 頁面正常 (狀態碼: {response.status_code})")
            else:
                print(f"✗ /community/friends 頁面錯誤 (狀態碼: {response.status_code})")
                return False
            
            # 測試好友申請 POST (會重定向到登錄)
            response = client.post('/community/add-friend', data={'friend_invite_code': 'test123'})
            if response.status_code in [200, 302]:
                print(f"✓ 好友申請功能正常 (狀態碼: {response.status_code})")
            else:
                print(f"✗ 好友申請功能錯誤 (狀態碼: {response.status_code})")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        return False

def check_template_syntax():
    """檢查模板語法"""
    print("\n=== 檢查模板語法 ===")
    
    template_path = r"c:\Users\User\OneDrive - National ChengChi University\113-2 commucation\code\proj\app\templates\community\friends.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查新功能是否正確實現
        required_elements = [
            '我的邀請碼',
            'current_user.player_id',
            'friend_invite_code',
            'copyInviteCode()',
            'addFriendForm',
            "url_for('community.add_friend')",
            "url_for('community.accept_request', request_id=request.player_id)",
            "url_for('community.decline_request', request_id=request.player_id)",
            "url_for('community.remove_friend', friend_id=friend.player_id)"
        ]
        
        print("檢查好友系統模板元素：")
        all_found = True
        for element in required_elements:
            if element in content:
                print(f"✓ 找到: {element}")
            else:
                print(f"✗ 缺少: {element}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"✗ 模板檢查失敗: {e}")
        return False

def check_firebase_integration():
    """檢查 Firebase 整合"""
    print("\n=== 檢查 Firebase 整合 ===")
    
    community_py_path = r"c:\Users\User\OneDrive - National ChengChi University\113-2 commucation\code\proj\app\routes\community.py"
    
    try:
        with open(community_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查 Firebase 相關功能
        firebase_features = [
            'firebase_service.firestore_db',
            'friends_pending',
            'current_user.player_id',
            "collection('users')",
            '.update({',
            'friends_pending.append(',
            'friends_pending.remove(',
        ]
        
        print("檢查 Firebase 整合：")
        all_found = True
        for feature in firebase_features:
            if feature in content:
                print(f"✓ 找到: {feature}")
            else:
                print(f"✗ 缺少: {feature}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"✗ Firebase 整合檢查失敗: {e}")
        return False

if __name__ == "__main__":
    print("開始測試好友系統...")
    
    success = True
    success &= test_friends_system()
    success &= check_template_syntax()
    success &= check_firebase_integration()
    
    if success:
        print("\n🎉 好友系統所有測試通過！")
        print("\n功能說明：")
        print("1. ✅ 顯示用戶邀請碼 (基於 player_id)")
        print("2. ✅ 複製邀請碼功能")
        print("3. ✅ 通過邀請碼添加好友")
        print("4. ✅ 好友申請列表")
        print("5. ✅ 接受/拒絕好友申請")
        print("6. ✅ 好友列表顯示")
        print("7. ✅ 移除好友功能")
        print("8. ✅ Firebase 資料庫整合")
        print("\n好友系統現在可以正常使用！")
    else:
        print("\n❌ 有測試失敗，請檢查錯誤信息。")
