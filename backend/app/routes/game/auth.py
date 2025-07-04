from flask import request, jsonify, session
from functools import wraps
from app.services.firebase_service import FirebaseService

# 認證裝飾器 - 同時支援 JWT 和 Session
def jwt_or_session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 檢查是否有 JWT 令牌
        auth_header = request.headers.get('Authorization')
        if (auth_header and auth_header.startswith('Bearer ')):
            token = auth_header.split(' ')[1]
            try:
                firebase_service = FirebaseService()
                decoded_token = firebase_service.verify_id_token(token)
                if decoded_token:
                    # 令牌有效，可以繼續
                    return f(*args, **kwargs)
            except Exception as e:
                print(f"JWT 驗證失敗: {e}")
                # 如果 JWT 驗證失敗，繼續檢查 session
        
        # 檢查是否有 session
        if 'user' in session:
            return f(*args, **kwargs)
        
        # 如果兩種認證都失敗，返回 401 未授權
        return jsonify({
            'success': False,
            'message': '請先登入'
        }), 401
    
    return decorated_function