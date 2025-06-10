#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的CSV測試腳本，避免Flask Blueprint衝突
"""

import os
import sys
import pandas as pd

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(current_dir, 'scripts')
sys.path.append(current_dir)
sys.path.append(scripts_dir)

def load_creatures_csv():
    """從CSV文件加載精靈數據"""
    try:
        csv_path = os.path.join(scripts_dir, 'creatures.csv')
        if not os.path.exists(csv_path):
            print(f"警告: 找不到CSV文件: {csv_path}")
            return None
            
        # 嘗試不同的編碼讀取CSV文件
        encodings = ['utf-8', 'big5', 'gbk', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"成功使用 {encoding} 編碼讀取 {len(df)} 隻精靈的數據")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"使用 {encoding} 編碼讀取失敗: {e}")
                continue
        
        if df is None:
            print("嘗試所有編碼都失敗，無法讀取CSV文件")
            return None
        
        # 檢查必要的欄位
        required_columns = ['ID', 'C_Name', 'EN_Name', 'HP_Max', 'HP_Min', 'ATK_Max', 'ATK_Min', 'Rate', 'Type', 'Route', 'Img']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"警告: CSV文件缺少必要欄位: {missing_columns}")
            return None
            
        return df
    except Exception as e:
        print(f"讀取CSV文件失敗: {e}")
        return None

def map_route_id_to_csv_route(route_id):
    """將資料庫路線ID映射到CSV文件中的路線名稱"""
    route_mapping = {
        'cat_left': 'cat_left_route',
        'cat_right': 'cat_right_route',
        'cat_left_zhinan': 'cat_left_zhinan_route',
        'br3': 'br3_route',
        'new_route': 'NEW'
    }
    
    # 檢查route_id中是否包含映射的關鍵字
    for key, csv_route in route_mapping.items():
        if key in str(route_id).lower():
            return csv_route
    
    # 如果沒有找到匹配，返回None
    print(f"警告: 無法映射路線ID {route_id} 到CSV路線")
    return None

def test_csv_loading():
    """測試CSV讀取功能"""
    print("=== 測試CSV讀取 ===")
    
    df = load_creatures_csv()
    if df is not None:
        print(f"CSV載入成功！共有 {len(df)} 隻精靈")
        print(f"欄位: {list(df.columns)}")
        print("\n前5筆資料:")
        print(df.head())
        
        # 檢查各路線的精靈數量
        print("\n各路線精靈數量:")
        route_counts = df['Route'].value_counts()
        for route, count in route_counts.items():
            print(f"  {route}: {count} 隻")
        
        # 檢查稀有度分佈
        print("\n稀有度分佈:")
        rarity_counts = df['Rate'].value_counts()
        for rarity, count in rarity_counts.items():
            print(f"  {rarity}: {count} 隻")
            
        # 檢查屬性分佈
        print("\n屬性分佈:")
        type_counts = df['Type'].value_counts()
        for type_name, count in type_counts.items():
            print(f"  {type_name}: {count} 隻")
        
        return True
    else:
        print("CSV載入失敗")
        return False

def test_route_mapping():
    """測試路線映射功能"""
    print("\n=== 測試路線映射 ===")
    
    test_routes = [
        'cat_left_route',
        'cat_right_route', 
        'cat_left_zhinan_route',
        'br3_route',
        'new_route',
        'unknown_route'
    ]
    
    for route_id in test_routes:
        csv_route = map_route_id_to_csv_route(route_id)
        print(f"路線ID: {route_id} -> CSV路線: {csv_route}")

def test_creature_filtering():
    """測試精靈過濾功能"""
    print("\n=== 測試精靈過濾 ===")
    
    df = load_creatures_csv()
    if df is None:
        print("無法載入CSV，跳過過濾測試")
        return
    
    # 測試按路線過濾
    test_routes = ['cat_left_route', 'cat_right_route', 'cat_left_zhinan_route', 'br3_route']
    
    for route in test_routes:
        filtered_df = df[df['Route'] == route]
        print(f"\n路線 {route} 的精靈:")
        if len(filtered_df) > 0:
            for _, creature in filtered_df.iterrows():
                print(f"  - {creature['C_Name']} ({creature['EN_Name']})")
                print(f"    HP: {creature['HP_Min']}-{creature['HP_Max']}, ATK: {creature['ATK_Min']}-{creature['ATK_Max']}")
                print(f"    稀有度: {creature['Rate']}, 屬性: {creature['Type']}")
        else:
            print(f"  沒有找到精靈")

if __name__ == "__main__":
    print("開始測試CSV整合功能...")
    
    # 測試CSV讀取
    csv_success = test_csv_loading()
    
    if csv_success:
        # 測試路線映射
        test_route_mapping()
        
        # 測試精靈過濾
        test_creature_filtering()
        
        print("\n=== 測試完成 ===")
        print("CSV整合功能測試成功！")
    else:
        print("\n=== 測試失敗 ===")
        print("CSV載入失敗，請檢查文件編碼或格式")
