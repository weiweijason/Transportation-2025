import os
import sys
import json
import random
import time
import pandas as pd
from datetime import datetime, timedelta
import threading
import schedule

# 將目前工作目錄加入到 sys.path，以便能夠匯入應用程式模組
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
sys.path.append(app_dir)

from app import create_app, db
from app.services.firebase_service import FirebaseService
from app.models.bus import BusRoute, BusRouteShape

# 創建應用實例
app = create_app(load_tdx=False)

def load_creatures_csv():
    """從CSV文件加載精靈數據"""
    try:
        csv_path = os.path.join(current_dir, 'creatures.csv')
        if not os.path.exists(csv_path):
            print(f"警告: 找不到CSV文件: {csv_path}")
            return None
            
        # 嘗試不同的編碼讀取CSV文件
        encodings = ['utf-8', 'big5', 'gbk', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"成功使用 {encoding} 編碼讀取 {len(df)} 隻精靈的數據")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("嘗試所有編碼都失敗，無法讀取CSV文件")
            return None
        
        # 檢查必要的欄位
        required_columns = ['ID', 'C_Name', 'EN_Name', 'HP_Max', 'HP_Min', 'ATK_Max', 'ATK_Min', 'Rate', 'Type', 'Route', 'Img']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"警告: CSV文件缺少必要欄位: {missing_columns}")
            return None
            
        return df
    except Exception as e:
        print(f"讀取CSV文件失敗: {e}")
        return None

def map_route_id_to_csv_route(route_id):
    """將資料庫路線ID映射到CSV文件中的路線名稱"""
    route_mapping = {
        # 根據現有的路線ID映射到CSV中的Route欄位
        # 注意順序：更具體的匹配要放在前面
        'cat_left_zhinan': 'cat_left_zhinan_route',
        'cat_left': 'cat_left_route',
        'cat_right': 'cat_right_route',
        'br3': 'br3_route',
        'brown-3': 'br3_route',  # 棕3路線映射到br3_route
        # 新的第四條路線
        'new_route': 'NEW'
    }
    
    # 檢查route_id中是否包含映射的關鍵字
    for key, csv_route in route_mapping.items():
        if key in str(route_id).lower():
            return csv_route
    
    # 如果沒有找到匹配，返回None
    print(f"警告: 無法映射路線ID {route_id} 到CSV路線")
    return None

def load_route_geometry(route_id):
    """從本地JSON文件加載路線幾何數據"""
    route_files = {
        'cat_right': 'app/data/routes/cat_right_route.json',
        'cat_left': 'app/data/routes/cat_left_route.json',
        'cat_left_zhinan': 'app/data/routes/cat_left_zhinan_route.json',
        'brown-3': 'app/data/routes/brown_3_route.json'
    }
    
    route_key = None
    if 'cat_right' in route_id:
        route_key = 'cat_right'
    elif 'cat_left_zhinan' in route_id:
        route_key = 'cat_left_zhinan'
    elif 'cat_left' in route_id:
        route_key = 'cat_left'
    elif 'brown-3' in route_id or 'brown_3' in route_id:
        route_key = 'brown-3'
    
    if route_key and route_key in route_files:
        try:
            file_path = os.path.join(app_dir, route_files[route_key])
            print(f"嘗試載入路線檔案: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                route_data = json.load(f)
                
                # 直接返回整個數據，交給 generate_route_creatures 處理
                # 貓空路線使用 data 屬性，包含座標點數組
                if isinstance(route_data, dict) and 'data' in route_data:
                    print(f"找到 {len(route_data['data'])} 個座標點在路線 {route_key} 中")
                    return route_data
                
                # 其他可能的格式
                if isinstance(route_data, list) and len(route_data) > 0:
                    route_item = route_data[0]
                    if 'geometry' in route_item:
                        return route_item['geometry']
                    elif 'Geometry' in route_item:
                        return route_item['Geometry']
                
                # 如果沒有找到標準結構，但數據不為空，直接返回原始數據
                if route_data:
                    print(f"找到非標準格式的路線數據，直接傳遞")
                    return route_data
                    
        except Exception as e:
            print(f"載入路線幾何數據失敗 {file_path}: {e}")
    
    print(f"沒有找到路線 {route_id} 的幾何數據")
    return None

def generate_creatures_for_all_routes():
    """為所有路線生成精靈"""
    print(f"=== 執行精靈生成任務 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 載入精靈CSV數據
    creatures_df = load_creatures_csv()
    if creatures_df is None:
        print("無法載入精靈數據，跳過此次生成")
        return
    
    # 初始化 Firebase 服務
    firebase_service = FirebaseService()
    
    # 獲取所有路線
    routes = BusRoute.query.all()
    print(f"共找到 {len(routes)} 條路線")
    
    # 先清理過期的精靈
    removed_count = firebase_service.remove_expired_creatures()
    if removed_count > 0:
        print(f"已清理 {removed_count} 隻過期的精靈")
    
    # 更新本地緩存
    firebase_service.cache_creatures_to_csv()
    print("已更新精靈緩存")
    
    # 為每條路線生成精靈
    for route in routes:
        # 80% 的機率生成精靈
        if random.random() < 0.8:
            # 將路線ID映射到CSV路線名稱
            csv_route_name = map_route_id_to_csv_route(route.route_id)
            if not csv_route_name:
                print(f"路線 {route.name} ({route.route_id}) 在CSV中找不到對應的精靈，跳過")
                continue
            
            # 嘗試從數據庫獲取路線形狀
            route_shape = BusRouteShape.query.filter_by(route_id=route.id).first()
            geometry = None
            
            # 如果數據庫中有路線形狀數據
            if route_shape and route_shape.geometry:
                try:
                    geometry = json.loads(route_shape.geometry)
                except:
                    print(f"無法解析路線 {route.name} 的幾何數據")
            
            # 如果從數據庫無法獲取，嘗試從本地文件加載
            if not geometry:
                geometry = load_route_geometry(route.route_id)
            
            # 生成精靈
            count = random.randint(1, 2)  # 每次生成1-2隻精靈
            creatures = firebase_service.generate_route_creatures(
                route_id=route.id,
                route_name=route.name,
                element_type=route.element_type,
                route_geometry=geometry,
                count=count,
                creatures_data=creatures_df,  # 傳入CSV數據
                csv_route_name=csv_route_name  # 傳入CSV路線名稱
            )
            
            if creatures:
                print(f"在路線 {route.name} 上生成了 {len(creatures)} 隻精靈")
            else:
                print(f"在路線 {route.name} 上生成精靈失敗")
        else:
            print(f"路線 {route.name} 本次未生成精靈 (20% 機率)")
    
    # 再次更新本地緩存，確保添加了新生成的精靈
    firebase_service.cache_creatures_to_csv()
    
    print(f"=== 精靈生成任務完成 ===\n")

def run_schedule():
    """執行定時任務"""
    # 每分鐘生成精靈
    def job():
        with app.app_context():
            generate_creatures_for_all_routes()
    
    schedule.every(1).minutes.do(job)
    
    # 初次執行
    with app.app_context():
        generate_creatures_for_all_routes()
    
    # 持續運行定時任務
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # 在背景執行定時任務
    scheduler_thread = threading.Thread(target=run_schedule)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    print("精靈生成服務已啟動...")
    
    try:
        # 保持主程序運行
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("服務已停止")