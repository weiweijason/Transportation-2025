#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
競技場 API 錯誤診斷工具
"""
import requests
import json

def test_arena_update_routes():
    """測試競技場路線更新 API"""
    
    print("🔍 競技場 API 錯誤診斷")
    print("=" * 40)
    
    # API 端點
    url = "http://127.0.0.1:3001/game/api/arena/update-routes"
    
    # 測試數據
    test_data = {
        "arenaId": "test_arena_1",
        "routeName": "test_route"
    }
    
    print(f"📡 測試 API: {url}")
    print(f"📦 測試數據: {json.dumps(test_data, indent=2)}")
    
    try:
        # 發送 POST 請求
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📊 回應狀態: {response.status_code}")
        print(f"📋 回應標頭: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("\n❌ 500 內部服務器錯誤")
            print("📝 回應內容:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
        
        elif response.status_code == 401:
            print("\n🔐 401 未授權錯誤")
            print("可能原因: 需要登入認證")
            
        elif response.status_code == 200:
            print("\n✅ 200 成功")
            result = response.json()
            print(json.dumps(result, indent=2))
            
        else:
            print(f"\n⚠️  未預期的狀態碼: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 連接錯誤: 服務器可能未運行")
        print("請確認 Flask 應用程式正在 127.0.0.1:3001 運行")
        
    except requests.exceptions.Timeout:
        print("\n⏰ 請求超時")
        
    except Exception as e:
        print(f"\n💥 其他錯誤: {e}")

def check_common_issues():
    """檢查常見問題"""
    
    print("\n🔧 常見問題檢查:")
    
    # 檢查 Flask 應用是否運行
    try:
        health_response = requests.get("http://127.0.0.1:3001/", timeout=5)
        print("✅ Flask 應用程式正在運行")
    except:
        print("❌ Flask 應用程式可能未運行")
        print("   請執行: python run_app.py")
    
    # 檢查路由註冊
    print("\n📋 可能的解決方案:")
    print("1. 檢查 arena_api.py 中的路由是否正確註冊")
    print("2. 確認 FirebaseService 初始化正常")
    print("3. 檢查 Firestore 連接")
    print("4. 驗證用戶認證狀態")
    print("5. 查看服務器控制台日誌")

if __name__ == "__main__":
    test_arena_update_routes()
    check_common_issues()
