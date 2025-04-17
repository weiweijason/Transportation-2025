from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from app.services.firebase_service import FirebaseService, FirebaseUser

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
            session['user'] = {
                'uid': result['user']['localId'],
                'email': email,
                'username': result['user_data'].get('username', 'User'),
                'token': result['user']['idToken']
            }
            
            # 使用 Flask-Login 登入用戶
            login_user(result['flask_user'])
            
            flash('登入成功！', 'success')
            return redirect(url_for('main.index'))
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
            # 註冊成功，提示用戶並轉到登入頁面
            flash('註冊成功！請登入', 'success')
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