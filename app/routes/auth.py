from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.services.firebase_service import FirebaseService, FirebaseUser
import time  # 新增這個導入，用於記錄登入時間戳

# 創建認證藍圖
auth = Blueprint('auth', __name__)

# 實例化Firebase服務
firebase_service = FirebaseService()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """處理用戶登入"""
    # 如果用戶已登入，重定向到主頁
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 處理POST請求（用戶提交登入表單）
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 驗證表單數據
        if not email or not password:
            flash('請填寫完整的登入資訊', 'danger')
            return render_template('auth/login.html')
        
        # 嘗試登入
        result = firebase_service.login_user(email, password)
        
        if result['status'] == 'success':
            # 登入成功，儲存用戶信息到會話
            flask_user = result['flask_user']
            
            # 使用 Flask-Login 登入用戶
            login_success = login_user(flask_user, remember=True)
            
            if login_success:
                # 登入成功
                session.permanent = True  # 確保會話是永久的
                session['user'] = {
                    'uid': result['user']['localId'],
                    'email': email,
                    'username': result['user_data'].get('username', 'User'),
                    'token': result['user']['idToken'],
                    'last_login': int(time.time())  # 添加登錄時間戳
                }
                
                # 保存會話
                session.modified = True
                
                print(f"成功登入用戶 {email} (ID: {flask_user.id})")
                flash('登入成功！', 'success')
                
                # 檢查是否有下一頁參數
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('main.index'))
            else:
                # Flask-Login登入失敗
                flash('登入過程中發生錯誤，請稍後再試', 'danger')
        else:
            # 登入失敗
            flash(result['message'], 'danger')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """處理用戶註冊"""
    # 如果用戶已登入，重定向到主頁
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 處理POST請求（用戶提交註冊表單）
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 驗證表單數據
        if not username or not email or not password:
            flash('請填寫完整的註冊資訊', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('兩次輸入的密碼不一致', 'danger')
            return render_template('auth/register.html')
        
        # 嘗試註冊
        result = firebase_service.register_user(email, password, username)
        
        if result['status'] == 'success':
            # 註冊成功，提示用戶並顯示隨機生成的玩家ID
            player_id = result.get('player_id', '未生成ID')
            flash(f'註冊成功！您的玩家ID是: {player_id}，請登入以開始遊戲', 'success')
            # 儲存玩家ID到會話，以便登入後顯示
            session['registered_player_id'] = player_id
            return redirect(url_for('auth.login'))
        else:
            # 註冊失敗
            flash(result['message'], 'danger')
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    """處理用戶登出"""
    # 使用 Flask-Login 登出用戶
    logout_user()
    
    # 清除會話中的用戶信息
    session.pop('user', None)
    
    flash('您已成功登出', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/get-custom-token', methods=['GET'])
@login_required
def get_custom_token():
    """獲取 Firebase 自定義認證令牌
    
    此端點為前端提供一個自定義令牌，用於在前端自動登入到 Firebase
    """
    try:
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': '用戶未登入'
            }), 401
        
        # 獲取當前用戶的 Firebase UID
        user_id = current_user.id
        
        # 使用 Firebase Admin SDK 生成自定義令牌
        from firebase_admin import auth as firebase_admin_auth
        custom_token = firebase_admin_auth.create_custom_token(user_id)
        
        return jsonify({
            'success': True,
            'token': custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"生成自定義令牌失敗: {e}\n{error_details}")
        
        return jsonify({
            'success': False,
            'message': f'生成令牌失敗: {str(e)}'
        }), 500