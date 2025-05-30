from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.firebase_service import FirebaseService
import logging

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ?�建社群?��?
community_bp = Blueprint('community', __name__, url_prefix='/community')

# 實�??�Firebase?��?
firebase_service = FirebaseService()

@community_bp.route('/friends')
@login_required
def friends():
    """顯示好�??�面"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('?�戶資�?不�??��?請�??�登??, 'danger')
            return redirect(url_for('auth.login'))
        
        # ?��??��??�戶?��???
        user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        
        friends_list = []
        friend_requests_list = []
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            
            # ?��?好�??�表
            friends_ids = user_data.get('friends', [])
            for friend_id in friends_ids:
                friend_doc = firebase_service.firestore_db.collection('users').document(friend_id).get()
                if friend_doc.exists:
                    friend_data = friend_doc.to_dict()
                    friends_list.append({
                        'player_id': friend_id,
                        'username': friend_data.get('username', '?�知?�戶'),
                        'online': False  # TODO: 實現線�??�?�檢??
                    })
            
            # ?��?好�??��??�表
            friends_pending = user_data.get('friends_pending', [])
            for pending_id in friends_pending:
                pending_doc = firebase_service.firestore_db.collection('users').document(pending_id).get()
                if pending_doc.exists:
                    pending_data = pending_doc.to_dict()
                    friend_requests_list.append({
                        'player_id': pending_id,
                        'username': pending_data.get('username', '?�知?�戶')
                    })
        
        return render_template('community/friends.html', 
                             friends=friends_list, 
                             friend_requests=friend_requests_list)
    except Exception as e:
        flash(f'載入好�??�面失�?: {str(e)}', 'danger')
        return redirect(url_for('main.home'))

@community_bp.route('/add-friend', methods=['POST'])
@login_required
def add_friend():
    """?��?好�??��?"""
    try:
        friend_invite_code = request.form.get('friend_invite_code', '').strip()
        current_player_id = current_user.player_id
        
        if not friend_invite_code:
            flash('請輸?�好?��?請碼', 'danger')
            return redirect(url_for('community.friends'))
        
        if not current_player_id:
            flash('?�戶資�?不�??��?請�??�登??, 'danger')
            return redirect(url_for('auth.login'))
        
        # 檢查?�否?�自己�??�請碼
        if friend_invite_code == current_player_id:
            flash('不能?��??�己?�好??, 'danger')
            return redirect(url_for('community.friends'))
        
        # ?��??��??�戶
        target_user_doc = firebase_service.firestore_db.collection('users').document(friend_invite_code).get()
        if not target_user_doc.exists:
            flash('?��??�該?�請碼對�??�用??, 'danger')
            return redirect(url_for('community.friends'))
        
        # ?��??��??�戶資�?
        current_user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        if not current_user_doc.exists:
            flash('?��??�戶資�??�常', 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        target_user_data = target_user_doc.to_dict()
        
        # 檢查?�否已�??�好??
        current_friends = current_user_data.get('friends', [])
        if friend_invite_code in current_friends:
            flash('該用?�已經是?��?好�?', 'warning')
            return redirect(url_for('community.friends'))
        
        # 檢查?�否已�??�送�??��?
        target_pending = target_user_data.get('friends_pending', [])
        if current_player_id in target_pending:
            flash('已�??�該?�戶?�送�?好�??��?', 'warning')
            return redirect(url_for('community.friends'))
        
        # 將當?�用?�ID?�入?��??�戶?�friends_pending?�表
        target_pending.append(current_player_id)
        firebase_service.firestore_db.collection('users').document(friend_invite_code).update({
            'friends_pending': target_pending
        })
        
        target_username = target_user_data.get('username', '?�知?�戶')
        flash(f'已�? {target_username} ?�送好?�申�?, 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        flash(f'?��?好�?失�?: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))

@community_bp.route('/remove-friend/<friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    """移除好�?"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('?�戶資�?不�??��?請�??�登??, 'danger')
            return redirect(url_for('auth.login'))
        
        # ?��??��??�戶資�?
        current_user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        if not current_user_doc.exists:
            flash('?��??�戶資�??�常', 'danger')
            return redirect(url_for('community.friends'))
        
        # ?��?好�?資�?
        friend_doc = firebase_service.firestore_db.collection('users').document(friend_id).get()
        if not friend_doc.exists:
            flash('好�?資�?不�???, 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        friend_data = friend_doc.to_dict()
        
        # 從�??�好?��?表中移除
        current_friends = current_user_data.get('friends', [])
        friend_friends = friend_data.get('friends', [])
        
        if friend_id in current_friends:
            current_friends.remove(friend_id)
        if current_player_id in friend_friends:
            friend_friends.remove(current_player_id)
        
        # ?�新?�方資�?
        firebase_service.firestore_db.collection('users').document(current_player_id).update({
            'friends': current_friends
        })
        
        firebase_service.firestore_db.collection('users').document(friend_id).update({
            'friends': friend_friends
        })
        
        friend_username = friend_data.get('username', '?�知?�戶')
        flash(f'已移?�好??{friend_username}', 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        flash(f'移除好�?失�?: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))

@community_bp.route('/accept-request/<request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    """?��?好�??��?"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('?�戶資�?不�??��?請�??�登??, 'danger')
            return redirect(url_for('auth.login'))
        
        # ?��??��??�戶資�?
        current_user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        if not current_user_doc.exists:
            flash('?��??�戶資�??�常', 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        friends_pending = current_user_data.get('friends_pending', [])
        
        # 檢查?��??�否存在
        if request_id not in friends_pending:
            flash('?��??�該好�??��?', 'danger')
            return redirect(url_for('community.friends'))
        
        # ?��??��??��???
        requester_doc = firebase_service.firestore_db.collection('users').document(request_id).get()
        if not requester_doc.exists:
            flash('?��??��??��?存在', 'danger')
            return redirect(url_for('community.friends'))
        
        requester_data = requester_doc.to_dict()
        
        # 移除?��?記�?
        friends_pending.remove(request_id)
        
        # ?�方互相?�為好�?
        current_friends = current_user_data.get('friends', [])
        requester_friends = requester_data.get('friends', [])
        
        if request_id not in current_friends:
            current_friends.append(request_id)
        if current_player_id not in requester_friends:
            requester_friends.append(current_player_id)
        
        # ?�新?��??�戶資�?
        firebase_service.firestore_db.collection('users').document(current_player_id).update({
            'friends_pending': friends_pending,
            'friends': current_friends
        })
        
        # ?�新?��??��???
        firebase_service.firestore_db.collection('users').document(request_id).update({
            'friends': requester_friends
        })
        
        requester_username = requester_data.get('username', '?�知?�戶')
        flash(f'已接??{requester_username} ?�好?�申�?, 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        flash(f'?��?好�??��?失�?: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))

@community_bp.route('/decline-request/<request_id>', methods=['POST'])
@login_required
def decline_request(request_id):
    """?��?好�??��?"""
    try:
        current_player_id = current_user.player_id
        if not current_player_id:
            flash('?�戶資�?不�??��?請�??�登??, 'danger')
            return redirect(url_for('auth.login'))
        
        # ?��??��??�戶資�?
        current_user_doc = firebase_service.firestore_db.collection('users').document(current_player_id).get()
        if not current_user_doc.exists:
            flash('?��??�戶資�??�常', 'danger')
            return redirect(url_for('community.friends'))
        
        current_user_data = current_user_doc.to_dict()
        friends_pending = current_user_data.get('friends_pending', [])
        
        # 檢查?��??�否存在
        if request_id not in friends_pending:
            flash('?��??�該好�??��?', 'danger')
            return redirect(url_for('community.friends'))
        
        # 移除?��?記�?
        friends_pending.remove(request_id)
        
        # ?�新?�戶資�?
        firebase_service.firestore_db.collection('users').document(current_player_id).update({
            'friends_pending': friends_pending
        })
        
        flash('已�?絕好?�申�?, 'success')
        return redirect(url_for('community.friends'))
        
    except Exception as e:
        flash(f'?��?好�??��?失�?: {str(e)}', 'danger')
        return redirect(url_for('community.friends'))
