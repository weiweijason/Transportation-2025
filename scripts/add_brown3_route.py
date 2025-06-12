#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加棕3路線到數據庫的腳本
"""

import os
import sys

# 將目前工作目錄加入到 sys.path，以便能夠匯入應用程式模組
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
sys.path.append(app_dir)

from app import create_app, db
from app.models.bus import BusRoute

def check_existing_routes():
    """檢查現有的路線記錄"""
    print("檢查現有路線記錄...")
    routes = BusRoute.query.all()
    print(f"現有路線數量: {len(routes)}")
    
    for route in routes:
        print(f"路線ID: {route.route_id}, 名稱: {route.name}, 元素類型: {route.element_type}")
    
    return routes

def add_brown3_route():
    """添加棕3路線記錄"""
    print("\n檢查是否已存在棕3路線...")
    
    # 檢查是否已存在棕3路線
    existing_route = BusRoute.query.filter_by(route_id='brown-3').first()
    if existing_route:
        print(f"棕3路線已存在: {existing_route.name}")
        return existing_route
    
    print("創建棕3路線記錄...")
    
    # 創建棕3路線記錄
    brown3_route = BusRoute(
        route_id='brown-3',
        name='棕3路線',
        departure='棕3起點站',
        destination='棕3終點站',
        city='台北市',
        operator='台北客運',  # 假設營運業者，實際可能需要查詢
        element_type='earth'  # 設定為土系元素，可根據需要調整
    )
    
    try:
        db.session.add(brown3_route)
        db.session.commit()
        print(f"✅ 成功添加棕3路線: {brown3_route.name}")
        return brown3_route
    except Exception as e:
        db.session.rollback()
        print(f"❌ 添加棕3路線失敗: {e}")
        return None

def main():
    """主函數"""
    print("=== 添加棕3路線到數據庫 ===")
    
    # 創建應用實例
    app = create_app(load_tdx=False)
    
    with app.app_context():
        # 檢查現有路線
        existing_routes = check_existing_routes()
        
        # 添加棕3路線
        brown3_route = add_brown3_route()
        
        if brown3_route:
            print("\n=== 更新後的路線列表 ===")
            check_existing_routes()
            print("\n✅ 棕3路線添加完成！")
        else:
            print("\n❌ 棕3路線添加失敗！")

if __name__ == '__main__':
    main()
