from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user
from app.services.tdx_service import TDXService
from app.models.bus import BusRoute, BusStop

# 創建遊戲藍圖
game = Blueprint('game', __name__)

@game.route('/catch')
@login_required
def catch_creatures():
    """捕捉精靈頁面"""
    return render_template('game/catch.html')

@game.route('/arena')
@login_required
def arena_list():
    """擂台列表頁面"""
    return render_template('game/arena_list.html')

@game.route('/battle')
@login_required
def battle():
    """PVP對戰頁面"""
    return render_template('game/battle.html')

@game.route('/api/bus/route/shape', methods=['GET'])
@login_required
def get_bus_route_shape():
    """獲取公車路線形狀的API端點"""
    city = request.args.get('city', 'Taipei')
    route_name = request.args.get('route_name')

    if not route_name:
        return jsonify({'error': '缺少必要參數: route_name'}), 400

    # 使用TDX服務獲取路線形狀數據
    tdx_service = TDXService()
    route_shape_data = tdx_service.get_bus_route_shape(city, route_name)

    return jsonify(route_shape_data)

@game.route('/api/bus/routes', methods=['GET'])
@login_required
def get_bus_routes():
    """獲取公車路線的API端點"""
    city = request.args.get('city', 'Taipei')
    
    # 從資料庫中查詢路線
    routes = BusRoute.query.filter_by(city=city).all()
    
    # 將路線資料轉換為JSON格式
    routes_data = [route.to_dict() for route in routes]
    
    return jsonify(routes_data)

@game.route('/api/bus/nearby-stops', methods=['GET'])
@login_required
def get_nearby_bus_stops():
    """獲取附近公車站點的API端點"""
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius', 500)
    city = request.args.get('city', 'Taipei')
    
    if not lat or not lon:
        return jsonify({'error': '缺少必要參數: lat, lon'}), 400
    
    # 使用TDX服務獲取附近站點
    tdx_service = TDXService()
    nearby_stops = tdx_service.get_nearby_stops(lat, lon, radius, city)
    
    return jsonify(nearby_stops)

@game.route('/api/bus/cat-left-route', methods=['GET'])
@login_required
def get_cat_left_route():
    """獲取貓空左線(動物園)路線形狀的API端點"""
    # 使用TDX服務獲取貓空左線路線形狀數據
    tdx_service = TDXService()
    route_shape_data = tdx_service.get_cat_left_route()
    
    # 檢查數據是否為空
    if not route_shape_data or (isinstance(route_shape_data, list) and len(route_shape_data) == 0):
        current_app.logger.error("獲取貓空左線(動物園)路線數據為空")
        return jsonify([]), 200
    
    return jsonify(route_shape_data)

@game.route('/api/bus/cat-right-route', methods=['GET'])
@login_required
def get_cat_right_route():
    """獲取貓空右線路線形狀的API端點"""
    # 使用TDX服務獲取貓空右線路線形狀數據
    tdx_service = TDXService()
    route_shape_data = tdx_service.get_cat_right_route()
    
    # 檢查數據是否為空
    if not route_shape_data or (isinstance(route_shape_data, list) and len(route_shape_data) == 0):
        current_app.logger.error("獲取貓空右線路線數據為空")
        return jsonify([]), 200
        
    # 記錄返回的數據格式，便於調試
    # current_app.logger.info(f"獲取貓空右線路線數據成功: {len(route_shape_data)} 條記錄")
    
    return jsonify(route_shape_data)

@game.route('/api/bus/cat-left-zhinan-route', methods=['GET'])
@login_required
def get_cat_left_zhinan_route():
    """獲取貓空左線(指南宮)路線形狀的API端點"""
    # 使用TDX服務獲取貓空左線(指南宮)路線形狀數據
    tdx_service = TDXService()
    route_shape_data = tdx_service.get_cat_left_zhinan_route()
    
    # 檢查數據是否為空
    if not route_shape_data or (isinstance(route_shape_data, list) and len(route_shape_data) == 0):
        current_app.logger.error("獲取貓空左線(指南宮)路線數據為空")
        return jsonify([]), 200
    
    return jsonify(route_shape_data)