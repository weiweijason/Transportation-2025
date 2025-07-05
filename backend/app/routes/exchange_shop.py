from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.services.firebase_service import FirebaseService
from app.config.firebase_config import FIREBASE_CONFIG
from google.cloud import firestore
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
        
        # 獲取用戶背包子集合數據
        backpack_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('user_backpack')
        backpack_docs = backpack_ref.get()
        
        # 初始化數據
        exchange_data = {
            'normal_potion_fragments': 0,
            'normal_potions': 0,
            'magic_circle_normal': 0,
            'magic_circle_advanced': 0,
            'magic_circle_legendary': 0
        }
        
        # 從背包子集合中提取數據
        for doc in backpack_docs:
            item_id = doc.id
            item_data = doc.to_dict()
            count = int(item_data.get('count', 0))
            
            # 魔法陣數量
            if item_id == 'normal':
                exchange_data['magic_circle_normal'] = count
            elif item_id == 'advanced':
                exchange_data['magic_circle_advanced'] = count
            elif item_id == 'premium':
                exchange_data['magic_circle_legendary'] = count
            # 藥水碎片數量
            elif item_id == 'normal_potion_fragments':
                exchange_data['normal_potion_fragments'] = count
            # 普通藥水數量
            elif item_id == 'normal_potion':
                exchange_data['normal_potions'] = count
        
        logger.info(f"成功獲取用戶 {user_id} 的兌換數據 (從user_backpack): {exchange_data}")
        
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
        
        # 獲取用戶背包子集合中的藥水碎片數據
        backpack_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('user_backpack')
        fragments_doc_ref = backpack_ref.document('normal_potion_fragments')
        potions_doc_ref = backpack_ref.document('normal_potion')
        
        # 使用事務確保數據一致性
        @firestore.transactional
        def update_potion_exchange(transaction):
            # 獲取當前碎片數量
            fragments_doc = fragments_doc_ref.get(transaction=transaction)
            current_fragments = 0
            if fragments_doc.exists:
                current_fragments = int(fragments_doc.to_dict().get('count', 0))
            
            if current_fragments < 7:
                raise ValueError(f"碎片不足！需要7個碎片，目前只有{current_fragments}個")
            
            # 計算兌換數量
            potions_to_exchange = current_fragments // 7
            fragments_after_exchange = current_fragments % 7
            
            # 獲取當前藥水數量
            potions_doc = potions_doc_ref.get(transaction=transaction)
            current_potions = 0
            if potions_doc.exists:
                current_potions = int(potions_doc.to_dict().get('count', 0))
            
            new_potions = current_potions + potions_to_exchange
            
            # 更新碎片數量
            if fragments_after_exchange > 0:
                transaction.set(fragments_doc_ref, {'count': fragments_after_exchange})
            else:
                # 如果碎片數量為0，刪除文檔
                transaction.delete(fragments_doc_ref)
            
            # 更新藥水數量
            transaction.set(potions_doc_ref, {'count': new_potions})
            
            return potions_to_exchange, fragments_after_exchange, new_potions
        
        # 執行事務
        try:
            potions_exchanged, remaining_fragments, total_potions = update_potion_exchange(
                firebase_service.firestore_db.transaction()
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
        exchange_amount = data.get('exchange_amount', 1)  # 用戶指定的兌換次數，默認為1
        
        if exchange_type not in ['normal_to_advanced', 'advanced_to_legendary']:
            return jsonify({'success': False, 'message': '無效的兌換類型'}), 400
        
        # 驗證兌換數量
        try:
            exchange_amount = int(exchange_amount)
            if exchange_amount <= 0:
                return jsonify({'success': False, 'message': '兌換數量必須大於0'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '無效的兌換數量'}), 400
        
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 獲取用戶背包子集合引用
        backpack_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('user_backpack')
        
        if exchange_type == 'normal_to_advanced':
            # 10個普通魔法陣兌換1個進階魔法陣
            normal_doc_ref = backpack_ref.document('normal')
            advanced_doc_ref = backpack_ref.document('advanced')
            
            @firestore.transactional
            def update_normal_to_advanced(transaction):
                # 獲取當前普通魔法陣數量
                normal_doc = normal_doc_ref.get(transaction=transaction)
                current_normal = 0
                if normal_doc.exists:
                    current_normal = int(normal_doc.to_dict().get('count', 0))
                
                # 檢查是否有足夠的普通魔法陣進行指定次數的兌換
                required_normal = exchange_amount * 10
                if current_normal < required_normal:
                    raise ValueError(f'普通魔法陣不足！需要{required_normal}個進行{exchange_amount}次兌換，目前只有{current_normal}個')
                
                # 計算兌換後的數量
                normal_remaining = current_normal - required_normal
                
                # 獲取當前進階魔法陣數量
                advanced_doc = advanced_doc_ref.get(transaction=transaction)
                current_advanced = 0
                if advanced_doc.exists:
                    current_advanced = int(advanced_doc.to_dict().get('count', 0))
                
                new_advanced = current_advanced + exchange_amount
                
                # 更新普通魔法陣數量
                if normal_remaining > 0:
                    transaction.set(normal_doc_ref, {'count': normal_remaining})
                else:
                    # 如果數量為0，刪除文檔
                    transaction.delete(normal_doc_ref)
                
                # 更新進階魔法陣數量
                transaction.set(advanced_doc_ref, {'count': new_advanced})
                
                return exchange_amount, normal_remaining, new_advanced
            
            try:
                exchanged_amount, remaining_normal, total_advanced = update_normal_to_advanced(
                    firebase_service.firestore_db.transaction()
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
            advanced_doc_ref = backpack_ref.document('advanced')
            premium_doc_ref = backpack_ref.document('premium')
            
            @firestore.transactional
            def update_advanced_to_legendary(transaction):
                # 獲取當前進階魔法陣數量
                advanced_doc = advanced_doc_ref.get(transaction=transaction)
                current_advanced = 0
                if advanced_doc.exists:
                    current_advanced = int(advanced_doc.to_dict().get('count', 0))
                
                # 檢查是否有足夠的進階魔法陣進行指定次數的兌換
                required_advanced = exchange_amount * 10
                if current_advanced < required_advanced:
                    raise ValueError(f'進階魔法陣不足！需要{required_advanced}個進行{exchange_amount}次兌換，目前只有{current_advanced}個')
                
                # 計算兌換後的數量
                advanced_remaining = current_advanced - required_advanced
                
                # 獲取當前高級魔法陣數量
                premium_doc = premium_doc_ref.get(transaction=transaction)
                current_legendary = 0
                if premium_doc.exists:
                    current_legendary = int(premium_doc.to_dict().get('count', 0))
                
                new_legendary = current_legendary + exchange_amount
                
                # 更新進階魔法陣數量
                if advanced_remaining > 0:
                    transaction.set(advanced_doc_ref, {'count': advanced_remaining})
                else:
                    # 如果數量為0，刪除文檔
                    transaction.delete(advanced_doc_ref)
                
                # 更新高級魔法陣數量
                transaction.set(premium_doc_ref, {'count': new_legendary})
                
                return exchange_amount, advanced_remaining, new_legendary
            
            try:
                exchanged_amount, remaining_advanced, total_legendary = update_advanced_to_legendary(
                    firebase_service.firestore_db.transaction()
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
