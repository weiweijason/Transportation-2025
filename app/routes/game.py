from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user
from datetime import datetime
import random
import json

from app.models.user import User
from app.models.creature import Creature
from app.models.arena import FirebaseArena as Arena
from app.services.tdx_service import (get_cat_right_route, get_cat_left_route, 
                                     get_cat_left_zhinan_route, get_cat_right_stops,
                                     get_cat_left_stops, get_cat_left_zhinan_stops,
                                     get_tdx_token, TDX_API_URL)

# 創建藍圖 blueprint
game_bp = Blueprint('game', __name__, url_prefix='/game')

# 遊戲主頁面
@game_bp.route('/')
@login_required
def game_home():
    return render_template('game/catch.html')

# 捕捉精靈頁面
@game_bp.route('/catch')
@login_required
def catch():
    return render_template('game/catch.html')

# 擂台對戰頁面
@game_bp.route('/battle')
@login_required
def battle():
    return render_template('game/battle.html')

# 新增：擂台列表頁面
@game_bp.route('/arenas')
@login_required
def list_arenas():
    """顯示所有擂台列表"""
    # 獲取所有擂台
    arenas = Arena.get_all()
    return render_template('game/arenas.html', arenas=arenas)

# 精靈捕捉 API
@game_bp.route('/api/catch-creature', methods=['POST'])
@login_required
def catch_creature():
    data = request.json
    creature_id = data.get('creatureId')
    creature_name = data.get('creatureName')
    creature_type = data.get('creatureType')
    creature_rarity = data.get('creatureRarity')
    creature_power = data.get('creaturePower')
    creature_img = data.get('creatureImg')
    
    if not all([creature_id, creature_name, creature_type, creature_rarity, creature_power]):
        return jsonify({'success': False, 'message': '缺少必要資訊'}), 400
        
    # 創建新精靈
    new_creature = Creature(
        name=creature_name,
        type=creature_type,
        rarity=creature_rarity,
        power=creature_power,
        image_url=creature_img,
        level=1,
        experience=0,
        user_id=current_user.id
    )
    
    # 儲存到資料庫
    new_creature.save()
    
    # 回傳成功資訊
    return jsonify({
        'success': True,
        'message': f'成功捕捉到 {creature_name}!',
        'creature': {
            'id': new_creature.id,
            'name': new_creature.name,
            'type': new_creature.type,
            'rarity': new_creature.rarity,
            'power': new_creature.power,
            'imageUrl': new_creature.image_url,
            'level': new_creature.level,
            'experience': new_creature.experience
        }
    })

# 公車路線 API
@game_bp.route('/api/bus/cat-right-route')
def get_cat_right_route_api():
    route_data = get_cat_right_route()
    return jsonify(route_data)

@game_bp.route('/api/bus/cat-left-route')
def get_cat_left_route_api():
    route_data = get_cat_left_route()
    return jsonify(route_data)

@game_bp.route('/api/bus/cat-left-zhinan-route')
def get_cat_left_zhinan_route_api():
    route_data = get_cat_left_zhinan_route()
    return jsonify(route_data)

# 公車站牌 API
@game_bp.route('/api/bus/cat-right-stops')
def get_cat_right_stops_api():
    stops_data = get_cat_right_stops()
    return jsonify(stops_data)

@game_bp.route('/api/bus/cat-left-stops')
def get_cat_left_stops_api():
    stops_data = get_cat_left_stops()
    return jsonify(stops_data)

@game_bp.route('/api/bus/cat-left-zhinan-stops')
def get_cat_left_zhinan_stops_api():
    stops_data = get_cat_left_zhinan_stops()
    return jsonify(stops_data)

# V3 Network API 路由 - 直接使用站點資料
@game_bp.route('/api/bus/network/cat-right')
def get_cat_right_network_api():
    """獲取貓空右線的V3 Network API數據"""
    # 使用現有的站點資料替代
    stops_data = get_cat_right_stops()
    return jsonify(stops_data)

@game_bp.route('/api/bus/network/cat-left')
def get_cat_left_network_api():
    """獲取貓空左線(動物園)的V3 Network API數據"""
    # 使用現有的站點資料替代
    stops_data = get_cat_left_stops()
    return jsonify(stops_data)

@game_bp.route('/api/bus/network/cat-left-zhinan')
def get_cat_left_zhinan_network_api():
    """獲取貓空左線(指南宮)的V3 Network API數據"""
    # 使用現有的站點資料替代
    stops_data = get_cat_left_zhinan_stops()
    return jsonify(stops_data)

# 新增: 直接從TDX API獲取公車站點網路資料
@game_bp.route('/api/bus/network/stations')
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

# 擂台相關 API
@game_bp.route('/api/arena/get-all')
def get_all_arenas():
    """獲取所有擂台資訊"""
    arenas = Arena.get_all()
    return jsonify([arena.to_dict() for arena in arenas])

@game_bp.route('/api/arena/get/<arena_id>')
def get_arena(arena_id):
    """獲取特定擂台資訊"""
    arena = Arena.get_by_id(arena_id)
    if not arena:
        return jsonify({'success': False, 'message': '找不到指定擂台'}), 404
    return jsonify(arena.to_dict())

@game_bp.route('/api/arena/save', methods=['POST'])
@login_required
def save_arena():
    """儲存擂台狀態"""
    data = request.json
    
    # 檢查數據完整性
    if not all([data.get('id'), data.get('name'), data.get('position')]):
        return jsonify({'success': False, 'message': '缺少必要資訊'}), 400
    
    # 先查找是否已有相同名稱的擂台
    existing_arena = Arena.get_by_name(data.get('name'))
    
    if existing_arena:
        # 更新現有擂台
        existing_arena.position = data.get('position')
        existing_arena.stop_ids = data.get('stopIds', [])
        existing_arena.routes = data.get('routes', [])
        existing_arena.owner = data.get('owner')
        existing_arena.owner_creature = data.get('ownerCreature')
        
        # 保存更新
        existing_arena.save()
        
        return jsonify({
            'success': True, 
            'message': '擂台資訊已更新',
            'arena': existing_arena.to_dict()
        })
    else:
        # 創建新擂台
        new_arena = Arena(
            id=data.get('id'),
            name=data.get('name'),
            position=data.get('position'),
            stop_ids=data.get('stopIds', []),
            routes=data.get('routes', []),
            owner=data.get('owner'),
            owner_creature=data.get('ownerCreature')
        )
        
        # 保存新擂台
        new_arena.save()
        
        return jsonify({
            'success': True, 
            'message': '新擂台已建立',
            'arena': new_arena.to_dict()
        })

@game_bp.route('/api/arena/challenge', methods=['POST'])
@login_required
def challenge_arena():
    """挑戰擂台"""
    data = request.json
    
    # 檢查數據完整性
    if not all([data.get('arenaId'), data.get('creatureId'), data.get('creatureName'), data.get('creaturePower')]):
        return jsonify({'success': False, 'message': '缺少必要資訊'}), 400
    
    # 獲取擂台
    arena = Arena.get_by_id(data.get('arenaId'))
    if not arena:
        return jsonify({'success': False, 'message': '找不到指定擂台'}), 404
    
    # 進行挑戰
    result, message = arena.challenge(
        challenger_id=data.get('creatureId'),
        challenger_name=data.get('creatureName'),
        challenger_power=data.get('creaturePower'),
        challenger_username=current_user.username
    )
    
    return jsonify({
        'success': True,
        'result': result,
        'message': message,
        'arena': arena.to_dict()
    })

# 用戶相關 API
@game_bp.route('/api/user/get-current')
@login_required
def get_current_user():
    """獲取當前登入的用戶資訊"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    })

@game_bp.route('/api/user/creatures')
@login_required
def get_user_creatures():
    """獲取當前用戶的所有精靈"""
    creatures = Creature.get_by_user(current_user.id)
    return jsonify([creature.to_dict() for creature in creatures])