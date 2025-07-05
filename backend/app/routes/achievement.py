from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from app.config.firebase_config import FIREBASE_CONFIG
from app.services.firebase_service import FirebaseService
import hashlib

# 創建 achievement 藍圖
achievement = Blueprint('achievement', __name__, url_prefix='/achievement')

# 開發者密碼 (SHA256 hash)
# 實際密碼: "dev2025"
DEVELOPER_PASSWORD_HASH = "c17b089ec9b921e3112244c075633bd5c86b76578ed61788da874993654b4f6c"

def check_developer_access():
    """檢查開發者訪問權限"""
    return session.get('developer_access') == True

def verify_password(password):
    """驗證開發者密碼"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == DEVELOPER_PASSWORD_HASH

@achievement.route('/')
@login_required
def achievement_page():
    """成就頁面"""
    return render_template('achievement/achievement.html', firebase_config=FIREBASE_CONFIG)

@achievement.route('/api/user_achievements', methods=['GET'])
@login_required
def api_user_achievements():
    """取得目前登入使用者的成就資料 (JSON)"""
    user_id = str(current_user.id)
    firebase_service = FirebaseService()
    data = firebase_service.get_user_achievements(user_id)
    return jsonify(data)

@achievement.route('/demo', methods=['GET', 'POST'])
def achievement_demo():
    """成就頁面演示 (需要開發者密碼)"""
    # 檢查是否已經通過驗證
    if check_developer_access():
        return render_template('achievement/achievement.html', 
                             firebase_config=FIREBASE_CONFIG, 
                             is_demo=True)
    
    # 如果是POST請求，處理密碼驗證
    if request.method == 'POST':
        password = request.form.get('password')
        if password and verify_password(password):
            session['developer_access'] = True
            return redirect(url_for('achievement.achievement_demo'))
        else:
            flash('密碼錯誤', 'error')
    
    # 顯示密碼輸入頁面
    return render_template('achievement/demo_login.html')

@achievement.route('/demo/logout')
def demo_logout():
    """開發者登出demo模式"""
    session.pop('developer_access', None)
    flash('已登出開發者模式', 'info')
    return redirect(url_for('achievement.achievement_demo'))

@achievement.route('/api/demo_achievements', methods=['GET'])
def api_demo_achievements():
    """取得演示成就資料 (需要開發者權限)"""
    # 檢查開發者訪問權限
    if not check_developer_access():
        return jsonify({'status': 'error', 'message': '無權限訪問'}), 403
    
    from app.models.achievement import ACHIEVEMENTS, get_achievements_by_category, CATEGORY_DISPLAY_NAMES, CATEGORY_ICONS
    
    # 創建演示數據 - 所有成就都已解鎖
    demo_achievements = {}
    for achievement_id, achievement in ACHIEVEMENTS.items():
        # 在demo模式中，所有成就都設為已完成
        completed = True
        progress = achievement.target_value  # 進度設為目標值
        
        demo_achievements[achievement_id] = {
            'achievement_id': achievement_id,
            'completed': completed,
            'progress': progress,
            'target_value': achievement.target_value,
            'completed_at': None,
            'created_at': 0,
            'name': achievement.name,
            'description': achievement.description,
            'icon': achievement.icon,
            'category': achievement.category.value,
            'reward_points': achievement.reward_points,
            'hidden': achievement.hidden
        }
      # 按類別分組
    categories = get_achievements_by_category()
    categorized_achievements = {}
    
    for category_name, achievements_list in categories.items():
        # 找到對應的enum來獲取顯示名稱和圖標
        category_enum = None
        for enum_val in CATEGORY_DISPLAY_NAMES.keys():
            if enum_val.value == category_name:
                category_enum = enum_val
                break
        
        if category_enum:
            categorized_achievements[category_name] = {
                'display_name': CATEGORY_DISPLAY_NAMES[category_enum],
                'icon': CATEGORY_ICONS[category_enum],
                'achievements': []
            }
            
            for achievement_def in achievements_list:
                if achievement_def.id in demo_achievements:
                    categorized_achievements[category_name]['achievements'].append(
                        demo_achievements[achievement_def.id]
                    )
      # 計算統計數據 - demo模式所有成就都已完成
    total_achievements = len(ACHIEVEMENTS)
    completed_achievements = total_achievements  # 所有成就都已完成
    completion_rate = 100.0  # 100%完成率
    recent_achievements = min(5, total_achievements)  # 最近完成成就數，最多顯示5個
    
    return jsonify({
        'status': 'success',
        'achievements': demo_achievements,
        'categories': categorized_achievements,
        'stats': {
            'total': total_achievements,
            'completed': completed_achievements,
            'completion_rate': completion_rate,
            'recent': recent_achievements
        }})

@achievement.route('/summary')
@login_required
def achievement_summary():
    """成就總結頁面 - 顯示用戶的成就統計摘要"""
    user_id = str(current_user.id)
    firebase_service = FirebaseService()
    data = firebase_service.get_user_achievements(user_id)
    
    if data.get('status') == 'success':
        return render_template('achievement/summary.html', 
                             achievement_data=data, 
                             firebase_config=FIREBASE_CONFIG)
    else:
        flash('無法載入成就資料', 'error')
        return redirect(url_for('main.index'))
