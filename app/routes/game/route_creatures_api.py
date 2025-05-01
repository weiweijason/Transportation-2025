from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
import random
import traceback

from app.models.creature import ElementType
from app.models.bus import BusRoute
from app.services.firebase_service import FirebaseService
from app.routes.game.auth import jwt_or_session_required

# 修改藍圖前綴為 /game/api 以符合前端預期
route_creatures_bp = Blueprint('game_route_creatures', __name__, url_prefix='/game/api')

@route_creatures_bp.route('/route-creatures/generate', methods=['POST'])
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

@route_creatures_bp.route('/route-creatures/get/<route_id>')
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

@route_creatures_bp.route('/route-creatures/catch', methods=['POST'])
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

@route_creatures_bp.route('/route-creatures/get-all')
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

@route_creatures_bp.route('/route-creatures/get-from-csv', methods=['GET'])
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
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'無法獲取精靈資料: {str(e)}',
            'creatures': []
        }), 500

@route_creatures_bp.route('/route-creatures', methods=['GET'])
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