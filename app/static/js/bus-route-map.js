// 精靈公車 - 公車路線地圖繪製 (主檔案)

// 導入所有模組
import { initMap } from './modules/map-core.js';
import { updateUserLocation } from './modules/user-location.js';
import { loadAllRoutes, loadCatRightRoute, loadCatLeftRoute, loadCatLeftZhinanRoute, loadBrown3Route } from './modules/route-manager.js';
import { loadAllBusStops } from './modules/stop-manager.js';
import { createArena, showArenaInfo, renderAllArenas } from './modules/arena-manager.js';
import { showLoading, hideLoading, showErrorMessage } from './modules/ui-utils.js';
import { 
    routeLayer,
    stopsLayer,
    busesLayer,
    creaturesLayer,
    arenaLayer,
    routeColors,
    routeCoordinates,
    routeCreatures
} from './modules/config.js';

// 從 arena-manager.js 導入新增的函數
import { checkExistingArenaForStop, updateArenaRoutes } from './modules/arena-manager.js';

// 全局暴露必要的函數給 HTML，使其可以通過onclick等直接調用
window.initMap = initMap;
window.updateUserLocation = updateUserLocation;
window.loadAllRoutes = loadAllRoutes;
window.loadCatRightRoute = loadCatRightRoute;
window.loadCatLeftRoute = loadCatLeftRoute;
window.loadCatLeftZhinanRoute = loadCatLeftZhinanRoute;
window.loadBrown3Route = loadBrown3Route;
window.loadAllBusStops = loadAllBusStops;
window.showArenaInfo = showArenaInfo;
window.createArena = createArena;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showErrorMessage = showErrorMessage;
window.renderAllArenas = renderAllArenas; // 暴露新函數

// 暴露道館等級相關的新函數
window.checkExistingArenaForStop = checkExistingArenaForStop;
window.updateArenaRoutes = updateArenaRoutes;

// 全局暴露必要的變數給其他模組可能需要用到
window.routeLayer = routeLayer;
window.stopsLayer = stopsLayer;
window.busesLayer = busesLayer;
window.creaturesLayer = creaturesLayer;  // 保留 creaturesLayer，但不生成精靈
window.arenaLayer = arenaLayer;
window.routeColors = routeColors;
window.routeCoordinates = routeCoordinates;

// 註解掉與客戶端精靈生成相關的全局變數
window.routeCreatures = routeCreatures;
// window.MAX_CREATURES_PER_ROUTE = MAX_CREATURES_PER_ROUTE;
// window.CREATURE_LIFETIME = CREATURE_LIFETIME;
// window.SPAWN_INTERVAL = SPAWN_INTERVAL;
// window.SPAWN_CHANCE = SPAWN_CHANCE;
// window.routeCreatureTypes = routeCreatureTypes;

// 初始化應用
function initApp() {
    console.log('初始化精靈公車應用');
    
    try {
        // 顯示加載中提示
        showLoading();
        
        // 檢查地圖容器是否存在
        const mapContainer = document.getElementById('map');
        if (!mapContainer) {
            console.error('找不到地圖容器元素 #map');
            showErrorMessage('地圖初始化失敗，請檢查網絡連接並刷新頁面重試。', true);
            hideLoading();
            return;
        }
        
        // 初始化地圖 (等待初始化完成再執行後續操作)
        console.log('開始初始化地圖');
        
        // 使用非同步初始化地圖
        setTimeout(() => {
            try {
                // 初始化地圖
                const map = initMap('map');
                
                // 設定一個計時器來等待地圖初始化完成
                let checkCount = 0;
                const maxChecks = 60; // 增加到60次 (30秒)，給予更充分的初始化時間
                
                const checkMapInit = setInterval(() => {
                    checkCount++;
                    console.log(`檢查地圖初始化狀態 (${checkCount}/${maxChecks})...`);
                    
                    // 檢查地圖實例和瓦片載入狀態
                    if (window.busMap && (window.tilesLoaded || checkCount > 10)) {
                        // 如果地圖存在且瓦片已載入或已檢查超過10次則繼續
                        clearInterval(checkMapInit);
                        console.log('地圖初始化完成或已達到最低檢查次數，繼續初始化應用');
                        
                        // 強制設置瓦片載入狀態為完成
                        window.tilesLoaded = true;
                        
                        // 確保地圖大小正確
                        try {
                            if (window.busMap && typeof window.busMap.invalidateSize === 'function') {
                                window.busMap.invalidateSize(true);
                            }
                        } catch (e) {
                            console.warn('地圖大小調整失敗:', e);
                        }
                        
                        // 載入所有路線
                        loadAllRoutes();
                        
                        // 修改: 使用新的流程
                        // 1. 首先只載入所有站點，但不創建道館
                        loadAllBusStops();
                        
                        // 2. 等待站點載入完成後，從緩存中載入並繪製所有道館
                        setTimeout(() => {
                            console.log('站點載入完成，開始從緩存中載入並繪製道館...');
                            renderAllArenas();
                        }, 2000); // 給予2秒的時間讓站點完全載入
                        
                        // 初始化精靈圖層，但不生成精靈
                        console.log('初始化精靈圖層，等待從Firebase加載精靈');
                        if (!window.creaturesLayer) {
                            window.creaturesLayer = L.layerGroup().addTo(window.busMap);
                        }
                                                
                        // 隱藏加載中提示
                        hideLoading();
                    } else if (checkCount >= maxChecks) {
                        // 超過最大檢查次數，視為初始化失敗
                        clearInterval(checkMapInit);
                        console.error('地圖初始化超時');
                        
                        // 嘗試直接創建最基本的地圖（緊急備用方案）
                        tryCreateEmergencyMap();
                        
                        showErrorMessage('地圖初始化花費時間過長，已切換至基本地圖模式。部分功能可能受限。', true);
                        hideLoading();
                    }
                }, 500); // 每0.5秒檢查一次
            } catch (error) {
                console.error('初始化地圖時發生錯誤:', error);
                showErrorMessage(`應用初始化失敗: ${error.message}，請檢查網絡連接並刷新頁面重試。`, true);
                hideLoading();
                
                // 嘗試直接創建最基本的地圖
                tryCreateEmergencyMap();
            }
        }, 500); // 延遲0.5秒啟動，確保DOM已完全準備好
        
    } catch (error) {
        console.error('初始化應用時發生錯誤:', error);
        showErrorMessage(`應用初始化失敗: ${error.message}，請檢查網絡連接並刷新頁面重試。`, true);
        hideLoading();
    }
}

// 嘗試創建最基本的地圖 (緊急備用方案)
function tryCreateEmergencyMap() {
    console.log('嘗試創建緊急備用地圖');
    const mapElement = document.getElementById('map');
    
    if (!mapElement || typeof L === 'undefined') {
        console.error('無法創建緊急備用地圖：缺少必要條件');
        return;
    }
    
    try {
        // 清除可能存在的舊地圖
        if (window.busMap) {
            try {
                window.busMap.remove();
            } catch(e) {
                console.warn('清理舊地圖失敗:', e);
            }
        }
        
        // 創建基本地圖
        window.busMap = L.map('map', {
            center: [25.0165, 121.5375],
            zoom: 14,
            zoomControl: true,
            attributionControl: true,
            dragging: true,       // 明確啟用拖動
            scrollWheelZoom: true, // 啟用滾輪縮放
            doubleClickZoom: true, // 啟用雙擊縮放
            touchZoom: true,      // 啟用觸控縮放
            boxZoom: true,        // 啟用框選縮放
            tap: true             // 啟用移動設備上的點擊
        });
        
        // 使用多個圖層源嘗試確保至少一個能加載
        try {
            // 嘗試 OpenStreetMap
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19
            }).addTo(window.busMap);
        } catch(e) {
            console.warn('OpenStreetMap 圖層添加失敗，嘗試備用圖層:', e);
            
            try {
                // 備用1: CartoDB
                L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
                    subdomains: 'abcd',
                    maxZoom: 19
                }).addTo(window.busMap);
            } catch(e2) {
                console.error('所有圖層添加失敗:', e2);
            }
        }
        
        // 創建必要的圖層
        window.routeLayer = L.layerGroup().addTo(window.busMap);
        window.stopsLayer = L.layerGroup().addTo(window.busMap);
        window.busesLayer = L.layerGroup().addTo(window.busMap);
        window.creaturesLayer = L.layerGroup().addTo(window.busMap);
        window.arenaLayer = L.layerGroup().addTo(window.busMap);
        
        console.log('緊急備用地圖創建成功');
        
        // 載入基本數據
        try {
            loadAllRoutes();
            loadAllBusStops();
        } catch (loadError) {
            console.warn('載入路線和站點失敗:', loadError);
        }
        
        // 強制刷新地圖大小
        setTimeout(() => {
            try {
                window.busMap.invalidateSize();
            } catch(e) {
                console.warn('刷新地圖大小失敗:', e);
            }
        }, 1000);
        
    } catch (emergencyError) {
        console.error('緊急備用地圖創建失敗:', emergencyError);
    }
}

// 設置初始化和事件綁定
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM載入完成，準備初始化地圖');
    initApp();
});

// 導出主要功能供外部使用
export { initApp };