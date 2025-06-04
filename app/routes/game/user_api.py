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
        firebase_service = FirebaseService()
        
        # 獲取用戶的精靈子集合
        user_ref = firebase_service.firestore_db.collection('users').document(current_user.id)
        user_creatures_ref = user_ref.collection('user_creatures').get()
        
        creatures_list = []
        for creature_doc in user_creatures_ref:
            creature_data = creature_doc.to_dict()
            creatures_list.append({
                'id': creature_doc.id,
                'name': creature_data.get('name', '未知精靈'),
                'element': creature_data.get('element', 'Normal'),
                'power': creature_data.get('power', 100),
                'image_url': creature_data.get('image_url', ''),
                'level': creature_data.get('level', 1),
                'captured_at': creature_data.get('captured_at', ''),
                'original_creature_id': creature_data.get('original_creature_id', '')
            })
        
        return jsonify(creatures_list)
    
    except Exception as e:
        current_app.logger.error(f"獲取用戶精靈失敗: {e}")
        return jsonify({'error': f'獲取精靈資料失敗: {str(e)}'}), 500

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