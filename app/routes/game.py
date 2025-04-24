from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import random
import json

from app.models.user import User
from app.models.creature import Creature, ElementType
from app.models.bus import BusRoute
from app.models.arena import FirebaseArena as Arena
from app.services.firebase_service import FirebaseService
from app.services.tdx_service import (get_cat_right_route, get_cat_left_route, 
                                     get_cat_left_zhinan_route, get_cat_right_stops,
                                     get_cat_left_stops, get_cat_left_zhinan_stops,
                                     get_tdx_token, TDX_API_URL)

# 認證裝飾器 - 同時支援 JWT 和 Session
def jwt_or_session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 檢查是否有 JWT 令牌
        auth_header = request.headers.get('Authorization')
        if (auth_header and auth_header.startswith('Bearer ')):
            token = auth_header.split(' ')[1]
            try:
                firebase_service = FirebaseService()
                decoded_token = firebase_service.verify_id_token(token)
                if decoded_token:
                    # 令牌有效，可以繼續
                    return f(*args, **kwargs)
            except Exception as e:
                print(f"JWT 驗證失敗: {e}")
                # 如果 JWT 驗證失敗，繼續檢查 session
        
        # 檢查是否有 session
        if 'user' in session:
            return f(*args, **kwargs)
        
        # 如果兩種認證都失敗，返回 401 未授權
        return jsonify({
            'success': False,
            'message': '請先登入'
        }), 401
    
    return decorated_function

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

@game_bp.route('/api/arena/get-by-name/<arena_name>')
def get_arena_by_name(arena_name):
    """根據名稱獲取擂台資訊（優先從Firestore獲取）"""
    # 嘗試從Firestore獲取
    arena = Arena.get_by_name_firestore(arena_name)
    
    # 如果Firestore中沒有，嘗試從Realtime Database獲取
    if not arena:
        arena = Arena.get_by_name(arena_name)
        
    if not arena:
        return jsonify({'success': False, 'message': '找不到指定擂台'}), 404
    
    # 獲取擂台數據
    arena_data = arena.to_dict()
    
    # 如果有擁有者ID，嘗試獲取擁有者用戶名
    if arena_data.get('ownerPlayerId'):
        try:
            from app.services.firebase_service import FirebaseService
            firebase_service = FirebaseService()
            
            # 查詢所有用戶，找到對應playerID的用戶
            users_ref = firebase_service.firestore_db.collection('users').where('player_id', '==', arena_data['ownerPlayerId']).limit(1).get()
            
            if users_ref and len(users_ref) > 0:
                user_data = users_ref[0].to_dict()
                # 將用戶名添加到返回數據中
                arena_data['ownerUsername'] = user_data.get('username', '未知玩家')
        except Exception as e:
            current_app.logger.error(f"獲取擁有者資訊失敗: {e}")
    
    return jsonify({
        'success': True,
        'arena': arena_data
    })

@game_bp.route('/api/arena/save', methods=['POST'])
@login_required
def save_arena():
    """儲存擂台狀態"""
    data = request.json
    
    # 檢查數據完整性
    if not all([data.get('id'), data.get('name'), data.get('position')]):
        return jsonify({'success': False, 'message': '缺少必要資訊'}), 400
    
    # 先查找是否已有相同名稱的擂台 (優先從 Firestore 查詢)
    existing_arena = Arena.get_by_name_firestore(data.get('name'))
    
    # 如果 Firestore 中沒有，再嘗試從 Realtime Database 中查詢
    if not existing_arena:
        existing_arena = Arena.get_by_name(data.get('name'))
    
    if existing_arena:
        # 更新現有擂台
        existing_arena.position = data.get('position')
        existing_arena.stop_ids = data.get('stopIds', [])
        existing_arena.routes = data.get('routes', [])
        existing_arena.owner = data.get('owner')
        existing_arena.owner_player_id = data.get('ownerPlayerId')
        existing_arena.owner_creature = data.get('ownerCreature')
        
        # 保存更新 (同時儲存到 Firestore 和 Realtime Database)
        existing_arena.save_to_firestore()
        
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
            owner_player_id=data.get('ownerPlayerId'),
            owner_creature=data.get('ownerCreature')
        )
        
        # 保存新擂台 (同時儲存到 Firestore 和 Realtime Database)
        new_arena.save_to_firestore()
        
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
    
    # 獲取擂台 (優先從 Firestore 獲取)
    arena_name = data.get('arenaName')
    if arena_name:
        arena = Arena.get_by_name_firestore(arena_name)
    else:
        arena = Arena.get_by_id(data.get('arenaId'))
        
    if not arena:
        return jsonify({'success': False, 'message': '找不到指定擂台'}), 404
    
    # 獲取當前用戶的 player_id
    from app.services.firebase_service import FirebaseService
    firebase_service = FirebaseService()
    user_data = firebase_service.get_user_info(current_user.id)
    player_id = user_data.get('player_id') if user_data else None
    
    # 如果用戶沒有 player_id，生成一個隨機 ID
    if not player_id:
        import random
        import string
        player_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # 更新用戶資料
        if user_data:
            user_data['player_id'] = player_id
            firebase_service.update_user_info(current_user.id, {'player_id': player_id})
    
    # 進行挑戰 (使用支援 player_id 的新方法)
    result, message = arena.challenge_with_player_id(
        challenger_id=data.get('creatureId'),
        challenger_name=data.get('creatureName'),
        challenger_power=data.get('creaturePower'),
        challenger_username=current_user.username,
        challenger_player_id=player_id
    )
    
    return jsonify({
        'success': True,
        'result': result,
        'message': message,
        'arena': arena.to_dict()
    })

# ----- 新增: 路線精靈相關API ----- #

@game_bp.route('/api/route-creatures/generate', methods=['POST'])
@login_required
def generate_route_creatures():
    """生成路線上的精靈
    
    需要提供路線ID和元素類型
    """
    data = request.json
    route_id = data.get('routeId')
    route_name = data.get('routeName')
    element_type = data.get('elementType')
    count = data.get('count', 3)  # 預設生成3隻精靈
    
    if not all([route_id, route_name, element_type]):
        return jsonify({
            'success': False,
            'message': '缺少必要資訊'
        }), 400
    
    # 檢查元素類型是否有效
    try:
        element_enum = ElementType[element_type.upper()]
    except (KeyError, AttributeError):
        return jsonify({
            'success': False,
            'message': '無效的元素類型'
        }), 400
    
    # 使用Firebase服務生成精靈
    firebase_service = FirebaseService()
    creatures = firebase_service.generate_route_creatures(
        route_id=route_id,
        route_name=route_name,
        element_type=element_type,
        count=count
    )
    
    if not creatures:
        return jsonify({
            'success': False,
            'message': '生成精靈失敗'
        }), 500
    
    return jsonify({
        'success': True,
        'message': f'已在路線 {route_name} 上生成 {len(creatures)} 隻精靈',
        'creatures': creatures
    })

@game_bp.route('/api/route-creatures/get/<route_id>')
@login_required
def get_route_creatures(route_id):
    """獲取路線上的精靈"""
    if not route_id:
        return jsonify({
            'success': False,
            'message': '缺少路線ID'
        }), 400
    
    # 獲取路線資訊
    route = BusRoute.query.filter_by(id=route_id).first()
    if not route:
        return jsonify({
            'success': False,
            'message': '找不到指定路線'
        }), 404
    
    # 使用Firebase服務獲取精靈
    firebase_service = FirebaseService()
    creatures = firebase_service.get_route_creatures(route_id)
    
    # 如果路線上沒有精靈，自動生成一些
    if not creatures:
        creatures = firebase_service.generate_route_creatures(
            route_id=route_id,
            route_name=route.name,
            element_type=route.element_type,
            count=random.randint(1, 3)  # 隨機生成1-3隻精靈
        )
        message = '路線上沒有精靈，已自動生成新精靊'
    else:
        message = f'找到 {len(creatures)} 隻路線精靈'
    
    return jsonify({
        'success': True,
        'message': message,
        'route': {
            'id': route.id,
            'name': route.name,
            'element_type': route.element_type
        },
        'creatures': creatures
    })

@game_bp.route('/api/route-creatures/catch', methods=['POST'])
@login_required
def catch_route_creature():
    """捕捉路線上的精靈"""
    data = request.json
    creature_id = data.get('creatureId')
    
    if not creature_id:
        return jsonify({
            'success': False,
            'message': '缺少精靈ID'
        }), 400
    
    # 使用Firebase服務捕捉精靈
    firebase_service = FirebaseService()
    result = firebase_service.catch_route_creature(
        creature_id=creature_id,
        user_id=current_user.id
    )
    
    return jsonify(result)

@game_bp.route('/api/route-creatures/get-all')
@login_required
def get_all_route_creatures():
    """獲取所有路線上的精靈
    
    此API提供給前端用於顯示地圖上所有路線的精靈
    """
    # 使用Firebase服務獲取所有精靈
    firebase_service = FirebaseService()
    creatures = firebase_service.get_route_creatures()
    
    # 移除所有已過期的精靊（這個操作也會在定時任務中執行，這裡作為額外保障）
    firebase_service.remove_expired_creatures()
    
    return jsonify({
        'success': True,
        'message': f'找到 {len(creatures)} 隻路線精靈',
        'creatures': creatures
    })

@game_bp.route('/api/route-creatures/get-from-csv', methods=['GET'])
@jwt_or_session_required
def get_route_creatures_from_csv():
    """從CSV檔案獲取快取的精靈資料

    Returns:
        JSON: 所有可捕捉的精靈資料
    """
    try:
        firebase_service = FirebaseService()
        creatures = firebase_service.get_creatures_from_csv()
        
        if not creatures:
            return jsonify({
                'success': False,
                'message': '目前沒有精靈資料。請稍後再試。',
                'creatures': []
            })
        
        return jsonify({
            'success': True,
            'message': f'成功從CSV檔案讀取 {len(creatures)} 隻精靈',
            'creatures': creatures
        })
    except Exception as e:
        print(f"獲取CSV精靈資料時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'無法獲取精靈資料: {str(e)}',
            'creatures': []
        }), 500

# 新增: 從巴士路線捕捉頁面
@game_bp.route('/catch-on-route/<route_id>')
@login_required
def catch_on_route(route_id):
    """在特定公車路線上捕捉精靈的頁面"""
    # 獲取路線資訊
    route = BusRoute.query.filter_by(id=route_id).first()
    if not route:
        flash('找不到指定路線', 'error')
        return redirect(url_for('game.catch'))
    
    return render_template(
        'game/catch.html',
        route=route,
        active_route_id=route_id
    )

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