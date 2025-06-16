from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash, current_app
from flask_login import login_required
import inspect
import os
from functools import wraps
from app import create_app

# 創建API文檔藍圖
api_docs = Blueprint('api_docs', __name__, url_prefix='/api-docs')

def api_docs_required(f):
    """API 文檔認證裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 檢查是否已通過認證
        if not session.get('api_docs_authenticated'):
            return redirect(url_for('api_docs.login'))
        return f(*args, **kwargs)
    return decorated_function

@api_docs.route('/login', methods=['GET', 'POST'])
def login():
    """API 文檔登入頁面"""
    if request.method == 'POST':
        password = request.form.get('password')
        # 從配置中獲取密碼
        api_docs_password = current_app.config.get('API_DOCS_PASSWORD', 'devdocs2024')
        
        if password == api_docs_password:
            session['api_docs_authenticated'] = True
            flash('成功進入 API 文檔系統', 'success')
            return redirect(url_for('api_docs.index'))
        else:
            flash('密碼錯誤', 'danger')
    
    return render_template('api_docs/login.html')

@api_docs.route('/logout')
def logout():
    """API 文檔登出"""
    session.pop('api_docs_authenticated', None)
    flash('已登出 API 文檔系統', 'info')
    return redirect(url_for('api_docs.login'))

@api_docs.route('/')
@api_docs_required
def index():
    """API文檔主頁"""
    return render_template('api_docs/index.html')

@api_docs.route('/api/endpoints')
@api_docs_required
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
@api_docs_required
def test_interface():
    """API測試介面"""
    return render_template('api_docs/test.html')
