from datetime import datetime
import enum
from app import db

class ElementType(enum.Enum):
    """精靈元素類型"""
    FIRE = "fire"      # 火系
    WATER = "water"    # 水系
    EARTH = "earth"    # 地系
    AIR = "air"        # 風系
    ELECTRIC = "electric"  # 電系
    NORMAL = "normal"  # 一般

class Creature(db.Model):
    """精靈模型"""
    __tablename__ = 'creatures'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    species = db.Column(db.String(64), nullable=False)  # 精靈種類
    element_type = db.Column(db.Enum(ElementType), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    power = db.Column(db.Integer, default=10)  # 攻擊力
    defense = db.Column(db.Integer, default=10)  # 防禦力
    hp = db.Column(db.Integer, default=100)  # 血量
    max_hp = db.Column(db.Integer, default=100)  # 最大血量
    image_url = db.Column(db.String(256))  # 精靈圖片URL
    captured_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bus_route_id = db.Column(db.Integer, db.ForeignKey('bus_routes.id'), nullable=True)
    arena_id = db.Column(db.Integer, db.ForeignKey('arenas.id'), nullable=True)
    
    # 關聯查詢
    bus_route = db.relationship('BusRoute', backref='creatures')
    
    def level_up(self):
        """精靈升級"""
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.power += 5
        self.defense += 5
        return self
    
    def heal(self, amount=None):
        """恢復血量"""
        if amount is None:
            self.hp = self.max_hp  # 完全恢復
        else:
            self.hp = min(self.hp + amount, self.max_hp)  # 恢復特定量，但不超過最大值
        return self
    
    def is_effective_against(self, other_creature):
        """檢查屬性相剋關係"""
        # 元素克制關係字典
        effectiveness = {
            ElementType.FIRE: [ElementType.AIR, ElementType.EARTH],  # 火克風和地
            ElementType.WATER: [ElementType.FIRE, ElementType.ELECTRIC],  # 水克火和電
            ElementType.EARTH: [ElementType.ELECTRIC, ElementType.WATER],  # 地克電和水
            ElementType.AIR: [ElementType.EARTH],  # 風克地
            ElementType.ELECTRIC: [ElementType.AIR, ElementType.WATER],  # 電克風和水
            ElementType.NORMAL: []  # 一般沒有特別克制
        }
        
        return other_creature.element_type in effectiveness.get(self.element_type, [])
    
    def calculate_damage(self, target):
        """計算對目標造成的傷害"""
        # 基本傷害公式
        base_damage = max(5, self.power - target.defense // 2)
        
        # 屬性克制加成
        if self.is_effective_against(target):
            base_damage = int(base_damage * 1.5)  # 克制加成50%
            
        # 等級差異加成
        level_bonus = max(0, (self.level - target.level) * 0.1)
        final_damage = int(base_damage * (1 + level_bonus))
        
        return max(1, final_damage)  # 最小傷害為1
    
    def to_dict(self):
        """將精靈數據轉換為字典（用於API）"""
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
            'element_type': self.element_type.value,
            'level': self.level,
            'experience': self.experience,
            'power': self.power,
            'defense': self.defense,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'image_url': self.image_url,
            'owner_id': self.user_id,
            'bus_route': self.bus_route.name if self.bus_route else None
        }
    
    def __repr__(self):
        return f'<Creature {self.name} ({self.species}/{self.element_type.value})>'