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
import pandas as pd
import time
from datetime import datetime
import logging
import traceback

from app.config.firebase_config import FIREBASE_CONFIG, FIREBASE_ADMIN_CONFIG

# 確保data/creatures目錄存在
os.makedirs('app/data/creatures', exist_ok=True)

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
                "created_at": time.time(),
                "experience": 0,
                "level": 1,
                "avatar": "default.png",
                "last_active": time.time(),
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
              # 創建用戶背包子集合並初始化魔法陣
            self._initialize_user_backpack(user['localId'])
            
            # 初始化用戶成就
            self.initialize_user_achievements(user['localId'])
            
            # 為用戶設置顯示名稱
            self.auth.update_profile(user['idToken'], display_name=username)
            
            return {
                "status": "success",
                "message": "使用者註冊成功",
                "user": user,
                "player_id": player_id  # 返回生成的玩家ID
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
                    "created_at": time.time(),
                    "experience": 0,
                    "level": 1,
                    "avatar": "default.png",
                    "last_active": time.time(),
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
                    "last_active": time.time()
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
    
    def update_user_profile(self, user_id, data):
        """更新用戶配置文件
        
        Args:
            user_id: 使用者ID
            data: 要更新的資料字典
            
        Returns:
            dict: 更新結果
        """
        try:
            # 更新 Firestore 中的用戶資料
            self.firestore_db.collection('users').document(user_id).update(data)
              # 同時更新 Realtime Database 中的用戶資料 (保持兼容性)
            self.db.child("users").child(user_id).update(data)
            
            return {
                'status': 'success',
                'message': '用戶配置文件更新成功'
            }
        except Exception as e:
            print(f"更新用戶配置文件失敗: {e}")
            return {
                'status': 'error',
                'message': f'更新配置文件失敗: {str(e)}'
            }
    
    def _initialize_user_backpack(self, user_id):
        """初始化用戶背包子集合並設置魔法陣和藥水數量
        
        Args:
            user_id: 使用者ID
        """
        try:
            # 創建用戶背包子集合的引用
            user_ref = self.firestore_db.collection('users').document(user_id)
            backpack_ref = user_ref.collection('user_backpack')
            
            # 初始化魔法陣類型和數量
            magic_circles = [
                {
                    'item_type': 'magic_circle',
                    'item_name': 'normal',
                    'display_name': '普通魔法陣',
                    'count': 10,  # 初始給予10個普通魔法陣
                    'description': '基礎的魔法陣，成功率 60%',
                    'success_rate': 0.6,
                    'created_at': time.time()
                },
                {
                    'item_type': 'magic_circle',
                    'item_name': 'advanced',
                    'display_name': '進階魔法陣',
                    'count': 5,  # 初始給予5個進階魔法陣
                    'description': '進階的魔法陣，成功率 80%',
                    'success_rate': 0.8,
                    'created_at': time.time()
                },
                {
                    'item_type': 'magic_circle',
                    'item_name': 'premium',
                    'display_name': '高級魔法陣',
                    'count': 3,  # 初始給予3個高級魔法陣
                    'description': '高級的魔法陣，成功率 95%',
                    'success_rate': 0.95,
                    'created_at': time.time()
                }
            ]
            
            # 初始化藥水類型和數量
            potions = [
                {
                    'item_type': 'potion',
                    'item_name': 'normal_potion',
                    'display_name': '普通藥水',
                    'count': 1,  # 初始給予1個普通藥水
                    'description': '普通的捕捉藥水，輕微提升捕捉能力',
                    'effect': '捕捉率 1.13 倍',
                    'created_at': time.time()
                },
                {
                    'item_type': 'potion',
                    'item_name': 'advanced_potion',
                    'display_name': '進階藥水',
                    'count': 1,  # 初始給予1個進階藥水
                    'description': '進階捕捉藥水，顯著提升捕捉能力',
                    'effect': '捕捉率 1.25 倍',
                    'created_at': time.time()
                },
                {
                    'item_type': 'potion',
                    'item_name': 'premium_potion',
                    'display_name': '高級藥水',
                    'count': 1,  # 初始給予1個高級藥水
                    'description': '傳說中的捕捉藥水，大幅提升捕捉能力',
                    'effect': '捕捉率 1.50 倍',
                    'created_at': time.time()
                }
            ]
              # 將每個魔法陣類型添加到背包子集合中
            for circle in magic_circles:
                backpack_ref.document(circle['item_name']).set(circle)
            
            # 將每個藥水類型添加到背包子集合中
            for potion in potions:
                backpack_ref.document(potion['item_name']).set(potion)
            
            print(f"已為用戶 {user_id} 初始化背包，包含 {len(magic_circles)} 種魔法陣和 {len(potions)} 種藥水")
            
        except Exception as e:
            print(f"初始化用戶背包失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def get_user_backpack(self, user_id):
        """獲取用戶背包內容
        
        Args:
            user_id: 使用者ID
            
        Returns:
            dict: 背包內容，按物品類型組織
        """
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            backpack_ref = user_ref.collection('user_backpack').get()
            
            backpack_contents = {}
            
            for doc in backpack_ref:
                item_data = doc.to_dict()
                item_name = doc.id
                backpack_contents[item_name] = item_data
            
            return {
                'status': 'success',
                'backpack': backpack_contents
            }
            
        except Exception as e:
            print(f"獲取用戶背包失敗: {e}")
            return {
                'status': 'error',
                'message': f'獲取背包內容失敗: {str(e)}',
                'backpack': {}
            }
    
    def update_backpack_item(self, user_id, item_name, count_change):
        """更新背包中物品的數量
        
        Args:
            user_id: 使用者ID
            item_name: 物品名稱
            count_change: 數量變化（正數為增加，負數為減少）
            
        Returns:
            dict: 更新結果
        """
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            item_ref = user_ref.collection('user_backpack').document(item_name)
            
            # 獲取當前物品數據
            item_doc = item_ref.get()
            
            if not item_doc.exists:
                return {
                    'status': 'error',
                    'message': f'物品 {item_name} 不存在'
                }
            
            item_data = item_doc.to_dict()
            current_count = item_data.get('count', 0)
            new_count = max(0, current_count + count_change)  # 確保數量不會小於0
            
            # 更新數量
            item_ref.update({
                'count': new_count,
                'last_updated': time.time()
            })
            
            return {
                'status': 'success',
                'item_name': item_name,
                'old_count': current_count,
                'new_count': new_count,
                'change': count_change
            }
            
        except Exception as e:
            print(f"更新背包物品失敗: {e}")
            return {
                'status': 'error',
                'message': f'更新物品失敗: {str(e)}'
            }
    
    def generate_route_creatures(self, route_id, route_name, element_type, route_geometry=None, count=1, creatures_data=None, csv_route_name=None):
        """在特定公車路線上生成隨機精靈
        
        Args:
            route_id (str): 公車路線ID
            route_name (str): 公車路線名稱
            element_type (str): 路線元素類型 (fire, water, earth, air, electric, normal)
            route_geometry (dict, optional): 路線的GeoJSON幾何資訊，用於生成精靈位置
            count (int, optional): 要生成的精靈數量. 默認為 1.
            creatures_data (DataFrame, optional): 來自CSV的精靈數據
            csv_route_name (str, optional): CSV中對應的路線名稱
        
        Returns:
            list: 生成的精靈列表
        """
        try:
            from app.models.creature import ElementType
            import json
            from datetime import datetime, timedelta
            import time
            
            # 如果提供了CSV數據和路線名稱，使用CSV數據
            if creatures_data is not None and csv_route_name is not None:
                return self._generate_creatures_from_csv(
                    route_id, route_name, element_type, route_geometry, 
                    count, creatures_data, csv_route_name
                )
            
            # 否則使用原來的硬編碼方式 (向後兼容)
            return self._generate_creatures_legacy(
                route_id, route_name, element_type, route_geometry, count
            )
            
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
                if geometry_data:
                    coordinates = []
                    
                    # 檢查數據格式，處理 app/data/routes/ 中的路線數據格式
                    if 'data' in geometry_data:
                        # 路線格式: { "data": [ {"PositionLon": x, "PositionLat": y}, ... ] }
                        for point in geometry_data['data']:
                            if 'PositionLon' in point and 'PositionLat' in point:
                                coordinates.append({
                                    'lng': point['PositionLon'],
                                    'lat': point['PositionLat']
                                })
                    elif 'coordinates' in geometry_data:
                        # GeoJSON 格式: { "coordinates": [[lng, lat], [lng, lat], ...] }
                        for coord in geometry_data['coordinates']:
                            if len(coord) >= 2:
                                coordinates.append({
                                    'lng': coord[0],
                                    'lat': coord[1]
                                })
                    
                    # 從路線上隨機選擇點
                    if coordinates:
                        print(f"從路線上的 {len(coordinates)} 個點中選擇精靈位置")
                        for _ in range(count):
                            # 隨機選擇一個座標點作為精靈位置
                            random_point_index = random.randint(0, len(coordinates) - 1)
                            position = coordinates[random_point_index]
                            positions.append(position)
            
            # 如果無法從路線幾何資訊中獲取位置，使用預設位置
            if not positions:
                print("警告: 無法從路線數據中獲取座標點，使用預設位置範圍")
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
                
                # 根據精靈種類設置屬性範圍並生成隨機值
                if species == '一般種':
                    hp = random.randint(50, 100)
                    attack = random.randint(10, 30)
                elif species == '罕見種':
                    hp = random.randint(80, 150)
                    attack = random.randint(25, 45)
                elif species == '稀有種':
                    hp = random.randint(120, 200)
                    attack = random.randint(40, 70)
                else:  # 傳說種
                    hp = random.randint(180, 300)
                    attack = random.randint(65, 100)
                
                # 選擇隨機圖片URL
                if element_type in image_urls and image_urls[element_type]:
                    image_url = random.choice(image_urls[element_type])
                else:
                    image_url = default_image
                
                # 生成隨機ID
                random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
                
                # 創建精靈數據
                creature_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
                creature_data = {
                    'id': creature_id,
                    'random_id': random_id,
                    'name': name,
                    'species': species,
                    'element_type': element_enum.value,
                    'level': 1,
                    'experience': 0,
                    'attack': attack,  # 隨機生成的攻擊力
                    'hp': hp,  # 隨機生成的生命值
                    'image_url': image_url,
                    'position': position,  # 精靈位置
                    'bus_route_id': route_id,
                    'bus_route_name': route_name,
                    'generated_at': time.time(),
                    'expires_at': expiry_timestamp,  # 精靈過期時間 (5分鐘後)
                }
                
                # 儲存到 Firestore
                creature_ref = self.firestore_db.collection('route_creatures').document(creature_id)
                creature_ref.set(creature_data)
                
                # 添加到返回列表
                creatures.append(creature_data)
            
            print(f"已在路線 {route_name} (ID: {route_id}) 上生成 {len(creatures)} 隻精靈")
            return creatures
        except Exception as e:
            print(f"生成路線精靈失敗: {e}")
            import traceback
            traceback.print_exc()
            return []
    def _generate_creatures_from_csv(self, route_id, route_name, element_type, route_geometry, count, creatures_data, csv_route_name):
        """使用CSV數據生成精靈"""
        try:
            import json
            from datetime import datetime, timedelta
            import time
            
            # 篩選出屬於指定路線的精靈
            route_creatures = creatures_data[creatures_data['Route'] == csv_route_name]
            
            if route_creatures.empty:
                print(f"警告: 在CSV中找不到路線 {csv_route_name} 的精靈數據")
                return []
            
            print(f"找到 {len(route_creatures)} 隻可用於路線 {csv_route_name} 的精靈")
            
            # 解析路線幾何數據以獲取位置
            positions = self._parse_route_geometry(route_geometry, count)
            
            # 設定精靈存活時間 (5分鐘)
            expiry_time = datetime.now() + timedelta(minutes=5)
            expiry_timestamp = int(time.mktime(expiry_time.timetuple()))
            
            # 生成精靈
            creatures = []
            for position in positions:
                # 從該路線的精靈中隨機選擇一隻
                selected_creature = route_creatures.sample(n=1).iloc[0]
                
                # 根據CSV中的HP和ATK範圍生成隨機值
                hp = random.randint(int(selected_creature['HP_Min']), int(selected_creature['HP_Max']))
                attack = random.randint(int(selected_creature['ATK_Min']), int(selected_creature['ATK_Max']))
                
                # 轉換稀有度為種類
                rate_to_species = {
                    'N': '一般種',
                    'R': '罕見種', 
                    'SR': '稀有種',
                    'SSR': '傳說種'
                }
                species = rate_to_species.get(selected_creature['Rate'], '一般種')
                
                # 轉換元素類型
                type_mapping = {
                    'fire': 1,
                    'water': 2, 
                    'earth': 3,
                    'air': 4,
                    'electric': 5,
                    'wood': 3,  # 將wood映射為earth
                    'normal': 0
                }
                
                # 使用CSV中的Type或fallback到路線的element_type
                csv_element_type = selected_creature.get('Type', element_type).lower()
                element_type_value = type_mapping.get(csv_element_type, 0)
                
                # 生成隨機ID
                creature_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
                random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
                  # 創建精靈數據
                creature_data = {
                    'id': creature_id,
                    'random_id': random_id,
                    'name': selected_creature['C_Name'],
                    'en_name': selected_creature['EN_Name'],
                    'csv_id': str(selected_creature['ID']),
                    'species': species,
                    'type': selected_creature['Type'],  # 保存原始的精靈種類
                    'element_type': element_type_value,
                    'level': 1,
                    'experience': 0,
                    'attack': attack,  # 從CSV範圍生成的實際攻擊力
                    'hp': hp,  # 從CSV範圍生成的實際生命值
                    'image_url': selected_creature['Img'],
                    'position': position,
                    'bus_route_id': route_id,
                    'bus_route_name': route_name,
                    'csv_route': csv_route_name,
                    'rate': selected_creature['Rate'],
                    'generated_at': time.time(),
                    'expires_at': expiry_timestamp,  # 精靈過期時間 (5分鐘後)
                }
                
                # 儲存到 Firestore
                creature_ref = self.firestore_db.collection('route_creatures').document(creature_id)
                creature_ref.set(creature_data)
                
                # 添加到返回列表
                creatures.append(creature_data)
            
            print(f"已在路線 {route_name} (ID: {route_id}) 上生成 {len(creatures)} 隻精靈 (使用CSV數據)")
            return creatures
            
        except Exception as e:
            print(f"使用CSV數據生成路線精靈失敗: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_route_geometry(self, route_geometry, count):
        """解析路線幾何數據以獲取位置"""
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
            if geometry_data:
                coordinates = []
                
                # 檢查數據格式，處理 app/data/routes/ 中的路線數據格式
                if 'data' in geometry_data:
                    # 路線格式: { "data": [ {"PositionLon": x, "PositionLat": y}, ... ] }
                    for point in geometry_data['data']:
                        if 'PositionLon' in point and 'PositionLat' in point:
                            coordinates.append({
                                'lng': point['PositionLon'],
                                'lat': point['PositionLat']
                            })
                elif 'coordinates' in geometry_data:
                    # GeoJSON 格式: { "coordinates": [[lng, lat], [lng, lat], ...] }
                    for coord in geometry_data['coordinates']:
                        if len(coord) >= 2:
                            coordinates.append({
                                'lng': coord[0],
                                'lat': coord[1]
                            })
                
                # 從路線上隨機選擇點
                if coordinates:
                    print(f"從路線上的 {len(coordinates)} 個點中選擇精靈位置")
                    for _ in range(count):
                        # 隨機選擇一個座標點作為精靈位置
                        random_point_index = random.randint(0, len(coordinates) - 1)
                        position = coordinates[random_point_index]
                        positions.append(position)
        
        # 如果無法從路線幾何資訊中獲取位置，使用預設位置
        if not positions:
            print("警告: 無法從路線數據中獲取座標點，使用預設位置範圍")
            # 使用硬編碼的預設位置範圍 (台北市範圍)
            for _ in range(count):
                lat = random.uniform(25.01, 25.10)  # 台北市緯度範圍
                lng = random.uniform(121.50, 121.60)  # 台北市經度範圍
                positions.append({'lat': lat, 'lng': lng})
        
        return positions
    
    def _generate_creatures_legacy(self, route_id, route_name, element_type, route_geometry, count):
        """使用原來硬編碼方式生成精靈 (向後兼容)"""
        try:
            from app.models.creature import ElementType
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
                if geometry_data:
                    coordinates = []
                    
                    # 檢查數據格式，處理 app/data/routes/ 中的路線數據格式
                    if 'data' in geometry_data:
                        # 路線格式: { "data": [ {"PositionLon": x, "PositionLat": y}, ... ] }
                        for point in geometry_data['data']:
                            if 'PositionLon' in point and 'PositionLat' in point:
                                coordinates.append({
                                    'lng': point['PositionLon'],
                                    'lat': point['PositionLat']
                                })
                    elif 'coordinates' in geometry_data:
                        # GeoJSON 格式: { "coordinates": [[lng, lat], [lng, lat], ...] }
                        for coord in geometry_data['coordinates']:
                            if len(coord) >= 2:
                                coordinates.append({
                                    'lng': coord[0],
                                    'lat': coord[1]
                                })
                    
                    # 從路線上隨機選擇點
                    if coordinates:
                        print(f"從路線上的 {len(coordinates)} 個點中選擇精靈位置")
                        for _ in range(count):
                            # 隨機選擇一個座標點作為精靈位置
                            random_point_index = random.randint(0, len(coordinates) - 1)
                            position = coordinates[random_point_index]
                            positions.append(position)
            
            # 如果無法從路線幾何資訊中獲取位置，使用預設位置
            if not positions:
                print("警告: 無法從路線數據中獲取座標點，使用預設位置範圍")
                # 使用硬編碼的預設位置範圍 (台北市範圍)
                for _ in range(count):
                    lat = random.uniform(25.01, 25.10)  # 台北市緫度範圍
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
                
                # 根據精靈種類設置屬性範圍並生成隨機值
                if species == '一般種':
                    hp = random.randint(50, 100)
                    attack = random.randint(10, 30)
                elif species == '罕見種':
                    hp = random.randint(80, 150)
                    attack = random.randint(25, 45)
                elif species == '稀有種':
                    hp = random.randint(120, 200)
                    attack = random.randint(40, 70)
                else:  # 傳說種
                    hp = random.randint(180, 300)
                    attack = random.randint(65, 100)
                
                # 選擇隨機圖片URL
                if element_type in image_urls and image_urls[element_type]:
                    image_url = random.choice(image_urls[element_type])
                else:
                    image_url = default_image
                
                # 生成隨機ID
                random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
                
                # 創建精靈數據
                creature_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
                creature_data = {
                    'id': creature_id,
                    'random_id': random_id,
                    'name': name,
                    'species': species,
                    'element_type': element_enum.value,
                    'level': 1,
                    'experience': 0,
                    'attack': attack,  # 隨機生成的攻擊力
                    'hp': hp,  # 隨機生成的生命值
                    'image_url': image_url,
                    'position': position,  # 精靈位置
                    'bus_route_id': route_id,
                    'bus_route_name': route_name,
                    'generated_at': time.time(),
                    'expires_at': expiry_timestamp,  # 精靈過期時間 (5分鐘後)
                }
                
                # 儲存到 Firestore
                creature_ref = self.firestore_db.collection('route_creatures').document(creature_id)
                creature_ref.set(creature_data)
                
                # 添加到返回列表
                creatures.append(creature_data)
            
            print(f"已在路線 {route_name} (ID: {route_id}) 上生成 {len(creatures)} 隻精靈")
            return creatures
        except Exception as e:
            print(f"生成路線精靈失敗: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_route_creatures(self, route_id=None, player_id=None):
        """獲取指定路線上的所有未過期的精靈
        
        Args:
            route_id (str, optional): 公車路線ID。如果為None，返回所有路線上的精靈。
            player_id (str, optional): 玩家ID。如果提供，將過濾出該玩家尚未捕獲的精靈。
        
        Returns:
            list: 未過期的精靈列表，若提供player_id則只返回該玩家未捕獲的精靈
        """
        try:
            import time
            from datetime import datetime
            from google.api_core.exceptions import FailedPrecondition
            
            # 獲取當前時間戳
            current_timestamp = int(time.mktime(datetime.now().timetuple()))
            
            # 使用簡單查詢取得所有未過期的精靈
            query = self.firestore_db.collection('route_creatures')
            
            # 如果指定了路線ID，添加路線過濾條件
            if (route_id):
                query = query.where('bus_route_id', '==', route_id)
            
            try:
                # 執行查詢
                creatures_ref = query.get()
                
                creatures = []
                for doc in creatures_ref:
                    creature_data = doc.to_dict()
                    
                    # 在代碼中過濾過期精靈
                    if 'expires_at' in creature_data and creature_data['expires_at'] > current_timestamp:
                        # 如果提供了player_id，檢查該玩家是否已捕獲此精靈
                        if player_id:
                            # 檢查captured_players欄位
                            captured_players = creature_data.get('captured_players', '')
                            player_list = captured_players.split(',') if captured_players else []
                            
                            # 如果玩家已捕獲此精靈，則跳過
                            if player_id in player_list:
                                continue
                        
                        # 確保精靊數據包含必要的字段
                        if 'position' not in creature_data or not creature_data['position']:
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
                
                print(f"從Firestore獲取了 {len(creatures)} 隻未過期的精靈" +
                      (f"，其中 {len(creatures)} 隻尚未被玩家 {player_id} 捕獲" if player_id else ""))
                return creatures
                    
            except FailedPrecondition as e:
                # 如果仍然出現索引問題，嘗試完全簡化查詢然後在內存中過濾
                print(f"複合查詢失敗，進行簡單查詢並在代碼中過濾: {e}")
                all_creatures = self.firestore_db.collection('route_creatures').get()
                
                creatures = []
                for doc in all_creatures:
                    creature_data = doc.to_dict()
                    
                    # 在代碼中過濾條件
                    if (creature_data.get('expires_at', 0) > current_timestamp and
                        (route_id is None or creature_data.get('bus_route_id') == route_id)):
                        
                        # 如果提供了player_id，檢查該玩家是否已捕獲此精靈
                        if player_id:
                            captured_players = creature_data.get('captured_players', '')
                            player_list = captured_players.split(',') if captured_players else []
                            
                            # 如果玩家已捕獲此精靊，則跳過
                            if player_id in player_list:
                                continue
                        
                        # 確保精靊數據包含必要的字段
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
                        
                print(f"從Firestore簡單查詢後過濾獲得了 {len(creatures)} 隻未過期的精靈")
                return creatures
        except Exception as e:
            print(f"獲取路線精靊失敗: {e}")
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
            
            # 刪除已過期的精靈（包括子集合）
            count = 0
            for doc in expired_ref:
                try:
                    # 首先刪除 captured_players 子集合中的所有文檔
                    captured_players_ref = doc.reference.collection('captured_players').get()
                    for captured_player_doc in captured_players_ref:
                        captured_player_doc.reference.delete()
                    
                    # 然後刪除主精靈文檔
                    doc.reference.delete()
                    count += 1
                    
                except Exception as delete_error:
                    print(f"刪除精靈 {doc.id} 時發生錯誤: {delete_error}")
                    # 即使單個精靈刪除失敗，也繼續處理其他精靈
                    continue
            
            if count > 0:
                print(f"已刪除 {count} 隻過期精靈（包括其 captured_players 子集合）")            
            return count
        except Exception as e:
            print(f"刪除過期精靈失敗: {e}")
            return 0
    
    def catch_route_creature(self, creature_id, user_id, circle_type=None, capture_rate=None):
        """捕捉路線上的精靈
        
        Args:
            creature_id (str): 精靈ID
            user_id (str): 使用者ID
            circle_type (str, optional): 魔法陣類型 (normal/advanced/premium)
            capture_rate (float, optional): 實際使用的捕捉率
        
        Returns:
            dict: 捕捉結果
        """
        try:
            print(f">>> DEBUG: 開始嘗試捕捉精靈 ID: {creature_id}, 用戶 ID: {user_id}")
            if circle_type:
                print(f">>> DEBUG: 使用魔法陣類型: {circle_type}")
            if capture_rate is not None:
                print(f">>> DEBUG: 前端計算的捕捉率: {capture_rate}")
            
            # 步驟 1: 檢查精靈是否存在
            try:
                creature_ref = self.firestore_db.collection('route_creatures').document(creature_id)
                creature_doc = creature_ref.get()
                
                if not creature_doc.exists:
                    print(f">>> DEBUG: 找不到精靈，ID: {creature_id}")
                    return {
                        'success': False,
                        'message': '找不到該精靈，可能已被移除或過期'
                    }
                
                creature_data = creature_doc.to_dict()
                print(f">>> DEBUG: 找到精靈: {creature_data.get('name')}, 稀有度: {creature_data.get('rate', 'N')}")
            except Exception as e:
                print(f">>> DEBUG: 獲取精靈數據失敗: {e}")
                import traceback
                print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
                return {
                    'success': False,
                    'message': f'獲取精靈數據失敗: {str(e)}'
                }
            
            # 步驟 2: 獲取用戶資料以取得 player_id
            try:
                user_ref = self.firestore_db.collection('users').document(user_id)
                user_doc = user_ref.get()
                
                if not user_doc.exists:
                    print(f">>> DEBUG: 找不到用戶資料，嘗試生成新的 player_id 並創建基本用戶資料")
                    
                    # 生成一個新的 player_id
                    player_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    
                    # 創建基本用戶資料
                    user_data = {
                        'username': f'User_{player_id}',
                        'player_id': player_id,
                        'created_at': time.time()
                    }
                    
                    # 保存用戶資料
                    user_ref.set(user_data)
                    print(f">>> DEBUG: 已為用戶 {user_id} 創建新的基本資料，player_id: {player_id}")
                else:
                    user_data = user_doc.to_dict()
                    player_id = user_data.get('player_id')
                    
                    # 如果用戶沒有 player_id，生成一個並更新用戶資料
                    if not player_id:
                        player_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                        user_ref.update({'player_id': player_id})
                        print(f">>> DEBUG: 已為用戶 {user_id} 更新 player_id: {player_id}")
                    else:
                        print(f">>> DEBUG: 用戶 {user_id} 已有 player_id: {player_id}")
                
                print(f">>> DEBUG: 使用 player_id: {player_id}")
            except Exception as e:
                print(f">>> DEBUG: 獲取或創建用戶資料失敗: {e}")
                import traceback
                print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
                return {
                    'success': False,
                    'message': f'獲取用戶資料失敗: {str(e)}'
                }
            
            # 步驟 3: 檢查精靈是否已被此玩家捕捉 (使用子集合)
            try:
                # 檢查 captured_players 子集合中是否已包含此玩家
                player_capture_ref = creature_ref.collection('captured_players').document(player_id)
                player_capture_doc = player_capture_ref.get()
                
                if player_capture_doc.exists:
                    print(f">>> DEBUG: 玩家 {player_id} 已經捕捉過精靈 {creature_id}")
                    return {
                        'success': False,
                        'message': '你已經捕捉過這隻精靈了'
                    }
            except Exception as e:
                print(f">>> DEBUG: 檢查玩家捕捉狀態失敗: {e}")
                import traceback
                print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
                return {
                    'success': False,
                    'message': f'檢查捕捉狀態失敗: {str(e)}'
                }
            
            # 步驟 4: 將此玩家添加到精靈的捕獲子集合中
            try:
                # 在精靈的 captured_players 子集合中添加此玩家
                capture_data = {
                    'player_id': player_id,
                    'user_id': user_id,
                    'captured_at': time.time()
                }
                player_capture_ref.set(capture_data)
                
                # 更新精靈主文件的捕捉時間
                creature_ref.update({
                    'last_captured_at': time.time()
                })
                
                print(f">>> DEBUG: 已將玩家 {player_id} 添加到精靈 {creature_id} 的捕獲列表中")
            except Exception as e:
                print(f">>> DEBUG: 更新精靈捕獲列表失敗: {e}")
                import traceback
                print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
                return {
                    'success': False,
                    'message': f'更新精靈捕獲列表失敗: {str(e)}'
                }
            
            # 步驟 5: 添加精靈到用戶的收藏子集合中
            try:
                user_creature_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
                
                # 確保有攻擊力值（兼容舊值 power 和新值 attack）
                attack_value = creature_data.get('attack', creature_data.get('power', 10))
                
                # 安全處理 element_type
                element_type = creature_data.get('element_type')
                if isinstance(element_type, int):
                    try:
                        from app.models.creature import ElementType
                        element_type = ElementType(element_type).name.lower()
                    except:
                        element_type = 'normal'
                elif not element_type:
                    element_type = 'normal'                # 精靈數據
                user_creature_data = {
                    'id': user_creature_id,
                    'original_creature_id': creature_id,
                    'random_id': creature_data.get('random_id', ''),
                    'name': creature_data.get('name', '未知精靈'),
                    'rate': creature_data.get('rate', 'N'),  # 使用原始 rate 值 (SSR/SR/R/N)
                    'species': creature_data.get('species', '一般種'),  # 保留 species 作為備份
                    'type': creature_data.get('type', ''),  # 保存原始的精靈種類
                    'element_type': element_type,
                    'level': 1,  # 初始等級
                    'experience': 0,  # 初始經驗值
                    'max_experience': 100,  # 升級所需經驗值（可根據等級調整）
                    'attack': attack_value,
                    'hp': creature_data.get('hp', 100),
                    'image_url': creature_data.get('image_url', ''),
                    'bus_route_id': creature_data.get('bus_route_id', ''),
                    'bus_route_name': creature_data.get('bus_route_name', ''),
                    'captured_at': time.time()
                }
                
                print(f">>> DEBUG: 精靊數據準備完成，即將添加到用戶收藏: {user_creature_data}")
                
                # 儲存到用戶的 user_creatures 子集合中
                user_ref.collection('user_creatures').document(user_creature_id).set(user_creature_data)
                
                # 同時保留在全局 user_creatures 集合中 (兼容現有程式碼) <--- 這部分將被移除或註解
                # self.firestore_db.collection('user_creatures').document(user_creature_id).set({
                #     **user_creature_data,
                #     'user_id': user_id,
                #     'player_id': player_id
                # })
                
                print(f">>> DEBUG: 精靈已成功添加到用戶的收藏: {user_creature_id}")
            except Exception as e:
                print(f">>> DEBUG: 添加精靈到用戶收藏失敗: {e}")
                import traceback
                print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
                return {
                    'success': False,
                    'message': f'添加精靊到用戶收藏失敗: {str(e)}'
                }
              # 步驟 6: 同步道館資料 (如有必要)
            try:
                if 'arena_id' in creature_data and creature_data['arena_id']:
                    arena_id = creature_data['arena_id']
                    # 檢查道館是否存在於 Firebase
                    arena_ref = self.firestore_db.collection('arenas').document(arena_id)
                    arena_doc = arena_ref.get()
                    
                    if not arena_doc.exists:
                        # 如果道館不存在，從本地緩存獲取道館資料並保存到 Firebase
                        try:
                            from app.models.arena import get_arena_from_cache
                            arena_data = get_arena_from_cache(arena_id=arena_id)
                            if arena_data:
                                # 保存道館資料到 Firebase
                                arena_ref.set(arena_data)
                                print(f">>> DEBUG: 已同步道館 {arena_data.get('name', arena_id)} 到 Firebase")
                        except Exception as arena_error:
                            print(f">>> DEBUG: 同步道館資料失敗 (非致命錯誤): {arena_error}")
            except Exception as e:
                # 這個錯誤不影響捕捉結果，只是記錄
                print(f">>> DEBUG: 同步道館資料失敗 (非致命錯誤): {e}")            # 步驟 7: 為新捕捉的精靈添加經驗值獎勵，並為用戶添加經驗值
            try:
                # 根據精靈稀有度決定經驗值獎勵
                rate = creature_data.get('rate', 'N')
                experience_rewards = {
                    'N': 20,
                    'R': 40, 
                    'SR': 60,
                    'SSR': 80
                }
                experience_amount = experience_rewards.get(rate, 20)
                print(f">>> DEBUG: 根據稀有度 {rate} 獲得 {experience_amount} 經驗值")
                
                # 為精靈添加經驗值
                exp_result = self.add_experience_to_creature(user_id, user_creature_id, experience_amount=experience_amount)
                if exp_result.get('success'):
                    print(f">>> DEBUG: 已為新精靈 {user_creature_id} 添加捕捉經驗值獎勵")
                    # 更新返回的精靈數據，包含最新的經驗值和等級信息
                    user_creature_data.update({
                        'level': exp_result.get('new_level', 1),
                        'experience': exp_result.get('current_experience', experience_amount),
                        'max_experience': exp_result.get('max_experience', 100)
                    })
                else:
                    print(f">>> DEBUG: 添加捕捉經驗值失敗: {exp_result.get('message', '未知錯誤')}")                  # 為用戶添加經驗值
                user_exp_result = self.add_experience_to_user(user_id, experience_amount)
                if user_exp_result.get('success'):
                    print(f">>> DEBUG: 已為用戶 {user_id} 添加 {experience_amount} 經驗值")
                    print(f">>> DEBUG: 用戶等級更新 - 舊等級: {user_exp_result.get('old_level')}, 新等級: {user_exp_result.get('new_level')}")
                else:
                    print(f">>> DEBUG: 為用戶添加經驗值失敗: {user_exp_result.get('message', '未知錯誤')}")
                    
            except Exception as exp_error:
                print(f">>> DEBUG: 添加經驗值時發生錯誤 (非致命): {exp_error}")
            
            print(f">>> DEBUG: 精靈捕捉完全成功: {creature_data.get('name', '未知精靈')}")
            
            # 準備返回數據
            response_data = {
                'success': True,
                'message': f"已成功捕捉 {creature_data.get('name', '未知精靈')}!",
                'creature': user_creature_data
            }
            
            # 添加用戶等級更新信息（如果有的話）
            try:
                if user_exp_result and user_exp_result.get('success'):
                    response_data['user_level_info'] = {
                        'old_level': user_exp_result.get('old_level'),
                        'new_level': user_exp_result.get('new_level'),
                        'level_up': user_exp_result.get('level_up', False),
                        'current_experience': user_exp_result.get('current_experience'),
                        'experience_gained': user_exp_result.get('experience_gained')
                    }
                    print(f">>> DEBUG: 已添加用戶等級信息到回應: {response_data['user_level_info']}")
            except:
                print(f">>> DEBUG: 添加用戶等級信息時發生錯誤，但不影響捕捉結果")
                pass
            
            # 添加經驗值獲得信息（如果有的話）
            try:
                rate = creature_data.get('rate', 'N')
                experience_rewards = {
                    'N': 20, 'R': 40, 'SR': 60, 'SSR': 80
                }
                experience_gained = experience_rewards.get(rate, 20)
                response_data['experience_gained'] = experience_gained
                response_data['creature_rate'] = rate
            except:
                pass
                
            return response_data
        except Exception as e:
            print(f">>> DEBUG: 捕捉精靈過程中發生未預期錯誤: {e}")
            import traceback
            print(f">>> DEBUG: 完整錯誤詳情: {traceback.format_exc()}")
            return {
                'success': False,
                'message': f'捕捉精靈時發生錯誤: {str(e)}'
            }
    
    def capture_tutorial_creature(self, user_id, creature_id):
        """捕捉教學模式中的精靈
        
        Args:
            user_id (str): 使用者ID
            creature_id (str): 精靈ID（用於教學模式）
        
        Returns:
            dict: 捕捉結果
        """
        import random
        import re
        import string
        import time
        
        try:
            print(f">>> DEBUG: 開始捕捉教學精靈 ID: {creature_id}, 用戶 ID: {user_id}")
            
            # 教學模式中的預設精靈資料
            tutorial_creatures = {
                'tutorial_fire': {
                    'name': '教學火龍',
                    'species': '一般種',
                    'type': 'fire',
                    'element_type': 1,  # 火屬性
                    'hp': 80,
                    'attack': 35,
                    'image_url': 'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Ftutorial_fire.png'
                },
                'tutorial_water': {
                    'name': '教學水龜',
                    'species': '一般種', 
                    'type': 'water',
                    'element_type': 2,  # 水屬性
                    'hp': 90,
                    'attack': 30,
                    'image_url': 'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Ftutorial_water.png'
                },
                'tutorial_earth': {
                    'name': '教學土熊',
                    'species': '一般種',
                    'type': 'earth', 
                    'element_type': 3,  # 土屬性
                    'hp': 100,
                    'attack': 25,
                    'image_url': 'https://firebasestorage.googleapis.com/v0/b/YOUR_BUCKET/o/creatures%2Ftutorial_earth.png'
                }
            }
              # 檢查是否為有效的教學精靈
            creature_template = None
            
            if creature_id in tutorial_creatures:
                # 使用預定義的固定教學精靈
                creature_template = tutorial_creatures[creature_id]
                print(f">>> DEBUG: 使用固定教學精靈模板: {creature_id}")
            elif creature_id.startswith('tutorial_'):
                # 處理動態生成的教學精靈 ID (格式: tutorial_obnuxis_數字_數字 或 tutorial_數字_數字)
                if re.match(r'^tutorial_[a-zA-Z0-9_]+_\d+_\d+$', creature_id):
                    # 使用蒙昧精靈模板（教學模式固定精靈）
                    creature_template = {
                        'name': '蒙昧',
                        'species': '超稀有種',
                        'type': 'dark',  # 暗系
                        'element_type': 1,  # 暗屬性
                        'hp': random.randint(2700, 2800),  # HP範圍：2700-2800
                        'attack': random.randint(500, 550),  # ATK範圍：500-550
                        'image_url': 'https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/68390f3c001270e4def2/view?project=681c5c6b002355634f3c&mode=admin'
                    }
                    print(f">>> DEBUG: 使用蒙昧精靈模板: {creature_id}")
                else:
                    print(f">>> DEBUG: 無效的動態教學精靈ID格式: {creature_id}")
                    return {
                        'status': 'error',
                        'message': '無效的教學精靈ID格式'
                    }
            else:
                print(f">>> DEBUG: 無效的教學精靈ID: {creature_id}")
                return {
                    'status': 'error',
                    'message': '無效的教學精靈ID'
                }
            if not creature_template:
                return {
                    'status': 'error',
                    'message': '無法找到教學精靈模板'
                }
              # 獲取或創建用戶資料
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                # 創建基本用戶資料
                player_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                user_data = {
                    'username': f'User_{player_id}',
                    'player_id': player_id,
                    'created_at': time.time()
                }
                user_ref.set(user_data)
                print(f">>> DEBUG: 已為用戶 {user_id} 創建新的基本資料，player_id: {player_id}")
                
                # 初始化用戶背包
                try:
                    self._initialize_user_backpack(user_id)
                    print(f">>> DEBUG: 已為教學用戶 {user_id} 初始化背包")
                except Exception as e:
                    print(f">>> DEBUG: 初始化教學用戶背包失敗: {e}")
            else:
                user_data = user_doc.to_dict()
                player_id = user_data.get('player_id')
                if not player_id:
                    player_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    user_ref.update({'player_id': player_id})
                    print(f">>> DEBUG: 已為用戶 {user_id} 更新 player_id: {player_id}")
                
                # 檢查是否需要初始化背包
                backpack_ref = user_ref.collection('user_backpack').get()
                if not backpack_ref:
                    try:
                        self._initialize_user_backpack(user_id)
                        print(f">>> DEBUG: 已為現有教學用戶 {user_id} 初始化背包")
                    except Exception as e:
                        print(f">>> DEBUG: 初始化現有教學用戶背包失敗: {e}")
            
            # 檢查是否已經捕捉過此教學精靈
            existing_creature = user_ref.collection('user_creatures').where('tutorial_id', '==', creature_id).get()
            
            if existing_creature:
                print(f">>> DEBUG: 用戶已捕捉過教學精靈: {creature_id}")
                # 返回已存在的精靈資料
                existing_data = existing_creature[0].to_dict()
                return {
                    'status': 'success', 
                    'message': f"您已經擁有 {creature_template['name']}！",
                    'creature': existing_data,
                    'already_captured': True
                }
            
            # 創建新的用戶精靈
            user_creature_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
            
            user_creature_data = {
                'id': user_creature_id,
                'tutorial_id': creature_id,  # 標記為教學精靈
                'name': creature_template['name'],
                'species': creature_template['species'],
                'type': creature_template['type'],
                'element_type': creature_template['element_type'],
                'level': 1,
                'experience': 0,
                'attack': creature_template['attack'],
                'hp': creature_template['hp'],
                'image_url': creature_template['image_url'],
                'bus_route_id': 'tutorial',
                'bus_route_name': '教學模式',
                'captured_at': time.time(),
                'is_tutorial': True  # 標記為教學精靈
            }
              # 保存到用戶的精靈子集合中
            user_ref.collection('user_creatures').document(user_creature_id).set(user_creature_data)
            
            print(f">>> DEBUG: 教學精靈捕捉成功: {creature_template['name']}")
            
            return {
                'status': 'success',
                'message': f"已成功捕捉 {creature_template['name']}！",
                'creature': user_creature_data,
                'already_captured': False
            }
            
        except Exception as e:
            print(f">>> DEBUG: 捕捉教學精靈失敗: {e}")
            import traceback
            print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
            return {
                'status': 'error',
                               'message': f'捕捉教學精靈失敗: {str(e)}'
            }

    def save_tutorial_creature(self, user_id, creature_data):
        """保存教學精靈到Firebase
        
        Args:
            user_id (str): 使用者ID
            creature_data (dict): 教學精靈資料
            
        Returns:
            dict: 保存結果
        """
        try:
            print(f">>> DEBUG: 保存教學精靈 ID: {creature_data.get('id')}, 用戶 ID: {user_id}")
            
            # 保存到教學精靈集合中
            tutorial_ref = self.firestore_db.collection('tutorial_creatures').document(creature_data['id'])
            
            # 添加額外的元數據
            tutorial_creature_data = {
                **creature_data,
                'created_for_user': user_id,
                'created_at': time.time(),
                'is_tutorial': True,
                'captured': False  # 初始狀態為未捕獲
            }
            
            tutorial_ref.set(tutorial_creature_data)
            
            print(f">>> DEBUG: 教學精靈已保存: {creature_data.get('name', '未知精靈')}")
            
            return {
                'status': 'success',
                'message': '教學精靈保存成功',
                'creature_id': creature_data['id']
            }
            
        except Exception as e:
            print(f">>> DEBUG: 保存教學精靈失敗: {e}")
            import traceback
            print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
            return {
                'status': 'error',
                'message': f'保存教學精靈失敗: {str(e)}'
            }

    # 新增 - 將精靈資料緩存到CSV文件
    def cache_creatures_to_csv(self):
        """從Firebase抓取精靈資料並緩存到CSV文件
        
        Returns:
            int: 緩存的精靈數量
        """
        try:            # 獲取所有未捕捉且未過期的精靊
            creatures = self.get_route_creatures()
            
            if not creatures:
                logging.warning("沒有可緩存的精靈，返回空數據")
                # 創建一個空的DataFrame並保存，確保文件存在
                empty_df = pd.DataFrame(columns=['id', 'name', 'type', 'rate', 'hp', 'attack', 
                                                'route_id', 'route_name', 'lat', 'lng', 
                                                'created_at', 'expires_at', 'image_url'])
                csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'creatures', 'current_creatures.csv')
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)
                empty_df.to_csv(csv_path, index=False, encoding='utf-8')
                return 0
            
            # 將精靈資料轉換為DataFrame格式
            creatures_data = []
            for creature in creatures:                # 提取位置資訊
                position = creature.get('position', {})
                lat = position.get('lat', 0)
                lng = position.get('lng', 0)
                
                # 創建行數據
                row = {
                    'id': creature.get('id', ''),
                    'name': creature.get('name', '未知精靈'),
                    'type': creature.get('type', ''),  # 精靈的type字段
                    'rate': creature.get('rate', ''),  # 精靈稀有度
                    'hp': creature.get('hp', 100),
                    'attack': creature.get('attack', 50),
                    'route_id': creature.get('route_id', ''),
                    'route_name': creature.get('route_name', ''),
                    'lat': lat,
                    'lng': lng,
                    'created_at': creature.get('created_at', ''),
                    'expires_at': creature.get('expires_at', ''),
                    'image_url': creature.get('image_url', '')
                }
                creatures_data.append(row)
              # 創建DataFrame
            df = pd.DataFrame(creatures_data)
            # 保存到CSV文件 (主遊戲緩存存放至 app/data/creatures/)
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'creatures', 'firebase_cached_creatures.csv')
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            print(f"已緩存 {len(creatures_data)} 隻精靈到 CSV 文件: {csv_path}")
            return df
            
        except Exception as e:
            print(f"緩存精靈數據失敗: {e}")
            return None

    # 新增 - 從CSV文件讀取精靈資料
    def get_creatures_from_csv(self):
        """從CSV文件讀取緩存的精靈資料
        
        Returns:
            list: 精靈資料列表，格式與Firebase兼容
        """
        try:
            import pandas as pd
            import os
              # CSV文件路徑 (主遊戲緩存存放至 app/data/creatures/)
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'creatures', 'firebase_cached_creatures.csv')
            
            # 檢查文件是否存在
            if not os.path.exists(csv_path):
                print(f"CSV文件不存在: {csv_path}")
                return []
            
            # 讀取CSV文件
            try:
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
            except UnicodeDecodeError:
                # 如果UTF-8失敗，嘗試其他編碼
                try:
                    df = pd.read_csv(csv_path, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(csv_path, encoding='big5')
            
            if df.empty:
                print("CSV文件為空")
                return []
            
            # 將DataFrame轉換為與Firebase兼容的格式
            creatures = []
            for _, row in df.iterrows():
                # 構建位置信息
                position = {
                    'lat': float(row.get('lat', 0)) if pd.notna(row.get('lat')) else 0,
                    'lng': float(row.get('lng', 0)) if pd.notna(row.get('lng')) else 0
                }                # 構建精靈數據，與Firebase格式兼容
                creature_data = {
                    'id': str(row.get('id', '')),
                    'name': str(row.get('name', '未知精靈')),
                    'type': str(row.get('type', '')),  # 精靈的type字段
                    'rate': str(row.get('rate', '')),  # 精靈稀有度
                    'hp': int(row.get('hp', 100)) if pd.notna(row.get('hp')) else 100,
                    'attack': int(row.get('attack', 50)) if pd.notna(row.get('attack')) else 50,
                    'position': position,
                    'bus_route_id': str(row.get('route_id', '')),
                    'bus_route_name': str(row.get('route_name', '')),
                    'image_url': str(row.get('image_url', '')),
                    'expires_at': int(row.get('expires_at', 0)) if pd.notna(row.get('expires_at')) else 0,
                    'created_at': int(row.get('created_at', 0)) if pd.notna(row.get('created_at')) else 0
                }
                
                creatures.append(creature_data)
            
            print(f"從CSV文件讀取了 {len(creatures)} 隻精靈")
            return creatures
            
        except Exception as e:
            print(f"讀取CSV精靈數據失敗: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def save_user_base_gym(self, user_id, gym_data):
        """保存使用者的基地道館
        
        Args:
            user_id (str): 使用者ID
            gym_data (dict): 道館資料
            
        Returns:
            dict: 保存結果
        """
        try:
            print(f">>> DEBUG: 保存基地道館 ID: {gym_data.get('gym_id')}, 用戶 ID: {user_id}")
            
            # 準備基地道館資料
            base_gym_data = {
                'user_id': user_id,
                'gym_id': gym_data.get('gym_id'),
                'gym_name': gym_data.get('gym_name'),
                'gym_level': gym_data.get('gym_level', 5),
                'lat': gym_data.get('lat'),
                'lng': gym_data.get('lng'),
                'guardian_creature': gym_data.get('guardian_creature', {}),
                'established_at': time.time(),
                'is_tutorial_base': True,  # 標記為教學基地
                'status': 'active'
            }
              # 保存到 user_base_gyms 集合中
            base_gym_ref = self.firestore_db.collection('user_base_gyms').document(f"{user_id}_{gym_data.get('gym_id')}")
            base_gym_ref.set(base_gym_data)
            
            # 保存到用戶的 user_arenas 子集合中 (重要：用於用戶道館管理)
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_arena_ref = user_ref.collection('user_arenas').document(gym_data.get('gym_id'))
            
            user_arena_data = {
                'arena_id': gym_data.get('gym_id'),
                'arena_name': gym_data.get('gym_name'),
                'level': gym_data.get('gym_level', 5),
                'position': {
                    'lat': gym_data.get('lat'),
                    'lng': gym_data.get('lng')
                },
                'guardian_creature': gym_data.get('guardian_creature', {}),
                'occupied_at': time.time(),
                'is_base_gym': True,  # 標記為基地道館
                'is_tutorial': True,  # 標記為教學道館
                'status': 'occupied',
                'owner_id': user_id            }
            
            user_arena_ref.set(user_arena_data)
            
            # 確保用戶文檔存在，然後更新或創建用戶資料
            user_doc = user_ref.get()
            if not user_doc.exists:
                # 如果用戶文檔不存在，先創建基本用戶資料
                print(f">>> DEBUG: 用戶文檔不存在，創建基本用戶資料: {user_id}")
                user_basic_data = {
                    'username': f'TutorialUser_{user_id}',
                    'player_id': user_id,
                    'created_at': time.time(),
                    'is_tutorial_user': True,
                    'current_base_gym': {
                        'gym_id': gym_data.get('gym_id'),
                        'gym_name': gym_data.get('gym_name'),
                        'established_at': time.time()
                    },
                    'tutorial_completed': {
                        'base_selection': True,
                        'completed_at': time.time()
                    }
                }
                user_ref.set(user_basic_data)
            else:
                # 用戶文檔存在，進行更新
                user_ref.update({
                    'current_base_gym': {
                        'gym_id': gym_data.get('gym_id'),
                        'gym_name': gym_data.get('gym_name'),
                        'established_at': time.time()
                    },
                    'tutorial_completed': {
                        'base_selection': True,
                        'completed_at': time.time()
                    }
                })
            print(f">>> DEBUG: 基地道館保存成功: {gym_data.get('gym_name')}")
            print(f">>> DEBUG: 已保存到 user_base_gyms 集合和 users/{user_id}/user_arenas 子集合")
            
            # 觸發成就檢查 - 道館佔領成就
            try:
                print(f">>> DEBUG: 觸發道館佔領成就檢查，用戶ID: {user_id}")
                triggered_achievements = self.trigger_achievement_check(
                    user_id,
                    'gym_occupied',
                    {
                        'gym_id': gym_data.get('gym_id'),
                        'gym_name': gym_data.get('gym_name'),
                        'is_base_gym': True
                    }
                )
                
                # 記錄新獲得的成就
                if triggered_achievements:
                    print(f">>> DEBUG: 用戶獲得道館成就: {[ach.get('achievement_name', ach.get('achievement_id')) for ach in triggered_achievements]}")
                    
            except Exception as achievement_error:
                print(f">>> ERROR: 觸發道館佔領成就檢查失敗: {achievement_error}")
                # 不影響道館建立結果，僅記錄錯誤
            
            return {
                'status': 'success',
                'message': f"已成功建立基地: {gym_data.get('gym_name')}",
                'base_gym_data': base_gym_data
            }
            
        except Exception as e:
            print(f">>> DEBUG: 保存基地道館失敗: {e}")
            import traceback
            print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
            return {
                'status': 'error',
                'message': f'保存基地道館失敗: {str(e)}'
            }

    def toggle_creature_favorite(self, user_id, creature_id):
        """切換精靈的我的最愛狀態
        
        Args:
            user_id (str): 使用者ID
            creature_id (str): 精靈ID
        
        Returns:
            dict: 操作結果，包含 success, favorite, message
        """
        try:
            print(f">>> DEBUG: 切換精靈我的最愛狀態 - 用戶: {user_id}, 精靈: {creature_id}")
            
            # 獲取精靈文檔
            creature_ref = self.firestore_db.collection('users').document(user_id).collection('user_creatures').document(creature_id)
            creature_doc = creature_ref.get()
            
            if not creature_doc.exists:
                print(f">>> DEBUG: 精靈不存在: {creature_id}")
                return {
                    'success': False,
                    'message': '精靈不存在'
                }
            
            # 獲取當前狀態並切換
            current_data = creature_doc.to_dict()
            current_favorite = current_data.get('favorite', False)
            new_favorite = not current_favorite
            
            print(f">>> DEBUG: 當前我的最愛狀態: {current_favorite}, 新狀態: {new_favorite}")
            
            # 更新 Firebase
            creature_ref.update({'favorite': new_favorite})
            
            message = '已加入我的最愛' if new_favorite else '已移出我的最愛'
            print(f">>> DEBUG: 更新成功 - {message}")
            
            return {
                'success': True,
                'favorite': new_favorite,
                'message': message
            }
            
        except Exception as e:
            print(f">>> DEBUG: 更新我的最愛狀態失敗: {e}")
            import traceback
            print(f">>> DEBUG: 錯誤詳情: {traceback.format_exc()}")
            return {
                'success': False,
                'message': f'更新失敗: {str(e)}'
            }
    
    def add_experience_to_creature(self, user_id, creature_id, experience_amount=10):
        """為精靈添加經驗值並處理等級提升
        
        Args:
            user_id (str): 用戶ID
            creature_id (str): 精靈ID（user_creatures 子集合中的文檔ID）
            experience_amount (int): 要添加的經驗值數量
            
        Returns:
            dict: 包含更新結果和是否升級的信息
        """
        try:
            # 獲取精靈資料
            user_ref = self.firestore_db.collection('users').document(user_id)
            creature_ref = user_ref.collection('user_creatures').document(creature_id)
            creature_doc = creature_ref.get()
            
            if not creature_doc.exists:
                return {
                    'success': False,
                    'message': '找不到指定精靈'
                }
            
            creature_data = creature_doc.to_dict()
            current_level = creature_data.get('level', 1)
            current_exp = creature_data.get('experience', 0)
            max_exp = creature_data.get('max_experience', 100)
            
            # 添加經驗值
            new_exp = current_exp + experience_amount
            level_up = False
            new_level = current_level
            
            # 檢查是否升級（可以連續升級）
            while new_exp >= max_exp and new_level < 100:  # 假設最高等級為100
                new_exp -= max_exp
                new_level += 1
                level_up = True
                # 每升一級，所需經驗值增加
                max_exp = self._calculate_max_experience(new_level)
            
            # 更新精靈資料
            update_data = {
                'experience': new_exp,
                'level': new_level,
                'max_experience': max_exp
            }
              # 升級時不增加攻擊力和生命值 (已移除稀有度加成功能)
            
            creature_ref.update(update_data)
            
            return {
                'success': True,
                'level_up': level_up,
                'old_level': current_level,
                'new_level': new_level,
                'experience_gained': experience_amount,
                'current_experience': new_exp,
                'max_experience': max_exp,
                'message': f'獲得 {experience_amount} 經驗值！' +                          (f'恭喜升級至 {new_level} 級！' if level_up else '')
            }
            
        except Exception as e:
            print(f">>> DEBUG: 添加經驗值失敗: {e}")
            return {
                'success': False,
                'message': f'添加經驗值失敗: {str(e)}'
            }
    
    def add_experience_to_user(self, user_id, experience_amount=20):
        """為用戶添加經驗值並處理等級提升
        
        Args:
            user_id (str): 用戶ID
            experience_amount (int): 要添加的經驗值數量
            
        Returns:
            dict: 包含更新結果和是否升級的信息
        """
        try:
            # 獲取用戶資料
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {
                    'success': False,
                    'message': '找不到指定用戶'
                }
            
            user_data = user_doc.to_dict()
            current_level = user_data.get('level', 1)
            current_exp = user_data.get('experience', 0)
            
            # 添加經驗值
            new_exp = current_exp + experience_amount
            level_up = False
            new_level = current_level
            
            # 檢查是否升級（可以連續升級）
            while new_level < 100:  # 假設最高等級為100
                max_exp = self._calculate_max_experience(new_level)
                if new_exp >= max_exp:
                    new_exp -= max_exp
                    new_level += 1
                    level_up = True
                else:
                    break
            
            # 更新用戶資料
            update_data = {
                'experience': new_exp,
                'level': new_level
            }
            
            user_ref.update(update_data)
            
            return {
                'success': True,
                'level_up': level_up,
                'old_level': current_level,
                'new_level': new_level,
                'experience_gained': experience_amount,
                'current_experience': new_exp,
                'max_experience': self._calculate_max_experience(new_level),
                'message': f'獲得 {experience_amount} 經驗值！' + 
                          (f'恭喜升級至 {new_level} 級！' if level_up else '')
            }
            
        except Exception as e:
            print(f">>> DEBUG: 為用戶添加經驗值失敗: {e}")
            return {
                'success': False,
                'message': f'為用戶添加經驗值失敗: {str(e)}'
            }
    
    def _calculate_max_experience(self, level):
        """計算指定等級所需的最大經驗值"""
        # 使用簡單的線性增長公式
        return 100 + (level - 1) * 50
    
    # ==================== 成就系統相關方法 ====================
    
    def initialize_user_achievements(self, user_id):
        """初始化用戶成就數據
        
        Args:
            user_id (str): 用戶ID
        """
        try:
            from app.models.achievement import ACHIEVEMENTS
            
            user_ref = self.firestore_db.collection('users').document(user_id)
            achievements_ref = user_ref.collection('user_achievements')
            
            # 為每個成就創建初始記錄
            batch = self.firestore_db.batch()
            
            for achievement_id, achievement in ACHIEVEMENTS.items():
                achievement_doc_ref = achievements_ref.document(achievement_id)
                achievement_data = {
                    'achievement_id': achievement_id,
                    'completed': False,
                    'progress': 0,
                    'target_value': achievement.target_value,
                    'completed_at': None,
                    'created_at': time.time()
                }
                batch.set(achievement_doc_ref, achievement_data)
            
            batch.commit()
            print(f"已為用戶 {user_id} 初始化 {len(ACHIEVEMENTS)} 個成就")
            
        except Exception as e:
            print(f"初始化用戶成就失敗: {e}")
    
    def get_user_achievements(self, user_id):
        """獲取用戶成就進度
        
        Args:
            user_id (str): 用戶ID
            
        Returns:
            dict: 成就進度數據
        """
        try:
            from app.models.achievement import ACHIEVEMENTS, get_achievements_by_category, CATEGORY_DISPLAY_NAMES, CATEGORY_ICONS, get_achievement_by_id
            
            user_ref = self.firestore_db.collection('users').document(user_id)
            achievements_ref = user_ref.collection('user_achievements')
            
            # 檢查是否已初始化成就
            achievements_docs = achievements_ref.get()
            if not achievements_docs:
                self.initialize_user_achievements(user_id)
                achievements_docs = achievements_ref.get()
            
            # 構建用戶成就數據
            user_achievements = {}
            for doc in achievements_docs:
                achievement_data = doc.to_dict()
                achievement_id = doc.id
                
                # 獲取成就定義
                achievement_def = ACHIEVEMENTS.get(achievement_id)
                if achievement_def:
                    user_achievements[achievement_id] = {
                        **achievement_data,
                        'name': achievement_def.name,
                        'description': achievement_def.description,
                        'icon': achievement_def.icon,
                        'category': achievement_def.category.value,
                        'reward_points': achievement_def.reward_points,
                        'hidden': achievement_def.hidden
                    }
              # 按類別分組
            categories = get_achievements_by_category()
            categorized_achievements = {}
            
            for category_name, achievements_list in categories.items():
                # 找到對應的enum來獲取顯示名稱和圖標
                category_enum = None
                for enum_val in CATEGORY_DISPLAY_NAMES.keys():
                    if enum_val.value == category_name:
                        category_enum = enum_val
                        break
                
                if category_enum:
                    categorized_achievements[category_name] = {
                        'display_name': CATEGORY_DISPLAY_NAMES[category_enum],
                        'icon': CATEGORY_ICONS[category_enum],
                        'achievements': []
                    }
                    
                    for achievement_def in achievements_list:
                        if achievement_def.id in user_achievements:
                            categorized_achievements[category_name]['achievements'].append(
                                user_achievements[achievement_def.id]
                            )
            
            # 計算統計數據
            total_achievements = len(ACHIEVEMENTS)
            completed_achievements = sum(1 for ach in user_achievements.values() if ach['completed'])
            completion_rate = (completed_achievements / total_achievements * 100) if total_achievements > 0 else 0
              # 獲取最近完成的成就（最近7天）
            recent_time = time.time() - (7 * 24 * 60 * 60)  # 7天前
            recent_achievements = sum(1 for ach in user_achievements.values() 
                                   if ach['completed'] and ach.get('completed_at', 0) > recent_time)
            
            return {
                'status': 'success',
                'achievements': user_achievements,
                'categories': categorized_achievements,
                'stats': {
                    'total': total_achievements,
                    'completed': completed_achievements,
                    'completion_rate': round(completion_rate, 1),
                    'recent': recent_achievements
                }
            }
            
        except Exception as e:
            print(f"獲取用戶成就失敗: {e}")
            return {
                'status': 'error',
                'message': f'獲取成就數據失敗: {str(e)}'
            }
    
    def check_and_update_achievement(self, user_id, achievement_id, progress_value=1):
        """檢查並更新成就進度
        
        Args:
            user_id (str): 用戶ID
            achievement_id (str): 成就ID
            progress_value (int): 進度值（默認增加1）
            
        Returns:
            dict: 更新結果
        """
        try:
            from app.models.achievement import get_achievement_by_id
            
            user_ref = self.firestore_db.collection('users').document(user_id)
            achievement_ref = user_ref.collection('user_achievements').document(achievement_id)
            achievement_doc = achievement_ref.get()
            
            if not achievement_doc.exists:
                # 如果成就不存在，初始化用戶成就
                self.initialize_user_achievements(user_id)
                achievement_doc = achievement_ref.get()
            
            achievement_data = achievement_doc.to_dict()
            achievement_def = get_achievement_by_id(achievement_id)
            
            if not achievement_def:
                return {'status': 'error', 'message': '成就定義不存在'}
            
            # 如果已經完成，不需要更新
            if achievement_data.get('completed', False):
                return {'status': 'already_completed'}
            
            # 更新進度
            current_progress = achievement_data.get('progress', 0)
            new_progress = current_progress + progress_value
            
            # 檢查是否完成
            target_value = achievement_def.target_value
            completed = new_progress >= target_value
            
            update_data = {
                'progress': min(new_progress, target_value),
                'completed': completed
            }
            
            if completed:
                update_data['completed_at'] = time.time()
            
            achievement_ref.update(update_data)
            
            result = {
                'status': 'success',
                'achievement_id': achievement_id,
                'progress': update_data['progress'],
                'target_value': target_value,
                'completed': completed,
                'achievement_name': achievement_def.name,
                'reward_points': achievement_def.reward_points if completed else 0
            }
            
            # 如果完成了成就，更新用戶總成就點數
            if completed:
                self._add_achievement_points(user_id, achievement_def.reward_points)
                result['message'] = f'恭喜！獲得成就「{achievement_def.name}」！'
            
            return result
            
        except Exception as e:
            print(f"更新成就進度失敗: {e}")
            return {
                'status': 'error',
                'message': f'更新成就失敗: {str(e)}'
            }
    
    def _add_achievement_points(self, user_id, points):
        """為用戶添加成就點數
        
        Args:
            user_id (str): 用戶ID
            points (int): 要添加的點數
        """
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                current_points = user_doc.to_dict().get('achievement_points', 0)
                user_ref.update({
                    'achievement_points': current_points + points
                })
            else:
                user_ref.update({                    'achievement_points': points
                })
                
        except Exception as e:
            print(f"添加成就點數失敗: {e}")
    
    def trigger_achievement_check(self, user_id, event_type, event_data=None):
        """觸發成就檢查
        
        Args:
            user_id (str): 用戶ID
            event_type (str): 事件類型
            event_data (dict): 事件數據
            
        Returns:
            list: 觸發的成就列表
        """
        try:
            from app.models.achievement import get_achievement_by_id
            triggered_achievements = []
            
            # 根據事件類型檢查相應的成就
            if event_type == 'creature_captured':
                # 檢查初次邂逅成就
                result = self.check_and_update_achievement(user_id, 'ACH-INIT-001')
                if result.get('status') == 'success' and result.get('completed'):
                    triggered_achievements.append(result)
                
                # 檢查精靈收集數量成就
                user_creatures_count = self._get_user_creatures_count(user_id)
                collection_achievements = ['ACH-COLL-001', 'ACH-COLL-002', 'ACH-COLL-003', 
                                         'ACH-COLL-004', 'ACH-COLL-005', 'ACH-COLL-006']
                
                for ach_id in collection_achievements:
                    achievement_def = get_achievement_by_id(ach_id)
                    if achievement_def and user_creatures_count >= achievement_def.target_value:
                        result = self.check_and_update_achievement(user_id, ach_id, achievement_def.target_value)
                        if result.get('status') == 'success' and result.get('completed'):
                            triggered_achievements.append(result)
                
                # 檢查屬性收集成就
                if event_data and 'element_type' in event_data:
                    element_type = event_data['element_type']
                    self._check_element_type_achievements(user_id, element_type, triggered_achievements)
            
            elif event_type == 'arena_battle':
                # 檢查競技場對戰成就
                result = self.check_and_update_achievement(user_id, 'ACH-ARENA-001')
                if result.get('status') == 'success' and result.get('completed'):
                    triggered_achievements.append(result)
                  # 檢查其他競技場成就
                arena_achievements = ['ACH-ARENA-002', 'ACH-ARENA-003', 'ACH-ARENA-004']
                for ach_id in arena_achievements:
                    result = self.check_and_update_achievement(user_id, ach_id)
                    if result.get('status') == 'success' and result.get('completed'):
                        triggered_achievements.append(result)
            
            elif event_type == 'arena_victory':
                # 檢查競技場勝利成就
                victory_achievements = ['ACH-VICTORY-001', 'ACH-VICTORY-002', 'ACH-VICTORY-003', 'ACH-VICTORY-004']
                for ach_id in victory_achievements:
                    result = self.check_and_update_achievement(user_id, ach_id)
                    if result.get('status') == 'success' and result.get('completed'):
                        triggered_achievements.append(result)            
            elif event_type == 'friend_added':
                # 檢查交友成就
                user_friends_count = self._get_user_friends_count(user_id)
                friend_achievements = ['ACH-FRIEND-001', 'ACH-FRIEND-002', 'ACH-FRIEND-003', 'ACH-FRIEND-004']
                
                for ach_id in friend_achievements:
                    achievement_def = get_achievement_by_id(ach_id)
                    if achievement_def and user_friends_count >= achievement_def.target_value:
                        result = self._check_and_complete_achievement(user_id, ach_id, user_friends_count)
                        if result.get('status') == 'success' and result.get('completed'):
                            triggered_achievements.append(result)
            elif event_type == 'gym_occupied':
                # 檢查道館佔領成就
                user_gyms_count = self._get_user_gyms_count(user_id)
                gym_achievements = ['ACH-GYM-001', 'ACH-GYM-002', 'ACH-GYM-003', 'ACH-GYM-004']
                
                for ach_id in gym_achievements:
                    achievement_def = get_achievement_by_id(ach_id)
                    if achievement_def and user_gyms_count >= achievement_def.target_value:
                        result = self.check_and_update_achievement(user_id, ach_id, achievement_def.target_value)
                        if result.get('status') == 'success' and result.get('completed'):
                            triggered_achievements.append(result)
            
            elif event_type == 'daily_login':
                # 檢查登入天數成就
                login_days = self._get_user_login_days(user_id)
                login_achievements = ['ACH-LOGIN-001', 'ACH-LOGIN-002', 'ACH-LOGIN-003', 'ACH-LOGIN-004', 'ACH-LOGIN-005']
                
                for ach_id in login_achievements:
                    achievement_def = get_achievement_by_id(ach_id)
                    if achievement_def and login_days >= achievement_def.target_value:
                        result = self.check_and_update_achievement(user_id, ach_id, achievement_def.target_value)
                        if result.get('status') == 'success' and result.get('completed'):
                            triggered_achievements.append(result)
            
            elif event_type == 'login_after_long_absence':
                # 檢查特殊成就：長時間未登入後回歸
                result = self.check_and_update_achievement(user_id, 'ACH-SPEC-001')
                if result.get('status') == 'success' and result.get('completed'):
                    triggered_achievements.append(result)
            
            return triggered_achievements
            
        except Exception as e:
            print(f"觸發成就檢查失敗: {e}")
            return []
    
    def _get_user_creatures_count(self, user_id):
        """獲取用戶精靈數量"""
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            creatures_ref = user_ref.collection('user_creatures')
            creatures = creatures_ref.get()
            return len(creatures)
        except Exception as e:
            print(f"獲取用戶精靈數量失敗: {e}")
            return 0
    
    def _check_element_type_achievements(self, user_id, element_type, triggered_achievements):
        """檢查屬性類型相關成就"""
        try:
            from app.models.achievement import get_achievement_by_id
            
            # 檢查單一屬性成就
            element_achievement_map = {
                'grass': 'ACH-TYPE-002',
                'water': 'ACH-TYPE-003', 
                'fire': 'ACH-TYPE-004',
                'light': 'ACH-TYPE-005',
                'dark': 'ACH-TYPE-006',
                'normal': 'ACH-TYPE-007'
            }
            
            if element_type in element_achievement_map:
                ach_id = element_achievement_map[element_type]
                # 檢查是否收集了該屬性的所有精靈
                if self._has_all_creatures_of_type(user_id, element_type):
                    result = self.check_and_update_achievement(user_id, ach_id, 1)
                    if result.get('status') == 'success' and result.get('completed'):
                        triggered_achievements.append(result)
            
            # 檢查全屬性成就
            all_types = ['fire', 'water', 'grass', 'light', 'dark', 'normal']
            if self._has_creatures_of_all_types(user_id, all_types):
                result = self.check_and_update_achievement(user_id, 'ACH-TYPE-001', len(all_types))
                if result.get('status') == 'success' and result.get('completed'):
                    triggered_achievements.append(result)
                    
        except Exception as e:
            print(f"檢查屬性成就失敗: {e}")
    
    def _has_all_creatures_of_type(self, user_id, element_type):
        """檢查是否擁有某屬性的所有精靈"""
        # 這裡需要根據實際的精靈數據結構來實現
        # 暫時返回False，實際實現時需要查詢所有該屬性的精靈種類
        return False
    
    def _has_creatures_of_all_types(self, user_id, element_types):
        """檢查是否擁有所有屬性的精靈"""
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            creatures_ref = user_ref.collection('user_creatures')
            creatures = creatures_ref.get()
            
            # 統計用戶擁有的精靈屬性
            user_element_types = set()
            for creature_doc in creatures:
                creature_data = creature_doc.to_dict()
                element_type = creature_data.get('element_type')
                if element_type:
                    user_element_types.add(element_type)
            
            # 檢查是否包含所有要求的屬性
            return all(element_type in user_element_types for element_type in element_types)
            
        except Exception as e:
            print(f"檢查全屬性精靈失敗: {e}")
            return False
    
    def _get_user_login_days(self, user_id):
        """獲取用戶登入天數"""
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return user_data.get('login_days', 0)
            
            return 0
            
        except Exception as e:
            print(f"獲取用戶登入天數失敗: {e}")
            return 0
    
    def update_user_login_stats(self, user_id):
        """更新用戶登入統計"""
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            current_time = time.time()
            today = int(current_time // (24 * 60 * 60))  # 以天為單位的時間戳
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                last_login_day = user_data.get('last_login_day', 0)
                login_days = user_data.get('login_days', 0)
                last_active = user_data.get('last_active', 0)
                
                # 檢查是否為新的一天登入
                if last_login_day != today:
                    login_days += 1
                    user_ref.update({
                        'last_login_day': today,
                        'login_days': login_days,
                        'last_active': current_time
                    })
                    
                    # 檢查是否為長時間未登入後回歸
                    days_since_last_login = (current_time - last_active) / (24 * 60 * 60)
                    if days_since_last_login >= 14:
                        # 觸發特殊成就檢查
                        self.trigger_achievement_check(user_id, 'login_after_long_absence')
                    
                    # 觸發登入成就檢查
                    self.trigger_achievement_check(user_id, 'daily_login')
                else:
                    # 同一天內的登入，只更新最後活動時間
                    user_ref.update({
                        'last_active': current_time
                    })
            else:
                # 首次登入
                user_ref.update({
                    'last_login_day': today,
                    'login_days': 1,
                    'last_active': current_time
                })
                
        except Exception as e:
            print(f"更新用戶登入統計失敗: {e}")
    
    def _get_user_gyms_count(self, user_id):
        """獲取用戶佔領的道館數量
        
        Args:
            user_id (str): 用戶ID
            
        Returns:
            int: 道館數量
        """
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_arenas = user_ref.collection('user_arenas').where('status', '==', 'occupied').get()
            return len(user_arenas)
        except Exception as e:
            print(f"獲取用戶道館數量失敗: {e}")
            return 0
    
    def _get_user_friends_count(self, user_id):
        """獲取用戶好友數量
        
        Args:
            user_id (str): 用戶ID
            
        Returns:
            int: 好友數量
        """
        try:
            user_ref = self.firestore_db.collection('users').document(user_id)
            friends = user_ref.collection('friends').where('status', '==', 'active').get()
            return len(friends)
        except Exception as e:
            print(f"獲取用戶好友數量失敗: {e}")
            return 0

    def _check_and_complete_achievement(self, user_id, achievement_id, current_count):
        """檢查並完成成就（用於絕對值檢查）
        
        Args:
            user_id (str): 用戶ID
            achievement_id (str): 成就ID
            current_count (int): 當前數量
            
        Returns:
            dict: 更新結果
        """
        try:
            from app.models.achievement import get_achievement_by_id
            
            user_ref = self.firestore_db.collection('users').document(user_id)
            achievement_ref = user_ref.collection('user_achievements').document(achievement_id)
            achievement_doc = achievement_ref.get()
            
            if not achievement_doc.exists:
                # 如果成就不存在，初始化用戶成就
                self.initialize_user_achievements(user_id)
                achievement_doc = achievement_ref.get()
            
            achievement_data = achievement_doc.to_dict()
            achievement_def = get_achievement_by_id(achievement_id)
            
            if not achievement_def:
                return {'status': 'error', 'message': '成就定義不存在'}
            
            # 如果已經完成，不需要更新
            if achievement_data.get('completed', False):
                return {'status': 'already_completed'}
            
            # 檢查是否達到目標
            target_value = achievement_def.target_value
            completed = current_count >= target_value
            
            if completed:
                update_data = {
                    'progress': target_value,
                    'completed': True,
                    'completed_at': time.time()
                }
                
                achievement_ref.update(update_data)
                
                # 更新用戶總成就點數
                self._add_achievement_points(user_id, achievement_def.reward_points)
                
                return {
                    'status': 'success',
                    'achievement_id': achievement_id,
                    'progress': target_value,
                    'target_value': target_value,
                    'completed': True,
                    'achievement_name': achievement_def.name,
                    'reward_points': achievement_def.reward_points,
                    'message': f'恭喜！獲得成就「{achievement_def.name}」！'
                }
            else:
                # 更新進度但未完成
                update_data = {
                    'progress': current_count
                }
                achievement_ref.update(update_data)
                
                return {
                    'status': 'progress_updated',
                    'achievement_id': achievement_id,
                    'progress': current_count,
                    'target_value': target_value,
                    'completed': False
                }
                
        except Exception as e:
            print(f"檢查成就完成狀態失敗: {e}")
            return {
                'status': 'error',
                'message': f'檢查成就失敗: {str(e)}'
            }