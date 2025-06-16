#!/usr/bin/env python3
"""
道館數據同步腳本
將現有的道館數據同步到Firebase中，包含arena_levels.json中的棕3道館數據
"""

import sys
import os
import json

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.firebase_service import FirebaseService
from app.models.arena import FirebaseArena as Arena
import time
from datetime import datetime

def load_arena_levels_data():
    """載入arena_levels.json中的道館數據"""
    arena_levels_file = os.path.join(project_root, 'app', 'data', 'arenas', 'arena_levels.json')
    
    if not os.path.exists(arena_levels_file):
        print(f"警告：arena_levels.json 文件不存在於 {arena_levels_file}")
        return {}
    
    try:
        with open(arena_levels_file, 'r', encoding='utf-8') as f:
            arena_data = json.load(f)
        
        print(f"✅ 成功載入 arena_levels.json，包含 {len(arena_data)} 個道館")
        
        # 統計各路線道館數量
        route_stats = {}
        for arena_id, arena in arena_data.items():
            routes = arena.get('routes', [])
            for route in routes:
                route_stats[route] = route_stats.get(route, 0) + 1
        
        print("道館路線分布：")
        for route, count in route_stats.items():
            print(f"  {route}: {count} 個道館")
        
        return arena_data
    
    except Exception as e:
        print(f"載入 arena_levels.json 失敗: {e}")
        return {}

def sync_arenas_to_firebase():
    """同步道館數據到Firebase"""
    print("開始同步道館數據到Firebase...")
    
    try:
        firebase_service = FirebaseService()
        
        # 載入arena_levels.json數據
        arena_levels_data = load_arena_levels_data()
        
        # 獲取所有現有道館（從舊模型）
        try:
            old_arenas = Arena.get_all()
            print(f"找到 {len(old_arenas)} 個舊模型道館")
        except:
            old_arenas = []
            print("無法載入舊模型道館，跳過")
        
        # 合併數據源
        all_arenas = []
        
        # 添加arena_levels.json中的數據
        for arena_id, arena_data in arena_levels_data.items():
            all_arenas.append(arena_data)
        
        # 添加舊模型中的數據（如果不重複）
        existing_ids = set(arena_levels_data.keys())
        for old_arena in old_arenas:
            old_arena_dict = old_arena.to_dict()
            arena_id = old_arena_dict.get('id')
            if arena_id and arena_id not in existing_ids:
                all_arenas.append(old_arena_dict)
        
        print(f"總共需要同步 {len(all_arenas)} 個道館")
        
        synced_count = 0
        error_count = 0
        brown3_count = 0
        
        for arena_data in all_arenas:
            try:
                arena_id = arena_data.get('id')
                if not arena_id:
                    arena_id = f"arena-{int(time.time())}"
                
                # 檢查Firebase中是否已存在
                arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_id)
                existing_doc = arena_ref.get()
                
                # 準備同步數據，適配新的字段結構
                sync_data = {
                    'id': arena_id,
                    'name': arena_data.get('name', '未知道館'),
                    'level': determine_arena_level(arena_data),
                    'owner': arena_data.get('owner'),
                    'owner_player_id': arena_data.get('owner_player_id') or arena_data.get('ownerPlayerId'),
                    'owner_creature': arena_data.get('owner_creature') or arena_data.get('ownerCreature'),
                    'position': arena_data.get('position'),
                    'stop_ids': arena_data.get('stopIds') or arena_data.get('stop_ids', []),
                    'routes': arena_data.get('routes', []),
                    'stop_name': arena_data.get('stopName'),
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'total_battles': arena_data.get('total_battles', 0),
                    'rewards': {
                        'last_collected': None,
                        'accumulated_hours': 0,
                        'available_rewards': []
                    }
                }
                
                # 如果有佔領者，設置佔領時間
                if sync_data['owner']:
                    sync_data['occupied_at'] = datetime.now().isoformat()
                    sync_data['rewards']['last_collected'] = datetime.now().isoformat()
                
                # 統計棕3道館
                routes = sync_data.get('routes', [])
                if '棕3' in routes:
                    brown3_count += 1
                
                if existing_doc.exists:
                    # 更新現有道館，保留某些字段
                    existing_data = existing_doc.to_dict()
                    sync_data['created_at'] = existing_data.get('created_at', sync_data['created_at'])
                    sync_data['total_battles'] = existing_data.get('total_battles', 0)
                    if existing_data.get('occupied_at'):
                        sync_data['occupied_at'] = existing_data['occupied_at']
                    if existing_data.get('rewards'):
                        sync_data['rewards'] = existing_data['rewards']
                    
                    arena_ref.update(sync_data)
                    print(f"更新道館: {sync_data['name']} (ID: {arena_id})")
                else:
                    # 創建新道館
                    arena_ref.set(sync_data)
                    print(f"創建道館: {sync_data['name']} (ID: {arena_id})")
                
                synced_count += 1
                
            except Exception as e:
                print(f"同步道館失敗 {arena_data.get('name', '未知')}: {e}")
                error_count += 1
                continue
        
        print(f"\n同步完成！")
        print(f"成功同步: {synced_count} 個道館")
        print(f"失敗: {error_count} 個道館")
        print(f"棕3道館: {brown3_count} 個")
        
        # 創建一些測試道館
        create_test_arenas(firebase_service)
        
        # 驗證同步結果
        verify_firebase_sync(firebase_service)
        
    except Exception as e:
        print(f"同步過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

def verify_firebase_sync(firebase_service):
    """驗證Firebase同步結果"""
    print("\n📊 驗證Firebase同步結果...")
    
    try:
        # 獲取所有道館
        arenas_ref = firebase_service.firestore_db.collection('arenas')
        arenas_docs = arenas_ref.get()
        
        total_arenas = len(arenas_docs)
        route_stats = {}
        
        for doc in arenas_docs:
            arena_data = doc.to_dict()
            routes = arena_data.get('routes', [])
            for route in routes:
                route_stats[route] = route_stats.get(route, 0) + 1
        
        print(f"📈 Firebase中的道館統計:")
        print(f"   總道館數: {total_arenas}")
        print(f"   路線分布:")
        for route, count in sorted(route_stats.items()):
            print(f"     {route}: {count} 個道館")
        
        # 特別檢查棕3道館
        brown3_count = route_stats.get('棕3', 0)
        if brown3_count > 0:
            print(f"✅ 棕3道館同步成功: {brown3_count} 個")
        else:
            print("❌ 未找到棕3道館")
        
        return True
        
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {e}")
        return False

def determine_arena_level(arena_data):
    """根據道館數據確定等級"""
    # 如果已經有level字段，直接使用
    if 'level' in arena_data:
        return arena_data['level']
    
    name = arena_data.get('name', '').lower()
    routes = arena_data.get('routes', [])
    
    # 根據路線確定等級
    if '棕3' in routes:
        return 3  # 棕3路線設為3級道館
    elif '貓空右線' in routes or '貓空左線' in routes:
        return 2  # 貓空路線設為2級道館
    elif 'level_1' in name or 'lv1' in name or '等級1' in name:
        return 1
    elif 'level_2' in name or 'lv2' in name or '等級2' in name:
        return 2
    elif 'level_3' in name or 'lv3' in name or '等級3' in name:
        return 3
    elif 'level_4' in name or 'lv4' in name or '等級4' in name:
        return 4
    elif 'level_5' in name or 'lv5' in name or '等級5' in name:
        return 5
    else:
        # 預設等級
        return 1

def create_test_arenas(firebase_service):
    """創建一些測試道館"""
    print("\n創建測試道館...")
    
    test_arenas = [
        {
            'id': 'arena-level-1-001',
            'name': '新手道館',
            'level': 1,
            'owner': None,
            'owner_player_id': None,
            'owner_creature': None,
            'position': {'lat': 25.0, 'lng': 121.5},
            'stop_ids': ['test_stop_001'],
            'routes': ['cat_right'],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'total_battles': 0,
            'rewards': {
                'last_collected': None,
                'accumulated_hours': 0,
                'available_rewards': []
            }
        },
        {
            'id': 'arena-level-2-001',
            'name': '進階道館',
            'level': 2,
            'owner': None,
            'owner_player_id': None,
            'owner_creature': None,
            'position': {'lat': 25.01, 'lng': 121.51},
            'stop_ids': ['test_stop_002'],
            'routes': ['cat_left'],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'total_battles': 0,
            'rewards': {
                'last_collected': None,
                'accumulated_hours': 0,
                'available_rewards': []
            }
        },
        {
            'id': 'arena-level-3-001',
            'name': '高級道館',
            'level': 3,
            'owner': None,
            'owner_player_id': None,
            'owner_creature': None,
            'position': {'lat': 25.02, 'lng': 121.52},
            'stop_ids': ['test_stop_003'],
            'routes': ['brown_3'],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'total_battles': 0,
            'rewards': {
                'last_collected': None,
                'accumulated_hours': 0,
                'available_rewards': []
            }
        }
    ]
    
    for arena_data in test_arenas:
        try:
            arena_ref = firebase_service.firestore_db.collection('arenas').document(arena_data['id'])
            existing_doc = arena_ref.get()
            
            if not existing_doc.exists:
                arena_ref.set(arena_data)
                print(f"創建測試道館: {arena_data['name']} (等級 {arena_data['level']})")
            else:
                print(f"測試道館已存在: {arena_data['name']}")
                
        except Exception as e:
            print(f"創建測試道館失敗 {arena_data['name']}: {e}")

if __name__ == "__main__":
    sync_arenas_to_firebase()
