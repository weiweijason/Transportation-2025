from datetime import datetime
from app import db

class Arena(db.Model):
    """擂台模型（每個公車站點可以有一個擂台）"""
    __tablename__ = 'arenas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    prestige = db.Column(db.Integer, default=0)  # 擂台聲望值，越高越難挑戰
    last_battle = db.Column(db.DateTime, nullable=True)  # 上次對戰時間
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    bus_stop_id = db.Column(db.Integer, db.ForeignKey('bus_stops.id'), unique=True)
    master_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 擂台主人
    guardian_id = db.Column(db.Integer, db.ForeignKey('creatures.id'), nullable=True)  # 守護精靈
    
    # 反向關聯
    bus_stop = db.relationship('BusStop', backref=db.backref('arena', uselist=False))
    guardian = db.relationship('Creature', foreign_keys=[guardian_id])
    battles = db.relationship('Battle', backref='arena', lazy='dynamic')
    
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
                db.session.add(old_arena)
                
        self.guardian_id = creature.id
        creature.arena_id = self.id
        db.session.add(creature)
        db.session.add(self)
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
                db.session.add(old_guardian)
        
        # 設置新守護精靈
        if new_guardian_id:
            new_guardian = Creature.query.get(new_guardian_id)
            if new_guardian and new_guardian.user_id == new_master_id:
                self.guardian_id = new_guardian_id
                new_guardian.arena_id = self.id
                db.session.add(new_guardian)
        else:
            self.guardian_id = None
            
        self.last_battle = datetime.utcnow()
        db.session.add(self)
        return old_master_id
    
    def increase_prestige(self, amount=1):
        """增加擂台聲望值"""
        self.prestige += amount
        db.session.add(self)
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


class Battle(db.Model):
    """對戰記錄模型"""
    __tablename__ = 'battles'
    
    id = db.Column(db.Integer, primary_key=True)
    arena_id = db.Column(db.Integer, db.ForeignKey('arenas.id'))
    challenger_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 挑戰者
    defender_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 擂台主
    challenger_creature_id = db.Column(db.Integer, db.ForeignKey('creatures.id'))  # 挑戰者精靈
    defender_creature_id = db.Column(db.Integer, db.ForeignKey('creatures.id'))  # 守護精靈
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 獲勝者
    battle_log = db.Column(db.Text)  # 對戰記錄
    experience_gained = db.Column(db.Integer, default=0)  # 獲得的經驗值
    prestige_change = db.Column(db.Integer, default=0)  # 擂台聲望值變化
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    challenger = db.relationship('User', foreign_keys=[challenger_id])
    defender = db.relationship('User', foreign_keys=[defender_id])
    challenger_creature = db.relationship('Creature', foreign_keys=[challenger_creature_id])
    defender_creature = db.relationship('Creature', foreign_keys=[defender_creature_id])
    
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