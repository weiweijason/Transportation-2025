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
  console.log('使用直接方法初始化地圖，容器ID:', containerId);
  try {
    // 確保容器存在且有效
    const mapContainer = document.getElementById(containerId);
    if (!mapContainer) {
      throw new Error('地圖容器不存在: ' + containerId);
    }
    
    // 徹底清理容器，移除任何 Leaflet 相關的屬性和事件
    function thoroughlyCleanContainer(container) {
      try {
        // 移除所有 Leaflet 相關的數據屬性
        delete container._leaflet_id;
        delete container._leaflet;
        
        // 移除 Leaflet 的 CSS 類
        container.classList.remove('leaflet-container', 'leaflet-touch', 'leaflet-fade-anim', 'leaflet-grab', 'leaflet-touch-drag', 'leaflet-touch-zoom');
        
        // 清空容器內容
        container.innerHTML = '';
        
        // 重置樣式
        container.style.cssText = '';
        container.style.width = '100%';
        container.style.height = '100vh';
        container.style.minHeight = '400px';
        container.style.position = 'relative';
        
        console.log('容器已徹底清理:', containerId);
      } catch (cleanError) {
        console.warn('清理容器時出錯:', cleanError);
      }
    }
    
    // 徹底清理並移除現有地圖實例
    const instancesToClean = [gameMap, window.gameMap, window.busMap];
    
    for (let i = 0; i < instancesToClean.length; i++) {
      const mapInstance = instancesToClean[i];
      if (mapInstance && typeof mapInstance.remove === 'function') {
        try {
          mapInstance.off(); // 移除所有事件監聽器
          mapInstance.remove();
          console.log(`地圖實例 ${i} 已移除`);
        } catch (removeError) {
          console.warn(`移除地圖實例 ${i} 時出錯:`, removeError);
          
          // 如果 remove() 失敗，嘗試手動清理
          try {
            if (mapInstance._container) {
              thoroughlyCleanContainer(mapInstance._container);
            }
          } catch (manualCleanError) {
            console.warn('手動清理失敗:', manualCleanError);
          }
        }
      }
    }
    
    // 清理全局變量
    gameMap = null;
    window.gameMap = null;
    window.busMap = null;
    
    // 徹底清理目標容器
    thoroughlyCleanContainer(mapContainer);
    
    // 等待一小段時間確保清理完成
    setTimeout(() => {
      console.log('開始創建新地圖實例...');
      
      // 再次確保容器有尺寸
      const rect = mapContainer.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) {
        console.warn('地圖容器尺寸為0，設置預設尺寸');
        mapContainer.style.width = '100%';
        mapContainer.style.height = '100vh';
        mapContainer.style.minHeight = '400px';
      }
      
      // 創建新地圖實例
      try {
        createNewMapInstance(containerId);
      } catch (createError) {
        console.error('創建新地圖實例失敗:', createError);
        hideLoading();
        showGameAlert('地圖創建失敗，請刷新頁面重試', 'error');
      }
    }, 100);
    
  } catch (error) {
    console.error('地圖初始化失敗:', error);
    hideLoading();
    showGameAlert('地圖初始化失敗，請刷新頁面重試', 'error');
  }
}

// 創建新地圖實例的獨立函數
function createNewMapInstance(containerId) {
  try {
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
    
  } catch (createInstanceError) {
    console.error('創建地圖實例失敗:', createInstanceError);
    hideLoading();
    showGameAlert('地圖實例創建失敗，請刷新頁面重試', 'error');
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
  const targetMap = window.gameMap || window.busMap;
  if (!targetMap) {
    console.warn('沒有可用的地圖實例，無法添加默認位置標記');
    return;
  }
  
  const defaultPos = [25.0330, 121.5654]; // 台北市中心
  window.userLocation = { lat: defaultPos[0], lng: defaultPos[1] };
  
  console.log('使用預設位置:', defaultPos);
  
  // 創建用戶位置標記
  if (window.userMarker) {
    window.userMarker.setLatLng(defaultPos);
  } else {
    window.userMarker = L.marker(defaultPos, {
      icon: L.divIcon({
        className: 'user-marker',
        html: '<div style="background-color:#FFA500;width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 2px 5px rgba(0,0,0,0.3);"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      })
    }).addTo(targetMap);
  }
  
  // 創建用戶範圍圓圈
  if (window.userCircle) {
    window.userCircle.setLatLng(defaultPos);
  } else {
    window.userCircle = L.circle(defaultPos, {
      radius: 300,
      color: '#FFA500',
      fillColor: '#FFA500',
      fillOpacity: 0.1,
      weight: 2
    }).addTo(targetMap);
  }
  
  // 更新地圖視角
  if (window.safeSetMapView) {
    window.safeSetMapView(targetMap, defaultPos, 14);
  } else {
    try {
      targetMap.setView(defaultPos, 14);
    } catch (error) {
      console.error('設置預設位置視圖時發生錯誤:', error);
    }
  }
  
  // 更新位置顯示
  const locationElement = document.getElementById('currentLocation');
  if (locationElement) {
    locationElement.textContent = `默認位置 (無法獲取實際位置)`;
  }
}

// 更新用戶位置
function updateUserLocation() {
  return new Promise((resolve, reject) => {
    console.log('開始獲取用戶位置...');
    
    // 檢查地圖實例
    const targetMap = window.gameMap || window.busMap;
    if (!targetMap) {
      const error = '地圖尚未初始化';
      console.error(error);
      reject(error);
      return;
    }
    
    // 檢查地理位置API是否可用
    if (!navigator.geolocation) {
      const error = '您的瀏覽器不支持地理位置功能';
      console.error(error);
      reject(error);
      return;
    }
    
    // 首先檢查位置權限
    if (navigator.permissions) {
      navigator.permissions.query({name: 'geolocation'}).then((permissionStatus) => {
        console.log('位置權限狀態:', permissionStatus.state);
        
        if (permissionStatus.state === 'denied') {
          const error = '位置權限被拒絕，請在瀏覽器設置中允許位置訪問';
          console.error(error);
          showGameAlert('位置權限被拒絕，請允許位置訪問後重試', 'warning');
          reject(error);
          return;
        }
        
        // 執行位置獲取
        performLocationRequest(targetMap, resolve, reject);
      }).catch(() => {
        // 如果權限查詢失敗，直接嘗試獲取位置
        console.warn('無法查詢位置權限，直接嘗試獲取位置');
        performLocationRequest(targetMap, resolve, reject);
      });
    } else {
      // 舊版瀏覽器沒有 permissions API
      console.log('瀏覽器不支持權限API，直接嘗試獲取位置');
      performLocationRequest(targetMap, resolve, reject);
    }
  });
}

// 執行實際的位置請求
function performLocationRequest(targetMap, resolve, reject) {
  const positionOptions = {
    enableHighAccuracy: true,    // 高精度定位
    timeout: 15000,             // 15秒超時（增加超時時間）
    maximumAge: 30000           // 30秒內的缓存位置有效
  };
  
  console.log('開始地理位置請求，選項:', positionOptions);
  
  navigator.geolocation.getCurrentPosition(
    // 成功回調
    (position) => {
      console.log('位置獲取成功:', position);
      
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
      const accuracy = position.coords.accuracy;
      
      console.log(`位置: ${lat}, ${lng}, 精度: ${accuracy}米`);
      
      // 檢查位置是否合理（台灣範圍）
      if (lat < 21.5 || lat > 25.5 || lng < 119.5 || lng > 122.5) {
        console.warn('位置似乎不在台灣範圍內，但仍繼續使用');
      }
        
        // 更新用戶位置標記
        if (window.userMarker) {
          window.userMarker.setLatLng([lat, lng]);
        } else {
          window.userMarker = L.marker([lat, lng], {
            icon: L.divIcon({
              className: 'user-marker',
              html: '<div style="background-color:#4285F4;width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 2px 5px rgba(0,0,0,0.3);"></div>',
              iconSize: [20, 20],
              iconAnchor: [10, 10]
            })
          }).addTo(targetMap);
        }
        
        // 更新用戶範圍圓圈
        if (window.userCircle) {
          window.userCircle.setLatLng([lat, lng]);
        } else {
          window.userCircle = L.circle([lat, lng], {
            radius: 300,
            color: '#4285F4',
            fillColor: '#4285F4',
            fillOpacity: 0.1,
            weight: 2
          }).addTo(targetMap);
        }
        
        // 使用安全的地圖視角更新
        if (window.safeSetMapView) {
          const success = window.safeSetMapView(targetMap, [lat, lng], 16);
          if (!success) {
            console.warn('安全地圖視角設置失敗，使用備用方法');
            try {
              targetMap.setView([lat, lng], 16);
            } catch (setViewError) {
              console.error('地圖視角設置失敗:', setViewError);
            }
          }
        } else {
          try {
            targetMap.setView([lat, lng], 16);
          } catch (error) {
            console.error('設置用戶位置視圖時發生錯誤:', error);
          }
        }
        
        // 更新位置顯示
        const locationElement = document.getElementById('currentLocation');
        if (locationElement) {
          locationElement.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        }
        
        // 保存位置到全局變量
        window.userLocation = { lat: lat, lng: lng };
        
        console.log('用戶位置更新完成');
        showGameAlert('位置更新成功！', 'success');
        resolve([lat, lng]);
    },
    // 錯誤回調
    (error) => {
      console.error('地理位置獲取失敗:', error);
      
      let errorMessage = '無法獲取您的位置';
      
      switch(error.code) {
        case error.PERMISSION_DENIED:
          errorMessage = '位置權限被拒絕，請在瀏覽器設置中允許位置訪問';
          showGameAlert('請允許瀏覽器訪問您的位置', 'warning');
          break;
        case error.POSITION_UNAVAILABLE:
          errorMessage = '位置信息不可用，請檢查GPS或網絡連接';
          showGameAlert('無法獲取位置信息，請檢查GPS設置', 'warning');
          break;
        case error.TIMEOUT:
          errorMessage = '位置獲取超時，請重試';
          showGameAlert('定位超時，請重試', 'warning');
          break;
        default:
          errorMessage = '位置獲取發生未知錯誤';
          showGameAlert('定位失敗，請重試', 'error');
          break;
      }
      
      console.error('使用預設位置:', errorMessage);
      
      // 失敗時使用默認標記
      addDefaultLocationMarker();
      showGameAlert('使用預設位置（台北市中心）', 'info');
      
      reject(new Error(errorMessage));
    },
    // 選項
    positionOptions
  );
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

// 安全的地圖操作函數，避免 _leaflet_pos 錯誤
function safeSetMapView(map, center, zoom) {
  if (!map || !center) {
    console.warn('safeSetMapView: 無效的地圖實例或座標');
    return false;
  }
  
  try {
    // 檢查地圖實例是否有效
    if (!map.getContainer || !map.getContainer()) {
      console.warn('safeSetMapView: 地圖容器無效');
      return false;
    }
    
    // 檢查容器是否在 DOM 中且有尺寸
    const container = map.getContainer();
    if (!container.parentNode || container.offsetWidth === 0 || container.offsetHeight === 0) {
      console.warn('safeSetMapView: 地圖容器尺寸無效或不在 DOM 中');
      return false;
    }
    
    // 檢查地圖是否已經初始化完成
    if (!map._loaded) {
      console.warn('safeSetMapView: 地圖尚未完全載入，延遲執行');
      setTimeout(() => safeSetMapView(map, center, zoom), 100);
      return false;
    }
    
    // 檢查地圖的內部狀態
    if (!map._panes || !map._panes.mapPane) {
      console.warn('safeSetMapView: 地圖內部結構不完整');
      return false;
    }
    
    // 強制重新計算容器位置
    if (map._resetView) {
      try {
        map.invalidateSize();
      } catch (invalidateError) {
        console.warn('地圖尺寸重新計算失敗:', invalidateError);
      }
    }
    
    // 使用更安全的方式設置視圖
    // 如果直接 setView 失敗，嘗試分步設置
    try {
      map.setView(center, zoom);
      return true;
    } catch (setViewError) {
      console.warn('直接 setView 失敗，嘗試分步設置:', setViewError);
      
      try {
        // 分步設置：先設置中心點，再設置縮放級別
        map.panTo(center);
        setTimeout(() => {
          try {
            map.setZoom(zoom);
          } catch (zoomError) {
            console.warn('設置縮放級別失敗:', zoomError);
          }
        }, 50);
        return true;
      } catch (panError) {
        console.error('分步設置也失敗:', panError);
        return false;
      }
    }
    
  } catch (error) {
    console.error('safeSetMapView 發生錯誤:', error);
    return false;
  }
}

// 安全的地圖縮放函數
function safeSetMapZoom(map, zoom) {
  if (!map) {
    console.warn('safeSetMapZoom: 無效的地圖實例');
    return false;
  }
  
  try {
    if (!map.getContainer || !map.getContainer()) {
      console.warn('safeSetMapZoom: 地圖容器無效');
      return false;
    }
    
    const container = map.getContainer();
    if (!container.parentNode || container.offsetWidth === 0 || container.offsetHeight === 0) {
      console.warn('safeSetMapZoom: 地圖容器尺寸無效');
      return false;
    }
    
    if (!map._loaded) {
      console.warn('safeSetMapZoom: 地圖尚未完全載入，延遲執行');
      setTimeout(() => safeSetMapZoom(map, zoom), 100);
      return false;
    }
    
    map.setZoom(zoom);
    return true;
    
  } catch (error) {
    console.error('safeSetMapZoom 發生錯誤:', error);
    return false;
  }
}

// 檢查地圖實例是否有效
function isMapInstanceValid(map) {
  try {
    return map && 
           typeof map.getContainer === 'function' && 
           map.getContainer() && 
           map.getContainer().parentNode &&
           map.getContainer().offsetWidth > 0 &&
           map.getContainer().offsetHeight > 0;
  } catch (error) {
    console.warn('檢查地圖實例時發生錯誤:', error);
    return false;
  }
}

// 全局導出安全函數
window.safeSetMapView = safeSetMapView;
window.safeSetMapZoom = safeSetMapZoom;
window.isMapInstanceValid = isMapInstanceValid;

// 全局導出地圖功能函數
window.initializeMap = initializeMap;
window.createDirectMap = createDirectMap;
window.updateUserLocation = updateUserLocation;
window.addDefaultLocationMarker = addDefaultLocationMarker;