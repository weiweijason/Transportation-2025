from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import logging
from firebase_admin import firestore
from app.services.firebase_service import FirebaseService
from app.config.firebase_config import FIREBASE_CONFIG

# 創建 daily_migration 藍圖
daily_migration = Blueprint('daily_migration', __name__, url_prefix='/daily-migration')

# 設置日誌記錄
logger = logging.getLogger(__name__)

@daily_migration.route('/')
@login_required
def daily_migration_page():
    """每日簽到頁面"""
    return render_template('daily_migration/daily_migration.html', 
                         firebase_config=FIREBASE_CONFIG)

@daily_migration.route('/api/get-migration-status', methods=['GET'])
@login_required
def get_migration_status():
    """獲取用戶的每日簽到狀態"""
    try:
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 獲取用戶數據
        user_data = firebase_service.get_user_info(user_id)
        if not user_data:
            return jsonify({'success': False, 'message': '找不到用戶資料'}), 404
        
        # 獲取今日日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 獲取每日簽到記錄
        migration_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('daily_migrations')
        today_migration = migration_ref.document(today).get()
        
        migration_data = {
            'user_id': user_id,
            'username': user_data.get('username', '未知用戶'),
            'today': today,
            'has_migrated_today': today_migration.exists,
            'total_migrations': 0,
            'consecutive_days': 0,
            'last_migration_date': None,
            'migration_streak': 0,
            'rewards_claimed': False
        }
        
        if today_migration.exists:
            today_data = today_migration.to_dict()
            migration_data.update({
                'migration_time': today_data.get('migration_time'),
                'rewards_claimed': today_data.get('rewards_claimed', False),
                'experience_gained': today_data.get('experience_gained', 0),
                'items_received': today_data.get('items_received', [])
            })
        
        # 獲取遷移統計
        all_migrations = migration_ref.order_by('migration_date', direction=firestore.Query.DESCENDING).get()
        migration_data['total_migrations'] = len(all_migrations)
        
        # 計算連續天數
        consecutive_days = calculate_consecutive_days(all_migrations)
        migration_data['consecutive_days'] = consecutive_days
        
        if all_migrations:
            latest_migration = all_migrations[0].to_dict()
            migration_data['last_migration_date'] = latest_migration.get('migration_date')
        
        return jsonify({
            'success': True,
            'migration_data': migration_data
        })
        
    except Exception as e:
        logger.error(f"獲取遷移狀態失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'獲取狀態失敗: {str(e)}'}), 500

@daily_migration.route('/api/perform-migration', methods=['POST'])
@login_required
def perform_migration():
    """執行每日遷移"""
    try:
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 獲取今日日期
        today = datetime.now().strftime('%Y-%m-%d')
        today_datetime = datetime.now()
          # 檢查今天是否已經簽到過
        migration_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('daily_migrations')
        today_migration = migration_ref.document(today).get()
        
        if today_migration.exists:
            return jsonify({
                'success': False, 
                'message': '今天已經完成簽到了！明天再來吧～'
            }), 400
        
        # 獲取用戶資料
        user_data = firebase_service.get_user_info(user_id)
        if not user_data:
            return jsonify({'success': False, 'message': '找不到用戶資料'}), 404
        
        # 計算獎勵
        rewards = calculate_migration_rewards(user_id, firebase_service)
          # 記錄簽到
        migration_data = {
            'migration_date': today,
            'migration_time': today_datetime.isoformat(),
            'experience_gained': rewards['experience'],
            'items_received': rewards['items'],
            'rewards_claimed': True,
            'created_at': today_datetime.isoformat()
        }
        
        # 保存簽到記錄
        migration_ref.document(today).set(migration_data)
        
        # 更新用戶經驗值
        current_exp = user_data.get('experience', 0)
        new_exp = current_exp + rewards['experience']
        
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        user_ref.update({
            'experience': new_exp,
            'last_migration_date': today
        })
        
        # 添加道具到背包
        if rewards['items']:
            add_items_to_backpack(user_id, rewards['items'], firebase_service)
          # 檢查並觸發成就
        triggered_achievements = check_migration_achievements(user_id, firebase_service)
        
        return jsonify({
            'success': True,
            'message': '簽到完成！獲得了豐富的獎勵！',
            'rewards': rewards,
            'new_experience': new_exp,
            'triggered_achievements': triggered_achievements
        })
        
    except Exception as e:
        logger.error(f"執行遷移失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'遷移失敗: {str(e)}'}), 500

@daily_migration.route('/api/get-migration-history', methods=['GET'])
@login_required
def get_migration_history():
    """獲取遷移歷史記錄"""
    try:
        firebase_service = FirebaseService()
        user_id = current_user.id
        
        # 獲取最近30天的遷移記錄
        migration_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('daily_migrations')
        migrations = migration_ref.order_by('migration_date', direction=firestore.Query.DESCENDING).limit(30).get()
        
        history = []
        for migration in migrations:
            data = migration.to_dict()
            history.append({
                'date': data.get('migration_date'),
                'experience': data.get('experience_gained', 0),
                'items': data.get('items_received', []),
                'time': data.get('migration_time')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"獲取遷移歷史失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'獲取歷史失敗: {str(e)}'}), 500

def calculate_consecutive_days(migrations):
    """計算連續天數"""
    if not migrations:
        return 0
    
    consecutive = 0
    today = datetime.now().date()
    
    for i, migration in enumerate(migrations):
        data = migration.to_dict()
        migration_date = datetime.strptime(data.get('migration_date'), '%Y-%m-%d').date()
        
        expected_date = today - timedelta(days=i)
        
        if migration_date == expected_date:
            consecutive += 1
        else:
            break
    
    return consecutive

def calculate_migration_rewards(user_id, firebase_service):
    """計算簽到獎勵"""
    # 獲取連續天數
    migration_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('daily_migrations')
    all_migrations = migration_ref.order_by('migration_date', direction=firestore.Query.DESCENDING).get()
    consecutive_days = calculate_consecutive_days(all_migrations)
    
    # 基礎獎勵：100經驗值和1個普通藥水碎片
    base_experience = 100
    base_items = [{'item_id': 'normal_potion_fragment', 'quantity': 1, 'name': '普通藥水碎片'}]
    
    # 連續獎勵加成
    bonus_multiplier = min(1 + (consecutive_days * 0.1), 3.0)  # 最多3倍獎勵
    experience = int(base_experience * bonus_multiplier)
    
    items = base_items.copy()
    
    # 連續天數特殊獎勵
    if consecutive_days >= 7:
        items.append({'item_id': 'magic_circle_normal', 'quantity': 1, 'name': '普通魔法陣'})
    if consecutive_days >= 14:
        items.append({'item_id': 'normal_potion_fragment', 'quantity': 2, 'name': '普通藥水碎片'})
    if consecutive_days >= 30:
        items.append({'item_id': 'magic_circle_advanced', 'quantity': 1, 'name': '進階魔法陣'})
    
    return {
        'experience': experience,
        'items': items,
        'consecutive_days': consecutive_days,
        'bonus_multiplier': bonus_multiplier
    }

def add_items_to_backpack(user_id, items, firebase_service):
    """添加道具到背包"""
    try:
        for item in items:
            item_id = item['item_id']
            quantity = item['quantity']
            
            # 特殊處理普通藥水碎片 - 存儲到 user_backpack 子集合
            if item_id == 'normal_potion_fragment':
                backpack_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('user_backpack')
                fragments_doc_ref = backpack_ref.document('normal_potion_fragments')
                
                # 獲取當前碎片文檔
                fragments_doc = fragments_doc_ref.get()
                
                if fragments_doc.exists:
                    # 如果文檔存在，更新 count
                    current_count = fragments_doc.to_dict().get('count', 0)
                    new_count = current_count + quantity
                    fragments_doc_ref.update({
                        'count': new_count,
                        'updated_at': datetime.now().isoformat()
                    })
                    logger.info(f"更新普通藥水碎片: 用戶 {user_id}, 從 {current_count} 增加到 {new_count}")
                else:
                    # 如果文檔不存在，創建新文檔
                    fragments_doc_ref.set({
                        'count': quantity,
                        'item_type': 'potion_fragment',
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'source': 'daily_checkin'
                    })
                    logger.info(f"創建普通藥水碎片文檔: 用戶 {user_id}, 設置 count 為 {quantity}")
            else:
                # 其他道具的處理邏輯保持原樣
                backpack_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('user_backpack')
                existing_item = backpack_ref.where('item_id', '==', item_id).get()
                
                if existing_item:
                    # 更新數量
                    doc = existing_item[0]
                    current_quantity = doc.to_dict().get('quantity', 0)
                    doc.reference.update({'quantity': current_quantity + quantity})
                else:
                    # 新增道具
                    backpack_ref.add({
                        'item_id': item_id,
                        'item_name': item['name'],
                        'quantity': quantity,
                        'obtained_at': datetime.now().isoformat(),
                        'source': 'daily_checkin'
                    })
                    
    except Exception as e:
        logger.error(f"添加道具到背包失敗: {str(e)}")
        raise e  # 重新拋出異常，讓上層處理

def check_migration_achievements(user_id, firebase_service):
    """檢查並觸發遷移相關成就"""
    try:
        # 獲取遷移統計
        migration_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('daily_migrations')
        all_migrations = migration_ref.get()
        total_migrations = len(all_migrations)
        consecutive_days = calculate_consecutive_days(all_migrations)
        
        triggered_achievements = []
        
        # 檢查登入天數成就
        achievement_triggers = [
            {'id': 'ACH-LOGIN-001', 'threshold': 1, 'name': '感謝每一次相遇'},
            {'id': 'ACH-LOGIN-002', 'threshold': 7, 'name': '感恩每一段緣分'},
            {'id': 'ACH-LOGIN-003', 'threshold': 30, 'name': '珍惜旅途的風景'},
            {'id': 'ACH-LOGIN-004', 'threshold': 60, 'name': '期待每一個明天'},
            {'id': 'ACH-LOGIN-005', 'threshold': 100, 'name': '阿偉你麼還在打電動？'},
        ]
        
        for trigger in achievement_triggers:
            if total_migrations >= trigger['threshold']:
                # 檢查成就是否已達成
                achievement_ref = firebase_service.firestore_db.collection('users').document(user_id).collection('user_achievements').document(trigger['id'])
                achievement_doc = achievement_ref.get()
                
                if not achievement_doc.exists:
                    # 觸發成就
                    achievement_data = {
                        'achievement_id': trigger['id'],
                        'completed': True,
                        'progress': total_migrations,
                        'target_value': trigger['threshold'],
                        'completed_at': datetime.now().isoformat(),
                        'created_at': datetime.now().isoformat()
                    }
                    achievement_ref.set(achievement_data)
                    triggered_achievements.append({
                        'id': trigger['id'],
                        'name': trigger['name']
                    })
        
        return triggered_achievements
        
    except Exception as e:
        logger.error(f"檢查成就失敗: {str(e)}")
        return []
