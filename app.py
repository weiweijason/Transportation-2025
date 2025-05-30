import os
import threading
import time
from app import create_app, db
from flask_migrate import Migrate
from flask import session, redirect, url_for, request
from flask_login import current_user
from app.services.firebase_service import FirebaseService

# 創建應用實例
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

# 設置會話密鑰
app.secret_key = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'

# 設置會話的有效期
app.permanent_session_lifetime = 3600 * 24 * 7  # 7天

@app.shell_context_processor
def make_shell_context():
    """為Flask shell提供上下文"""
    from app.models.user import User
    from app.models.creature import Creature
    from app.models.bus import BusRoute, BusStop
    from app.models.arena import Arena, Battle
    
    return dict(
        app=app, db=db, User=User, Creature=Creature,
        BusRoute=BusRoute, BusStop=BusStop, Arena=Arena, Battle=Battle
    )

@app.cli.command()
def test():
    """運行單元測試"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.before_request
def before_request():
    """在每個請求之前執行
    
    用於實現自動重定向到登入頁面的功能
    """
    # 獲取當前路徑
    path = request.path
      # 定義不需要認證的路徑
    public_paths = [
        '/static/', 
        '/favicon.ico',
        '/auth/login',
        '/auth/login-for-setup', 
        '/auth/register',
        '/auth/user-setup',
        '/auth/logout',
        '/auth/get-custom-token',
        '/auth/tutorial'
    ]
    
    # 檢查是否為公開路徑
    is_public_path = any(path.startswith(public_path) for public_path in public_paths)
    
    # 如果用戶未登入且不在公開路徑，則重定向到登入頁面
    if not current_user.is_authenticated and not is_public_path:
        # 避免重導向循環 - 如果已經在前往登入頁面，就不要再重導向
        if path != '/':
            return redirect(url_for('auth.login', next=path))
        else:
            return redirect(url_for('auth.login'))

def start_periodic_cache():
    def periodic_task():
        firebase_service = FirebaseService()
        while True:
            print("[INFO] 正在從 Firebase 獲取精靈數據並更新到 CSV...")
            firebase_service.cache_creatures_to_csv()
            time.sleep(30)  # 每 30 秒執行一次

    thread = threading.Thread(target=periodic_task, daemon=True)
    thread.start()

if __name__ == '__main__':
    # 啟動定時任務
    start_periodic_cache()

    # 啟動伺服器
    app.run(debug=True, port=5001)