#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試全螢幕地圖初始化
"""

from flask import Flask, render_template
import os
import sys

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
           template_folder='app/templates',
           static_folder='app/static')

@app.route('/test-map')
def test_map():
    """測試全螢幕地圖頁面"""
    firebase_config = {
        'apiKey': 'test',
        'authDomain': 'test',
        'projectId': 'test'
    }
    return render_template('game/map.html', firebase_config=firebase_config)

@app.route('/test-catch')
def test_catch():
    """測試捕捉頁面"""
    firebase_config = {
        'apiKey': 'test',
        'authDomain': 'test',
        'projectId': 'test'
    }
    return render_template('game/catch.html', firebase_config=firebase_config)

if __name__ == '__main__':
    print("啟動測試服務器...")
    print("測試頁面:")
    print("  - 全螢幕地圖: http://localhost:5001/test-map")
    print("  - 捕捉頁面: http://localhost:5001/test-catch")
    print("\n在瀏覽器中打開上述連結進行測試")
    print("按 Ctrl+C 停止服務器")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
