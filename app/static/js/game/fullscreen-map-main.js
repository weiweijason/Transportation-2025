/**
 * 全螢幕地圖主要邏輯模組
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
      // 使用改進的提示函數
      showGameAlert(message, type);
    };
  }
  // 初始化地圖應用，使用map容器（與map.html同步）
  setTimeout(function() {
    if (typeof initApp === 'function') {
      console.log('使用 initApp 初始化地圖');
      initApp('map');
    } else if (typeof initializeMap === 'function') {
      console.log('使用 initializeMap 初始化地圖');
      initializeMap('map');
    } else {
      console.error('地圖初始化函數未找到');
      showGameAlert('地圖初始化函數未找到，請刷新頁面', 'error');
    }
    
    // 延遲初始化用戶位置
    setTimeout(function() {
      console.log('開始初始化用戶位置...');
      if (typeof window.updateUserLocation === 'function') {
        window.updateUserLocation().then(function(position) {
          console.log('用戶位置初始化成功:', position);
        }).catch(function(error) {
          console.warn('用戶位置初始化失敗，使用預設位置:', error);
          if (typeof window.addDefaultLocationMarker === 'function') {
            window.addDefaultLocationMarker();
          }
        });
      } else {
        console.warn('updateUserLocation 函數不存在，使用預設位置');
        if (typeof window.addDefaultLocationMarker === 'function') {
          window.addDefaultLocationMarker();
        }
      }
    }, 1000);
  }, 500); // 延遲初始化，確保所有腳本都已載入
    // 設置地圖容器ID為全螢幕地圖使用
  window.mapContainerId = 'map';
  
  // 修改現有的地圖初始化函數以支持自定義容器ID
  if (typeof window.initializeMap === 'function') {
    const originalInitializeMap = window.initializeMap;
    window.initializeMap = function() {
      console.log('使用全螢幕地圖容器初始化地圖...');
      showLoading();
      
      // 確認地圖容器存在
      const mapContainer = document.getElementById('map');
      if (!mapContainer) {
        console.error('找不到地圖容器元素 #map');
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
        // 創建全螢幕地圖
        createFullscreenMap();
      } catch (error) {
        console.error('初始化全螢幕地圖時發生錯誤:', error);
        hideLoading();
        showGameAlert('地圖初始化失敗，請檢查網絡連接並刷新頁面重試。', 'danger');
      }
    };
  }  // 創建全螢幕地圖的函數
  function createFullscreenMap() {
    console.log('創建全螢幕地圖實例');
    
    // 確保容器存在且可見 - 修正為正確的容器ID
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
      console.error('地圖容器不存在 - 查找容器ID: map');
      return;
    }
    
    // 確保容器有適當的尺寸
    if (mapContainer.offsetWidth === 0 || mapContainer.offsetHeight === 0) {
      console.warn('地圖容器尺寸為零，延遲初始化');
      setTimeout(() => createFullscreenMap(), 100);
      return;
    }
    
    try {
      // 安全地移除現有地圖實例
      if (window.gameMap && typeof window.gameMap.remove === 'function') {
        try {
          window.gameMap.remove();
        } catch (e) {
          console.warn('移除舊地圖實例時出錯:', e);
        }
      }
      if (window.busMap && typeof window.busMap.remove === 'function') {
        try {
          window.busMap.remove();        } catch (e) {
          console.warn('移除舊地圖實例時出錯:', e);
        }
      }
      
      // 創建新的地圖實例
      const map = L.map('map', {
        center: [25.0165, 121.5375],
        zoom: 16,
        maxZoom: 19,
        minZoom: 10,
        zoomControl: true,
        attributionControl: false
      });
      
      // 添加地圖圖層
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
      }).addTo(map);
      
      // 設置全局地圖變量
      window.gameMap = map;
      window.busMap = map;
      
      console.log('全螢幕地圖創建成功');
      
      // 初始化用戶位置
      if (typeof window.updateUserLocation === 'function') {
        window.updateUserLocation().then(() => {
          console.log('用戶位置初始化完成');
          updateLocationIndicator();
        }).catch((error) => {
          console.warn('初始定位失敗:', error);
        });
      }
      
      // 載入其他地圖功能（公車路線、精靈等）
      if (typeof window.loadBusRoutes === 'function') {
        setTimeout(() => {
          window.loadBusRoutes();
        }, 1000);
      }
      
      if (typeof window.loadCreatures === 'function') {
        setTimeout(() => {
          window.loadCreatures();
        }, 1500);
      }
      
      hideLoading();
      
    } catch (error) {
      console.error('創建全螢幕地圖失敗:', error);
      hideLoading();
      
      // 如果創建失敗，嘗試使用更強力的清理和重建
      if (error.message && error.message.includes('reused')) {
        showGameAlert('地圖容器衝突，正在強制重建...', 'warning');
        setTimeout(() => {
          if (typeof window.createDirectMap === 'function') {
            window.createDirectMap('map');
          } else {
            showGameAlert('地圖重建失敗，請刷新頁面', 'error');
          }
        }, 500);
      } else {
        showGameAlert('地圖創建失敗，請嘗試重新初始化', 'error');
      }
    }
  }
  
  // 修改busMap初始化以支持自定義容器
  if (typeof window.initApp === 'function') {
    const originalInitApp = window.initApp;
    window.initApp = function(containerId = 'map') {
      // 對於全螢幕模式，直接初始化地圖
      if (typeof window.initializeMap === 'function') {
        window.initializeMap(containerId);
      } else {
        originalInitApp(containerId);
      }
    };
  }
  
  // 設置地圖初始化
  setTimeout(function() {
    try {
      let targetMap = null;
      
      // 使用安全檢查函數
      if (window.isMapInstanceValid && window.isMapInstanceValid(window.gameMap)) {
        targetMap = window.gameMap;
      } else if (window.isMapInstanceValid && window.isMapInstanceValid(window.busMap)) {
        targetMap = window.busMap;
      }
      
      if (targetMap && window.safeSetMapView) {
        // 使用安全的 setView 函數
        const success = window.safeSetMapView(targetMap, [25.0165, 121.5375], 16);
        if (!success) {
          console.log('安全 setView 失敗，重新初始化地圖');
          throw new Error('地圖設置視圖失敗');
        }
      } else {
        // 如果還沒有地圖，嘗試初始化
        console.log('沒有有效的地圖實例，開始初始化...');        if (typeof window.initializeMap === 'function') {
          window.initializeMap('map');
        } else if (typeof window.initApp === 'function') {
          window.initApp('map');
        } else {
          console.error('找不到地圖初始化函數');
          showGameAlert('地圖初始化函數不存在，請刷新頁面', 'error');
        }
      }
    } catch (error) {
      console.error('設置地圖初始視圖時發生錯誤:', error);
      showGameAlert('地圖初始化過程中發生錯誤，正在重試...', 'warning');
      // 延遲重試
      setTimeout(function() {
        if (typeof window.initializeMap === 'function') {
          window.initializeMap('map');
        }
      }, 1000);
    }
  }, 1000);
  
  // 信息面板切換
  document.getElementById('infoToggleBtn').addEventListener('click', function() {
    const bottomInfo = document.getElementById('bottomInfo');
    bottomInfo.classList.toggle('show');
  });
  
  // 位置按鈕事件
  document.getElementById('goToCurrentLocationBtn').addEventListener('click', function() {
    if (window.userLocation) {
      try {
        let targetMap = null;
        
        // 使用安全檢查函數
        if (window.isMapInstanceValid && window.isMapInstanceValid(window.gameMap)) {
          targetMap = window.gameMap;
        } else if (window.isMapInstanceValid && window.isMapInstanceValid(window.busMap)) {
          targetMap = window.busMap;
        }
        
        if (targetMap && window.safeSetMapView) {
          // 使用安全的 setView 函數
          const success = window.safeSetMapView(targetMap, window.userLocation, 17);
          if (success) {
            updateLocationIndicator();
          } else {
            console.warn('安全 setView 失敗，嘗試重新初始化地圖');
            showGameAlert('定位失敗，正在重新初始化地圖...', 'warning');            if (typeof window.initializeMap === 'function') {
              window.initializeMap('map');
            }
          }
        } else {
          console.warn('沒有有效的地圖實例或安全函數，嘗試重新初始化');
          showGameAlert('地圖實例無效，正在重新初始化...', 'warning');
          if (typeof window.initializeMap === 'function') {
            window.initializeMap('map');
          }
        }
      } catch (error) {
        console.error('設置地圖視圖時發生錯誤:', error);
        showGameAlert('定位失敗，請嘗試重新初始化地圖', 'error');
        if (typeof window.initializeMap === 'function') {
          window.initializeMap('map');
        }
      }
    } else {
      showGameAlert('無法獲取當前位置，請嘗試重新定位', 'warning');
    }
  });
  
  // 重新定位按鈕
  document.getElementById('refreshLocationBtn').addEventListener('click', function() {
    console.log('重新定位按鈕被點擊');
    showGameAlert('正在重新獲取位置...', 'info');
    
    if (typeof window.updateUserLocation === 'function') {
      window.updateUserLocation().then(function(position) {
        console.log('重新定位成功:', position);
        updateLocationIndicator();
        showGameAlert('位置更新成功！', 'success');
      }).catch(function(error) {
        console.error('重新定位失敗:', error);
        showGameAlert('定位失敗：' + error.message, 'error');
        
        // 如果定位失敗，提供使用預設位置的選項
        if (confirm('定位失敗，是否使用預設位置（台北市中心）？')) {
          if (typeof window.addDefaultLocationMarker === 'function') {
            window.addDefaultLocationMarker();
            updateLocationIndicator();
            showGameAlert('已設置為預設位置', 'info');
          }
        }
      });
    } else {
      console.error('updateUserLocation 函數不存在');
      showGameAlert('位置更新功能不可用，請刷新頁面', 'error');
    }
  });
  
  // 重整地圖按鈕
  document.getElementById('initMapBtn').addEventListener('click', function() {
    showGameAlert('重新初始化地圖...', 'info');
      // 使用更強力的重新初始化
    try {
      if (typeof window.createDirectMap === 'function') {
        window.createDirectMap('map');
      } else if (typeof window.initializeMap === 'function') {
        window.initializeMap('map');
      } else {
        console.warn('找不到地圖初始化函數，重新整理頁面');
        location.reload();
      }
    } catch (error) {
      console.error('重新初始化地圖失敗:', error);
      showGameAlert('重新初始化失敗，請刷新頁面', 'error');
      setTimeout(() => location.reload(), 2000);
    }
  });
  
  // 更新位置指示器
  function updateLocationIndicator() {
    const locationIndicator = document.getElementById('locationIndicator');
    const locationText = document.getElementById('currentLocationText');
    
    if (window.userLocation) {
      const lat = window.userLocation.lat.toFixed(4);
      const lng = window.userLocation.lng.toFixed(4);
      locationText.textContent = `${lat}, ${lng}`;
      locationIndicator.classList.remove('d-none');
    } else {
      locationIndicator.classList.add('d-none');
    }
  }
  
  // 監聽位置更新
  if (typeof window.updateUserLocation === 'function') {
    const originalUpdateUserLocation = window.updateUserLocation;
    window.updateUserLocation = function() {
      return originalUpdateUserLocation().then(function(result) {
        updateLocationIndicator();
        return result;
      }).catch(function(error) {
        document.getElementById('locationIndicator').classList.add('d-none');
        throw error;
      });
    };
  }
  
  // 防止頁面滾動
  document.body.style.overflow = 'hidden';
  
  // 點擊空白處關閉信息面板
  document.addEventListener('click', function(e) {
    const bottomInfo = document.getElementById('bottomInfo');
    const infoToggleBtn = document.getElementById('infoToggleBtn');
    
    if (!bottomInfo.contains(e.target) && !infoToggleBtn.contains(e.target)) {
      bottomInfo.classList.remove('show');
    }
  });
  
  // 處理手機瀏覽器的地址欄自動隱藏
  function handleMobileViewport() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  }
  
  window.addEventListener('resize', handleMobileViewport);
  handleMobileViewport();
});

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
  }, 3000);
}
