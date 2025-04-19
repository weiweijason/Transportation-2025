import requests
import json
import os
from datetime import datetime, timedelta
import time
import random
import logging
import pathlib

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# TDX API 配置參數
TDX_CLIENT_ID = os.getenv('TDX_CLIENT_ID', 'tdx-client-id')
TDX_CLIENT_SECRET = os.getenv('TDX_CLIENT_SECRET', 'tdx-client-secret')
TDX_API_URL = "https://tdx.transportdata.tw/api/basic"

# 本地數據存儲配置
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
ROUTES_DATA_DIR = os.path.join(DATA_DIR, 'routes')
STOPS_DATA_DIR = os.path.join(DATA_DIR, 'stops')

# 確保數據目錄存在
pathlib.Path(ROUTES_DATA_DIR).mkdir(parents=True, exist_ok=True)
pathlib.Path(STOPS_DATA_DIR).mkdir(parents=True, exist_ok=True)

# 本地數據文件路徑
LOCAL_DATA_FILES = {
    'cat-right-route': os.path.join(ROUTES_DATA_DIR, 'cat_right_route.json'),
    'cat-left-route': os.path.join(ROUTES_DATA_DIR, 'cat_left_route.json'),
    'cat-left-zhinan-route': os.path.join(ROUTES_DATA_DIR, 'cat_left_zhinan_route.json'),
    'cat-right-stops': os.path.join(STOPS_DATA_DIR, 'cat_right_stops.json'),
    'cat-left-stops': os.path.join(STOPS_DATA_DIR, 'cat_left_stops.json'),
    'cat-left-zhinan-stops': os.path.join(STOPS_DATA_DIR, 'cat_left_zhinan_stops.json'),
}

# 緩存配置
TOKEN_CACHE = {
    'token': None,
    'expires_at': None
}

# 本地數據過期時間 (小時)
LOCAL_DATA_EXPIRE_HOURS = 24  # 數據過期時間，默認24小時

# API 請求重試配置
MAX_RETRIES = 3
BASE_DELAY = 2  # 基礎延遲（秒）
RATE_LIMIT_DELAY = 5  # 遇到 429 錯誤時的延遲（秒）

def get_tdx_token():
    """
    獲取 TDX API 訪問令牌
    如果已有有效令牌，直接返回；否則獲取新令牌
    """
    global TOKEN_CACHE
    
    # 檢查緩存中是否有未過期的令牌
    if (TOKEN_CACHE['token'] and TOKEN_CACHE['expires_at'] 
        and datetime.now() < TOKEN_CACHE['expires_at']):
        return TOKEN_CACHE['token']
    
    # 請求新令牌
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": TDX_CLIENT_ID,
        "client_secret": TDX_CLIENT_SECRET
    }
    
    try:
        response = requests.post(auth_url, data=auth_data)
        response.raise_for_status()  # Raise error for bad responses
        auth_response = response.json()
        
        # 更新緩存
        TOKEN_CACHE['token'] = auth_response.get('access_token')
        # 設置過期時間 (比實際過期時間提前5分鐘)
        expires_in_seconds = auth_response.get('expires_in', 900) - 300
        TOKEN_CACHE['expires_at'] = datetime.now() + timedelta(seconds=expires_in_seconds)
        
        return TOKEN_CACHE['token']
    except Exception as e:
        logger.error(f"TDX API Token 獲取錯誤: {e}")
        return None

def make_tdx_request(url, token):
    """
    通用 TDX API 請求函數，包含重試機制
    
    Args:
        url: API 請求 URL
        token: TDX API 認證令牌
        
    Returns:
        API 回應資料，若請求失敗則返回空列表
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # 增加隨機延遲，避免短時間內大量請求
            if retries > 0:
                jitter = random.uniform(0, 1)
                delay = BASE_DELAY * (2 ** retries) + jitter
                time.sleep(delay)
                
            response = requests.get(url, headers=headers)
            
            # 處理不同狀態碼
            if response.status_code == 429:  # Too Many Requests
                # 遇到頻率限制，等待更長時間
                time.sleep(RATE_LIMIT_DELAY * (2 ** retries))
                retries += 1
                continue
                
            response.raise_for_status()
            data = response.json()
            
            return data
            
        except requests.exceptions.RequestException as e:
            # 記錄錯誤
            logger.error(f"TDX API 請求錯誤 (重試 {retries+1}/{MAX_RETRIES}): {e}")
            
            # 如果不是 429 錯誤，使用標準退避策略
            if not (hasattr(e.response, 'status_code') and e.response.status_code == 429):
                jitter = random.uniform(0, 1)
                delay = BASE_DELAY * (2 ** retries) + jitter
                time.sleep(delay)
            
            retries += 1
    
    # 所有重試都失敗
    return []

def save_data_to_file(data, file_path):
    """
    將數據保存到本地文件
    
    Args:
        data: 要保存的數據
        file_path: 文件保存路徑
    
    Returns:
        bool: 保存是否成功
    """
    try:
        # 確保目錄存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存數據
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'data': data,
                'timestamp': datetime.now().timestamp(),
                'expires_at': (datetime.now() + timedelta(hours=LOCAL_DATA_EXPIRE_HOURS)).timestamp()
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"數據成功保存到: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存數據到文件失敗: {e}")
        return False

def load_data_from_file(file_path):
    """
    從本地文件讀取數據
    
    Args:
        file_path: 文件讀取路徑
    
    Returns:
        data: 讀取的數據，如果文件不存在或已過期則返回None
    """
    try:
        if not os.path.exists(file_path):
            logger.info(f"本地數據文件不存在: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
            
        # 檢查數據是否過期
        expires_at = file_data.get('expires_at', 0)
        if expires_at < datetime.now().timestamp():
            logger.info(f"本地數據已過期: {file_path}")
            return None
            
        logger.info(f"從本地文件讀取數據: {file_path}")
        return file_data.get('data')
    except Exception as e:
        logger.error(f"從文件讀取數據失敗: {e}")
        return None

def process_geojson_data(data, output_type="route"):
    """
    處理GeoJSON格式的回應資料
    
    Args:
        data: GeoJSON格式的回應資料
        output_type: 輸出類型，"route"或"stops"
        
    Returns:
        處理後的資料列表
    """
    if not data or not isinstance(data, dict) or "features" not in data:
        return []
    
    result = []
    
    if output_type == "route":
        # 處理路線資料 - 需要LineString或MultiLineString類型的要素
        for feature in data["features"]:
            geometry_type = feature.get("geometry", {}).get("type")
            
            # 處理普通LineString類型
            if geometry_type == "LineString":
                coordinates = feature.get("geometry", {}).get("coordinates", [])
                for coord in coordinates:
                    if len(coord) >= 2:
                        # 轉換格式 [經度, 緯度] -> {"PositionLat": 緯度, "PositionLon": 經度}
                        result.append({
                            "PositionLon": coord[0],
                            "PositionLat": coord[1]
                        })
            
            # 處理MultiLineString類型 (貓空左線指南宮使用這種格式)
            elif geometry_type == "MultiLineString":
                logger.info("檢測到MultiLineString格式的路線資料，可能是貓空左線(指南宮)")
                multi_coordinates = feature.get("geometry", {}).get("coordinates", [])
                
                # MultiLineString是一個線段集合，每個線段包含兩個點
                # 我們需要提取所有點，但要避免重複
                added_points = set()  # 用於追踪已添加的點，避免重複
                
                for line_segment in multi_coordinates:
                    for coord in line_segment:
                        if len(coord) >= 2:
                            # 創建一個可哈希的座標點表示
                            point_key = (coord[0], coord[1])
                            
                            # 如果這個點還沒添加過，則添加
                            if point_key not in added_points:
                                added_points.add(point_key)
                                result.append({
                                    "PositionLon": coord[0],
                                    "PositionLat": coord[1]
                                })
                
                logger.info(f"從MultiLineString中提取了 {len(result)} 個唯一座標點")
    
    elif output_type == "stops":
        # 處理站點資料 - 只需要Point類型的要素
        for feature in data["features"]:
            if feature.get("geometry", {}).get("type") == "Point":
                coords = feature.get("geometry", {}).get("coordinates", [])
                if len(coords) >= 2:
                    # 獲取站點資訊
                    stop_info = feature.get("properties", {}).get("model", {})
                    stop = {
                        "StopID": stop_info.get("StopID"),
                        "StopName": {"Zh_tw": stop_info.get("StopName")},
                        "StopPosition": {
                            "PositionLon": coords[0],
                            "PositionLat": coords[1]
                        },
                        "StopSequence": stop_info.get("StopSequence")
                    }
                    result.append(stop)
    
    return result

def fetch_and_save_cat_right_route():
    """
    獲取并保存貓空右線的路線資料
    """
    logger.info("開始獲取貓空右線路線資料")
    token = get_tdx_token()
    if not token:
        logger.error("獲取TDX Token失敗")
        return False
    
    # 使用V3 Map API獲取GeoJSON格式的路線資料
    url = f"{TDX_API_URL}/V3/Map/Bus/Network/StopOfRoute/City/Taipei/RouteName/貓空右線?$format=GEOJSON"
    
    data = make_tdx_request(url, token)
    
    # 處理GeoJSON格式的資料
    route_data = process_geojson_data(data, "route")
    
    # 保存到本地文件
    success = save_data_to_file(route_data, LOCAL_DATA_FILES['cat-right-route'])
    return success

def fetch_and_save_cat_left_route():
    """
    獲取并保存貓空左線(動物園)的路線資料
    """
    logger.info("開始獲取貓空左線(動物園)路線資料")
    token = get_tdx_token()
    if not token:
        logger.error("獲取TDX Token失敗")
        return False
    
    # 使用V3 Map API獲取GeoJSON格式的路線資料
    url = f"{TDX_API_URL}/V3/Map/Bus/Network/StopOfRoute/City/Taipei/RouteName/貓空左線(動物園)?$format=GEOJSON"
    
    data = make_tdx_request(url, token)
    
    # 處理GeoJSON格式的資料
    route_data = process_geojson_data(data, "route")
    
    # 保存到本地文件
    success = save_data_to_file(route_data, LOCAL_DATA_FILES['cat-left-route'])
    return success

def fetch_and_save_cat_left_zhinan_route():
    """
    獲取并保存貓空左線(指南宮)的路線資料
    """
    logger.info("開始獲取貓空左線(指南宮)路線資料")
    token = get_tdx_token()
    if not token:
        logger.error("獲取TDX Token失敗")
        return False
    
    # 使用V3 Map API獲取GeoJSON格式的路線資料
    url = f"{TDX_API_URL}/V3/Map/Bus/Network/StopOfRoute/City/Taipei/RouteName/%E8%B2%93%E7%A9%BA%E5%B7%A6%E7%B7%9A%28%E6%8C%87%E5%8D%97%E5%AE%AE%29?%24top=3&%24format=GEOJSON"
    
    data = make_tdx_request(url, token)
    
    # 處理GeoJSON格式的資料
    route_data = process_geojson_data(data, "route")
    
    # 保存到本地文件
    success = save_data_to_file(route_data, LOCAL_DATA_FILES['cat-left-zhinan-route'])
    return success

def fetch_and_save_cat_right_stops():
    """
    獲取并保存貓空右線的站牌資料
    """
    logger.info("開始獲取貓空右線站點資料")
    token = get_tdx_token()
    if not token:
        logger.error("獲取TDX Token失敗")
        return False
    
    # 使用V3 Map API獲取GeoJSON格式的站點資料
    url = f"{TDX_API_URL}/V3/Map/Bus/Network/StopOfRoute/City/Taipei/RouteName/貓空右線?$format=GEOJSON"
    
    data = make_tdx_request(url, token)
    
    # 處理GeoJSON格式的資料
    stops_data = process_geojson_data(data, "stops")
    
    # 保存到本地文件
    success = save_data_to_file(stops_data, LOCAL_DATA_FILES['cat-right-stops'])
    return success

def fetch_and_save_cat_left_stops():
    """
    獲取并保存貓空左線(動物園)的站牌資料
    """
    logger.info("開始獲取貓空左線(動物園)站點資料")
    token = get_tdx_token()
    if not token:
        logger.error("獲取TDX Token失敗")
        return False
    
    # 使用V3 Map API獲取GeoJSON格式的站點資料
    url = f"{TDX_API_URL}/V3/Map/Bus/Network/StopOfRoute/City/Taipei/RouteName/貓空左線(動物園)?$format=GEOJSON"
    
    data = make_tdx_request(url, token)
    
    # 處理GeoJSON格式的資料
    stops_data = process_geojson_data(data, "stops")
    
    # 保存到本地文件
    success = save_data_to_file(stops_data, LOCAL_DATA_FILES['cat-left-stops'])
    return success

def fetch_and_save_cat_left_zhinan_stops():
    """
    獲取并保存貓空左線(指南宮)的站牌資料
    """
    logger.info("開始獲取貓空左線(指南宮)站點資料")
    token = get_tdx_token()
    if not token:
        logger.error("獲取TDX Token失敗")
        return False
    
    # 使用V3 Map API獲取GeoJSON格式的站點資料
    url = f"{TDX_API_URL}/V3/Map/Bus/Network/StopOfRoute/City/Taipei/RouteName/貓空左線(指南宮)?$format=GEOJSON"
    
    data = make_tdx_request(url, token)
    
    # 處理GeoJSON格式的資料
    stops_data = process_geojson_data(data, "stops")
    
    # 保存到本地文件
    success = save_data_to_file(stops_data, LOCAL_DATA_FILES['cat-left-zhinan-stops'])
    return success

def fetch_all_data():
    """
    獲取并保存所有貓空纜車路線和站點資料
    先抓取路線資料，等待一分鐘後再抓取站點資料，避免因API限制而獲取到空資料
    
    Returns:
        dict: 每個資料類型的獲取結果
    """
    # 先抓取所有路線資料
    logger.info("第一階段: 開始獲取所有路線資料...")
    route_results = {}
    
    # 抓取第一條路線資料
    logger.info("抓取貓空右線路線資料...")
    route_results['cat-right-route'] = fetch_and_save_cat_right_route()
    print(f"=== 貓空右線路線資料抓取完成, 結果: {'成功' if route_results['cat-right-route'] else '失敗'} ===")
    
    # 等待15秒再抓取下一條路線資料
    wait_seconds = 15
    logger.info(f"等待 {wait_seconds} 秒，以避免API請求限制...")
    print(f"=== 等待 {wait_seconds} 秒後抓取下一條路線資料... ===")
    time.sleep(wait_seconds)
    
    # 抓取第二條路線資料
    logger.info("抓取貓空左線(動物園)路線資料...")
    route_results['cat-left-route'] = fetch_and_save_cat_left_route()
    print(f"=== 貓空左線(動物園)路線資料抓取完成, 結果: {'成功' if route_results['cat-left-route'] else '失敗'} ===")
    
    # 再等待15秒抓取最後一條路線資料
    logger.info(f"等待 {wait_seconds} 秒，以避免API請求限制...")
    print(f"=== 等待 {wait_seconds} 秒後抓取最後一條路線資料... ===")
    time.sleep(wait_seconds)
    
    # 抓取第三條路線資料
    logger.info("抓取貓空左線(指南宮)路線資料...")
    route_results['cat-left-zhinan-route'] = fetch_and_save_cat_left_zhinan_route()
    print(f"=== 貓空左線(指南宮)路線資料抓取完成, 結果: {'成功' if route_results['cat-left-zhinan-route'] else '失敗'} ===")
    
    # 計算路線資料抓取的成功率
    route_success_count = sum(1 for success in route_results.values() if success)
    route_total_count = len(route_results)
    logger.info(f"路線資料獲取完成，結果: {route_success_count}/{route_total_count} 項成功")
    print(f"=== 路線資料獲取完成: {route_success_count}/{route_total_count} 項成功 ===")
    
    # 等待一分鐘，避免因為TDX API限制而無法獲取站點資料
    wait_time = 60  # 等待秒數
    logger.info(f"等待 {wait_time} 秒，以避免API請求限制...")
    print(f"=== 等待 {wait_time} 秒後開始抓取站點資料... ===")
    time.sleep(wait_time)
    
    # 然後抓取所有站點資料，這裡也按照順序依次抓取，每次間隔15秒
    logger.info("第二階段: 開始獲取所有站點資料...")
    stops_results = {}
    
    # 抓取第一個站點資料
    logger.info("抓取貓空右線站點資料...")
    stops_results['cat-right-stops'] = fetch_and_save_cat_right_stops()
    print(f"=== 貓空右線站點資料抓取完成, 結果: {'成功' if stops_results['cat-right-stops'] else '失敗'} ===")
    
    # 等待15秒再抓取下一個站點資料
    logger.info(f"等待 {wait_seconds} 秒，以避免API請求限制...")
    print(f"=== 等待 {wait_seconds} 秒後抓取下一個站點資料... ===")
    time.sleep(wait_seconds)
    
    # 抓取第二個站點資料
    logger.info("抓取貓空左線(動物園)站點資料...")
    stops_results['cat-left-stops'] = fetch_and_save_cat_left_stops()
    print(f"=== 貓空左線(動物園)站點資料抓取完成, 結果: {'成功' if stops_results['cat-left-stops'] else '失敗'} ===")
    
    # 再等待15秒抓取最後一個站點資料
    logger.info(f"等待 {wait_seconds} 秒，以避免API請求限制...")
    print(f"=== 等待 {wait_seconds} 秒後抓取最後一個站點資料... ===")
    time.sleep(wait_seconds)
    
    # 抓取第三個站點資料
    logger.info("抓取貓空左線(指南宮)站點資料...")
    stops_results['cat-left-zhinan-stops'] = fetch_and_save_cat_left_zhinan_stops()
    print(f"=== 貓空左線(指南宮)站點資料抓取完成, 結果: {'成功' if stops_results['cat-left-zhinan-stops'] else '失敗'} ===")
    
    # 計算站點資料抓取的成功率
    stops_success_count = sum(1 for success in stops_results.values() if success)
    stops_total_count = len(stops_results)
    logger.info(f"站點資料獲取完成，結果: {stops_success_count}/{stops_total_count} 項成功")
    print(f"=== 站點資料獲取完成: {stops_success_count}/{stops_total_count} 項成功 ===")
    
    # 合併結果
    results = {**route_results, **stops_results}
    
    # 計算總體抓取的成功率
    total_success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    logger.info(f"所有資料獲取完成，結果: {total_success_count}/{total_count} 項成功")
    print(f"=== 所有TDX資料獲取完成: {total_success_count}/{total_count} 項成功 ===")
    
    return results

def get_cat_right_route():
    """
    獲取貓空右線的路線資料
    優先從本地文件讀取，如果不存在或已過期則從API獲取
    """
    # 嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-right-route'])
    
    if local_data is not None:
        return local_data
    
    # 本地數據不存在或已過期，從API獲取
    logger.info("本地貓空右線路線數據不存在或已過期，從API獲取")
    fetch_and_save_cat_right_route()
    
    # 再次嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-right-route'])
    
    # 如果仍然無法獲取數據，返回空列表
    if local_data is None:
        logger.warning("無法獲取貓空右線路線數據，返回空列表")
        return []
        
    return local_data

def get_cat_left_route():
    """
    獲取貓空左線(動物園)的路線資料
    優先從本地文件讀取，如果不存在或已過期則從API獲取
    """
    # 嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-left-route'])
    
    if local_data is not None:
        return local_data
    
    # 本地數據不存在或已過期，從API獲取
    logger.info("本地貓空左線(動物園)路線數據不存在或已過期，從API獲取")
    fetch_and_save_cat_left_route()
    
    # 再次嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-left-route'])
    
    # 如果仍然無法獲取數據，返回空列表
    if local_data is None:
        logger.warning("無法獲取貓空左線(動物園)路線數據，返回空列表")
        return []
        
    return local_data

def get_cat_left_zhinan_route():
    """
    獲取貓空左線(指南宮)的路線資料
    優先從本地文件讀取，如果不存在或已過期則從API獲取
    """
    # 嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-left-zhinan-route'])
    
    if local_data is not None:
        return local_data
    
    # 本地數據不存在或已過期，從API獲取
    logger.info("本地貓空左線(指南宮)路線數據不存在或已過期，從API獲取")
    fetch_and_save_cat_left_zhinan_route()
    
    # 再次嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-left-zhinan-route'])
    
    # 如果仍然無法獲取數據，返回空列表
    if local_data is None:
        logger.warning("無法獲取貓空左線(指南宮)路線數據，返回空列表")
        return []
        
    return local_data

def get_cat_right_stops():
    """
    獲取貓空右線的站牌資料
    優先從本地文件讀取，如果不存在或已過期則從API獲取
    """
    # 嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-right-stops'])
    
    if local_data is not None:
        return local_data
    
    # 本地數據不存在或已過期，從API獲取
    logger.info("本地貓空右線站點數據不存在或已過期，從API獲取")
    fetch_and_save_cat_right_stops()
    
    # 再次嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-right-stops'])
    
    # 如果仍然無法獲取數據，返回空列表
    if local_data is None:
        logger.warning("無法獲取貓空右線站點數據，返回空列表")
        return []
        
    return local_data

def get_cat_left_stops():
    """
    獲取貓空左線(動物園)的站牌資料
    優先從本地文件讀取，如果不存在或已過期則從API獲取
    """
    # 嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-left-stops'])
    
    if local_data is not None:
        return local_data
    
    # 本地數據不存在或已過期，從API獲取
    logger.info("本地貓空左線(動物園)站點數據不存在或已過期，從API獲取")
    fetch_and_save_cat_left_stops()
    
    # 再次嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-left-stops'])
    
    # 如果仍然無法獲取數據，返回空列表
    if local_data is None:
        logger.warning("無法獲取貓空左線(動物園)站點數據，返回空列表")
        return []
        
    return local_data

def get_cat_left_zhinan_stops():
    """
    獲取貓空左線(指南宮)的站牌資料
    優先從本地文件讀取，如果不存在或已過期則從API獲取
    """
    # 嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-left-zhinan-stops'])
    
    if local_data is not None:
        return local_data
    
    # 本地數據不存在或已過期，從API獲取
    logger.info("本地貓空左線(指南宮)站點數據不存在或已過期，從API獲取")
    fetch_and_save_cat_left_zhinan_stops()
    
    # 再次嘗試從本地文件讀取
    local_data = load_data_from_file(LOCAL_DATA_FILES['cat-left-zhinan-stops'])
    
    # 如果仍然無法獲取數據，返回空列表
    if local_data is None:
        logger.warning("無法獲取貓空左線(指南宮)站點數據，返回空列表")
        return []
        
    return local_data

def get_data_status():
    """
    獲取所有本地數據的狀態
    
    Returns:
        dict: 各個數據文件的狀態信息
    """
    status = {}
    
    for data_type, file_path in LOCAL_DATA_FILES.items():
        try:
            if not os.path.exists(file_path):
                status[data_type] = {
                    'exists': False,
                    'timestamp': None,
                    'expires_at': None,
                    'is_expired': True,
                    'size': 0
                }
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                
            timestamp = file_data.get('timestamp')
            expires_at = file_data.get('expires_at')
            
            status[data_type] = {
                'exists': True,
                'timestamp': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else None,
                'expires_at': datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S') if expires_at else None,
                'is_expired': expires_at < datetime.now().timestamp() if expires_at else True,
                'size': os.path.getsize(file_path),
                'data_count': len(file_data.get('data', [])) if 'data' in file_data else 0
            }
        except Exception as e:
            logger.error(f"獲取數據狀態失敗 ({data_type}): {e}")
            status[data_type] = {
                'exists': os.path.exists(file_path),
                'error': str(e)
            }
    
    return status