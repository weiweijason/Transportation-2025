// 模組：map-core.js - 地圖核心功能

import {
    map,
    routeLayer,
    stopsLayer,
    busesLayer,
    creaturesLayer,
    arenaLayer
} from './config.js';

import { updateUserLocation } from './user-location.js';
import { showErrorMessage } from './ui-utils.js';

// 全局參考以便於清理
let mapInstance = null;
let networkChecked = false;
let tilesLoaded = false;

// 將 tilesLoaded 變數暴露到全局，以便其他模組可以檢查地圖加載狀態
window.tilesLoaded = false;

// 檢查網絡連接狀態
function checkNetworkConnection() {
    return new Promise((resolve, reject) => {
        // 如果瀏覽器線上，嘗試發送一個小型請求確認連接
        if (navigator.onLine) {
            // 創建一個圖片請求來測試連接
            const tester = new Image();
            let timeout = setTimeout(() => {
                tester.onerror = tester.onload = null;
                reject(new Error('網絡連接超時'));
            }, 5000);

            tester.onerror = function() {
                clearTimeout(timeout);
                console.warn('網絡連接測試失敗');
                reject(new Error('網絡連接測試失敗'));
            };

            tester.onload = function() {
                clearTimeout(timeout);
                console.log('網絡連接正常');
                resolve(true);
            };

            // 使用 OpenStreetMap 的小圖標作為測試
            const testTime = new Date().getTime();
            tester.src = 'https://tile.openstreetmap.org/0/0/0.png?' + testTime;
        } else {
            console.warn('瀏覽器離線');
            reject(new Error('瀏覽器顯示當前處於離線狀態'));
        }
    });
}

// 顯示指定頁面元素的載入狀態
function showLoadingState(elementId, message = '正在加載地圖...') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // 保存原始內容
    element.dataset.originalContent = element.innerHTML;
    
    // 設置加載中訊息
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'map-loading-indicator';
    loadingDiv.style.position = 'absolute';
    loadingDiv.style.top = '50%';
    loadingDiv.style.left = '50%';
    loadingDiv.style.transform = 'translate(-50%, -50%)';
    loadingDiv.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
    loadingDiv.style.padding = '15px';
    loadingDiv.style.borderRadius = '5px';
    loadingDiv.style.zIndex = '1000';
    loadingDiv.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.1)';
    loadingDiv.innerHTML = `<div style="text-align:center">
        <div style="margin-bottom:10px">${message}</div>
        <div style="width:40px;height:40px;border:4px solid #f3f3f3;border-top:4px solid #3498db;border-radius:50%;margin:0 auto;animation:spin 2s linear infinite"></div>
    </div>
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>`;
    
    // 確保元素有合適的定位
    const computedStyle = window.getComputedStyle(element);
    if (computedStyle.position === 'static') {
        element.style.position = 'relative';
    }
    
    element.appendChild(loadingDiv);
    return loadingDiv;
}

// 移除載入狀態
function removeLoadingState(elementId, loadingElement) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (loadingElement && element.contains(loadingElement)) {
        element.removeChild(loadingElement);
    }
    
    // 恢復原始狀態
    if (element.dataset.originalContent !== undefined) {
        // 不恢復內容，因為地圖可能已經初始化
    }
}

// 檢查本地資源可用性
function checkLocalResources() {
    return new Promise((resolve, reject) => {
        // 檢查本地資源檔案
        fetch('/game/api/bus/cat-right-route', { 
            method: 'HEAD',
            cache: 'no-cache'
        })
        .then(response => {
            if (response.ok) {
                console.log('本地路線資源可用');
                resolve(true);
            } else {
                console.warn('本地路線資源不可用');
                reject(new Error('無法訪問路線資料'));
            }
        })
        .catch(error => {
            console.error('檢查本地資源時出錯:', error);
            reject(error);
        });
    });
}

// 初始化地圖
function initMap(elementId, center = [25.0165, 121.5375], zoom = 14) {
    console.log('開始初始化地圖, elementId:', elementId);
    
    // 檢查元素是否存在
    const mapElement = document.getElementById(elementId);
    if (!mapElement) {
        console.error(`地圖容器元素 #${elementId} 不存在`);
        if (typeof showErrorMessage === 'function') {
            showErrorMessage(`無法找到地圖容器元素 #${elementId}，請檢查網絡連接並刷新頁面重試。`, true);
        } else {
            alert(`無法找到地圖容器元素 #${elementId}，請檢查網絡連接並刷新頁面重試。`);
        }
        return null;
    }
    
    // 檢查 Leaflet 是否已載入
    if (typeof L === 'undefined') {
        console.error('Leaflet 庫未載入');
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('地圖初始化失敗：Leaflet 地圖庫未能載入，請檢查網絡連接並刷新頁面重試。', true);
        } else {
            alert('地圖初始化失敗：Leaflet 地圖庫未能載入，請檢查網絡連接並刷新頁面重試。');
        }
        return null;
    }
    
    // 顯示載入狀態
    const loadingIndicator = showLoadingState(elementId, '正在初始化地圖...');
    
    // 檢查網絡連接和本地資源 (只在啟動時檢查一次)
    if (!networkChecked) {
        // 首先檢查網絡連接
        checkNetworkConnection()
            .then(() => {
                console.log('網絡連接正常，檢查本地資源...');
                // 然後檢查本地資源
                return checkLocalResources();
            })
            .then(() => {
                console.log('所有檢查都通過，繼續初始化地圖');
                networkChecked = true;
                // 一切就緒，繼續初始化地圖
                return continueInitMap();
            })
            .catch(err => {
                console.error('初始化前檢查失敗:', err);
                removeLoadingState(elementId, loadingIndicator);
                
                let errorMessage = '地圖初始化失敗：';
                if (err.message.includes('網絡')) {
                    errorMessage += '無法連接到地圖服務。請檢查您的網絡連接並刷新頁面重試。';
                } else if (err.message.includes('路線資料')) {
                    errorMessage += '無法載入地圖資料。請確認服務器狀態並刷新頁面重試。';
                } else {
                    errorMessage += `${err.message}，請檢查網絡連接並刷新頁面重試。`;
                }
                
                if (typeof showErrorMessage === 'function') {
                    showErrorMessage(errorMessage, true);
                } else {
                    alert(errorMessage);
                }
                return null;
            });
    } else {
        // 已經檢查過網絡和資源，直接初始化
        continueInitMap();
    }
    
    // 地圖初始化函數由可能返回完成的地圖實例或 null
    return mapInstance;

    // 地圖初始化的主要邏輯
    function continueInitMap() {
        try {
            // 安全清理：確保在創建新地圖前清理舊的資源
            try {
                // 檢查是否已有地圖實例，如果有，則清理
                if (mapInstance) {
                    console.log('已存在地圖實例，清理後重新初始化');
                    mapInstance.remove();
                    mapInstance = null;
                }
                
                // 如果 window.busMap 存在，也需要清理
                if (window.busMap && window.busMap !== mapInstance) {
                    console.log('全局 busMap 存在，清理它');
                    window.busMap.remove();
                    window.busMap = null;
                }
            } catch (cleanupError) {
                console.warn('清理舊地圖時出現非關鍵錯誤，繼續初始化:', cleanupError);
            }
            
            // 重置各圖層
            try {
                routeLayer.clearLayers();
                stopsLayer.clearLayers();
                busesLayer.clearLayers();
                creaturesLayer.clearLayers();
                arenaLayer.clearLayers();
            } catch (layerError) {
                console.warn('清理圖層時出現錯誤，重新創建圖層:', layerError);
                // 如果清理失敗，重新創建圖層
                window.routeLayer = L.layerGroup();
                window.stopsLayer = L.layerGroup();
                window.busesLayer = L.layerGroup();
                window.creaturesLayer = L.layerGroup();
                window.arenaLayer = L.layerGroup();
            }
            
            // 創建地圖，添加錯誤處理選項
            console.log('創建地圖實例, center:', center, 'zoom:', zoom);

            // Leaflet 1.7+ 會在 DOM 元素上加 _leaflet_id 屬性，避免重複初始化
            const mapElement = document.getElementById(elementId);
            if (mapElement && mapElement._leaflet_id) {
                mapElement._leaflet_id = null;
                mapElement.innerHTML = '';
            }

            // 設置初始化超時
            let initTimeout = setTimeout(() => {
                if (!tilesLoaded) {
                    console.error('地圖瓦片加載超時');
                    if (typeof showErrorMessage === 'function') {
                        showErrorMessage('地圖初始化超時。請檢查您的網絡連接並刷新頁面重試。', true);
                    }
                }
            }, 20000); // 20秒超時
            
            mapInstance = L.map(elementId, {
                // 添加更多容錯選項
                attributionControl: true,
                zoomControl: true,
                closePopupOnClick: true,
                maxBoundsViscosity: 1.0,
                // 添加錯誤處理回調
                worldCopyJump: true,
                preferCanvas: true // 使用 Canvas 渲染可能提高效能
            }).setView(center, zoom);
            
            console.log('地圖實例已創建');

            // 添加OpenStreetMap圖層 (使用備用地圖源以防主要源失效)
            console.log('添加OpenStreetMap圖層');
            let tileLoadErrors = 0;
            const MAX_TILE_ERRORS = 5;
            
            // 主要地圖瓦片源
            const mainTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19,
                subdomains: 'abc',
                // 添加重試選項
                errorTileUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFdgIQokjwPQAAAABJRU5ErkJggg==', // 透明像素
                crossOrigin: true
            });
            
            // 監聽瓦片加載事件
            let tilesTotal = 0;
            let tilesLoadedCount = 0; // 修正變數名稱，避免與外層 tilesLoaded 衝突
            
            mainTileLayer.on('loading', function() {
                console.log('開始加載地圖瓦片');
            });
            
            mainTileLayer.on('load', function() {
                console.log('地圖瓦片加載完成');
                tilesLoaded = true;
                clearTimeout(initTimeout);
            });
            
            mainTileLayer.on('tileloadstart', function() {
                tilesTotal++;
            });
            
            mainTileLayer.on('tileload', function() {
                tilesLoadedCount++;
                // 當加載了至少9個瓦片(3x3視圖)，認為地圖基本可用
                if (tilesLoadedCount >= 9 && !tilesLoaded) {
                    tilesLoaded = true;
                    clearTimeout(initTimeout);
                }
            });
            
            mainTileLayer.on('tileerror', function(error) {
                console.warn('主地圖瓦片加載錯誤:', error);
                tileLoadErrors++;
                
                if (tileLoadErrors > MAX_TILE_ERRORS && !tilesLoaded) {
                    console.warn(`已有${tileLoadErrors}個地圖瓦片加載失敗，嘗試使用備用地圖源`);
                    // 嘗試移除並使用備用源
                    try {
                        mainTileLayer.remove();
                    } catch(e) {
                        console.warn('移除主地圖層失敗:', e);
                    }
                    useFallbackLayer();
                }
            });
            
            function useFallbackLayer() {
                // 備用地圖源1: CartoDB
                console.log('嘗試使用備用地圖源 1');
                const fallbackTileLayer1 = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                    subdomains: 'abcd',
                    maxZoom: 19,
                    errorTileUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFdgIQokjwPQAAAABJRU5ErkJggg=='
                });
                
                fallbackTileLayer1.on('load', function() {
                    console.log('備用地圖源1加載完成');
                    tilesLoaded = true;
                    clearTimeout(initTimeout);
                });
                
                fallbackTileLayer1.on('tileerror', function(error) {
                    console.warn('備用地圖源1加載錯誤:', error);
                    
                    // 嘗試移除並使用第二備用源
                    try {
                        fallbackTileLayer1.remove();
                    } catch(e) {
                        console.warn('移除備用地圖層1失敗:', e);
                    }
                    
                    // 備用地圖源2: Stamen
                    console.log('嘗試使用備用地圖源 2');
                    const fallbackTileLayer2 = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}{r}.png', {
                        attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                        subdomains: 'abcd',
                        maxZoom: 18,
                        errorTileUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFdgIQokjwPQAAAABJRU5ErkJggg=='
                    });
                    
                    fallbackTileLayer2.on('load', function() {
                        console.log('備用地圖源2加載完成');
                        tilesLoaded = true;
                        clearTimeout(initTimeout);
                    });
                    
                    fallbackTileLayer2.on('tileerror', function() {
                        console.error('備用地圖源2也加載失敗，可能是網絡問題');
                        
                        // 所有地圖源都失敗了
                        if (typeof showErrorMessage === 'function') {
                            showErrorMessage('地圖瓦片加載失敗，請檢查您的網絡連接並刷新頁面重試。', true);
                        } else {
                            alert('地圖瓦片加載失敗，請檢查您的網絡連接並刷新頁面重試。');
                        }
                    });
                    
                    // 嘗試添加第二備用源
                    try {
                        fallbackTileLayer2.addTo(mapInstance);
                    } catch(e) {
                        console.error('添加備用地圖層2失敗:', e);
                        showFatalError('無法載入任何地圖資源，請檢查網絡並重試。');
                    }
                });
                
                // 嘗試添加第一備用源
                try {
                    fallbackTileLayer1.addTo(mapInstance);
                } catch(e) {
                    console.error('添加備用地圖層1失敗:', e);
                    showFatalError('無法載入地圖資源，請檢查網絡並重試。');
                }
            }
            
            // 嘗試添加主地圖源
            try {
                mainTileLayer.addTo(mapInstance);
            } catch(e) {
                console.error('添加主地圖層失敗:', e);
                useFallbackLayer();
            }
            
            console.log('OpenStreetMap圖層已添加');

            // 添加各圖層到地圖
            console.log('添加其他圖層到地圖');
            
            try {
                routeLayer.addTo(mapInstance);
                stopsLayer.addTo(mapInstance);
                busesLayer.addTo(mapInstance);
                creaturesLayer.addTo(mapInstance);
                arenaLayer.addTo(mapInstance);
                console.log('所有圖層已添加到地圖');
            } catch(e) {
                console.error('添加圖層失敗:', e);
                showFatalError('添加地圖圖層失敗，請刷新頁面重試。');
                return null;
            }
            
            // 全局引用
            window.busMap = mapInstance;
            
            // 如果有定位權限，獲取用戶位置（加入錯誤處理）
            if (navigator.geolocation) {
                console.log('嘗試獲取用戶位置');
                try {
                    updateUserLocation().catch(err => {
                        console.warn('獲取用戶位置失敗，使用默認位置:', err);
                    });
                } catch (locationError) {
                    console.warn('獲取用戶位置時出錯:', locationError);
                }
            } else {
                console.log('瀏覽器不支持地理定位');
            }
            
            // 觸發一次resize事件以確保地圖正確渲染
            setTimeout(() => {
                console.log('觸發地圖resize事件');
                if (mapInstance) {
                    try {
                        mapInstance.invalidateSize();
                    } catch(e) {
                        console.warn('調整地圖大小失敗:', e);
                    }
                }
                
                // 移除載入狀態
                removeLoadingState(elementId, loadingIndicator);
            }, 1000); // 增加延遲以確保DOM已完全渲染
            
            // 註冊視窗大小變更事件（只註冊一次）
            if (!window._mapResizeHandlerAdded) {
                window.addEventListener('resize', function() {
                    console.log('視窗大小改變，重新調整地圖大小');
                    if (mapInstance) {
                        try {
                            mapInstance.invalidateSize();
                        } catch(e) {
                            console.warn('調整地圖大小失敗:', e);
                        }
                    }
                });
                window._mapResizeHandlerAdded = true;
            }
            
            // 設置地圖載入事件
            mapInstance.on('load', function() {
                console.log('地圖完全載入');
                removeLoadingState(elementId, loadingIndicator);
            });
            
            console.log('地圖初始化完成');
            return mapInstance;
        } catch (error) {
            console.error('初始化地圖時發生錯誤:', error);
            removeLoadingState(elementId, loadingIndicator);
            
            // 提供更具體的錯誤信息給用戶
            let errorMessage = '地圖初始化失敗，請檢查網絡連接並刷新頁面重試。';
            
            if (error.message) {
                if (error.message.includes('container')) {
                    errorMessage = '地圖容器初始化失敗，請檢查網絡連接並刷新頁面重試。';
                } else if (error.message.includes('already initialized')) {
                    errorMessage = '地圖已經被初始化，請刷新頁面後再試。';
                } else if (error.message.includes('network') || error.message.includes('資源') || error.message.includes('連接')) {
                    errorMessage = '無法載入地圖資源，請檢查您的網絡連接並刷新頁面重試。';
                } else {
                    errorMessage = `地圖初始化時發生錯誤: ${error.message}，請刷新頁面重試。`;
                }
            }
            
            showFatalError(errorMessage);
            return null;
        }
    }
    
    // 顯示嚴重錯誤
    function showFatalError(message) {
        if (typeof showErrorMessage === 'function') {
            showErrorMessage(message, true);
        } else {
            alert(message);
        }
        
        // 移除載入狀態
        removeLoadingState(elementId, loadingIndicator);
    }
}

// 導出模組
export { initMap, checkNetworkConnection };