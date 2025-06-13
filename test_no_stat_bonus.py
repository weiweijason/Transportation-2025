#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試移除稀有度屬性加成功能後的經驗值系統
"""

import sys
import os

# 添加專案路徑到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.services.firebase_service import FirebaseService
    print("✅ Firebase服務初始化成功")
except Exception as e:
    print(f"❌ Firebase服務初始化失敗: {e}")
    sys.exit(1)

def test_removed_stat_bonus():
    """測試稀有度屬性加成功能已被移除"""
    
    print("\n🔧 測試移除屬性加成功能:")
    
    try:
        firebase_service = FirebaseService()
        
        # 檢查 _get_stat_bonus_by_rate 方法是否已被移除
        if hasattr(firebase_service, '_get_stat_bonus_by_rate'):
            print("   ❌ _get_stat_bonus_by_rate 方法仍然存在")
            return False
        else:
            print("   ✅ _get_stat_bonus_by_rate 方法已成功移除")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 測試過程中發生錯誤: {e}")
        return False

def test_experience_system_still_works():
    """測試經驗值系統在移除屬性加成後是否仍正常工作"""
    
    print("\n🧪 測試經驗值系統:")
    
    try:
        firebase_service = FirebaseService()
        
        # 測試經驗值計算
        level_1_exp = firebase_service._calculate_max_experience(1)
        level_2_exp = firebase_service._calculate_max_experience(2)
        level_5_exp = firebase_service._calculate_max_experience(5)
        
        print(f"   等級 1 所需經驗: {level_1_exp}")
        print(f"   等級 2 所需經驗: {level_2_exp}")
        print(f"   等級 5 所需經驗: {level_5_exp}")
        
        # 驗證計算結果
        expected_values = {1: 100, 2: 200, 5: 1600}
        
        for level, expected in expected_values.items():
            actual = firebase_service._calculate_max_experience(level)
            if actual == expected:
                print(f"   ✅ 等級 {level} 經驗值計算正確: {actual}")
            else:
                print(f"   ❌ 等級 {level} 經驗值計算錯誤: 期望 {expected}, 實際 {actual}")
                return False
        
        print("   ✅ 經驗值系統工作正常")
        return True
        
    except Exception as e:
        print(f"   ❌ 測試過程中發生錯誤: {e}")
        return False

def main():
    """主測試函數"""
    
    print("🎮 測試移除稀有度屬性加成功能")
    print("=" * 50)
    
    # 測試項目
    tests = [
        ("移除屬性加成功能", test_removed_stat_bonus),
        ("經驗值系統功能", test_experience_system_still_works)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 測試: {test_name}")
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有測試通過！屬性加成功能已成功移除，經驗值系統仍正常工作。")
    else:
        print("❌ 某些測試失敗。")
    
    return all_passed

if __name__ == "__main__":
    main()
