import random

def battle_system(A_atk: float, A_hp: float, A_type: str,
                  B_atk: float, B_hp: float, B_type: str) -> str:
    # 克制對照表
    advantage_map = {
        'water': 'fire',
        'fire': 'grass',
        'grass': 'water',
        'light': 'dark',
        'dark': 'normal',
        'normal': 'light'
    }

    # 屬性克制修正
    if advantage_map.get(A_type) == B_type:
        A_atk *= 1.05
        B_atk *= 0.95
    elif advantage_map.get(B_type) == A_type:
        B_atk *= 1.05
        A_atk *= 0.95

    # 戰鬥回合
    while A_hp > 0 and B_hp > 0:
        # 每回合擲硬幣決定先攻
        turn = random.randint(0, 1)  # 1: A先, 0: B先

        # 先手攻擊
        if turn == 1:
            damage = A_atk * random.uniform(0.9, 1.1)
            B_hp -= damage
            if B_hp <= 0:
                return "A 勝利"
            damage = B_atk * random.uniform(0.9, 1.1)
            A_hp -= damage
            if A_hp <= 0:
                return "B 勝利"
        else:
            damage = B_atk * random.uniform(0.9, 1.1)
            A_hp -= damage
            if A_hp <= 0:
                return "B 勝利"
            damage = A_atk * random.uniform(0.9, 1.1)
            B_hp -= damage
            if B_hp <= 0:
                return "A 勝利"

    return "平手"

def calculate_battle(host_creature, visitor_creature):
    """計算好友對戰結果"""
    try:
        # 提取精靈數據，確保所有數值都不是 None
        # 優先使用 Firebase 中的實際 attack 和 hp 值
        host_attack_value = host_creature.get('attack')
        host_hp_value = host_creature.get('hp')
        host_power_value = host_creature.get('power')
        
        if host_attack_value is not None:
            host_attack = float(host_attack_value)
        elif host_power_value is not None:
            host_attack = float(host_power_value)
        else:
            host_attack = 100.0
            
        if host_hp_value is not None:
            host_hp = float(host_hp_value)
        elif host_power_value is not None:
            host_hp = float(host_power_value) * 10
        else:
            host_hp = 1000.0
        
        visitor_attack_value = visitor_creature.get('attack')
        visitor_hp_value = visitor_creature.get('hp')
        visitor_power_value = visitor_creature.get('power')
        
        if visitor_attack_value is not None:
            visitor_attack = float(visitor_attack_value)
        elif visitor_power_value is not None:
            visitor_attack = float(visitor_power_value)
        else:
            visitor_attack = 100.0
            
        if visitor_hp_value is not None:
            visitor_hp = float(visitor_hp_value)
        elif visitor_power_value is not None:
            visitor_hp = float(visitor_power_value) * 10
        else:
            visitor_hp = 1000.0
        
        # 獲取元素類型和名稱
        host_element = (host_creature.get('element_type') or 
                       host_creature.get('type') or 
                       host_creature.get('element') or 'normal')
        host_name = host_creature.get('name', '精靈A')
        
        visitor_element = (visitor_creature.get('element_type') or 
                          visitor_creature.get('type') or 
                          visitor_creature.get('element') or 'normal')
        visitor_name = visitor_creature.get('name', '精靈B')        # 戰鬥邏輯基於攻擊力和血量
        # 攻擊力調整 = 基礎攻擊力 * 0.8~1.2隨機
        # 血量調整 = 基礎血量 * 0.9~1.1隨機
        host_atk = host_attack * random.uniform(0.8, 1.2)
        host_hp_battle = host_hp * random.uniform(0.9, 1.1)
        visitor_atk = visitor_attack * random.uniform(0.8, 1.2)
        visitor_hp_battle = visitor_hp * random.uniform(0.9, 1.1)
        
        # 執行戰鬥
        battle_outcome = battle_system(
            A_atk=host_atk, A_hp=host_hp_battle, A_type=host_element.lower(),
            B_atk=visitor_atk, B_hp=visitor_hp_battle, B_type=visitor_element.lower()
        )
        
        # 解析結果
        if battle_outcome == "A 勝利":
            winner = "host"
            winner_name = host_name
            loser_name = visitor_name
        elif battle_outcome == "B 勝利":
            winner = "visitor"
            winner_name = visitor_name
            loser_name = host_name
        else:
            winner = "draw"
            winner_name = None
            loser_name = None
        
        return {
            'winner': winner,
            'winner_name': winner_name,
            'loser_name': loser_name,            'battle_details': {
                'host_stats': {
                    'name': host_name,
                    'element': host_element,
                    'attack': host_attack,
                    'hp': host_hp,
                    'final_atk': round(host_atk, 2),
                    'final_hp': round(host_hp_battle, 2)
                },
                'visitor_stats': {
                    'name': visitor_name,
                    'element': visitor_element,
                    'attack': visitor_attack,
                    'hp': visitor_hp,
                    'final_atk': round(visitor_atk, 2),
                    'final_hp': round(visitor_hp_battle, 2)
                },
                'outcome': battle_outcome
            }
        }
        
    except Exception as e:
        # 如果戰鬥計算失敗，返回平局
        return {
            'winner': 'draw',
            'winner_name': None,
            'loser_name': None,
            'battle_details': {
                'error': str(e),
                'outcome': '戰鬥計算失敗'
            }
        }

"""print(battle_system(
    A_atk=90.0, A_hp=280.0, A_type="fire",
    B_atk=95.0,  B_hp=290.0, B_type="grass"
))"""