/**
 * 精靈捕捉遊戲主要核心邏輯
 * 處理遊戲初始化、事件綁定和整體狀態管理
 */

// 全局變數 - 使用bus-route-map.js中的地圖
var arenaList = [];
var currentCreatures = [];
var capturedCreatures = 0;
var updateTimer = 30;
var updateInterval;
var dataSourceToggle = true; // true 表示從Firebase獲取，false 表示從CSV獲取
var creatureUpdateInterval = 15000; // 15秒更新一次，實現交替更新
var firebaseListener = null; // 用於存儲Firebase監聽器的引用
var lastDataSourceUpdateTime = 0; // 上次資料來源更新時間

// DOM載入完成後初始化遊戲
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM內容載入完成');
  
  // 不再初始化新地圖，而是檢查bus-route-map.js是否已初始化地圖
  setTimeout(checkMapInitialized, 500);
  
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
    checkMapInitialized();
    setTimeout(hideLoading, 1000);
  });
  
  // 處理頁籤切換事件，確保地圖正確渲染
  const mapTab = document.getElementById('map-tab');
  if (mapTab) {
    mapTab.addEventListener('shown.bs.tab', function() {
      console.log('地圖頁籤被啟用');
      if (window.busMap) {
        console.log('調整地圖大小');
        window.busMap.invalidateSize();
      } else {
        console.log('地圖未初始化，嘗試初始化');
        checkMapInitialized();
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
  
  // 頁面關閉時清除Firebase監聽器
  window.addEventListener('beforeunload', function() {
    if (firebaseListener) {
      console.log('清除Firebase監聽器');
      firebaseListener();
      firebaseListener = null;
    }
  });
});

// 檢查地圖是否已初始化
function checkMapInitialized(callback) {
  console.log('檢查地圖初始化狀態...');

  // 等待bus-route-map.js初始化的全局地圖
  if (window.busMap) {
    console.log('地圖已存在，使用現有地圖');
    // 確保地圖大小正確
    window.busMap.invalidateSize();

    // 如果提供了回調函數，執行它
    if (typeof callback === 'function') {
      callback();
    }
  } else {
    console.log('地圖尚未初始化，等待...');
    // 如果地圖尚未初始化，等待並重試
    setTimeout(() => checkMapInitialized(callback), 1000);
  }
}

// 開始精靈更新倒計時
function startUpdateCountdown() {
  updateTimer = 30;
  
  // 安全檢查 DOM 元素是否存在
  const updateCountdownEl = document.getElementById('updateCountdown');
  const updateIndicatorEl = document.getElementById('updateIndicator');
  
  if (updateCountdownEl) {
    updateCountdownEl.textContent = updateTimer;
  } else {
    console.warn('updateCountdown 元素不存在，跳過倒計時顯示');
  }
  
  if (updateIndicatorEl) {
    updateIndicatorEl.style.display = 'block';
  } else {
    console.warn('updateIndicator 元素不存在，跳過指示器顯示');
  }
  
  if (updateInterval) {
    clearInterval(updateInterval);
  }    updateInterval = setInterval(function() {
    updateTimer--;
    
    // 安全更新倒計時顯示
    const updateCountdownEl = document.getElementById('updateCountdown');
    if (updateCountdownEl) {
      updateCountdownEl.textContent = updateTimer;
    }
    
    if (updateTimer <= 0) {
      // 時間到，使用新的綜合更新函數
      updateAllGameData();
      // 重置計時器
      updateTimer = 30;
    }
  }, 1000);
}

// 修改更新邏輯，統一從CSV獲取資料
function fetchCreatures() {
  console.log('從CSV獲取精靈資料...');
  showLoading();

  // 調用API從CSV獲取精靈資料
  fetch('/game/api/route-creatures/get-from-csv')
    .then(response => {
      if (!response.ok) {
        throw new Error('從CSV獲取精靈失敗');
      }
      return response.json();
    })
    .then(data => {
      hideLoading();
      console.log('從CSV獲取到的精靈:', data);

      if (data.success) {
        // 清除現有精靊標記
        clearExistingCreatureMarkers();

        // 更新精靈列表
        currentCreatures = data.creatures || [];

        // 在地圖上顯示精靈
        displayCreaturesDirectly(currentCreatures);

        // 顯示提示
        showGameAlert(`已從CSV更新 ${currentCreatures.length} 隻精靈！`, 'info', 3000);
      } else {
        console.error('從CSV獲取精靈返回失敗:', data.message);
        showGameAlert(data.message || '獲取精靈資訊失敗!', 'warning');
      }
    })
    .catch(error => {
      hideLoading();
      console.error('從CSV獲取精靈錯誤:', error);
      showGameAlert('無法讀取CSV資料，請稍後再試！', 'danger');
    });
}

// 新增：綜合更新函數 - 同時更新精靈、公車位置和用戶位置
function updateAllGameData() {
  console.log('開始綜合更新：精靈、公車位置和用戶位置...');
  
  // 顯示載入提示
  showLoading();
  
  // 1. 更新精靈數據
  fetch('/game/api/route-creatures/get-from-csv')
    .then(response => {
      if (!response.ok) {
        throw new Error('從CSV獲取精靈失敗');
      }
      return response.json();
    })
    .then(data => {
      console.log('精靈數據更新完成');
      
      if (data.success) {
        // 清除現有精靊標記
        clearExistingCreatureMarkers();
        
        // 更新精靈列表
        currentCreatures = data.creatures || [];
        
        // 在地圖上顯示精靈
        displayCreaturesDirectly(currentCreatures);
      }
      
      // 2. 更新公車位置（如果公車位置功能可用）
      if (typeof window.updateBusPositions === 'function') {
        console.log('更新公車位置...');
        return window.updateBusPositions();
      } else {
        console.warn('公車位置更新功能不可用');
        return Promise.resolve();
      }
    })
    .then(() => {
      // 3. 更新用戶位置（如果定位功能可用）
      console.log('更新用戶位置...');
      if (typeof window.updateUserLocation === 'function') {
        return window.updateUserLocation();
      } else {
        console.warn('用戶位置更新功能不可用');
        return Promise.resolve();
      }
    })
    .then(() => {
      hideLoading();
      console.log('所有數據更新完成');
      
      // 統計更新結果
      const creatureCount = currentCreatures ? currentCreatures.length : 0;
      showGameAlert(`數據已更新！精靈: ${creatureCount} 隻，公車和位置已同步`, 'success', 3000);
    })
    .catch(error => {
      hideLoading();
      console.error('綜合更新失敗:', error);
      
      // 如果是精靈更新失敗，仍然嘗試更新公車位置和用戶位置
      if (typeof window.updateBusPositions === 'function') {
        window.updateBusPositions().catch(busError => {
          console.error('公車位置更新也失敗:', busError);
        });
      }
      
      if (typeof window.updateUserLocation === 'function') {
        window.updateUserLocation().catch(locationError => {
          console.error('用戶位置更新也失敗:', locationError);
        });
      }
      
      showGameAlert('部分數據更新失敗，請稍後再試', 'warning');
    });
}

// 初始化時調用綜合更新函數，包含公車位置
checkMapInitialized(function() {
  console.log('地圖已就緒，執行初始化更新...');
  
  // 等待一段時間確保所有模組已載入
  setTimeout(() => {
    // 初始化公車位置圖層（如果尚未初始化）
    if (typeof window.initBusPositionLayer === 'function' && !window.busPositionLayer) {
      const map = window.gameMap || window.busMap;
      if (map) {
        console.log('初始化公車位置圖層...');
        window.initBusPositionLayer(map);
      }
    }
    
    // 執行綜合初始化更新
    updateAllGameData();
    
    // 開始定期更新倒計時
    startUpdateCountdown();
  }, 1000);
});

// 獲取路線上的精靈
function fetchRouteCreatures() {
  console.log('獲取路線上的精靈...');
  
  // 安全隱藏更新指示器
  const updateIndicatorEl = document.getElementById('updateIndicator');
  if (updateIndicatorEl) {
    updateIndicatorEl.style.display = 'none';
  }
  
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
        // 確保清除現有精靈標記
        clearExistingCreatureMarkers();
        
        // 更新精靈列表
        currentCreatures = data.creatures || [];
        
        // 輸出精靊數量和資料結構，方便調試
        console.log(`收到 ${currentCreatures.length} 隻精靈`);
        if (currentCreatures.length > 0) {
          console.log('第一個精靈資料:', JSON.stringify(currentCreatures[0]));
        }
        
        // 只有在真的有精靈數據時才顯示
        if (currentCreatures.length > 0) {
          // 在地圖上顯示精靈 - 直接使用新的渲染方法
          displayCreaturesDirectly(currentCreatures);
          
          // 設置Firebase監聽，監聽精靈刪除事件
          setupFirebaseListener();
        } else {
          console.log('沒有可顯示的精靊');
          showGameAlert('當前沒有可捕捉的精靈，請稍後再來！', 'info');
        }
        
        // 重新開始倒計時
        startUpdateCountdown();
      } else {
        console.error('獲取精靈返回失敗:', data.message);
        showGameAlert(data.message || '獲取精靊資訊失敗!', 'warning');
      }
    })
    .catch(error => {
      console.error('獲取精靈錯誤:', error);
      showGameAlert('無法連接到伺服器，請稍後再試！', 'danger');
      
      // 發生錯誤時也重新開始倒計時
      startUpdateCountdown();
    });
}

// 清除地圖上現有的所有精靈標記
function clearExistingCreatureMarkers() {
  console.log('清除地圖上所有現有的精靈標記');

  // 如果有專門的圖層用於存放精靈標記，清空該圖層
  if (window.creaturesLayer) {
    console.log('清空 creaturesLayer 圖層');
    window.creaturesLayer.clearLayers();
  }

  // 如果沒有專門的圖層，遍歷地圖上的所有圖層，移除精靈標記
  if (window.busMap) {
    console.log('遍歷地圖圖層，移除精靈標記');
    const layersToRemove = [];
    window.busMap.eachLayer(layer => {
      if (layer instanceof L.Marker && layer._icon) {
        const className = layer._icon.className || '';
        if (className.includes('creature-circle-marker')) {
          console.log('標記為移除的精靈標記');
          layersToRemove.push(layer);
        }
      }
    });

    // 從地圖中移除標記
    layersToRemove.forEach(layer => {
      window.busMap.removeLayer(layer);
    });
  }

  // 清空全局精靈標記數組
  if (window.creatureMarkers) {
    console.log('清空全局精靊標記數組');
    window.creatureMarkers.forEach(marker => {
      if (window.busMap && window.busMap.hasLayer(marker)) {
        window.busMap.removeLayer(marker);
      }
    });
    window.creatureMarkers = [];
  }
}

// 直接在地圖上顯示精靈 (不依賴任何圖層)
function displayCreaturesDirectly(creatures) {
  if (!window.busMap) {
    console.error('地圖未初始化，無法顯示精靈');
    return;
  }
  
  console.log(`嘗試直接在地圖上顯示 ${creatures.length} 隻精靈`);
  
  if (!creatures || creatures.length === 0) {
    console.log('沒有精靈可以顯示');
    return;
  }
  
  // 為每個精靈創建小圓點標記
  creatures.forEach((creature, index) => {
    try {
      // 獲取基本信息並輸出位置信息以便調試
      console.log(`精靈 ${index+1} 位置資料:`, JSON.stringify(creature.position));
      
      const position = creature.position || { lat: 25.033 + (Math.random() * 0.02), lng: 121.565 + (Math.random() * 0.02) };
      const name = creature.name || '未知精靈';
      
      // 輸出位置數據進行調試
      console.log(`精靈 ${name} 的位置: lat=${position.lat}, lng=${position.lng}`);
      
      // 確保位置為有效數值
      const lat = parseFloat(position.lat);
      const lng = parseFloat(position.lng);
      
      if (isNaN(lat) || isNaN(lng)) {
        console.error(`精靈 ${name} 位置無效:`, position);
        return;
      }      // 獲取元素類型對應的顏色
      let color = '#FF0000'; // 預設紅色
      if (creature.element_type) {
        switch(creature.element_type) {
          case 'fire': color = '#e74c3c'; break;    // 火紅色
          case 'water': color = '#3498db'; break;   // 水藍色
          case 'wood': color = '#27ae60'; break;    // 草綠色
          case 'light': color = '#f1c40f'; break;   // 光金色
          case 'dark': color = '#2c3e50'; break;    // 暗黑色
          case 'normal': color = '#95a5a6'; break;  // 一般灰色
          case 'electric': color = '#f1c40f'; break; // 電黃色
          default: color = '#95a5a6';              // 一般灰色
        }
      }
      
      // 創建小圓點標記 - 修改為更小的圓點
      const circleMarker = L.circleMarker([lat, lng], {
        radius: 10,                 // 小圓點大小從20減為10
        color: '#000000',           // 邊框顏色
        fillColor: color,           // 填充顏色
        fillOpacity: 0.9,           // 填充不透明度
        weight: 2,                  // 邊框寬度從3減為2
        className: 'creature-circle-marker-' + index
      });
      
      // 直接添加到地圖
      circleMarker.addTo(window.busMap);
      console.log(`精靈小圓點已添加: ${name} 在 [${lat}, ${lng}]`);
      
      // 保存標記引用 - 同時保存到circle_marker和direct_marker屬性中
      creature.circle_marker = circleMarker;
      creature.direct_marker = circleMarker; // 確保在捕獲時能夠正確找到
      
      // 添加點擊事件處理
      circleMarker.on('click', function() {
        console.log(`點擊了精靈 ${name}`);
        showGameAlert(`你發現了 ${name}！點擊捕捉按鈕來捕捉它。`, 'success');
          // 顯示精靈信息
        circleMarker.bindPopup(`
          <div class="text-center py-2">
            <h5 class="mb-2">${name}</h5>
            <button class="btn btn-success btn-sm w-100 catch-btn" onclick="catchCreature('${creature.id}')">
              <i class="fas fa-hand-sparkles me-1"></i>捕捉
            </button>
          </div>
        `).openPopup();
      });
      
      // 將標記添加到全局window對象，以便調試
      if (!window.creatureMarkers) {
        window.creatureMarkers = [];
      }
      window.creatureMarkers.push(circleMarker);
      
      console.log(`成功創建精靈標記: ${name}`);
    } catch (err) {
      console.error(`創建精靈標記時發生錯誤:`, err);
    }
  });
  
  // 強制刷新地圖
  window.busMap.invalidateSize();
  
  // 顯示提示
  showGameAlert(`已在地圖上顯示 ${creatures.length} 隻精靈！尋找彩色小圓點。`, 'success', 8000);
}

// 添加一個明顯的測試標記，用於驗證地圖是否正常工作
function addTestMarker() {
  // 此功能已被禁用
  console.log('測試標記功能已禁用');
  return null;
}

// 顯示遊戲提示
function showGameAlert(message, type = 'info', duration = 5000) {
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
  }, duration);
}

// 捕捉精靈函數 - 為全局作用域添加此函數
window.catchCreature = function(creatureId) {
  console.log(`嘗試捕捉精靈，ID: ${creatureId}`);
  
  // 查找點擊的精靈
  const creature = currentCreatures.find(c => c.id === creatureId);
  if (!creature) {
    console.error('找不到指定精靊:', creatureId);
    showGameAlert('這個精靈已經消失了，請尋找其他精靈。', 'warning');
    return;
  }
  
  // 關閉當前的彈出框
  if (creature.direct_marker && creature.direct_marker.closePopup) {
    creature.direct_marker.closePopup();
  }
  
  // 顯示加載中
  showLoading();
  
  // 導向互動捕捉頁面
  window.location.href = `/game/capture-interactive/${creatureId}`;
};

// 初始化捕捉模態框動畫
function initCatchModal() {
  const modal = document.getElementById('catchSuccessModal');
  if (modal) {
    modal.addEventListener('shown.bs.modal', function() {
      animateSparkles();
    });
  }
}

// 動畫效果 - 閃爍
function animateSparkles() {
  const sparkles = document.querySelectorAll('.catch-sparkle');
  sparkles.forEach((sparkle, index) => {
    setTimeout(() => {
      sparkle.classList.add('animate-sparkle');
    }, index * 200);
  });
}

// 顯示載入中遮罩
function showLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) {
    overlay.style.visibility = 'visible';
  }
}

// 隱藏載入中遮罩
function hideLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) {
    overlay.style.visibility = 'hidden';
  }
}

// 當發生錯誤時，在控制台輸出錯誤信息
window.onerror = function(message, source, lineno, colno, error) {
  // 過濾掉 "Script error." 這種無用的錯誤
  if (message === 'Script error.' && !source && !lineno && !colno) {
    console.debug('跨域腳本錯誤，忽略');
    return true; // 阻止默認錯誤處理
  }
  
  console.error('全局錯誤:', message, 'at', source, lineno, colno);
  
  // 如果有詳細錯誤對象，記錄堆棧
  if (error) {
    console.error('錯誤堆棧:', error.stack);
  }
  
  hideLoading();
  return false;
};

// 添加未處理的 Promise 拒絕處理
window.addEventListener('unhandledrejection', function(event) {
  console.error('未處理的 Promise 拒絕:', event.reason);
  hideLoading();
});