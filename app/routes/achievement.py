from flask import Blueprint, render_template
from flask_login import login_required
from app.config.firebase_config import FIREBASE_CONFIG

# 創建 achievement 藍圖
achievement = Blueprint('achievement', __name__, url_prefix='/achievement')

@achievement.route('/')
@login_required
def achievement_page():
    """成就頁面"""
    return render_template('achievement/achievement.html', firebase_config=FIREBASE_CONFIG)
