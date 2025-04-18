import os
import time
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode

from flask import current_app
from app import db
from app.models.bus import BusRoute, BusStop, BusPosition

class TDXAuth:
    """TDX 認證類，依照官方範例實現"""
    
    def __init__(self, client_id=None, client_secret=None):
        """初始化 TDX 認證"""
        self.client_id = client_id or current_app.config['TDX_CLIENT_ID']
        self.client_secret = client_secret or current_app.config['TDX_CLIENT_SECRET']
        self.auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    
    def get_auth_header(self):
        """獲取認證請求頭，完全符合官方範例"""
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'
        
        return {
            'content-type': content_type,
            'grant_type': grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

class TDXData:
    """TDX 資料處理類，依照官方範例實現"""
    
    def __init__(self, client_id, client_secret, auth_response):
        """初始化 TDX 資料處理"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_response = auth_response
        self.token_expires = None
        self._set_token_expiry()
    
    def _set_token_expiry(self):
        """設置令牌過期時間"""
        auth_JSON = json.loads(self.auth_response.text)
        expires_in = auth_JSON.get('expires_in', 1800)  # 預設30分鐘
        self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)  # 提前1分鐘刷新
    
    def get_data_header(self):
        """獲取資料請求頭，完全符合官方範例"""
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')
        
        return {
            'authorization': 'Bearer ' + access_token,
            'Accept-Encoding': 'gzip'
        }
    
    def is_token_valid(self):
        """檢查令牌是否有效"""
        return self.token_expires is not None and datetime.now() < self.token_expires

class TDXService:
    """TDX API 服務類"""
    
    def __init__(self, client_id=None, client_secret=None):
        """初始化TDX服務"""
        self.client_id = client_id or current_app.config['TDX_CLIENT_ID']
        self.client_secret = client_secret or current_app.config['TDX_CLIENT_SECRET']
        self.auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        self.api_url = "https://tdx.transportdata.tw/api/basic/v2"
        self.tdx_data = None
        self._init_auth()
    
    def _init_auth(self):
        """初始化認證"""
        auth = TDXAuth(self.client_id, self.client_secret)
        auth_response = requests.post(self.auth_url, data=auth.get_auth_header())
        self.tdx_data = TDXData(self.client_id, self.client_secret, auth_response)
    
    def get_auth_header(self):
        """獲取認證頭信息"""
        # 檢查令牌是否過期
        if self.tdx_data is None or not self.tdx_data.is_token_valid():
            self._init_auth()
            
        return self.tdx_data.get_data_header()
    
    def get_city_bus_routes(self, city="Taipei", route_name=None):
        """獲取指定城市的公車路線"""
        url = f"{self.api_url}/Bus/Route/City/{city}"
        
        params = {}
        if route_name:
            params["$filter"] = f"contains(RouteName/Zh_tw, '{route_name}')"
        
        params["$format"] = "JSON"
        
        if params:
            url = f"{url}?{urlencode(params)}"
        
        try:
            response = requests.get(url, headers=self.get_auth_header())
            if response.status_code != 200:
                current_app.logger.error(f"無法獲取公車路線資料: {response.text}")
                return []
                
            return response.json()
        except:
            # 若請求失敗，重新進行認證並再次嘗試
            self._init_auth()
            response = requests.get(url, headers=self.get_auth_header())
            if response.status_code != 200:
                current_app.logger.error(f"無法獲取公車路線資料: {response.text}")
                return []
                
            return response.json()
    
    def get_city_bus_route_stops(self, city="Taipei", route_name=None):
        """獲取指定城市公車路線的站牌資訊"""
        url = f"{self.api_url}/Bus/StopOfRoute/City/{city}"
        
        params = {}
        if route_name:
            params["$filter"] = f"contains(RouteName/Zh_tw, '{route_name}')"
        
        params["$format"] = "JSON"
        
        if params:
            url = f"{url}?{urlencode(params)}"
        
        response = requests.get(url, headers=self.get_auth_header())
        if response.status_code != 200:
            current_app.logger.error(f"無法獲取公車站牌資料: {response.text}")
            return []
            
        return response.json()
    
    def get_city_bus_dynamic_positions(self, city="Taipei", route_name=None):
        """獲取指定城市公車的即時位置資訊"""
        url = f"{self.api_url}/Bus/RealTimeByFrequency/City/{city}"
        
        params = {}
        if route_name:
            params["$filter"] = f"contains(RouteName/Zh_tw, '{route_name}')"
        
        params["$format"] = "JSON"
        
        if params:
            url = f"{url}?{urlencode(params)}"
        
        response = requests.get(url, headers=self.get_auth_header())
        if response.status_code != 200:
            current_app.logger.error(f"無法獲取公車即時位置資料: {response.text}")
            return []
            
        return response.json()
    
    def get_city_bus_estimated_arrival(self, city="Taipei", route_name=None, stop_name=None):
        """獲取指定城市公車的預估到站時間"""
        url = f"{self.api_url}/Bus/EstimatedTimeOfArrival/City/{city}"
        
        params = {}
        filters = []
        
        if route_name:
            filters.append(f"contains(RouteName/Zh_tw, '{route_name}')")
            
        if stop_name:
            filters.append(f"contains(StopName/Zh_tw, '{stop_name}')")
            
        if filters:
            params["$filter"] = " and ".join(filters)
        
        params["$format"] = "JSON"
        
        if params:
            url = f"{url}?{urlencode(params)}"
        
        response = requests.get(url, headers=self.get_auth_header())
        if response.status_code != 200:
            current_app.logger.error(f"無法獲取公車預估到站資料: {response.text}")
            return []
            
        return response.json()
    
    def sync_bus_routes(self, city="Taipei", routes=None):
        """同步指定城市的公車路線資料到資料庫"""
        # 如果指定了特定路線，則只同步這些路線
        for route_name in routes or [None]:
            routes_data = self.get_city_bus_routes(city, route_name)
            
            for route_data in routes_data:
                route_id = route_data.get('RouteID')
                zh_name = route_data.get('RouteName', {}).get('Zh_tw', '')
                
                # 檢查路線是否已存在
                route = BusRoute.query.filter_by(route_id=route_id).first()
                if not route:
                    route = BusRoute(
                        route_id=route_id,
                        name=zh_name,
                        departure=route_data.get('DepartureStopNameZh', ''),
                        destination=route_data.get('DestinationStopNameZh', ''),
                        city=city,
                        operator=route_data.get('OperatorName', {}).get('Zh_tw', ''),
                        # 根據路線名稱或ID分配元素類型
                        element_type="fire" if route_name == routes[0] else "water"
                    )
                    db.session.add(route)
            
            db.session.commit()
            
            # 同步站點資料
            self.sync_bus_stops(city, route_name)
            
            # 等待一下以避免API請求過快
            time.sleep(1)
    
    def sync_bus_stops(self, city="Taipei", route_name=None):
        """同步指定城市的公車站點資料到資料庫"""
        stops_data = self.get_city_bus_route_stops(city, route_name)
        
        for route_stops in stops_data:
            route_id = route_stops.get('RouteID')
            route = BusRoute.query.filter_by(route_id=route_id).first()
            
            if not route:
                current_app.logger.warning(f"找不到路線 {route_id}，無法同步站點")
                continue
                
            for direction in route_stops.get('Stops', []):
                for stop_data in direction:
                    stop_id = stop_data.get('StopID')
                    zh_name = stop_data.get('StopName', {}).get('Zh_tw', '')
                    
                    # 檢查站點是否已存在
                    stop = BusStop.query.filter_by(stop_id=stop_id).first()
                    if not stop:
                        stop = BusStop(
                            stop_id=stop_id,
                            name=zh_name,
                            sequence=stop_data.get('StopSequence', 0),
                            latitude=stop_data.get('StopPosition', {}).get('PositionLat', 0),
                            longitude=stop_data.get('StopPosition', {}).get('PositionLon', 0),
                            address=stop_data.get('StopAddress', ''),
                            route_id=route.id
                        )
                        db.session.add(stop)
            
            db.session.commit()
    
    def update_bus_positions(self, city="Taipei", route_name=None):
        """更新指定城市的公車即時位置資料"""
        positions_data = self.get_city_bus_dynamic_positions(city, route_name)
        
        # 獲取更新的時間戳
        now = datetime.utcnow()
        
        for position_data in positions_data:
            bus_id = position_data.get('PlateNumb')
            route_id = position_data.get('RouteID')
            
            route = BusRoute.query.filter_by(route_id=route_id).first()
            if not route:
                continue
                
            # 檢查是否已有此公車的位置記錄
            bus_position = BusPosition.query.filter_by(bus_id=bus_id, route_id=route.id).first()
            
            # 位置數據
            lat = position_data.get('BusPosition', {}).get('PositionLat', 0)
            lng = position_data.get('BusPosition', {}).get('PositionLon', 0)
            
            if bus_position:
                # 更新位置
                bus_position.latitude = lat
                bus_position.longitude = lng
                bus_position.direction = position_data.get('Direction', 0)
                bus_position.speed = position_data.get('Speed', 0)
                bus_position.azimuth = position_data.get('Azimuth')
                bus_position.updated_at = now
            else:
                # 創建新記錄
                bus_position = BusPosition(
                    plate_numb=position_data.get('PlateNumb', ''),
                    bus_id=bus_id,
                    route_id=route.id,
                    latitude=lat,
                    longitude=lng,
                    direction=position_data.get('Direction', 0),
                    speed=position_data.get('Speed', 0),
                    azimuth=position_data.get('Azimuth'),
                    updated_at=now
                )
                db.session.add(bus_position)
                
        db.session.commit()
    
    def get_bus_route_shape(self, city="Taipei", route_uid=None, sub_route_uid=None):
        """獲取公車路線形狀資料
        
        參數:
        city (str): 城市，預設為臺北市
        route_uid (str): 路線唯一識別碼，可選
        sub_route_uid (str): 子路線唯一識別碼，可選
        
        返回:
        list: 路線形狀資料列表
        """
        url = f"{self.api_url}/Bus/Shape/City/{city}"
        
        params = {}
        if route_uid:
            params["$filter"] = f"RouteUID eq '{route_uid}'"
            if sub_route_uid:
                params["$filter"] += f" and SubRouteUID eq '{sub_route_uid}'"
        
        params["$format"] = "JSON"
        
        if params:
            url = f"{url}?{urlencode(params)}"
        
        try:
            response = requests.get(url, headers=self.get_auth_header())
            if response.status_code != 200:
                current_app.logger.error(f"無法獲取公車路線形狀資料: {response.text}")
                return []
                
            return response.json()
        except Exception as e:
            current_app.logger.error(f"獲取公車路線形狀資料時發生錯誤: {str(e)}")
            # 若請求失敗，重新進行認證並再次嘗試
            self._init_auth()
            try:
                response = requests.get(url, headers=self.get_auth_header())
                if response.status_code != 200:
                    current_app.logger.error(f"無法獲取公車路線形狀資料: {response.text}")
                    return []
                    
                return response.json()
            except Exception as e:
                current_app.logger.error(f"重試獲取公車路線形狀資料時發生錯誤: {str(e)}")
                return []
    
    def save_bus_route_shape(self, shape_data, route_id=None):
        """儲存公車路線形狀資料到資料庫
        
        參數:
        shape_data (dict): 路線形狀資料，格式如下:
        {
            "RouteUID": "string",
            "RouteID": "string",
            "RouteName": {
                "Zh_tw": "string",
                "En": "string"
            },
            "SubRouteUID": "string",
            "SubRouteID": "string",
            "SubRouteName": {
                "Zh_tw": "string",
                "En": "string"
            },
            "Direction": 0,
            "Geometry": "string",
            "EncodedPolyline": "string",
            "UpdateTime": "2025-04-18T00:53:46.335Z",
            "VersionID": 0
        }
        route_id (int): 對應的 BusRoute 模型 ID，可選
        
        返回:
        BusRouteShape: 儲存的公車路線形狀模型
        """
        from app.models.bus import BusRouteShape, BusRoute
        
        # 若未提供 route_id，嘗試從資料庫中查找
        if route_id is None and shape_data.get('RouteID'):
            route = BusRoute.query.filter_by(route_id=shape_data['RouteID']).first()
            if route:
                route_id = route.id
        
        # 檢查資料庫中是否已存在此路線形狀
        existing_shape = BusRouteShape.query.filter_by(
            route_uid=shape_data['RouteUID'],
            sub_route_uid=shape_data['SubRouteUID'],
            direction=shape_data['Direction']
        ).first()
        
        if existing_shape:
            # 更新現有記錄
            existing_shape.geometry = shape_data.get('Geometry')
            existing_shape.encoded_polyline = shape_data.get('EncodedPolyline')
            existing_shape.version_id = shape_data.get('VersionID')
            existing_shape.updated_at = datetime.now()
            db.session.commit()
            return existing_shape
        else:
            # 創建新記錄
            new_shape = BusRouteShape(
                route_uid=shape_data['RouteUID'],
                sub_route_uid=shape_data['SubRouteUID'],
                route_id=route_id,
                direction=shape_data['Direction'],
                geometry=shape_data.get('Geometry'),
                encoded_polyline=shape_data.get('EncodedPolyline'),
                version_id=shape_data.get('VersionID'),
                updated_at=datetime.now()
            )
            db.session.add(new_shape)
            db.session.commit()
            return new_shape
    
    def get_cat_right_route(self):
        """獲取貓空右線路線資料
        
        Returns:
            list: 貓空右線路線形狀資料的列表
        """
        # 直接使用特定的 URL 來獲取貓空右線路線形狀資料
        url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Shape/City/Taipei/%E8%B2%93%E7%A9%BA%E5%8F%B3%E7%B7%9A?%24top=30&%24format=JSON"
        
        try:
            # 先嘗試使用現有的授權頭獲取數據
            response = requests.get(url, headers=self.get_auth_header())
            if response.status_code != 200:
                current_app.logger.error(f"無法獲取貓空右線路線形狀資料: {response.text}")
                return []
            
            # 記錄返回的原始數據，便於調試
            data = response.json()
            # current_app.logger.info(f"TDX API 返回原始數據: {data}")
            
            # 確保返回的數據是一個列表
            if not isinstance(data, list):
                current_app.logger.warning("TDX API 返回的數據不是列表格式，嘗試轉換")
                if isinstance(data, dict):
                    # 如果是字典格式，嘗試提取相關字段
                    data = [data]
                else:
                    # 其他情況，返回空列表
                    return []
            
            # 確保每個路線對象都有必要的字段
            for i, route in enumerate(data):
                if 'Geometry' not in route or not route['Geometry']:
                    current_app.logger.warning(f"路線 {i} 缺少 Geometry 字段")
                    # 如果缺少 Geometry 字段，可以移除這個路線
                    continue
                
                # 確保路線具有必要的屬性
                if 'RouteName' not in route:
                    route['RouteName'] = {'Zh_tw': '貓空右線'}
                if 'Direction' not in route:
                    route['Direction'] = 0
                if 'SubRouteID' not in route:
                    route['SubRouteID'] = '未知子路線'
            
            return data
        except Exception as e:
            current_app.logger.error(f"獲取貓空右線路線形狀資料時發生錯誤: {str(e)}")
            # 若請求失敗，重新進行認證並再次嘗試，完全符合官方範例的錯誤處理模式
            try:
                # 重新進行認證
                self._init_auth()
                # 再次嘗試請求
                response = requests.get(url, headers=self.get_auth_header())
                if response.status_code != 200:
                    current_app.logger.error(f"重試後仍無法獲取貓空右線路線形狀資料: {response.text}")
                    return []
                
                data = response.json()
                # 同樣進行數據格式檢查和轉換
                if not isinstance(data, list):
                    if isinstance(data, dict):
                        data = [data]
                    else:
                        return []
                
                # 確保每個路線對象都有必要的字段
                for i, route in enumerate(data):
                    if 'Geometry' not in route or not route['Geometry']:
                        continue
                    if 'RouteName' not in route:
                        route['RouteName'] = {'Zh_tw': '貓空右線'}
                    if 'Direction' not in route:
                        route['Direction'] = 0
                    if 'SubRouteID' not in route:
                        route['SubRouteID'] = '未知子路線'
                
                return data
            except Exception as e:
                current_app.logger.error(f"重試獲取貓空右線路線形狀資料時發生錯誤: {str(e)}")
                return []
    
    def get_cat_left_route(self):
        """獲取貓空左線(動物園)路線資料
        
        Returns:
            list: 貓空左線(動物園)路線形狀資料的列表
        """
        # 直接使用特定的 URL 來獲取貓空左線(動物園)路線形狀資料
        url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Shape/City/Taipei/%E8%B2%93%E7%A9%BA%E5%B7%A6%E7%B7%9A%28%E5%8B%95%E7%89%A9%E5%9C%92%29?%24top=30&%24format=JSON"
        
        try:
            # 先嘗試使用現有的授權頭獲取數據
            response = requests.get(url, headers=self.get_auth_header())
            if response.status_code != 200:
                current_app.logger.error(f"無法獲取貓空左線(動物園)路線形狀資料: {response.text}")
                return []
            
            # 記錄返回的原始數據，便於調試
            data = response.json()
            
            # 確保返回的數據是一個列表
            if not isinstance(data, list):
                current_app.logger.warning("TDX API 返回的數據不是列表格式，嘗試轉換")
                if isinstance(data, dict):
                    # 如果是字典格式，嘗試提取相關字段
                    data = [data]
                else:
                    # 其他情況，返回空列表
                    return []
            
            # 確保每個路線對象都有必要的字段
            for i, route in enumerate(data):
                if 'Geometry' not in route or not route['Geometry']:
                    current_app.logger.warning(f"路線 {i} 缺少 Geometry 字段")
                    # 如果缺少 Geometry 字段，可以移除這個路線
                    continue
                
                # 確保路線具有必要的屬性
                if 'RouteName' not in route:
                    route['RouteName'] = {'Zh_tw': '貓空左線(動物園)'}
                if 'Direction' not in route:
                    route['Direction'] = 0
                if 'SubRouteID' not in route:
                    route['SubRouteID'] = '未知子路線'
            
            return data
        except Exception as e:
            current_app.logger.error(f"獲取貓空左線(動物園)路線形狀資料時發生錯誤: {str(e)}")
            # 若請求失敗，重新進行認證並再次嘗試
            try:
                # 重新進行認證
                self._init_auth()
                # 再次嘗試請求
                response = requests.get(url, headers=self.get_auth_header())
                if response.status_code != 200:
                    current_app.logger.error(f"重試後仍無法獲取貓空左線(動物園)路線形狀資料: {response.text}")
                    return []
                
                data = response.json()
                # 同樣進行數據格式檢查和轉換
                if not isinstance(data, list):
                    if isinstance(data, dict):
                        data = [data]
                    else:
                        return []
                
                # 確保每個路線對象都有必要的字段
                for i, route in enumerate(data):
                    if 'Geometry' not in route or not route['Geometry']:
                        continue
                    if 'RouteName' not in route:
                        route['RouteName'] = {'Zh_tw': '貓空左線(動物園)'}
                    if 'Direction' not in route:
                        route['Direction'] = 0
                    if 'SubRouteID' not in route:
                        route['SubRouteID'] = '未知子路線'
                
                return data
            except Exception as e:
                current_app.logger.error(f"重試獲取貓空左線(動物園)路線形狀資料時發生錯誤: {str(e)}")
                return []
    
    def get_cat_left_zhinan_route(self):
        """獲取貓空左線(指南宮)路線資料
        
        Returns:
            list: 貓空左線(指南宮)路線形狀資料的列表
        """
        # 直接使用特定的 URL 來獲取貓空左線(指南宮)路線形狀資料
        url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Shape/City/Taipei/%E8%B2%93%E7%A9%BA%E5%B7%A6%E7%B7%9A%28%E6%8C%87%E5%8D%97%E5%AE%AE%29?%24top=30&%24format=JSON"
        
        try:
            # 先嘗試使用現有的授權頭獲取數據
            response = requests.get(url, headers=self.get_auth_header())
            if response.status_code != 200:
                current_app.logger.error(f"無法獲取貓空左線(指南宮)路線形狀資料: {response.text}")
                return []
            
            # 記錄返回的原始數據，便於調試
            data = response.json()
            
            # 確保返回的數據是一個列表
            if not isinstance(data, list):
                current_app.logger.warning("TDX API 返回的數據不是列表格式，嘗試轉換")
                if isinstance(data, dict):
                    # 如果是字典格式，嘗試提取相關字段
                    data = [data]
                else:
                    # 其他情況，返回空列表
                    return []
            
            # 確保每個路線對象都有必要的字段
            for i, route in enumerate(data):
                if 'Geometry' not in route or not route['Geometry']:
                    current_app.logger.warning(f"路線 {i} 缺少 Geometry 字段")
                    # 如果缺少 Geometry 字段，可以移除這個路線
                    continue
                
                # 確保路線具有必要的屬性
                if 'RouteName' not in route:
                    route['RouteName'] = {'Zh_tw': '貓空左線(指南宮)'}
                if 'Direction' not in route:
                    route['Direction'] = 0
                if 'SubRouteID' not in route:
                    route['SubRouteID'] = '未知子路線'
            
            return data
        except Exception as e:
            current_app.logger.error(f"獲取貓空左線(指南宮)路線形狀資料時發生錯誤: {str(e)}")
            # 若請求失敗，重新進行認證並再次嘗試
            try:
                # 重新進行認證
                self._init_auth()
                # 再次嘗試請求
                response = requests.get(url, headers=self.get_auth_header())
                if response.status_code != 200:
                    current_app.logger.error(f"重試後仍無法獲取貓空左線(指南宮)路線形狀資料: {response.text}")
                    return []
                
                data = response.json()
                # 同樣進行數據格式檢查和轉換
                if not isinstance(data, list):
                    if isinstance(data, dict):
                        data = [data]
                    else:
                        return []
                
                # 確保每個路線對象都有必要的字段
                for i, route in enumerate(data):
                    if 'Geometry' not in route or not route['Geometry']:
                        continue
                    if 'RouteName' not in route:
                        route['RouteName'] = {'Zh_tw': '貓空左線(指南宮)'}
                    if 'Direction' not in route:
                        route['Direction'] = 0
                    if 'SubRouteID' not in route:
                        route['SubRouteID'] = '未知子路線'
                
                return data
            except Exception as e:
                current_app.logger.error(f"重試獲取貓空左線(指南宮)路線形狀資料時發生錯誤: {str(e)}")
                return []
    
    def get_nearby_stops(self, lat, lon, radius=500, city="Taipei"):
        """獲取指定坐標附近的公車站點
        
        Args:
            lat (float): 緯度
            lon (float): 經度
            radius (int): 搜尋半徑（公尺）
            city (str): 城市名稱
            
        Returns:
            list: 附近站點列表
        """
        # 從資料庫直接查詢
        from math import radians, cos, sin, asin, sqrt
        from app.models.bus import BusStop
        
        # 使用 Haversine 公式計算距離
        def haversine(lat1, lon1, lat2, lon2):
            # 將經緯度轉換為弧度
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            
            # Haversine 公式
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371000  # 地球半徑（公尺）
            return c * r
        
        # 查詢所有站點
        all_stops = BusStop.query.all()
        nearby_stops = []
        
        for stop in all_stops:
            # 計算距離
            distance = haversine(float(lat), float(lon), stop.latitude, stop.longitude)
            
            # 如果在搜尋半徑內，加入結果列表
            if distance <= float(radius):
                stop_data = stop.to_dict()
                stop_data['distance'] = round(distance)
                nearby_stops.append(stop_data)
        
        # 按距離排序
        nearby_stops.sort(key=lambda x: x['distance'])
        
        return nearby_stops
    
    def get_city_bus_route_shapes(self, city="Taipei", route_name=None):
        """獲取指定城市公車路線的形狀資料"""
        url = f"{self.api_url}/Bus/Shape/City/{city}"
        
        params = {}
        if route_name:
            params["$filter"] = f"contains(RouteName/Zh_tw, '{route_name}')"
        
        params["$format"] = "JSON"
        
        if params:
            url = f"{url}?{urlencode(params)}"
        
        try:
            response = requests.get(url, headers=self.get_auth_header())
            if response.status_code != 200:
                current_app.logger.error(f"無法獲取公車路線形狀資料: {response.text}")
                return []
                
            return response.json()
        except Exception as e:
            current_app.logger.error(f"獲取公車路線形狀資料時發生錯誤: {str(e)}")
            # 若請求失敗，重新進行認證並再次嘗試
            self._init_auth()
            response = requests.get(url, headers=self.get_auth_header())
            if response.status_code != 200:
                current_app.logger.error(f"無法獲取公車路線形狀資料: {response.text}")
                return []
                
            return response.json()