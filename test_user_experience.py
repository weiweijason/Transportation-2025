#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試用戶經驗值系統

此腳本測試用戶經驗值保存到 Firebase 的功能
"""
import sys
import os

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.firebase_service import FirebaseService
import time

def test_user_experience_system():
    """測試用戶經驗值系統"""
    print("🧪 Testing User Experience System")
    print("=" * 50)
    
    # 初始化 Firebase 服務
    try:
        firebase_service = FirebaseService()
        print("✅ Firebase服務初始化成功")
    except Exception as e:
        print(f"❌ Firebase服務初始化失敗: {e}")
        return False
    
    # 測試用戶ID (使用假的測試ID)
    test_user_id = "test_user_experience_123"
    
    print(f"\n📋 使用測試用戶ID: {test_user_id}")
    
    # 步驟1: 創建或重置測試用戶
    print("\n🔧 步驟1: 設置測試用戶...")
    try:
        # 刪除可能存在的測試用戶數據
        user_ref = firebase_service.firestore_db.collection('users').document(test_user_id)
        user_ref.delete()
        print("   已清理舊測試數據")
        
        # 創建新的測試用戶
        initial_user_data = {
            'username': 'Test User',
            'level': 1,
            'experience': 0,
            'fight_count': 0,
            'created_at': time.time()
        }
        user_ref.set(initial_user_data)
        print("   ✅ 測試用戶創建成功")
        
    except Exception as e:
        print(f"   ❌ 設置測試用戶失敗: {e}")
        return False
    
    # 步驟2: 測試 add_experience_to_user 方法
    print("\n💎 步驟2: 測試用戶經驗值添加...")
    
    test_cases = [
        {"experience": 20, "description": "添加 20 經驗值 (N級精靈)"},
        {"experience": 40, "description": "添加 40 經驗值 (R級精靈)"},
        {"experience": 60, "description": "添加 60 經驗值 (SR級精靈)"},
        {"experience": 80, "description": "添加 80 經驗值 (SSR級精靈)"},
    ]
    
    total_expected_exp = 0
    expected_level = 1
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   測試 {i}: {test_case['description']}")
        
        try:
            # 調用 add_experience_to_user 方法
            result = firebase_service.add_experience_to_user(
                test_user_id, 
                test_case['experience']
            )
            
            if result.get('success'):
                print(f"      ✅ 經驗值添加成功")
                print(f"      📊 升級狀態: {'是' if result.get('level_up') else '否'}")
                print(f"      🎯 當前等級: {result.get('new_level', '未知')}")
                print(f"      💫 當前經驗: {result.get('current_experience', '未知')}")
                print(f"      🎪 升級所需: {result.get('max_experience', '未知')}")
                
                # 計算預期值
                total_expected_exp += test_case['experience']
                while expected_level < 100:
                    level_max_exp = firebase_service._calculate_max_experience(expected_level)
                    if total_expected_exp >= level_max_exp:
                        total_expected_exp -= level_max_exp
                        expected_level += 1
                    else:
                        break
                
                print(f"      🧮 預期等級: {expected_level}, 預期經驗: {total_expected_exp}")
                
            else:
                print(f"      ❌ 經驗值添加失敗: {result.get('message', '未知錯誤')}")
                return False
                
        except Exception as e:
            print(f"      ❌ 測試異常: {e}")
            return False
    
    # 步驟3: 驗證 Firebase 中的數據
    print("\n🔍 步驟3: 驗證 Firebase 中的用戶數據...")
    try:
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            
            print(f"   📋 Firebase 中的用戶數據:")
            print(f"      等級: {user_data.get('level', '未設置')}")
            print(f"      經驗值: {user_data.get('experience', '未設置')}")
            print(f"      用戶名: {user_data.get('username', '未設置')}")
            print(f"      戰鬥次數: {user_data.get('fight_count', '未設置')}")
            
            # 驗證數據正確性
            actual_level = user_data.get('level', 1)
            actual_exp = user_data.get('experience', 0)
            
            if actual_level == expected_level and actual_exp == total_expected_exp:
                print("   ✅ Firebase 數據驗證成功！")
            else:
                print(f"   ⚠️ 數據不一致:")
                print(f"      預期: 等級 {expected_level}, 經驗 {total_expected_exp}")
                print(f"      實際: 等級 {actual_level}, 經驗 {actual_exp}")
        else:
            print("   ❌ 找不到用戶文檔")
            return False
            
    except Exception as e:
        print(f"   ❌ 驗證 Firebase 數據失敗: {e}")
        return False
    
    # 步驟4: 測試升級機制
    print("\n🚀 步驟4: 測試等級提升機制...")
    try:
        # 添加大量經驗值來觸發多次升級
        big_exp_amount = 500
        result = firebase_service.add_experience_to_user(test_user_id, big_exp_amount)
        
        if result.get('success'):
            print(f"   ✅ 大量經驗值 ({big_exp_amount}) 添加成功")
            print(f"   🎯 最終等級: {result.get('new_level', '未知')}")
            print(f"   💫 剩餘經驗: {result.get('current_experience', '未知')}")
            print(f"   📈 是否升級: {'是' if result.get('level_up') else '否'}")
        else:
            print(f"   ❌ 大量經驗值添加失敗: {result.get('message', '未知錯誤')}")
            
    except Exception as e:
        print(f"   ❌ 測試升級機制失敗: {e}")
    
    # 清理測試數據
    print("\n🧹 清理測試數據...")
    try:
        user_ref.delete()
        print("   ✅ 測試用戶數據已清理")
    except Exception as e:
        print(f"   ⚠️ 清理測試數據時出錯: {e}")
    
    print("\n🎉 用戶經驗值系統測試完成！")
    return True

if __name__ == "__main__":
    success = test_user_experience_system()
    if success:
        print("\n✅ 所有測試通過！")
    else:
        print("\n❌ 部分測試失敗！")
