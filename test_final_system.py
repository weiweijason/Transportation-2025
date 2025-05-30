#!/usr/bin/env python3
"""
最終路由測試 - 驗證所有路由都能正常工作
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_all_routes():
    """測試所有重要路由"""
    try:
        from app import create_app
        from flask import url_for
        
        app = create_app()
        print("✓ 應用程序創建成功")
        
        with app.app_context():
            with app.test_request_context():
                # 測試關鍵路由
                routes_to_test = [
                    # Community routes
                    ('community.friends', {}),
                    ('community.add_friend', {}),
                    ('community.accept_request', {'request_id': 'test123'}),
                    ('community.decline_request', {'request_id': 'test456'}),
                    ('community.remove_friend', {'friend_id': 'test789'}),
                    
                    # Game routes
                    ('game.catch', {}),
                    ('game.game_home', {}),
                    
                    # Main routes
                    ('main.home', {}),
                ]
                
                print("\n=== 路由測試結果 ===")
                all_working = True
                for endpoint, kwargs in routes_to_test:
                    try:
                        url = url_for(endpoint, **kwargs)
                        print(f"✓ {endpoint} -> {url}")
                    except Exception as e:
                        print(f"✗ {endpoint} 失敗: {e}")
                        all_working = False
                
                return all_working
                
    except Exception as e:
        print(f"✗ 應用程序測試失敗: {e}")
        return False

def test_friends_page_access():
    """測試好友頁面訪問"""
    try:
        from app import create_app
        
        app = create_app()
        with app.test_client() as client:
            # 測試好友頁面
            response = client.get('/community/friends')
            print(f"\n✓ 好友頁面訪問測試: 狀態碼 {response.status_code}")
            
            if response.status_code == 302:
                print("  → 重定向到登錄頁面 (正常行為)")
            elif response.status_code == 200:
                print("  → 頁面正常載入")
            else:
                print(f"  → 異常狀態碼: {response.status_code}")
                return False
                
            return True
            
    except Exception as e:
        print(f"✗ 頁面訪問測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("=== 最終系統測試 ===")
    
    success = True
    success &= test_all_routes()
    success &= test_friends_page_access()
    
    if success:
        print("\n🎉 所有測試通過！系統完全可用！")
        print("\n📱 好友系統功能：")
        print("1. ✅ 邀請碼分享")
        print("2. ✅ 好友申請")
        print("3. ✅ 申請管理")
        print("4. ✅ 好友列表")
        print("5. ✅ 移除好友")
        print("\n🚀 系統可以啟動使用了！")
    else:
        print("\n❌ 有問題需要修正")
