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
- 精確顯示使用者當前地理位置並以藍色標記標示
- 在使用者周圍 500 米範圍內根據公車路線隨機生成精靈
- 精靈在地圖上以綠色標記顯示
- 精靈具有存在時間限制，超時會自動消失
- 支援地圖上查看附近公車站點

### 精靈系統
- 多樣化的精靈元素類型（火系、水系、草系、電系、風系、地系等）
- 元素相剋機制（如火克風和地、水克火和電等）
- 不同的稀有度（普通、稀有、史詩、傳說）和力量值
- 精靈等級與經驗值系統
- 專屬於特定公車路線的精靈種類
- 精靈可進行升級、恢復血量等操作

### 站點擂台
- 每個公車站點設有擂台，以地圖標記顯示
- 擂台關聯至特定公車站點位置
- 玩家可以派出精靈守衛擂台成為站主
- 每個擂台由一隻守護精靈保護
- 挑戰其他玩家設立的擂台
- 成功挑戰後可接管擂台成為新站主
- 獲得擂台獎勵和聲望

### PVP 對戰
- 玩家之間的精靈對戰系統
- 屬性相剋機制
- 戰鬥排名和獎勵機制

### 公車路線整合
- 整合貓空左線(動物園)、貓空右線、貓空左線(指南宮)等特定路線
- 顯示公車路線和站點於地圖上
- 各路線專屬精靈種類

### 後台管理功能
- 管理員介面，用於監控和管理遊戲資料
- 使用者權限控制
- 數據統計與分析功能

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
│   ├── data/               # 本地資料存儲
│   │   ├── routes/         # 公車路線資料
│   │   └── stops/          # 公車站點資料
│   ├── models/             # 資料模型
│   │   ├── arena.py        # 擂台模型
│   │   ├── bus.py          # 公車模型
│   │   ├── creature.py     # 精靈模型
│   │   └── user.py         # 使用者模型
│   ├── routes/             # 路由控制器
│   │   ├── admin.py        # 管理員相關路由
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
│   │   ├── admin/          # 管理員頁面
│   │   ├── auth/           # 認證相關頁面
│   │   ├── game/           # 遊戲功能頁面
│   │   │   ├── battle.html # 擂台對戰頁面
│   │   │   └── catch.html  # 捕捉精靈頁面
│   │   └── main/           # 主要頁面
│   └── __init__.py         # 應用程式初始化
├── credentials/            # 憑證文件
├── dataconnect/            # 資料連接設定
├── dataconnect-generated/  # 資料連接生成的檔案
├── extensions/             # 擴展功能目錄
├── functions/              # Firebase 雲函數
├── instance/               # Flask 實例配置
├── public/                 # 公開檔案
├── test/                   # 測試代碼目錄
├── app.py                  # 應用程式入口
├── apphosting.emulator.yaml # Firebase 模擬器配置
├── apphosting.yaml         # Firebase 部署配置
├── config.py               # 配置文件
├── database.rules.json     # Firebase 資料庫規則
├── firebase.json           # Firebase 配置
├── firestore.indexes.json  # Firestore 索引設定
├── firestore.rules         # Firestore 安全規則
├── package.json            # npm 套件依賴
├── remoteconfig.template.json # Firebase 遠端配置
├── requirements.txt        # Python 依賴套件
├── storage.rules           # Firebase 存儲規則
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

### 擂台對戰系統 (`game/battle.html`)
擂台對戰系統透過 Firebase 即時資料庫提供以下功能：

1. **擂台管理**：
   - 顯示地圖上所有擂台位置
   - 每個擂台關聯一個公車站點
   - 站主可設置守護精靈

2. **對戰機制**：
   - 挑戰者可選擇精靈進行對戰
   - 以精靈力量值和屬性相剋進行判定
   - 勝利後可接管擂台成為新站主

### TDX API 整合服務
透過 `tdx_service.py` 實現與台灣運輸資料交換平台 (TDX) 的整合：

1. **路線資料管理**：
   - 自動抓取貓空左右線路線數據
   - 適應性地處理 GeoJSON 格式資料
   - 本地緩存機制降低 API 請求次數

2. **站點資料整合**：
   - 系統性管理公車站點資訊
   - 支援多種路線的站點資料
   - 資料自動更新與過期管理

3. **錯誤處理與重試機制**：
   - 完善的 API 錯誤處理流程
   - 退避式重試減輕 API 負載
   - 本地資料備援確保系統穩定性

## 開發計劃
1. 階段一：基本功能實作 ✓
   - 使用者認證系統
   - 基本前端界面建立
   - 地圖與位置功能整合
   
2. 階段二：精靈系統實作 ✓
   - 精靈生成機制
   - 捕捉功能實現
   - TDX API整合準備
   
3. 階段三：公車整合與擂台系統 ✓
   - TDX 公車 API 整合
   - 使用者位置與公車位置確認
   - 擂台系統建立
   
4. 階段四：PVP功能與進階功能 ✓
   - 玩家對戰系統 ✓
   - 管理員後台功能 ✓
   - 獎勵機制設計 ✓
   
5. 階段五：系統優化與擴展 (進行中)
   - 更多公車路線支持
   - 使用者體驗優化
   - 社群功能整合

## 使用技術
- **前端框架**：Bootstrap 5 響應式佈局
- **地圖技術**：OpenStreetMap + Leaflet.js
- **後端框架**：Flask
- **資料儲存**：Firebase Realtime Database + Firestore
- **使用者認證**：Firebase Authentication
- **API 整合**：TDX 運輸資料 API + Firebase Cloud Functions
- **部署環境**：Firebase Hosting + Cloud Functions
- **版本控制**：Git + GitHub