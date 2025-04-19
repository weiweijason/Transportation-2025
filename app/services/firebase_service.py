import firebase_admin
from firebase_admin import credentials, auth, firestore
import pyrebase
from flask import session, redirect, url_for
from functools import wraps
from flask_login import UserMixin
import os
import json

from app.config.firebase_config import FIREBASE_CONFIG, FIREBASE_ADMIN_CONFIG

# 創建一個 Flask-Login 相容的用戶類別
class FirebaseUser(UserMixin):
    def __init__(self, uid, email, username=None, data=None):
        self.id = uid
        self.email = email
        self.username = username
        self.data = data or {}
        self.is_admin = self.data.get('is_admin', False)  # 從 data 字典中獲取 is_admin 屬性
        
    def get_id(self):
        return self.id

# 從 uid 獲取用戶實例的函數，用於 Flask-Login 的 user_loader
def get_user_from_id(user_id):
    try:
        # 初始化 Firebase 服務，如果未初始化
        firebase_service = FirebaseService()
        
        # 從 Firebase 獲取用戶數據
        user_data = firebase_service.get_user_info(user_id)
        
        if not user_data:
            return None
            
        # 創建一個 FirebaseUser 實例
        user = FirebaseUser(
            uid=user_id,
            email=user_data.get('email', ''),
            username=user_data.get('username', ''),
            data=user_data
        )
        
        return user
    except Exception as e:
        print(f"從 ID 加載用戶時出錯: {e}")
        return None

class FirebaseService:
    """Firebase認證服務類，提供登入、註冊和使用者管理功能"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化Firebase"""
        try:
            # 初始化Firebase Admin SDK (用於伺服器端驗證和管理)
            if not firebase_admin._apps:
                # 方法1: 嘗試從環境變數或指定路徑讀取服務帳號檔案
                service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', 'credentials/firebase-service-account.json')
                
                if os.path.exists(service_account_path):
                    # 如果服務帳號文件存在，使用文件初始化
                    cred = credentials.Certificate(service_account_path)
                else:
                    # 如果文件不存在，使用配置字典初始化
                    cred = credentials.Certificate(FIREBASE_ADMIN_CONFIG)
                
                self.admin_app = firebase_admin.initialize_app(cred)
            
            # 初始化Pyrebase (用於前端認證操作的封裝)
            self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
            self.auth = self.firebase.auth()
            self.db = self.firebase.database()
            
            # 初始化 Firestore 資料庫
            self.firestore_db = firestore.client()
            
            print("Firebase服務初始化成功")
        except Exception as e:
            print(f"Firebase服務初始化失敗: {e}")
    
    def register_user(self, email, password, username):
        """註冊新使用者
        
        Args:
            email: 使用者電子郵件
            password: 使用者密碼
            username: 使用者名稱
        
        Returns:
            dict: 包含使用者資訊和註冊狀態的字典
        """
        try:
            # 使用Firebase創建使用者
            user = self.auth.create_user_with_email_and_password(email, password)
            
            # 準備使用者資料
            user_data = {
                "username": username,
                "email": email,
                "created_at": firebase_admin.firestore.SERVER_TIMESTAMP,
                "experience": 0,
                "level": 1,
                "avatar": "default.png",
                "last_active": firebase_admin.firestore.SERVER_TIMESTAMP,
                "is_admin": False
            }
            
            # 儲存使用者資料到 Realtime Database (保留原有功能)
            self.db.child("users").child(user['localId']).set({
                "username": username,
                "email": email,
                "created_at": {".sv": "timestamp"},
                "experience": 0,
                "level": 1
            })
            
            # 儲存使用者資料到 Firestore Database
            self.firestore_db.collection('users').document(user['localId']).set(user_data)
            
            # 為用戶設置顯示名稱
            self.auth.update_profile(user['idToken'], display_name=username)
            
            return {
                "status": "success",
                "message": "使用者註冊成功",
                "user": user
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"註冊失敗: {str(e)}"
            }
    
    def login_user(self, email, password):
        """使用者登入
        
        Args:
            email: 使用者電子郵件
            password: 使用者密碼
        
        Returns:
            dict: 包含使用者資訊和登入狀態的字典
        """
        try:
            # 使用Firebase驗證使用者
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            # 首先嘗試從 Firestore 獲取使用者資料
            firestore_user_doc = self.firestore_db.collection('users').document(user['localId']).get()
            user_data = firestore_user_doc.to_dict() if firestore_user_doc.exists else None
            
            # 如果 Firestore 中沒有用戶數據，嘗試從 Realtime Database 獲取
            if user_data is None:
                user_data = self.db.child("users").child(user['localId']).get().val()
            
            # 如果用戶數據仍不存在，則創建基本用戶數據
            if user_data is None:
                print(f"警告: 用戶 {user['localId']} 的數據在數據庫中不存在，創建基本資料")
                user_data = {
                    "username": email.split('@')[0],  # 使用郵箱前綴作為默認用戶名
                    "email": email,
                    "created_at": firebase_admin.firestore.SERVER_TIMESTAMP,
                    "experience": 0,
                    "level": 1,
                    "avatar": "default.png",
                    "last_active": firebase_admin.firestore.SERVER_TIMESTAMP,
                    "is_admin": False
                }
                
                # 保存到 Firestore
                try:
                    self.firestore_db.collection('users').document(user['localId']).set(user_data)
                    # 為了與時間戳相容，需要替換 user_data 中的 SERVER_TIMESTAMP
                    user_data["created_at"] = user_data["last_active"] = {"seconds": int(firebase_admin.datetime.datetime.now().timestamp())}
                    print(f"已創建用戶 {user['localId']} 的基本資料於 Firestore")
                except Exception as e:
                    print(f"創建 Firestore 基本用戶資料失敗: {e}")
                
                # 同時保存到 Realtime Database (保持兼容性)
                try:
                    self.db.child("users").child(user['localId']).set({
                        "username": email.split('@')[0],
                        "email": email,
                        "created_at": {".sv": "timestamp"},
                        "experience": 0,
                        "level": 1
                    })
                    print(f"已創建用戶 {user['localId']} 的基本資料於 Realtime Database")
                except Exception as e:
                    print(f"創建 Realtime Database 基本用戶資料失敗: {e}")
            
            # 創建 Flask-Login 用戶
            firebase_user = FirebaseUser(
                uid=user['localId'],
                email=email,
                username=user_data.get('username', 'User') if user_data else email.split('@')[0],
                data=user_data or {}
            )
            
            # 更新用戶的最後活動時間
            try:
                self.firestore_db.collection('users').document(user['localId']).update({
                    "last_active": firebase_admin.firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                print(f"更新用戶最後活動時間失敗: {e}")
            
            return {
                "status": "success",
                "message": "登入成功",
                "user": user,
                "user_data": user_data or {},
                "flask_user": firebase_user
            }
        except Exception as e:
            print(f"登入詳細錯誤: {str(e)}")
            return {
                "status": "error",
                "message": f"登入失敗: {str(e)}"
            }
    
    def get_user_info(self, uid):
        """獲取使用者資訊
        
        Args:
            uid: 使用者ID
        
        Returns:
            dict: 使用者資訊
        """
        try:
            # 首先嘗試從 Firestore 獲取用戶數據
            firestore_user_doc = self.firestore_db.collection('users').document(uid).get()
            if firestore_user_doc.exists:
                return firestore_user_doc.to_dict()
            
            # 如果 Firestore 中沒有，嘗試從 Realtime Database 獲取
            user_data = self.db.child("users").child(uid).get().val()
            return user_data
        except Exception as e:
            print(f"獲取使用者資訊失敗: {e}")
            return None
    
    def update_user_info(self, uid, user_data):
        """更新使用者資訊
        
        Args:
            uid: 使用者ID
            user_data: 更新的使用者資料
        
        Returns:
            bool: 更新成功返回True，否則返回False
        """
        try:
            # 更新 Firestore 中的用戶數據
            self.firestore_db.collection('users').document(uid).update(user_data)
            
            # 同時更新 Realtime Database 中的用戶數據 (保持兼容性)
            self.db.child("users").child(uid).update(user_data)
            
            return True
        except Exception as e:
            print(f"更新使用者資訊失敗: {e}")
            return False
    
    def verify_id_token(self, id_token):
        """驗證ID令牌
        
        Args:
            id_token: Firebase身份驗證ID令牌
        
        Returns:
            dict: 解碼後的令牌資訊
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"令牌驗證失敗: {e}")
            return None

# 創建裝飾器，用於路由保護
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function