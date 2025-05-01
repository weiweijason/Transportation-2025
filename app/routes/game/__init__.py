from flask import Blueprint

# 導入各個模組藍圖
from app.routes.game.views import views_bp
from app.routes.game.creature_api import creature_bp
from app.routes.game.bus_api import bus_bp
from app.routes.game.arena_api import arena_bp
from app.routes.game.route_creatures_api import route_creatures_bp
from app.routes.game.user_api import user_bp

# 創建主藍圖 - 這個會被 app/__init__.py 直接使用
game_bp = views_bp

# 在主藍圖中註冊所有子藍圖
def init_app(app):
    # 註冊 API 藍圖
    app.register_blueprint(creature_bp)
    app.register_blueprint(bus_bp)
    app.register_blueprint(arena_bp)
    app.register_blueprint(route_creatures_bp)
    app.register_blueprint(user_bp)
    
    return app