from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
import inspect
import os
from app import create_app

# 創建API文檔藍圖
api_docs = Blueprint('api_docs', __name__, url_prefix='/api-docs')

@api_docs.route('/')
def index():
    """API文檔主頁"""
    return render_template('api_docs/index.html')

@api_docs.route('/api/endpoints')
def get_endpoints():
    """獲取所有API端點資訊"""
    from flask import current_app
    
    endpoints = []
    
    # 遍歷所有註冊的路由
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
            
        # 獲取視圖函數
        view_func = current_app.view_functions.get(rule.endpoint)
        if not view_func:
            continue
            
        # 獲取文檔字符串
        docstring = inspect.getdoc(view_func) or "無描述"
        
        # 獲取方法
        methods = list(rule.methods - {'HEAD', 'OPTIONS'})
        
        # 判斷是否為API端點
        is_api = (
            '/api/' in str(rule) or 
            rule.endpoint.startswith('api') or
            'api' in rule.endpoint.lower() or
            any(method in ['POST', 'PUT', 'DELETE', 'PATCH'] for method in methods)
        )
        
        endpoint_info = {
            'rule': str(rule),
            'endpoint': rule.endpoint,
            'methods': methods,
            'description': docstring,
            'is_api': is_api,
            'blueprint': rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'main',
            'requires_auth': _requires_authentication(view_func)
        }
        
        endpoints.append(endpoint_info)
    
    # 按藍圖分組
    grouped_endpoints = {}
    for endpoint in endpoints:
        blueprint = endpoint['blueprint']
        if blueprint not in grouped_endpoints:
            grouped_endpoints[blueprint] = []
        grouped_endpoints[blueprint].append(endpoint)
    
    return jsonify({
        'endpoints': endpoints,
        'grouped': grouped_endpoints,
        'total': len(endpoints)
    })

def _requires_authentication(view_func):
    """檢查視圖函數是否需要認證"""
    if hasattr(view_func, '__wrapped__'):
        # 檢查裝飾器
        func = view_func
        while hasattr(func, '__wrapped__'):
            if hasattr(func, '__name__') and 'login_required' in str(func):
                return True
            func = func.__wrapped__
    
    # 檢查源代碼中是否有login_required裝飾器
    try:
        source = inspect.getsource(view_func)
        return '@login_required' in source
    except:
        return False

@api_docs.route('/test')
@login_required
def test_interface():
    """API測試介面"""
    return render_template('api_docs/test.html')
