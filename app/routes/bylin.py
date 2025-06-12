from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.config.firebase_config import FIREBASE_CONFIG

# 創建 bylin 藍圖
bylin = Blueprint('bylin', __name__, url_prefix='/bylin')

@bylin.route('/myelf')
@login_required
def myelf():
    """我的精靈頁面"""
    return render_template('bylin/myelf.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/myarena')
@login_required
def myarena():
    """我的擂台頁面"""
    return render_template('bylin/myarena.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/backpack')
@login_required
def backpack():
    """我的背包頁面"""
    return render_template('bylin/backpack.html', firebase_config=FIREBASE_CONFIG)
