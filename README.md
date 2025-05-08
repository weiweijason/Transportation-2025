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

### 站點擂台系統
- 每個公車站點設有擂台，以地圖標記顯示
- 擂台關聯至特定公車站點位置
- 玩家可以派出精靈守衛擂台成為站主
- 每個擂台由一隻守護精靈保護
- 擂台有不同等級(1-5級)，根據經過的路線數量決定
  - 等級1: 基礎道館，僅經過一條路線
  - 等級2: 中級道館，經過兩條路線
  - 等級3: 高級道館，經過三條路線
  - 等級4及5: 特級道館，經過更多路線或特殊站點
- 不同等級的擂台有不同外觀與背景顏色：
  - 等級1: 綠色背景
  - 等級2: 橙色背景
  - 等級3: 紫色背景
  - 等級4: 粉紅色背景
  - 等級5: 紅色背景
- 挑戰其他玩家設立的擂台
- 成功挑戰後可接管擂台成為新站主
- 獲得擂台獎勵和聲望
- 當找不到道館時會顯示404錯誤頁面，而不會自動創建道館

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
- 資料庫：Firebase Realtime Database 與 Firestore + SQLite/SQLAlchemy
- 前端：HTML5, CSS3, JavaScript, Bootstrap 5
- 地圖：OpenStreetMap 與 Leaflet.js
- API整合：TDX運輸資料API
- 地理位置：使用瀏覽器的Geolocation API
- 使用者認證：Firebase Authentication + Flask-Login

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
5. 設置環境變數（在 .env 檔或系統環境變數）：
   ```
   SECRET_KEY=your_secret_key
   TDX_CLIENT_ID=your_tdx_client_id
   TDX_CLIENT_SECRET=your_tdx_client_secret
   FLASK_CONFIG=development  # 或 production, testing
   ```
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
│   │   ├── game/           # 遊戲功能模組化路由
│   │   │   ├── __init__.py # 遊戲藍圖整合
│   │   │   ├── auth.py     # 認證裝飾器
│   │   │   ├── views.py    # 頁面路由
│   │   │   ├── creature_api.py    # 精靈API
│   │   │   ├── bus_api.py         # 公車API
│   │   │   ├── arena_api.py       # 擂台API
│   │   │   ├── route_creatures_api.py # 路線精靈API
│   │   │   └── user_api.py        # 用戶API
│   │   └── main.py         # 主頁相關路由
│   ├── services/           # 服務層
│   │   ├── firebase_service.py  # Firebase 服務
│   │   └── tdx_service.py       # TDX API 服務
│   ├── static/             # 靜態資源
│   │   ├── css/            # CSS樣式
│   │   │   └── game/       # 遊戲相關樣式
│   │   │       └── catch-game.css  # 捕捉遊戲頁面樣式
│   │   └── js/             # JavaScript腳本
│   │       ├── admin/      # 管理員相關腳本
│   │       ├── game/       # 遊戲相關模組化腳本
│   │       │   ├── catch-game.js      # 捕捉遊戲主要邏輯
│   │       │   ├── map-functions.js   # 地圖相關功能
│   │       │   ├── creature-functions.js # 精靈相關功能
│   │       │   ├── arena-functions.js # 擂台相關功能
│   │       │   └── ui-effects.js      # UI特效與動畫
│   │       └── modules/    # 共用模組
│   ├── templates/          # HTML模板
│   │   ├── admin/          # 管理員頁面
│   │   ├── auth/           # 認證相關頁面
│   │   ├── game/           # 遊戲功能頁面
│   │   │   ├── battle.html # 擂台對戰頁面
│   │   │   └── catch.html  # 捕捉精靈頁面
│   └── main/               # 主要頁面
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

### 應用初始化與配置
應用在啟動時會執行以下操作：
1. 載入環境變數配置
2. 初始化Flask應用和擴展（SQLAlchemy, Flask-Login）
3. 預載TDX公車資料（在後台線程進行，避免阻塞應用啟動）
4. 設置會話管理（7天有效期）
5. 實現自動重定向，未登入用戶訪問非認證頁面時重定向至登入頁面

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

### 前端模組化架構
本專案採用模組化的前端結構，將複雜的JavaScript和CSS代碼拆分為功能性模組：

1. **CSS 模組化**：
   - 將頁面樣式從HTML中分離，移至專用CSS文件
   - 按功能區塊組織樣式代碼，提高可讀性
   - 使用CSS變數統一管理主題色彩和常用樣式
   - 實現響應式設計，適配不同設備尺寸

2. **JavaScript 功能模組**：
   - 遵循關注點分離原則，按功能拆分成多個獨立文件
   - `catch-game.js` - 遊戲核心邏輯與初始化
   - `map-functions.js` - 地圖渲染與定位功能
   - `creature-functions.js` - 精靈生成與互動功能
   - `arena-functions.js` - 擂台相關功能
   - `ui-effects.js` - 視覺特效與動畫

3. **模組化優勢**：
   - 提高代碼可維護性和可讀性
   - 更容易除錯和追蹤問題
   - 支持團隊協作開發
   - 更好的瀏覽器緩存管理
   - 便於擴展功能

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
擂台對戰系統透過資料庫提供以下功能：

1. **擂台管理**：
   - 顯示地圖上所有擂台位置
   - 每個擂台關聯一個公車站點
   - 站主可設置守護精靈

2. **對戰機制**：
   - 挑戰者可選擇精靈進行對戰
   - 以精靈力量值和屬性相剋進行判定
   - 勝利後可接管擂台成為新站主

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
   - 前端代碼模組化重構 ✓
   - 更多公車路線支持
   - 使用者體驗優化
   - 社群功能整合

## 最新進度更新 (2025年5月1日)

### 代碼架構改進
1. **後端代碼模組化重構**:
   - 將單一的 `game.py` 文件拆分為多個功能模組，提高可維護性
   - 建立了 `app/routes/game/` 子包，包含多個功能專一的模組
   - 實現關注點分離，每個功能區域有專屬的程式碼檔案

2. **模組化後的文件結構**:
   - `app/routes/game/__init__.py` - 整合所有遊戲模組的藍圖
   - `app/routes/game/auth.py` - 認證裝飾器與相關功能
   - `app/routes/game/views.py` - 基本頁面路由
   - `app/routes/game/creature_api.py` - 精靈捕捉 API
   - `app/routes/game/bus_api.py` - 公車路線 API
   - `app/routes/game/arena_api.py` - 擂台相關 API
   - `app/routes/game/route_creatures_api.py` - 路線精靈 API
   - `app/routes/game/user_api.py` - 用戶相關 API

3. **前後端一致性優化**:
   - 保持 API 路徑結構一致性，確保前端請求正確
   - 所有 API 遵循 `/game/api/...` 路徑格式

### 新增功能
1. **個人化地圖體驗**:
   - 實現了針對每位使用者過濾已捕獲精靈的功能
   - 使用者地圖上只會顯示尚未捕獲的精靈，提升多人遊戲體驗
   - 優化CSV讀取邏輯，根據使用者背包中的`original_creature_id`過濾顯示精靈

2. **互動式捕捉體驗**:
   - 全新互動式捕捉頁面 (`game/capture_interactive.html`)，提升捕捉體驗
   - 新增魔法陣特效和粒子動畫系統
   - 精靈捕捉過程有動態視覺反饋

3. **前端架構優化**:
   - 完成前端 CSS 模組化重構
   - 建立獨立的捕捉互動樣式表 (`css/game/capture_interactive.css`)
   - 改進主題切換系統，支援深色/淺色模式，且記住使用者偏好設定

4. **UI/UX 改進**:
   - 優化精靈資訊卡片排版
   - 改進按鈕位置與互動體驗
   - 提升移動設備上的操作體驗

## 最新進度更新 (2025年5月7日)

### 個人資料頁面改進與Firebase整合
1. **Firebase後端整合**:
   - 完成個人資料頁面與Firebase後端的整合
   - 從Firebase Firestore動態讀取使用者資料，包括等級、經驗值和戰鬥統計
   - 即時顯示使用者已捕獲的精靈數量和擁有的擂台
   - 實現使用者資料同步更新

2. **用戶模型擴展**:
   - 擴展`FirebaseUser`和`User`模型，新增`fight_count`(戰鬥總數)屬性
   - 增加`arenas`集合，追蹤使用者佔領的擂台
   - 實現`user_creatures`子集合數量統計，顯示在個人資料頁面

3. **前端JavaScript模組化**:
   - 將個人資料頁面的JavaScript代碼重構為外部模組
   - 建立`/static/js/profile/profile.js`專用模組
   - 改進程式碼組織和可維護性
   - 實現淺色/深色模式下的最佳顯示效果

4. **精靈卡片顯示優化**:
   - 優化精靈卡片呈現，支援1024x1536的垂直長方形圖片格式
   - 調整CSS樣式，確保精靈圖片完整顯示而不失真
   - 改進深色模式下的力量值和標籤顯示，提高對比度
   - 為不同元素類型的精靈設定對應的顏色標記

5. **按元素類型分類顯示精靈**:
   - 將精靈收藏按元素類型(水系、火系、土系、風系)分類顯示
   - 實現分頁切換功能，方便瀏覽不同類型的精靈
   - 空狀態處理，當無特定元素精靈時顯示適當提示

### 資料結構更新
1. **資料庫結構優化**:
   - 新增`arenas`集合，記錄所有擂台資訊
   - 使用者文檔中新增`fight_count`字段，追蹤戰鬥總數
   - 優化擂台從`game.arena_detail`到`game_arena.get_arena`的路由結構
   - 改進使用者精靈查詢效率

2. **資料同步機制**:
   - 建立Firebase與本地資料的同步機制
   - 優化資料讀取流程，減少不必要的API請求
   - 實現資料快取策略，提升應用效能

### 目前進行中的工作
1. **社群功能開發**:
   - 精靈交換系統設計中
   - 好友系統框架建立中

2. **遊戲平衡性調整**:
   - 精靈屬性相剋系統細化
   - 擂台獎勵機制優化

3. **性能優化**:
   - 地圖渲染效能改進
   - API 請求緩存策略升級

### 即將推出的功能
1. **每日任務系統**:
   - 提供日常任務和獎勵
   - 特殊事件和時限挑戰

2. **更多路線支援**:
   - 擴展至更多公車路線
   - 城市間的精靈差異化設計

3. **精靈進化系統**:
   - 精靈進化路線設計
   - 進化條件與特殊技能

## 最新進度更新 (2025年5月8日)

### 導航與用戶體驗改進
1. **道館導航優化**:
   - 修復從捕捉頁面 (catch.html) 點擊道館時導航問題
   - 現在從捕捉頁面點擊道館按鈕時會直接導向特定道館頁面 (`/game/battle?arena_id=arena-xxx`)，而不是道館列表頁面
   - 統一所有地圖上道館標記的點擊行為，保持一致的用戶體驗

2. **關鍵檔案修改**:
   - 修改 `stop-manager.js`：將彈出視窗中的按鈕事件從 `showArenaInfo` 更改為 `goToArena`
   - 修改 `arena-manager.js`：新增 `goToArena` 函數，實現直接導航到特定道館頁面的功能
   - 統一多個模組中的道館點擊行為，確保一致性

3. **用戶體驗提升**:
   - 精簡用戶導航路徑，減少頁面跳轉
   - 確保所有地圖上的道館互動保持一致
   - 優化道館訪問流程，提高用戶體驗

## 使用技術
- **前端框架**：Bootstrap 5 響應式佈局
- **地圖技術**：OpenStreetMap + Leaflet.js
- **後端框架**：Flask 2.3.0
- **資料庫**：Firebase Realtime Database + Firestore + SQLAlchemy
- **使用者認證**：Firebase Authentication + Flask-Login
- **API 整合**：TDX 運輸資料 API + Firebase Cloud Functions
- **部署環境**：Firebase Hosting + Cloud Functions
- **自動化測試**：Pytest + pytest-cov
- **程式碼品質工具**：Black + Ruff
- **版本控制**：Git + GitHub

## 前端架構說明
本專案前端採用模組化設計，透過關注點分離原則提高代碼可維護性：

1. **HTML模板**：採用Flask Jinja2模板引擎
2. **CSS架構**：
   - 遵循BEM命名約定
   - 採用功能模組化組織
   - 支援深色模式與響應式設計
3. **JavaScript架構**：
   - 功能模組化拆分
   - 事件委派模式
   - 非同步請求處理
   - 錯誤捕獲與處理機制
