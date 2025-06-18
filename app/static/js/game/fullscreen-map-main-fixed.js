/**
 * 全螢幕地圖主要邏輯模組 - 修正版
 * 處理全螢幕地圖的事件監聽、用戶交互和地圖功能
 */

// 全螢幕地圖專用腳本
document.addEventListener('DOMContentLoaded', function() {
  console.log('全螢幕地圖 DOM 載入完成');
  
  // 隱藏導航欄和頁腳
  const navbar = document.querySelector('.navbar');
  const footer = document.querySelector('footer');
  if (navbar) navbar.style.display = 'none';
  if (footer) footer.style.display = 'none';

  // 確保必要的 UI 函數存在
  if (typeof showLoading !== 'function') {
    window.showLoading = function() {
      const overlay = document.getElementById('loadingOverlay');
      if (overlay) overlay.style.visibility = 'visible';
    };
  }
  
  if (typeof hideLoading !== 'function') {
    window.hideLoading = function() {
      const overlay = document.getElementById('loadingOverlay');
      if (overlay) overlay.style.visibility = 'hidden';
    };
  }
  
  if (typeof showGameAlert !== 'function') {
    window.showGameAlert = function(message, type) {
      console.log('[' + type + '] ' + message);
    };
  }

  // 初始化地圖應用
  setTimeout(function() {
    initializeFullscreenMap();
  }, 500);
  
  // 設置地圖容器ID為全螢幕地圖使用
  window.mapContainerId = 'map';
});

// 安全的地圖容器清理函數
function cleanMapContainer(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return false;
  
  try {
    // 移除 Leaflet 相關屬性
    delete container._leaflet_id;
    delete container._leaflet;
    
    // 移除所有 Leaflet 類名
    const leafletClasses = ['leaflet-container', 'leaflet-touch', 'leaflet-fade-anim', 
                           'leaflet-grab', 'leaflet-touch-drag', 'leaflet-touch-zoom'];
    leafletClasses.forEach(cls => container.classList.remove(cls));
    
    // 清空容器內容
    container.innerHTML = '';
    
    // 重置樣式
    container.style.cssText = '';
    container.style.width = '100%';
    container.style.height = '100vh';
    container.style.position = 'relative';
    
    console.log('地圖容器已清理:', containerId);
    return true;
  } catch (error) {
    console.error('清理地圖容器失敗:', error);
    return false;
  }
}

// 初始化全螢幕地圖
function initializeFullscreenMap() {
  console.log('開始初始化全螢幕地圖...');
  showLoading();
  
  // 移除現有地圖實例
  if (window.gameMap && typeof window.gameMap.remove === 'function') {
    try {
      window.gameMap.off();
      window.gameMap.remove();
      window.gameMap = null;
    } catch (e) {
      console.warn('移除 gameMap 失敗:', e);
    }
  }
  
  if (window.busMap && typeof window.busMap.remove === 'function') {
    try {
      window.busMap.off();
      window.busMap.remove();
      window.busMap = null;
    } catch (e) {
      console.warn('移除 busMap 失敗:', e);
    }
  }
  
  // 清理容器
  const containerCleaned = cleanMapContainer('map');
  if (!containerCleaned) {
    console.error('地圖容器清理失敗');
    hideLoading();
    return;
  }
  
  // 短暫延遲確保清理完成
  setTimeout(() => {
    createNewMap();
  }, 200);
}

// 創建新地圖
function createNewMap() {
  try {
    console.log('創建新的地圖實例...');
    
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
      throw new Error('地圖容器不存在');
    }
    
    // 確保容器有有效尺寸
    if (mapContainer.offsetWidth === 0 || mapContainer.offsetHeight === 0) {
      console.warn('容器尺寸異常，延遲重試');
      setTimeout(createNewMap, 500);
      return;
    }
    
    // 創建地圖
    const map = L.map('map', {
      center: [25.0165, 121.5375],
      zoom: 16,
      maxZoom: 19,
      minZoom: 10,
      zoomControl: true,
      attributionControl: false
    });
    
    // 添加圖層
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(map);
    
  // 等待地圖完全載入
  map.whenReady(() => {
    console.log('地圖已完全載入');
    
    // 設置全局變量
    window.gameMap = map;
    window.busMap = map;
    
    // 設置最大縮放級別（與catch.html一致）
    setTimeout(() => {
      if (map && typeof map.setZoom === 'function') {
        map.setZoom(19);
        console.log('地圖縮放級別已設置為最大: 19');
      }
    }, 500);
    
    // 初始化其他功能
    initializeMapFeatures();
    
    hideLoading();
  });
    
  } catch (error) {
    console.error('創建地圖失敗:', error);
    hideLoading();
    showGameAlert('地圖初始化失敗: ' + error.message, 'error');
  }
}

// 初始化地圖功能 - 與catch.html保持一致
function initializeMapFeatures() {
  console.log('初始化地圖功能...');
  
  // 當地圖初始化完成後，設置最大縮放（與catch.html一致）
  setTimeout(function() {
    const targetMap = window.gameMap || window.busMap;
    if (targetMap && typeof targetMap.setZoom === 'function') {
      targetMap.setZoom(19); // 設置為最大縮放級別
      console.log('地圖縮放級別已設置為最大: 19');
    }
  }, 1000);
  
  // 初始化用戶位置
  if (typeof window.updateUserLocation === 'function') {
    setTimeout(() => {
      window.updateUserLocation().then(() => {
        console.log('用戶位置初始化完成');
        
        // 確保用戶位置標記顯示
        setTimeout(() => {
          ensureUserLocationMarker();
        }, 500);
        
        // 隱藏定位錯誤提示（與catch.html一致）
        const errorContainer = document.getElementById('locationErrorContainer');
        if (errorContainer) {
          errorContainer.classList.add('d-none');
        }
      }).catch((error) => {
        console.warn('初始定位失敗:', error);
        
        // 顯示定位錯誤提示（與catch.html一致）
        const errorContainer = document.getElementById('locationErrorContainer');
        const errorText = document.getElementById('currentLocation');
        if (errorContainer && errorText) {
          errorContainer.classList.remove('d-none');
          errorText.textContent = '無法定位';
        }
      });
    }, 1000);
  }
  
  // 載入公車路線
  if (typeof window.loadBusRoutes === 'function') {
    setTimeout(() => {
      window.loadBusRoutes();
    }, 1500);
  }
  
  // 載入精靈
  if (typeof window.loadCreatures === 'function') {
    setTimeout(() => {
      window.loadCreatures();
    }, 2000);
  }
}

// 按鈕事件處理 - 與catch.html保持一致
document.addEventListener('DOMContentLoaded', function() {
  // 目前位置按鈕
  const goToCurrentLocationBtn = document.getElementById('goToCurrentLocationBtn');
  if (goToCurrentLocationBtn) {    goToCurrentLocationBtn.addEventListener('click', function() {
      console.log('用戶點擊目前位置按鈕');
      if (window.userLocation) {
        // 先檢查地圖容器健康狀態
        const healthCheck = checkMapContainerHealth();
        if (!healthCheck.healthy) {
          console.warn('地圖容器不健康:', healthCheck.reason);
          showGameAlert(healthCheck.reason + '，請稍候再試', 'warning');
          return;
        }
        
        const targetMap = window.gameMap || window.busMap;
        if (targetMap && typeof targetMap.setView === 'function') {
          // 先確保用戶位置標記存在
          ensureUserLocationMarker();
          
          // 使用安全設置，不再嘗試直接設置
          const success = safeSetMapView(targetMap, window.userLocation, 19);
          if (success) {
            console.log('已跳轉到用戶位置，縮放級別: 19');
          } else {
            console.log('地圖視圖設置延遲執行中...');
            showGameAlert('正在跳轉到您的位置，請稍候...', 'info');
            
            // 延遲後再次確保標記顯示
            setTimeout(() => {
              ensureUserLocationMarker();
            }, 1000);
          }
        } else {
          showGameAlert('地圖未就緒，請稍候再試', 'warning');
        }
      } else {
        showGameAlert('無法獲取當前位置，請嘗試重新定位', 'warning');
      }
    });
  }

  // 重新定位按鈕
  const refreshLocationBtn = document.getElementById('refreshLocationBtn');
  if (refreshLocationBtn) {
    refreshLocationBtn.addEventListener('click', function() {
      console.log('用戶點擊重新定位按鈕');
      
      // 顯示載入指示
      this.disabled = true;
      this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 定位中...';
        if (typeof window.updateUserLocation === 'function') {
        window.updateUserLocation().then(function() {
          showGameAlert('位置更新成功！', 'success');
          // 確保用戶位置標記重新顯示
          setTimeout(() => {
            ensureUserLocationMarker();
          }, 500);
        }).catch(function(error) {
          const errorMessage = error && error.message ? error.message : 
                             (typeof error === 'string' ? error : '重新定位失敗');
          showGameAlert('重新定位失敗: ' + errorMessage, 'warning');
        }).finally(() => {
          // 恢復按鈕狀態
          const btn = document.getElementById('refreshLocationBtn');
          if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-crosshairs"></i> 重新定位';
          }
        });
      } else {
        showGameAlert('位置更新功能不可用，請刷新頁面', 'error');
        this.disabled = false;
        this.innerHTML = '<i class="fas fa-crosshairs"></i> 重新定位';
      }
    });
  }

  // 重新初始化地圖按鈕
  const initMapBtn = document.getElementById('initMapBtn');
  if (initMapBtn) {
    initMapBtn.addEventListener('click', function() {
      console.log('用戶要求重新初始化地圖');
      showGameAlert('重新初始化地圖...', 'info');
      initializeFullscreenMap();
    });
  }
});

// 安全的地圖視圖設置函數 - 增強版
function safeSetMapView(map, location, zoom) {
  if (!map || typeof map.setView !== 'function') {
    console.warn('地圖實例無效');
    return false;
  }
  
  try {
    // 多層級檢查地圖就緒狀態
    const hasContainer = map._container !== null && map._container !== undefined;
    const isLoaded = map._loaded === true;
    const hasSize = map._size && map._size.x > 0 && map._size.y > 0;
    const hasLeafletPos = hasContainer && map._container._leaflet_pos !== undefined;
    const hasPanes = map._panes && map._panes.mapPane;
    
    console.log('地圖狀態檢查:', {
      hasContainer,
      isLoaded, 
      hasSize,
      hasLeafletPos,
      hasPanes
    });
    
    // 最基本的檢查 - 只要容器存在且已載入
    if (hasContainer && isLoaded) {
      try {
        // 先檢查是否有 _leaflet_pos，如果沒有就等一下
        if (!hasLeafletPos) {
          console.log('容器缺少 _leaflet_pos，等待初始化...');
          setTimeout(() => {
            safeSetMapView(map, location, zoom);
          }, 200);
          return false;
        }
        
        map.setView(location, zoom);
        console.log('地圖視圖設置成功');
        return true;
        
      } catch (setViewError) {
        console.warn('setView 調用失敗:', setViewError);
        
        // 如果是 _leaflet_pos 錯誤，等待並重試
        if (setViewError.message && setViewError.message.includes('_leaflet_pos')) {
          console.log('檢測到 _leaflet_pos 錯誤，延遲重試...');
          setTimeout(() => {
            safeSetMapView(map, location, zoom);
          }, 500);
          return false;
        }
        
        throw setViewError;
      }
    } else {
      console.warn('地圖基本條件不滿足，無法設置視圖');
      return false;
    }
  } catch (error) {
    console.error('地圖視圖設置完全失敗:', error);
    return false;
  }
}

// 確保用戶位置標記顯示的函數
function ensureUserLocationMarker() {
  const targetMap = window.gameMap || window.busMap;
  if (!targetMap || !window.userLocation) {
    return;
  }
  
  try {
    // 檢查是否已有用戶位置標記
    if (window.userLocationMarker) {
      // 如果標記存在但不在地圖上，重新添加
      if (!targetMap.hasLayer(window.userLocationMarker)) {
        window.userLocationMarker.addTo(targetMap);
        console.log('重新添加用戶位置標記到地圖');
      }
    } else {
      // 如果沒有標記，創建新的
      console.log('創建新的用戶位置標記');
      if (typeof window.addUserLocationMarker === 'function') {
        window.addUserLocationMarker();
      } else if (typeof L !== 'undefined') {
        // 創建簡單的位置標記
        window.userLocationMarker = L.marker(window.userLocation, {
          icon: L.divIcon({
            className: 'user-location-marker',
            html: '<i class="fas fa-crosshairs"></i>',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
          })
        }).addTo(targetMap);
        console.log('創建了簡單的用戶位置標記');
      }
    }
  } catch (error) {
    console.error('確保用戶位置標記失敗:', error);
  }
}

// 地圖容器健康狀態檢查函數
function checkMapContainerHealth() {
  const map = window.gameMap || window.busMap;
  if (!map) {
    console.log('地圖實例不存在');
    return { healthy: false, reason: '地圖實例不存在' };
  }
  
  if (!map._container) {
    console.log('地圖容器不存在');
    return { healthy: false, reason: '地圖容器不存在' };
  }
  
  if (!map._container._leaflet_pos) {
    console.log('地圖容器 _leaflet_pos 未初始化');
    return { healthy: false, reason: '地圖容器正在初始化中' };
  }
  
  if (!map._loaded) {
    console.log('地圖尚未載入完成');
    return { healthy: false, reason: '地圖正在載入中' };
  }
  
  console.log('地圖容器狀態健康');
  return { healthy: true, reason: '地圖已就緒' };
}

// 暴露函數到全局
window.initializeFullscreenMap = initializeFullscreenMap;
window.createNewMap = createNewMap;
window.cleanMapContainer = cleanMapContainer;
window.safeSetMapView = safeSetMapView;
window.ensureUserLocationMarker = ensureUserLocationMarker;
window.checkMapContainerHealth = checkMapContainerHealth;

// 簡單的提示函數
function showGameAlert(message, type = 'info') {
  const alertClass = type === 'success' ? 'alert-success' : 
                    type === 'error' ? 'alert-danger' : 
                    type === 'warning' ? 'alert-warning' : 'alert-info';
  
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert ${alertClass} position-fixed`;
  alertDiv.style.cssText = 'top: 70px; right: 20px; z-index: 9999; min-width: 250px;';
  alertDiv.innerHTML = `
    <div class="d-flex align-items-center">
      <span>${message}</span>
      <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
    </div>
  `;
  
  document.body.appendChild(alertDiv);
  
  setTimeout(() => {
    if (alertDiv && alertDiv.parentNode) {
      alertDiv.remove();
    }
  }, 5000);
}

window.showGameAlert = showGameAlert;
