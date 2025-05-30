#!/usr/bin/env python3
from app import create_app

if __name__ == "__main__":
    app = create_app()
    print("Flask app created successfully!")
    
    # 檢查所有路由
    print("\n所有註冊的路由:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
    
    # 特別檢查 community 路由
    print("\nCommunity 路由:")
    community_routes = [rule for rule in app.url_map.iter_rules() if 'community' in rule.endpoint]
    for route in community_routes:
        print(f"  {route.endpoint}: {route.rule}")
