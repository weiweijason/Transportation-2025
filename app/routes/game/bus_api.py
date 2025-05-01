from flask import Blueprint, jsonify, current_app
import requests
from app.services.tdx_service import (get_cat_right_route, get_cat_left_route, 
                                     get_cat_left_zhinan_route, get_cat_right_stops,
                                     get_cat_left_stops, get_cat_left_zhinan_stops,
                                     get_tdx_token, TDX_API_URL)

# 修改藍圖前綴為 /game/api/bus 以符合前端預期
bus_bp = Blueprint('game_bus', __name__, url_prefix='/game/api/bus')

# 公車路線 API
@bus_bp.route('/cat-right-route')
def get_cat_right_route_api():
    route_data = get_cat_right_route()
    return jsonify(route_data)

@bus_bp.route('/cat-left-route')
def get_cat_left_route_api():
    route_data = get_cat_left_route()
    return jsonify(route_data)

@bus_bp.route('/cat-left-zhinan-route')
def get_cat_left_zhinan_route_api():
    route_data = get_cat_left_zhinan_route()
    return jsonify(route_data)

# 公車站牌 API
@bus_bp.route('/cat-right-stops')
def get_cat_right_stops_api():
    stops_data = get_cat_right_stops()
    return jsonify(stops_data)

@bus_bp.route('/cat-left-stops')
def get_cat_left_stops_api():
    stops_data = get_cat_left_stops()
    return jsonify(stops_data)

@bus_bp.route('/cat-left-zhinan-stops')
def get_cat_left_zhinan_stops_api():
    stops_data = get_cat_left_zhinan_stops()
    return jsonify(stops_data)

# V3 Network API 路由 - 直接使用站點資料
@bus_bp.route('/network/cat-right')
def get_cat_right_network_api():
    """獲取貓空右線的V3 Network API數據"""
    # 使用現有的站點資料替代
    stops_data = get_cat_right_stops()
    return jsonify(stops_data)

@bus_bp.route('/network/cat-left')
def get_cat_left_network_api():
    """獲取貓空左線(動物園)的V3 Network API數據"""
    # 使用現有的站點資料替代
    stops_data = get_cat_left_stops()
    return jsonify(stops_data)

@bus_bp.route('/network/cat-left-zhinan')
def get_cat_left_zhinan_network_api():
    """獲取貓空左線(指南宮)的V3 Network API數據"""
    # 使用現有的站點資料替代
    stops_data = get_cat_left_zhinan_stops()
    return jsonify(stops_data)

# 新增: 直接從TDX API獲取公車站點網路資料
@bus_bp.route('/network/stations')
def get_network_stations_api():
    """直接從TDX API獲取公車站點網路資料
    
    使用原始TDX API URL: /V3/Map/Bus/Network/Station/City/Taipei 
    並篩選貓空相關路線
    """
    import requests
    
    # 獲取TDX API令牌
    token = get_tdx_token()
    if not token:
        return jsonify([])
    
    # 使用原始TDX API URL請求站點數據
    url = f"{TDX_API_URL}/V3/Map/Bus/Network/Station/City/Taipei?%24select=%E8%B2%93%E7%A9%BA&%24top=50&%24format=JSON"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 返回數據
        return jsonify(data)
    except Exception as e:
        current_app.logger.error(f"獲取站點數據錯誤: {e}")
        return jsonify([])