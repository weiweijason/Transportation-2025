from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app.services.firebase_service import FirebaseService
import logging
import uuid
import json
from datetime import datetime
import firebase_admin.firestore

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 創建好友對戰藍圖
friend_fight_bp = Blueprint('friend_fight', __name__, url_prefix='/friend_fight')

# 實例化Firebase服務
firebase_service = FirebaseService()

def get_user_by_player_id(player_id):
    """根據 player_id 查詢用戶文件"""
    try:
        users_ref = firebase_service.firestore_db.collection('users')
        query = users_ref.where('player_id', '==', player_id).limit(1)
        docs = query.get()
        
        if docs:
            doc = docs[0]
            return doc, doc.id
        return None, None
    except Exception as e:
        logger.error(f"根據player_id查詢用戶失敗: {str(e)}")
        return None, None

@friend_fight_bp.route('/choose')
@login_required
def choose_fight():
    """選擇對戰模式頁面"""
    return render_template('friend_fight/choose_fight.html')

@friend_fight_bp.route('/host')
@login_required
def host_fight():
    """創建對戰房間頁面"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('用戶資料不完整，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        # 獲取當前用戶的精靈列表
        user_doc, user_doc_id = get_user_by_player_id(current_player_id)
        if not user_doc:
            flash('找不到用戶資料', 'danger')
            return redirect(url_for('main.home'))
          # 獲取用戶的精靈
        user_creatures_ref = firebase_service.firestore_db.collection('users').document(user_doc_id).collection('user_creatures')
        user_creatures = user_creatures_ref.get()
        
        creatures_list = []
        for creature_doc in user_creatures:
            creature_data = creature_doc.to_dict()
            creatures_list.append({
                'id': creature_doc.id,
                'name': creature_data.get('name', '未知精靈'),
                'element': creature_data.get('type', creature_data.get('element', 'Normal')),
                'power': creature_data.get('power', 100),
                'attack': creature_data.get('attack', creature_data.get('power', 100)),
                'hp': creature_data.get('hp', creature_data.get('power', 100) * 10),
                'image_url': creature_data.get('image_url', '')
            })
        
        return render_template('friend_fight/host_fight.html', creatures=creatures_list)
    
    except Exception as e:
        logger.error(f"載入創建對戰頁面失敗: {str(e)}")
        flash('載入頁面失敗', 'danger')
        return redirect(url_for('main.home'))

@friend_fight_bp.route('/join')
@login_required
def join_fight():
    """加入對戰房間頁面"""
    return render_template('friend_fight/join_fight.html')

@friend_fight_bp.route('/create_room', methods=['POST'])
@login_required
def create_room():
    """創建對戰房間API"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            return jsonify({'success': False, 'message': '用戶資料不完整'})
        
        # 獲取選中的精靈ID
        selected_creature_id = request.json.get('creature_id')
        if not selected_creature_id:
            return jsonify({'success': False, 'message': '請選擇一隻精靈'})
        
        # 獲取當前用戶資料
        user_doc, user_doc_id = get_user_by_player_id(current_player_id)
        if not user_doc:
            return jsonify({'success': False, 'message': '找不到用戶資料'})
        
        user_data = user_doc.to_dict()
        
        # 驗證精靈是否屬於當前用戶
        creature_ref = firebase_service.firestore_db.collection('users').document(user_doc_id).collection('user_creatures').document(selected_creature_id)
        creature_doc = creature_ref.get()
        
        if not creature_doc.exists:
            return jsonify({'success': False, 'message': '精靈不存在或不屬於您'})
        
        creature_data = creature_doc.to_dict()
          # 生成隨機房間ID（8位英文數字組合）
        room_id = str(uuid.uuid4())[:8].upper()
        
        # 在Firebase創建臨時房間
        room_data = {
            'room_id': room_id,
            'host_player_id': current_player_id,
            'host_username': user_data.get('username', '未知用戶'),            'host_creature': {
                'id': selected_creature_id,
                'name': creature_data.get('name'),
                'element': creature_data.get('type', creature_data.get('element', 'Normal')),
                'power': creature_data.get('power'),
                'attack': creature_data.get('attack', creature_data.get('power', 100)),
                'hp': creature_data.get('hp', creature_data.get('health', 1000)),
                'image_url': creature_data.get('image_url', '')
            },
            'visitor_player_id': None,
            'visitor_username': None,
            'visitor_creature': None,
            'status': 'waiting',  # waiting, ready, fighting, finished
            'created_at': firebase_admin.firestore.SERVER_TIMESTAMP,
            'battle_result': None
        }
        
        firebase_service.firestore_db.collection('temp_rooms').document(room_id).set(room_data)
        
        logger.info(f"房間創建成功: {room_id} by {current_player_id}")
        return jsonify({
            'success': True, 
            'room_id': room_id,
            'message': f'房間創建成功！房間ID: {room_id}'
        })
        
    except Exception as e:
        logger.error(f"創建房間失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'創建房間失敗: {str(e)}'})

@friend_fight_bp.route('/join_room', methods=['POST'])
@login_required
def join_room():
    """加入對戰房間API"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            return jsonify({'success': False, 'message': '用戶資料不完整'})
        
        room_id = request.json.get('room_id', '').strip().upper()
        if not room_id:
            return jsonify({'success': False, 'message': '請輸入房間ID'})
        
        # 檢查房間是否存在
        room_ref = firebase_service.firestore_db.collection('temp_rooms').document(room_id)
        room_doc = room_ref.get()
        
        if not room_doc.exists:
            return jsonify({'success': False, 'message': '房間不存在'})
        
        room_data = room_doc.to_dict()
        
        # 檢查房間狀態
        if room_data.get('status') != 'waiting':
            return jsonify({'success': False, 'message': '房間已滿或已結束'})
        
        # 檢查是否是房主自己
        if room_data.get('host_player_id') == current_player_id:
            return jsonify({'success': False, 'message': '不能加入自己創建的房間'})
          # 獲取加入者的精靈列表
        user_doc, user_doc_id = get_user_by_player_id(current_player_id)
        if not user_doc:
            return jsonify({'success': False, 'message': '找不到用戶資料'})
        
        user_creatures_ref = firebase_service.firestore_db.collection('users').document(user_doc_id).collection('user_creatures')
        user_creatures = user_creatures_ref.get()
        
        creatures_list = []
        for creature_doc in user_creatures:
            creature_data = creature_doc.to_dict()
            creatures_list.append({
                'id': creature_doc.id,
                'name': creature_data.get('name', '未知精靈'),
                'element': creature_data.get('element', 'Normal'),
                'power': creature_data.get('power', 100),
                'image_url': creature_data.get('image_url', '')
            })
        
        return jsonify({
            'success': True,
            'room_data': room_data,
            'creatures': creatures_list,
            'message': '找到房間，請選擇精靈'
        })
        
    except Exception as e:
        logger.error(f"加入房間失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'加入房間失敗: {str(e)}'})

@friend_fight_bp.route('/visitor_fight/<room_id>')
@login_required
def visitor_fight(room_id):
    """對戰頁面（房主和訪客共用）"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('用戶資料不完整，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        # 檢查房間是否存在
        room_ref = firebase_service.firestore_db.collection('temp_rooms').document(room_id)
        room_doc = room_ref.get()
        
        if not room_doc.exists:
            flash('房間不存在', 'danger')
            return redirect(url_for('friend_fight.join_fight'))
        
        room_data = room_doc.to_dict()
        
        # 檢查是否是房主或訪客
        if (room_data.get('visitor_player_id') != current_player_id and 
            room_data.get('host_player_id') != current_player_id):
            flash('無權訪問此房間', 'danger')
            return redirect(url_for('friend_fight.join_fight'))
        
        # 判斷當前用戶角色
        user_role = 'host' if room_data.get('host_player_id') == current_player_id else 'visitor'
        
        return render_template('friend_fight/visitor_fight.html', 
                             room_data=room_data, 
                             room_id=room_id,
                             user_role=user_role)
    
    except Exception as e:
        logger.error(f"載入對戰頁面失敗: {str(e)}")
        flash('載入頁面失敗', 'danger')
        return redirect(url_for('friend_fight.join_fight'))

@friend_fight_bp.route('/confirm_join', methods=['POST'])
@login_required
def confirm_join():
    """確認加入房間並選擇精靈"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            return jsonify({'success': False, 'message': '用戶資料不完整'})
        
        room_id = request.json.get('room_id')
        selected_creature_id = request.json.get('creature_id')
        
        if not room_id or not selected_creature_id:
            return jsonify({'success': False, 'message': '缺少必要參數'})
        
        # 獲取當前用戶資料
        user_doc, user_doc_id = get_user_by_player_id(current_player_id)
        if not user_doc:
            return jsonify({'success': False, 'message': '找不到用戶資料'})
        
        user_data = user_doc.to_dict()
        
        # 驗證精靈是否屬於當前用戶
        creature_ref = firebase_service.firestore_db.collection('users').document(user_doc_id).collection('user_creatures').document(selected_creature_id)
        creature_doc = creature_ref.get()
        
        if not creature_doc.exists:
            return jsonify({'success': False, 'message': '精靈不存在或不屬於您'})
        
        creature_data = creature_doc.to_dict()
        
        # 更新房間資料
        room_ref = firebase_service.firestore_db.collection('temp_rooms').document(room_id)
        room_ref.update({
            'visitor_player_id': current_player_id,
            'visitor_username': user_data.get('username', '未知用戶'),            'visitor_creature': {
                'id': selected_creature_id,
                'name': creature_data.get('name'),
                'element': creature_data.get('type', creature_data.get('element', 'Normal')),
                'power': creature_data.get('power'),
                'attack': creature_data.get('attack', creature_data.get('power', 100)),
                'hp': creature_data.get('hp', creature_data.get('health', 1000)),
                'image_url': creature_data.get('image_url', '')
            },
            'status': 'ready'
        })
        
        logger.info(f"用戶 {current_player_id} 成功加入房間 {room_id}")
        return jsonify({
            'success': True,
            'redirect_url': url_for('friend_fight.visitor_fight', room_id=room_id),
            'message': '成功加入房間'
        })
        
    except Exception as e:
        logger.error(f"確認加入房間失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'加入房間失敗: {str(e)}'})

@friend_fight_bp.route('/start_battle', methods=['POST'])
@login_required
def start_battle():
    """開始戰鬥"""
    try:
        current_player_id = current_user.player_id
        room_id = request.json.get('room_id')
        
        if not room_id:
            return jsonify({'success': False, 'message': '缺少房間ID'})
        
        # 檢查房間狀態
        room_ref = firebase_service.firestore_db.collection('temp_rooms').document(room_id)
        room_doc = room_ref.get()
        
        if not room_doc.exists:
            return jsonify({'success': False, 'message': '房間不存在'})
        
        room_data = room_doc.to_dict()
        
        # 只有房主可以開始戰鬥
        if room_data.get('host_player_id') != current_player_id:
            return jsonify({'success': False, 'message': '只有房主可以開始戰鬥'})
        
        # 檢查是否雙方都準備好
        if room_data.get('status') != 'ready':
            return jsonify({'success': False, 'message': '等待對方加入'})
        
        # 執行戰鬥計算
        host_creature = room_data.get('host_creature')
        visitor_creature = room_data.get('visitor_creature')
        
        # 導入戰鬥系統
        from app.models.fight import calculate_battle
        
        battle_result = calculate_battle(host_creature, visitor_creature)
          # 更新房間狀態
        room_ref.update({
            'status': 'finished',
            'battle_result': battle_result,
            'finished_at': firebase_admin.firestore.SERVER_TIMESTAMP
        })
        
        # 5分鐘後自動清理房間
        import threading
        def cleanup_room():
            import time
            time.sleep(300)  # 等待5分鐘
            try:
                room_doc = room_ref.get()
                if room_doc.exists:
                    room_ref.delete()
                    logger.info(f"房間 {room_id} 已自動清理")
            except Exception as e:
                logger.error(f"自動清理房間 {room_id} 失敗: {str(e)}")
        
        cleanup_thread = threading.Thread(target=cleanup_room)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        logger.info(f"房間 {room_id} 戰鬥完成，結果: {battle_result}")
        return jsonify({
            'success': True,
            'battle_result': battle_result,
            'message': '戰鬥完成'
        })
        
    except Exception as e:
        logger.error(f"開始戰鬥失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'戰鬥失敗: {str(e)}'})

@friend_fight_bp.route('/room_status/<room_id>')
@login_required
def room_status(room_id):
    """獲取房間狀態"""
    try:
        room_ref = firebase_service.firestore_db.collection('temp_rooms').document(room_id)
        room_doc = room_ref.get()
        
        if not room_doc.exists:
            return jsonify({'success': False, 'message': '房間不存在'})
        
        room_data = room_doc.to_dict()
        return jsonify({'success': True, 'room_data': room_data})
        
    except Exception as e:
        logger.error(f"獲取房間狀態失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'獲取狀態失敗: {str(e)}'})

@friend_fight_bp.route('/delete_room/<room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    """刪除房間（房主專用）"""
    try:
        current_player_id = current_user.player_id
        
        # 檢查房間是否存在且用戶是房主
        room_ref = firebase_service.firestore_db.collection('temp_rooms').document(room_id)
        room_doc = room_ref.get()
        
        if not room_doc.exists:
            return jsonify({'success': False, 'message': '房間不存在'})
        
        room_data = room_doc.to_dict()
        
        if room_data.get('host_player_id') != current_player_id:
            return jsonify({'success': False, 'message': '只有房主可以刪除房間'})
        
        # 刪除房間
        room_ref.delete()
        
        logger.info(f"房間 {room_id} 已被房主 {current_player_id} 刪除")
        return jsonify({'success': True, 'message': '房間已刪除'})
        
    except Exception as e:
        logger.error(f"刪除房間失敗: {str(e)}")
        return jsonify({'success': False, 'message': f'刪除房間失敗: {str(e)}'})
