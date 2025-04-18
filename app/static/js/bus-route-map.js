// 精靈公車 - 公車路線地圖繪製

// 定義地圖和圖層變數
let map;
let routeLayer = L.layerGroup();
let stopsLayer = L.layerGroup();
let busesLayer = L.layerGroup();
let userMarker;
let userCircle;

// 新增精靈圖層
let creaturesLayer = L.layerGroup();

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

// 儲存各路線的座標點
const routeCoordinates = {
    'cat-right': [],
    'cat-left': [],
    'cat-left-zhinan': []
};

// 路線顏色配置
const routeColors = {
    '火': '#ff5733', // 紅色系
    '水': '#33a1ff', // 藍色系
    '草': '#4caf50', // 綠色系
    '電': '#ffd700', // 黃色系
    '一般': '#9e9e9e' // 灰色系
};

// 初始化地圖
function initMap(elementId, center = [25.0408, 121.5359], zoom = 13) {
    // 創建地圖
    map = L.map(elementId).setView(center, zoom);

    // 添加OpenStreetMap圖層
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // 添加各圖層到地圖
    routeLayer.addTo(map);
    stopsLayer.addTo(map);
    busesLayer.addTo(map);
    
    // 如果有定位權限，獲取用戶位置
    if (navigator.geolocation) {
        updateUserLocation();
    }
    
    return map;
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

// 繪製指定的公車路線
function drawBusRoute(routeData) {
    // 清空現有路線圖層
    routeLayer.clearLayers();
    
    // 如果沒有路線數據，提前返回
    if (!routeData || !routeData.length) {
        console.error('未獲取到路線數據');
        return;
    }
    
    console.log('獲取到路線數據:', routeData);
    
    // 遍歷每條路線
    routeData.forEach(route => {
        // 獲取路線座標點
        const geometry = route.Geometry;
        if (!geometry) {
            console.error('路線缺少 Geometry 數據:', route);
            return;
        }
        
        // 解析路線座標
        const routeCoords = decodeLineString(geometry);
        if (routeCoords.length === 0) {
            console.error('無法解析路線座標:', geometry);
            return;
        }
        
        // 根據路線方向決定顏色
        const direction = route.Direction || 0;
        let color = direction === 0 ? '#33a1ff' : '#ff5733'; // 去程藍色，返程紅色
        
        // 創建並添加路線到地圖
        const polyline = L.polyline(routeCoords, {
            color: color,
            weight: 5,
            opacity: 0.8
        }).addTo(routeLayer);
        
        // 添加路線資訊彈窗
        const routeName = route.RouteName?.Zh_tw || '未知路線';
        const subRouteID = route.SubRouteID || '未知子路線';
        const directionStr = direction === 0 ? '去程' : '返程';
        
        polyline.bindPopup(`
            <div style="font-weight:bold;font-size:16px;">${routeName}</div>
            <div>子路線ID: ${subRouteID}</div>
            <div>方向: ${directionStr}</div>
        `);
    });
    
    // 根據路線範圍調整地圖視角
    const bounds = routeLayer.getBounds();
    if (bounds.isValid()) {
        map.fitBounds(bounds, {
            padding: [50, 50], // 增加一些內邊距
            maxZoom: 15        // 限制最大縮放層級
        });
    } else {
        console.error('無法獲取有效的路線範圍');
    }
}

// 解析 WKT 格式的 LineString 為座標數組
function decodeLineString(wkt) {
    // 檢查是否是 WKT 格式
    if (typeof wkt !== 'string' || !wkt.startsWith('LINESTRING')) {
        console.error('無效的 WKT LineString 格式');
        return [];
    }
    
    // 提取座標部分
    const coordsStr = wkt.substring(wkt.indexOf('(') + 1, wkt.lastIndexOf(')'));
    
    // 分割為單獨的座標點
    return coordsStr.split(',').map(point => {
        const [lng, lat] = point.trim().split(' ').map(parseFloat);
        return [lat, lng]; // Leaflet 使用 [lat, lng] 格式
    });
}

// 直接獲取並繪製貓空右線
function loadCatRightRoute() {
    // 顯示加載中提示
    showLoading();
    
    // 使用後端API獲取貓空右線數據 - 修正API路徑以匹配藍圖前綴
    fetch('/game/api/bus/cat-right-route')
        .then(response => {
            if (!response.ok) {
                throw new Error('無法獲取貓空右線數據');
            }
            return response.json();
        })
        .then(data => {
            console.log('API返回原始數據:', data);
            
            // 檢查數據是否為空
            if (!data || (Array.isArray(data) && data.length === 0)) {
                throw new Error('獲取到的貓空右線數據為空');
            }
            
            // 繪製獲取到的路線數據
            drawBusRoute(data);
            
            // 更新路線名稱顯示
            if (document.getElementById('routeSelect')) {
                const routeSelect = document.getElementById('routeSelect');
                routeSelect.innerHTML = '<option value="貓空右線" selected>貓空右線</option>';
            }
            
            // 添加路線圖例到地圖
            addRouteLegend();
        })
        .catch(error => {
            console.error('獲取貓空右線數據失敗:', error);
            // alert('獲取貓空右線數據失敗，請稍後再試。');
        })
        .finally(() => {
            // 隱藏加載中提示
            hideLoading();
        });
}

// 直接獲取並繪製貓空左線(動物園)
function loadCatLeftRoute() {
    // 顯示加載中提示
    showLoading();
    
    // 使用後端API獲取貓空左線(動物園)數據
    fetch('/game/api/bus/cat-left-route')
        .then(response => {
            if (!response.ok) {
                throw new Error('無法獲取貓空左線(動物園)數據');
            }
            return response.json();
        })
        .then(data => {
            console.log('API返回貓空左線數據:', data);
            
            // 檢查數據是否為空
            if (!data || (Array.isArray(data) && data.length === 0)) {
                throw new Error('獲取到的貓空左線(動物園)數據為空');
            }
            
            // 繪製獲取到的路線數據，使用綠色
            drawBusRouteWithColor(data, '#4caf50'); // 使用綠色
        })
        .catch(error => {
            console.error('獲取貓空左線(動物園)數據失敗:', error);
        })
        .finally(() => {
            // 隱藏加載中提示
            hideLoading();
        });
}

// 直接獲取並繪製貓空左線(指南宮)
function loadCatLeftZhinanRoute() {
    // 顯示加載中提示
    showLoading();
    
    // 使用後端API獲取貓空左線(指南宮)數據
    fetch('/game/api/bus/cat-left-zhinan-route')
        .then(response => {
            if (!response.ok) {
                throw new Error('無法獲取貓空左線(指南宮)數據');
            }
            return response.json();
        })
        .then(data => {
            console.log('API返回貓空左線(指南宮)數據:', data);
            
            // 檢查數據是否為空
            if (!data || (Array.isArray(data) && data.length === 0)) {
                throw new Error('獲取到的貓空左線(指南宮)數據為空');
            }
            
            // 繪製獲取到的路線數據，使用紫色
            drawBusRouteWithColor(data, '#9c27b0'); // 使用紫色
        })
        .catch(error => {
            console.error('獲取貓空左線(指南宮)數據失敗:', error);
        })
        .finally(() => {
            // 隱藏加載中提示
            hideLoading();
        });
}

// 使用指定顏色繪製公車路線
function drawBusRouteWithColor(routeData, color) {
    // 如果沒有路線數據，提前返回
    if (!routeData || !routeData.length) {
        console.error('未獲取到路線數據');
        return;
    }
    
    console.log('獲取到路線數據:', routeData);
    
    // 遍歷每條路線
    routeData.forEach(route => {
        // 獲取路線座標點
        const geometry = route.Geometry;
        if (!geometry) {
            console.error('路線缺少 Geometry 數據:', route);
            return;
        }
        
        // 解析路線座標
        const routeCoords = decodeLineString(geometry);
        if (routeCoords.length === 0) {
            console.error('無法解析路線座標:', geometry);
            return;
        }
        
        // 創建並添加路線到地圖
        const polyline = L.polyline(routeCoords, {
            color: color,
            weight: 5,
            opacity: 0.8
        }).addTo(routeLayer);
        
        // 添加路線資訊彈窗
        const routeName = route.RouteName?.Zh_tw || '未知路線';
        const subRouteID = route.SubRouteID || '未知子路線';
        const direction = route.Direction || 0;
        const directionStr = direction === 0 ? '去程' : '返程';
        
        polyline.bindPopup(`
            <div style="font-weight:bold;font-size:16px;">${routeName}</div>
            <div>子路線ID: ${subRouteID}</div>
            <div>方向: ${directionStr}</div>
        `);
    });
    
    // 根據路線範圍調整地圖視角
    const bounds = routeLayer.getBounds();
    if (bounds.isValid()) {
        map.fitBounds(bounds, {
            padding: [50, 50], // 增加一些內邊距
            maxZoom: 15        // 限制最大縮放層級
        });
    }
}

// 添加路線圖例
function addRouteLegend() {
    // 檢查圖例是否已存在
    const existingLegend = document.querySelector('.bus-routes-legend');
    if (existingLegend) {
        existingLegend.remove();
    }
    
    // 創建圖例控件
    const legend = L.control({ position: 'bottomright' });
    
    legend.onAdd = function (map) {
        const div = L.DomUtil.create('div', 'bus-routes-legend');
        div.innerHTML = `
            <h6>路線圖例</h6>
            <div><span class="route-line" style="background:#33a1ff"></span>貓空右線 (去程)</div>
            <div><span class="route-line" style="background:#ff5733"></span>貓空右線 (返程)</div>
            <div><span class="route-line" style="background:#4caf50"></span>貓空左線(動物園)</div>
            <div><span class="route-line" style="background:#9c27b0"></span>貓空左線(指南宮)</div>
        `;
        return div;
    };
    
    legend.addTo(map);
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
    // 獲取地圖容器元素
    const mapElement = document.getElementById('map');
    if (!mapElement) return;
    
    // 初始化地圖
    initMap('map');
    
    // 直接加載貓空右線
    loadCatRightRoute();
    
    // 加載貓空左線(動物園)
    loadCatLeftRoute();
    
    // 加載貓空左線(指南宮)
    loadCatLeftZhinanRoute();
    
    // 添加精靈圖層到地圖
    creaturesLayer.addTo(map);
    
    // 開始精靈生成循環
    startCreatureGeneration();
    
    // 綁定重新定位按鈕
    const refreshLocationBtn = document.getElementById('refreshLocationBtn');
    if (refreshLocationBtn) {
        refreshLocationBtn.addEventListener('click', updateUserLocation);
    }
});

// 精靈生成相關函數
// 開始精靈生成循環
function startCreatureGeneration() {
    // 首次生成
    generateRouteCreatures();
    
    // 設置定時生成 (每分鐘嘗試一次)
    setInterval(generateRouteCreatures, SPAWN_INTERVAL);
    
    // 設置定時檢查過期精靈 (每30秒檢查一次)
    setInterval(removeExpiredCreatures, 30 * 1000);
}

// 在路線上生成精靈
function generateRouteCreatures() {
    console.log('嘗試生成路線精靈...');
    
    // 獲取所有路線的路徑數據
    const routeData = routeLayer.getLayers();
    if (!routeData || routeData.length === 0) {
        console.log('沒有可用的路線數據');
        return;
    }
    
    // 檢查每條路線
    routeData.forEach(route => {
        // 判斷路線類型
        const routeColor = route.options.color;
        let routeType = 'unknown';
        
        // 根據顏色識別路線
        if (routeColor === '#33a1ff' || routeColor === '#ff5733') {
            routeType = 'cat-right'; // 貓空右線
        } else if (routeColor === '#4caf50') {
            routeType = 'cat-left'; // 貓空左線(動物園)
        } else if (routeColor === '#9c27b0') {
            routeType = 'cat-left-zhinan'; // 貓空左線(指南宮)
        }
        
        // 如果是未知路線，跳過
        if (routeType === 'unknown') return;
        
        // 獲取該路線目前已有的精靈數量
        const existingCreatureCount = routeCreatures.filter(c => c.routeType === routeType).length;
        
        // 如果已達到最大數量，不再生成
        if (existingCreatureCount >= MAX_CREATURES_PER_ROUTE) {
            console.log(`${routeType} 路線精靈已達上限 (${MAX_CREATURES_PER_ROUTE})`);
            return;
        }
        
        // 根據機率決定是否生成
        if (Math.random() > SPAWN_CHANCE) {
            console.log(`${routeType} 路線本次嘗試未生成精靈 (機率: ${SPAWN_CHANCE * 100}%)`);
            return;
        }
        
        // 從路線上隨機選擇一個點
        const routePath = route.getLatLngs();
        if (!routePath || routePath.length === 0) return;
        
        // 攤平可能的嵌套數組
        const flattenedPath = flattenLatLngs(routePath);
        if (flattenedPath.length === 0) return;
        
        // 隨機選擇點的索引
        const randomIndex = Math.floor(Math.random() * flattenedPath.length);
        const position = flattenedPath[randomIndex];
        
        // 檢查位置是否已有精靈
        const isPositionOccupied = routeCreatures.some(c => 
            c.position.lat === position.lat && c.position.lng === position.lng
        );
        
        if (isPositionOccupied) {
            console.log('選擇的位置已有精靈，跳過生成');
            return;
        }
        
        // 隨機選擇該路線的一種精靈
        const availableCreatures = routeCreatureTypes[routeType];
        const randomCreatureIndex = Math.floor(Math.random() * availableCreatures.length);
        const creatureTemplate = availableCreatures[randomCreatureIndex];
        
        // 創建新精靈實例
        const newCreature = {
            id: `${routeType}-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
            position: position,
            routeType: routeType,
            spawnedAt: Date.now(),
            // 複製精靈模板的屬性
            ...creatureTemplate
        };
        
        // 添加到精靈列表
        routeCreatures.push(newCreature);
        
        // 在地圖上添加精靈標記
        addCreatureMarker(newCreature);
        
        console.log(`在 ${routeType} 路線上生成了 ${newCreature.name}`);
    });
    
    // 更新UI上的精靈顯示
    updateCreaturesList();
}

// 攤平可能的嵌套LatLng數組
function flattenLatLngs(latlngs) {
    let result = [];
    
    if (!latlngs) return result;
    
    // 處理單一點
    if (latlngs.lat !== undefined && latlngs.lng !== undefined) {
        return [latlngs];
    }
    
    // 處理數組
    if (Array.isArray(latlngs)) {
        for (let i = 0; i < latlngs.length; i++) {
            const item = latlngs[i];
            
            // 如果是普通點
            if (item.lat !== undefined && item.lng !== undefined) {
                result.push(item);
            } 
            // 如果是嵌套數組
            else if (Array.isArray(item)) {
                result = result.concat(flattenLatLngs(item));
            }
        }
    }
    
    return result;
}

// 在地圖上添加精靈標記
function addCreatureMarker(creature) {
    // 創建精靈圖標
    const creatureIcon = L.divIcon({
        className: 'creature-marker',
        html: `<div style="background-color:#64dd17;width:20px;height:20px;border-radius:50%;border:2px solid white;display:flex;justify-content:center;align-items:center;font-size:14px;font-weight:bold;color:white;">✧</div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });
    
    // 創建標記
    const marker = L.marker(creature.position, {
        icon: creatureIcon,
        creatureId: creature.id // 儲存精靈ID以便後續引用
    }).addTo(creaturesLayer);
    
    // 添加彈出信息
    marker.bindPopup(`
        <div style="text-align:center;">
            <h5>${creature.name}</h5>
            <div>類型：<span class="badge bg-secondary">${creature.type}</span></div>
            <div>稀有度：${creature.rarity}</div>
            <div>力量：${creature.power}</div>
            <button class="btn btn-sm btn-success mt-2" onclick="catchCreatureFromMap('${creature.id}')">捕捉</button>
        </div>
    `);
    
    // 儲存標記引用
    creature.marker = marker;
}

// 移除過期的精靈
function removeExpiredCreatures() {
    const currentTime = Date.now();
    const expiredCreatures = routeCreatures.filter(
        creature => (currentTime - creature.spawnedAt) > CREATURE_LIFETIME
    );
    
    if (expiredCreatures.length > 0) {
        console.log(`移除 ${expiredCreatures.length} 隻過期精靈`);
        
        // 遍歷並移除過期精靈
        expiredCreatures.forEach(creature => {
            // 從地圖上移除標記
            if (creature.marker) {
                creaturesLayer.removeLayer(creature.marker);
            }
            
            // 從列表中移除
            const index = routeCreatures.findIndex(c => c.id === creature.id);
            if (index !== -1) {
                routeCreatures.splice(index, 1);
            }
        });
        
        // 更新UI
        updateCreaturesList();
    }
}

// 更新UI上的精靈列表顯示
function updateCreaturesList() {
    const creatureList = document.getElementById('creatureList');
    if (!creatureList) return;
    
    // 清空現有內容
    creatureList.innerHTML = '';
    
    // 如果沒有精靈，顯示提示
    if (routeCreatures.length === 0) {
        creatureList.innerHTML = `
            <div class="col-12 text-center py-5">
                <p>目前公車路線上沒有發現精靈，請稍後再試！</p>
                <p class="text-muted">提示：精靈每分鐘有 ${SPAWN_CHANCE * 100}% 的機率在路線上出現</p>
            </div>
        `;
        return;
    }
    
    // 添加每個精靈卡片
    routeCreatures.forEach(creature => {
        const creatureCard = document.createElement('div');
        creatureCard.className = 'col-md-4 col-sm-6';
        creatureCard.innerHTML = `
            <div class="card creature-card">
                <img src="${creature.img}" class="card-img-top" alt="${creature.name}">
                <div class="card-body">
                    <h5 class="card-title">${creature.name}</h5>
                    <p class="card-text">
                        類型: <span class="badge bg-secondary">${creature.type}</span><br>
                        稀有度: ${creature.rarity}<br>
                        力量: ${creature.power}<br>
                        路線: ${getRouteNameByType(creature.routeType)}
                    </p>
                    <button class="btn btn-success catch-btn" data-creature-id="${creature.id}">捕捉</button>
                </div>
            </div>
        `;
        
        creatureList.appendChild(creatureCard);
    });
    
    // 為所有捕捉按鈕添加事件
    document.querySelectorAll('.catch-btn').forEach(button => {
        button.addEventListener('click', function() {
            const creatureId = this.getAttribute('data-creature-id');
            catchCreature(creatureId);
        });
    });
}

// 根據路線類型獲取路線名稱
function getRouteNameByType(routeType) {
    switch (routeType) {
        case 'cat-right': return '貓空右線';
        case 'cat-left': return '貓空左線(動物園)';
        case 'cat-left-zhinan': return '貓空左線(指南宮)';
        default: return '未知路線';
    }
}

// 從地圖捕捉精靈
function catchCreatureFromMap(creatureId) {
    catchCreature(creatureId);
    // 關閉彈出窗口
    map.closePopup();
}