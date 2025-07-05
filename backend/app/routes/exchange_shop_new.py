from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.services.firebase_service import FirebaseService
from app.config.firebase_config import FIREBASE_CONFIG
import logging

# 設置日誌
logger = logging.getLogger(__name__)

# 創建兌換商店藍圖
exchange_shop = Blueprint('exchange_shop', __name__, url_prefix='/exchange-shop')

@exchange_shop.route('/')
@login_required
def exchange_shop_page():
    """兌換商店主頁"""
    return render_template('exchange_shop/exchange_shop.html',
                         firebase_config=FIREBASE_CONFIG)

@exchange_shop.route('/api/get-exchange-data', methods=['GET'])
@login_required
def get_exchange_data():
    """獲取兌換相關數據"""
    try:
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 使用 FirebaseService 的方法獲取用戶數據
        user_data = firebase_service.get_user_info(user_id)
        
        if not user_data:
            logger.warning(f"找不到用戶資料: {user_id}")
            return jsonify({'success': False, 'message': '找不到用戶資料'}), 404
        
        # 提取兌換相關數據，使用默認值確保數據完整性
        exchange_data = {
            'normal_potion_fragments': int(user_data.get('normal_potion_fragments', 0)),
            'normal_potions': int(user_data.get('normal_potions', 0)),
            'magic_circle_normal': int(user_data.get('magic_circle_normal', 0)),
            'magic_circle_advanced': int(user_data.get('magic_circle_advanced', 0)),
            'magic_circle_legendary': int(user_data.get('magic_circle_legendary', 0))
        }
        
        logger.info(f"成功獲取用戶 {user_id} 的兌換數據: {exchange_data}")
        
        return jsonify({
            'success': True,
            'exchange_data': exchange_data
        })
        
    except Exception as e:
        logger.error(f"獲取兌換數據失敗 - 用戶ID: {getattr(current_user, 'id', 'unknown')}, 錯誤: {str(e)}")
        return jsonify({'success': False, 'message': f'系統錯誤，請稍後再試'}), 500

@exchange_shop.route('/api/exchange-potion-fragments', methods=['POST'])
@login_required
def exchange_potion_fragments():
    """兌換普通藥水碎片為普通藥水"""
    try:
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 使用 FirebaseService 獲取最新的用戶數據
        user_data = firebase_service.get_user_info(user_id)
        
        if not user_data:
            logger.warning(f"兌換藥水碎片時找不到用戶資料: {user_id}")
            return jsonify({'success': False, 'message': '找不到用戶資料'}), 404
        
        current_fragments = int(user_data.get('normal_potion_fragments', 0))
        
        if current_fragments < 7:
            logger.info(f"用戶 {user_id} 藥水碎片不足: {current_fragments}")
            return jsonify({
                'success': False, 
                'message': f'碎片不足！需要7個碎片，目前只有{current_fragments}個'
            }), 400
        
        # 計算可兌換的藥水數量
        potions_to_exchange = current_fragments // 7
        fragments_after_exchange = current_fragments % 7
        
        current_potions = int(user_data.get('normal_potions', 0))
        new_potions = current_potions + potions_to_exchange
        
        # 直接更新Firestore（更可靠的方法）
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        
        # 使用事務確保數據一致性
        @firebase_service.firestore_db.transactional
        def update_potion_exchange(transaction, user_ref):
            # 再次檢查最新數據（防止併發問題）
            fresh_user_doc = user_ref.get(transaction=transaction)
            if not fresh_user_doc.exists:
                raise ValueError("用戶文檔不存在")
            
            fresh_user_data = fresh_user_doc.to_dict()
            fresh_fragments = int(fresh_user_data.get('normal_potion_fragments', 0))
            
            if fresh_fragments < 7:
                raise ValueError(f"碎片不足！需要7個碎片，目前只有{fresh_fragments}個")
            
            # 重新計算（基於最新數據）
            fresh_potions_to_exchange = fresh_fragments // 7
            fresh_fragments_after = fresh_fragments % 7
            fresh_current_potions = int(fresh_user_data.get('normal_potions', 0))
            fresh_new_potions = fresh_current_potions + fresh_potions_to_exchange
            
            # 更新數據
            transaction.update(user_ref, {
                'normal_potion_fragments': fresh_fragments_after,
                'normal_potions': fresh_new_potions
            })
            
            return fresh_potions_to_exchange, fresh_fragments_after, fresh_new_potions
        
        # 執行事務
        try:
            potions_exchanged, remaining_fragments, total_potions = update_potion_exchange(
                firebase_service.firestore_db.transaction(), user_ref
            )
        except ValueError as ve:
            return jsonify({'success': False, 'message': str(ve)}), 400
        
        logger.info(f"用戶 {user_id} 成功兌換 {potions_exchanged} 瓶藥水，剩餘碎片: {remaining_fragments}")
        
        return jsonify({
            'success': True,
            'message': f'成功兌換{potions_exchanged}瓶普通藥水！',
            'exchanged_potions': potions_exchanged,
            'remaining_fragments': remaining_fragments,
            'total_potions': total_potions
        })
        
    except Exception as e:
        logger.error(f"兌換藥水碎片失敗 - 用戶ID: {getattr(current_user, 'id', 'unknown')}, 錯誤: {str(e)}")
        return jsonify({'success': False, 'message': '兌換失敗，請稍後再試'}), 500

@exchange_shop.route('/api/exchange-magic-circles', methods=['POST'])
@login_required
def exchange_magic_circles():
    """兌換魔法陣"""
    try:
        data = request.get_json()
        exchange_type = data.get('exchange_type')  # 'normal_to_advanced' 或 'advanced_to_legendary'
        
        if exchange_type not in ['normal_to_advanced', 'advanced_to_legendary']:
            return jsonify({'success': False, 'message': '無效的兌換類型'}), 400
        
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 使用 FirebaseService 獲取最新的用戶數據
        user_data = firebase_service.get_user_info(user_id)
        
        if not user_data:
            logger.warning(f"兌換魔法陣時找不到用戶資料: {user_id}")
            return jsonify({'success': False, 'message': '找不到用戶資料'}), 404
        
        # 直接獲取Firestore引用準備事務操作
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        
        if exchange_type == 'normal_to_advanced':
            # 10個普通魔法陣兌換1個進階魔法陣
            @firebase_service.firestore_db.transactional
            def update_normal_to_advanced(transaction, user_ref):
                fresh_user_doc = user_ref.get(transaction=transaction)
                if not fresh_user_doc.exists:
                    raise ValueError("用戶文檔不存在")
                
                fresh_user_data = fresh_user_doc.to_dict()
                current_normal = int(fresh_user_data.get('magic_circle_normal', 0))
                
                if current_normal < 10:
                    raise ValueError(f'普通魔法陣不足！需要10個，目前只有{current_normal}個')
                
                advanced_to_add = current_normal // 10
                normal_remaining = current_normal % 10
                current_advanced = int(fresh_user_data.get('magic_circle_advanced', 0))
                new_advanced = current_advanced + advanced_to_add
                
                transaction.update(user_ref, {
                    'magic_circle_normal': normal_remaining,
                    'magic_circle_advanced': new_advanced
                })
                
                return advanced_to_add, normal_remaining, new_advanced
            
            try:
                exchanged_amount, remaining_normal, total_advanced = update_normal_to_advanced(
                    firebase_service.firestore_db.transaction(), user_ref
                )
            except ValueError as ve:
                return jsonify({'success': False, 'message': str(ve)}), 400
            
            logger.info(f"用戶 {user_id} 成功兌換 {exchanged_amount} 個進階魔法陣")
            
            return jsonify({
                'success': True,
                'message': f'成功兌換{exchanged_amount}個進階魔法陣！',
                'exchanged_amount': exchanged_amount,
                'remaining_normal': remaining_normal,
                'total_advanced': total_advanced
            })
            
        elif exchange_type == 'advanced_to_legendary':
            # 10個進階魔法陣兌換1個高級魔法陣
            @firebase_service.firestore_db.transactional
            def update_advanced_to_legendary(transaction, user_ref):
                fresh_user_doc = user_ref.get(transaction=transaction)
                if not fresh_user_doc.exists:
                    raise ValueError("用戶文檔不存在")
                
                fresh_user_data = fresh_user_doc.to_dict()
                current_advanced = int(fresh_user_data.get('magic_circle_advanced', 0))
                
                if current_advanced < 10:
                    raise ValueError(f'進階魔法陣不足！需要10個，目前只有{current_advanced}個')
                
                legendary_to_add = current_advanced // 10
                advanced_remaining = current_advanced % 10
                current_legendary = int(fresh_user_data.get('magic_circle_legendary', 0))
                new_legendary = current_legendary + legendary_to_add
                
                transaction.update(user_ref, {
                    'magic_circle_advanced': advanced_remaining,
                    'magic_circle_legendary': new_legendary
                })
                
                return legendary_to_add, advanced_remaining, new_legendary
            
            try:
                exchanged_amount, remaining_advanced, total_legendary = update_advanced_to_legendary(
                    firebase_service.firestore_db.transaction(), user_ref
                )
            except ValueError as ve:
                return jsonify({'success': False, 'message': str(ve)}), 400
            
            logger.info(f"用戶 {user_id} 成功兌換 {exchanged_amount} 個高級魔法陣")
            
            return jsonify({
                'success': True,
                'message': f'成功兌換{exchanged_amount}個高級魔法陣！',
                'exchanged_amount': exchanged_amount,
                'remaining_advanced': remaining_advanced,
                'total_legendary': total_legendary
            })
        
    except Exception as e:
        logger.error(f"兌換魔法陣失敗 - 用戶ID: {getattr(current_user, 'id', 'unknown')}, 錯誤: {str(e)}")
        return jsonify({'success': False, 'message': '兌換失敗，請稍後再試'}), 500
