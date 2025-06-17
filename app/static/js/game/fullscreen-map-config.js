/**
 * 全螢幕地圖配置模組
 * 處理全螢幕地圖的初始化和特殊設置
 */

// 為全螢幕地圖設置特殊的地圖容器ID
window.MAP_CONTAINER_ID = 'fullscreen-map';
window.isFullscreenMode = true;

// 重寫地圖初始化函數
window.initializeMapForFullscreen = function() {
  console.log('全螢幕模式地圖初始化...');
  
  const mapContainer = document.getElementById('fullscreen-map');
  if (!mapContainer) {
    console.error('找不到全螢幕地圖容器');
    return;
  }
  
  if (typeof L === 'undefined') {
    console.error('Leaflet 庫未載入');
    return;
  }
  
  try {
    // 移除現有地圖實例
    if (window.gameMap && typeof window.gameMap.remove === 'function') {
      window.gameMap.remove();
    }
    if (window.busMap && typeof window.busMap.remove === 'function') {
      window.busMap.remove();
    }
    
    // 創建新地圖
    const map = L.map('fullscreen-map', {
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
    
    // 設置全局變量
    window.gameMap = map;
    window.busMap = map;
    
    console.log('全螢幕地圖創建成功');
    
    // 隱藏載入指示器
    const loading = document.getElementById('loadingOverlay');
    if (loading) {
      loading.style.display = 'none';
    }
    
    return map;
    
  } catch (error) {
    console.error('全螢幕地圖創建失敗:', error);
  }
};
