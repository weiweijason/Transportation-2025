from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_required, current_user
from app.models.bus import BusRoute
from app.config.firebase_config import FIREBASE_CONFIG  # 導入Firebase配置

# 創建藍圖 blueprint - 不設置 url_prefix，將由主藍圖統一設置
views_bp = Blueprint('game', __name__)

# 遊戲主頁面
@views_bp.route('/')
@login_required
def game_home():
    return render_template('game/catch.html', firebase_config=FIREBASE_CONFIG)

# 捕捉精靈頁面
@views_bp.route('/catch')
@login_required
def catch():
    return render_template('game/catch.html', firebase_config=FIREBASE_CONFIG)

# 擂台對戰頁面
@views_bp.route('/battle')
@login_required
def battle():
    # 從請求參數中獲取擂台ID
    arena_id = request.args.get('arena_id')
    
    # 如果沒有提供擂台ID，則重定向到擂台列表頁面
    if not arena_id:
        flash('請先選擇一個擂台進行挑戰', 'warning')
        return redirect(url_for('game.list_arenas'))
    
    return render_template('game/battle.html', arena_id=arena_id, firebase_config=FIREBASE_CONFIG)

# 新增：擂台列表頁面
@views_bp.route('/arenas')
@login_required
def list_arenas():
    """顯示所有擂台列表"""
    # 獲取所有擂台
    from app.models.arena import FirebaseArena as Arena
    arenas = Arena.get_all()
    return render_template('game/arenas.html', arenas=arenas, firebase_config=FIREBASE_CONFIG)

# 新增: 從巴士路線捕捉頁面
@views_bp.route('/catch-on-route/<route_id>')
@login_required
def catch_on_route(route_id):
    """在特定公車路線上捕捉精靈的頁面"""
    # 獲取路線資訊
    route = BusRoute.query.filter_by(id=route_id).first()
    if not route:
        flash('找不到指定路線', 'error')
        return redirect(url_for('game.catch'))
    
    return render_template(
        'game/catch.html',
        route=route,
        active_route_id=route_id,
        firebase_config=FIREBASE_CONFIG
    )

# 新增：互動捕捉頁面
@views_bp.route('/capture-interactive/<creature_id>')
@login_required
def capture_interactive(creature_id):
    """精靈互動捕捉頁面"""
    # 獲取精靈資訊
    from app.services.firebase_service import FirebaseService
    
    # 從 Firebase 獲取精靈
    firebase_service = FirebaseService()
    
    creature_ref = firebase_service.firestore_db.collection('route_creatures').document(creature_id)
    creature_doc = creature_ref.get()
    
    if not creature_doc.exists:
        flash('找不到指定精靈', 'error')
        return redirect(url_for('game.catch'))
    
    creature = creature_doc.to_dict()
    
    # 檢查該玩家是否已經捕捉過這隻精靈
    current_player_id = None
    if current_user.is_authenticated:
        # 獲取用戶數據
        user_data = firebase_service.get_user_info(current_user.id)
        if user_data and 'player_id' in user_data:
            current_player_id = user_data['player_id']
    
    # 檢查是否已被捕捉 (使用子集合)
    if current_player_id:
        try:
            # 檢查 captured_players 子集合中是否已包含此玩家
            player_capture_ref = creature_ref.collection('captured_players').document(current_player_id)
            player_capture_doc = player_capture_ref.get()
            
            if player_capture_doc.exists:
                flash('你已經捕捉過這隻精靈了', 'warning')
                return redirect(url_for('game.catch'))
        except Exception as e:
            current_app.logger.error(f"檢查玩家捕捉狀態失敗: {e}")
            # 若檢查失敗，繼續讓用戶嘗試捕捉
    
    # 元素類型對應中文名稱
    element_types = {
        'fire': '火系',
        'water': '水系',
        'earth': '土系',
        'air': '風系',
        'electric': '電系',
        'normal': '一般系',
        0: '火系',
        1: '水系',
        2: '土系',
        3: '風系',
        4: '電系',
        5: '一般系'
    }
    
    return render_template(
        'game/capture_interactive.html',
        creature=creature,
        element_types=element_types,
        firebase_config=FIREBASE_CONFIG
    )