from flask import Flask

def init_routes(app: Flask):
    """初始化所有路由"""
    # 導入並註冊其他藍圖
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    
    # 使用新的遊戲模組結構
    from app.routes.game import init_app as init_game_routes
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # 初始化遊戲路由
    init_game_routes(app)
    
    return app