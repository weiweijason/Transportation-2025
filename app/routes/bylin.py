from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from flask_login import login_required, current_user
from app.config.firebase_config import FIREBASE_CONFIG
import firebase_admin
from firebase_admin import firestore

# 創建 bylin 藍圖
bylin = Blueprint('bylin', __name__, url_prefix='/bylin')

@bylin.route('/myelf')
@login_required
def myelf():
    """我的精靈頁面"""
    return render_template('bylin/myelf.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/myarena')
@login_required
def myarena():
    """我的擂台頁面"""
    return render_template('bylin/myarena.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/backpack')
@login_required
def backpack():
    """我的背包頁面"""
    return render_template('bylin/mybag.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/api/backpack', methods=['GET'])
@login_required
def get_backpack():
    """獲取使用者背包資料的API"""
    try:
        # 獲取使用者ID
        user_id = session.get('user', {}).get('uid')
        if not user_id:
            return jsonify({'success': False, 'message': '使用者未登入'})
        
        # 初始化 Firestore 客戶端
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        
        # 獲取使用者背包子集合
        backpack_ref = db.collection('users').document(user_id).collection('user_backpack')
        backpack_docs = backpack_ref.get()
        
        # 組織背包資料
        backpack_data = {
            'magic-circle': {},
            'potion': {}
        }        
        for doc in backpack_docs:
            item_id = doc.id
            item_data = doc.to_dict()
            count = item_data.get('count', 0)
            
            # 根據道具類型分類
            if item_id in ['normal', 'advanced', 'premium']:
                # 魔法陣類型
                backpack_data['magic-circle'][item_id] = count
            elif item_id in ['normal_potion', 'advanced_potion', 'premium_potion']:
                # 藥水類型，移除 _potion 後綴以符合前端期望的格式
                key = item_id.replace('_potion', '')
                backpack_data['potion'][key] = count
        
        return jsonify({
            'success': True,
            'backpack': backpack_data
        })
        
    except Exception as e:
        print(f"獲取背包資料錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'獲取背包資料失敗: {str(e)}'
        })

@bylin.route('/use-item', methods=['POST'])
@login_required
def use_item():
    """使用道具的API"""
    try:
        data = request.get_json()
        item_type = data.get('type')
        item_key = data.get('key')
        
        if not item_type or not item_key:
            return jsonify({'success': False, 'message': '缺少必要參數'})
        
        # 獲取使用者ID
        user_id = session.get('user', {}).get('uid')
        if not user_id:
            return jsonify({'success': False, 'message': '使用者未登入'})
        
        # 初始化 Firestore 客戶端
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
          # 轉換道具鍵名以符合 Firebase 格式
        firebase_key = item_key
        if item_type == 'potion':
            firebase_key = f"{item_key}_potion"
        
        # 獲取當前道具數量
        item_ref = db.collection('users').document(user_id).collection('user_backpack').document(firebase_key)
        item_doc = item_ref.get()
        
        if not item_doc.exists:
            return jsonify({'success': False, 'message': '道具不存在'})
        
        current_count = item_doc.to_dict().get('count', 0)
        
        if current_count <= 0:
            return jsonify({'success': False, 'message': '道具數量不足'})
        
        # 減少道具數量
        new_count = current_count - 1
        item_ref.update({'count': new_count})
        
        return jsonify({
            'success': True,
            'message': '道具使用成功',
            'new_count': new_count
        })
        
    except Exception as e:
        print(f"使用道具錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'使用道具時發生錯誤: {str(e)}'
        })

@bylin.route('/magic-circle-details')
@login_required
def magic_circle_details():
    """魔法陣詳情頁面"""
    return render_template('bylin/magic_circle_details.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/potion-details')
@login_required
def potion_details():
    """藥水詳情頁面"""
    return render_template('bylin/potion_details.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/api/magic-circle-data', methods=['GET'])
@login_required
def get_magic_circle_data():
    """獲取魔法陣詳情數據的API"""
    try:
        # 獲取使用者ID
        user_id = session.get('user', {}).get('uid')
        if not user_id:
            return jsonify({'success': False, 'message': '使用者未登入'})
        
        # 初始化 Firestore 客戶端
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        
        # 獲取魔法陣數據
        magic_circle_data = []
        magic_circle_types = ['normal', 'advanced', 'premium']
        
        for mc_type in magic_circle_types:
            # 從背包中獲取數量
            item_ref = db.collection('users').document(user_id).collection('user_backpack').document(mc_type)
            item_doc = item_ref.get()
            count = item_doc.to_dict().get('count', 0) if item_doc.exists else 0
            
            magic_circle_data.append({
                'key': mc_type,
                'count': count
            })
        
        return jsonify({
            'success': True,
            'magic_circles': magic_circle_data
        })
        
    except Exception as e:
        print(f"獲取魔法陣數據錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'獲取魔法陣數據失敗: {str(e)}'
        })

@bylin.route('/api/potion-data', methods=['GET'])
@login_required
def get_potion_data():
    """獲取藥水詳情數據的API"""
    try:
        # 獲取使用者ID
        user_id = session.get('user', {}).get('uid')
        if not user_id:
            return jsonify({'success': False, 'message': '使用者未登入'})
        
        # 初始化 Firestore 客戶端
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        
        # 獲取藥水數據
        potion_data = []
        potion_types = ['normal', 'advanced', 'premium']
        
        for potion_type in potion_types:
            # 從背包中獲取數量（Firebase中存儲為 {type}_potion）
            firebase_key = f"{potion_type}_potion"
            item_ref = db.collection('users').document(user_id).collection('user_backpack').document(firebase_key)
            item_doc = item_ref.get()
            count = item_doc.to_dict().get('count', 0) if item_doc.exists else 0
            
            potion_data.append({
                'key': potion_type,
                'count': count
            })
        
        return jsonify({
            'success': True,
            'potions': potion_data
        })
        
    except Exception as e:
        print(f"獲取藥水數據錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'獲取藥水數據失敗: {str(e)}'
        })

@bylin.route('/api/myarena', methods=['GET'])
@login_required
def get_my_arenas():
    """獲取使用者道館和基地資料的API"""
    try:
        # 獲取使用者ID
        user_id = session.get('user', {}).get('uid')
        if not user_id:
            return jsonify({'success': False, 'message': '使用者未登入'})
        
        # 初始化 Firestore 客戶端
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        
        # 獲取使用者的 user_arenas 子集合
        user_arenas_ref = db.collection('users').document(user_id).collection('user_arenas')
        user_arenas_docs = user_arenas_ref.get()
        
        arenas_data = []
        base_gyms_data = []
        
        for doc in user_arenas_docs:
            arena_id = doc.id
            arena_data = doc.to_dict()
              # 檢查是否為基地道館（tutorial-gym 開頭）
            if arena_id.startswith('tutorial-gym'):
                # 獲取完整的基地道館資訊
                try:
                    base_gym_ref = db.collection('user_base_gyms').document(arena_id)
                    base_gym_doc = base_gym_ref.get()
                    if base_gym_doc.exists:
                        base_gym_full_data = base_gym_doc.to_dict()
                        base_gym_full_data['id'] = arena_id
                        base_gym_full_data['user_arena_data'] = arena_data
                        
                        # 為基地道館也計算佔領時間（可用於獎勵計算）
                        occupied_at = arena_data.get('occupied_at')
                        if occupied_at and isinstance(occupied_at, str):
                            from datetime import datetime
                            try:
                                occupied_time = datetime.fromisoformat(occupied_at)
                                time_diff = datetime.now() - occupied_time
                                hours_occupied = int(time_diff.total_seconds() // 3600)
                                base_gym_full_data['hours_occupied'] = hours_occupied
                            except:
                                base_gym_full_data['hours_occupied'] = 0
                        else:
                            base_gym_full_data['hours_occupied'] = 0
                        
                        base_gyms_data.append(base_gym_full_data)
                    else:
                        # 如果在 user_base_gyms 找不到，嘗試從 arenas 集合獲取
                        arena_ref = db.collection('arenas').document(arena_id)
                        arena_doc = arena_ref.get()
                        if arena_doc.exists:
                            base_gym_from_arena = arena_doc.to_dict()
                            base_gym_from_arena['id'] = arena_id
                            base_gym_from_arena['user_arena_data'] = arena_data
                            base_gym_from_arena['is_base_gym'] = True
                            
                            # 計算佔領時間
                            occupied_at = arena_data.get('occupied_at')
                            if occupied_at and isinstance(occupied_at, str):
                                from datetime import datetime
                                try:
                                    occupied_time = datetime.fromisoformat(occupied_at)
                                    time_diff = datetime.now() - occupied_time
                                    hours_occupied = int(time_diff.total_seconds() // 3600)
                                    base_gym_from_arena['hours_occupied'] = hours_occupied
                                except:
                                    base_gym_from_arena['hours_occupied'] = 0
                            else:
                                base_gym_from_arena['hours_occupied'] = 0
                            
                            base_gyms_data.append(base_gym_from_arena)
                        else:
                            # 完全找不到，創建基本資訊
                            base_gym_basic = {
                                'id': arena_id,
                                'arena_name': arena_data.get('arena_name', '基地道館'),
                                'name': arena_data.get('arena_name', '基地道館'),
                                'level': arena_data.get('level', 5),
                                'is_base_gym': True,
                                'user_arena_data': arena_data,
                                'hours_occupied': 0
                            }
                            base_gyms_data.append(base_gym_basic)
                except Exception as e:
                    print(f"獲取基地道館詳細資訊失敗: {e}")
                    # 即使獲取詳細資訊失敗，仍然添加基本資訊
                    base_gym_basic = {
                        'id': arena_id,
                        'arena_name': arena_data.get('arena_name', '基地道館'),
                        'name': arena_data.get('arena_name', '基地道館'),
                        'level': arena_data.get('level', 5),
                        'is_base_gym': True,
                        'user_arena_data': arena_data,
                        'hours_occupied': 0
                    }
                    base_gyms_data.append(base_gym_basic)
            else:
                # 普通道館，獲取完整道館資訊
                try:
                    arena_ref = db.collection('arenas').document(arena_id)
                    arena_doc = arena_ref.get()
                    if arena_doc.exists:
                        arena_full_data = arena_doc.to_dict()
                        arena_full_data['id'] = arena_id
                        arena_full_data['user_arena_data'] = arena_data
                        
                        # 計算獎勵時間
                        occupied_at = arena_data.get('occupied_at')
                        if occupied_at and isinstance(occupied_at, str):
                            from datetime import datetime
                            try:
                                occupied_time = datetime.fromisoformat(occupied_at)
                                time_diff = datetime.now() - occupied_time
                                hours_occupied = int(time_diff.total_seconds() // 3600)
                                arena_full_data['hours_occupied'] = hours_occupied
                            except:
                                arena_full_data['hours_occupied'] = 0
                        else:
                            arena_full_data['hours_occupied'] = 0
                        
                        arenas_data.append(arena_full_data)
                except Exception as e:
                    print(f"獲取道館詳細資訊失敗: {e}")
                    # 即使獲取詳細資訊失敗，仍然添加基本資訊
                    arena_basic = {
                        'id': arena_id,
                        'name': arena_data.get('arena_name', '未知道館'),
                        'level': arena_data.get('level', 1),
                        'user_arena_data': arena_data,
                        'hours_occupied': 0
                    }
                    arenas_data.append(arena_basic)
        
        return jsonify({
            'success': True,
            'arenas': arenas_data,
            'base_gyms': base_gyms_data,
            'total_arenas': len(arenas_data),
            'total_base_gyms': len(base_gyms_data)
        })
        
    except Exception as e:
        print(f"獲取道館資料錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'獲取道館資料失敗: {str(e)}'
        })

@bylin.route('/api/collect-arena-rewards', methods=['POST'])
@login_required
def collect_arena_rewards():
    """收集道館獎勵的API"""
    try:
        data = request.get_json()
        arena_id = data.get('arena_id')
        
        if not arena_id:
            return jsonify({'success': False, 'message': '缺少道館ID'})
        
        # 獲取使用者ID
        user_id = session.get('user', {}).get('uid')
        if not user_id:
            return jsonify({'success': False, 'message': '使用者未登入'})
        
        # 初始化 Firestore 客戶端
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        
        # 檢查道館擁有權
        user_arena_ref = db.collection('users').document(user_id).collection('user_arenas').document(arena_id)
        user_arena_doc = user_arena_ref.get()
        
        if not user_arena_doc.exists:
            return jsonify({'success': False, 'message': '您未擁有此道館'})
        
        user_arena_data = user_arena_doc.to_dict()
        occupied_at = user_arena_data.get('occupied_at')
        
        if not occupied_at:
            return jsonify({'success': False, 'message': '道館資料異常'})
        
        # 計算可收集的獎勵
        from datetime import datetime
        try:
            if isinstance(occupied_at, str):
                occupied_time = datetime.fromisoformat(occupied_at)
            else:
                occupied_time = datetime.fromtimestamp(occupied_at)
            
            # 檢查上次收集時間
            last_collected = user_arena_data.get('last_reward_collected')
            if last_collected:
                if isinstance(last_collected, str):
                    last_collected_time = datetime.fromisoformat(last_collected)
                else:
                    last_collected_time = datetime.fromtimestamp(last_collected)
            else:
                last_collected_time = occupied_time
            
            time_diff = datetime.now() - last_collected_time
            hours_passed = int(time_diff.total_seconds() // 3600)
            
            if hours_passed <= 0:
                return jsonify({'success': False, 'message': '目前沒有可收集的獎勵'})
            
            # 根據道館等級決定獎勵類型
            arena_level = user_arena_data.get('level', 1)
            if arena_level == 1:
                circle_type = 'normal'
            elif arena_level == 2:
                circle_type = 'advanced'
            else:
                circle_type = 'premium'
            
            # 添加獎勵到用戶背包
            backpack_ref = db.collection('users').document(user_id).collection('user_backpack').document(circle_type)
            backpack_doc = backpack_ref.get()
            
            if backpack_doc.exists:
                current_count = backpack_doc.to_dict().get('count', 0)
                new_count = current_count + hours_passed
                backpack_ref.update({'count': new_count})
            else:
                backpack_ref.set({'count': hours_passed})
            
            # 更新最後收集時間
            user_arena_ref.update({
                'last_reward_collected': datetime.now().isoformat()
            })
            
            return jsonify({
                'success': True,
                'message': f'成功收集 {hours_passed} 個 {circle_type} 魔法陣！',
                'rewards': {
                    'type': circle_type,
                    'quantity': hours_passed
                }
            })
            
        except Exception as e:
            print(f"計算獎勵時間失敗: {e}")
            return jsonify({'success': False, 'message': '計算獎勵失敗'})
        
    except Exception as e:
        print(f"收集獎勵錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'收集獎勵失敗: {str(e)}'
        })
