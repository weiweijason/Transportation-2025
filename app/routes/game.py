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
    # 使用Firebase服務獲取所有精靊
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
    """從CSV檔案獲取快取的精靈資料，並過濾掉用戶已捕獲的精靈

    Returns:
        JSON: 所有可捕捉的精靈資料（排除用戶已捕獲的）
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
        
        # 獲取當前用戶的player_id
        player_id = None
        if current_user.is_authenticated:
            # 獲取用戶數據
            user_data = firebase_service.get_user_info(current_user.id)
            if user_data and 'player_id' in user_data:
                player_id = user_data.get('player_id')
                current_app.logger.info(f"用戶 {current_user.id} 的 player_id: {player_id}")
        
        # 如果用戶已登入且有player_id，過濾出用戶尚未捕獲的精靈
        if player_id:
            # 獲取用戶已捕獲的精靈，查詢其original_creature_id
            captured_creatures_ids = []
            try:
                # 從用戶的user_creatures子集合獲取所有已捕獲的精靈
                user_ref = firebase_service.firestore_db.collection('users').document(current_user.id)
                user_creatures_ref = user_ref.collection('user_creatures').get()
                
                # 提取所有original_creature_id
                for doc in user_creatures_ref:
                    creature_data = doc.to_dict()
                    if 'original_creature_id' in creature_data:
                        captured_creatures_ids.append(creature_data['original_creature_id'])
                        
                current_app.logger.info(f"用戶 {current_user.id} 已捕獲 {len(captured_creatures_ids)} 隻精靈")
            except Exception as e:
                current_app.logger.error(f"獲取用戶已捕獲精靈時發生錯誤: {e}")
                import traceback
                current_app.logger.error(f"錯誤詳情: {traceback.format_exc()}")
            
            # 過濾掉用戶已捕獲的精靈
            if captured_creatures_ids:
                filtered_creatures = [c for c in creatures if c['id'] not in captured_creatures_ids]
                creatures = filtered_creatures
                current_app.logger.info(f"過濾後剩餘 {len(creatures)} 隻精靈可供捕獲")
        
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

# 新增：互動捕捉頁面
@game_bp.route('/capture-interactive/<creature_id>')
@login_required
def capture_interactive(creature_id):
    """精靈互動捕捉頁面"""
    # 獲取精靈資訊
    firebase_service = FirebaseService()
    
    # 從 Firebase 獲取精靈
    creature_ref = firebase_service.firestore_db.collection('route_creatures').document(creature_id)
    creature_doc = creature_ref.get()
    
    if not creature_doc.exists:
        flash('找不到指定精靈', 'error')
        return redirect(url_for('game.catch'))
    
    creature = creature_doc.to_dict()
    
    # 檢查該玩家是否已經捕捉過這隻精靈
    current_player_id = None
    if current_user.is_authenticated:
        # 獲取用戶數據
        user_data = firebase_service.get_user_info(current_user.id)
        if user_data and 'player_id' in user_data:
            current_player_id = user_data['player_id']
    
    # 檢查是否已被捕捉 (使用子集合)
    if current_player_id:
        try:
            # 檢查 captured_players 子集合中是否已包含此玩家
            player_capture_ref = creature_ref.collection('captured_players').document(current_player_id)
            player_capture_doc = player_capture_ref.get()
            
            if player_capture_doc.exists:
                flash('你已經捕捉過這隻精靈了', 'warning')
                return redirect(url_for('game.catch'))
        except Exception as e:
            current_app.logger.error(f"檢查玩家捕捉狀態失敗: {e}")
            # 若檢查失敗，繼續讓用戶嘗試捕捉
    
    # 元素類型對應中文名稱
    element_types = {
        'fire': '火系',
        'water': '水系',
        'earth': '土系',
        'air': '風系',
        'electric': '電系',
        'normal': '一般系',
        0: '火系',
        1: '水系',
        2: '土系',
        3: '風系',
        4: '電系',
        5: '一般系'
    }
    
    return render_template(
        'game/capture_interactive.html',
        creature=creature,
        element_types=element_types
    )

# 新增：互動捕捉 API
@game_bp.route('/api/capture-interactive', methods=['POST'])
@login_required
def capture_interactive_api():
    """精靈互動捕捉 API"""
    try:
        # 記錄請求開始
        current_app.logger.info(f"接收到捕捉請求，用戶ID: {current_user.id}")
        
        data = request.json
        creature_id = data.get('creatureId')
        
        # 記錄請求參數
        current_app.logger.info(f"捕捉請求參數: 精靈ID={creature_id}")
        
        if not creature_id:
            return jsonify({
                'success': False,
                'message': '缺少精靈ID'
            }), 400
        
        # 獲取 Firebase 服務
        firebase_service = FirebaseService()
        
        # 檢查精靈是否存在
        try:
            creature_ref = firebase_service.firestore_db.collection('route_creatures').document(creature_id)
            creature_doc = creature_ref.get()
            
            if not creature_doc.exists:
                return jsonify({
                    'success': False,
                    'message': '找不到指定精靈，可能已被移除或過期'
                }), 404
                
            current_app.logger.info(f"找到精靈: {creature_id}")
        except Exception as creature_error:
            current_app.logger.error(f"檢查精靈時發生錯誤: {creature_error}")
            return jsonify({
                'success': False,
                'message': f'檢查精靈時發生錯誤: {str(creature_error)}'
            }), 500
        
        # 檢查用戶 player_id
        try:
            user_data = firebase_service.get_user_info(current_user.id)
            
            player_id = None
            if user_data and 'player_id' in user_data:
                player_id = user_data.get('player_id')
                current_app.logger.info(f"用戶 {current_user.id} 的 player_id: {player_id}")
            
            # 如果用戶沒有 player_id，生成一個並更新用戶資料
            if not player_id:
                import string
                import random
                player_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                
                # 更新用戶資料
                update_result = firebase_service.update_user_info(current_user.id, {'player_id': player_id})
                current_app.logger.info(f"已為用戶 {current_user.id} 生成新的 player_id: {player_id}, 更新結果: {update_result}")
            
            # 使用子集合檢查是否已經捕捉過該精靈
            try:
                # 檢查 captured_players 子集合中是否已包含此玩家
                player_capture_ref = creature_ref.collection('captured_players').document(player_id)
                player_capture_doc = player_capture_ref.get()
                
                if player_capture_doc.exists:
                    current_app.logger.info(f"用戶 {player_id} 已經捕捉過精靈 {creature_id}")
                    return jsonify({
                        'success': False,
                        'message': '你已經捕捉過這隻精靈了'
                    }), 409  # 衝突狀態碼
            except Exception as check_error:
                current_app.logger.error(f"檢查玩家捕捉狀態失敗: {check_error}")
                import traceback
                current_app.logger.error(f"檢查玩家捕捉狀態失敗詳情: {traceback.format_exc()}")
                # 即使檢查失敗，也讓捕捉繼續進行，假設用戶尚未捕捉
                current_app.logger.info(f"忽略檢查錯誤，繼續捕捉流程")
                
        except Exception as user_error:
            current_app.logger.error(f"檢查用戶時發生錯誤: {user_error}")
            return jsonify({
                'success': False,
                'message': f'檢查用戶資料時發生錯誤: {str(user_error)}'
            }), 500
        
        # 使用 Firebase 服務捕捉精靈
        try:
            current_app.logger.info(f"開始捕捉精靈，精靈ID: {creature_id}, 用戶ID: {current_user.id}")
            result = firebase_service.catch_route_creature(
                creature_id=creature_id,
                user_id=current_user.id
            )
            
            current_app.logger.info(f"捕捉結果: {result}")
            
            # 處理結果中的 Sentinel 對象 (Firebase 伺服器時間戳記)
            # 如果結果中包含精靈資料且有 captured_at 字段是 Sentinel 對象
            if result.get('success') and 'creature' in result:
                creature_data = result['creature']
                if 'captured_at' in creature_data:
                    # 檢查是否為 Sentinel 對象 (無法 JSON 序列化)
                    if hasattr(creature_data['captured_at'], '__class__') and 'Sentinel' in creature_data['captured_at'].__class__.__name__:
                        # 將 Sentinel 替換為當前時間的字符串表示
                        from datetime import datetime
                        creature_data['captured_at'] = datetime.now().isoformat()
            
            return jsonify(result)
        except Exception as catch_error:
            current_app.logger.error(f"捕捉精靈時發生錯誤: {catch_error}")
            # 詳細記錄異常
            import traceback
            error_details = traceback.format_exc()
            current_app.logger.error(f"捕捉精靈詳細錯誤: \n{error_details}")
            
            return jsonify({
                'success': False,
                'message': f'捕捉精靈時發生錯誤: {str(catch_error)}'
            }), 500
            
    except Exception as e:
        # 詳細記錄異常
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"捕捉精靈時發生異常: {str(e)}\n{error_details}")
        
        # 返回用戶友好的錯誤訊息
        return jsonify({
            'success': False,
            'message': f'捕捉精靈時發生錯誤: {str(e)}'
        }), 500

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

@game_bp.route('/api/arena/cached-levels')
def get_cached_arena_levels():
    """獲取緩存的道館等級資料"""
    from app.models.arena import get_all_arenas_from_cache
    
    try:
        # 從緩存獲取所有道館資料
        arenas = get_all_arenas_from_cache()
        
        # 將數據格式化為適合前端使用的格式
        formatted_arenas = {}
        
        # 依照道館名稱進行分類，確保同名道館只出現一次
        arena_by_name = {}
        for arena in arenas:
            arena_name = arena.get('name')
            
            # 直接使用原始名稱，不進行任何映射
            if arena_name in arena_by_name:
                # 如果同名道館已存在，則保留等級較高的那個
                if arena.get('level', 1) > arena_by_name[arena_name].get('level', 1):
                    arena_by_name[arena_name] = arena
                    print(f"[道館API] 更新道館 {arena_name} 等級為 {arena.get('level', 1)}")
            else:
                arena_by_name[arena_name] = arena
                print(f"[道館API] 添加道館 {arena_name} 等級為 {arena.get('level', 1)}")
        
        # 將分類後的道館資料轉換為前端所需格式
        for arena_name, arena in arena_by_name.items():
            formatted_arenas[arena.get('id')] = {
                'id': arena.get('id'),
                'name': arena.get('name'),
                'level': arena.get('level', 1),
                'routes': arena.get('routes', []),
                'position': arena.get('position'),
                'updatedAt': arena.get('updatedAt')
            }
        
        print(f"[道館API] 從緩存讀取了 {len(arenas)} 個道館，合併後剩餘 {len(formatted_arenas)} 個道館")
        
        return jsonify({
            'success': True,
            'message': f'成功獲取 {len(formatted_arenas)} 個道館等級資料',
            'arenas': formatted_arenas
        })
    except Exception as e:
        current_app.logger.error(f"獲取緩存道館等級時出錯: {e}")
        print(f"[道館API錯誤] 獲取緩存道館等級時出錯: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'獲取道館等級失敗: {str(e)}',
            'arenas': {}
        }), 500

@game_bp.route('/api/arena/sync/<arena_id>', methods=['POST'])
@login_required
def sync_arena_to_firebase(arena_id):
    """將道館資料同步到 Firebase 的 API"""
    try:
        # 從本地緩存獲取道館資料
        from app.models.arena import get_arena_from_cache
        arena_data = get_arena_from_cache(arena_id=arena_id)
        
        if not arena_data:
            return jsonify({
                'success': False,
                'message': f'無法找到 ID 為 {arena_id} 的道館資料'
            }), 404
        
        # 獲取 Firebase 服務
        firebase_service = FirebaseService()
        
        # 檢查道館是否已存在於 Firebase
        arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
        arena_doc = arena_ref.get()
        
        if (arena_doc.exists):
            # 道館已存在，更新資料
            arena_ref.update(arena_data)
            message = f'已更新道館資料: {arena_data.get("name", arena_id)}'
        else:
            # 道館不存在，新增資料
            arena_ref.set(arena_data)
            message = f'已新增道館資料: {arena_data.get("name", arena_id)}'
        
        return jsonify({
            'success': True,
            'message': message,
            'arena': arena_data
        })
    except Exception as e:
        # 記錄錯誤
        current_app.logger.error(f'同步道館資料失敗: {str(e)}')
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'message': f'同步道館資料時發生錯誤: {str(e)}'
        }), 500

@game_bp.route('/api/route-creatures', methods=['GET'])
def get_all_route_creatures_by_player():
    """獲取路線上的精靈 API，會根據玩家ID過濾
    
    這個API會傳回當前玩家尚未捕獲的精靈
    """
    try:
        route_id = request.args.get('route_id')
        
        # 獲取當前用戶的 player_id
        player_id = None
        if current_user.is_authenticated:
            player_id = current_user.player_id
        
        # 初始化 Firebase 服務
        firebase_service = FirebaseService()
        
        # 從 Firebase 獲取精靈數據，並根據玩家 ID 過濾
        creatures = firebase_service.get_route_creatures(route_id=route_id, player_id=player_id)
        
        return jsonify({
            'success': True,
            'message': f'找到 {len(creatures)} 隻精靈',
            'creatures': creatures
        })
    except Exception as e:
        current_app.logger.error(f"獲取精靈失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'獲取精靈失敗: {str(e)}',
            'creatures': []
        })

@game_bp.route('/api/user/verify-auth-status', methods=['POST'])
@jwt_or_session_required
def verify_auth_status():
    """驗證用戶登入狀態，供前端 JS 使用
    
    此 API 僅需返回用戶 ID 和基本資訊即可,
    用於確認用戶是否已登入並獲取基本用戶資料
    """
    try:
        # 如果用戶已登入，jwt_or_session_required 裝飾器會確保 current_user 可用
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': '用戶未登入'
            }), 401
        
        # 獲取 Firebase 用戶資料
        firebase_service = FirebaseService()
        user_data = firebase_service.get_user_info(current_user.id)
        
        # 返回用戶基本資訊
        return jsonify({
            'success': True,
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'player_id': user_data.get('player_id') if user_data else None
        })
    except Exception as e:
        current_app.logger.error(f"驗證用戶狀態失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'驗證用戶狀態失敗: {str(e)}'
        }), 500