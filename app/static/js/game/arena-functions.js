/**
 * 擂台功能相關函數模組
 * 處理站牌擂台顯示和挑戰功能
 */

// 獲取擂台列表
function fetchArenasInfo() {
  console.log('獲取擂台資訊');
  showLoading();
  
  const arenaListElement = document.getElementById('arenaList');
  if (!arenaListElement) {
    console.error('找不到擂台列表元素');
    hideLoading();
    return;
  }
  
  // 如果尚未獲取到擂台列表，等待道館加載完成
  if (!window.busStopsArenas || Object.keys(window.busStopsArenas).length === 0) {
    console.log('尚未獲取到擂台列表，等待一秒後重試');
    setTimeout(fetchArenasInfo, 1000);
    return;
  }
  
  // 清空列表
  arenaListElement.innerHTML = '';
  
  // 將擂台資訊轉換為陣列
  arenaList = Object.values(window.busStopsArenas);
  
  if (arenaList.length === 0) {
    arenaListElement.innerHTML = '<div class="col-12 text-center py-5"><p>找不到任何擂台資訊</p></div>';
    hideLoading();
    return;
  }
  
  // 按照路線分組
  const groupedArenas = {};
  
  arenaList.forEach(arena => {
    if (!groupedArenas[arena.routeName]) {
      groupedArenas[arena.routeName] = [];
    }
    groupedArenas[arena.routeName].push(arena);
  });
  
  // 生成HTML
  Object.keys(groupedArenas).forEach(routeName => {
    const arenas = groupedArenas[routeName];
    
    // 添加路線標題
    const routeColor = getRouteColorByName(routeName);
    arenaListElement.innerHTML += `
      <div class="col-12 mb-3">
        <div class="d-flex align-items-center mb-2">
          <span class="route-line" style="background-color:${routeColor};"></span>
          <h5 class="mb-0">${routeName} 站點道館</h5>
        </div>
      </div>
    `;
    
    // 添加該路線的擂台
    arenas.forEach(arena => {
      const arenaCard = document.createElement('div');
      arenaCard.className = 'col-md-4 col-sm-6 mb-3';
      arenaCard.innerHTML = `
        <div class="card arena-card" style="background-image: url('https://placehold.co/600x400/${routeColor.replace('#', '')}/white?text=${encodeURIComponent(arena.stopName)}')">
          <div class="arena-level-badge">${arena.level}</div>
          <div class="card-header arena-card-header text-center">
            <h5 class="mb-0">${arena.stopName}</h5>
          </div>
          <div class="card-body arena-card-body d-flex flex-column justify-content-end">
            <div class="arena-status mb-2">
              <p class="mb-0"><small>擂主: ${arena.owner || '無'}</small></p>
              <p class="mb-0"><small>守護精靈: ${arena.guardianName || '無'}</small></p>
            </div>
            <button class="btn btn-light btn-sm challenge-arena-btn" 
                  onclick="goToArena('${arena.stopId}', '${arena.stopName}', '${arena.routeName}')">
              <i class="fas fa-trophy me-1"></i>前往道館
            </button>
          </div>
        </div>
      `;
      arenaListElement.appendChild(arenaCard);
    });
  });
  
  console.log('擂台列表生成完成');
  hideLoading();
}

// 前往道館的函數
function goToArena(stopId, stopName, routeName) {
  // 從全局存儲的擂台資訊中查找正確的擂台ID
  const arenaId = findArenaIdByStopId(stopId);
  
  if (arenaId) {
    // 如果找到擂台ID，直接用arena_id參數導向battle頁面
    window.location.href = `/game/battle?arena_id=${arenaId}`;
  } else {
    // 如果找不到擂台ID，回退到原來的方法
    console.warn('無法找到擂台ID，使用舊方法導航');
    // 獲取目前位置（用於lat和lon參數）
    const location = window.userLocation || [25.0282, 121.5432]; // 默認位置
    
    window.location.href = `/game/battle?stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}&lat=${location[0]}&lon=${location[1]}`;
  }
}

// 根據站點ID查找擂台ID
function findArenaIdByStopId(stopId) {
  // 檢查全局擂台資訊中是否存在此站點ID對應的擂台
  if (window.busStopsArenas && window.busStopsArenas[stopId] && window.busStopsArenas[stopId].arenaId) {
    return window.busStopsArenas[stopId].arenaId;
  }
  
  // 如果我們有完整的擂台列表，嘗試從中查找
  if (window.allArenas) {
    const arena = window.allArenas.find(a => 
      a.stopIds && (a.stopIds.includes(stopId) || a.stopIds[0] === stopId)
    );
    if (arena && arena.id) {
      return arena.id;
    }
  }
  
  // 如果找不到，返回一個格式化的擂台ID (這僅是一種臨時解決方案)
  return `arena-${stopId}`;
}