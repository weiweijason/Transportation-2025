#!/usr/bin/env python3
"""
測試基地道館後端 API
"""
import requests
import json

def test_base_gym_api():
    """測試基地道館設定 API"""
    print(">>> 測試基地道館後端 API")
    
    # 測試數據
    test_data = {
        "gym_id": "tutorial-gym-1",
        "gym_name": "中正紀念堂基地道館",
        "gym_level": 5,
        "lat": 25.03556,
        "lng": 121.51972,
        "guardian_creature": {
            "id": "starter_creature",
            "name": "初始精靈",
            "image": "/static/images/creatures/default.png",
            "type": "water",
            "power": 50
        }
    }
    
    try:
        # 發送 POST 請求
        url = "http://localhost:3001/auth/tutorial/set-base-gym"
        headers = {'Content-Type': 'application/json'}
        
        print(f">>> 發送請求到: {url}")
        print(f">>> 請求數據: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f">>> 回應狀態碼: {response.status_code}")
        print(f">>> 回應內容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 測試成功!")
            print(f"   成功狀態: {data.get('success')}")
            print(f"   訊息: {data.get('message')}")
        else:
            print(f"❌ API 測試失敗，狀態碼: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器，請確認 Flask 應用程序正在運行")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_base_gym_api()
