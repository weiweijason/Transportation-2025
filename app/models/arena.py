import time
from app.services.firebase_service import FirebaseService
from app.services.tdx_service import TdxService
from datetime import datetime
import uuid
from app import db as app_db
import json
import os
import threading
import logging
import pandas as pd

# 設置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 緩存檔案路徑
ARENA_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'arenas')
ARENA_CACHE_FILE = os.path.join(ARENA_CACHE_DIR, 'arena_levels.json')

# 全局道館等級緩存
arena_levels_cache = {}
cache_lock = threading.Lock()

# 特殊處理的道館站點映射 - 解決命名不一致問題
SPECIAL_STOP_MAPPING = {
    # 取消特殊處理的道館站點映射功能
    # 原有映射已被移除
}

# 手動設定為三級道館的站點
FORCE_LEVEL_THREE_STOPS = [
    # 取消手動設定的三級道館站點
    # 原有設定已被移除
]

# 緩存相關函數
def load_arena_cache():
    """從緩存檔案載入道館等級資料"""
    global arena_levels_cache
    
    try:
        if os.path.exists(ARENA_CACHE_FILE):
            with open(ARENA_CACHE_FILE, 'r', encoding='utf-8') as f:
                with cache_lock:
                    arena_levels_cache = json.load(f)
                logger.info(f"已從緩存檔案載入 {len(arena_levels_cache)} 個道館等級資料")
                print(f"[道館緩存] 已從緩存檔案載入 {len(arena_levels_cache)} 個道館等級資料")
        else:
            logger.info("緩存檔案不存在，將創建新緩存")
            print("[道館緩存] 緩存檔案不存在，將創建新緩存")
            update_arena_cache()
    except Exception as e:
        logger.error(f"載入道館等級緩存時發生錯誤: {e}")
        print(f"[道館緩存錯誤] 載入道館等級緩存時發生錯誤: {e}")
        arena_levels_cache = {}

def update_arena_cache_from_tdx():
    """從TDX獲取站點資料並更新道館等級緩存，使用pandas進行數據處理"""
    global arena_levels_cache
    
    try:
        # 確保緩存目錄存在
        os.makedirs(ARENA_CACHE_DIR, exist_ok=True)
        
        # 獲取TDX服務實例
        tdx_service = TdxService()
        
        # 獲取各路線站點資料
        routes_info = [
            {'key': 'cat-right', 'name': '貓空右線'},
            {'key': 'cat-left', 'name': '貓空左線(動物園)'},
            {'key': 'cat-left-zhinan', 'name': '貓空左線(指南宮)'}
        ]
        
        print(f"[道館數據處理] 開始從TDX獲取{len(routes_info)}條路線的站點資料")
        
        # 創建pandas DataFrame來存儲和處理站點數據
        all_stops_df = pd.DataFrame(columns=['StopID', 'StopName', 'Route', 'PositionLat', 'PositionLon'])
        
        # 處理每條路線的站點
        for route_info in routes_info:
            route_key = route_info['key']
            route_name = route_info['name']
            
            print(f"[道館數據處理] 正在處理路線: {route_name}")
            
            # 從TDX獲取站點資料
            stops_data = tdx_service.get_route_stops(route_key)
            
            if not stops_data:
                logger.warning(f"無法從TDX獲取路線 {route_name} 的站點資料")
                print(f"[道館數據處理] 警告: 無法從TDX獲取路線 {route_name} 的站點資料")
                continue
                
            logger.info(f"從TDX獲取了 {route_name} 的 {len(stops_data)} 個站點資料")
            print(f"[道館數據處理] 從TDX獲取了 {route_name} 的 {len(stops_data)} 個站點資料")
            
            # 處理每個站點，添加到DataFrame
            for stop in stops_data:
                stop_id = stop.get('StopID')
                stop_name = stop.get('StopName', {}).get('Zh_tw', '未知站點')
                
                # 特殊站點處理 - 修正名稱不一致問題
                if stop_name in SPECIAL_STOP_MAPPING:
                    print(f"[道館數據處理] 特殊站點映射: {stop_name} -> {SPECIAL_STOP_MAPPING[stop_name]}")
                    stop_name = SPECIAL_STOP_MAPPING[stop_name]
                
                # 取得站點坐標
                position_lat = None
                position_lon = None
                if 'StopPosition' in stop:
                    position_lat = stop['StopPosition'].get('PositionLat')
                    position_lon = stop['StopPosition'].get('PositionLon')
                
                if not stop_id or not position_lat or not position_lon:
                    continue
                
                # 添加到DataFrame
                new_row = {
                    'StopID': stop_id,
                    'StopName': stop_name,
                    'Route': route_name,
                    'PositionLat': position_lat,
                    'PositionLon': position_lon
                }
                all_stops_df = pd.concat([all_stops_df, pd.DataFrame([new_row])], ignore_index=True)
        
        # 計算每個站點經過的路線數量
        print(f"[道館數據處理] 開始分析站點和路線關係")
        stops_routes_count = all_stops_df.groupby(['StopName']).agg({
            'StopID': 'first',  # 取第一個站點ID
            'Route': lambda x: list(set(x)),  # 去重後的路線列表
            'PositionLat': 'first',  # 取第一個座標值
            'PositionLon': 'first'   # 取第一個座標值
        }).reset_index()
        
        # 添加路線數量和道館等級
        stops_routes_count['RoutesCount'] = stops_routes_count['Route'].apply(len)
        stops_routes_count['Level'] = stops_routes_count['RoutesCount']
        
        # 手動處理特殊站點的等級
        for i, row in stops_routes_count.iterrows():
            stop_name = row['StopName']
            # 特定站點強制設置為三級道館
            if stop_name in FORCE_LEVEL_THREE_STOPS:
                print(f"[道館數據處理] 手動設置 {stop_name} 為三級道館")
                # 確保包含所有三條路線
                all_routes = ['貓空右線', '貓空左線(動物園)', '貓空左線(指南宮)']
                # 更新Level和Routes
                stops_routes_count.at[i, 'Level'] = 3
                stops_routes_count.at[i, 'Route'] = all_routes
                stops_routes_count.at[i, 'RoutesCount'] = 3
        
        # 創建道館數據
        arenas_data = {}
        
        print(f"[道館數據處理] 開始創建道館數據，共有{len(stops_routes_count)}個站點")
        
        # 檢查是否有現有數據
        existing_data = {}
        if os.path.exists(ARENA_CACHE_FILE):
            try:
                with open(ARENA_CACHE_FILE, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"[道館數據處理] 載入了{len(existing_data)}個現有道館數據")
            except Exception as e:
                logger.error(f"讀取現有道館數據時出錯: {e}")
                print(f"[道館數據處理] 警告: 讀取現有道館數據時出錯: {e}")
        
        # 統計
        new_arenas_count = 0
        updated_arenas_count = 0
        unchanged_arenas_count = 0
        
        # 根據分析結果創建道館數據
        for _, row in stops_routes_count.iterrows():
            stop_id = row['StopID']
            stop_name = row['StopName']
            routes = row['Route']
            position = [row['PositionLat'], row['PositionLon']]
            level = row['Level']
            
            # 創建道館ID和名稱
            arena_id = f"arena-{stop_id}"
            arena_name = f"{stop_name}道館"
            
            # 檢查是否已存在此道館 (按名稱查找)
            existing_arena = None
            existing_arena_id = None
            
            # 首先尋找完全相同名稱的道館
            for ex_id, ex_arena in existing_data.items():
                if ex_arena.get('name') == arena_name:
                    existing_arena = ex_arena
                    existing_arena_id = ex_id
                    break
            
            if existing_arena:
                # 道館已存在，更新路線和等級
                existing_routes = set(existing_arena.get('routes', []))
                new_routes = set(routes)
                combined_routes = list(existing_routes.union(new_routes))
                
                # 計算新等級 - 根據經過的路線數量
                new_level = len(combined_routes) if combined_routes else 1
                
                # 特殊站點強制設定等級
                if stop_name in FORCE_LEVEL_THREE_STOPS:
                    new_level = 3
                    combined_routes = ['貓空右線', '貓空左線(動物園)', '貓空左線(指南宮)']
                
                # 檢查是否需要更新
                if new_level != existing_arena.get('level', 1) or set(combined_routes) != existing_routes:
                    # 創建更新後的道館資料，保留現有的戰鬥相關數據
                    arena_data = {
                        'id': existing_arena_id,
                        'name': arena_name,
                        'position': position,
                        'stopIds': [stop_id] + existing_arena.get('stopIds', [])[1:] if existing_arena.get('stopIds') else [stop_id],
                        'stopName': stop_name,
                        'routes': combined_routes,
                        'level': new_level,
                        'owner': existing_arena.get('owner'),
                        'ownerPlayerId': existing_arena.get('ownerPlayerId'),
                        'ownerCreature': existing_arena.get('ownerCreature'),
                        'challengers': existing_arena.get('challengers', []),
                        'updatedAt': int(time.time() * 1000)
                    }
                    arenas_data[existing_arena_id] = arena_data
                    updated_arenas_count += 1
                    print(f"[道館數據處理] 更新道館: {arena_name} (ID: {existing_arena_id}), 路線數: {new_level}, 路線: {combined_routes}")
                else:
                    # 無需更新，保留原有數據
                    arenas_data[existing_arena_id] = existing_arena
                    unchanged_arenas_count += 1
            else:
                # 創建新道館資料
                arena_data = {
                    'id': arena_id,
                    'name': arena_name,
                    'position': position,
                    'stopIds': [stop_id],
                    'stopName': stop_name,
                    'routes': routes,
                    'level': level,
                    'owner': None,
                    'ownerPlayerId': None,
                    'ownerCreature': None,
                    'challengers': [],
                    'updatedAt': int(time.time() * 1000)
                }
                arenas_data[arena_id] = arena_data
                new_arenas_count += 1
                print(f"[道館數據處理] 新建道館: {arena_name} (ID: {arena_id}), 路線數: {level}, 路線: {routes}")
        
        # 報告處理結果
        print(f"[道館數據處理] 處理完成: 新增{new_arenas_count}個道館, 更新{updated_arenas_count}個道館, 保留{unchanged_arenas_count}個道館")
        logger.info(f"從TDX共處理了 {len(arenas_data)} 個道館資料")
        print(f"[道館數據處理] 從TDX共處理了 {len(arenas_data)} 個道館資料")
        
        # 更新緩存
        with cache_lock:
            arena_levels_cache = arenas_data
        
        # 保存到緩存檔案
        with open(ARENA_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(arenas_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"成功更新道館等級緩存，共 {len(arenas_data)} 筆資料")
        print(f"[道館數據處理] 成功更新道館等級緩存，共 {len(arenas_data)} 筆資料")
        return True
    except Exception as e:
        logger.error(f"從TDX更新道館等級緩存時發生錯誤: {e}")
        print(f"[道館數據處理錯誤] 從TDX更新道館等級緩存時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_arena_cache():
    """更新道館等級緩存檔案"""
    # 優先使用 TDX 作為資料來源
    success = update_arena_cache_from_tdx()
    
    # 如果從 TDX 更新失敗且 Firebase 可用，則嘗試從 Firebase 更新
    if not success:
        try:
            # 確保緩存目錄存在
            os.makedirs(ARENA_CACHE_DIR, exist_ok=True)
            
            # 獲取所有道館資料
            firebase_service = FirebaseService()
            arenas_data = {}
            
            # 從 Firestore 獲取
            arenas_ref = firebase_service.firestore_db.collection('arenas').get()
            if arenas_ref:
                for arena_doc in arenas_ref:
                    arena_data = arena_doc.to_dict()
                    arena_id = arena_doc.id
                    # 確保 ID 被包含
                    arena_data['id'] = arena_id
                    # 計算等級
                    if 'routes' in arena_data:
                        arena_data['level'] = len(arena_data['routes']) if arena_data['routes'] else 1
                    else:
                        arena_data['level'] = 1
                    arenas_data[arena_id] = arena_data
            
            logger.info(f"從 Firebase 獲取了 {len(arenas_data)} 個道館資料（作為備用）")
            
            # 檢查本地緩存中是否有已經在 Firebase 中不存在的道館
            with cache_lock:
                # 獲取當前緩存道館IDs
                current_cache_ids = set(arena_levels_cache.keys())
                # 獲取Firebase道館IDs
                firebase_ids = set(arenas_data.keys())
                # 計算在本地緩存但不在Firebase中的道館IDs
                deleted_ids = current_cache_ids - firebase_ids
                
                if deleted_ids:
                    logger.info(f"發現 {len(deleted_ids)} 個在Firebase中已刪除的道館，將從緩存中移除: {deleted_ids}")
                    print(f"[道館數據處理] 發現 {len(deleted_ids)} 個在Firebase中已刪除的道館，將從緩存中移除")
                    # 從緩存中移除已刪除的道館
                    for arena_id in deleted_ids:
                        if arena_id in arena_levels_cache:
                            deleted_name = arena_levels_cache[arena_id].get('name', 'unknown')
                            logger.info(f"從緩存中移除已刪除的道館: {deleted_name} (ID: {arena_id})")
                            print(f"[道館數據處理] 從緩存中移除已刪除的道館: {deleted_name} (ID: {arena_id})")
                            del arena_levels_cache[arena_id]
            
            # 更新緩存
            with cache_lock:
                arena_levels_cache = arenas_data
                
            # 保存到緩存檔案
            with open(ARENA_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(arenas_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"成功從Firebase更新道館等級緩存，共 {len(arenas_data)} 筆資料")
            return True
        except Exception as e:
            logger.error(f"更新道館等級緩存時發生錯誤: {e}")
            return False
    
    return success

def get_arena_level_from_cache(arena_id):
    """從緩存中獲取道館等級"""
    with cache_lock:
        if arena_id in arena_levels_cache:
            return arena_levels_cache[arena_id].get('level', 1)
    return 1  # 默認等級

def get_arena_from_cache(arena_id=None, arena_name=None):
    """從緩存中獲取道館資料，可以通過ID或名稱獲取"""
    with cache_lock:
        # 使用ID搜尋
        if arena_id and arena_id in arena_levels_cache:
            return arena_levels_cache[arena_id]
        
        # 使用名稱搜尋
        if arena_name:
            for arena_id, arena_data in arena_levels_cache.items():
                if arena_data.get('name') == arena_name:
                    return arena_data
    
    return None

def get_all_arenas_from_cache():
    """從緩存中獲取所有道館資料"""
    with cache_lock:
        return list(arena_levels_cache.values())

# 在模組載入時初始化緩存
load_arena_cache()

# 定期更新緩存的後台任務
def start_cache_update_scheduler():
    """啟動緩存定期更新的排程器"""
    import threading
    import time
    
    def update_cache_periodically():
        while True:
            try:
                logger.info("開始定期更新道館等級緩存...")
                update_arena_cache()
                # 每小時更新一次
                time.sleep(3600)
            except Exception as e:
                logger.error(f"定期更新道館緩存時發生錯誤: {e}")
                # 發生錯誤時，等待10分鐘後重試
                time.sleep(600)
    
    # 創建後台執行緒
    update_thread = threading.Thread(
        target=update_cache_periodically, 
        daemon=True,
        name="ArenaLevelCacheUpdater"
    )
    update_thread.start()
    logger.info("道館等級緩存自動更新排程器已啟動")

# 啟動緩存更新排程器
start_cache_update_scheduler()

def sync_arena_cache_to_firebase():
    """
    系統啟動時，將本地 JSON 道館數據同步到 Firebase
    優先保存：如果本地緩存中有道館但 Firebase 中沒有，則將其添加到 Firebase
    """
    try:
        logger.info("開始將本地道館數據同步到 Firebase...")
        print("[道館數據同步] 開始將本地道館數據同步到 Firebase...")
        
        # 檢查緩存文件是否存在
        if not os.path.exists(ARENA_CACHE_FILE):
            logger.warning("本地道館緩存文件不存在，無法同步到 Firebase")
            print("[道館數據同步] 本地道館緩存文件不存在，無法同步到 Firebase")
            return False
        
        # 讀取本地道館緩存
        local_arenas = {}
        try:
            with open(ARENA_CACHE_FILE, 'r', encoding='utf-8') as f:
                local_arenas = json.load(f)
            logger.info(f"成功從本地緩存讀取 {len(local_arenas)} 個道館數據")
            print(f"[道館數據同步] 成功從本地緩存讀取 {len(local_arenas)} 個道館數據")
        except Exception as e:
            logger.error(f"讀取本地道館緩存文件時出錯: {e}")
            print(f"[道館數據同步] 讀取本地道館緩存文件時出錯: {e}")
            return False
        
        # 獲取 Firebase 服務實例
        firebase_service = FirebaseService()
        
        # 從 Firebase 獲取現有道館 ID
        firebase_arena_ids = set()
        try:
            arenas_ref = firebase_service.firestore_db.collection('arenas').get()
            for arena_doc in arenas_ref:
                firebase_arena_ids.add(arena_doc.id)
            logger.info(f"從 Firebase 獲取了 {len(firebase_arena_ids)} 個道館 ID")
            print(f"[道館數據同步] 從 Firebase 獲取了 {len(firebase_arena_ids)} 個道館 ID")
        except Exception as e:
            logger.error(f"從 Firebase 獲取道館數據時出錯: {e}")
            print(f"[道館數據同步] 從 Firebase 獲取道館數據時出錯: {e}")
            return False
        
        # 找出需要添加到 Firebase 的道館（本地有但 Firebase 沒有的）
        arenas_to_add = []
        for arena_id, arena_data in local_arenas.items():
            if arena_id not in firebase_arena_ids:
                arenas_to_add.append((arena_id, arena_data))
        
        logger.info(f"發現 {len(arenas_to_add)} 個需要添加到 Firebase 的道館")
        print(f"[道館數據同步] 發現 {len(arenas_to_add)} 個需要添加到 Firebase 的道館")
        
        # 批量添加道館到 Firebase
        added_count = 0
        for arena_id, arena_data in arenas_to_add:
            try:
                # 確保數據格式正確
                if 'id' not in arena_data:
                    arena_data['id'] = arena_id
                
                # 添加到 Firestore
                firebase_service.firestore_db.collection('arenas').document(arena_id).set(arena_data)
                added_count += 1
                logger.info(f"成功將道館 {arena_data.get('name', arena_id)} 添加到 Firebase")
                print(f"[道館數據同步] 成功將道館 {arena_data.get('name', arena_id)} 添加到 Firebase")
            except Exception as e:
                logger.error(f"將道館 {arena_id} 添加到 Firebase 時出錯: {e}")
                print(f"[道館數據同步] 將道館 {arena_id} 添加到 Firebase 時出錯: {e}")
        
        logger.info(f"完成道館數據同步，成功添加 {added_count}/{len(arenas_to_add)} 個道館到 Firebase")
        print(f"[道館數據同步] 完成道館數據同步，成功添加 {added_count}/{len(arenas_to_add)} 個道館到 Firebase")
        return True
    except Exception as e:
        logger.error(f"同步道館數據到 Firebase 時發生未預期的錯誤: {e}")
        print(f"[道館數據同步] 同步道館數據到 Firebase 時發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

class FirebaseArena:
    """
    擂台(道館)模型 - Firebase 版本
    擂台為公車站牌，同名站牌視為同一個擂台，即使位置不同
    """
    def __init__(self, id=None, name=None, position=None, stop_ids=None, routes=None, 
                 owner=None, owner_creature=None, challengers=None, owner_player_id=None):
        # 如果沒有提供ID，生成一個唯一ID
        self.id = id or str(uuid.uuid4())
        self.name = name  # 站牌名稱，作為唯一識別符
        self.position = position  # [lat, lng] 格式
        self.stop_ids = stop_ids or []  # 站牌ID列表
        self.routes = routes or []  # 經過路線列表
        self.owner = owner  # 控制者 (用戶名稱)
        self.owner_player_id = owner_player_id  # 控制者玩家ID
        self.owner_creature = owner_creature  # 控制者精靈 (包含id, name, power)
        self.challengers = challengers or []  # 挑戰紀錄
        self.updated_at = int(time.time() * 1000)  # 更新時間 (毫秒時間戳)
        # 獲取 Firebase 服務實例
        self.firebase_service = FirebaseService()
        self.db = self.firebase_service.db
        self.firestore_db = self.firebase_service.firestore_db

    @staticmethod
    def create_from_dict(arena_dict):
        """從字典創建擂台對象"""
        if not arena_dict:
            return None
            
        return FirebaseArena(
            id=arena_dict.get('id'),
            name=arena_dict.get('name'),
            position=arena_dict.get('position'),
            stop_ids=arena_dict.get('stopIds') or arena_dict.get('stop_ids', []),
            routes=arena_dict.get('routes', []),
            owner=arena_dict.get('owner'),
            owner_creature=arena_dict.get('ownerCreature') or arena_dict.get('owner_creature'),
            challengers=arena_dict.get('challengers', []),
            owner_player_id=arena_dict.get('ownerPlayerId')
        )

    def to_dict(self):
        """將擂台轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'stopIds': self.stop_ids,
            'routes': self.routes,
            'level': self.calculate_level(),  # 確保在每次轉換為字典時計算正確的等級
            'owner': self.owner,
            'ownerPlayerId': self.owner_player_id,
            'ownerCreature': self.owner_creature,
            'challengers': self.challengers,
            'updatedAt': self.updated_at
        }

    @staticmethod
    def get_all():
        """獲取所有擂台"""
        firebase_service = FirebaseService()
        arenas_ref = firebase_service.db.child('arenas').get()
        if not arenas_ref.val():
            return []
        return [FirebaseArena.create_from_dict(arena.val()) for arena in arenas_ref.each()]
    
    @staticmethod
    def get_by_id(arena_id):
        """根據ID獲取擂台"""
        firebase_service = FirebaseService()
        arena_ref = firebase_service.db.child('arenas').child(arena_id).get()
        if not arena_ref.val():
            return None
        return FirebaseArena.create_from_dict(arena_ref.val())
    
    @staticmethod
    def get_by_name(name):
        """根據名稱獲取擂台"""
        firebase_service = FirebaseService()
        # Firebase Realtime Database 沒有直接的 where 查詢，需要獲取所有記錄並過濾
        arenas_ref = firebase_service.db.child('arenas').get()
        if not arenas_ref.val():
            return None
            
        for arena in arenas_ref.each():
            arena_data = arena.val()
            if arena_data.get('name') == name:
                return FirebaseArena.create_from_dict(arena_data)
        return None
    
    @staticmethod
    def get_by_name_firestore(name):
        """根據名稱從Firestore獲取擂台"""
        firebase_service = FirebaseService()
        
        # 使用Firestore的where查詢功能
        arenas_ref = firebase_service.firestore_db.collection('arenas').where('name', '==', name).limit(1).get()
          # 檢查是否有結果
        if not arenas_ref or len(arenas_ref) == 0:
            return None
            
        # 返回第一個匹配的道館
        arena_dict = arenas_ref[0].to_dict()
        arena_dict['id'] = arenas_ref[0].id  # 確保ID也被添加到字典中
        return FirebaseArena.create_from_dict(arena_dict)
    
    def save(self):
        """保存擂台"""
        self.updated_at = int(time.time() * 1000)
        self.db.child('arenas').child(self.id).set(self.to_dict())
        return self
    
    def save_to_firestore(self):
        """將擂台保存到Firestore"""
        try:
            self.updated_at = int(time.time() * 1000)
            arena_dict = self.to_dict()
            
            # 使用文檔ID保存到Firestore
            self.firestore_db.collection('arenas').document(self.id).set(arena_dict)
            
            # 同時更新Realtime Database（保持兼容性）
            self.save()
            
            return True
        except Exception as e:
            print(f"保存擂台到Firestore失敗: {e}")
            return False
    
    @staticmethod
    def create_arena_if_not_exists(name, position, stop_ids=None, routes=None):
        """創建擂台如果不存在，否則返回現有擂台，並根據路線更新道館等級"""
        # 首先嘗試從Firestore獲取
        arena = FirebaseArena.get_by_name_firestore(name)

        # 如果Firestore中不存在，嘗試從Realtime Database獲取
        if arena is None:
            arena = FirebaseArena.get_by_name(name)

        # 如果仍然不存在，創建新的擂台
        if arena is None:
            arena = FirebaseArena(
                name=name,
                position=position,
                stop_ids=stop_ids or [],
                routes=routes or []
            )
            # 保存到兩個數據庫
            arena.save_to_firestore()
        else:
            # 如果擂台已存在，檢查路線是否為新路線
            existing_routes = set(arena.routes) if arena.routes else set()
            new_routes = set(routes) if routes else set()
            
            # 如果有新路線，添加新路線
            if not new_routes.issubset(existing_routes) and new_routes:
                arena.routes = list(existing_routes.union(new_routes))
                # 保存到數據庫
                arena.save_to_firestore()

        return arena

    def challenge(self, challenger_id, challenger_name, challenger_power, challenger_username):
        """
        挑戰擂台
        :param challenger_id: 挑戰者精靈ID
        :param challenger_name: 挑戰者精靈名稱
        :param challenger_power: 挑戰者精靈力量
        :param challenger_username: 挑戰者用戶名稱
        :return: (是否獲勝, 挑戰信息)
        """
        # 記錄挑戰
        challenge_record = {
            'timestamp': int(time.time() * 1000),
            'challengerId': challenger_id,
            'challengerName': challenger_name,
            'challengerPower': challenger_power,
            'challengerUsername': challenger_username,
            'result': False
        }
          # 如果擂台無人控制，直接獲勝
        if not self.owner:
            self.owner = challenger_username
            self.owner_creature = {
                'id': challenger_id,
                'name': challenger_name,
                'power': challenger_power
            }
            challenge_record['result'] = True
            self.challengers.append(challenge_record)
            self.save()
            return True, "成功佔領無人擂台"
            
        # 計算勝率 - 挑戰者攻擊力 / (挑戰者攻擊力 + 防守者攻擊力)
        win_chance = challenger_power / (challenger_power + self.owner_creature.get('attack', self.owner_creature.get('power', 0)))
        
        # 決定勝負
        import random
        is_win = random.random() < win_chance
        
        if is_win:
            # 更新擂台控制者
            self.owner = challenger_username
            self.owner_creature = {
                'id': challenger_id,
                'name': challenger_name,
                'power': challenger_power
            }
            challenge_record['result'] = True
            
        # 記錄挑戰結果
        self.challengers.append(challenge_record)
        
        # 限制挑戰記錄數量
        if len(self.challengers) > 20:
            self.challengers = self.challengers[-20:]
            
        # 保存更新
        self.save()
        
        return is_win, "挑戰成功" if is_win else "挑戰失敗"
    
    def challenge_with_player_id(self, challenger_id, challenger_name, challenger_power, challenger_username, challenger_player_id):
        """
        帶有玩家ID的擂台挑戰
        :param challenger_id: 挑戰者精靈ID
        :param challenger_name: 挑戰者精靈名稱
        :param challenger_power: 挑戰者精靈力量
        :param challenger_username: 挑戰者用戶名稱
        :param challenger_player_id: 挑戰者玩家ID
        :return: (是否獲勝, 挑戰信息)
        """
        # 記錄挑戰
        challenge_record = {
            'timestamp': int(time.time() * 1000),
            'challengerId': challenger_id,
            'challengerName': challenger_name,
            'challengerPower': challenger_power,
            'challengerUsername': challenger_username,        'challengerPlayerId': challenger_player_id,
            'result': False
        }
        
        # 如果擂台無人控制，直接獲勝
        if not self.owner:
            self.owner = challenger_username
            self.owner_player_id = challenger_player_id
            self.owner_creature = {
                'id': challenger_id,
                'name': challenger_name,
                'power': challenger_power
            }
            challenge_record['result'] = True
            self.challengers.append(challenge_record)
            self.save_to_firestore()
            return True, "成功佔領無人擂台"
            
        # 計算勝率 - 挑戰者攻擊力 / (挑戰者攻擊力 + 防守者攻擊力)
        win_chance = challenger_power / (challenger_power + self.owner_creature.get('attack', self.owner_creature.get('power', 0)))
        
        # 決定勝負
        import random
        is_win = random.random() < win_chance
        
        if is_win:
            # 更新擂台控制者
            self.owner = challenger_username
            self.owner_player_id = challenger_player_id
            self.owner_creature = {
                'id': challenger_id,
                'name': challenger_name,
                'power': challenger_power
            }
            challenge_record['result'] = True
            
        # 記錄挑戰結果
        self.challengers.append(challenge_record)
        
        # 限制挑戰記錄數量
        if len(self.challengers) > 20:
            self.challengers = self.challengers[-20:]
            
        # 保存更新到兩個數據庫
        self.save_to_firestore()
        
        return is_win, "挑戰成功" if is_win else "挑戰失敗"

    def calculate_level(self):
        """根據經過的路線數量計算道館等級"""
        if not self.routes:
            return 1  # 如果沒有路線，默認為等級1
        return len(self.routes)  # 道館等級為路線數量

    def update_level(self):
        """更新道館等級"""
        self.level = self.calculate_level()
        self.save_to_firestore()


class Arena(app_db.Model):
    """擂台模型（每個公車站點可以有一個擂台）"""
    __tablename__ = 'arenas'
    
    id = app_db.Column(app_db.Integer, primary_key=True)
    name = app_db.Column(app_db.String(64), nullable=False)
    prestige = app_db.Column(app_db.Integer, default=0)  # 擂台聲望值，越高越難挑戰
    last_battle = app_db.Column(app_db.DateTime, nullable=True)  # 上次對戰時間
    created_at = app_db.Column(app_db.DateTime, default=datetime.utcnow)
    
    # 關聯
    bus_stop_id = app_db.Column(app_db.Integer, app_db.ForeignKey('bus_stops.id'), unique=True)
    master_id = app_db.Column(app_db.Integer, app_db.ForeignKey('users.id'))  # 擂台主人
    guardian_id = app_db.Column(app_db.Integer, app_db.ForeignKey('creatures.id'), nullable=True)  # 守護精靈
    
    # 反向關聯
    bus_stop = app_db.relationship('BusStop', foreign_keys=[bus_stop_id], backref=app_db.backref('arena', uselist=False))
    guardian = app_db.relationship('Creature', foreign_keys=[guardian_id])
    battles = app_db.relationship('Battle', backref='arena', lazy='dynamic')
    
    def assign_guardian(self, creature):
        """設置守護精靈"""
        if self.guardian_id == creature.id:
            return False  # 已經是守護精靈
            
        if creature.user_id != self.master_id:
            return False  # 精靈不屬於擂台主人
            
        # 移除精靈之前的擂台關聯（如果有）
        if creature.arena_id:
            old_arena = Arena.query.get(creature.arena_id)
            if old_arena:
                old_arena.guardian_id = None
                app_db.session.add(old_arena)
                
        self.guardian_id = creature.id
        creature.arena_id = self.id
        app_db.session.add(creature)
        app_db.session.add(self)
        return True
    
    def change_master(self, new_master_id, new_guardian_id=None):
        """變更擂台主人"""
        old_master_id = self.master_id
        self.master_id = new_master_id
        
        # 移除原守護精靈的擂台關聯
        if self.guardian_id:
            old_guardian = Creature.query.get(self.guardian_id)
            if old_guardian:
                old_guardian.arena_id = None
                app_db.session.add(old_guardian)
        
        # 設置新守護精靈
        if new_guardian_id:
            new_guardian = Creature.query.get(new_guardian_id)
            if new_guardian and new_guardian.user_id == new_master_id:
                self.guardian_id = new_guardian_id
                new_guardian.arena_id = self.id
                app_db.session.add(new_guardian)
        else:
            self.guardian_id = None
            
        self.last_battle = datetime.utcnow()
        app_db.session.add(self)
        return old_master_id
    
    def increase_prestige(self, amount=1):
        """增加擂台聲望值"""
        self.prestige += amount
        app_db.session.add(self)
        return self.prestige
    
    def can_challenge(self, user_id):
        """檢查用戶是否可以挑戰此擂台"""
        if user_id == self.master_id:
            return False  # 不能挑戰自己的擂台
            
        if self.guardian_id is None:
            return False  # 沒有守護精靈，不能挑戰
            
        # 可以增加更多條件，例如冷卻時間檢查等
        
        return True
    
    def to_dict(self):
        """將擂台資料轉換為字典（用於API）"""
        guardian = Creature.query.get(self.guardian_id) if self.guardian_id else None
        return {
            'id': self.id,
            'name': self.name,
            'bus_stop': self.bus_stop.name if self.bus_stop else None,
            'prestige': self.prestige,
            'master_id': self.master_id,
            'master_name': User.query.get(self.master_id).username if self.master_id else None,
            'guardian': guardian.to_dict() if guardian else None,
            'last_battle': self.last_battle.isoformat() if self.last_battle else None,
            'battle_count': self.battles.count()
        }
    
    def __repr__(self):
        return f'<Arena {self.name} at {self.bus_stop.name if self.bus_stop else "Unknown"}>'


class Battle(app_db.Model):
    """對戰記錄模型"""
    __tablename__ = 'battles'
    
    id = app_db.Column(app_db.Integer, primary_key=True)
    arena_id = app_db.Column(app_db.Integer, app_db.ForeignKey('arenas.id'))
    challenger_id = app_db.Column(app_db.Integer, app_db.ForeignKey('users.id'))  # 挑戰者
    defender_id = app_db.Column(app_db.Integer, app_db.ForeignKey('users.id'))  # 擂台主
    challenger_creature_id = app_db.Column(app_db.Integer, app_db.ForeignKey('creatures.id'))  # 挑戰者精靈
    defender_creature_id = app_db.Column(app_db.Integer, app_db.ForeignKey('creatures.id'))  # 守護精靈
    winner_id = app_db.Column(app_db.Integer, app_db.ForeignKey('users.id'), nullable=True)  # 獲勝者
    battle_log = app_db.Column(app_db.Text)  # 對戰記錄
    experience_gained = app_db.Column(app_db.Integer, default=0)  # 獲得的經驗值
    prestige_change = app_db.Column(app_db.Integer, default=0)  # 擂台聲望值變化
    created_at = app_db.Column(app_db.DateTime, default=datetime.utcnow)
    
    # 關聯
    challenger = app_db.relationship('User', foreign_keys=[challenger_id])
    defender = app_db.relationship('User', foreign_keys=[defender_id])
    challenger_creature = app_db.relationship('Creature', foreign_keys=[challenger_creature_id])
    defender_creature = app_db.relationship('Creature', foreign_keys=[defender_creature_id])
    
    def to_dict(self):
        """將對戰記錄轉換為字典（用於API）"""
        return {
            'id': self.id,
            'arena_id': self.arena_id,
            'arena_name': self.arena.name if self.arena else None,
            'challenger': self.challenger.username,
            'defender': self.defender.username,
            'challenger_creature': self.challenger_creature.name,
            'defender_creature': self.defender_creature.name,
            'winner': User.query.get(self.winner_id).username if self.winner_id else None,
            'experience_gained': self.experience_gained,
            'prestige_change': self.prestige_change,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Battle {self.id} between {self.challenger.username} and {self.defender.username}>'


# 避免循環導入
from app.models.user import User
from app.models.creature import Creature