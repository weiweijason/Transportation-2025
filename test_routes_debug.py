#!/usr/bin/env python3
"""測試路由註冊的調試腳本"""

try:
    from app import create_app
    print("正在創建應用程序...")
    app = create_app(load_tdx=False)
    print("應用程序創建成功！")
    
    with app.app_context():
        print("\n=== 所有註冊的路由 ===")
        for rule in app.url_map.iter_rules():
            print(f'{rule.rule} -> {rule.endpoint} ({", ".join(rule.methods)})')
        
        print("\n=== Community 相關路由 ===")
        community_routes = [rule for rule in app.url_map.iter_rules() 
                           if 'community' in rule.endpoint]
        
        if community_routes:
            for rule in community_routes:
                print(f'{rule.rule} -> {rule.endpoint} ({", ".join(rule.methods)})')
        else:
            print("沒有找到 community 相關路由！")
        
        # 測試 url_for
        print("\n=== 測試 url_for ===")
        try:
            from flask import url_for
            friends_url = url_for('community.friends')
            print(f"url_for('community.friends') = {friends_url}")
        except Exception as e:
            print(f"url_for('community.friends') 失敗: {e}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
