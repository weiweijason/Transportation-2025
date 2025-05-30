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

def get_user_by_player_id(player_id):
    """根據 player_id 查詢用戶文件"""
    users_query = firebase_service.firestore_db.collection('users').where('player_id', '==', player_id).limit(1).get()
    if users_query:
        return users_query[0], users_query[0].id
    return None, None

@community_bp.route('/friends')
@login_required
def friends():
    """顯示好友頁面"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('用戶資料不完整，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        # 獲取當前用戶的資料（根據 player_id 查詢）
        user_doc, user_doc_id = get_user_by_player_id(current_player_id)
        
        if not user_doc:
            flash('找不到用戶資料，請重新登錄', 'danger')
            return redirect(url_for('auth.login'))
        
        friends_list = []
        friend_requests_list = []
        
        user_data = user_doc.to_dict()
        
        # 處理好友列表（從好友子集合查詢）
        friends_refs = firebase_service.firestore_db.collection('users').document(user_doc_id).collection('friends').get()
        for friend_ref in friends_refs:
            friend_data_from_collection = friend_ref.to_dict()
            friend_player_id = friend_data_from_collection.get('friend_player_id')
            friend_username = friend_data_from_collection.get('friend_username', '未知用戶')
            friends_list.append({
                'player_id': friend_player_id,
                'username': friend_username,
                'online': False  # TODO: 實現線上狀態檢查
            })
        
        # 處理好友申請列表（從 friends_pending 子集合查詢）
        pending_requests = firebase_service.firestore_db.collection('users').document(user_doc_id).collection('friends_pending').get()
        for pending_doc in pending_requests:
            pending_data = pending_doc.to_dict()
            requester_player_id = pending_data.get('requester_player_id')
            if requester_player_id:
                requester_doc, _ = get_user_by_player_id(requester_player_id)
                if requester_doc:
                    requester_data = requester_doc.to_dict()
                    friend_requests_list.append({
                        'player_id': requester_player_id,
                        'username': requester_data.get('username', '未知用戶'),
                        'requested_at': pending_data.get('requested_at'),
                        'request_id': pending_doc.id
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
        
        # 搜尋目標用戶（根據 player_id 欄位查詢）
        logger.info(f"搜尋目標用戶: {friend_invite_code}")
        target_user_doc, target_user_doc_id = get_user_by_player_id(friend_invite_code)
        
        if not target_user_doc:
            logger.warning(f"目標用戶不存在: {friend_invite_code}")
            flash('找不到該邀請碼對應的用戶', 'danger')
            return redirect(url_for('community.friends'))
        
        # 獲取當前用戶資料（根據 player_id 查詢）
        logger.info(f"獲取申請者資料: {current_player_id}")
        current_user_doc, current_user_doc_id = get_user_by_player_id(current_player_id)
        
        if not current_user_doc:
            logger.warning(f"申請者資料不存在: {current_player_id}")
            flash('當前用戶資料異常', 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        target_user_data = target_user_doc.to_dict()
        
        logger.info(f"目標用戶名稱: {target_user_data.get('username', '未知用戶')}")
        
        # 檢查是否已經是好友（檢查 friends 子集合）
        existing_friend = firebase_service.firestore_db.collection('users').document(current_user_doc_id)\
            .collection('friends').document(friend_invite_code).get()
        
        if existing_friend.exists:
            logger.warning(f"已經是好友: {friend_invite_code}")
            flash('該用戶已經是您的好友', 'warning')
            return redirect(url_for('community.friends'))
        
        # 檢查是否已經發送過申請（檢查 friends_pending 子集合）
        existing_request = firebase_service.firestore_db.collection('users').document(target_user_doc_id)\
            .collection('friends_pending').where('requester_player_id', '==', current_player_id).limit(1).get()
        
        if existing_request:
            logger.warning(f"已經發送過申請: {current_player_id} -> {friend_invite_code}")
            flash('已經向該用戶發送過好友申請', 'warning')
            return redirect(url_for('community.friends'))
        
        # 在目標用戶的 friends_pending 子集合中新增申請
        from datetime import datetime
        import firebase_admin.firestore
        
        logger.info(f"添加到待處理子集合: {current_player_id} -> {friend_invite_code}")
        firebase_service.firestore_db.collection('users').document(target_user_doc_id)\
            .collection('friends_pending').add({
                'requester_player_id': current_player_id,
                'requester_username': current_user_data.get('username', '未知用戶'),
                'requested_at': firebase_admin.firestore.SERVER_TIMESTAMP,
                'status': 'pending'
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
        current_user_doc, current_user_doc_id = get_user_by_player_id(current_player_id)
        if not current_user_doc:
            flash('當前用戶資料異常', 'danger')
            return redirect(url_for('community.friends'))
        
        # 獲取好友資料
        friend_doc, friend_doc_id = get_user_by_player_id(friend_id)
        if not friend_doc:
            flash('好友資料不存在', 'danger')
            return redirect(url_for('community.friends'))
        
        # 從雙方的好友子集合中移除
        firebase_service.firestore_db.collection('users').document(current_user_doc_id)\
            .collection('friends').document(friend_id).delete()
        
        firebase_service.firestore_db.collection('users').document(friend_doc_id)\
            .collection('friends').document(current_player_id).delete()
        
        friend_data = friend_doc.to_dict()
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
        current_user_doc, current_user_doc_id = get_user_by_player_id(current_player_id)
        if not current_user_doc:
            flash('當前用戶資料異常', 'danger')
            return redirect(url_for('community.friends'))
        
        # 檢查好友申請是否存在（從子集合中獲取）
        request_doc_ref = firebase_service.firestore_db.collection('users').document(current_user_doc_id)\
            .collection('friends_pending').document(request_id)
        request_doc = request_doc_ref.get()
        
        if not request_doc.exists:
            flash('找不到該好友申請', 'danger')
            return redirect(url_for('community.friends'))
        
        request_data = request_doc.to_dict()
        requester_player_id = request_data.get('requester_player_id')
        
        # 獲取申請者資料
        requester_doc, requester_doc_id = get_user_by_player_id(requester_player_id)
        if not requester_doc:
            flash('申請者資料不存在', 'danger')
            return redirect(url_for('community.friends'))
        
        requester_data = requester_doc.to_dict()
        current_user_data = current_user_doc.to_dict()
        
        # 雙方互相在好友子集合中加為好友
        from datetime import datetime
        import firebase_admin.firestore
        
        # 在當前用戶的 friends 子集合中加入好友
        firebase_service.firestore_db.collection('users').document(current_user_doc_id)\
            .collection('friends').document(requester_player_id).set({
                'friend_player_id': requester_player_id,
                'friend_username': requester_data.get('username', '未知用戶'),
                'added_at': firebase_admin.firestore.SERVER_TIMESTAMP,
                'status': 'active'
            })
        
        # 在申請者的 friends 子集合中加入好友
        firebase_service.firestore_db.collection('users').document(requester_doc_id)\
            .collection('friends').document(current_player_id).set({
                'friend_player_id': current_player_id,
                'friend_username': current_user_data.get('username', '未知用戶'),
                'added_at': firebase_admin.firestore.SERVER_TIMESTAMP,
                'status': 'active'
            })
        
        # 刪除好友申請記錄（從子集合中移除）
        request_doc_ref.delete()
        
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
        current_user_doc, current_user_doc_id = get_user_by_player_id(current_player_id)
        if not current_user_doc:
            flash('當前用戶資料異常', 'danger')
            return redirect(url_for('community.friends'))
        
        # 檢查好友申請是否存在（從子集合中獲取）
        request_doc_ref = firebase_service.firestore_db.collection('users').document(current_user_doc_id)\
            .collection('friends_pending').document(request_id)
        request_doc = request_doc_ref.get()
        
        if not request_doc.exists:
            flash('找不到該好友申請', 'danger')
            return redirect(url_for('community.friends'))
        
        # 移除申請記錄（刪除子集合中的文件）
        request_doc_ref.delete()
        
        flash('已拒絕好友申請', 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        flash(f'拒絕好友申請失敗: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))
