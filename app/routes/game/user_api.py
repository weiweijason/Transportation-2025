from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user

from app.models.creature import Creature
from app.services.firebase_service import FirebaseService
from app.routes.game.auth import jwt_or_session_required

# 修改藍圖前綴為 /game/api/user 以符合前端預期
user_bp = Blueprint('game_user', __name__, url_prefix='/game/api/user')

@user_bp.route('/get-current')
@login_required
def get_current_user():
    """獲取當前登入的用戶資訊"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    })

@user_bp.route('/creatures')
@login_required
def get_user_creatures():
    """獲取當前用戶的所有精靈（從Firebase）"""
    try:
        current_app.logger.info(f"獲取用戶 {current_user.id} 的精靈列表")
        firebase_service = FirebaseService()
        
        # 獲取用戶的精靈子集合
        user_ref = firebase_service.firestore_db.collection('users').document(current_user.id)
        user_creatures_ref = user_ref.collection('user_creatures').get()
        
        creatures_list = []
        for creature_doc in user_creatures_ref:
            creature_data = creature_doc.to_dict()
            
            # 從 Firebase 數據中提取數值，確保類型正確
            attack_value = creature_data.get('attack')
            hp_value = creature_data.get('hp')
            power_value = creature_data.get('power')
            
            # 確保 attack 值存在且為數字
            if attack_value is not None:
                attack = float(attack_value)
            elif power_value is not None:
                attack = float(power_value)
            else:
                attack = 100.0
                
            # 確保 hp 值存在且為數字
            if hp_value is not None:
                hp = float(hp_value)
            elif power_value is not None:
                hp = float(power_value) * 10
            else:
                hp = 1000.0
            
            # 統一字段名稱，確保與前端期望的一致
            creature_info = {
                'id': creature_doc.id,
                'name': creature_data.get('name', '未知精靈'),
                'element': creature_data.get('type', creature_data.get('element', 'Normal')),
                'power': int(power_value) if power_value is not None else int(attack),
                'image_url': creature_data.get('image_url', '/static/img/creature.PNG'),
                'level': creature_data.get('level', 1),                'captured_at': creature_data.get('captured_at', ''),
                'original_creature_id': creature_data.get('original_creature_id', ''),
                # 戰鬥數值字段，確保不為 None
                'attack': attack,
                'hp': hp,
                'type': creature_data.get('type', creature_data.get('element', 'Normal')),
                'element_type': str(creature_data.get('element_type') or 
                               creature_data.get('type', 'Normal')).lower()
            }
            creatures_list.append(creature_info)
            current_app.logger.debug(f"添加精靈: {creature_info['name']} (ID: {creature_info['id']})")
        
        current_app.logger.info(f"成功獲取 {len(creatures_list)} 隻精靈")
        return jsonify(creatures_list)
    
    except Exception as e:
        current_app.logger.error(f"獲取用戶精靈失敗: {e}")
        import traceback
        current_app.logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return jsonify({'error': f'獲取精靈資料失敗: {str(e)}'}), 500

@user_bp.route('/backpack')
@login_required
def get_user_backpack():
    """獲取當前用戶的背包內容"""
    try:
        firebase_service = FirebaseService()
        result = firebase_service.get_user_backpack(current_user.id)
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'backpack': result['backpack']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"獲取用戶背包失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'獲取背包資料失敗: {str(e)}'
        }), 500

@user_bp.route('/backpack/update', methods=['POST'])
@login_required
def update_backpack_item():
    """更新背包中物品的數量"""
    try:
        from flask import request
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '缺少請求數據'
            }), 400
        
        item_name = data.get('item_name')
        count_change = data.get('count_change')
        
        if item_name is None or count_change is None:
            return jsonify({
                'success': False,
                'message': '缺少必要參數: item_name 和 count_change'
            }), 400
        
        firebase_service = FirebaseService()
        result = firebase_service.update_backpack_item(
            current_user.id, 
            item_name, 
            count_change
        )
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
    
    except Exception as e:
        current_app.logger.error(f"更新背包物品失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'更新背包物品失敗: {str(e)}'
        }), 500

@user_bp.route('/verify-auth-status', methods=['POST'])
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

@user_bp.route('/creatures/<creature_id>/toggle-favorite', methods=['POST'])
@login_required
def toggle_creature_favorite(creature_id):
    """切換精靈的我的最愛狀態"""
    try:
        current_app.logger.info(f"切換精靈我的最愛狀態 - 用戶: {current_user.id}, 精靈: {creature_id}")
        
        # 驗證 creature_id
        if not creature_id:
            return jsonify({
                'success': False,
                'message': '缺少精靈ID'
            }), 400
        
        # 使用 Firebase 服務切換我的最愛狀態
        firebase_service = FirebaseService()
        result = firebase_service.toggle_creature_favorite(current_user.id, creature_id)
        
        if result['success']:
            current_app.logger.info(f"成功更新精靈 {creature_id} 的我的最愛狀態: {result['favorite']}")
            return jsonify({
                'success': True,
                'favorite': result['favorite'],
                'message': result['message']
            })
        else:
            current_app.logger.error(f"更新精靈我的最愛狀態失敗: {result['message']}")
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"切換精靈我的最愛狀態時發生錯誤: {e}")
        import traceback
        current_app.logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'操作失敗: {str(e)}'
        }), 500