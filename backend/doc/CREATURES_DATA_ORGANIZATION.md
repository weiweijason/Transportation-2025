# 精靈數據文件組織說明

## 文件分離結構

為了更好地管理和組織精靈數據，我們將精靈相關的CSV文件分為兩個不同的目錄：

### 1. 生成器腳本數據 (`/scripts/`)
- **文件位置**: `scripts/cached_creatures.csv`
- **用途**: `creature_generator.py` 腳本生成的精靈數據緩存
- **特點**: 
  - 由獨立的生成器腳本維護
  - 包含從CSV模板生成的精靈數據
  - 主要用於測試和開發階段

### 2. 主遊戲數據 (`/app/data/creatures/`)
- **文件位置**: `app/data/creatures/firebase_cached_creatures.csv`
- **用途**: 主遊戲從Firebase抓取的精靈數據緩存
- **特點**:
  - 由 `firebase_service.py` 的 `cache_creatures_to_csv()` 方法維護
  - 包含實時從Firebase獲取的精靈數據
  - 用於離線模式或緩存加速

## 文件結構

```
proj/
├── scripts/
│   ├── cached_creatures.csv          # 生成器腳本的緩存
│   ├── creatures.csv                 # 精靈模板數據
│   └── creature_generator.py         # 精靈生成器腳本
└── app/
    └── data/
        └── creatures/
            ├── firebase_cached_creatures.csv  # 主遊戲Firebase緩存
            ├── current_creatures.csv          # 當前活躍精靈（如果有）
            ├── .gitignore                     # 忽略緩存文件
            └── .gitkeep                       # 保持目錄結構
```

## 版本控制

- **被追蹤的文件**: 
  - `scripts/creatures.csv` (精靈模板)
  - `app/data/creatures/.gitkeep` (目錄結構)
  
- **被忽略的文件**:
  - `scripts/cached_creatures.csv` (生成器緩存)
  - `app/data/creatures/firebase_cached_creatures.csv` (主遊戲緩存)
  - `app/data/creatures/current_creatures.csv` (臨時文件)

## 相關方法

### FirebaseService.cache_creatures_to_csv()
- 從Firebase獲取精靈數據並緩存到 `app/data/creatures/firebase_cached_creatures.csv`
- 包含字段: id, name, type, rate, hp, attack, route_id, route_name, lat, lng, created_at, expires_at, image_url

### FirebaseService.get_creatures_from_csv()
- 從 `app/data/creatures/firebase_cached_creatures.csv` 讀取緩存的精靈數據
- 返回與Firebase格式兼容的精靈數據列表

## 優點

1. **清晰分離**: 開發/測試數據與生產數據分開
2. **易於維護**: 每個部分的職責明確
3. **版本控制**: 只追蹤必要的模板文件，忽略緩存文件
4. **性能優化**: 主遊戲可以使用本地緩存提高響應速度
