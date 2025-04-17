from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class User(UserMixin, db.Model):
    """使用者模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.String(128), default='default.png')
    experience = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    last_location_lat = db.Column(db.Float, nullable=True)
    last_location_lng = db.Column(db.Float, nullable=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    creatures = db.relationship('Creature', backref='owner', lazy='dynamic')
    arenas = db.relationship('Arena', backref='master', lazy='dynamic')
    
    @property
    def password(self):
        """禁止直接讀取密碼"""
        raise AttributeError('密碼不可讀取')
    
    @password.setter
    def password(self, password):
        """設置密碼（加密存儲）"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)
    
    def update_location(self, lat, lng):
        """更新使用者位置"""
        self.last_location_lat = lat
        self.last_location_lng = lng
        self.last_active = datetime.utcnow()
        db.session.add(self)
        
    def add_experience(self, points):
        """增加經驗值並檢查是否升級"""
        self.experience += points
        
        # 簡單的升級邏輯 (可根據需求調整)
        level_threshold = self.level * 100  # 每級所需經驗增加100
        if self.experience >= level_threshold:
            self.level += 1
            return True  # 表示已升級
        return False
    
    def to_dict(self):
        """將用戶數據轉換為字典（用於API）"""
        return {
            'id': self.id,
            'username': self.username,
            'avatar': self.avatar,
            'level': self.level,
            'experience': self.experience,
            'creature_count': self.creatures.count(),
            'arena_count': self.arenas.count()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login載入使用者的回調函數"""
    return User.query.get(int(user_id))