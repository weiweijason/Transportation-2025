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
        # 提取精靈數據
        host_power = host_creature.get('power', 100)
        host_element = host_creature.get('element', 'normal').lower()
        host_name = host_creature.get('name', '精靈A')
        
        visitor_power = visitor_creature.get('power', 100)
        visitor_element = visitor_creature.get('element', 'normal').lower()
        visitor_name = visitor_creature.get('name', '精靈B')
        
        # 將power轉換為攻擊力和血量
        # 攻擊力 = power * 0.8~1.2隨機
        # 血量 = power * 2.5~3.5隨機
        host_atk = host_power * random.uniform(0.8, 1.2)
        host_hp = host_power * random.uniform(2.5, 3.5)
        
        visitor_atk = visitor_power * random.uniform(0.8, 1.2)
        visitor_hp = visitor_power * random.uniform(2.5, 3.5)
        
        # 執行戰鬥
        battle_outcome = battle_system(
            A_atk=host_atk, A_hp=host_hp, A_type=host_element,
            B_atk=visitor_atk, B_hp=visitor_hp, B_type=visitor_element
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
            'loser_name': loser_name,
            'battle_details': {
                'host_stats': {
                    'name': host_name,
                    'element': host_element,
                    'power': host_power,
                    'final_atk': round(host_atk, 2),
                    'final_hp': round(host_hp, 2)
                },
                'visitor_stats': {
                    'name': visitor_name,
                    'element': visitor_element,
                    'power': visitor_power,
                    'final_atk': round(visitor_atk, 2),
                    'final_hp': round(visitor_hp, 2)
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