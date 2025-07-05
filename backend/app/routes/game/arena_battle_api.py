from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.services.firebase_service import FirebaseService
from app.models.fight import calculate_battle
import traceback
import time
from datetime import datetime

# 創建新的道館戰鬥藍圖
arena_battle_bp = Blueprint('arena_battle', __name__, url_prefix='/game/api/arena-battle')

@arena_battle_bp.route('/get-arena/<arena_id>')
@login_required
def get_arena_details(arena_id):
    """獲取道館詳細資訊，如果不存在則創建"""
    try:
        firebase_service = FirebaseService()
        
        # 嘗試從 Firebase 獲取道館資料
        arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
        arena_doc = arena_ref.get()
        
        if arena_doc.exists:
            # 道館已存在，返回資料
            arena_data = arena_doc.to_dict()
            arena_data['id'] = arena_id
            
            # 檢查並更新獎勵
            arena_data = check_and_update_rewards(arena_data, firebase_service)
            
            return jsonify({
                'success': True,
                'arena': arena_data
            })
        else:
            # 道館不存在，創建新道館
            new_arena_data = create_new_arena(arena_id, firebase_service)
            return jsonify({
                'success': True,
                'arena': new_arena_data,
                'created': True
            })
            
    except Exception as e:
        current_app.logger.error(f"獲取道館資料失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'獲取道館資料失敗: {str(e)}'
        }), 500

def create_new_arena(arena_id, firebase_service):
    """創建新道館"""
    # 根據 arena_id 解析道館等級和名稱
    # 假設 arena_id 格式為 "level_1_arena_001" 或類似
    level = extract_arena_level(arena_id)
    name = extract_arena_name(arena_id)
    
    new_arena_data = {
        'id': arena_id,
        'name': name,
        'level': level,
        'owner': None,
        'owner_player_id': None,
        'owner_creature': None,
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
        'total_battles': 0,
        'rewards': {
            'last_collected': None,
            'accumulated_hours': 0,
            'available_rewards': []
        }
    }
    
    # 保存到 Firebase
    firebase_service.firestore_db.collection('arenas').document(arena_id).set(new_arena_data)
    
    return new_arena_data

def extract_arena_level(arena_id):
    """從道館ID提取等級，預設為1"""
    try:
        # 嘗試從ID中提取等級信息
        if 'level_1' in arena_id or 'lv1' in arena_id:
            return 1
        elif 'level_2' in arena_id or 'lv2' in arena_id:
            return 2
        elif 'level_3' in arena_id or 'lv3' in arena_id:
            return 3
        elif 'level_4' in arena_id or 'lv4' in arena_id:
            return 4
        elif 'level_5' in arena_id or 'lv5' in arena_id:
            return 5
        else:
            return 1  # 預設等級
    except:
        return 1

def extract_arena_name(arena_id):
    """從道館ID提取名稱"""
    try:
        # 簡單的名稱生成邏輯
        level = extract_arena_level(arena_id)
        return f"等級 {level} 道館"
    except:
        return "未知道館"

@arena_battle_bp.route('/get-user-creatures')
@login_required
def get_user_creatures():
    """獲取用戶的精靈，根據道館等級進行過濾，並排除已佔領道館的精靈"""
    try:
        arena_level = request.args.get('arena_level', 1, type=int)
        include_occupied = request.args.get('include_occupied', 'false').lower() == 'true'
        
        firebase_service = FirebaseService()
        
        # 獲取用戶的精靈
        user_ref = firebase_service.firestore_db.collection('users').document(current_user.id)
        user_creatures_ref = user_ref.collection('user_creatures').get()
        
        # 獲取已佔領道館的精靈ID列表
        occupied_creature_ids = set()
        if not include_occupied:
            user_arenas = user_ref.collection('user_arenas').where('status', '==', 'occupied').get()
            for arena_doc in user_arenas:
                arena_data = arena_doc.to_dict()
                creature_id = arena_data.get('guardian_creature_id')
                if creature_id:
                    occupied_creature_ids.add(creature_id)
        
        creatures_list = []
        for creature_doc in user_creatures_ref:
            creature_data = creature_doc.to_dict()
            creature_data['id'] = creature_doc.id
            
            # 檢查精靈是否已被用於佔領道館
            if not include_occupied and creature_doc.id in occupied_creature_ids:
                creature_data['is_occupied'] = True
                continue  # 跳過已佔領道館的精靈
            else:
                creature_data['is_occupied'] = False
            
            # 根據道館等級過濾精靈
            if is_creature_allowed_in_arena(creature_data, arena_level):
                creatures_list.append(creature_data)
        
        return jsonify({
            'success': True,
            'creatures': creatures_list,
            'total_available': len(creatures_list),
            'occupied_count': len(occupied_creature_ids)
        })
        
    except Exception as e:
        current_app.logger.error(f"獲取用戶精靈失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'獲取用戶精靈失敗: {str(e)}'
        }), 500

def is_creature_allowed_in_arena(creature_data, arena_level):
    """檢查精靈是否能在指定等級的道館中使用"""
    rarity = creature_data.get('rarity', creature_data.get('rate', 'N')).upper()
    
    if arena_level == 1:
        # 等級1道館：只能使用 N, R
        return rarity in ['N', 'R']
    elif arena_level == 2:
        # 等級2道館：只能使用 N, R, SR
        return rarity in ['N', 'R', 'SR']
    else:
        # 等級3+道館：全部稀有度都可以使用
        return True

@arena_battle_bp.route('/occupy', methods=['POST'])
@login_required
def occupy_arena():
    """佔領道館（無人佔領時直接佔領）"""
    try:
        data = request.json
        arena_id = data.get('arena_id')
        creature_id = data.get('creature_id')
        
        if not arena_id or not creature_id:
            return jsonify({
                'success': False,
                'message': '缺少必要參數'
            }), 400
        
        firebase_service = FirebaseService()
        
        # 獲取道館資料
        arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
        arena_doc = arena_ref.get()
        
        if not arena_doc.exists:
            return jsonify({
                'success': False,
                'message': '道館不存在'
            }), 404
        
        arena_data = arena_doc.to_dict()
        
        # 檢查道館是否已被佔領
        if arena_data.get('owner'):
            return jsonify({
                'success': False,
                'message': '道館已被佔領，請進行戰鬥'
            }), 400
        
        # 獲取用戶精靈資料
        user_ref = firebase_service.firestore_db.collection('users').document(current_user.id)
        creature_ref = user_ref.collection('user_creatures').document(creature_id)
        creature_doc = creature_ref.get()
        
        if not creature_doc.exists:
            return jsonify({
                'success': False,
                'message': '精靈不存在'
            }), 404
        
        creature_data = creature_doc.to_dict()
        creature_data['id'] = creature_id
        
        # 檢查精靈是否符合道館等級要求
        arena_level = arena_data.get('level', 1)
        if not is_creature_allowed_in_arena(creature_data, arena_level):
            return jsonify({
                'success': False,
                'message': f'此精靈不符合等級 {arena_level} 道館的使用要求'
            }), 400
        
        # 檢查精靈是否已被用於佔領其他道館
        if is_creature_already_occupying(current_user.id, creature_id, firebase_service):
            return jsonify({
                'success': False,
                'message': '此精靈已被用於佔領其他道館，不可重複使用'
            }), 400
        
        # 獲取用戶資料
        user_data = firebase_service.get_user_info(current_user.id)
        username = user_data.get('username', '未知玩家')
        player_id = user_data.get('player_id', current_user.id)
        
        # 佔領道館
        occupy_time = datetime.now().isoformat()
        arena_ref.update({
            'owner': username,
            'owner_player_id': player_id,
            'owner_creature': creature_data,
            'occupied_at': occupy_time,
            'last_updated': occupy_time,
            'rewards.last_collected': occupy_time,
            'rewards.accumulated_hours': 0
        })
        
        # 保存到用戶的 user_arenas 子集合中
        save_user_arena_occupation(current_user.id, arena_id, creature_id, firebase_service)
        
        # 獲取更新後的道館資料
        updated_arena = arena_ref.get().to_dict()
        updated_arena['id'] = arena_id
        
        return jsonify({
            'success': True,
            'message': f'成功佔領道館！',
            'arena': updated_arena
        })
        
    except Exception as e:
        current_app.logger.error(f"佔領道館失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'佔領道館失敗: {str(e)}'
        }), 500

@arena_battle_bp.route('/battle', methods=['POST'])
@login_required
def battle_arena():
    """道館戰鬥"""
    try:
        data = request.json
        arena_id = data.get('arena_id')
        challenger_creature_id = data.get('creature_id')
        
        if not arena_id or not challenger_creature_id:
            return jsonify({
                'success': False,
                'message': '缺少必要參數'
            }), 400
        
        firebase_service = FirebaseService()
        
        # 獲取道館資料
        arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
        arena_doc = arena_ref.get()
        
        if not arena_doc.exists:
            return jsonify({
                'success': False,
                'message': '道館不存在'
            }), 404
        
        arena_data = arena_doc.to_dict()
        
        # 檢查道館是否有守護者
        if not arena_data.get('owner') or not arena_data.get('owner_creature'):
            return jsonify({
                'success': False,
                'message': '道館無人佔領，請直接佔領'
            }), 400
        
        # 檢查是否為道館擁有者
        user_data = firebase_service.get_user_info(current_user.id)
        player_id = user_data.get('player_id', current_user.id)
        
        if arena_data.get('owner_player_id') == player_id:
            return jsonify({
                'success': False,
                'message': '不能挑戰自己的道館'
            }), 400
        
        # 獲取挑戰者精靈資料
        user_ref = firebase_service.firestore_db.collection('users').document(current_user.id)
        challenger_creature_ref = user_ref.collection('user_creatures').document(challenger_creature_id)
        challenger_creature_doc = challenger_creature_ref.get()
        
        if not challenger_creature_doc.exists:
            return jsonify({
                'success': False,
                'message': '挑戰者精靈不存在'
            }), 404
        
        challenger_creature = challenger_creature_doc.to_dict()
        challenger_creature['id'] = challenger_creature_id
          # 檢查精靈是否符合道館等級要求
        arena_level = arena_data.get('level', 1)
        if not is_creature_allowed_in_arena(challenger_creature, arena_level):
            return jsonify({
                'success': False,
                'message': f'此精靈不符合等級 {arena_level} 道館的使用要求'
            }), 400
        
        # 檢查精靈是否已被用於佔領其他道館
        if is_creature_already_occupying(current_user.id, challenger_creature_id, firebase_service):
            return jsonify({
                'success': False,
                'message': '此精靈已被用於佔領其他道館，不可重複使用'
            }), 400
        
        # 獲取守護者精靈資料
        defender_creature = arena_data.get('owner_creature')
        
        # 執行戰鬥（使用 fight.py 的戰鬥系統）
        battle_result = calculate_battle(challenger_creature, defender_creature)
        
        # 更新道館戰鬥次數
        arena_ref.update({
            'total_battles': arena_data.get('total_battles', 0) + 1,
            'last_updated': datetime.now().isoformat()
        })
          # 處理戰鬥結果
        if battle_result['winner'] == 'host':  # 挑戰者獲勝
            # 移除原擁有者的 user_arenas 記錄
            remove_user_arena_occupation(arena_data.get('owner_player_id'), arena_id, firebase_service)
            
            # 更新道館擁有者
            username = user_data.get('username', '未知玩家')
            occupy_time = datetime.now().isoformat()
            
            arena_ref.update({
                'owner': username,
                'owner_player_id': player_id,
                'owner_creature': challenger_creature,
                'occupied_at': occupy_time,
                'last_updated': occupy_time,
                'rewards.last_collected': occupy_time,
                'rewards.accumulated_hours': 0
            })
            
            # 保存到新擁有者的 user_arenas 子集合中
            save_user_arena_occupation(current_user.id, arena_id, challenger_creature_id, firebase_service)
            
            message = f'恭喜！您成功佔領了道館！'
            is_win = True
        else:
            message = f'很遺憾，挑戰失敗了。請再接再厲！'
            is_win = False
        
        # 獲取更新後的道館資料
        updated_arena = arena_ref.get().to_dict()
        updated_arena['id'] = arena_id
        
        return jsonify({
            'success': True,
            'is_win': is_win,
            'message': message,
            'battle_result': battle_result,
            'arena': updated_arena
        })
        
    except Exception as e:
        current_app.logger.error(f"道館戰鬥失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'道館戰鬥失敗: {str(e)}'
        }), 500

@arena_battle_bp.route('/collect-rewards', methods=['POST'])
@login_required
def collect_rewards():
    """收集道館獎勵"""
    try:
        data = request.json
        arena_id = data.get('arena_id')
        
        if not arena_id:
            return jsonify({
                'success': False,
                'message': '缺少道館ID'
            }), 400
        
        firebase_service = FirebaseService()
        
        # 獲取道館資料
        arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
        arena_doc = arena_ref.get()
        
        if not arena_doc.exists:
            return jsonify({
                'success': False,
                'message': '道館不存在'
            }), 404
        
        arena_data = arena_doc.to_dict()
        
        # 檢查是否為道館擁有者
        user_data = firebase_service.get_user_info(current_user.id)
        player_id = user_data.get('player_id', current_user.id)
        
        if arena_data.get('owner_player_id') != player_id:
            return jsonify({
                'success': False,
                'message': '只有道館擁有者才能收集獎勵'
            }), 403
        
        # 計算可收集的獎勵
        rewards = calculate_arena_rewards(arena_data)
        
        if not rewards['available_rewards']:
            return jsonify({
                'success': False,
                'message': '目前沒有可收集的獎勵'
            })
        
        # 添加獎勵到用戶背包
        user_ref = firebase_service.firestore_db.collection('users').document(current_user.id)
        backpack_ref = user_ref.collection('backpack')
        
        collected_items = []
        for reward in rewards['available_rewards']:
            # 檢查背包中是否已有該類型的魔法陣
            existing_items = backpack_ref.where('item_type', '==', 'magic_circle').where('circle_type', '==', reward['circle_type']).get()
            
            if existing_items:
                # 更新現有數量
                existing_item = existing_items[0]
                existing_data = existing_item.to_dict()
                new_quantity = existing_data.get('quantity', 0) + reward['quantity']
                existing_item.reference.update({'quantity': new_quantity})
            else:
                # 創建新物品
                backpack_ref.add({
                    'item_type': 'magic_circle',
                    'circle_type': reward['circle_type'],
                    'quantity': reward['quantity'],
                    'acquired_at': datetime.now().isoformat()
                })
            
            collected_items.append(reward)
        
        # 更新道館獎勵狀態
        arena_ref.update({
            'rewards.last_collected': datetime.now().isoformat(),
            'rewards.accumulated_hours': 0,
            'rewards.available_rewards': []
        })
        
        return jsonify({
            'success': True,
            'message': '成功收集獎勵！',
            'collected_items': collected_items
        })
        
    except Exception as e:
        current_app.logger.error(f"收集獎勵失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'收集獎勵失敗: {str(e)}'
        }), 500

def check_and_update_rewards(arena_data, firebase_service):
    """檢查並更新道館獎勵"""
    if not arena_data.get('owner') or not arena_data.get('occupied_at'):
        return arena_data
    
    try:
        # 計算獎勵
        rewards = calculate_arena_rewards(arena_data)
        
        # 更新道館資料中的獎勵信息
        arena_data['rewards'] = rewards
        
        # 如果有新獎勵，更新到 Firebase
        if rewards['available_rewards']:
            firebase_service.firestore_db.collection('arenas').document(arena_data['id']).update({
                'rewards': rewards
            })
    
    except Exception as e:
        current_app.logger.error(f"更新獎勵失敗: {e}")
    
    return arena_data

def calculate_arena_rewards(arena_data):
    """計算道館獎勵"""
    rewards = {
        'last_collected': arena_data.get('rewards', {}).get('last_collected'),
        'accumulated_hours': 0,
        'available_rewards': []
    }
    
    if not arena_data.get('occupied_at'):
        return rewards
    
    try:
        # 計算佔領時間
        occupied_time = datetime.fromisoformat(arena_data['occupied_at'])
        last_collected_time = occupied_time
        
        if rewards['last_collected']:
            last_collected_time = datetime.fromisoformat(rewards['last_collected'])
        
        # 計算小時數
        time_diff = datetime.now() - last_collected_time
        hours_passed = int(time_diff.total_seconds() // 3600)
        
        if hours_passed > 0:
            arena_level = arena_data.get('level', 1)
            
            # 根據道館等級決定獎勵類型
            if arena_level == 1:
                circle_type = 'normal'
            elif arena_level == 2:
                circle_type = 'advanced'
            else:
                circle_type = 'premium'
            
            rewards['accumulated_hours'] = hours_passed
            rewards['available_rewards'] = [{
                'circle_type': circle_type,
                'quantity': hours_passed,
                'description': f'{hours_passed} 個 {circle_type} 魔法陣'
            }]
    
    except Exception as e:
        current_app.logger.error(f"計算獎勵時發生錯誤: {e}")
    
    return rewards

def is_creature_already_occupying(user_id, creature_id, firebase_service):
    """檢查精靈是否已被用於佔領其他道館
    
    Args:
        user_id (str): 用戶ID
        creature_id (str): 精靈ID
        firebase_service: Firebase服務實例
        
    Returns:
        bool: 如果精靈已被用於佔領道館則返回True，否則返回False
    """
    try:
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        user_arenas = user_ref.collection('user_arenas').where('status', '==', 'occupied').get()
        
        for arena_doc in user_arenas:
            arena_data = arena_doc.to_dict()
            if arena_data.get('guardian_creature_id') == creature_id:
                return True
        
        return False
    except Exception as e:
        current_app.logger.error(f"檢查精靈佔領狀態失敗: {e}")
        return False

def save_user_arena_occupation(user_id, arena_id, creature_id, firebase_service):
    """保存用戶道館佔領記錄到 user_arenas 子集合
    
    Args:
        user_id (str): 用戶ID
        arena_id (str): 道館ID
        creature_id (str): 精靈ID
        firebase_service: Firebase服務實例
    """
    try:
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        user_arena_ref = user_ref.collection('user_arenas').document(arena_id)
        
        user_arena_data = {
            'arena_id': arena_id,
            'guardian_creature_id': creature_id,
            'occupied_at': datetime.now().isoformat(),
            'status': 'occupied'
        }
        
        user_arena_ref.set(user_arena_data)
        current_app.logger.info(f"已保存用戶道館佔領記錄: {user_id} -> {arena_id}")
        
    except Exception as e:
        current_app.logger.error(f"保存用戶道館佔領記錄失敗: {e}")

def remove_user_arena_occupation(user_id, arena_id, firebase_service):
    """移除用戶道館佔領記錄
    
    Args:
        user_id (str): 用戶ID
        arena_id (str): 道館ID
        firebase_service: Firebase服務實例
    """
    try:
        if not user_id:
            return
            
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        user_arena_ref = user_ref.collection('user_arenas').document(arena_id)
        
        # 檢查文檔是否存在
        if user_arena_ref.get().exists:
            user_arena_ref.delete()
            current_app.logger.info(f"已移除用戶道館佔領記錄: {user_id} -> {arena_id}")
        
    except Exception as e:
        current_app.logger.error(f"移除用戶道館佔領記錄失敗: {e}")

def get_user_occupied_arenas(user_id, firebase_service):
    """獲取用戶已佔領的道館列表
    
    Args:
        user_id (str): 用戶ID
        firebase_service: Firebase服務實例
        
    Returns:
        list: 已佔領的道館ID列表
    """
    try:
        user_ref = firebase_service.firestore_db.collection('users').document(user_id)
        user_arenas = user_ref.collection('user_arenas').where('status', '==', 'occupied').get()
        
        occupied_arenas = []
        for arena_doc in user_arenas:
            arena_data = arena_doc.to_dict()
            occupied_arenas.append(arena_data.get('arena_id'))
        
        return occupied_arenas
    except Exception as e:
        current_app.logger.error(f"獲取用戶已佔領道館列表失敗: {e}")
        return []

@arena_battle_bp.route('/user-arenas')
@login_required
def get_user_arenas():
    """獲取用戶已佔領的道館列表"""
    try:
        firebase_service = FirebaseService()
        occupied_arenas = get_user_occupied_arenas(current_user.id, firebase_service)
        
        # 獲取詳細的道館資訊
        arena_details = []
        for arena_id in occupied_arenas:
            arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
            arena_doc = arena_ref.get()
            
            if arena_doc.exists:
                arena_data = arena_doc.to_dict()
                arena_data['id'] = arena_id
                arena_details.append(arena_data)
        
        return jsonify({
            'success': True,
            'occupied_arenas': arena_details,
            'total_count': len(arena_details)
        })
        
    except Exception as e:
        current_app.logger.error(f"獲取用戶道館列表失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'獲取用戶道館列表失敗: {str(e)}'
        }), 500

@arena_battle_bp.route('/release', methods=['POST'])
@login_required
def release_arena():
    """釋放道館（讓玩家主動放棄道館）"""
    try:
        data = request.json
        arena_id = data.get('arena_id')
        
        if not arena_id:
            return jsonify({
                'success': False,
                'message': '缺少道館ID'
            }), 400
        
        firebase_service = FirebaseService()
        
        # 獲取道館資料
        arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
        arena_doc = arena_ref.get()
        
        if not arena_doc.exists:
            return jsonify({
                'success': False,
                'message': '道館不存在'
            }), 404
        
        arena_data = arena_doc.to_dict()
        
        # 檢查是否為道館擁有者
        user_data = firebase_service.get_user_info(current_user.id)
        player_id = user_data.get('player_id', current_user.id)
        
        if arena_data.get('owner_player_id') != player_id:
            return jsonify({
                'success': False,
                'message': '只有道館擁有者才能釋放道館'
            }), 403
        
        # 釋放道館
        arena_ref.update({
            'owner': None,
            'owner_player_id': None,
            'owner_creature': None,
            'occupied_at': None,
            'last_updated': datetime.now().isoformat(),
            'rewards.last_collected': None,
            'rewards.accumulated_hours': 0,
            'rewards.available_rewards': []
        })
        
        # 移除用戶的 user_arenas 記錄
        remove_user_arena_occupation(current_user.id, arena_id, firebase_service)
        
        # 獲取更新後的道館資料
        updated_arena = arena_ref.get().to_dict()
        updated_arena['id'] = arena_id
        
        return jsonify({
            'success': True,
            'message': '成功釋放道館！',
            'arena': updated_arena
        })
        
    except Exception as e:
        current_app.logger.error(f"釋放道館失敗: {e}")
        return jsonify({
            'success': False,
            'message': f'釋放道館失敗: {str(e)}'
        }), 500
