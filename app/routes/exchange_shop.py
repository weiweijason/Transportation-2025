from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
import logging
from firebase_admin import firestore
from app.services.firebase_service import FirebaseService
from app.config.firebase_config import FIREBASE_CONFIG

# 創建兌換商店藍圖
exchange_shop = Blueprint('exchange_shop', __name__, url_prefix='/exchange-shop')

# 設置日誌記錄
logger = logging.getLogger(__name__)

@exchange_shop.route('/')
@login_required
def exchange_shop_page():
    """兌換商店頁面"""
    return render_template('exchange_shop/exchange_shop.html', 
                         firebase_config=FIREBASE_CONFIG)

@exchange_shop.route('/api/get-exchange-data', methods=['GET'])
@login_required
def get_exchange_data():
    """獲取兌換相關數據"""
    try:
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 獲取用戶數據
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'success': False, 'message': '找不到用戶資料'}), 404
        
        user_data = user_doc.to_dict()
        
        exchange_data = {
            'normal_potion_fragments': user_data.get('normal_potion_fragments', 0),
            'normal_potions': user_data.get('normal_potions', 0),
            'magic_circle_normal': user_data.get('magic_circle_normal', 0),
            'magic_circle_advanced': user_data.get('magic_circle_advanced', 0),
            'magic_circle_legendary': user_data.get('magic_circle_legendary', 0)
        }
        
        return jsonify({
            'success': True,
            'exchange_data': exchange_data
        })
        
    except Exception as e:
        logger.error(f"獲取兌換數據失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'獲取數據失敗: {str(e)}'}), 500

@exchange_shop.route('/api/exchange-potion-fragments', methods=['POST'])
@login_required
def exchange_potion_fragments():
    """兌換普通藥水碎片為普通藥水"""
    try:
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 獲取用戶數據
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'success': False, 'message': '找不到用戶資料'}), 404
        
        user_data = user_doc.to_dict()
        current_fragments = user_data.get('normal_potion_fragments', 0)
        
        if current_fragments < 7:
            return jsonify({
                'success': False, 
                'message': f'碎片不足！需要7個碎片，目前只有{current_fragments}個'
            }), 400
        
        # 計算可兌換的藥水數量
        potions_to_exchange = current_fragments // 7
        fragments_after_exchange = current_fragments % 7
        
        current_potions = user_data.get('normal_potions', 0)
        new_potions = current_potions + potions_to_exchange
        
        # 更新Firebase
        user_ref.update({
            'normal_potion_fragments': fragments_after_exchange,
            'normal_potions': new_potions
        })
        
        return jsonify({
            'success': True,
            'message': f'成功兌換{potions_to_exchange}瓶普通藥水！',
            'exchanged_potions': potions_to_exchange,
            'remaining_fragments': fragments_after_exchange,
            'total_potions': new_potions
        })
        
    except Exception as e:
        logger.error(f"兌換藥水碎片失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'兌換失敗: {str(e)}'}), 500

@exchange_shop.route('/api/exchange-magic-circles', methods=['POST'])
@login_required
def exchange_magic_circles():
    """兌換魔法陣"""
    try:
        data = request.get_json()
        exchange_type = data.get('exchange_type')  # 'normal_to_advanced' 或 'advanced_to_legendary'
        
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 獲取用戶數據
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'success': False, 'message': '找不到用戶資料'}), 404
        
        user_data = user_doc.to_dict()
        
        if exchange_type == 'normal_to_advanced':
            # 10個普通魔法陣兌換1個進階魔法陣
            current_normal = user_data.get('magic_circle_normal', 0)
            
            if current_normal < 10:
                return jsonify({
                    'success': False, 
                    'message': f'普通魔法陣不足！需要10個，目前只有{current_normal}個'
                }), 400
            
            advanced_to_add = current_normal // 10
            normal_remaining = current_normal % 10
            current_advanced = user_data.get('magic_circle_advanced', 0)
            
            user_ref.update({
                'magic_circle_normal': normal_remaining,
                'magic_circle_advanced': current_advanced + advanced_to_add
            })
            
            return jsonify({
                'success': True,
                'message': f'成功兌換{advanced_to_add}個進階魔法陣！',
                'exchanged_amount': advanced_to_add,
                'remaining_normal': normal_remaining,
                'total_advanced': current_advanced + advanced_to_add
            })
            
        elif exchange_type == 'advanced_to_legendary':
            # 10個進階魔法陣兌換1個高級魔法陣
            current_advanced = user_data.get('magic_circle_advanced', 0)
            
            if current_advanced < 10:
                return jsonify({
                    'success': False, 
                    'message': f'進階魔法陣不足！需要10個，目前只有{current_advanced}個'
                }), 400
            
            legendary_to_add = current_advanced // 10
            advanced_remaining = current_advanced % 10
            current_legendary = user_data.get('magic_circle_legendary', 0)
            
            user_ref.update({
                'magic_circle_advanced': advanced_remaining,
                'magic_circle_legendary': current_legendary + legendary_to_add
            })
            
            return jsonify({
                'success': True,
                'message': f'成功兌換{legendary_to_add}個高級魔法陣！',
                'exchanged_amount': legendary_to_add,
                'remaining_advanced': advanced_remaining,
                'total_legendary': current_legendary + legendary_to_add
            })
        else:
            return jsonify({'success': False, 'message': '無效的兌換類型'}), 400
            
    except Exception as e:
        logger.error(f"兌換魔法陣失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'兌換失敗: {str(e)}'}), 500
