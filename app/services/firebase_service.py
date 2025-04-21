import firebase_admin
from firebase_admin import credentials, auth, firestore
import pyrebase
from flask import session, redirect, url_for
from functools import wraps
from flask_login import UserMixin
import os
import json
import random
import string

from app.config.firebase_config import FIREBASE_CONFIG, FIREBASE_ADMIN_CONFIG

# 創建一個 Flask-Login 相容的用戶類別
class FirebaseUser(UserMixin):
    def __init__(self, uid, email, username=None, data=None):
        self.id = uid
        self.email = email
        self.username = username
        self.data = data or {}
        self.is_admin = self.data.get('is_admin', False)  # 從 data 字典中獲取 is_admin 屬性
        self.player_id = self.data.get('player_id')  # 添加 player_id 屬性
        
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
            
            # 生成隨機玩家ID (8位英數字元)
            player_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # 準備使用者資料
            user_data = {
                "username": username,
                "email": email,
                "created_at": firebase_admin.firestore.SERVER_TIMESTAMP,
                "experience": 0,
                "level": 1,
                "avatar": "default.png",
                "last_active": firebase_admin.firestore.SERVER_TIMESTAMP,
                "is_admin": False,
                "player_id": player_id  # 添加玩家ID
            }
            
            # 儲存使用者資料到 Realtime Database (保留原有功能)
            self.db.child("users").child(user['localId']).set({
                "username": username,
                "email": email,
                "created_at": {".sv": "timestamp"},
                "experience": 0,
                "level": 1,
                "player_id": player_id  # 添加玩家ID
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
            if (firestore_user_doc.exists):
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
    
    def generate_route_creatures(self, route_id, route_name, element_type, route_geometry=None, count=1):
        """在特定公車路線上生成隨機精靈
        
        Args:
            route_id (str): 公車路線ID
            route_name (str): 公車路線名稱
            element_type (str): 路線元素類型 (fire, water, earth, air, electric, normal)
            route_geometry (dict, optional): 路線的GeoJSON幾何資訊，用於生成精靈位置
            count (int, optional): 要生成的精靈數量. 默認為 1.
        
        Returns:
            list: 生成的精靈列表
        """
        try:
            from app.models.creature import ElementType
            import random
            import json
            from datetime import datetime, timedelta
            import time
            
            # 精靈名稱庫 (依據元素類型分類)
            creature_names = {
                'fire': ['火焰龍', '炎魔獸', '熔岩鼠', '火羽鳥', '赤炎狐', '煙霧蟲'],
                'water': ['水晶蛇', '深海魚', '漣漪蛙', '珊瑚龜', '海泡兔', '水精靈'],
                'earth': ['岩石熊', '泥沼蟹', '土靈鼠', '山嶽龜', '晶石蜥', '花園精'],
                'air': ['旋風鷹', '雲朵羊', '微風蝶', '颶風鳥', '風翼獸', '空氣精'],
                'electric': ['雷電獸', '閃電鼠', '電流蜥', '充電鳥', '感應蟲', '電磁龍'],
                'normal': ['普通貓', '常見鳥', '小兔子', '灰松鼠', '家犬', '普通鼠']
            }
            
            # 轉換元素類型字符串為枚舉值
            try:
                element_enum = ElementType[element_type.upper()]
            except (KeyError, AttributeError):
                # 如果類型不匹配，使用一般類型
                element_enum = ElementType.NORMAL
                element_type = 'normal'
            
            # 精靈種類庫
            species_list = ['一般種', '罕見種', '稀有種', '傳說種']
            species_weights = [60, 25, 10, 5]  # 不同稀有度的機率權重
            
            # 精靈圖片URL庫 (依據元素類型分類)
            image_urls = {
                'fire': [
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Ffire1.png',
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Ffire2.png'
                ],
                'water': [
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fwater1.png',
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fwater2.png'
                ],
                'earth': [
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fearth1.png',
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fearth2.png'
                ],
                'air': [
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fair1.png',
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fair2.png'
                ],
                'electric': [
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Felectric1.png',
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Felectric2.png'
                ],
                'normal': [
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fnormal1.png',
                    'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fnormal2.png'
                ]
            }
            
            # 預設圖片，如果找不到對應的元素圖片
            default_image = 'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Fdefault.png'
            
            # 如果提供了路線幾何資訊，解析它以生成精靈位置
            positions = []
            if route_geometry:
                # 如果是字符串，嘗試解析為 JSON
                if isinstance(route_geometry, str):
                    try:
                        geometry_data = json.loads(route_geometry)
                    except json.JSONDecodeError:
                        geometry_data = None
                else:
                    geometry_data = route_geometry
                
                # 從幾何數據中提取座標點
                if geometry_data and 'coordinates' in geometry_data:
                    coordinates = geometry_data['coordinates']
                    # 從路線上隨機選擇點
                    for _ in range(count):
                        # 隨機選擇一個座標點作為精靈位置
                        if coordinates:
                            random_point_index = random.randint(0, len(coordinates) - 1)
                            lng, lat = coordinates[random_point_index]
                            positions.append({'lat': lat, 'lng': lng})
            
            # 如果無法從路線幾何資訊中獲取位置，使用預設位置
            if not positions:
                # 使用硬編碼的預設位置範圍 (台北市範圍)
                for _ in range(count):
                    lat = random.uniform(25.01, 25.10)  # 台北市緯度範圍
                    lng = random.uniform(121.50, 121.60)  # 台北市經度範圍
                    positions.append({'lat': lat, 'lng': lng})
            
            # 設定精靈存活時間 (5分鐘)
            expiry_time = datetime.now() + timedelta(minutes=5)
            expiry_timestamp = int(time.mktime(expiry_time.timetuple()))
            
            # 生成隨機精靈
            creatures = []
            for position in positions:
                # 隨機選擇精靈名稱
                if element_type in creature_names and creature_names[element_type]:
                    name = random.choice(creature_names[element_type])
                else:
                    name = random.choice(creature_names['normal'])
                
                # 隨機選擇精靈種類 (基於權重)
                species = random.choices(species_list, weights=species_weights, k=1)[0]
                
                # 根據精靈種類設置基本數值
                if species == '一般種':
                    base_power = random.randint(10, 30)
                    base_defense = random.randint(10, 30)
                    base_hp = random.randint(50, 100)
                elif species == '罕見種':
                    base_power = random.randint(25, 45)
                    base_defense = random.randint(25, 45)
                    base_hp = random.randint(80, 150)
                elif species == '稀有種':
                    base_power = random.randint(40, 70)
                    base_defense = random.randint(40, 70)
                    base_hp = random.randint(120, 200)
                else:  # 傳說種
                    base_power = random.randint(65, 100)
                    base_defense = random.randint(65, 100)
                    base_hp = random.randint(180, 300)
                
                # 選擇隨機圖片URL
                if element_type in image_urls and image_urls[element_type]:
                    image_url = random.choice(image_urls[element_type])
                else:
                    image_url = default_image
                
                # 創建精靈數據
                creature_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
                creature_data = {
                    'id': creature_id,
                    'name': name,
                    'species': species,
                    'element_type': element_enum.value,
                    'level': 1,
                    'experience': 0,
                    'power': base_power,
                    'defense': base_defense,
                    'hp': base_hp,
                    'max_hp': base_hp,
                    'image_url': image_url,
                    'position': position,  # 精靈位置
                    'bus_route_id': route_id,
                    'bus_route_name': route_name,
                    'generated_at': firebase_admin.firestore.SERVER_TIMESTAMP,
                    'expires_at': expiry_timestamp,  # 精靈過期時間 (5分鐘後)
                    'is_captured': False
                }
                
                # 儲存到 Firestore
                self.firestore_db.collection('route_creatures').document(creature_id).set(creature_data)
                
                # 添加到返回列表
                creatures.append(creature_data)
            
            print(f"已在路線 {route_name} (ID: {route_id}) 上生成 {len(creatures)} 隻精靈")
            return creatures
        except Exception as e:
            print(f"生成路線精靈失敗: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_route_creatures(self, route_id=None):
        """獲取指定路線上的所有未被捕捉且未過期的精靈
        
        Args:
            route_id (str, optional): 公車路線ID。如果為None，返回所有路線上的精靈。
        
        Returns:
            list: 未被捕捉且未過期的精靈列表
        """
        try:
            import time
            from datetime import datetime
            from google.api_core.exceptions import FailedPrecondition
            
            # 獲取當前時間戳
            current_timestamp = int(time.mktime(datetime.now().timetuple()))
            
            # 使用單一條件查詢，避免需要複合索引
            # 先只查詢未被捕捉的精靈 - 使用正確的位置參數格式
            query = self.firestore_db.collection('route_creatures').where('is_captured', '==', False)
            
            # 如果指定了路線ID，添加路線過濾條件
            if route_id:
                query = query.where('bus_route_id', '==', route_id)
            
            try:
                # 執行查詢
                creatures_ref = query.get()
                
                creatures = []
                for doc in creatures_ref:
                    creature_data = doc.to_dict()
                    
                    # 在代碼中過濾過期精靈，而不是在查詢中做
                    if 'expires_at' in creature_data and creature_data['expires_at'] > current_timestamp:
                        # 確保精靈數據包含必要的字段
                        if 'position' not in creature_data or not creature_data['position']:
                            # 如果沒有位置信息，添加默認位置（台北市中心附近）
                            creature_data['position'] = {
                                'lat': 25.0330 + random.uniform(-0.01, 0.01),
                                'lng': 121.5654 + random.uniform(-0.01, 0.01)
                            }
                        
                        # 確保元素類型是字符串格式
                        if 'element_type' in creature_data:
                            # 如果是數字枚舉值，轉換為字符串
                            element_type = creature_data['element_type']
                            if isinstance(element_type, int):
                                from app.models.creature import ElementType
                                # 將枚舉值轉換為字符串
                                try:
                                    element_type_str = ElementType(element_type).name.lower()
                                    creature_data['element_type'] = element_type_str
                                except (ValueError, AttributeError):
                                    # 如果轉換失敗，使用默認值
                                    creature_data['element_type'] = 'normal'
                        
                        # 添加到返回列表
                        creatures.append(creature_data)
                
                print(f"從Firestore獲取了 {len(creatures)} 隻未捕捉的精靈")
                return creatures
                    
            except FailedPrecondition as e:
                # 如果仍然出現索引問題，嘗試完全簡化查詢然後在內存中過濾
                print(f"複合查詢失敗，進行簡單查詢並在代碼中過濾: {e}")
                all_creatures = self.firestore_db.collection('route_creatures').get()
                
                creatures = []
                for doc in all_creatures:
                    creature_data = doc.to_dict()
                    
                    # 在代碼中過濾條件
                    if (creature_data.get('is_captured', True) == False and 
                        creature_data.get('expires_at', 0) > current_timestamp and
                        (route_id is None or creature_data.get('bus_route_id') == route_id)):
                        
                        # 確保精靈數據包含必要的字段
                        if 'position' not in creature_data or not creature_data['position']:
                            creature_data['position'] = {
                                'lat': 25.0330 + random.uniform(-0.01, 0.01),
                                'lng': 121.5654 + random.uniform(-0.01, 0.01)
                            }
                        
                        # 確保元素類型是字符串格式
                        if 'element_type' in creature_data:
                            element_type = creature_data['element_type']
                            if isinstance(element_type, int):
                                from app.models.creature import ElementType
                                try:
                                    element_type_str = ElementType(element_type).name.lower()
                                    creature_data['element_type'] = element_type_str
                                except (ValueError, AttributeError):
                                    creature_data['element_type'] = 'normal'
                        
                        creatures.append(creature_data)
                        
                print(f"從Firestore簡單查詢後過濾獲得了 {len(creatures)} 隻未捕捉的精靈")
                return creatures
        except Exception as e:
            print(f"獲取路線精靈失敗: {e}")
            import traceback
            traceback.print_exc()
            
            # 發生錯誤時返回空列表而不是失敗
            print("返回空精靈列表")
            return []
            
    def remove_expired_creatures(self):
        """刪除所有已過期的精靈
        
        Returns:
            int: 刪除的精靈數量
        """
        try:
            import time
            from datetime import datetime
            
            # 獲取當前時間戳
            current_timestamp = int(time.mktime(datetime.now().timetuple()))
            
            # 查詢所有已過期的精靈
            expired_ref = self.firestore_db.collection('route_creatures').where(
                'expires_at', '<=', current_timestamp
            ).get()
            
            # 刪除已過期的精靈
            count = 0
            for doc in expired_ref:
                doc.reference.delete()
                count += 1
            
            if count > 0:
                print(f"已刪除 {count} 隻過期精靈")
            
            return count
        except Exception as e:
            print(f"刪除過期精靈失敗: {e}")
            return 0
    
    def catch_route_creature(self, creature_id, user_id):
        """捕捉路線上的精靈
        
        Args:
            creature_id (str): 精靈ID
            user_id (str): 使用者ID
        
        Returns:
            dict: 捕捉結果
        """
        try:
            # 獲取精靈數據
            creature_ref = self.firestore_db.collection('route_creatures').document(creature_id)
            creature_doc = creature_ref.get()
            
            if not creature_doc.exists:
                return {
                    'success': False,
                    'message': '找不到該精靈'
                }
            
            creature_data = creature_doc.to_dict()
            
            # 檢查精靈是否已被捕捉
            if creature_data.get('is_captured', False):
                return {
                    'success': False,
                    'message': '該精靈已被捕捉'
                }
            
            # 更新精靈狀態為已捕捉
            creature_ref.update({
                'is_captured': True,
                'captured_by': user_id,
                'captured_at': firebase_admin.firestore.SERVER_TIMESTAMP
            })
            
            # 添加精靈到用戶的收藏中
            user_creature_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
            user_creature_data = {
                'id': user_creature_id,
                'original_creature_id': creature_id,
                'name': creature_data.get('name', '未知精靈'),
                'species': creature_data.get('species', '一般種'),
                'element_type': creature_data.get('element_type', 'normal'),
                'level': 1,
                'experience': 0,
                'power': creature_data.get('power', 10),
                'defense': creature_data.get('defense', 10),
                'hp': creature_data.get('hp', 100),
                'max_hp': creature_data.get('max_hp', 100),
                'image_url': creature_data.get('image_url', ''),
                'user_id': user_id,
                'bus_route_id': creature_data.get('bus_route_id', ''),
                'bus_route_name': creature_data.get('bus_route_name', ''),
                'captured_at': firebase_admin.firestore.SERVER_TIMESTAMP
            }
            
            # 儲存到用戶精靈集合
            self.firestore_db.collection('user_creatures').document(user_creature_id).set(user_creature_data)
            
            return {
                'success': True,
                'message': f"已成功捕捉 {creature_data.get('name', '未知精靈')}!",
                'creature': user_creature_data
            }
        except Exception as e:
            print(f"捕捉精靈失敗: {e}")
            return {
                'success': False,
                'message': f'捕捉精靈時發生錯誤: {str(e)}'
            }

# 創建裝飾器，用於路由保護
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function