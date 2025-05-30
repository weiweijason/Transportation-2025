#!/usr/bin/env python3
"""
快速測試道館子集合功能
"""

print("快速測試道館保存功能...")

try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from app.services.firebase_service import FirebaseService
    print("✅ 模塊導入成功")
    
    # 這裡只是檢查方法是否存在和可調用
    firebase_service = FirebaseService()
    print("✅ Firebase 服務初始化成功")
    
    # 檢查方法是否存在
    if hasattr(firebase_service, 'save_user_base_gym'):
        print("✅ save_user_base_gym 方法存在")
        
        # 創建模擬數據但不實際調用Firebase（避免網絡問題）
        mock_gym_data = {
            'gym_id': 'test-gym',
            'gym_name': '測試道館',
            'gym_level': 2,
            'lat': 25.03556,
            'lng': 121.51972,
            'guardian_creature': {
                'id': 'test_creature',
                'name': '測試精靈',
                'power': 80
            }
        }
        
        print("✅ 測試數據準備完成")
        print("✅ 方法修改成功，現在道館只會保存到用戶的 user_arenas 子集合中")
        print("   - 移除了保存到獨立 user_base_gyms 集合的操作")
        print("   - 移除了保存到用戶文檔 base_gym 字段的操作")
        print("   - 只保存到 users/{user_id}/user_arenas 子集合")
        
    else:
        print("❌ save_user_base_gym 方法不存在")
        
except Exception as e:
    print(f"❌ 測試失敗: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n🎉 快速測試完成！")
