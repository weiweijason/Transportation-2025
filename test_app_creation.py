#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from app import create_app
    print("Importing app module...")
    
    app = create_app(load_tdx=False)
    print("App created successfully!")
    
    # 測試路由註冊
    with app.app_context():
        print("\n=== Game related routes ===")
        for rule in app.url_map.iter_rules():
            if 'game' in rule.endpoint:
                print(f'{rule.rule} -> {rule.endpoint} ({", ".join(rule.methods)})')
        
        print("\n=== Testing url_for ===")
        from flask import url_for
        try:
            catch_url = url_for('game.catch')
            print(f'url_for("game.catch") = {catch_url}')
        except Exception as e:
            print(f'Error with game.catch: {e}')
        
        try:
            community_url = url_for('community.friends')
            print(f'url_for("community.friends") = {community_url}')
        except Exception as e:
            print(f'Error with community.friends: {e}')
            
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
