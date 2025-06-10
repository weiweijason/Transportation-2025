# -*- coding: utf-8 -*-
"""
測試分離後的CSV文件路徑配置
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_csv_paths():
    """測試新的CSV文件路徑配置"""
    try:
        from app.services.firebase_service import FirebaseService
        
        print("=== 測試新的CSV文件路徑配置 ===")
        
        # 初始化Firebase服務
        firebase_service = FirebaseService()
        
        # 測試緩存到新路徑
        print("\n1. 測試緩存精靈到新路徑...")
        result = firebase_service.cache_creatures_to_csv()
        
        if result is not None:
            if hasattr(result, 'shape'):
                print(f"✓ 成功緩存 {result.shape[0]} 隻精靈")
                print(f"✓ 欄位: {list(result.columns)}")
            else:
                print(f"✓ 緩存結果: {result}")
        else:
            print("✗ 緩存失敗")
        
        # 檢查文件是否存在於正確位置
        expected_path = os.path.join(
            os.path.dirname(__file__), 
            'app', 'data', 'creatures', 'firebase_cached_creatures.csv'
        )
        
        print(f"\n2. 檢查文件是否存在於: {expected_path}")
        if os.path.exists(expected_path):
            print("✓ 文件存在於正確位置")
            
            # 檢查文件大小
            file_size = os.path.getsize(expected_path)
            print(f"✓ 文件大小: {file_size} bytes")
        else:
            print("✗ 文件不存在於預期位置")
        
        # 測試從新路徑讀取
        print("\n3. 測試從新路徑讀取精靈數據...")
        creatures = firebase_service.get_creatures_from_csv()
        
        if creatures:
            print(f"✓ 成功讀取 {len(creatures)} 隻精靈")
            
            # 顯示第一隻精靈的信息
            if len(creatures) > 0:
                first_creature = creatures[0]
                print(f"✓ 第一隻精靈: {first_creature.get('name', 'Unknown')}")
                print(f"  - Type: {first_creature.get('type', 'N/A')}")
                print(f"  - Rate: {first_creature.get('rate', 'N/A')}")
                print(f"  - HP: {first_creature.get('hp', 'N/A')}")
                print(f"  - Attack: {first_creature.get('attack', 'N/A')}")
        else:
            print("✗ 無法從新路徑讀取精靈數據")
        
        # 檢查目錄結構
        print("\n4. 檢查目錄結構...")
        creatures_dir = os.path.join(os.path.dirname(__file__), 'app', 'data', 'creatures')
        
        if os.path.exists(creatures_dir):
            print(f"✓ creatures 目錄存在: {creatures_dir}")
            
            files = os.listdir(creatures_dir)
            print(f"✓ 目錄內容: {files}")
            
            # 檢查 .gitignore 和 .gitkeep
            gitignore_path = os.path.join(creatures_dir, '.gitignore')
            gitkeep_path = os.path.join(creatures_dir, '.gitkeep')
            
            if os.path.exists(gitignore_path):
                print("✓ .gitignore 文件存在")
            else:
                print("✗ .gitignore 文件不存在")
                
            if os.path.exists(gitkeep_path):
                print("✓ .gitkeep 文件存在")
            else:
                print("✗ .gitkeep 文件不存在")
        else:
            print(f"✗ creatures 目錄不存在: {creatures_dir}")
        
        print("\n=== 測試完成 ===")
        
    except Exception as e:
        print(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_paths()
