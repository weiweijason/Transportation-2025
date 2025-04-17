from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# 初始化擴展
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name='default'):
    """工廠函數，用於創建應用實例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 註冊藍圖
    from app.routes import main, auth, game
    app.register_blueprint(main.main)
    app.register_blueprint(auth.auth, url_prefix='/auth')
    
    # 當需要遊戲功能時，可以取消下方註解
    app.register_blueprint(game.game, url_prefix='/game')
    
    # 設置 user_loader 回調
    from app.services.firebase_service import get_user_from_id
    
    @login_manager.user_loader
    def load_user(user_id):
        return get_user_from_id(user_id)
    
    return app