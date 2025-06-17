/**
 * 精靈功能相關函數模組
 * 處理精靈顯示、捕捉和屬性判定等功能
 */

// 在地圖上顯示精靈的函數
function displayCreaturesOnMap(creatures) {
  if (!gameMap) {
    console.error('地圖未初始化');
    return;
  }
  
  // 清空所有現有標記（不依賴圖層）
  gameMap.eachLayer(layer => {
    if (layer instanceof L.Marker && layer._icon && layer._icon.classList.contains('spirit-marker')) {
      gameMap.removeLayer(layer);
    }
  });
  
  if (!creatures || creatures.length === 0) {
    console.log('沒有精靈可顯示');
    return;
  }
  
  // 獲取當前用戶 player_id（從全局變量或 localStorage 中獲取）
  const currentPlayerId = getCurrentPlayerId();
  console.log(`當前玩家ID: ${currentPlayerId}`);
  console.log(`嘗試在地圖上顯示 ${creatures.length} 隻精靈`);
  
  // 獲取當前時間
  const now = new Date().getTime() / 1000;
  
  // 存儲已創建的標記
  const createdMarkers = [];
  
  // 為每個精靈創建標記
  creatures.forEach((creature, index) => {
    // 檢查此精靈是否已被當前玩家捕獲
    const capturedPlayers = creature.captured_players || '';
    const playerList = capturedPlayers.split(',').filter(Boolean);
    
    if (playerList.includes(currentPlayerId)) {
      console.log(`精靈 ${creature.name} (ID: ${creature.id}) 已被當前玩家捕獲，不顯示`);
      return; // 跳過此精靈
    }
    
    // 獲取基本信息
    const position = creature.position || { lat: 25.033 + (Math.random() * 0.02), lng: 121.565 + (Math.random() * 0.02) };
    const name = creature.name || '未知精靈';
    const elementType = creature.element_type || 'normal';
    const species = creature.species || '一般種';
    const hp = creature.hp || 100;
    const attack = creature.attack || 10;
    
    // 計算剩餘時間
    let remainingTime = 0;
    if (creature.expires_at) {
      remainingTime = Math.max(0, Math.floor(creature.expires_at - now));
    }
    const minutes = Math.floor(remainingTime / 60);
    const seconds = remainingTime % 60;
    const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    // 根據元素類型獲取顏色
    let bgColor;    switch(elementType) {
      case 'fire': bgColor = '#e74c3c'; break;
      case 'water': bgColor = '#3498db'; break;
      case 'wood': bgColor = '#27ae60'; break;
      case 'light': bgColor = '#f1c40f'; break;
      case 'dark': bgColor = '#2c3e50'; break;
      case 'normal': bgColor = '#95a5a6'; break;
      default: bgColor = '#95a5a6';
    }
    
    // 獲取表情符號
    let emoji = getCreatureEmoji(elementType);
    
    // 創建醒目的圖標HTML（增加尺寸和邊框，添加動畫和脈衝效果）
    const iconHtml = `
      <div style="
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: ${bgColor};
        border: 5px solid yellow;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 0 20px rgba(255,255,0,0.8);
        color: white;
        font-weight: bold;
        font-size: 30px;
        position: relative;
        z-index: 2000;
        animation: pulse 1.5s infinite;
      ">
        ${emoji}
        <div style="
          position: absolute;
          bottom: -15px;
          left: 50%;
          transform: translateX(-50%);
          background-color: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 3px 10px;
          border-radius: 10px;
          font-size: 12px;
          white-space: nowrap;
          font-weight: bold;
          border: 2px solid yellow;
        ">${timeStr}</div>
      </div>
      <style>
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.1); }
          100% { transform: scale(1); }
        }
      </style>
    `;
    
    try {
      // 確保位置為有效數值
      const lat = parseFloat(position.lat);
      const lng = parseFloat(position.lng);
      
      if (isNaN(lat) || isNaN(lng)) {
        console.error(`精靈 ${name} 位置無效:`, position);
        return;
      }
      
      // 使用超高zIndex值來確保標記位於頂部
      const icon = L.divIcon({
        html: iconHtml,
        className: 'spirit-marker spirit-marker-' + index,
        iconSize: [60, 60],
        iconAnchor: [30, 30]
      });
      
      // 創建標記並設置極高zIndex
      const marker = L.marker([lat, lng], { 
        icon: icon,
        zIndexOffset: 9000 + index  // 極高的z-index確保顯示在最上層
      });
      
      // 首先把精靈標記直接添加到地圖，確保可見
      marker.addTo(gameMap);
      
      // 再次確認已添加到地圖
      if (window.creaturesLayer) {
        window.creaturesLayer.addLayer(marker);
      }
        // 添加彈出框
      marker.bindPopup(`
        <div class="text-center py-2">
          <h5 class="mb-2">${name}</h5>
          <p class="mb-3">
            <strong>攻擊:</strong> ${attack} | 
            <strong>生命:</strong> ${hp}
          </p>
          <button class="btn btn-success btn-sm w-100 catch-btn" onclick="catchCreature('${creature.id}')">
            <i class="fas fa-hand-sparkles me-1"></i>捕捉
          </button>
          <p class="mt-2 mb-0"><small>剩餘時間: ${timeStr}</small></p>
        </div>
      `);
      
      // 點擊事件
      marker.on('click', function() {
        marker.openPopup();
      });
      
      // 保存標記並添加到列表中
      creature.marker = marker;
      createdMarkers.push(marker);
      
      console.log(`第 ${index+1} 隻精靈 ${name} 標記已創建`);
    } catch (err) {
      console.error(`創建精靈 ${name} 標記時發生錯誤:`, err);
    }
  });
  
  console.log(`成功創建 ${createdMarkers.length} 個精靈標記`);
    // 如果有精靈，平移到第一個精靈的位置
  if (createdMarkers.length > 0 && creatures[0] && creatures[0].position) {
    const pos = creatures[0].position;
    console.log(`平移到第一個精靈位置:`, pos);
    
    // 使用安全的 setView 函數
    if (window.safeSetMapView && window.isMapInstanceValid && window.isMapInstanceValid(gameMap)) {
      const success = window.safeSetMapView(gameMap, [parseFloat(pos.lat), parseFloat(pos.lng)], 16);
      if (!success) {
        console.warn('無法安全地設置地圖視圖到精靈位置');
      }
    } else {
      // 備用方案：直接嘗試 setView，但包裝在 try-catch 中
      try {
        if (gameMap && gameMap.setView) {
          gameMap.setView([parseFloat(pos.lat), parseFloat(pos.lng)], 16);
        }
      } catch (error) {
        console.error('設置地圖視圖到精靈位置時發生錯誤:', error);
      }
    }
    
    // 添加大型閃爍圈圈指示器來標示精靈位置
    const animatedCircle = L.circleMarker([parseFloat(pos.lat), parseFloat(pos.lng)], {
      radius: 40,
      color: 'yellow',
      fillColor: 'rgba(255, 255, 0, 0.3)',
      weight: 5,
      opacity: 0.8,
      fillOpacity: 0.5,
      dashArray: '5, 10'
    }).addTo(gameMap);
    
    // 添加動畫效果
    let growing = true;
    let radius = 40;
    const pulseAnimation = setInterval(() => {
      if (growing) {
        radius += 2;
        if (radius >= 60) growing = false;
      } else {
        radius -= 2;
        if (radius <= 40) growing = true;
      }
      animatedCircle.setRadius(radius);
    }, 100);
    
    // 60秒後停止動畫
    setTimeout(() => {
      clearInterval(pulseAnimation);
      gameMap.removeLayer(animatedCircle);
    }, 60000);
  }
  
  // 強制刷新地圖
  gameMap.invalidateSize();
  
  // 向用戶顯示提示
  showGameAlert('精靈已出現在地圖上！請尋找黃色閃爍的標記。', 'success', 5000);
  
  // 返回創建的標記
  return createdMarkers;
}

// 獲取當前玩家ID的輔助函數
function getCurrentPlayerId() {
  // 從全局變量或localStorage中獲取
  if (window.currentUser && window.currentUser.player_id) {
    return window.currentUser.player_id;
  }
  
  // 嘗試從 localStorage 獲取
  const userDataStr = localStorage.getItem('currentUser');
  if (userDataStr) {
    try {
      const userData = JSON.parse(userDataStr);
      return userData.player_id || '';
    } catch (e) {
      console.error('解析用戶數據失敗:', e);
    }
  }
  
  // 如果無法獲取，返回空字符串
  return '';
}

// 捕捉精靈的函數
function catchCreature(creatureId) {
  // 查找點擊的精靈
  const creature = currentCreatures.find(c => c.id === creatureId);
  if (!creature) {
    console.error('找不到指定精靈:', creatureId);
    showGameAlert('這個精靈已經消失了，請尋找其他精靈。', 'warning');
    return;
  }
  
  // 檢查是否已經被捕獲
  const currentPlayerId = getCurrentPlayerId();
  const capturedPlayers = creature.captured_players || '';
  const playerList = capturedPlayers.split(',').filter(Boolean);
  
  if (playerList.includes(currentPlayerId)) {
    showGameAlert('你已經捕獲過這隻精靈了！', 'warning');
    return;
  }
  
  // 關閉當前的彈出框
  if (creature.marker && creature.marker.closePopup) {
    creature.marker.closePopup();
  }
  
  // 顯示加載中
  showLoading();
  
  // 導向互動捕捉頁面
  window.location.href = `/game/capture-interactive/${creatureId}`;
}

// 根據精靈類型獲取表情符號
function getCreatureEmoji(type) {
  switch(type) {
    case 'water': return '💧';
    case 'fire': return '🔥';
    case 'wood': return '🌱';
    case 'light': return '✨';
    case 'dark': return '🌙';
    case 'normal': return '⭐';
    default: return '⭐';
  }
}

// 獲取精靈默認圖片
function getDefaultCreatureImage(type, name) {
  const color = getTypeColor(type);
  return `https://placehold.co/200x200/${color}/white?text=${encodeURIComponent(name || '未知精靈')}`;
}

// 根據精靈類型獲取顏色
function getTypeColor(type) {
  switch(type) {
    case 'water': return '3498db';
    case 'fire': return 'e74c3c';
    case 'wood': return '27ae60';
    case 'light': return 'f1c40f';
    case 'dark': return '2c3e50';
    case 'normal': return '95a5a6';
    default: return '95a5a6';
  }
}

// 根據精靈類型獲取徽章類別
function getTypeBadgeClass(type) {
  switch(type) {
    case 'water': return 'bg-primary';
    case 'fire': return 'bg-danger';
    case 'wood': return 'bg-success';
    case 'light': return 'bg-warning';
    case 'dark': return 'bg-dark';
    case 'normal': return 'bg-secondary';
    default: return 'bg-secondary';
  }
}

// 根據稀有度獲取徽章類別
function getRarityBadgeClass(rarity) {
  switch(rarity) {
    case '一般種': return 'bg-secondary';
    case '罕見種': return 'bg-info';
    case '稀有種': return 'bg-primary';
    case '傳說種': return 'bg-danger';
    default: return 'bg-secondary';
  }
}

// 元素類型轉換為中文顯示
function getElementTypeName(type) {
  switch(type) {
    case 'fire': return '火系';
    case 'water': return '水系';
    case 'wood': return '草系';
    case 'light': return '光系';
    case 'dark': return '暗系';
    case 'normal': return '一般系';
    case 0: return '火系'; // 數字枚舉值 (FIRE = 0)
    case 1: return '水系'; // 數字枚舉值 (WATER = 1)
    case 2: return '草系'; // 數字枚舉值 (WOOD = 2)
    case 3: return '光系'; // 數字枚舉值 (LIGHT = 3)
    case 4: return '暗系'; // 數字枚舉值 (DARK = 4)
    case 5: return '一般系'; // 數字枚舉值 (NORMAL = 5)
    default: return '一般系';
  }
}

// 根據稀有度獲取 z-index 值
function getZIndexByRarity(rarity) {
  switch(rarity) {
    case '傳說種': return 1000;
    case '稀有種': return 900;
    case '罕見種': return 800;
    default: return 700;  // 一般種
  }
}

// 播放捕捉成功音效
function playCatchSound() {
  // 如果可以，這裡可以添加聲音效果
  console.log('播放捕捉成功音效');
}