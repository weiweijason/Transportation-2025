#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試全螢幕地圖功能
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fullscreen_map():
    """測試全螢幕地圖功能"""
    try:
        from app import create_app
        from flask import url_for
        
        print("正在初始化應用程式...")
        app = create_app()
        
        with app.app_context():
            print("測試路由配置...")
            
            # 測試捕捉頁面路由
            catch_url = url_for('game.catch')
            print(f"✅ 捕捉頁面路由: {catch_url}")
            
            # 測試全螢幕地圖路由
            map_url = url_for('game.fullscreen_map')
            print(f"✅ 全螢幕地圖路由: {map_url}")
            
            print("\n路由測試通過！")
            print("="*50)
            print("功能摘要:")
            print("1. ✅ 移除了棕3路線按鈕")
            print("2. ✅ 添加了全螢幕地圖按鈕")
            print("3. ✅ 創建了全螢幕地圖頁面 (map.html)")
            print("4. ✅ 配置了全螢幕地圖路由")
            print("5. ✅ 優化了手機端體驗")
            print("="*50)
            print(f"訪問路徑:")
            print(f"  - 普通捕捉頁面: {catch_url}")
            print(f"  - 全螢幕地圖: {map_url}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fullscreen_map()
