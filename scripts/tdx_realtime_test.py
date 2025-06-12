import requests
import json
import time
import os
from urllib.parse import quote

# TDX 金鑰資訊
TDX_CLIENT_ID = "sssun-09d597db-5ec8-446e"
TDX_CLIENT_SECRET = "8ffe4bd6-dc2e-40e1-8f9e-2c5d62e13ab1"

auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
TDX_API_URL = "https://tdx.transportdata.tw/api/basic"
SAVE_DIR = "app/data/bus"

# 建立資料夾
os.makedirs(SAVE_DIR, exist_ok=True)

# 路線對應表：{路線名稱: 檔名}
ROUTES = {
    "貓空左線(指南宮)": "cat_left_zhinan_bus.json",
    "貓空左線(動物園)": "cat_left_bus.json",
    "貓空右線": "cat_right_bus.json",
    "棕3": "br3_bus.json"
}

class TDXClient:
    def __init__(self, TDX_CLIENT_ID, TDX_CLIENT_SECRET):
        self.app_id = TDX_CLIENT_ID
        self.app_key = TDX_CLIENT_SECRET
        self.access_token = self._get_token()
        self.headers = {
            'authorization': f'Bearer {self.access_token}',
            'Accept-Encoding': 'gzip'
        }

    def _get_token(self):
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.app_id,
            'client_secret': self.app_key
        }
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']

    def get_realtime_data(self, route_name):
        encoded_name = quote(route_name, safe='')
        url = f"{TDX_API_URL}/v2/Bus/RealTimeByFrequency/City/Taipei/{encoded_name}?$format=JSON"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️ 無法取得「{route_name}」的即時資訊: {e}")
            return None

def save_route_data(filename, data):
    filepath = os.path.join(SAVE_DIR, filename)

    result = []
    if data:
        for item in data:
            plate = item.get('PlateNumb')
            pos = item.get('BusPosition', {})
            lon = pos.get('PositionLon')
            lat = pos.get('PositionLat')
            if plate and lon and lat:
                result.append({
                    "PlateNumb": plate,
                    "PositionLon": lon,
                    "PositionLat": lat
                })

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ 已儲存 {filename}，共 {len(result)} 筆資料")

if __name__ == '__main__':
    tdx = TDXClient(TDX_CLIENT_ID, TDX_CLIENT_SECRET)

    while True:
        for route_name, filename in ROUTES.items():
            data = tdx.get_realtime_data(route_name)
            save_route_data(filename, data)
        print("🕒 等待 5 秒...\n")
        time.sleep(5)
