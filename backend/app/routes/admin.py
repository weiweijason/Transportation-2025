from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import logging
from functools import wraps

from app.services.tdx_service import fetch_all_data, get_data_status, LOCAL_DATA_EXPIRE_HOURS

# 創建管理員藍圖
admin_bp = Blueprint('admin', __name__)

# 管理員裝飾器，確保只有管理員可以訪問後台頁面
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('請先登入', 'warning')
            return redirect(url_for('auth.login'))
        
        # 檢查是否為管理員 (根據用戶資料中的 is_admin 欄位)
        if not getattr(current_user, 'is_admin', False):
            flash('需要管理員權限訪問此頁面', 'danger')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function

# 管理後台首頁
@admin_bp.route('/')
@admin_required
def admin_index():
    """顯示管理後台主頁"""
    return render_template('admin/index.html')

# 資料管理頁面
@admin_bp.route('/data')
@admin_required
def data_management():
    """顯示資料管理頁面"""
    # 獲取所有資料的狀態
    data_status = get_data_status()
    
    # 組織資料狀態為易於理解的格式
    routes_data = []
    stops_data = []
    
    for data_type, status in data_status.items():
        item = {
            'type': data_type,
            'name': get_data_type_name(data_type),
            'status': status
        }
        
        if 'route' in data_type:
            routes_data.append(item)
        elif 'stops' in data_type:
            stops_data.append(item)
    
    # 排序資料
    routes_data.sort(key=lambda x: x['name'])
    stops_data.sort(key=lambda x: x['name'])
    
    context = {
        'routes_data': routes_data,
        'stops_data': stops_data,
        'expire_hours': LOCAL_DATA_EXPIRE_HOURS
    }
    
    return render_template('admin/data_management.html', **context)

# 更新 TDX API 資料
@admin_bp.route('/data/refresh', methods=['POST'])
@admin_required
def refresh_data():
    """手動更新 TDX API 資料"""
    try:
        data_type = request.form.get('data_type')
        
        # 如果沒有指定資料類型，刷新全部資料
        if not data_type or data_type == 'all':
            results = fetch_all_data()
            success = all(results.values())
            message = '所有資料刷新完成' if success else '部分資料刷新失敗，請查看日誌'
        else:
            # TODO: 實現特定資料類型刷新
            # 這裡暫時仍然刷新所有資料
            results = fetch_all_data()
            success = all(results.values())
            message = f'{get_data_type_name(data_type)}資料刷新完成' if success else f'{get_data_type_name(data_type)}資料刷新失敗'
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'warning')
            
        return redirect(url_for('admin.data_management'))
    except Exception as e:
        logging.error(f"資料刷新錯誤: {e}")
        flash(f'資料刷新過程中發生錯誤: {str(e)}', 'danger')
        return redirect(url_for('admin.data_management'))

# API 端點 - 獲取資料概況
@admin_bp.route('/api/data-summary')
@admin_required
def api_data_summary():
    """提供資料概況的 API 端點"""
    # 獲取所有資料的狀態
    data_status = get_data_status()
    
    # 計算各種統計資料
    routes_count = sum(1 for k in data_status if 'route' in k)
    stops_count = sum(1 for k in data_status if 'stops' in k)
    
    # 獲取最後更新時間
    last_update_time = None
    for _, status in data_status.items():
        if status['timestamp']:
            if not last_update_time or status['timestamp'] > last_update_time:
                last_update_time = status['timestamp']
    
    # 計算時間格式
    last_update_time_ago = format_time_ago(last_update_time) if last_update_time else '未知'
    
    # 模擬 API 請求數據（實際可從監控系統獲取）
    api_requests_count = 87  # 實際中可以從監控系統獲取
    
    return jsonify({
        'routesCount': routes_count,
        'stopsCount': stops_count,
        'lastUpdateTime': last_update_time,
        'lastUpdateTimeAgo': last_update_time_ago,
        'apiRequestsCount': api_requests_count
    })

# API 端點 - 獲取資料健康狀態
@admin_bp.route('/api/data-health')
@admin_required
def api_data_health():
    """提供資料健康狀態的 API 端點"""
    # 獲取所有資料的狀態
    data_status = get_data_status()
    
    # 計算路線資料健康度
    routes_data = [
        {'exists': status['exists'], 'isExpired': status['is_expired']}
        for key, status in data_status.items() if 'route' in key
    ]
    routes_health = calculate_data_health(routes_data)
    
    # 計算站點資料健康度
    stops_data = [
        {'exists': status['exists'], 'isExpired': status['is_expired']}
        for key, status in data_status.items() if 'stops' in key
    ]
    stops_health = calculate_data_health(stops_data)
    
    # 模擬時間健康度 (實際可以基於最後更新時間計算)
    time_health = 75
    
    # 模擬 API 健康度 (實際可以基於 API 調用成功率計算)
    api_health = 35
    
    return jsonify({
        'routesHealth': routes_health,
        'stopsHealth': stops_health,
        'timeHealth': time_health,
        'apiHealth': api_health
    })

# 輔助函數 - 計算資料健康度百分比
def calculate_data_health(data_array):
    """計算資料健康度百分比"""
    if not data_array:
        return 0
    
    healthy_count = sum(1 for item in data_array if item['exists'] and not item['isExpired'])
    return round((healthy_count / len(data_array)) * 100)

# 輔助函數 - 格式化時間（多久之前）
def format_time_ago(timestamp):
    """將時間戳格式化為'多久之前'的形式"""
    if not timestamp:
        return '未知'
    
    from datetime import datetime
    import pytz
    
    try:
        # 嘗試將時間字符串轉換為 datetime 對象
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        
        # 確保時間是 aware 的
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        
        now = datetime.now(pytz.utc)
        diff_seconds = (now - dt).total_seconds()
        
        if diff_seconds < 60:
            return '剛剛'
        elif diff_seconds < 3600:
            return f"{int(diff_seconds // 60)} 分鐘前"
        elif diff_seconds < 86400:
            return f"{int(diff_seconds // 3600)} 小時前"
        else:
            return f"{int(diff_seconds // 86400)} 天前"
    except Exception as e:
        logging.error(f"格式化時間錯誤: {e}")
        return '未知'

# 輔助函數 - 獲取資料類型的中文名稱
def get_data_type_name(data_type):
    """將資料類型轉換為易讀的名稱"""
    type_names = {
        'cat-right-route': '貓空右線路線',
        'cat-left-route': '貓空左線(動物園)路線',
        'cat-left-zhinan-route': '貓空左線(指南宮)路線',
        'cat-right-stops': '貓空右線站點',
        'cat-left-stops': '貓空左線(動物園)站點',
        'cat-left-zhinan-stops': '貓空左線(指南宮)站點'
    }
    
    return type_names.get(data_type, data_type)