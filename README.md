# 精靈公車專案

## 專案概述
「精靈公車」是一個結合公共交通與遊戲元素的互動式web應用程式。在大眾運輸過程中增加樂趣，提高民眾搭乘公車的意願。使用者可以在搭乘公車時，透過應用程式捕捉各種與公車路線相對應的精靈，並在公車站點設立擂台，與其他玩家進行對戰。

## 目標用戶
- 每位搭乘公車的乘客
- 喜歡收集遊戲的玩家
- 尋找通勤娛樂的民眾

## 主要功能
- 串接TDX中的公車到站站點資訊
- 使用 OpenStreetMap 顯示當前位置與周圍精靈
- 確認使用者是否真的在公車上
- 提供娛樂性高的公車體驗
- 可以在路上抓取路線特定的精靈
- 每個站點設有站主，可進行PVP對戰功能
- 精靈生成機制（當公車靠近點位500米時生成精靈）
- 實作多種精靈屬性（例如：火系、水系、草系、電系等）
- 每個擂台由一隻精靈守護

## 功能特色

### 捕捉精靈
- 使用 OpenStreetMap 和 Leaflet.js 實現互動地圖
- 精確顯示使用者當前地理位置
- 在使用者周圍 500 米範圍內隨機生成精靈
- 精靈具有不同屬性和稀有度
- 支援地圖上查看附近公車站點

### 精靈系統
- 多樣化的精靈類型（火、水、草、電等屬性）
- 不同的稀有度和力量值
- 專屬於特定公車路線的精靈
- 精靈收集與進化系統

### 站點擂台
- 每個公車站點設有擂台
- 可以派出精靈守衛擂台
- 挑戰其他玩家設立的擂台
- 獲得擂台獎勵和聲望

### PVP 對戰
- 玩家之間的精靈對戰系統
- 屬性相剋機制
- 戰鬥排名和獎勵機制

## 開發環境

### 技術棧
- 後端：Python 3.10+ / Flask 2.3.0+
- 資料庫：Firebase Realtime Database 與 Firestore
- 前端：HTML5, CSS3, JavaScript, Bootstrap 5
- 地圖：OpenStreetMap 與 Leaflet.js
- API整合：TDX運輸資料API
- 地理位置：使用瀏覽器的Geolocation API
- 使用者認證：Firebase Authentication

### 環境設置
1. 安裝Python 3.10以上版本
2. 建立虛擬環境：
   ```
   python -m venv venv
   ```
3. 啟動虛擬環境：
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. 安裝依賴套件：
   ```
   pip install -r requirements.txt
   ```
5. 設置環境變數（TDX API密鑰、Firebase 配置等）
6. 啟動開發伺服器：
   ```
   python app.py
   ```

## 專案結構
```
精靈公車/
├── app/                    # 主應用程式目錄
│   ├── config/             # 配置文件（Firebase 等）
│   ├── models/             # 資料模型
│   │   ├── arena.py        # 擂台模型
│   │   ├── bus.py          # 公車模型
│   │   ├── creature.py     # 精靈模型
│   │   └── user.py         # 使用者模型
│   ├── routes/             # 路由控制器
│   │   ├── auth.py         # 認證相關路由
│   │   ├── game.py         # 遊戲功能路由
│   │   └── main.py         # 主頁相關路由
│   ├── services/           # 服務層
│   │   ├── firebase_service.py  # Firebase 服務
│   │   └── tdx_service.py       # TDX API 服務
│   ├── static/             # 靜態資源
│   │   ├── css/            # CSS樣式
│   │   └── js/             # JavaScript腳本
│   ├── templates/          # HTML模板
│   │   ├── auth/           # 認證相關頁面
│   │   ├── game/           # 遊戲功能頁面
│   │   │   └── catch.html  # 捕捉精靈頁面
│   │   └── main/           # 主要頁面
│   └── __init__.py         # 應用程式初始化
├── credentials/            # 憑證文件
├── app.py                  # 應用程式入口
├── config.py               # 配置文件
├── requirements.txt        # 依賴套件
└── README.md               # 本文件
```

## 關鍵功能說明

### 捕捉精靈頁面 (`game/catch.html`)
捕捉精靈頁面使用 OpenStreetMap 作為基礎地圖，提供以下功能：

1. **互動地圖**：
   - 自動顯示使用者當前位置並以藍色標記標示
   - 顯示使用者周圍 500 米探索範圍
   - 地圖上標記附近公車站和可捕捉的精靈

2. **位置功能**：
   - 自動獲取使用者當前位置座標
   - 支援重新定位功能
   - 完整的錯誤處理機制

3. **精靈探索**：
   - 在使用者周圍隨機生成不同類型的精靈
   - 每個精靈都有特定屬性和稀有度
   - 精靈在地圖上以綠色標記顯示

4. **捕捉機制**：
   - 使用者可以嘗試捕捉發現的精靈
   - 成功/失敗的捕捉機制
   - 成功捕捉後會將精靈加入使用者收藏

## 開發計劃
1. 階段一：基本功能實作 ✓
   - 使用者認證系統
   - 基本前端界面建立
   - 地圖與位置功能整合
   
2. 階段二：精靈系統實作 ✓
   - 精靈生成機制
   - 捕捉功能實現
   - TDX API整合準備
   
3. 階段三：公車整合與擂台系統 (進行中)
   - TDX 公車 API 整合
   - 使用者位置與公車位置確認
   - 擂台系統建立
   
4. 階段四：PVP功能與進階功能 (計劃中)
   - 玩家對戰系統
   - 社群功能整合
   - 獎勵機制設計

## 使用技術
- **前端框架**：Bootstrap 5 響應式佈局
- **地圖技術**：OpenStreetMap + Leaflet.js
- **後端框架**：Flask
- **資料儲存**：Firebase Realtime Database
- **使用者認證**：Firebase Authentication
- **API 整合**：TDX 運輸資料 API