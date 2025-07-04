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

@api_docs.route('/daily-checkin-apis')
@api_docs_required
def daily_checkin_apis():
    """每日簽到系統API文檔"""
    return render_template('api_docs/daily_checkin_apis.html')

@api_docs.route('/exchange-shop-apis')
@api_docs_required
def exchange_shop_apis():
    """兌換商店系統API文檔"""
    return render_template('api_docs/exchange_shop_apis.html')

@api_docs.route('/api/daily-checkin-endpoints')
@api_docs_required
def get_daily_checkin_endpoints():
    """獲取每日簽到相關API端點資訊"""
    daily_checkin_apis = [
        {
            'endpoint': '/daily-migration/',
            'method': 'GET',
            'description': '每日簽到頁面',
            'auth_required': True,
            'parameters': [],
            'response_example': {
                'type': 'HTML',
                'description': '返回每日簽到頁面的HTML內容'
            }
        },
        {
            'endpoint': '/daily-migration/api/get-migration-status',
            'method': 'GET',
            'description': '獲取用戶的每日簽到狀態',
            'auth_required': True,
            'parameters': [],
            'response_example': {
                'success': True,
                'migration_data': {
                    'user_id': 'user123',
                    'username': '玩家名稱',
                    'today': '2025-06-17',
                    'has_migrated_today': False,
                    'total_migrations': 15,
                    'consecutive_days': 3,
                    'last_migration_date': '2025-06-16'
                }
            }
        },
        {
            'endpoint': '/daily-migration/api/perform-migration',
            'method': 'POST',
            'description': '執行每日簽到',
            'auth_required': True,
            'parameters': [],
            'response_example': {
                'success': True,
                'message': '簽到完成！獲得了豐富的獎勵！',
                'rewards': {
                    'experience': 100,
                    'items': [
                        {
                            'item_id': 'normal_potion_fragment',
                            'quantity': 1,
                            'name': '普通藥水碎片'
                        }
                    ],
                    'consecutive_days': 3,
                    'bonus_multiplier': 1.3
                },
                'new_experience': 1500,
                'triggered_achievements': []
            }
        },
        {
            'endpoint': '/daily-migration/api/get-migration-history',
            'method': 'GET',
            'description': '獲取簽到歷史記錄',
            'auth_required': True,
            'parameters': [],
            'response_example': {
                'success': True,
                'history': [
                    {
                        'date': '2025-06-16',
                        'experience': 100,
                        'items': [
                            {
                                'item_id': 'normal_potion_fragment',
                                'quantity': 1,
                                'name': '普通藥水碎片'
                            }
                        ],
                        'time': '2025-06-16T10:30:00'
                    }
                ]
            }
        }
    ]
    
    return jsonify({
        'apis': daily_checkin_apis,
        'total': len(daily_checkin_apis)
    })

@api_docs.route('/api/exchange-shop-endpoints')
@api_docs_required
def get_exchange_shop_endpoints():
    """獲取兌換商店相關API端點資訊"""
    exchange_shop_apis = [
        {
            'endpoint': '/exchange-shop/',
            'method': 'GET',
            'description': '兌換商店頁面',
            'auth_required': True,
            'parameters': [],
            'response_example': {
                'type': 'HTML',
                'description': '返回兌換商店頁面的HTML內容'
            }
        },
        {
            'endpoint': '/exchange-shop/api/get-exchange-data',
            'method': 'GET',
            'description': '獲取兌換相關數據',
            'auth_required': True,
            'parameters': [],
            'response_example': {
                'success': True,
                'exchange_data': {
                    'normal_potion_fragments': 15,
                    'normal_potions': 2,
                    'magic_circle_normal': 25,
                    'magic_circle_advanced': 3,
                    'magic_circle_legendary': 0
                }
            }
        },
        {
            'endpoint': '/exchange-shop/api/exchange-potion-fragments',
            'method': 'POST',
            'description': '兌換普通藥水碎片為普通藥水（7碎片 = 1藥水）',
            'auth_required': True,
            'parameters': [],
            'response_example': {
                'success': True,
                'message': '成功兌換2瓶普通藥水！',
                'exchanged_potions': 2,
                'remaining_fragments': 1,
                'total_potions': 4
            },
            'error_example': {
                'success': False,
                'message': '碎片不足！需要7個碎片，目前只有3個'
            }
        },        {
            'endpoint': '/exchange-shop/api/exchange-magic-circles',
            'method': 'POST',
            'description': '兌換魔法陣（10普通 = 1進階，10進階 = 1高級）- 支援自選兌換數量',
            'auth_required': True,
            'parameters': [
                {
                    'name': 'exchange_type',
                    'type': 'string',
                    'required': True,
                    'description': '兌換類型：normal_to_advanced 或 advanced_to_legendary'
                },
                {
                    'name': 'exchange_amount',
                    'type': 'integer',
                    'required': False,
                    'default': 1,
                    'description': '兌換次數（用戶可自選），必須大於0'
                }
            ],
            'request_example': {
                'exchange_type': 'normal_to_advanced',
                'exchange_amount': 3
            },
            'response_example': {
                'success': True,
                'message': '成功兌換3個進階魔法陣！',
                'exchanged_amount': 3,
                'remaining_normal': 15,
                'total_advanced': 8
            },
            'error_examples': [
                {
                    'case': '數量不足',
                    'response': {
                        'success': False,
                        'message': '普通魔法陣不足！需要30個進行3次兌換，目前只有25個'
                    }
                },
                {
                    'case': '無效數量',
                    'response': {
                        'success': False,
                        'message': '兌換數量必須大於0'
                    }
                },
                {
                    'case': '參數錯誤',
                    'response': {
                        'success': False,
                        'message': '無效的兌換數量'
                    }
                }
            ],
            'notes': [
                '用戶可以選擇兌換次數，不再強制全部兌換',
                '每次兌換消耗10個低級魔法陣，獲得1個高級魔法陣',
                '前端提供+/-按鈕和數字輸入框供用戶選擇',
                '系統會自動計算最大可兌換次數並限制用戶輸入'
            ]
        }
    ]
    
    return jsonify({
        'apis': exchange_shop_apis,
        'total': len(exchange_shop_apis)
    })
