from flask import Flask

def init_routes(app: Flask):
    """初始化所有路由"""
    # 導入並註冊其他藍圖
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.admin import admin_bp
    from app.routes.community import community_bp
    from app.routes.friend_fight import friend_fight_bp
    from app.routes.bylin import bylin
    from app.routes.achievement import achievement
    from app.routes.api_docs import api_docs
    from app.routes.daily_migration import daily_migration
    from app.routes.exchange_shop import exchange_shop
    # 使用新的遊戲模組結構
    from app.routes.game import init_app as init_game_routes
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(friend_fight_bp)
    app.register_blueprint(bylin)
    app.register_blueprint(achievement)
    app.register_blueprint(api_docs)
    app.register_blueprint(daily_migration)
    app.register_blueprint(exchange_shop)
    
    # 初始化遊戲路由
    init_game_routes(app)
    
    return app
