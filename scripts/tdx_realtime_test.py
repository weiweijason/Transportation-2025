import requests
import json
from urllib.parse import quote

# 請填入你註冊 TDX 後獲得的
TDX_CLIENT_ID = "sssun-09d597db-5ec8-446e"
TDX_CLIENT_SECRET= "8ffe4bd6-dc2e-40e1-8f9e-2c5d62e13ab1"

auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
TDX_API_URL = "https://tdx.transportdata.tw/api/basic"

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

    def _get_realtime_by_left(self):
        url = f"{TDX_API_URL}/v2/Bus/RealTimeByFrequency/City/Taipei/貓空左線(動物園)?$format=JSON"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"取得貓空左線(動物園) 即時資訊失敗: {e}")
            return None

    def _get_realtime_by_br3(self):
        url = f"{TDX_API_URL}/v2/Bus/RealTimeByFrequency/City/Taipei/棕3?$format=JSON"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"取得即時資訊失敗: {e}")
            return None
    
    def _get_realtime_by_left_zhinan(self):
        url = f"{TDX_API_URL}/v2/Bus/RealTimeByFrequency/City/Taipei/貓空左線(指南宮)?$format=JSON"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"取得即時資訊失敗: {e}")
            return None
    
    def _get_realtime_by_right(self):
        url = f"{TDX_API_URL}/v2/Bus/RealTimeByFrequency/City/Taipei/貓空右線?$format=JSON"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"取得即時資訊失敗: {e}")
            return None

# 測試
if __name__ == '__main__':
    tdx = TDXClient(TDX_CLIENT_ID, TDX_CLIENT_SECRET)
    data = tdx._get_realtime_by_br3()
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
        #print(f"原始資料共有 {len(data)} 筆，符合條件的有 {len(result)} 筆")//確認有沒有不見
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("查無資料或發生錯誤")
