/**
 * 地圖功能相關函數模組
 * 處理地圖初始化、標記顯示和地理位置等功能
 */

// 全局地圖變數 - 確保在 window 物件上也有備份
let gameMap = null;
window.gameMap = null;
window.busMap = null;

// 初始化地圖的函數
function initializeMap(containerId = 'map') {
  console.log('開始初始化地圖...');
  showLoading();
  
  // 確認地圖容器存在
  const mapContainer = document.getElementById(containerId);
  if (!mapContainer) {
    console.error('找不到地圖容器元素 #' + containerId);
    hideLoading();
    showGameAlert('地圖容器元素不存在，請刷新頁面重試。', 'danger');
    return;
  }
  
  // 確保 Leaflet 庫已載入
  if (typeof L === 'undefined') {
    console.error('Leaflet 庫未載入或未定義');
    hideLoading();
    showGameAlert('地圖庫未載入，請刷新頁面重試。', 'danger');
    return;
  }
  
  try {
    // 嘗試直接創建地圖，不再依賴模組導出的函數
    createDirectMap(containerId);
  } catch (error) {
    console.error('初始化地圖時發生錯誤:', error);
    hideLoading();
    showGameAlert('地圖初始化失敗，請檢查網絡連接並刷新頁面重試。', 'danger');
  }
}

// 備用：直接創建地圖（不依賴模組）
function createDirectMap(containerId = 'map') {
  console.log('使用直接方法初始化地圖');
  try {    // 如果已經有地圖實例，先移除
    if (gameMap && typeof gameMap.remove === 'function') {
      gameMap.remove();
    }
    if (window.gameMap && typeof window.gameMap.remove === 'function') {
      window.gameMap.remove();
    }
    if (window.busMap && typeof window.busMap.remove === 'function') {
      window.busMap.remove();
    }
    
    // 創建新的地圖實例
    gameMap = L.map(containerId, {
      center: [25.0165, 121.5375],
      zoom: 14,
      attributionControl: true,
      zoomControl: true,
      dragging: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      touchZoom: true,
      boxZoom: true,
      tap: true
    });
    
    // 同步全局變數
    window.gameMap = gameMap;
    window.busMap = gameMap;
    
    console.log('地圖實例已創建');
    
    // 添加基本地圖圖層（測試多個圖層來源以確保至少一個能夠載入）
    try {
      // 嘗試使用OpenStreetMap
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(gameMap);
      console.log('OpenStreetMap 圖層已添加');
    } catch (tileError) {
      console.warn('無法添加OpenStreetMap圖層，嘗試備用圖層', tileError);
      
      try {
        // 備用地圖源: CartoDB
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
          subdomains: 'abcd',
          maxZoom: 19
        }).addTo(gameMap);
        console.log('CartoDB 圖層已添加');
      } catch (backupTileError) {
        console.error('所有地圖圖層添加失敗', backupTileError);
        showGameAlert('地圖圖層載入失敗，請檢查網絡連接並刷新頁面重試。', 'danger');
      }
    }
    
    // 創建必要的圖層
    window.routeLayer = L.layerGroup().addTo(gameMap);
    window.stopsLayer = L.layerGroup().addTo(gameMap);
    window.busesLayer = L.layerGroup().addTo(gameMap);
    window.creaturesLayer = L.layerGroup().addTo(gameMap);
    window.arenaLayer = L.layerGroup().addTo(gameMap);
    
    console.log('地圖圖層已創建');
    
    // 加入默認數據
    setupDefaultData();
    
    // 完成初始化
    finishMapInitialization();
  } catch (directError) {
    console.error('備用地圖初始化也失敗:', directError);
    hideLoading();
    showGameAlert('地圖初始化失敗，請檢查網絡連接並刷新頁面重試。', 'danger');
    throw directError; // 重新拋出錯誤以便於調試
  }
}

// 設置默認數據（當模組加載失敗時使用）
function setupDefaultData() {
  // 設置默認路線顏色
  window.routeColors = {
    'cat_right': '#ff9800',
    'cat_left': '#4caf50',
    'cat_left_zhinan': '#9c27b0'
  };
  
  // 設置默認座標（空陣列，將在實際操作中填充）
  window.routeCoordinates = {
    'cat_right': [],
    'cat_left': [],
    'cat_left_zhinan': []
  };
  
  // 設置精靈生成參數
  window.MAX_CREATURES_PER_ROUTE = 3;
  window.CREATURE_LIFETIME = 300000; // 5分鐘
  window.SPAWN_INTERVAL = 60000;     // 1分鐘
  window.SPAWN_CHANCE = 0.3;         // 30%機率
  
  // 設置精靈類型
  window.routeCreatureTypes = {
    'cat_right': [
      { id: 'cr1', name: '火焰鼠', type: '火系', rarity: '普通', power: 10 },
      { id: 'cr2', name: '閃電貓', type: '電系', rarity: '稀有', power: 25 }
    ],
    'cat_left': [
      { id: 'cl1', name: '水靈兔', type: '水系', rarity: '普通', power: 12 },
      { id: 'cl2', name: '綠葉猴', type: '土系', rarity: '稀有', power: 27 }
    ],
    'cat_left_zhinan': [
      { id: 'cz1', name: '風翔鷹', type: '風系', rarity: '史詩', power: 35 },
      { id: 'cz2', name: '雷擊獅', type: '電系', rarity: '傳說', power: 50 }
    ]
  };
  
  // 默認用戶位置（台北市）
  window.userLocation = [25.0330, 121.5654];
}

// 完成地圖初始化後的共同操作
function finishMapInitialization() {
  try {
    // 加載路線（如果函數存在）
    if (typeof loadCatRightRoute === 'function') {
      console.log('載入路線-右線');
      loadCatRightRoute();
    }
    
    if (typeof loadCatLeftRoute === 'function') {
      console.log('載入路線-左線');
      loadCatLeftRoute();
    }
    
    if (typeof loadCatLeftZhinanRoute === 'function') {
      console.log('載入路線-左線指南宮');
      loadCatLeftZhinanRoute();
    }
    
    // 加載站點和道館
    if (typeof loadAllBusStops === 'function') {
      console.log('載入站點和道館');
      loadAllBusStops();
    }
    
    // 調整地圖大小以確保正確渲染
    setTimeout(function() {
      console.log('調整地圖大小');
      if (gameMap && typeof gameMap.invalidateSize === 'function') {
        gameMap.invalidateSize();
      }
    }, 500);
    
    // 更新用戶位置（如果函數存在）
    if (typeof updateUserLocation === 'function') {
      console.log('更新用戶位置');
      updateUserLocation().catch(err => {
        console.warn('位置更新失敗:', err);
      });
    } else {
      // 如果無法獲取位置，使用默認位置標記
      addDefaultLocationMarker();
    }
    
    // 載入路線精靈
    fetchRouteCreatures();
    
    console.log('地圖初始化完成');
    hideLoading();
  } catch (finishError) {
    console.error('完成地圖初始化時發生錯誤:', finishError);
    hideLoading();
    showGameAlert('地圖功能部分載入失敗，部分功能可能不可用。', 'warning');
  }
}

// 添加默認位置標記
function addDefaultLocationMarker() {
  if (!gameMap) return;
  
  const defaultPos = [25.0330, 121.5654]; // 台北市中心
  window.userLocation = defaultPos;
  
  // 創建用戶位置標記
  window.userMarker = L.marker(defaultPos, {
    icon: L.divIcon({
      className: 'user-marker',
      html: '<div style="background-color:#FFA500;width:20px;height:20px;border-radius:50%;border:3px solid white;"></div>',
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    })
  }).addTo(gameMap);
  
  // 創建用戶範圍圓圈
  window.userCircle = L.circle(defaultPos, {
    radius: 300,
    color: '#FFA500',
    fillColor: '#FFA500',
    fillOpacity: 0.1,
    weight: 1
  }).addTo(gameMap);
  
  // 更新地圖視角
  gameMap.setView(defaultPos, 14);
  
  // 更新位置顯示
  const locationElement = document.getElementById('currentLocation');
  if (locationElement) {
    locationElement.textContent = `默認位置 (無法獲取實際位置)`;
  }
}

// 更新用戶位置
function updateUserLocation() {
  return new Promise((resolve, reject) => {
    if (!gameMap) {
      reject('地圖尚未初始化');
      return;
    }
    
    if (!navigator.geolocation) {
      reject('您的瀏覽器不支持地理位置功能');
      return;
    }
    
    navigator.geolocation.getCurrentPosition(
      // 成功回調
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        
        // 更新用戶位置標記
        if (window.userMarker) {
          window.userMarker.setLatLng([lat, lng]);
        } else {
          window.userMarker = L.marker([lat, lng], {
            icon: L.divIcon({
              className: 'user-marker',
              html: '<div style="background-color:#FFA500;width:20px;height:20px;border-radius:50%;border:3px solid white;"></div>',
              iconSize: [20, 20],
              iconAnchor: [10, 10]
            })
          }).addTo(gameMap);
        }
        
        // 更新用戶範圍圓圈
        if (window.userCircle) {
          window.userCircle.setLatLng([lat, lng]);
        } else {
          window.userCircle = L.circle([lat, lng], {
            radius: 300,
            color: '#FFA500',
            fillColor: '#FFA500',
            fillOpacity: 0.1,
            weight: 1
          }).addTo(gameMap);
        }
        
        // 更新地圖視角
        gameMap.setView([lat, lng], 16);
        
        // 更新位置顯示
        const locationElement = document.getElementById('currentLocation');
        if (locationElement) {
          locationElement.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        }
        
        // 保存位置到全局變量
        window.userLocation = [lat, lng];
        
        resolve([lat, lng]);
      },
      // 錯誤回調
      (error) => {
        console.error('無法獲取位置:', error.message);
        addDefaultLocationMarker(); // 失敗時使用默認標記
        reject(error);
      },
      // 選項
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  });
}

// 根據路線名稱獲取顏色
function getRouteColorByName(routeName) {
  if (routeName.includes('右線')) {
    return '#ff9800';
  } else if (routeName.includes('左線') && routeName.includes('動物園')) {
    return '#4caf50';
  } else if (routeName.includes('左線') && routeName.includes('指南宮')) {
    return '#9c27b0';
  }
  return '#3498db'; // 預設藍色
}