// 精靈公車 - 公車路線地圖繪製

// 定義地圖和圖層變數
let map;
let routeLayer = L.layerGroup();
let stopsLayer = L.layerGroup();
let busesLayer = L.layerGroup();
let userMarker;
let userCircle;

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
    
    // 綁定重新定位按鈕
    const refreshLocationBtn = document.getElementById('refreshLocationBtn');
    if (refreshLocationBtn) {
        refreshLocationBtn.addEventListener('click', updateUserLocation);
    }
});