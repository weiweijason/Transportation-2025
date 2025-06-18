from flask import Blueprint, render_template, redirect, url_for, session, flash, request
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
    
    return render_template('main/profile.html', firebase_config=FIREBASE_CONFIG)

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """編輯用戶資料頁面"""
    from app.services.firebase_service import FirebaseService
    from app.config.firebase_config import FIREBASE_CONFIG
    
    firebase_service = FirebaseService()
    
    if request.method == 'POST':
        # 處理表單提交
        new_username = request.form.get('username', '').strip()
        avatar_id = request.form.get('avatar_id')
        
        if not new_username:
            flash('用戶名稱不能為空', 'danger')
            return redirect(url_for('main.edit_profile'))
        
        # 準備頭像URL映射（與user_setup.html相同）
        avatar_url_mapping = {
            "1": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c769d000e8e2515f6/view?project=681c5c6b002355634f3c&mode=admin",
            "2": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76a2002589aa244a/view?project=681c5c6b002355634f3c&mode=admin",
            "3": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76aa0030f3d8e5f1/view?project=681c5c6b002355634f3c&mode=admin",
            "4": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76af001cac084ee3/view?project=681c5c6b002355634f3c&mode=admin",
            "5": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76b8000b6f6ff334/view?project=681c5c6b002355634f3c&mode=admin",
            "6": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76bc00200e74dfaa/view?project=681c5c6b002355634f3c&mode=admin",
            "7": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76c100023ff731b5/view?project=681c5c6b002355634f3c&mode=admin",
            "8": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76c60019ba53529d/view?project=681c5c6b002355634f3c&mode=admin",
            "9": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76cb0027c008c539/view?project=681c5c6b002355634f3c&mode=admin",
            "10": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76d000263718b58e/view?project=681c5c6b002355634f3c&mode=admin"
        }
        
        # 準備更新數據
        update_data = {
            'username': new_username
        }
        
        # 如果選擇了新頭像，更新頭像
        if avatar_id and avatar_id in avatar_url_mapping:
            update_data['avatar_id'] = avatar_id
            update_data['avatar'] = avatar_url_mapping[avatar_id]
        
        try:
            # 更新Firebase中的用戶資料
            result = firebase_service.update_user_profile(current_user.id, update_data)
            
            if result['status'] == 'success':
                # 更新session中的用戶名稱
                if 'user' in session:
                    session['user']['username'] = new_username
                    session.modified = True
                
                flash('資料更新成功！', 'success')
                return redirect(url_for('main.profile'))
            else:
                flash(f'更新失敗：{result["message"]}', 'danger')
        except Exception as e:
            flash(f'更新過程中發生錯誤：{str(e)}', 'danger')
    
    # GET請求，獲取當前用戶資料
    try:
        user_data = firebase_service.get_user_info(current_user.id)
        if not user_data:
            flash('無法獲取用戶資料', 'danger')
            return redirect(url_for('main.profile'))
    except Exception as e:
        flash(f'獲取用戶資料失敗：{str(e)}', 'danger')
        return redirect(url_for('main.profile'))
    
    return render_template('main/edit_profile.html', 
                         user_data=user_data, 
                         firebase_config=FIREBASE_CONFIG)