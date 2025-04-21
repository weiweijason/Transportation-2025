/**
 * 精靈捕捉遊戲主要核心邏輯
 * 處理遊戲初始化、事件綁定和整體狀態管理
 */

// 全局變數
var gameMap;
var arenaList = [];
var currentCreatures = [];
var capturedCreatures = 0;
var updateTimer = 30;
var updateInterval;
var creatureUpdateInterval = 30000; // 30秒更新一次

// DOM載入完成後初始化遊戲
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM內容載入完成');
  
  // 初始化地圖 (使用一個延遲確保DOM完全渲染)
  setTimeout(initializeMap, 500);
  
  // 綁定更新位置按鈕
  document.getElementById('refreshLocationBtn').addEventListener('click', function() {
    console.log('點擊了重新定位按鈕');
    showLoading();
    if (typeof updateUserLocation === 'function') {
      updateUserLocation().then(() => {
        hideLoading();
      }).catch(() => {
        hideLoading();
        showGameAlert('無法獲取您的位置，請確保已授予位置權限。', 'warning');
      });
    } else {
      console.error('updateUserLocation 函數不存在');
      hideLoading();
    }
  });
  
  // 綁定重新載入地圖按鈕
  document.getElementById('initMapBtn').addEventListener('click', function() {
    console.log('點擊了重新載入地圖按鈕');
    showLoading();
    initializeMap();
    setTimeout(hideLoading, 1000);
  });
  
  // 處理頁籤切換事件，確保地圖正確渲染
  const mapTab = document.getElementById('map-tab');
  if (mapTab) {
    mapTab.addEventListener('shown.bs.tab', function() {
      console.log('地圖頁籤被啟用');
      if (gameMap) {
        console.log('調整地圖大小');
        gameMap.invalidateSize();
      } else {
        console.log('地圖未初始化，嘗試初始化');
        initializeMap();
      }
    });
  }
  
  // 更新擂台列表當擂台標籤被點擊時
  const arenasTab = document.getElementById('arenas-tab');
  if (arenasTab) {
    arenasTab.addEventListener('shown.bs.tab', function() {
      console.log('擂台頁籤被啟用');
      fetchArenasInfo();
    });
  }
  
  // 初始化捕捉模態框動畫效果
  initCatchModal();
  
  // 初始化倒計時更新
  startUpdateCountdown();
});

// 開始精靈更新倒計時
function startUpdateCountdown() {
  updateTimer = 30;
  document.getElementById('updateCountdown').textContent = updateTimer;
  document.getElementById('updateIndicator').style.display = 'block';
  
  if (updateInterval) {
    clearInterval(updateInterval);
  }
  
  updateInterval = setInterval(function() {
    updateTimer--;
    document.getElementById('updateCountdown').textContent = updateTimer;
    
    if (updateTimer <= 0) {
      // 時間到，更新精靈
      fetchRouteCreatures();
      // 重置計時器
      updateTimer = 30;
    }
  }, 1000);
}

// 隨機展示測試標記
function addTestMarker() {
  if (!gameMap) return;
  
  // 創建超醒目測試標記（紅色大標記）
  const testMarker = L.marker([25.033, 121.565], {
    icon: L.divIcon({
      html: `<div style="
        width: 60px; 
        height: 60px; 
        background-color: red; 
        border: 4px solid white;
        border-radius: 50%; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        color: white; 
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
      ">測試</div>`,
      className: 'test-marker',
      iconSize: [60, 60],
      iconAnchor: [30, 30]
    })
  }).addTo(gameMap);
  
  console.log('超醒目測試標記已添加');
}

// 獲取路線上的精靈
function fetchRouteCreatures() {
  console.log('獲取路線上的精靈...');
  document.getElementById('updateIndicator').style.display = 'none';
  
  // 調用API獲取所有路線上的精靈
  fetch('/game/api/route-creatures/get-all')
    .then(response => {
      if (!response.ok) {
        throw new Error('獲取精靈失敗');
      }
      return response.json();
    })
    .then(data => {
      console.log('獲取到的精靈:', data);
      
      if (data.success) {
        // 清除當前地圖上的精靈
        if (window.creaturesLayer) {
          window.creaturesLayer.clearLayers();
        }
        
        // 更新精靈列表
        currentCreatures = data.creatures;
        
        // 在地圖上顯示精靈
        displayCreaturesOnMap(currentCreatures);
        
        // 重新開始倒計時
        startUpdateCountdown();
      } else {
        console.error('獲取精靈返回失敗:', data.message);
        showGameAlert(data.message || '獲取精靈資訊失敗!', 'warning');
      }
    })
    .catch(error => {
      console.error('獲取精靈錯誤:', error);
      showGameAlert('無法連接到伺服器，請稍後再試！', 'danger');
      
      // 發生錯誤時也重新開始倒計時
      startUpdateCountdown();
    });
}

// 顯示遊戲提示
function showGameAlert(message, type = 'info') {
  const alertContainer = document.createElement('div');
  alertContainer.className = `alert alert-${type} alert-dismissible fade show game-alert position-fixed`;
  alertContainer.style.top = '80px';
  alertContainer.style.right = '20px';
  alertContainer.style.zIndex = '9999';
  alertContainer.style.maxWidth = '300px';
  alertContainer.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
  
  alertContainer.innerHTML = `
    <div class="d-flex">
      <div class="me-3">
        <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
      </div>
      <div>${message}</div>
    </div>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  document.body.appendChild(alertContainer);
  
  // 自動消失
  setTimeout(() => {
    const bsAlert = new bootstrap.Alert(alertContainer);
    bsAlert.close();
  }, 5000);
}

// 初始化捕捉模態框動畫
function initCatchModal() {
  const modal = document.getElementById('catchSuccessModal');
  if (modal) {
    modal.addEventListener('shown.bs.modal', function() {
      animateSparkles();
    });
  }
}

// 顯示載入中遮罩
function showLoading() {
  document.getElementById('loadingOverlay').style.visibility = 'visible';
}

// 隱藏載入中遮罩
function hideLoading() {
  document.getElementById('loadingOverlay').style.visibility = 'hidden';
}

// 當發生錯誤時，在控制台輸出錯誤信息
window.onerror = function(message, source, lineno, colno, error) {
  console.error('全局錯誤:', message, 'at', source, lineno, colno);
  hideLoading();
  return false;
};