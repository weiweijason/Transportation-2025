from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.config.firebase_config import FIREBASE_CONFIG
from app.services.firebase_service import FirebaseService

# 創建 achievement 藍圖
achievement = Blueprint('achievement', __name__, url_prefix='/achievement')

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

@achievement.route('/demo')
def achievement_demo():
    """成就頁面演示 (不需要登入)"""
    return render_template('achievement/achievement.html', 
                         firebase_config=FIREBASE_CONFIG, 
                         is_demo=True)

@achievement.route('/api/demo_achievements', methods=['GET'])
def api_demo_achievements():
    """取得演示成就資料 (不需要登入)"""
    from app.models.achievement import ACHIEVEMENTS, get_achievements_by_category, CATEGORY_DISPLAY_NAMES, CATEGORY_ICONS
    import random
    
    # 創建演示數據
    demo_achievements = {}
    for achievement_id, achievement in ACHIEVEMENTS.items():
        # 隨機設置一些成就為已完成
        completed = random.choice([True, False, False])  # 約1/3的成就已完成
        progress = achievement.target_value if completed else random.randint(0, achievement.target_value - 1)
        
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
    
    # 計算統計數據
    total_achievements = len(ACHIEVEMENTS)
    completed_achievements = sum(1 for ach in demo_achievements.values() if ach['completed'])
    completion_rate = (completed_achievements / total_achievements * 100) if total_achievements > 0 else 0
    recent_achievements = random.randint(0, 5)  # 隨機最近成就數
    
    return jsonify({
        'status': 'success',
        'achievements': demo_achievements,
        'categories': categorized_achievements,
        'stats': {
            'total': total_achievements,
            'completed': completed_achievements,
            'completion_rate': round(completion_rate, 1),
            'recent': recent_achievements
        }    })

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
