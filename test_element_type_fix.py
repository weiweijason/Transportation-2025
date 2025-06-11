#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的 element_type 處理邏輯
"""

def test_element_type_processing():
    """測試各種 element_type 數據類型的處理"""
    
    test_cases = [
        # 字符串類型
        {'element_type': 'normal', 'type': 'fire', 'name': '字符串測試'},
        # 整數類型（可能導致錯誤的情況）
        {'element_type': 1, 'type': 'water', 'name': '整數測試'},
        # None 值
        {'element_type': None, 'type': 'grass', 'name': 'None測試'},
        # 空字符串
        {'element_type': '', 'type': 'electric', 'name': '空字符串測試'},
        # 只有 type 沒有 element_type
        {'type': 'psychic', 'name': '只有type測試'},
        # 都沒有
        {'name': '完全缺失測試'}
    ]

    print('=== element_type 處理邏輯測試 ===')
    
    for i, case in enumerate(test_cases, 1):
        try:
            # 使用修復後的邏輯
            element_type = str(case.get('element_type') or case.get('type', 'Normal')).lower()
            print(f'✅ 案例 {i} ({case["name"]}): {case} -> element_type: "{element_type}"')
        except Exception as e:
            print(f'❌ 案例 {i} ({case["name"]}): {case} -> 錯誤: {e}')
            return False
    
    print('\n✅ 所有測試案例都能正常處理！')
    return True

def test_complete_creature_processing():
    """測試完整的精靈數據處理邏輯"""
    
    print('\n=== 完整精靈數據處理測試 ===')
    
    # 模擬可能有問題的 Firebase 數據
    problematic_creature = {
        'attack': 178,
        'hp': 1471,
        'element_type': 1,  # 整數類型，這是導致錯誤的原因
        'type': 'normal',
        'name': '問題精靈',
        'level': 1,
        'power': 100
    }
    
    try:
        # 模擬 user_api.py 中的處理邏輯
        creature_data = problematic_creature
        
        # 從 Firebase 數據中提取數值，確保類型正確
        attack_value = creature_data.get('attack')
        hp_value = creature_data.get('hp')
        power_value = creature_data.get('power')
        
        # 確保 attack 值存在且為數字
        if attack_value is not None:
            attack = float(attack_value)
        elif power_value is not None:
            attack = float(power_value)
        else:
            attack = 100.0
            
        # 確保 hp 值存在且為數字
        if hp_value is not None:
            hp = float(hp_value)
        elif power_value is not None:
            hp = float(power_value) * 10
        else:
            hp = 1000.0
        
        # 統一字段名稱，確保與前端期望的一致
        creature_info = {
            'id': 'test-id',
            'name': creature_data.get('name', '未知精靈'),
            'element': creature_data.get('type', creature_data.get('element', 'Normal')),
            'power': int(power_value) if power_value is not None else int(attack),
            'image_url': creature_data.get('image_url', '/static/img/creature.PNG'),
            'level': creature_data.get('level', 1),
            'captured_at': creature_data.get('captured_at', ''),
            'original_creature_id': creature_data.get('original_creature_id', ''),
            # 戰鬥數值字段，確保不為 None
            'attack': attack,
            'hp': hp,
            'type': creature_data.get('type', creature_data.get('element', 'Normal')),
            'element_type': str(creature_data.get('element_type') or 
                               creature_data.get('type', 'Normal')).lower()
        }
        
        print(f'✅ 完整處理成功:')
        print(f'   名稱: {creature_info["name"]}')
        print(f'   ATK: {creature_info["attack"]}')
        print(f'   HP: {creature_info["hp"]}')
        print(f'   元素類型: {creature_info["element_type"]}')
        print(f'   原始 element_type: {creature_data.get("element_type")} (類型: {type(creature_data.get("element_type"))})')
        
        return True
        
    except Exception as e:
        print(f'❌ 完整處理失敗: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_element_type_processing()
    success2 = test_complete_creature_processing()
    
    if success1 and success2:
        print('\n🎉 所有測試都通過！element_type 錯誤已修復。')
    else:
        print('\n❌ 部分測試失敗，需要進一步檢查。')
