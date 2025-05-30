#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好友申請調試腳本
用於測試和調試好友申請功能
"""

import requests
import json
from flask import Flask
from app import create_app
from app.services.firebase_service import FirebaseService

def test_friend_request_debug():
    """測試好友申請功能並顯示詳細調試信息"""
    
    print("=" * 60)
    print("好友申請調試測試")
    print("=" * 60)
    
    # 初始化 Firebase 服務
    try:
        firebase_service = FirebaseService()
        print("✅ Firebase 服務初始化成功")
    except Exception as e:
        print(f"❌ Firebase 服務初始化失敗: {e}")
        return
    
    # 測試用戶 ID（請替換為實際存在的用戶 ID）
    test_users = [
        "test_user_001",  # 發送申請的用戶
        "test_user_002"   # 接收申請的用戶
    ]
    
    print("\n1. 檢查測試用戶是否存在...")
    for user_id in test_users:
        try:
            user_doc = firebase_service.firestore_db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                print(f"✅ 用戶 {user_id} 存在")
                print(f"   用戶名: {user_data.get('username', '未設置')}")
                print(f"   現有好友: {user_data.get('friends', [])}")
                print(f"   待處理申請: {user_data.get('friends_pending', [])}")
            else:
                print(f"❌ 用戶 {user_id} 不存在，正在創建...")
                # 創建測試用戶
                firebase_service.firestore_db.collection('users').document(user_id).set({
                    'username': f'測試用戶_{user_id[-3:]}',
                    'friends': [],
                    'friends_pending': [],
                    'created_at': firebase_service.firestore_db.SERVER_TIMESTAMP
                })
                print(f"✅ 測試用戶 {user_id} 創建成功")
        except Exception as e:
            print(f"❌ 檢查用戶 {user_id} 時發生錯誤: {e}")
    
    print("\n2. 模擬好友申請流程...")
    sender_id = test_users[0]
    receiver_id = test_users[1]
    
    try:
        # 獲取發送者和接收者的當前資料
        sender_doc = firebase_service.firestore_db.collection('users').document(sender_id).get()
        receiver_doc = firebase_service.firestore_db.collection('users').document(receiver_id).get()
        
        if not sender_doc.exists or not receiver_doc.exists:
            print("❌ 測試用戶資料不完整")
            return
        
        sender_data = sender_doc.to_dict()
        receiver_data = receiver_doc.to_dict()
        
        print(f"發送者 {sender_id} 向接收者 {receiver_id} 發送好友申請...")
        
        # 檢查是否已經是好友
        sender_friends = sender_data.get('friends', [])
        if receiver_id in sender_friends:
            print(f"⚠️ {receiver_id} 已經是 {sender_id} 的好友")
            return
        
        # 檢查是否已經發送過申請
        receiver_pending = receiver_data.get('friends_pending', [])
        if sender_id in receiver_pending:
            print(f"⚠️ {sender_id} 已經向 {receiver_id} 發送過好友申請")
            return
        
        # 執行好友申請
        receiver_pending.append(sender_id)
        firebase_service.firestore_db.collection('users').document(receiver_id).update({
            'friends_pending': receiver_pending
        })
        
        print(f"✅ 好友申請發送成功！")
        print(f"   {receiver_id} 的待處理申請列表: {receiver_pending}")
        
        # 驗證申請是否成功寫入
        updated_receiver_doc = firebase_service.firestore_db.collection('users').document(receiver_id).get()
        if updated_receiver_doc.exists:
            updated_data = updated_receiver_doc.to_dict()
            actual_pending = updated_data.get('friends_pending', [])
            if sender_id in actual_pending:
                print(f"✅ Firebase 寫入驗證成功：申請已記錄在 {receiver_id} 的待處理列表中")
            else:
                print(f"❌ Firebase 寫入驗證失敗：申請未找到在待處理列表中")
        
    except Exception as e:
        print(f"❌ 好友申請過程中發生錯誤: {e}")
    
    print("\n3. 測試完成後的資料狀態...")
    for user_id in test_users:
        try:
            user_doc = firebase_service.firestore_db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                print(f"\n用戶 {user_id}:")
                print(f"  好友列表: {user_data.get('friends', [])}")
                print(f"  待處理申請: {user_data.get('friends_pending', [])}")
        except Exception as e:
            print(f"❌ 獲取用戶 {user_id} 最終狀態時發生錯誤: {e}")

def test_web_interface():
    """測試 Web 介面的好友申請功能"""
    print("\n" + "=" * 60)
    print("Web 介面測試")
    print("=" * 60)
    
    # 創建 Flask 應用實例進行測試
    try:
        app = create_app()
        with app.test_client() as client:
            print("✅ Flask 應用創建成功")
            
            # 測試好友頁面是否可訪問
            print("\n測試好友頁面訪問...")
            # 注意：這需要用戶登錄，實際測試可能需要模擬登錄
            
    except Exception as e:
        print(f"❌ Flask 應用測試失敗: {e}")

if __name__ == "__main__":
    print("開始好友申請調試測試...")
    test_friend_request_debug()
    test_web_interface()
    print("\n調試測試完成！")
