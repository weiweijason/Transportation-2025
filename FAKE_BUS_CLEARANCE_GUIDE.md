# 虛假公車數據清理說明

## 問題說明

用戶在地圖上看到了以下虛假的公車車號：
- **ZHN-888** (指南宮線測試車號)
- **CAT-001** (貓空左線測試車號)  
- **RIGHT-789** (貓空右線測試車號)

這些都是開發過程中使用的測試數據，不應該出現在實際地圖上。

## 解決方案

### 1. 清空JSON數據文件 ✅

已將以下文件清空為空陣列 `[]`：
- `/static/data/bus/cat_left_bus.json`
- `/static/data/bus/cat_left_zhinan_bus.json` 
- `/static/data/bus/cat_right_bus.json`

### 2. 創建自動清理腳本 ✅

新增 `/static/js/utils/clear-fake-buses.js` 腳本，功能包括：
- 🔍 **檢測虛假車號**: 自動識別並標記測試車號
- 🗑️ **清除地圖標記**: 移除地圖上的虛假公車標記
- 🔄 **強制重新載入**: 確保顯示最新的正確數據
- ✅ **驗證清理結果**: 確認清理是否成功

### 3. 整合到頁面 ✅

腳本已整合到：
- `catch.html` (精靈捕捉頁面)
- `map.html` (全螢幕地圖頁面)

## 自動執行

腳本會在頁面載入後2秒自動執行清理，確保：
- 🚫 移除所有虛假公車標記
- 📱 重新載入正確的公車數據
- ✨ 地圖只顯示真實的公車位置

## 手動執行

如果需要手動清理，可在瀏覽器控制台執行：

```javascript
// 完整清理流程
window.fakeBusClearance.performCompleteClearance();

// 快速清除地圖標記
window.fakeBusClearance.quickClearFakeBuses();

// 驗證JSON文件狀態
window.fakeBusClearance.verifyJsonFilesCleared();

// 強制重新載入公車位置
window.fakeBusClearance.forceReloadBusPositions();
```

## 清理效果

### 清理前
```
地圖顯示:
❌ ZHN-888 (虛假指南宮公車)
❌ CAT-001 (虛假貓空左線公車)  
❌ RIGHT-789 (虛假貓空右線公車)
✅ 723-U3 (真實棕3路線公車)
✅ KKA-0270 (真實棕3路線公車)
```

### 清理後
```
地圖顯示:
✅ 723-U3 (真實棕3路線公車)
✅ KKA-0270 (真實棕3路線公車)

清除的虛假車號:
🗑️ ZHN-888 已移除
🗑️ CAT-001 已移除
🗑️ RIGHT-789 已移除
```

## 預防措施

### 1. 數據文件管理
- 🔒 正式環境只使用真實的公車數據
- 📝 測試數據應標記為測試專用
- 🚫 避免將測試車號混入正式數據

### 2. 車號命名規範
- ✅ **真實車號**: 如 `723-U3`, `KKA-0270`
- ❌ **測試車號**: 如 `TEST-001`, `ZHN-888`, `CAT-001`

### 3. 部署檢查
- 📋 部署前檢查所有JSON文件
- 🧪 運行驗證腳本確認數據正確性
- 👀 在地圖上目視檢查公車標記

## 故障排除

### Q: 清理後仍看到虛假公車？
**A**: 可能需要刷新頁面或清除瀏覽器快取

### Q: 清理腳本沒有執行？
**A**: 檢查瀏覽器控制台是否有JavaScript錯誤

### Q: JSON文件清空後公車數據沒更新？
**A**: 手動執行 `window.fakeBusClearance.forceReloadBusPositions()`

## 技術細節

### 檢測邏輯
```javascript
const fakeBusPlateNumbers = [
    'ZHN-888',    // 指南宮測試車號
    'CAT-001',    // 貓空左線測試車號  
    'RIGHT-789'   // 貓空右線測試車號
];
```

### 清理流程
1. 📋 驗證JSON文件是否已清空
2. 🗑️ 掃描並移除地圖上的虛假標記
3. 🔄 強制重新載入公車位置數據
4. ✅ 驗證清理結果

### 文件結構
```
app/static/js/
├── utils/
│   └── clear-fake-buses.js    # 清理腳本
├── modules/
│   └── bus-position-manager.js # 公車位置管理
└── data/bus/
    ├── br3_bus.json           # 棕3路線(保留真實數據)
    ├── cat_left_bus.json      # 貓空左線(已清空)
    ├── cat_left_zhinan_bus.json # 指南宮線(已清空)
    └── cat_right_bus.json     # 貓空右線(已清空)
```

---

**狀態**: ✅ 已完成  
**效果**: 🎯 虛假公車車號已完全清除  
**維護**: 🔄 自動清理腳本已部署  

*最後更新: 2025年6月18日*
