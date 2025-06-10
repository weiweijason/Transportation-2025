# -*- coding: utf-8 -*-
"""
測試更新後的CSV緩存功能
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_csv_cache_and_read():
    """測試CSV緩存和讀取功能"""
    try:
        from app.services.firebase_service import FirebaseService
        
        # 初始化Firebase服務
        firebase_service = FirebaseService()
        
        print("=== 測試從Firebase緩存精靈到CSV ===")
        
        # 緩存精靈到CSV
        result = firebase_service.cache_creatures_to_csv()
        print(f"緩存結果: {type(result)}")
        
        if hasattr(result, 'shape'):
            print(f"緩存了 {result.shape[0]} 隻精靈")
            print("欄位:", list(result.columns))
            
            # 顯示前幾筆資料
            print("\n前3筆精靈資料:")
            for i, row in result.head(3).iterrows():
                print(f"  {i+1}. {row['name']} (ID: {row['id']})")
                print(f"     Type: {row['type']}, Rate: {row['rate']}")
                print(f"     HP: {row['hp']}, Attack: {row['attack']}")
        
        print("\n=== 測試從CSV讀取精靈資料 ===")
        
        # 從CSV讀取精靈
        creatures = firebase_service.get_creatures_from_csv()
        
        if creatures:
            print(f"從CSV讀取了 {len(creatures)} 隻精靈")
            
            # 顯示前幾筆資料
            print("\n前3筆精靈資料:")
            for i, creature in enumerate(creatures[:3]):
                print(f"  {i+1}. {creature['name']} (ID: {creature['id']})")
                print(f"     Type: {creature.get('type', 'N/A')}, Rate: {creature.get('rate', 'N/A')}")
                print(f"     HP: {creature['hp']}, Attack: {creature['attack']}")
                print(f"     Position: ({creature['position']['lat']}, {creature['position']['lng']})")
        else:
            print("沒有從CSV讀取到精靈資料")
            
    except Exception as e:
        print(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_cache_and_read()
