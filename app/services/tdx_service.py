import os
import time
import requests
import jwt
from datetime import datetime, timedelta
from urllib.parse import urlencode

from flask import current_app
from app import db
from app.models.bus import BusRoute, BusStop, BusPosition

class TDXService:
    """TDX API 服務類"""
    
    def __init__(self, client_id=None, client_secret=None):
        """初始化TDX服務"""
        self.client_id = client_id or current_app.config['TDX_CLIENT_ID']
        self.client_secret = client_secret or current_app.config['TDX_CLIENT_SECRET']
        self.auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        self.api_url = "https://tdx.transportdata.tw/api/basic/v2"
        self.token = None
        self.token_expires = None
    
    def get_auth_header(self):
        """獲取認證頭信息"""
        # 檢查令牌是否過期
        if self.token is None or self.token_expires is None or datetime.now() >= self.token_expires:
            self._refresh_token()
            
        return {"Authorization": f"Bearer {self.token}"}
    
    def _refresh_token(self):
        """刷新令牌"""
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(self.auth_url, data=payload)
        if response.status_code != 200:
            raise Exception(f"無法獲取TDX令牌: {response.text}")
            
        token_data = response.json()
        self.token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 1800)  # 預設30分鐘
        self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)  # 提前1分鐘刷新
    
    def get_city_bus_routes(self, city="Taipei", route_name=None):
        """獲取指定城市的公車路線"""
        url = f"{self.api_url}/Bus/Route/City/{city}"
        
        params = {}
        if route_name:
            params["$filter"] = f"contains(RouteName/Zh_tw, '{route_name}')"
        
        params["$format"] = "JSON"
        
        if params:
            url = f"{url}?{urlencode(params)}"
        
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