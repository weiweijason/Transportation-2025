// 模組：bus-position-manager.js - 公車實時位置管理

// 公車圖層和數據存儲
let busPositionLayer = L.layerGroup();
let currentBuses = [];
let busMarkers = {};

// 公車圖標配置
const busIcon = L.icon({
    iconUrl: 'data:image/svg+xml;base64,' + btoa(`
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
            <circle cx="16" cy="16" r="15" fill="#2196F3" stroke="#ffffff" stroke-width="2"/>
            <path d="M8 12h16v8H8z" fill="#ffffff"/>
            <rect x="10" y="14" width="3" height="2" fill="#2196F3"/>
            <rect x="19" y="14" width="3" height="2" fill="#2196F3"/>
            <circle cx="11" cy="22" r="2" fill="#333"/>
            <circle cx="21" cy="22" r="2" fill="#333"/>
            <rect x="12" y="8" width="8" height="3" rx="1" fill="#ffffff"/>
        </svg>
    `),
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
});

// 路線對應的公車數據文件
const busDataFiles = {
    'br3': '/static/data/bus/br3_bus.json',
    'cat_left': '/static/data/bus/cat_left_bus.json',
    'cat_left_zhinan': '/static/data/bus/cat_left_zhinan_bus.json',
    'cat_right': '/static/data/bus/cat_right_bus.json'
};

// 路線顏色對應
const routeBusColors = {
    'br3': '#8B4513',        // 棕色 - 棕3路線
    'cat_left': '#4caf50',   // 綠色 - 貓空左線(動物園)
    'cat_left_zhinan': '#9c27b0', // 紫色 - 貓空左線(指南宮)
    'cat_right': '#ff9800'   // 橙色 - 貓空右線
};

/**
 * 初始化公車位置圖層
 * @param {Object} map - Leaflet地圖實例
 */
function initBusPositionLayer(map) {
    if (!map) {
        console.error('地圖實例不存在，無法初始化公車位置圖層');
        return;
    }

    console.log('初始化公車位置圖層');
    
    // 清理現有圖層
    if (busPositionLayer) {
        busPositionLayer.clearLayers();
        map.removeLayer(busPositionLayer);
    }
    
    // 重新創建圖層
    busPositionLayer = L.layerGroup();
    map.addLayer(busPositionLayer);
    
    // 將圖層暴露給全局
    window.busPositionLayer = busPositionLayer;
    
    console.log('公車位置圖層初始化完成');
}

/**
 * 創建公車圖標（根據路線顏色）
 * @param {string} routeColor - 路線顏色
 * @returns {Object} Leaflet圖標對象
 */
function createBusIcon(routeColor = '#2196F3') {
    // 移除SVG中的中文字符，避免btoa編碼錯誤
    const svgContent = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
            <circle cx="16" cy="16" r="15" fill="${routeColor}" stroke="#ffffff" stroke-width="2"/>
            <path d="M8 12h16v8H8z" fill="#ffffff"/>
            <rect x="10" y="14" width="3" height="2" fill="${routeColor}"/>
            <rect x="19" y="14" width="3" height="2" fill="${routeColor}"/>
            <circle cx="11" cy="22" r="2" fill="#333"/>
            <circle cx="21" cy="22" r="2" fill="#333"/>
            <rect x="12" y="8" width="8" height="3" rx="1" fill="#ffffff"/>
            <path d="M12 16h8v2h-8z" fill="${routeColor}"/>
            <circle cx="16" cy="16" r="3" fill="${routeColor}" opacity="0.3"/>
        </svg>
    `;
    
    // 使用 encodeURIComponent 替代 btoa 來避免編碼問題
    const encodedSvg = encodeURIComponent(svgContent);
    
    return L.icon({
        iconUrl: 'data:image/svg+xml;charset=utf-8,' + encodedSvg,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16]
    });
}

/**
 * 載入所有公車位置數據
 */
async function loadAllBusPositions() {
    console.log('開始載入所有公車位置數據');
    
    if (!window.busMap && !window.gameMap) {
        console.error('地圖實例不存在，無法載入公車位置');
        return;
    }

    const map = window.busMap || window.gameMap;
    
    // 確保圖層已初始化
    if (!window.busPositionLayer) {
        initBusPositionLayer(map);
    }    // 清除現有公車標記
    clearBusMarkers();

    let totalBuses = 0;
    let activeRoutes = 0;
    let routesWithBuses = [];

    // 逐一載入每個路線的公車數據
    for (const [route, dataFile] of Object.entries(busDataFiles)) {
        try {
            const buses = await loadRouteBusPositions(route, dataFile);
            if (buses.length > 0) {
                totalBuses += buses.length;
                activeRoutes++;
                routesWithBuses.push(`${getRouteDisplayName(route)}(${buses.length}輛)`);
                console.log(`載入 ${route} 路線: ${buses.length} 輛公車`);
            }
            // 空集合時不記錄任何訊息
        } catch (error) {
            console.error(`載入 ${route} 路線公車數據失敗:`, error);
        }
    }

    // 只在有公車時才顯示載入結果
    if (totalBuses > 0) {
        console.log(`公車位置載入完成，共載入 ${totalBuses} 輛公車，${activeRoutes} 條路線有公車運行`);
        
        if (typeof window.showGameAlert === 'function') {
            const message = `已載入 ${totalBuses} 輛公車的位置資訊\n${routesWithBuses.join('、')}`;
            window.showGameAlert(message, 'info', 4000);
        }
    } else {
        // 沒有任何公車時，靜默處理，不顯示警告
        console.log('當前所有路線均無公車運行');
    }
}

/**
 * 載入特定路線的公車位置
 * @param {string} route - 路線名稱
 * @param {string} dataFile - 數據文件路徑
 * @returns {Array} 公車數據陣列
 */
async function loadRouteBusPositions(route, dataFile) {
    try {
        const response = await fetch(dataFile);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!Array.isArray(data)) {
            console.warn(`${route} 路線數據格式錯誤，預期為陣列`);
            return [];
        }        // 處理空陣列的情況（路線尚未發車或已收班）
        if (data.length === 0) {
            // 靜默處理空集合，不產生日誌訊息
            return [];
        }

        console.log(`${route} 路線載入 ${data.length} 輛公車`);
        
        // 在地圖上顯示公車
        data.forEach(bus => {
            displayBusOnMap(bus, route);
        });

        return data;
        
    } catch (error) {
        console.error(`載入 ${route} 路線公車數據錯誤:`, error);
        return [];
    }
}

/**
 * 在地圖上顯示公車標記
 * @param {Object} bus - 公車數據
 * @param {string} route - 路線名稱
 */
function displayBusOnMap(bus, route) {
    if (!bus.PositionLat || !bus.PositionLon || !bus.PlateNumb) {
        console.warn('公車數據不完整:', bus);
        return;
    }

    if (!window.busPositionLayer) {
        console.error('公車位置圖層未初始化');
        return;
    }

    const lat = parseFloat(bus.PositionLat);
    const lon = parseFloat(bus.PositionLon);
    
    if (isNaN(lat) || isNaN(lon)) {
        console.warn('公車位置座標無效:', bus);
        return;
    }

    // 獲取路線顏色
    const routeColor = routeBusColors[route] || '#2196F3';
    
    // 創建公車圖標
    const icon = createBusIcon(routeColor);
    
    // 創建標記
    const marker = L.marker([lat, lon], { icon: icon });
    
    // 設置彈出窗口內容
    const popupContent = `
        <div class="bus-popup" style="text-align: center; font-family: Arial, sans-serif;">
            <h6 style="margin: 0 0 8px 0; color: ${routeColor}; font-weight: bold;">
                <i class="fas fa-bus" style="margin-right: 5px;"></i>公車資訊
            </h6>
            <div style="background: #f8f9fa; padding: 8px; border-radius: 5px; margin-bottom: 8px;">
                <div style="font-size: 14px; font-weight: bold; color: #333;">
                    車號: <span style="color: ${routeColor};">${bus.PlateNumb}</span>
                </div>
            </div>
            <div style="font-size: 12px; color: #666;">
                <div>路線: ${getRouteDisplayName(route)}</div>
                <div>位置: ${lat.toFixed(5)}, ${lon.toFixed(5)}</div>
            </div>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    
    // 添加到圖層
    window.busPositionLayer.addLayer(marker);
    
    // 存儲標記以便後續管理
    const busKey = `${route}_${bus.PlateNumb}`;
    busMarkers[busKey] = marker;
    
    console.log(`已添加公車標記: ${bus.PlateNumb} (${route}) 在位置 [${lat}, ${lon}]`);
}

/**
 * 獲取路線顯示名稱
 * @param {string} route - 路線代碼
 * @returns {string} 顯示名稱
 */
function getRouteDisplayName(route) {
    const routeNames = {
        'br3': '棕3路線',
        'cat_left': '貓空左線(動物園)',
        'cat_left_zhinan': '貓空左線(指南宮)',
        'cat_right': '貓空右線'
    };
    return routeNames[route] || route;
}

/**
 * 清除所有公車標記
 */
function clearBusMarkers() {
    console.log('清除所有公車標記');
    
    if (window.busPositionLayer) {
        window.busPositionLayer.clearLayers();
    }
    
    // 清空標記存儲
    busMarkers = {};
    currentBuses = [];
}

/**
 * 更新公車位置（重新載入所有數據）
 */
async function updateBusPositions() {
    console.log('更新公車位置數據');
    await loadAllBusPositions();
}

/**
 * 切換公車圖層顯示/隱藏
 * @param {boolean} show - 是否顯示
 */
function toggleBusLayer(show = true) {
    if (!window.busPositionLayer) return;
    
    const map = window.busMap || window.gameMap;
    if (!map) return;
    
    if (show) {
        if (!map.hasLayer(window.busPositionLayer)) {
            map.addLayer(window.busPositionLayer);
        }
        console.log('公車圖層已顯示');
    } else {
        if (map.hasLayer(window.busPositionLayer)) {
            map.removeLayer(window.busPositionLayer);
        }
        console.log('公車圖層已隱藏');
    }
}

// 暴露函數到全局
window.initBusPositionLayer = initBusPositionLayer;
window.loadAllBusPositions = loadAllBusPositions;
window.updateBusPositions = updateBusPositions;
window.clearBusMarkers = clearBusMarkers;
window.toggleBusLayer = toggleBusLayer;

// 導出模組
export {
    initBusPositionLayer,
    loadAllBusPositions,
    updateBusPositions,
    clearBusMarkers,
    toggleBusLayer,
    busPositionLayer
};
