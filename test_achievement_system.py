"""
成就系統測試腳本
用於驗證成就系統的各個組件是否正常工作
"""

import sys
import os
import time

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_achievement_models():
    """測試成就模型"""
    print("🔍 測試成就模型...")
    
    try:
        from app.models.achievement import ACHIEVEMENTS, get_achievements_by_category, CATEGORY_DISPLAY_NAMES, CATEGORY_ICONS
        
        print(f"✅ 成就定義載入成功: {len(ACHIEVEMENTS)} 個成就")
        
        categories = get_achievements_by_category()
        print(f"✅ 成就分類載入成功: {len(categories)} 個分類")
        
        for category_name, achievements_list in categories.items():
            print(f"   📂 {category_name}: {len(achievements_list)} 個成就")
        
        print(f"✅ 類別顯示名稱: {len(CATEGORY_DISPLAY_NAMES)} 個")
        print(f"✅ 類別圖標: {len(CATEGORY_ICONS)} 個")
        
        return True
    except Exception as e:
        print(f"❌ 成就模型測試失敗: {e}")
        return False

def test_firebase_service():
    """測試Firebase服務"""
    print("\n🔍 測試Firebase服務...")
    
    try:
        from app.services.firebase_service import FirebaseService
        
        firebase_service = FirebaseService()
        print("✅ Firebase服務初始化成功")
        
        # 檢查是否有成就相關方法
        methods_to_check = [
            'get_user_achievements',
            'initialize_user_achievements', 
            'check_and_update_achievement',
            'trigger_achievement_check'
        ]
        
        for method_name in methods_to_check:
            if hasattr(firebase_service, method_name):
                print(f"✅ 方法存在: {method_name}")
            else:
                print(f"❌ 方法缺失: {method_name}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Firebase服務測試失敗: {e}")
        return False

def test_achievement_routes():
    """測試成就路由"""
    print("\n🔍 測試成就路由...")
    
    try:
        from app.routes.achievement import achievement
        
        print("✅ 成就路由模組載入成功")
        
        # 檢查路由是否註冊
        route_rules = [rule for rule in achievement.url_map.iter_rules()]
        print(f"✅ 已註冊路由數量: {len(route_rules)}")
        
        for rule in route_rules:
            print(f"   🔗 {rule.rule} ({rule.endpoint})")
        
        return True
    except Exception as e:
        print(f"❌ 成就路由測試失敗: {e}")
        return False

def test_static_files():
    """測試靜態檔案"""
    print("\n🔍 測試靜態檔案...")
    
    static_files = [
        'app/static/js/achievement/achievement.js',
        'app/static/css/achievement/achievement.css',
        'app/static/js/global-achievement-handler.js'
    ]
    
    all_exist = True
    for file_path in static_files:
        if os.path.exists(file_path):
            print(f"✅ 檔案存在: {file_path}")
        else:
            print(f"❌ 檔案缺失: {file_path}")
            all_exist = False
    
    return all_exist

def test_templates():
    """測試模板檔案"""
    print("\n🔍 測試模板檔案...")
    
    template_files = [
        'app/templates/achievement/achievement.html',
        'app/templates/achievement/summary.html'
    ]
    
    all_exist = True
    for file_path in template_files:
        if os.path.exists(file_path):
            print(f"✅ 模板存在: {file_path}")
        else:
            print(f"❌ 模板缺失: {file_path}")
            all_exist = False
    
    return all_exist

def run_comprehensive_test():
    """運行完整測試"""
    print("🚀 開始成就系統綜合測試...\n")
    
    tests = [
        ("成就模型", test_achievement_models),
        ("Firebase服務", test_firebase_service),
        ("成就路由", test_achievement_routes),
        ("靜態檔案", test_static_files),
        ("模板檔案", test_templates)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 測試結果總結:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！成就系統已準備就緒！")
        return True
    else:
        print("⚠️  部分測試失敗，需要檢查和修復。")
        return False

if __name__ == "__main__":
    run_comprehensive_test()
