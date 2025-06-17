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

// 初始化地圖功能
function initializeMapFeatures() {
  console.log('初始化地圖功能...');
  
  // 初始化用戶位置
  if (typeof window.updateUserLocation === 'function') {
    setTimeout(() => {
      window.updateUserLocation().then(() => {
        console.log('用戶位置初始化完成');
      }).catch((error) => {
        console.warn('初始定位失敗:', error);
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

// 按鈕事件處理
document.addEventListener('DOMContentLoaded', function() {
  // 重新初始化地圖按鈕
  const initMapBtn = document.getElementById('initMapBtn');
  if (initMapBtn) {
    initMapBtn.addEventListener('click', function() {
      console.log('用戶要求重新初始化地圖');
      initializeFullscreenMap();
    });
  }
});

// 暴露函數到全局
window.initializeFullscreenMap = initializeFullscreenMap;
window.createNewMap = createNewMap;
window.cleanMapContainer = cleanMapContainer;

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
