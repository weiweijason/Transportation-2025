#!/usr/bin/env python3
"""
道館戰鬥系統測試腳本
測試新的道館戰鬥API功能
"""

import sys
import os
import requests
import json

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_arena_battle_api():
    """測試道館戰鬥API"""
    base_url = "http://localhost:5000"
    
    print("開始測試道館戰鬥API...")
    
    # 測試獲取道館詳情
    print("\n1. 測試獲取道館詳情...")
    test_arena_id = "arena-level-1-001"
    
    try:
        response = requests.get(f"{base_url}/game/api/arena-battle/get-arena/{test_arena_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ 成功獲取道館: {data['arena']['name']}")
                print(f"  等級: {data['arena']['level']}")
                print(f"  擁有者: {data['arena']['owner'] or '無'}")
                if data.get('created'):
                    print("  (新創建的道館)")
            else:
                print(f"✗ 獲取道館失敗: {data.get('message')}")
        else:
            print(f"✗ API調用失敗: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
    
    # 測試獲取用戶精靈（需要登入，會失敗但可以看到響應）
    print("\n2. 測試獲取用戶精靈...")
    try:
        response = requests.get(f"{base_url}/game/api/arena-battle/get-user-creatures?arena_level=1")
        print(f"  響應狀態: HTTP {response.status_code}")
        if response.status_code == 401:
            print("  ✓ 正確要求登入認證")
        elif response.status_code == 200:
            data = response.json()
            print(f"  響應: {data}")
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
    
    # 測試精靈等級限制邏輯
    print("\n3. 測試精靈等級限制邏輯...")
    test_creatures = [
        {'rarity': 'N', 'name': 'N級精靈'},
        {'rarity': 'R', 'name': 'R級精靈'},
        {'rarity': 'SR', 'name': 'SR級精靈'},
        {'rarity': 'SSR', 'name': 'SSR級精靈'},
    ]
    
    from app.routes.game.arena_battle_api import is_creature_allowed_in_arena
    
    for level in [1, 2, 3]:
        print(f"\n  等級 {level} 道館:")
        for creature in test_creatures:
            allowed = is_creature_allowed_in_arena(creature, level)
            status = "✓" if allowed else "✗"
            print(f"    {status} {creature['name']} ({creature['rarity']})")
    
    # 測試獎勵計算
    print("\n4. 測試獎勵計算...")
    from app.routes.game.arena_battle_api import calculate_arena_rewards
    from datetime import datetime, timedelta
    
    # 模擬道館數據
    test_arena_data = {
        'level': 2,
        'occupied_at': (datetime.now() - timedelta(hours=3)).isoformat(),
        'rewards': {
            'last_collected': (datetime.now() - timedelta(hours=2)).isoformat(),
            'accumulated_hours': 0,
            'available_rewards': []
        }
    }
    
    rewards = calculate_arena_rewards(test_arena_data)
    print(f"  獎勵計算結果:")
    print(f"    累積小時: {rewards['accumulated_hours']}")
    print(f"    可領取獎勵: {len(rewards['available_rewards'])}")
    for reward in rewards['available_rewards']:
        print(f"      - {reward['description']}")
    
    print("\n測試完成！")

if __name__ == "__main__":
    test_arena_battle_api()
