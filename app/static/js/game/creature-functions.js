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
  
  console.log(`嘗試在地圖上顯示 ${creatures.length} 隻精靈`);
  
  // 獲取當前時間
  const now = new Date().getTime() / 1000;
  
  // 存儲已創建的標記
  const createdMarkers = [];
  
  // 為每個精靈創建標記
  creatures.forEach((creature, index) => {
    // 獲取基本信息
    const position = creature.position || { lat: 25.033 + (Math.random() * 0.02), lng: 121.565 + (Math.random() * 0.02) };
    const name = creature.name || '未知精靈';
    const elementType = creature.element_type || 'normal';
    const species = creature.species || '一般種';
    
    // 計算剩餘時間
    let remainingTime = 0;
    if (creature.expires_at) {
      remainingTime = Math.max(0, Math.floor(creature.expires_at - now));
    }
    const minutes = Math.floor(remainingTime / 60);
    const seconds = remainingTime % 60;
    const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    // 根據元素類型獲取顏色
    let bgColor;
    switch(elementType) {
      case 'fire': bgColor = '#e74c3c'; break;
      case 'water': bgColor = '#3498db'; break;
      case 'earth': bgColor = '#8e44ad'; break;
      case 'air': bgColor = '#2ecc71'; break;
      case 'electric': bgColor = '#f1c40f'; break;
      default: bgColor = '#95a5a6';
    }
    
    // 獲取表情符號
    let emoji = getCreatureEmoji(elementType);
    
    // 創建醒目的圖標HTML（增加尺寸和邊框）
    const iconHtml = `
      <div style="
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: ${bgColor};
        border: 3px solid white;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 0 10px rgba(0,0,0,0.7);
        color: white;
        font-weight: bold;
        font-size: 22px;
        position: relative;
        z-index: 1000;
      ">
        ${emoji}
        <div style="
          position: absolute;
          bottom: -15px;
          left: 50%;
          transform: translateX(-50%);
          background-color: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 2px 8px;
          border-radius: 10px;
          font-size: 11px;
          white-space: nowrap;
          font-weight: normal;
          border: 1px solid white;
        ">${timeStr}</div>
      </div>
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
        iconSize: [50, 50],
        iconAnchor: [25, 25]
      });
      
      // 創建標記並設置高zIndex
      const marker = L.marker([lat, lng], { 
        icon: icon,
        zIndexOffset: 1000 + index  // 確保高於其他地圖元素
      });
      
      // 直接添加到地圖
      marker.addTo(gameMap);
      
      // 添加彈出框
      marker.bindPopup(`
        <div class="text-center py-2">
          <h5 class="mb-2">${name}</h5>
          <p class="mb-2">
            <span class="badge ${getTypeBadgeClass(elementType)}">${getElementTypeName(elementType)}</span>
            <span class="badge ${getRarityBadgeClass(species)}">${species}</span>
          </p>
          <p class="mb-3">
            <strong>力量:</strong> ${creature.power || 10} | 
            <strong>防禦:</strong> ${creature.defense || 10} | 
            <strong>生命:</strong> ${creature.hp || 100}
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
    gameMap.setView([parseFloat(pos.lat), parseFloat(pos.lng)], 16);
    
    // 額外確認：在標記附近添加一個大型指示器
    L.circleMarker([parseFloat(pos.lat), parseFloat(pos.lng)], {
      radius: 30,
      color: 'yellow',
      fillColor: 'transparent',
      weight: 5,
      opacity: 0.8,
      dashArray: '5, 10'
    }).addTo(gameMap);
  }
  
  // 強制刷新地圖
  gameMap.invalidateSize();
  
  // 返回創建的標記
  return createdMarkers;
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
  
  // 顯示加載中
  showLoading();
  
  // 呼叫API捕捉精靈
  fetch('/game/api/route-creatures/catch', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ creatureId: creatureId })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('捕捉精靈失敗');
    }
    return response.json();
  })
  .then(data => {
    hideLoading();
    
    if (data.success) {
      console.log('捕捉成功:', data);
      
      // 應用捕捉動畫效果
      const markerElement = creature.marker.getElement();
      if (markerElement) {
        markerElement.classList.add('catch-animation');
        
        // 等待動畫完成後從地圖移除
        setTimeout(function() {
          if (window.creaturesLayer) {
            window.creaturesLayer.removeLayer(creature.marker);
          }
        }, 500);
      } else {
        // 如果無法獲取DOM元素，直接從地圖中移除
        if (window.creaturesLayer) {
          window.creaturesLayer.removeLayer(creature.marker);
        }
      }
      
      // 從精靈列表中移除
      const index = currentCreatures.findIndex(c => c.id === creatureId);
      if (index !== -1) {
        currentCreatures.splice(index, 1);
      }
      
      // 更新計數
      capturedCreatures++;
      
      // 更新模態框內容
      document.getElementById('catchSuccessMessage').textContent = data.message;
      document.getElementById('caughtCreatureImage').src = data.creature.image_url || getDefaultCreatureImage(data.creature.element_type, data.creature.name);
      document.getElementById('creature-power').textContent = data.creature.power;
      document.getElementById('creature-type').textContent = getElementTypeName(data.creature.element_type);
      document.getElementById('creature-rarity').textContent = data.creature.species;
      
      // 顯示成功模態框
      const successModal = new bootstrap.Modal(document.getElementById('catchSuccessModal'));
      successModal.show();
      
      // 播放音效和動畫
      animateSparkles();
      playCatchSound();
    } else {
      console.error('捕捉失敗:', data);
      showGameAlert(data.message || '捕捉精靈失敗，請稍後再試！', 'warning');
    }
  })
  .catch(error => {
    console.error('捕捉精靈錯誤:', error);
    hideLoading();
    showGameAlert('捕捉精靈失敗，請稍後再試！', 'danger');
  });
}

// 根據精靈類型獲取表情符號
function getCreatureEmoji(type) {
  switch(type) {
    case 'water': return '💧';
    case 'fire': return '🔥';
    case 'earth': return '🌱';
    case 'air': return '💨';
    case 'electric': return '⚡';
    default: return '✨';
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
    case 'earth': return '8e44ad';
    case 'air': return '2ecc71';
    case 'electric': return 'f1c40f';
    default: return '95a5a6';
  }
}

// 根據精靈類型獲取徽章類別
function getTypeBadgeClass(type) {
  switch(type) {
    case 'water': return 'bg-primary';
    case 'fire': return 'bg-danger';
    case 'earth': return 'bg-warning';
    case 'air': return 'bg-info';
    case 'electric': return 'bg-warning';
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
    case 'earth': return '土系';
    case 'air': return '風系';
    case 'electric': return '電系';
    case 0: return '火系'; // 數字枚舉值 (FIRE = 0)
    case 1: return '水系'; // 數字枚舉值 (WATER = 1)
    case 2: return '土系'; // 數字枚舉值 (EARTH = 2)
    case 3: return '風系'; // 數字枚舉值 (AIR = 3)
    case 4: return '電系'; // 數字枚舉值 (ELECTRIC = 4)
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