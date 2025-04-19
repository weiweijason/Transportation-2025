import time
from app.services.firebase_service import FirebaseService
from datetime import datetime
from app import db as app_db

class FirebaseArena:
    """
    擂台(道館)模型 - Firebase 版本
    擂台為公車站牌，同名站牌視為同一個擂台，即使位置不同
    """
    def __init__(self, id=None, name=None, position=None, stop_ids=None, routes=None, 
                 owner=None, owner_creature=None, challengers=None):
        self.id = id
        self.name = name  # 站牌名稱，作為唯一識別符
        self.position = position  # [lat, lng] 格式
        self.stop_ids = stop_ids or []  # 站牌ID列表
        self.routes = routes or []  # 經過路線列表
        self.owner = owner  # 控制者 (用戶名稱)
        self.owner_creature = owner_creature  # 控制者精靈 (包含id, name, power)
        self.challengers = challengers or []  # 挑戰紀錄
        self.updated_at = int(time.time() * 1000)  # 更新時間 (毫秒時間戳)
        # 獲取 Firebase 服務實例
        self.firebase_service = FirebaseService()
        self.db = self.firebase_service.db

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
            challengers=arena_dict.get('challengers', [])
        )

    def to_dict(self):
        """將擂台轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'stopIds': self.stop_ids,
            'routes': self.routes,
            'owner': self.owner,
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
    
    def save(self):
        """保存擂台"""
        self.updated_at = int(time.time() * 1000)
        self.db.child('arenas').child(self.id).set(self.to_dict())
        return self
    
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
            
        # 計算勝率 - 挑戰者力量 / (挑戰者力量 + 防守者力量)
        win_chance = challenger_power / (challenger_power + self.owner_creature.get('power', 0))
        
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
    bus_stop = app_db.relationship('BusStop', backref=app_db.backref('arena', uselist=False))
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