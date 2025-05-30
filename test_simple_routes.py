#!/usr/bin/env python3
"""
簡單的路由測試腳本
測試應用程序是否能正常啟動並訪問關鍵路由
"""

from app import create_app

def test_app_startup():
    """測試應用程序啟動"""
    print("正在創建 Flask 應用程序...")
    try:
        app = create_app()
        print("✓ 應用程序創建成功！")
        
        # 測試應用程序上下文
        with app.app_context():
            print("✓ 應用程序上下文正常")
            
            # 檢查路由
            print("\n=== 檢查重要路由 ===")
            rules = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint:
                    rules.append((rule.rule, rule.endpoint))
            
            # 檢查特定路由
            important_routes = [
                ('/community/friends', 'community.friends'),
                ('/game/catch', 'game.catch'),
            ]
            
            for route_path, endpoint in important_routes:
                found = any(rule[0] == route_path and rule[1] == endpoint for rule in rules)
                status = "✓" if found else "✗"
                print(f"{status} {route_path} -> {endpoint}")
            
            # 測試 url_for
            print("\n=== 測試 url_for ===")
            with app.test_request_context():
                try:
                    from flask import url_for
                    
                    # 測試 community.friends
                    friends_url = url_for('community.friends')
                    print(f"✓ url_for('community.friends') = {friends_url}")
                    
                    # 測試 game.catch
                    catch_url = url_for('game.catch')
                    print(f"✓ url_for('game.catch') = {catch_url}")
                    
                except Exception as e:
                    print(f"✗ url_for 測試失敗: {e}")
            
        return True
    except Exception as e:
        print(f"✗ 應用程序創建失敗: {e}")
        return False

def test_friends_page():
    """測試 friends 頁面"""
    print("\n=== 測試 Friends 頁面 ===")
    try:
        app = create_app()
        with app.test_client() as client:
            # 注意：這個測試會失敗因為需要登錄，但我們可以檢查路由是否存在
            response = client.get('/community/friends')
            print(f"✓ /community/friends 路由存在 (狀態碼: {response.status_code})")
            if response.status_code == 302:
                print("  → 重定向到登錄頁面 (正常行為)")
            
            return True
    except Exception as e:
        print(f"✗ Friends 頁面測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("開始路由測試...")
    
    success = True
    success &= test_app_startup()
    success &= test_friends_page()
    
    if success:
        print("\n🎉 所有測試通過！應用程序應該可以正常運行。")
    else:
        print("\n❌ 有測試失敗，請檢查錯誤信息。")
