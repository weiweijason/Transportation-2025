from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.firebase_service import FirebaseService
import logging

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 創建社群藍圖
community_bp = Blueprint('community', __name__, url_prefix='/community')

# 實例化Firebase服務
firebase_service = FirebaseService()

@community_bp.route('/friends')
@login_required
def friends():
    """顯示好友頁面"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('用戶資料不完整，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        # 獲取當前用戶的資料
        user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        
        friends_list = []
        friend_requests_list = []
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            
            # 處理好友列表
            friends_ids = user_data.get('friends', [])
            for friend_id in friends_ids:
                friend_doc = firebase_service.firestore_db.collection('users').document(friend_id).get()
                if friend_doc.exists:
                    friend_data = friend_doc.to_dict()
                    friends_list.append({
                        'player_id': friend_id,
                        'username': friend_data.get('username', '未知用戶'),
                        'online': False  # TODO: 實現線上狀態檢查
                    })
            
            # 處理好友申請列表
            friends_pending = user_data.get('friends_pending', [])
            for pending_id in friends_pending:
                pending_doc = firebase_service.firestore_db.collection('users').document(pending_id).get()
                if pending_doc.exists:
                    pending_data = pending_doc.to_dict()
                    friend_requests_list.append({
                        'player_id': pending_id,
                        'username': pending_data.get('username', '未知用戶')
                    })
        
        return render_template('community/friends.html', 
                             friends=friends_list, 
                             friend_requests=friend_requests_list)
    except Exception as e:
        flash(f'載入好友頁面失敗: {str(e)}', 'danger')
        return redirect(url_for('main.home'))

@community_bp.route('/add-friend', methods=['POST'])
@login_required
def add_friend():
    """新增好友申請"""
    logger.info("=== 開始處理好友申請 ===")
    try:
        friend_invite_code = request.form.get('friend_invite_code', '').strip()
        current_player_id = current_user.player_id
        
        logger.info(f"申請者ID: {current_player_id}")
        logger.info(f"目標邀請碼: {friend_invite_code}")
        
        if not friend_invite_code:
            logger.warning("邀請碼為空")
            flash('請輸入好友邀請碼', 'danger')
            return redirect(url_for('community.friends'))
        
        if not current_player_id:
            logger.warning("申請者ID為空")
            flash('用戶資料不完整，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        # 檢查是否為自己的邀請碼
        if friend_invite_code == current_player_id:
            logger.warning("嘗試添加自己為好友")
            flash('不能新增自己為好友', 'danger')
            return redirect(url_for('community.friends'))
        
        # 搜尋目標用戶
        logger.info(f"搜尋目標用戶: {friend_invite_code}")
        target_user_doc = firebase_service.firestore_db.collection('users').document(friend_invite_code).get()
        if not target_user_doc.exists:
            logger.warning(f"目標用戶不存在: {friend_invite_code}")
            flash('找不到該邀請碼對應的用戶', 'danger')
            return redirect(url_for('community.friends'))
        
        # 獲取當前用戶資料
        logger.info(f"獲取申請者資料: {current_player_id}")
        current_user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        if not current_user_doc.exists:
            logger.warning(f"申請者資料不存在: {current_player_id}")
            flash('當前用戶資料異常', 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        target_user_data = target_user_doc.to_dict()
        
        logger.info(f"目標用戶名稱: {target_user_data.get('username', '未知用戶')}")
        
        # 檢查是否已經是好友
        current_friends = current_user_data.get('friends', [])
        if friend_invite_code in current_friends:
            logger.warning(f"已經是好友: {friend_invite_code}")
            flash('該用戶已經是您的好友', 'warning')
            return redirect(url_for('community.friends'))
        
        # 檢查是否已經發送過申請
        target_pending = target_user_data.get('friends_pending', [])
        if current_player_id in target_pending:
            logger.warning(f"已經發送過申請: {current_player_id} -> {friend_invite_code}")
            flash('已經向該用戶發送過好友申請', 'warning')
            return redirect(url_for('community.friends'))
        
        # 將當前用戶ID加入目標用戶的friends_pending列表
        logger.info(f"添加到待處理列表: {current_player_id} -> {friend_invite_code}")
        target_pending.append(current_player_id)
        
        logger.info(f"更新目標用戶待處理列表: {target_pending}")
        firebase_service.firestore_db.collection('users').document(friend_invite_code).update({
            'friends_pending': target_pending
        })
        
        target_username = target_user_data.get('username', '未知用戶')
        logger.info(f"好友申請發送成功: {current_player_id} -> {friend_invite_code} ({target_username})")
        flash(f'已向 {target_username} 發送好友申請', 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        logger.error(f"好友申請失敗: {str(e)}", exc_info=True)
        flash(f'新增好友失敗: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))

@community_bp.route('/remove-friend/<friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    """移除好友"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('用戶資料不完整，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        # 獲取當前用戶資料
        current_user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        if not current_user_doc.exists:
            flash('當前用戶資料異常', 'danger')
            return redirect(url_for('community.friends'))
        
        # 獲取好友資料
        friend_doc = firebase_service.firestore_db.collection('users').document(friend_id).get()
        if not friend_doc.exists:
            flash('好友資料不存在', 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        friend_data = friend_doc.to_dict()
        
        # 從雙方好友列表中移除
        current_friends = current_user_data.get('friends', [])
        friend_friends = friend_data.get('friends', [])
        
        if friend_id in current_friends:
            current_friends.remove(friend_id)
        if current_player_id in friend_friends:
            friend_friends.remove(current_player_id)
        
        # 更新雙方資料
        firebase_service.firestore_db.collection('users').document(current_player_id).update({
            'friends': current_friends
        })
        
        firebase_service.firestore_db.collection('users').document(friend_id).update({
            'friends': friend_friends
        })
        
        friend_username = friend_data.get('username', '未知用戶')
        flash(f'已移除好友 {friend_username}', 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        flash(f'移除好友失敗: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))

@community_bp.route('/accept-request/<request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    """接受好友申請"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('用戶資料不完整，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        # 獲取當前用戶資料
        current_user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        if not current_user_doc.exists:
            flash('當前用戶資料異常', 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        friends_pending = current_user_data.get('friends_pending', [])
        
        # 檢查申請是否存在
        if request_id not in friends_pending:
            flash('找不到該好友申請', 'danger')
            return redirect(url_for('community.friends'))
        
        # 獲取申請者資料
        requester_doc = firebase_service.firestore_db.collection('users').document(request_id).get()
        if not requester_doc.exists:
            flash('申請者資料不存在', 'danger')
            return redirect(url_for('community.friends'))
        
        requester_data = requester_doc.to_dict()
        
        # 移除申請記錄
        friends_pending.remove(request_id)
        
        # 雙方互相加為好友
        current_friends = current_user_data.get('friends', [])
        requester_friends = requester_data.get('friends', [])
        
        if request_id not in current_friends:
            current_friends.append(request_id)
        if current_player_id not in requester_friends:
            requester_friends.append(current_player_id)
        
        # 更新當前用戶資料
        firebase_service.firestore_db.collection('users').document(current_player_id).update({
            'friends_pending': friends_pending,
            'friends': current_friends
        })
        
        # 更新申請者資料
        firebase_service.firestore_db.collection('users').document(request_id).update({
            'friends': requester_friends
        })
        
        requester_username = requester_data.get('username', '未知用戶')
        flash(f'已接受 {requester_username} 的好友申請', 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        flash(f'接受好友申請失敗: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))

@community_bp.route('/decline-request/<request_id>', methods=['POST'])
@login_required
def decline_request(request_id):
    """拒絕好友申請"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('用戶資料不完整，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        # 獲取當前用戶資料
        current_user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        if not current_user_doc.exists:
            flash('當前用戶資料異常', 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        friends_pending = current_user_data.get('friends_pending', [])
        
        # 檢查申請是否存在
        if request_id not in friends_pending:
            flash('找不到該好友申請', 'danger')
            return redirect(url_for('community.friends'))
        
        # 移除申請記錄
        friends_pending.remove(request_id)
        
        # 更新用戶資料
        firebase_service.firestore_db.collection('users').document(current_player_id).update({
            'friends_pending': friends_pending
        })
        
        flash('已拒絕好友申請', 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        flash(f'拒絕好友申請失敗: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))
