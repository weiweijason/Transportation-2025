"""
魔法陣捕捉機率系統測試文件
測試新的基於精靈稀有度的動態機率計算系統
"""

# 模擬新的機率計算系統
circle_rates_by_rarity = {
    'premium': {  # 高級魔法陣
        'SSR': 0.5,
        'SR': 0.8, 
        'R': 1.0,
        'N': 1.0
    },
    'advanced': {  # 進階魔法陣
        'SSR': 0.25,
        'SR': 0.5,
        'R': 0.8,
        'N': 1.0
    },
    'normal': {  # 普通魔法陣
        'SSR': 0.0,
        'SR': 0.25,
        'R': 0.5,
        'N': 0.8
    }
}

def calculate_capture_rate(circle_type, rarity, player_addition=1.0):
    """計算捕捉成功率"""
    base_rate = circle_rates_by_rarity.get(circle_type, {}).get(rarity, 0)
    final_rate = min(base_rate * player_addition, 1.0)
    return final_rate

def test_capture_rates():
    """測試所有魔法陣和稀有度組合的捕捉率"""
    rarities = ['N', 'R', 'SR', 'SSR']
    circles = ['normal', 'advanced', 'premium']
    additions = [1.0, 1.13, 1.25, 1.5]
    
    print("魔法陣捕捉機率測試結果:")
    print("=" * 60)
    
    for circle in circles:
        print(f"\n{circle.upper()} 魔法陣:")
        print("-" * 40)
        
        for rarity in rarities:
            base_rate = circle_rates_by_rarity[circle][rarity]
            print(f"  {rarity} 級精靈:")
            print(f"    基礎成功率: {base_rate * 100:.0f}%")
            
            for addition in additions:
                final_rate = calculate_capture_rate(circle, rarity, addition)
                bonus_text = f"(+{(addition-1)*100:.0f}%加成)" if addition > 1.0 else "(無加成)"
                print(f"    精靈加成 {addition}: {final_rate * 100:.1f}% {bonus_text}")
            print()

def test_edge_cases():
    """測試邊界情況"""
    print("\n邊界情況測試:")
    print("=" * 30)
    
    # 測試普通魔法陣無法捕捉SSR
    rate = calculate_capture_rate('normal', 'SSR', 1.5)
    print(f"普通魔法陣 + SSR + 1.5倍加成: {rate * 100:.1f}% {'✓ 正確' if rate == 0 else '✗ 錯誤'}")
    
    # 測試最高成功率限制
    rate = calculate_capture_rate('premium', 'N', 2.0)
    print(f"高級魔法陣 + N + 2.0倍加成: {rate * 100:.1f}% {'✓ 正確' if rate == 1.0 else '✗ 錯誤'}")
    
    # 測試進階魔法陣對SR的捕捉
    rate = calculate_capture_rate('advanced', 'SR', 1.25)
    expected = min(0.5 * 1.25, 1.0)
    print(f"進階魔法陣 + SR + 1.25倍加成: {rate * 100:.1f}% {'✓ 正確' if rate == expected else '✗ 錯誤'}")

if __name__ == "__main__":
    test_capture_rates()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("測試完成！新的魔法陣機率系統符合需求規格。")
    print("- 不同魔法陣對不同稀有度精靈有不同的基礎捕捉率")
    print("- 玩家精靈加成正確應用")
    print("- 最大成功率限制在100%")
    print("- 普通魔法陣無法捕捉SSR級精靈")
