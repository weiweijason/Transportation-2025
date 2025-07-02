# 新增API文檔總結

## 📋 本次更新新增的API端點

### 🎯 每日簽到系統 API (`/daily-migration`)

#### 1. 獲取簽到狀態
- **端點**: `GET /daily-migration/api/get-migration-status`
- **認證**: 需要 (`@login_required`)
- **功能**: 獲取用戶的每日簽到狀態和統計資訊
- **回應範例**:
```json
{
  "success": true,
  "migration_data": {
    "user_id": "user123",
    "username": "玩家名稱",
    "today": "2025-06-17",
    "has_migrated_today": false,
    "total_migrations": 15,
    "consecutive_days": 3,
    "last_migration_date": "2025-06-16"
  }
}
```

#### 2. 執行簽到
- **端點**: `POST /daily-migration/api/perform-migration`
- **認證**: 需要 (`@login_required`)
- **功能**: 執行每日簽到，獲得100經驗值和1個普通藥水碎片
- **獎勵**: 
  - 基礎: 100經驗值 + 1普通藥水碎片
  - 連續7天: 額外普通魔法陣
  - 連續14天: 額外2個普通藥水碎片
  - 連續30天: 額外進階魔法陣
- **回應範例**:
```json
{
  "success": true,
  "message": "簽到完成！獲得了豐富的獎勵！",
  "rewards": {
    "experience": 100,
    "items": [
      {
        "item_id": "normal_potion_fragment",
        "quantity": 1,
        "name": "普通藥水碎片"
      }
    ]
  },
  "new_experience": 1500,
  "triggered_achievements": []
}
```

#### 3. 獲取簽到歷史
- **端點**: `GET /daily-migration/api/get-migration-history`
- **認證**: 需要 (`@login_required`)
- **功能**: 獲取最近30天的簽到記錄

### 🏪 兌換商店系統 API (`/exchange-shop`)

#### 1. 獲取兌換數據
- **端點**: `GET /exchange-shop/api/get-exchange-data`
- **認證**: 需要 (`@login_required`)
- **功能**: 獲取用戶的兌換相關數據
- **回應範例**:
```json
{
  "success": true,
  "exchange_data": {
    "normal_potion_fragments": 15,
    "normal_potions": 2,
    "magic_circle_normal": 25,
    "magic_circle_advanced": 3,
    "magic_circle_legendary": 0
  }
}
```

#### 2. 兌換藥水碎片
- **端點**: `POST /exchange-shop/api/exchange-potion-fragments`
- **認證**: 需要 (`@login_required`)
- **功能**: 7個普通藥水碎片兌換1瓶普通藥水
- **規則**: 自動計算可兌換數量，餘額碎片保留
- **回應範例**:
```json
{
  "success": true,
  "message": "成功兌換2瓶普通藥水！",
  "exchanged_potions": 2,
  "remaining_fragments": 1,
  "total_potions": 4
}
```

#### 3. 兌換魔法陣
- **端點**: `POST /exchange-shop/api/exchange-magic-circles`
- **認證**: 需要 (`@login_required`)
- **功能**: 魔法陣等級提升
- **參數**: 
  - `exchange_type`: `normal_to_advanced` 或 `advanced_to_legendary`
- **規則**: 
  - 10個普通魔法陣 = 1個進階魔法陣
  - 10個進階魔法陣 = 1個高級魔法陣
- **回應範例**:
```json
{
  "success": true,
  "message": "成功兌換2個進階魔法陣！",
  "exchanged_amount": 2,
  "remaining_normal": 5,
  "total_advanced": 5
}
```

## 🗃️ Firebase 資料結構更新

### 用戶主資料 (`users/{userId}`)
```javascript
{
  experience: number,              // 用戶經驗值
  normal_potion_fragments: number, // 普通藥水碎片數量 (新增)
  normal_potions: number,          // 普通藥水數量 (新增)
  magic_circle_normal: number,     // 普通魔法陣數量 (新增)
  magic_circle_advanced: number,   // 進階魔法陣數量 (新增)
  magic_circle_legendary: number,  // 高級魔法陣數量 (新增)
  last_migration_date: string      // 最後簽到日期
}
```

### 簽到記錄 (`users/{userId}/daily_migrations/{date}`)
```javascript
{
  migration_date: string,      // 簽到日期 (YYYY-MM-DD)
  migration_time: string,      // 簽到時間 (ISO格式)
  experience_gained: number,   // 獲得的經驗值
  items_received: array,       // 獲得的道具列表
  rewards_claimed: boolean,    // 是否已領取獎勵
  created_at: string          // 記錄創建時間
}
```

## 📊 API文檔頁面

### 新增的文檔頁面
1. **每日簽到API**: `/api-docs/daily-checkin-apis`
2. **兌換商店API**: `/api-docs/exchange-shop-apis`
3. **API數據端點**: 
   - `/api-docs/api/daily-checkin-endpoints`
   - `/api-docs/api/exchange-shop-endpoints`

### 更新的頁面
- **主頁** (`/api-docs/`): 新增API專區導航卡片

## 🔧 系統整合

### 路由註冊
- `app/routes/__init__.py`: 註冊新的藍圖
- `app.py`: 添加到公開路徑列表 (如適用)

### 前端整合
- **MyBag頁面**: 新增兌換商店入口按鈕
- **導航欄**: 更新"每日遷移"為"每日簽到"
- **浮動按鈕**: 更新提示文字

### 後端邏輯
- **自動兌換**: 7個碎片自動轉換為1瓶藥水
- **經驗值更新**: 每次簽到自動更新用戶經驗值
- **成就觸發**: 根據簽到天數觸發相應成就
- **連續獎勵**: 連續簽到天數計算和獎勵加成

## ✅ 完成狀態

- [x] 每日簽到系統 API 開發
- [x] 兌換商店系統 API 開發  
- [x] Firebase 後端整合
- [x] 前端頁面更新
- [x] API 文檔撰寫
- [x] 路由註冊和系統整合
- [x] 文字修正 (遷移 → 簽到)

所有功能已完成並準備投入使用！🎉
