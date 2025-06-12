#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
棕3路線整合測試腳本
測試所有棕3路線相關功能是否正常運作
"""

import sys
import os
sys.path.append('.')

from app import create_app
from app.models.bus import BusRoute
from app.services.tdx_service import TdxService
from scripts.creature_generator import map_route_id_to_csv_route

def test_database_route():
    """測試資料庫中的棕3路線記錄"""
    print("=== 測試資料庫路線記錄 ===")
    
    app = create_app(load_tdx=False)
    with app.app_context():
        brown3_route = BusRoute.query.filter_by(route_id='brown-3').first()
        if brown3_route:
            print(f"✅ 路線ID: {brown3_route.route_id}")
            print(f"✅ 名稱: {brown3_route.name}")
            print(f"✅ 元素類型: {brown3_route.element_type}")
            print(f"✅ 城市: {brown3_route.city}")
            return True
        else:
            print("❌ 棕3路線不存在於資料庫中")
            return False

def test_tdx_service():
    """測試TdxService對棕3路線的支援"""
    print("\n=== 測試TdxService服務 ===")
    
    try:
        tdx = TdxService()
        
        # 測試路線資料
        print("測試獲取路線資料...")
        route_data = tdx.get_route_data('brown-3')
        print(f"✅ 獲取到 {len(route_data)} 個路線座標點")
        
        # 測試站點資料
        print("測試獲取站點資料...")
        stops_data = tdx.get_route_stops('brown-3')
        print(f"✅ 獲取到 {len(stops_data)} 個站點")
        
        return True
    except Exception as e:
        print(f"❌ TdxService測試失敗: {e}")
        return False

def test_creature_generator():
    """測試精靈生成器對棕3路線的支援"""
    print("\n=== 測試精靈生成器 ===")
    
    try:
        # 測試路線映射
        csv_route = map_route_id_to_csv_route('brown-3')
        if csv_route == 'br3_route':
            print(f"✅ 路線映射正確: brown-3 -> {csv_route}")
            return True
        else:
            print(f"❌ 路線映射錯誤: brown-3 -> {csv_route}")
            return False
    except Exception as e:
        print(f"❌ 精靈生成器測試失敗: {e}")
        return False

def test_frontend_configs():
    """測試前端配置檔案"""
    print("\n=== 測試前端配置 ===")
    
    # 檢查config.js是否包含棕3路線配置
    config_file = 'app/static/js/modules/config.js'
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "'brown-3'" in content and "#8B4513" in content:
                print("✅ 前端配置包含棕3路線顏色配置")
                return True
            else:
                print("❌ 前端配置缺少棕3路線配置")
                return False
    except Exception as e:
        print(f"❌ 無法讀取前端配置檔案: {e}")
        return False

def main():
    """執行所有測試"""
    print("🚌 棕3路線整合測試開始\n")
    
    tests = [
        ("資料庫路線記錄", test_database_route),
        ("TdxService服務", test_tdx_service),
        ("精靈生成器", test_creature_generator),
        ("前端配置", test_frontend_configs)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}測試發生異常: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n" + "="*50)
    print("🧪 測試結果總結")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！棕3路線整合完成！")
    else:
        print("⚠️  部分測試失敗，請檢查相關配置")
    
    return passed == total

if __name__ == "__main__":
    main()
