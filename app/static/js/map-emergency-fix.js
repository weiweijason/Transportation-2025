// Leaflet地圖緊急修復版本 - 修復拖動問題
document.addEventListener('DOMContentLoaded', function() {
  console.log("緊急修復: DOM內容載入完成");
  
  // 等待一小段時間確保頁面渲染完成
  setTimeout(setupMapFix, 800);
});

// 設置地圖修復邏輯
function setupMapFix() {
  // 綁定重整地圖按鈕
  const initMapBtn = document.getElementById('initMapBtn');
  if (initMapBtn) {
    initMapBtn.addEventListener('click', function() {
      console.log('緊急修復：點擊了重整地圖按鈕');
      showDragFixAlert();
      fixMapDragging();
    });
  }
  
  // 監聽地圖頁籤激活事件
  const mapTab = document.getElementById('map-tab');
  if (mapTab) {
    mapTab.addEventListener('shown.bs.tab', function() {
      console.log('緊急修復：地圖頁籤被激活');
      setTimeout(function() {
        if (window.gameMap) {
          window.gameMap.invalidateSize();
        }
      }, 200);
    });
  }
  
  // 初始化後立即嘗試修復拖動
  setTimeout(fixMapDragging, 1500);
  
  // 如果1.5秒後仍有問題，再次嘗試修復
  setTimeout(function() {
    try {
      if (window.gameMap && window.gameMap._container) {
        console.log("緊急修復: 二次嘗試修復拖動");
        forceDraggingFix(window.gameMap);
      }
    } catch (e) {
      console.warn("二次修復嘗試失敗", e);
    }
  }, 3000);
}

// 主要拖動修復函數
function fixMapDragging() {
  console.log('緊急修復：嘗試修復地圖拖動問題');
  
  // 檢查是否有可用的地圖實例
  const mapInstance = window.gameMap || window.busMap || window.testMap;
  if (!mapInstance) {
    console.warn('緊急修復：找不到地圖實例，無法修復拖動');
    return;
  }
  
  try {
    // 強制重設拖動處理程序
    forceDraggingFix(mapInstance);
    
    console.log('緊急修復：拖動修復完成');
  } catch (e) {
    console.error('緊急修復：拖動修復失敗', e);
  }
}

// 強制修復拖動功能
function forceDraggingFix(map) {
  if (!map) return;
  
  try {
    // 嘗試禁用再啟用拖動功能
    if (map.dragging) {
      map.dragging.disable();
      
      // 短暫延遲後重新啟用
      setTimeout(function() {
        map.dragging.enable();
        console.log('緊急修復：已重新啟用拖動功能');
      }, 100);
    }
    
    // 檢查並修復地圖容器
    fixMapContainer(map);
    
    // 重設地圖視圖
    setTimeout(function() {
      try {
        map.invalidateSize(true);
        
        // 嘗試移動視圖以觸發重新渲染
        const currentCenter = map.getCenter();
        map.panTo([currentCenter.lat, currentCenter.lng]);
      } catch (e) {
        console.warn('緊急修復：視圖重設失敗', e);
      }
    }, 200);
  } catch (e) {
    console.error('緊急修復：拖動修復過程錯誤', e);
  }
}

// 修復地圖容器問題
function fixMapContainer(map) {
  // 確保地圖容器存在並有正確的樣式
  if (map && map._container) {
    const container = map._container;
    
    // 強制設置關鍵樣式
    container.style.position = 'relative';
    container.style.outline = 'none';
    container.style.touchAction = 'none';
    container.style.msTouchAction = 'none';
    container.style.userSelect = 'none';
    container.style.msUserSelect = 'none';
    container.style.webkitUserSelect = 'none';
    container.style.MozUserSelect = 'none';
    
    // 確保容器有正確的尺寸
    if (container.clientWidth === 0 || container.clientHeight === 0) {
      container.style.width = '100%';
      container.style.height = '500px';
    }
    
    // 為容器添加觸摸事件處理
    container.addEventListener('touchstart', function(e) {
      if (e.touches.length === 1) {
        e.stopPropagation();
      }
    }, { passive: false });
    
    // 禁止容器上的右鍵菜單，避免干擾拖動
    container.addEventListener('contextmenu', function(e) {
      e.preventDefault();
    });
    
    console.log('緊急修復：地圖容器樣式已修復');
  } else {
    console.warn('緊急修復：找不到地圖容器元素');
  }
}

// 顯示拖動修復提示
function showDragFixAlert() {
  try {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
      <strong>地圖拖動已修復!</strong> 請嘗試拖動地圖。如果仍然無法拖動，請重新整理頁面。
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 找到適合插入提示的位置
    const mapElement = document.getElementById('map');
    if (mapElement && mapElement.parentNode) {
      mapElement.parentNode.insertBefore(alertDiv, mapElement.nextSibling);
      
      // 5秒後自動消失
      setTimeout(function() {
        alertDiv.classList.remove('show');
        setTimeout(function() {
          alertDiv.remove();
        }, 500);
      }, 5000);
    }
  } catch (e) {
    console.warn('緊急修復：無法顯示提示', e);
  }
}

// 執行初始修復
setTimeout(function() {
  console.log("緊急修復: 啟動自動修復");
  fixMapDragging();
}, 2500);