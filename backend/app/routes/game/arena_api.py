from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.arena import FirebaseArena as Arena
from app.services.firebase_service import FirebaseService
import traceback

# 修改藍圖前綴為 /game/api/arena 以符合前端預期
arena_bp = Blueprint('game_arena', __name__, url_prefix='/game/api/arena')

@arena_bp.route('/get-all')
def get_all_arenas():
    """獲取所有擂台資訊"""
    arenas = Arena.get_all()
    return jsonify([arena.to_dict() for arena in arenas])

@arena_bp.route('/get/<arena_id>')
def get_arena(arena_id):
    """獲取特定擂台資訊"""
    arena = Arena.get_by_id(arena_id)
    if not arena:
        return jsonify({'success': False, 'message': '找不到指定擂台'}), 404
    return jsonify(arena.to_dict())

@arena_bp.route('/get-by-name/<arena_name>')
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

@arena_bp.route('/save', methods=['POST'])
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

@arena_bp.route('/challenge', methods=['POST'])
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
    
    # 觸發成就檢查 - 競技場相關成就
    try:
        current_app.logger.info(f"觸發競技場成就檢查，用戶ID: {current_user.id}")
        triggered_achievements = firebase_service.trigger_achievement_check(
            current_user.id,
            'arena_battle',
            {
                'result': result,
                'arena_name': arena_name,
                'creature_power': data.get('creaturePower')
            }
        )
        
        # 如果是勝利，也觸發勝利成就檢查
        if result == 'victory':
            victory_achievements = firebase_service.trigger_achievement_check(
                current_user.id,
                'arena_victory',
                {
                    'arena_name': arena_name,
                    'creature_power': data.get('creaturePower')
                }
            )
            triggered_achievements.extend(victory_achievements)
        
        # 準備回應數據
        response_data = {
            'success': True,
            'result': result,
            'message': message,
            'arena': arena.to_dict()
        }
        
        # 將新獲得的成就添加到回應中
        if triggered_achievements:
            response_data['new_achievements'] = triggered_achievements
            current_app.logger.info(f"用戶獲得新成就: {[ach.get('achievement_name', ach.get('achievement_id')) for ach in triggered_achievements]}")
            
    except Exception as achievement_error:
        current_app.logger.error(f"觸發競技場成就檢查失敗: {achievement_error}")
        # 不影響挑戰結果，僅記錄錯誤
        response_data = {
            'success': True,
            'result': result,
            'message': message,
            'arena': arena.to_dict()
        }
    
    return jsonify(response_data)

@arena_bp.route('/cached-levels')
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
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'獲取道館等級失敗: {str(e)}',
            'arenas': {}
        }), 500

@arena_bp.route('/sync/<arena_id>', methods=['POST'])
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
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'message': f'同步道館資料時發生錯誤: {str(e)}'
        }), 500

@arena_bp.route('/check-exists', methods=['POST'])
def check_arena_exists():
    """檢查道館是否存在"""
    try:
        data = request.json
        arena_name = data.get('name')
        
        if not arena_name:
            return jsonify({'success': False, 'message': '缺少道館名稱'}), 400
        
        firebase_service = FirebaseService()
        
        # 檢查 Firestore 中是否存在
        arenas_ref = firebase_service.firestore_db.collection('arenas')
        query = arenas_ref.where('name', '==', arena_name).limit(1)
        docs = query.get()
        
        if docs:
            arena_data = docs[0].to_dict()
            return jsonify({
                'success': True,
                'exists': True,
                'arena': arena_data
            })
        else:
            return jsonify({
                'success': True,
                'exists': False
            })
            
    except Exception as e:
        current_app.logger.error(f"檢查道館存在時出錯: {e}")
        return jsonify({'success': False, 'message': f'檢查失敗: {str(e)}'}), 500

@arena_bp.route('/save-to-firebase', methods=['POST'])
@login_required
def save_arena_to_firebase():
    """保存道館到 Firebase"""
    try:
        data = request.json
        
        # 驗證必要欄位
        required_fields = ['id', 'name', 'position', 'level']
        if not all(data.get(field) for field in required_fields):
            return jsonify({'success': False, 'message': '缺少必要資訊'}), 400
        
        firebase_service = FirebaseService()
        
        # 檢查是否已存在
        arenas_ref = firebase_service.firestore_db.collection('arenas')
        existing_query = arenas_ref.where('name', '==', data['name']).limit(1)
        existing_docs = existing_query.get()
        
        if existing_docs:
            return jsonify({
                'success': True,
                'message': '道館已存在，無需保存',
                'exists': True
            })
        
        # 準備道館數據
        arena_data = {
            'id': data['id'],
            'name': data['name'],
            'position': data['position'],
            'level': data['level'],
            'routes': data.get('routes', []),
            'routeName': data.get('routeName', ''),
            'stopIds': data.get('stopIds', []),
            'stopName': data.get('stopName', ''),
            'owner': None,
            'ownerPlayerId': None,
            'ownerCreature': None,
            'challengers': [],
            'updatedAt': firebase_service.firestore_db.SERVER_TIMESTAMP,
            'createdAt': firebase_service.firestore_db.SERVER_TIMESTAMP
        }
        
        # 保存到 Firestore
        arena_ref = arenas_ref.document(data['id'])
        arena_ref.set(arena_data)
        
        # 驗證保存結果
        saved_doc = arena_ref.get()
        if saved_doc.exists:
            return jsonify({
                'success': True,
                'message': '道館已成功保存',
                'arena': saved_doc.to_dict()
            })
        else:
            return jsonify({'success': False, 'message': '保存後驗證失敗'}), 500
            
    except Exception as e:
        current_app.logger.error(f"保存道館到Firebase時出錯: {e}")
        return jsonify({'success': False, 'message': f'保存失敗: {str(e)}'}), 500

@arena_bp.route('/check/<arena_name>')
def check_arena_by_name(arena_name):
    """檢查道館是否存在 (GET方式)"""
    try:
        if not arena_name:
            return jsonify({'success': False, 'message': '缺少道館名稱'}), 400
        
        firebase_service = FirebaseService()
        
        # 檢查 Firestore 中是否存在
        arenas_ref = firebase_service.firestore_db.collection('arenas')
        query = arenas_ref.where('name', '==', arena_name).limit(1)
        docs = query.get()
        
        if docs:
            arena_data = docs[0].to_dict()
            return jsonify({
                'success': True,
                'exists': True,
                'arena': arena_data
            })
        else:
            return jsonify({
                'success': True,
                'exists': False
            })
            
    except Exception as e:
        current_app.logger.error(f"檢查道館時出錯: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@arena_bp.route('/update-routes', methods=['POST'])
@login_required
def update_arena_routes():
    """更新道館路線"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': '請求數據為空'}), 400
            
        arena_id = data.get('arenaId')
        route_name = data.get('routeName')
        
        if not arena_id or not route_name:
            return jsonify({'success': False, 'message': '缺少必要參數'}), 400
        
        # 記錄請求信息
        current_app.logger.info(f"用戶 {current_user.username} 嘗試更新道館 {arena_id} 的路線 {route_name}")
        
        # 初始化 Firebase 服務
        try:
            firebase_service = FirebaseService()
        except Exception as e:
            current_app.logger.error(f"Firebase 服務初始化失敗: {e}")
            return jsonify({'success': False, 'message': 'Firebase 服務不可用'}), 500
          # 獲取道館文檔
        try:
            arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
            arena_doc = arena_ref.get()
        except Exception as e:
            current_app.logger.error(f"獲取道館文檔失敗: {e}")
            return jsonify({'success': False, 'message': '無法訪問道館數據'}), 500
        
        if not arena_doc.exists:
            return jsonify({'success': False, 'message': '找不到指定道館'}), 404
        
        arena_data = arena_doc.to_dict()
        
        # 更新路線列表
        routes = arena_data.get('routes', [])
        if route_name not in routes:
            routes.append(route_name)
            
            # 更新等級
            level = len(routes)
            
            # 更新 Firestore
            try:
                arena_ref.update({
                    'routes': routes,
                    'level': level,
                    'updatedAt': firebase_service.get_server_timestamp()
                })
                
                arena_data['routes'] = routes
                arena_data['level'] = level
                
                current_app.logger.info(f"道館 {arena_id} 路線更新成功")
                
                return jsonify({
                    'success': True,
                    'message': '道館路線更新成功',
                    'arena': arena_data
                })
            except Exception as e:
                current_app.logger.error(f"更新 Firestore 文檔失敗: {e}")
                return jsonify({'success': False, 'message': '數據更新失敗'}), 500
        else:
            return jsonify({
                'success': True,
                'message': '路線已存在，無需更新',
                'arena': arena_data
            })
            
    except Exception as e:
        current_app.logger.error(f"更新道館路線時出錯: {e}")
        current_app.logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': '內部服務器錯誤'}), 500