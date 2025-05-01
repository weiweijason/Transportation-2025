from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import config as config_module
import logging
import threading

# 初始化擴展
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def fetch_tdx_data():
    """抓取所有 TDX API 資料並儲存到本地"""
    try:
        from app.services.tdx_service import fetch_all_data
        logging.info("開始抓取所有 TDX API 資料...")
        results = fetch_all_data()
        
        # 檢查各種資料的載入結果
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        if success_count == total_count:
            logging.info(f"所有 TDX API 資料抓取完成。({success_count}/{total_count})")
            print(f"=== TDX資料預載完成: 成功載入 {success_count} 項資料 ===")
        else:
            failed_items = [item for item, success in results.items() if not success]
            logging.warning(f"部分 TDX API 資料抓取失敗，{success_count}/{total_count} 項成功。失敗項目: {', '.join(failed_items)}")
            print(f"=== TDX資料預載部分完成: 成功 {success_count}/{total_count} ===")
            print(f"=== 以下項目載入失敗: {', '.join(failed_items)} ===")
    except Exception as e:
        logging.error(f"TDX API 資料抓取失敗: {e}")
        print(f"=== TDX資料預載失敗: {str(e)} ===")

# 用於處理應用啟動後資料預載
def load_tdx_data_on_startup(app):
    """在應用啟動時預載TDX資料"""
    print("=== 應用已啟動，將在背景預載TDX資料 ===")
    
    # 使用後台線程預載資料，避免阻塞應用啟動
    def load_data_background():
        with app.app_context():
            fetch_tdx_data()
            
            # 在加載 TDX 數據後，同步本地道館數據到 Firebase
            try:
                print("=== 開始將本地道館數據同步到 Firebase ===")
                from app.models.arena import sync_arena_cache_to_firebase
                sync_result = sync_arena_cache_to_firebase()
                if sync_result:
                    print("=== 成功將本地道館數據同步到 Firebase ===")
                else:
                    print("=== 同步本地道館數據到 Firebase 失敗，請查看日誌 ===")
            except Exception as e:
                import traceback
                print(f"=== 同步道館數據到 Firebase 時發生錯誤: {e} ===")
                traceback.print_exc()
    
    # 啟動後台線程載入資料
    data_loading_thread = threading.Thread(target=load_data_background)
    data_loading_thread.daemon = True  # 設置為守護線程，這樣主程序結束時，線程會自動結束
    data_loading_thread.start()

def create_app(config_name='default', load_tdx=True):
    """工廠函數，用於創建應用實例"""
    app = Flask(__name__)
    app.config.from_object(config_module.config[config_name])
    config_module.config[config_name].init_app(app)
    
    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 初始化會話管理
    if app.config.get('SESSION_TYPE') == 'filesystem':
        from flask_session import Session
        Session(app)
    
    # 註冊藍圖
    from app.routes import main, auth, game, admin
    app.register_blueprint(main.main)
    app.register_blueprint(auth.auth, url_prefix='/auth')
    app.register_blueprint(game.game_bp, url_prefix='/game')
    app.register_blueprint(admin.admin_bp, url_prefix='/admin')
    
    # 初始化遊戲模組的其他API藍圖
    game.init_app(app)
    
    # 設置 user_loader 回調
    from app.services.firebase_service import get_user_from_id
    
    @login_manager.user_loader
    def load_user(user_id):
        user = get_user_from_id(user_id)
        # 增加日誌以幫助排查問題
        if user:
            print(f"已載入用戶 {user_id}")
        else:
            print(f"無法載入用戶 {user_id}")
        return user
    
    # 只有在需要時才預載TDX資料
    if load_tdx:
        load_tdx_data_on_startup(app)
    
    return app