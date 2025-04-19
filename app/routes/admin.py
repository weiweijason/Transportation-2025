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