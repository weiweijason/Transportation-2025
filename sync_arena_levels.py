#!/usr/bin/env python3
"""
同步道館等級腳本 - 確保 Firebase 中的道館等級與路線數量一致
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService
from app.models.arena import FirebaseArena
import traceback

def sync_arena_levels():
    """同步所有道館的等級"""
    try:
        print("🔄 開始同步道館等級...")
        
        firebase_service = FirebaseService()
        
        # 獲取所有道館
        arenas_ref = firebase_service.firestore_db.collection('arenas')
        arenas = arenas_ref.get()
        
        if not arenas:
            print("❌ 沒有找到任何道館")
            return
        
        updated_count = 0
        error_count = 0
        
        print(f"📋 找到 {len(arenas)} 個道館，開始檢查等級...")
        
        for arena_doc in arenas:
            try:
                arena_data = arena_doc.to_dict()
                arena_id = arena_doc.id
                arena_name = arena_data.get('name', '未知道館')
                
                # 獲取路線列表
                routes = arena_data.get('routes', [])
                current_level = arena_data.get('level', 1)
                
                # 計算正確的等級
                correct_level = len(routes) if routes else 1
                
                print(f"  📍 {arena_name}")
                print(f"     路線: {routes}")
                print(f"     當前等級: {current_level}")
                print(f"     正確等級: {correct_level}")
                
                # 如果等級不正確，更新它
                if current_level != correct_level:
                    print(f"     🔧 需要更新等級: {current_level} → {correct_level}")
                    
                    # 更新 Firestore
                    arena_doc.reference.update({
                        'level': correct_level,
                        'updatedAt': firebase_service.get_server_timestamp()
                    })
                    
                    updated_count += 1
                    print(f"     ✅ 等級已更新")
                else:
                    print(f"     ✅ 等級正確，無需更新")
                
                print()
                
            except Exception as e:
                error_count += 1
                print(f"     ❌ 處理道館時出錯: {e}")
                print()
        
        print("=" * 50)
        print(f"📊 同步完成統計:")
        print(f"   總道館數: {len(arenas)}")
        print(f"   已更新: {updated_count}")
        print(f"   錯誤: {error_count}")
        print(f"   無需更新: {len(arenas) - updated_count - error_count}")
        
        if updated_count > 0:
            print(f"✅ 成功更新了 {updated_count} 個道館的等級！")
        else:
            print("✅ 所有道館等級都是正確的！")
            
    except Exception as e:
        print(f"❌ 同步道館等級時出錯: {e}")
        traceback.print_exc()

def check_specific_arena(arena_name):
    """檢查特定道館的等級"""
    try:
        print(f"🔍 檢查道館: {arena_name}")
        
        firebase_service = FirebaseService()
        
        # 查詢道館
        arenas_ref = firebase_service.firestore_db.collection('arenas')
        query = arenas_ref.where('name', '==', arena_name).limit(1)
        docs = query.get()
        
        if not docs:
            print(f"❌ 找不到道館: {arena_name}")
            return
        
        arena_doc = docs[0]
        arena_data = arena_doc.to_dict()
        
        routes = arena_data.get('routes', [])
        current_level = arena_data.get('level', 1)
        correct_level = len(routes) if routes else 1
        
        print(f"📋 道館資訊:")
        print(f"   名稱: {arena_name}")
        print(f"   ID: {arena_doc.id}")
        print(f"   路線: {routes}")
        print(f"   路線數量: {len(routes)}")
        print(f"   當前等級: {current_level}")
        print(f"   正確等級: {correct_level}")
        
        if current_level != correct_level:
            print(f"⚠️ 等級不正確！需要從 {current_level} 更新為 {correct_level}")
            
            # 詢問是否要更新
            update = input("是否要更新這個道館的等級？(y/n): ").lower().strip()
            if update == 'y':
                arena_doc.reference.update({
                    'level': correct_level,
                    'updatedAt': firebase_service.get_server_timestamp()
                })
                print("✅ 等級已更新！")
            else:
                print("⏭️ 跳過更新")
        else:
            print("✅ 等級正確！")
            
    except Exception as e:
        print(f"❌ 檢查道館時出錯: {e}")
        traceback.print_exc()

def main():
    print("🏟️ 道館等級同步工具")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        # 檢查特定道館
        arena_name = sys.argv[1]
        check_specific_arena(arena_name)
    else:
        # 同步所有道館
        confirm = input("是否要同步所有道館的等級？這將檢查並更新 Firebase 中的資料。(y/n): ").lower().strip()
        if confirm == 'y':
            sync_arena_levels()
        else:
            print("❌ 操作已取消")

if __name__ == "__main__":
    main()
