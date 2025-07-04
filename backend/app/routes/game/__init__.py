from flask import Blueprint

# 導入各個模組藍圖
from app.routes.game.views import views_bp
from app.routes.game.creature_api import creature_bp
from app.routes.game.bus_api import bus_bp
from app.routes.game.arena_api import arena_bp
from app.routes.game.arena_battle_api import arena_battle_bp
from app.routes.game.route_creatures_api import route_creatures_bp
from app.routes.game.user_api import user_bp

# 創建主藍圖 - 設置正確的 URL 前綴
game_bp = Blueprint('game', __name__, url_prefix='/game')

# 在主藍圖中註冊所有子藍圖
def init_app(app):
    # 將 views_bp 的路由註冊到 game_bp 上
    from app.routes.game.views import catch, game_home, battle, list_arenas, capture_interactive, catch_on_route, fullscreen_map
    
    # 手動註冊視圖路由到主藍圖
    game_bp.add_url_rule('/', 'game_home', game_home, methods=['GET'])
    game_bp.add_url_rule('/catch', 'catch', catch, methods=['GET'])
    game_bp.add_url_rule('/map', 'fullscreen_map', fullscreen_map, methods=['GET'])
    game_bp.add_url_rule('/battle', 'battle', battle, methods=['GET'])
    game_bp.add_url_rule('/arenas', 'list_arenas', list_arenas, methods=['GET'])
    game_bp.add_url_rule('/capture-interactive/<creature_id>', 'capture_interactive', capture_interactive, methods=['GET'])
    game_bp.add_url_rule('/catch-on-route/<route_id>', 'catch_on_route', catch_on_route, methods=['GET'])
    
    # 註冊主遊戲藍圖
    app.register_blueprint(game_bp)
      # 註冊 API 藍圖
    app.register_blueprint(creature_bp)
    app.register_blueprint(bus_bp)
    app.register_blueprint(arena_bp)
    app.register_blueprint(arena_battle_bp)
    app.register_blueprint(route_creatures_bp)
    app.register_blueprint(user_bp)
    
    return app