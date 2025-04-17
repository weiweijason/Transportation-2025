from flask import Blueprint, render_template
from flask_login import login_required, current_user

# 創建遊戲藍圖
game = Blueprint('game', __name__)

@game.route('/catch')
@login_required
def catch_creatures():
    """捕捉精靈頁面"""
    return render_template('game/catch.html')

@game.route('/arena')
@login_required
def arena_list():
    """擂台列表頁面"""
    return render_template('game/arena_list.html')

@game.route('/battle')
@login_required
def battle():
    """PVP對戰頁面"""
    return render_template('game/battle.html')