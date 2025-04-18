from datetime import datetime
from app import db

class BusRoute(db.Model):
    """公車路線模型"""
    __tablename__ = 'bus_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.String(20), unique=True, nullable=False)  # TDX API 路線ID
    name = db.Column(db.String(64), nullable=False)  # 路線名稱
    departure = db.Column(db.String(64), nullable=False)  # 起點站名
    destination = db.Column(db.String(64), nullable=False)  # 終點站名
    city = db.Column(db.String(20), nullable=False)  # 城市
    operator = db.Column(db.String(64))  # 營運業者
    element_type = db.Column(db.String(20), nullable=False)  # 關聯精靈系統的元素類型
    
    # 關聯
    stops = db.relationship('BusStop', backref='route', lazy='dynamic')
    
    def to_dict(self):
        """將路線資料轉換為字典（用於API）"""
        return {
            'id': self.id,
            'route_id': self.route_id,
            'name': self.name,
            'departure': self.departure,
            'destination': self.destination,
            'city': self.city,
            'operator': self.operator,
            'element_type': self.element_type,
            'stop_count': self.stops.count()
        }
    
    def __repr__(self):
        return f'<BusRoute {self.name} ({self.departure}-{self.destination})>'


class BusStop(db.Model):
    """公車站點模型"""
    __tablename__ = 'bus_stops'
    
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.String(20), unique=True, nullable=False)  # TDX API 站點ID
    name = db.Column(db.String(64), nullable=False)  # 站名
    sequence = db.Column(db.Integer, nullable=False)  # 站序
    latitude = db.Column(db.Float, nullable=False)  # 緯度
    longitude = db.Column(db.Float, nullable=False)  # 經度
    address = db.Column(db.String(128))  # 地址
    
    # 關聯
    route_id = db.Column(db.Integer, db.ForeignKey('bus_routes.id'))
    arena_id = db.Column(db.Integer, db.ForeignKey('arenas.id'), nullable=True)
    
    def to_dict(self):
        """將站點資料轉換為字典（用於API）"""
        return {
            'id': self.id,
            'stop_id': self.stop_id,
            'name': self.name,
            'sequence': self.sequence,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'route_id': self.route_id,
            'has_arena': self.arena_id is not None
        }
    
    def __repr__(self):
        return f'<BusStop {self.name} (seq: {self.sequence})>'


class BusPosition(db.Model):
    """公車即時位置模型"""
    __tablename__ = 'bus_positions'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_numb = db.Column(db.String(20), nullable=False)  # 車牌號碼
    bus_id = db.Column(db.String(20), nullable=False)  # TDX API 公車ID
    route_id = db.Column(db.Integer, db.ForeignKey('bus_routes.id'))
    latitude = db.Column(db.Float, nullable=False)  # 緯度
    longitude = db.Column(db.Float, nullable=False)  # 經度
    direction = db.Column(db.Integer, nullable=False)  # 去程/返程 (0:去程, 1:返程)
    speed = db.Column(db.Float, default=0)  # 車速
    azimuth = db.Column(db.Float)  # 方位角
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)  # 資料更新時間
    
    # 關聯
    route = db.relationship('BusRoute', backref='bus_positions')
    
    def to_dict(self):
        """將公車位置資料轉換為字典（用於API）"""
        return {
            'id': self.id,
            'plate_numb': self.plate_numb,
            'bus_id': self.bus_id,
            'route_id': self.route_id,
            'route_name': self.route.name if self.route else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'direction': self.direction,
            'speed': self.speed,
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<BusPosition {self.plate_numb} ({self.route.name if self.route else "Unknown"})>'


class BusRouteShape(db.Model):
    """公車路線形狀模型"""
    __tablename__ = 'bus_route_shapes'
    
    id = db.Column(db.Integer, primary_key=True)
    route_uid = db.Column(db.String(50), nullable=False)  # TDX API 路線UID
    sub_route_uid = db.Column(db.String(50), nullable=False)  # TDX API 子路線UID
    route_id = db.Column(db.Integer, db.ForeignKey('bus_routes.id'))
    direction = db.Column(db.Integer, nullable=False)  # 去程/返程 (0:去程, 1:返程)
    geometry = db.Column(db.Text)  # GeoJSON 格式的路線幾何資訊
    encoded_polyline = db.Column(db.Text)  # Google編碼折線格式
    version_id = db.Column(db.Integer)  # 資料版本號
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)  # 資料更新時間
    
    # 關聯
    route = db.relationship('BusRoute', backref='route_shapes')
    
    def to_dict(self):
        """將路線形狀資料轉換為字典（用於API）"""
        return {
            'id': self.id,
            'route_uid': self.route_uid,
            'sub_route_uid': self.sub_route_uid,
            'route_id': self.route_id,
            'direction': self.direction,
            'geometry': self.geometry,
            'encoded_polyline': self.encoded_polyline,
            'version_id': self.version_id,
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<BusRouteShape {self.route_uid} (direction: {self.direction})>'