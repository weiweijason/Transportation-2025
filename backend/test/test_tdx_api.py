# https://tdx.transportdata.tw/api/basic/V3/Map/Bus/Network/StopOfRoute/City/Taipei/RouteName/%E8%B2%93%E7%A9%BA%E5%8F%B3%E7%B7%9A?%24top=3&%24format=JSON
import requests
from pprint import pprint
import json

app_id = '111703037-06c51236-f14e-4c23'
app_key = 'b8fa4a43-b315-4407-aa12-5a4a3bb2b753'

auth_url="https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
url = "https://tdx.transportdata.tw/api/basic/V3/Map/Bus/Network/StopOfRoute/City/Taipei/RouteName/%E8%B2%93%E7%A9%BA%E5%8F%B3%E7%B7%9A?%24format=GEOJSON"

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'

        return{
            'content-type' : content_type,
            'grant_type' : grant_type,
            'client_id' : self.app_id,
            'client_secret' : self.app_key
        }

class data():

    def __init__(self, app_id, app_key, auth_response):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_response = auth_response

    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')

        return{
            'authorization': 'Bearer ' + access_token,
            'Accept-Encoding': 'gzip'
        }

if __name__ == '__main__':
    try:
        d = data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    except:
        a = Auth(app_id, app_key)
        auth_response = requests.post(auth_url, a.get_auth_header())
        d = data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    print(auth_response)
    pprint(auth_response.text)
    print(data_response)
    pprint(data_response.text)