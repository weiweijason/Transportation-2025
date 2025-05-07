from flask import Blueprint, render_template, redirect, url_for, session, flash
from flask_login import login_required, current_user

# 創建主藍圖
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """網站主頁"""
    # 如果用戶已登入，導向到用戶主頁
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # 否則重定向到登入頁面
    return redirect(url_for('auth.login'))

@main.route('/home')
@login_required
def home():
    """使用者主頁 (需要登入)"""
    return render_template('main/home.html')

@main.route('/profile')
@login_required
def profile():
    """用戶個人資料頁面"""
    # 從配置獲取Firebase前端配置
    from app.config.firebase_config import FIREBASE_CONFIG
    
    # 確保用戶已登入
    if 'user' not in session:
        flash('請先登入', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('main/profile.html', firebase_config=FIREBASE_CONFIG)