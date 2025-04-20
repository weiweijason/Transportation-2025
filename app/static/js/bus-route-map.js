// 精靈公車 - 公車路線地圖繪製

// 定義地圖和圖層變數
let map;
let routeLayer = L.layerGroup();
let stopsLayer = L.layerGroup();
let busesLayer = L.layerGroup();
let userMarker;
let userCircle;

// 精靈圖層
let creaturesLayer = L.layerGroup();

// 道館圖層
let arenaLayer = L.layerGroup();

// 追蹤已創建的站點/道館，避免重複創建
let uniqueStops = {};

// 路線顏色配置
const routeColors = {
    'cat-right': '#ff9800', // 橙色 - 貓空右線
    'cat-left': '#4caf50', // 綠色 - 貓空左線(動物園)
    'cat-left-zhinan': '#9c27b0' // 紫色 - 貓空左線(指南宮)
};

// 儲存各路線的座標點
const routeCoordinates = {
    'cat-right': [],
    'cat-left': [],
    'cat-left-zhinan': []
};

// 精靈生成相關變數
let routeCreatures = []; // 儲存所有路線上的精靈
const MAX_CREATURES_PER_ROUTE = 10; // 每條路線最多精靈數量
const CREATURE_LIFETIME = 5 * 60 * 1000; // 精靈存在時間 (5分鐘，單位毫秒)
const SPAWN_INTERVAL = 60 * 1000; // 生成嘗試間隔 (1分鐘，單位毫秒)
const SPAWN_CHANCE = 0.8; // 生成機率 (80%)


// 各路線的精靈定義
const routeCreatureTypes = {
    // 貓空右線的特有精靈
    'cat-right': [
        { id: 'cr1', name: '右線遊俠', type: '一般', rarity: '普通', power: 45, img: 'https://placehold.co/300x200/ff9800/ffffff?text=右線遊俠' },
        { id: 'cr2', name: '貓空飛鼠', type: '一般', rarity: '普通', power: 50, img: 'https://placehold.co/300x200/ff9800/ffffff?text=貓空飛鼠' },
        { id: 'cr3', name: '纜車守護者', type: '一般', rarity: '稀有', power: 65, img: 'https://placehold.co/300x200/ff9800/ffffff?text=纜車守護者' }
    ],
    // 貓空左線(動物園)的特有精靈
    'cat-left': [
        { id: 'cl1', name: '猴山之王', type: '一般', rarity: '普通', power: 45, img: 'https://placehold.co/300x200/4caf50/ffffff?text=猴山之王' },
        { id: 'cl2', name: '熊貓使者', type: '一般', rarity: '稀有', power: 70, img: 'https://placehold.co/300x200/4caf50/ffffff?text=熊貓使者' },
        { id: 'cl3', name: '動物園幻影', type: '一般', rarity: '普通', power: 55, img: 'https://placehold.co/300x200/4caf50/ffffff?text=動物園幻影' }
    ],
    // 貓空左線(指南宮)的特有精靈
    'cat-left-zhinan': [
        { id: 'cz1', name: '指南星使', type: '一般', rarity: '普通', power: 50, img: 'https://placehold.co/300x200/9c27b0/ffffff?text=指南星使' },
        { id: 'cz2', name: '宮殿守衛', type: '一般', rarity: '稀有', power: 65, img: 'https://placehold.co/300x200/9c27b0/ffffff?text=宮殿守衛' },
        { id: 'cz3', name: '山靈使者', type: '一般', rarity: '普通', power: 55, img: 'https://placehold.co/300x200/9c27b0/ffffff?text=山靈使者' }
    ]
};

// 初始化地圖
function initMap(elementId, center = [25.0165, 121.5375], zoom = 14) {
    console.log('開始初始化地圖, elementId:', elementId);
    
    // 檢查元素是否存在
    const mapElement = document.getElementById(elementId);
    if (!mapElement) {
        console.error(`地圖容器元素 #${elementId} 不存在`);
        return null;
    }
    
    try {
        // 創建地圖
        console.log('創建地圖實例, center:', center, 'zoom:', zoom);
        map = L.map(elementId).setView(center, zoom);
        console.log('地圖實例已創建');

        // 添加OpenStreetMap圖層
        console.log('添加OpenStreetMap圖層');
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        console.log('OpenStreetMap圖層已添加');

        // 添加各圖層到地圖
        console.log('添加其他圖層到地圖');
        routeLayer.addTo(map);
        stopsLayer.addTo(map);
        busesLayer.addTo(map);
        creaturesLayer.addTo(map);
        arenaLayer.addTo(map);
        console.log('所有圖層已添加到地圖');
        
        // 如果有定位權限，獲取用戶位置
        if (navigator.geolocation) {
            console.log('嘗試獲取用戶位置');
            updateUserLocation();
        } else {
            console.log('瀏覽器不支持地理定位');
        }
        
        // 觸發一次resize事件以確保地圖正確渲染
        setTimeout(() => {
            console.log('觸發地圖resize事件');
            map.invalidateSize();
        }, 100);
        
        // 註冊視窗大小變更事件
        window.addEventListener('resize', function() {
            console.log('視窗大小改變，重新調整地圖大小');
            map.invalidateSize();
        });
        
        return map;
    } catch (error) {
        console.error('初始化地圖時發生錯誤:', error);
        alert('初始化地圖時發生錯誤: ' + error.message);
        return null;
    }
}

// 更新用戶位置
function updateUserLocation() {
    navigator.geolocation.getCurrentPosition(
        (position) => {
            // 獲取位置座標
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            const userLatLng = [lat, lng];
            
            // 更新用戶位置標記
            if (userMarker) {
                userMarker.setLatLng(userLatLng);
                userCircle.setLatLng(userLatLng);
            } else {
                // 創建用戶位置標記
                userMarker = L.marker(userLatLng, {
                    icon: L.divIcon({
                        className: 'user-marker',
                        html: '<div style="background-color:#4285F4;width:20px;height:20px;border-radius:50%;border:3px solid white;"></div>',
                        iconSize: [20, 20],
                        iconAnchor: [10, 10]
                    })
                }).addTo(map);
                
                // 創建用戶範圍圓圈
                userCircle = L.circle(userLatLng, {
                    radius: 300,
                    color: '#4285F4',
                    fillColor: '#4285F4',
                    fillOpacity: 0.1,
                    weight: 1
                }).addTo(map);
            }
            
            // 更新地圖視角
            map.setView(userLatLng, 15);
            
            // 更新位置顯示
            const locationElement = document.getElementById('currentLocation');
            if (locationElement) {
                locationElement.textContent = `緯度: ${lat.toFixed(5)}, 經度: ${lng.toFixed(5)}`;
            }
            
        },
        (error) => {
            console.error('定位錯誤:', error);
            alert('無法獲取您的位置，請確保已授予位置權限。');
        }
    );
}

// 獲取並繪製貓空右線
function loadCatRightRoute() {
    console.log('載入貓空右線');
    showLoading();
    
    fetch('/game/api/bus/cat-right-route')
        .then(response => response.json())
        .then(data => {
            console.log('獲取到貓空右線資料:', data);
            
            // 解析路線座標
            if (data && Array.isArray(data)) {
                // 處理路線資料
                let coordinates = [];
                
                // 提取路線座標點
                data.forEach(point => {
                    if (point.PositionLat && point.PositionLon) {
                        coordinates.push([point.PositionLat, point.PositionLon]);
                    }
                });
                
                if (coordinates.length > 0) {
                    // 儲存路線座標
                    routeCoordinates['cat-right'] = coordinates;
                    
                    // 創建路線
                    const polyline = L.polyline(coordinates, {
                        color: routeColors['cat-right'],
                        weight: 5,
                        opacity: 0.8
                    }).addTo(routeLayer);
                    
                    // 添加路線資訊彈窗
                    polyline.bindPopup(`
                        <div style="font-weight:bold;font-size:16px;">貓空纜車右線</div>
                        <div>方向: 貓空 → 動物園</div>
                    `);
                    
                    console.log('貓空右線繪製完成，座標點數量:', coordinates.length);
                } else {
                    console.warn('貓空右線座標解析失敗，使用備用座標');
                    useBackupRoute('cat-right');
                }
            } else {
                console.warn('貓空右線資料格式不正確，使用備用資料');
                useBackupRoute('cat-right');
            }
        })
        .catch(error => {
            console.error('獲取貓空右線資料失敗:', error);
            useBackupRoute('cat-right');
        })
        .finally(() => {
            hideLoading();
        });
}

// 獲取並繪製貓空左線(動物園)
function loadCatLeftRoute() {
    console.log('載入貓空左線(動物園)');
    showLoading();
    
    fetch('/game/api/bus/cat-left-route')
        .then(response => response.json())
        .then(data => {
            console.log('獲取到貓空左線(動物園)資料:', data);
            
            // 解析路線座標
            if (data && Array.isArray(data)) {
                let coordinates = [];
                
                // 提取路線座標點
                data.forEach(point => {
                    if (point.PositionLat && point.PositionLon) {
                        coordinates.push([point.PositionLat, point.PositionLon]);
                    }
                });
                
                if (coordinates.length > 0) {
                    // 儲存路線座標
                    routeCoordinates['cat-left'] = coordinates;
                    
                    // 創建路線
                    const polyline = L.polyline(coordinates, {
                        color: routeColors['cat-left'],
                        weight: 5,
                        opacity: 0.8
                    }).addTo(routeLayer);
                    
                    // 添加路線資訊彈窗
                    polyline.bindPopup(`
                        <div style="font-weight:bold;font-size:16px;">貓空纜車左線(動物園)</div>
                        <div>方向: 動物園 → 貓空</div>
                    `);
                    
                    console.log('貓空左線(動物園)繪製完成，座標點數量:', coordinates.length);
                } else {
                    console.warn('貓空左線(動物園)座標解析失敗，使用備用座標');
                    useBackupRoute('cat-left');
                }
            } else {
                console.warn('貓空左線(動物園)資料格式不正確，使用備用資料');
                useBackupRoute('cat-left');
            }
        })
        .catch(error => {
            console.error('獲取貓空左線(動物園)資料失敗:', error);
            useBackupRoute('cat-left');
        })
        .finally(() => {
            hideLoading();
        });
}

// 獲取並繪製貓空左線(指南宮)
function loadCatLeftZhinanRoute() {
    console.log('載入貓空左線(指南宮)');
    showLoading();
    
    fetch('/game/api/bus/cat-left-zhinan-route')
        .then(response => response.json())
        .then(data => {
            console.log('獲取到貓空左線(指南宮)資料:', data);
            
            // 解析路線座標
            if (data && Array.isArray(data)) {
                let coordinates = [];
                
                // 提取路線座標點
                data.forEach(point => {
                    if (point.PositionLat && point.PositionLon) {
                        coordinates.push([point.PositionLat, point.PositionLon]);
                    }
                });
                
                if (coordinates.length > 0) {
                    // 儲存路線座標
                    routeCoordinates['cat-left-zhinan'] = coordinates;
                    
                    // 創建路線
                    const polyline = L.polyline(coordinates, {
                        color: routeColors['cat-left-zhinan'],
                        weight: 5,
                        opacity: 0.8
                    }).addTo(routeLayer);
                    
                    // 添加路線資訊彈窗
                    polyline.bindPopup(`
                        <div style="font-weight:bold;font-size:16px;">貓空纜車左線(指南宮)</div>
                        <div>方向: 貓空 → 指南宮</div>
                    `);
                    
                    console.log('貓空左線(指南宮)繪製完成，座標點數量:', coordinates.length);
                } else {
                    console.warn('貓空左線(指南宮)座標解析失敗，使用備用座標');
                    useBackupRoute('cat-left-zhinan');
                }
            } else {
                console.warn('貓空左線(指南宮)資料格式不正確，使用備用資料');
                useBackupRoute('cat-left-zhinan');
            }
        })
        .catch(error => {
            console.error('獲取貓空左線(指南宮)資料失敗:', error);
            useBackupRoute('cat-left-zhinan');
        })
        .finally(() => {
            hideLoading();
        });
}

// 使用備用路線資料（當API獲取失敗時）
function useBackupRoute(routeKey) {
    console.log(`使用備用路線資料: ${routeKey}`);
    
    let coordinates = [];
    
    // 根據路線類型提供備用座標
    switch(routeKey) {
        case 'cat-right':
            coordinates = [
                [25.0323, 121.5342], // 貓空站
                [25.0298, 121.5332], // 中途點
                [25.0273, 121.5321]  // 動物園站
            ];
            break;
            
        case 'cat-left':
            coordinates = [
                [25.0273, 121.5321], // 動物園站
                [25.0298, 121.5332], // 中途點
                [25.0323, 121.5342]  // 貓空站
            ];
            break;
            
        case 'cat-left-zhinan':
            // 修正貓空左線(指南宮)的備用路線座標
            coordinates = [
                [25.0323, 121.5342], // 貓空站
                [25.0330, 121.5360], // 中途點1
                [25.0345, 121.5376], // 中途點2
                [25.0355, 121.5389]  // 指南宮站
            ];
            break;
    }
    
    // 儲存路線座標
    routeCoordinates[routeKey] = coordinates;
    
    // 創建路線
    const polyline = L.polyline(coordinates, {
        color: routeColors[routeKey],
        weight: 5,
        opacity: 0.8
    }).addTo(routeLayer);
    
    // 添加路線資訊彈窗
    let routeName = '';
    let direction = '';
    
    switch(routeKey) {
        case 'cat-right':
            routeName = '貓空纜車右線';
            direction = '貓空 → 動物園';
            break;
        case 'cat-left':
            routeName = '貓空纜車左線(動物園)';
            direction = '動物園 → 貓空';
            break;
        case 'cat-left-zhinan':
            routeName = '貓空纜車左線(指南宮)';
            direction = '貓空 → 指南宮';
            break;
    }
    
    polyline.bindPopup(`
        <div style="font-weight:bold;font-size:16px;">${routeName}</div>
        <div>方向: ${direction}</div>
        <div><small>(備用資料)</small></div>
    `);
    
    console.log(`備用路線 ${routeKey} 繪製完成`);
}

// 載入並繪製所有貓空路線的站點
function loadAllBusStops() {
    console.log('載入所有貓空路線的站點');
    showLoading();
    
    // 清除現有站點圖層
    stopsLayer.clearLayers();
    arenaLayer.clearLayers();
    
    // 重置站點追蹤器
    uniqueStops = {};
    
    // 加載貓空右線站點
    loadBusStops('cat-right');
    
    // 加載貓空左線(動物園)站點
    loadBusStops('cat-left');
    
    // 加載貓空左線(指南宮)站點
    loadBusStops('cat-left-zhinan');
    
    hideLoading();
}

// 載入特定路線的站點
function loadBusStops(routeKey) {
    console.log(`載入 ${routeKey} 站點`);
    
    let apiUrl = '';
    let routeName = '';
    
    // 根據路線類型設置API和路線名稱
    switch(routeKey) {
        case 'cat-right':
            apiUrl = '/game/api/bus/cat-right-stops';
            routeName = '貓空右線';
            break;
        case 'cat-left':
            apiUrl = '/game/api/bus/cat-left-stops';
            routeName = '貓空左線(動物園)';
            break;
        case 'cat-left-zhinan':
            apiUrl = '/game/api/bus/cat-left-zhinan-stops';
            routeName = '貓空左線(指南宮)';
            break;
    }
    
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            console.log(`獲取到 ${routeKey} 站點資料:`, data);
            
            if (data && data.length > 0) {
                // 解析站點資料
                processStops(data, routeKey, routeName);
            } else {
                console.warn(`${routeKey} 站點資料為空，使用備用資料`);
                useBackupStops(routeKey, routeName);
            }
        })
        .catch(error => {
            console.error(`獲取 ${routeKey} 站點資料失敗:`, error);
            useBackupStops(routeKey, routeName);
        });
}

// 處理站點資料
function processStops(data, routeKey, routeName) {
    console.log(`處理 ${routeKey} 站點資料`);
    
    let stops = [];
    
    // 嘗試解析不同的資料格式
    if (data[0]?.Stops && Array.isArray(data[0].Stops)) {
        // V3 API格式: 包含Stops陣列
        data.forEach(route => {
            if (route.Stops && Array.isArray(route.Stops)) {
                route.Stops.forEach(stop => {
                    if (stop.StopPosition) {
                        stops.push({
                            id: stop.StopID || `stop-${routeKey}-${stops.length}`,
                            name: stop.StopName?.Zh_tw || '未知站名',
                            position: [
                                stop.StopPosition.PositionLat, 
                                stop.StopPosition.PositionLon
                            ]
                        });
                    }
                });
            }
        });
    } else if (Array.isArray(data)) {
        // 其他格式，逐個檢查站點資料
        data.forEach((item, index) => {
            // 檢查可能的位置資訊
            let position = null;
            let name = '未知站名';
            let id = `stop-${routeKey}-${index}`;
            
            if (item.StopPosition) {
                position = [item.StopPosition.PositionLat, item.StopPosition.PositionLon];
                name = item.StopName?.Zh_tw || '未知站名';
                id = item.StopID || id;
            } else if (item.StationPosition) {
                position = [item.StationPosition.PositionLat, item.StationPosition.PositionLon];
                name = item.StationName?.Zh_tw || '未知站名';
                id = item.StationID || id;
            } else if (item.PositionLat && item.PositionLon) {
                position = [item.PositionLat, item.PositionLon];
                name = item.StopName || item.name || '未知站名';
                id = item.StopID || item.id || id;
            }
            
            if (position) {
                stops.push({
                    id: id,
                    name: name,
                    position: position
                });
            }
        });
    }
    
    // 繪製站點和道館
    if (stops.length > 0) {
        stops.forEach(stop => {
            drawStop(stop, routeColors[routeKey], routeName);
            createArena(stop, routeColors[routeKey], routeName);
        });
        
        console.log(`${routeKey} 站點繪製完成，共 ${stops.length} 個站點`);
    } else {
        console.warn(`無法解析 ${routeKey} 站點資料，使用備用資料`);
        useBackupStops(routeKey, routeName);
    }
}

// 使用備用站點資料
function useBackupStops(routeKey, routeName) {
    console.log(`使用備用站點資料: ${routeKey}`);
    
    let backupStops = [];
    
    // 根據路線類型提供備用站點
    switch(routeKey) {
        case 'cat-right':
            backupStops = [
                { id: 'stop-cr-1', name: '貓空站', position: [25.0323, 121.5342] },
                { id: 'stop-cr-2', name: '指南宮站', position: [25.0355, 121.5389] },
                { id: 'stop-cr-3', name: '動物園站', position: [25.0273, 121.5321] }
            ];
            break;
            
        case 'cat-left':
            backupStops = [
                { id: 'stop-cl-1', name: '動物園站', position: [25.0273, 121.5321] },
                { id: 'stop-cl-2', name: '貓空纜車轉乘站', position: [25.0298, 121.5332] },
                { id: 'stop-cl-3', name: '貓空站', position: [25.0323, 121.5342] }
            ];
            break;
            
        case 'cat-left-zhinan':
            backupStops = [
                { id: 'stop-cz-1', name: '貓空站', position: [25.0323, 121.5342] },
                { id: 'stop-cz-2', name: '指南宮中途站', position: [25.0340, 121.5370] },
                { id: 'stop-cz-3', name: '指南宮站', position: [25.0355, 121.5389] }
            ];
            break;
    }
    
    // 繪製備用站點和道館
    backupStops.forEach(stop => {
        drawStop(stop, routeColors[routeKey], routeName, true);
        createArena(stop, routeColors[routeKey], routeName, true);
    });
    
    console.log(`備用站點 ${routeKey} 繪製完成，共 ${backupStops.length} 個站點`);
}

// 繪製站點
function drawStop(stop, color, routeName, isBackup = false) {
    console.log(`繪製站點: ${stop.name} at [${stop.position[0]}, ${stop.position[1]}]`);
    
    // 不再繪製站點標記（小圓點）
    // 只記錄站點資訊用於創建道館，但不添加到地圖上
}

// 創建道館
function createArena(stop, color, routeName, isBackup = false) {
    console.log(`嘗試創建道館: ${stop.name}`);
    
    // 檢查站點名稱是否已存在（不區分大小寫且去除空格）
    const normalizeName = name => name.toLowerCase().replace(/\s+/g, '');
    const stopNormalizedName = normalizeName(stop.name);
    
    // 檢查是否已有相同名稱的站點
    for (let key in uniqueStops) {
        if (normalizeName(uniqueStops[key].stopName) === stopNormalizedName) {
            console.log(`已存在同名道館 (${uniqueStops[key].stopName})，跳過創建: ${stop.name}`);
            return null;
        }
    }
    
    // 檢查是否已經存在相近位置的道館
    const positionKey = `${stop.position[0].toFixed(4)},${stop.position[1].toFixed(4)}`;
    if (uniqueStops[positionKey]) {
        console.log(`道館已存在於位置 ${positionKey}，跳過創建: ${stop.name}`);
        return null;
    }
    
    // 檢查是否有相近的道館
    // 計算經緯度約30米的差值 (0.0003大約是30米)
    const nearbyDistance = 0.0003;
    for (let key in uniqueStops) {
        const [existingLat, existingLng] = key.split(',').map(Number);
        const lat = parseFloat(stop.position[0]);
        const lng = parseFloat(stop.position[1]);
        
        // 如果兩個站牌位置非常接近，視為同一站牌
        if (Math.abs(existingLat - lat) < nearbyDistance && 
            Math.abs(existingLng - lng) < nearbyDistance) {
            console.log(`在附近找到現有道館 (${key})，跳過創建: ${stop.name}`);
            return null;
        }
    }
    
    // 如果沒有找到相同或相近的道館，則創建新道館
    console.log(`創建新道館: ${stop.name}`);
    
    // 記錄該位置已創建道館
    uniqueStops[positionKey] = { 
        stopName: stop.name, 
        routeName: routeName 
    };
    
    // 生成唯一ID
    const arenaId = `arena-${stop.id}`;
    
    // 創建道館級別 (1-3級，隨機生成)
    const level = Math.floor(Math.random() * 3) + 1;
    
    // 使用統一的顏色 - 深藍色
    const arenaColor = '#1565C0';
    
    // 創建道館圖標
    const iconSize = 36 + (level - 1) * 6; // 基礎大小36px，每增加一級增加6px
    
    const arenaIcon = L.divIcon({
        className: 'arena-marker',
        html: `
            <div style="
                background-color:${arenaColor};
                width:${iconSize}px;
                height:${iconSize}px;
                border-radius:50%;
                border:3px solid white;
                display:flex;
                justify-content:center;
                align-items:center;
                box-shadow:0 0 10px rgba(0,0,0,0.5);
                font-size:${16 + (level - 1) * 2}px;
                font-weight:bold;
                color:white;
            ">
                <span>⚔️</span>
                <span style="position:absolute;bottom:2px;right:2px;background:white;color:${arenaColor};border-radius:50%;width:18px;height:18px;font-size:12px;display:flex;justify-content:center;align-items:center;">${level}</span>
            </div>
        `,
        iconSize: [iconSize, iconSize],
        iconAnchor: [iconSize/2, iconSize/2],
        popupAnchor: [0, -iconSize/2]
    });
    
    // 創建道館標記
    const arenaMarker = L.marker(stop.position, {
        icon: arenaIcon,
        zIndexOffset: 1000 // 確保道館顯示在站點上方
    }).addTo(arenaLayer);
    
    // 創建道館信息對象
    const arena = {
        id: arenaId,
        name: `${stop.name}道館`,
        position: stop.position,
        level: level,
        routeName: routeName,
        stopId: stop.id,
        stopName: stop.name,
        isBackup: isBackup
    };
    
    // 將道館信息存入全局對象
    if (!window.busStopsArenas) {
        window.busStopsArenas = {};
    }
    window.busStopsArenas[arenaId] = arena;
    
    // 綁定彈出信息 - 簡化版本，只顯示名稱和等級
    arenaMarker.bindPopup(`
        <div style="text-align:center;">
            <h5>${arena.name}</h5>
            <p>等級: ${arena.level} 級</p>
            <button class="btn btn-danger mt-2 challenge-arena-btn" 
                    onclick="showArenaInfo('${arena.stopId}', '${arena.stopName}', '${arena.routeName}')">
                前往道館
            </button>
        </div>
    `);
    
    return arena;
}

// 顯示道館信息 (測試用)
function showArenaInfo(stopId, stopName, routeName) {
    console.log(`顯示道館信息: ${stopName}, ID: ${stopId}, 路線: ${routeName}`);
    
    // 跳轉到測試頁面
    window.location.href = `/game/battle?stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
}

// 顯示加載中提示
function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.visibility = 'visible';
    }
}

// 隱藏加載中提示
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.visibility = 'hidden';
    }
}

// 設置初始化和事件綁定
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM載入完成，準備初始化地圖');
});