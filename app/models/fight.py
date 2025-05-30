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

"""print(battle_system(
    A_atk=90.0, A_hp=280.0, A_type="fire",
    B_atk=95.0,  B_hp=290.0, B_type="grass"
))"""