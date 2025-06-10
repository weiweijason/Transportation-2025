#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('.')

from scripts.creature_generator import load_creatures_csv, map_route_id_to_csv_route

def test_csv_loading():
    """測試CSV讀取功能"""
    print('=== 測試CSV讀取 ===')
    creatures_df = load_creatures_csv()
    
    if creatures_df is not None:
        print(f'成功載入 {len(creatures_df)} 隻精靈')
        print(f'欄位: {list(creatures_df.columns)}')
        print()
        
        print('前3隻精靈數據:')
        print(creatures_df.head(3))
        print()
        
        print('=== 測試路線映射 ===')
        test_routes = ['cat_left', 'cat_right', 'cat_left_zhinan', 'br3', 'new_route']
        for route in test_routes:
            csv_route = map_route_id_to_csv_route(route)
            print(f'{route} -> {csv_route}')
        
        print()
        print('=== 檢查每個路線的精靈數量 ===')
        route_counts = creatures_df['Route'].value_counts()
        print(route_counts)
        
        print()
        print('=== 檢查稀有度分布 ===')
        rarity_counts = creatures_df['Rate'].value_counts()
        print(rarity_counts)
        
        print()
        print('=== 檢查類型分布 ===')
        type_counts = creatures_df['Type'].value_counts()
        print(type_counts)
        
        return creatures_df
    else:
        print('CSV載入失敗')
        return None

def test_creature_generation():
    """測試精靈生成功能"""
    print('\n=== 測試精靈生成功能 ===')
    
    try:
        from app.services.firebase_service import FirebaseService
        from app import create_app
        
        # 創建應用實例
        app = create_app(load_tdx=False)
        
        with app.app_context():
            firebase_service = FirebaseService()
            creatures_df = load_creatures_csv()
            
            if creatures_df is not None:
                # 測試不同路線的生成
                test_routes = [
                    ('cat_left', 'cat_left_route'),
                    ('cat_right', 'cat_right_route'),
                    ('cat_left_zhinan', 'cat_left_zhinan_route'),
                    ('br3', 'br3_route')
                ]
                
                for route_id, csv_route_name in test_routes:
                    print(f'\n--- 測試路線: {route_id} ---')
                    route_creatures = creatures_df[creatures_df['Route'] == csv_route_name]
                    print(f'該路線有 {len(route_creatures)} 隻精靈可生成')
                    
                    if len(route_creatures) > 0:
                        # 模擬生成精靈
                        sample_creature = route_creatures.sample(1).iloc[0]
                        print(f'範例精靈: {sample_creature["C_Name"]} ({sample_creature["EN_Name"]})')
                        print(f'HP範圍: {sample_creature["HP_Min"]} - {sample_creature["HP_Max"]}')
                        print(f'ATK範圍: {sample_creature["ATK_Min"]} - {sample_creature["ATK_Max"]}')
                        print(f'稀有度: {sample_creature["Rate"]}')
                        print(f'類型: {sample_creature["Type"]}')
            
    except Exception as e:
        print(f'測試精靈生成時發生錯誤: {e}')

if __name__ == '__main__':
    creatures_df = test_csv_loading()
    test_creature_generation()
