#!/usr/bin/env python3
"""
測試棕3路線API
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.tdx_service import get_brown_3_route, get_brown_3_stops

def test_brown3_apis():
    print("=== 測試棕3路線API ===")
    
    print("1. 測試棕3路線資料...")
    try:
        route_data = get_brown_3_route()
        print(f"路線資料長度: {len(route_data) if route_data else 0}")
        if route_data and len(route_data) > 0:
            print(f"前3個路線點: {route_data[:3]}")
        else:
            print("❌ 無路線資料")
    except Exception as e:
        print(f"❌ 獲取路線資料失敗: {e}")
    
    print("\n2. 測試棕3站點資料...")
    try:
        stops_data = get_brown_3_stops()
        print(f"站點資料長度: {len(stops_data) if stops_data else 0}")
        if stops_data and len(stops_data) > 0:
            print("前3個站點名稱:")
            for i, stop in enumerate(stops_data[:3]):
                stop_name = stop.get("StopName", {})
                if isinstance(stop_name, dict):
                    name = stop_name.get("Zh_tw", "未知")
                else:
                    name = str(stop_name)
                print(f"  {i+1}. {name}")
        else:
            print("❌ 無站點資料")
    except Exception as e:
        print(f"❌ 獲取站點資料失敗: {e}")

if __name__ == "__main__":
    test_brown3_apis()
