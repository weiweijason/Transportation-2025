import os
import sys
import json
import random
import time
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

def load_route_geometry(route_id):
    """從本地JSON文件加載路線幾何數據"""
    route_files = {
        'cat_right': 'app/data/routes/cat_right_route.json',
        'cat_left': 'app/data/routes/cat_left_route.json',
        'cat_left_zhinan': 'app/data/routes/cat_left_zhinan_route.json'
    }
    
    route_key = None
    if 'cat_right' in route_id:
        route_key = 'cat_right'
    elif 'cat_left_zhinan' in route_id:
        route_key = 'cat_left_zhinan'
    elif 'cat_left' in route_id:
        route_key = 'cat_left'
    
    if route_key and route_key in route_files:
        try:
            file_path = os.path.join(app_dir, route_files[route_key])
            with open(file_path, 'r', encoding='utf-8') as f:
                route_data = json.load(f)
                
                # 嘗試解析幾何資訊
                if isinstance(route_data, list) and len(route_data) > 0:
                    route_item = route_data[0]
                    if 'geometry' in route_item:
                        return route_item['geometry']
                    elif 'Geometry' in route_item:
                        return route_item['Geometry']
        except Exception as e:
            print(f"載入路線幾何數據失敗 {file_path}: {e}")
    
    return None

def generate_creatures_for_all_routes():
    """為所有路線生成精靈"""
    print(f"=== 執行精靈生成任務 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 初始化 Firebase 服務
    firebase_service = FirebaseService()
    
    # 獲取所有路線
    routes = BusRoute.query.all()
    print(f"共找到 {len(routes)} 條路線")
    
    # 先清理過期的精靈
    removed_count = firebase_service.remove_expired_creatures()
    if removed_count > 0:
        print(f"已清理 {removed_count} 隻過期的精靈")
    
    # 為每條路線生成精靈
    for route in routes:
        # 80% 的機率生成精靈
        if random.random() < 0.8:
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
                count=count
            )
            
            if creatures:
                print(f"在路線 {route.name} 上生成了 {len(creatures)} 隻精靈")
            else:
                print(f"在路線 {route.name} 上生成精靈失敗")
        else:
            print(f"路線 {route.name} 本次未生成精靈 (20% 機率)")
    
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