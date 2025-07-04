/**
 * 移動設備全螢幕地圖測試腳本
 * 用於驗證地圖是否在移動設備上正確全螢幕顯示
 */

console.log('=== 移動設備全螢幕地圖測試 ===');

/**
 * 檢測設備類型
 */
function detectDevice() {
    const isMobile = window.innerWidth <= 768;
    const isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
    const isDesktop = window.innerWidth > 1024;
    
    const userAgent = navigator.userAgent.toLowerCase();
    const isIOS = /iphone|ipad|ipod/.test(userAgent);
    const isAndroid = /android/.test(userAgent);
    
    return {
        isMobile,
        isTablet,
        isDesktop,
        isIOS,
        isAndroid,
        screenWidth: window.innerWidth,
        screenHeight: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio || 1
    };
}

/**
 * 檢查viewport設置
 */
function checkViewportSettings() {
    console.log('檢查viewport設置...');
    
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
        console.log('✓ Viewport meta標籤存在:', viewport.content);
    } else {
        console.log('❌ 缺少viewport meta標籤');
        return false;
    }
    
    // 檢查CSS變數
    const computedStyle = getComputedStyle(document.documentElement);
    const vhValue = computedStyle.getPropertyValue('--vh');
    console.log('CSS --vh 變數值:', vhValue);
    
    return true;
}

/**
 * 檢查地圖容器尺寸
 */
function checkMapContainerSize() {
    console.log('檢查地圖容器尺寸...');
    
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.log('❌ 地圖容器不存在');
        return false;
    }
    
    const containerInfo = {
        offsetWidth: mapContainer.offsetWidth,
        offsetHeight: mapContainer.offsetHeight,
        clientWidth: mapContainer.clientWidth,
        clientHeight: mapContainer.clientHeight,
        scrollWidth: mapContainer.scrollWidth,
        scrollHeight: mapContainer.scrollHeight,
        computedStyle: getComputedStyle(mapContainer)
    };
    
    console.log('地圖容器信息:', containerInfo);
    
    // 檢查是否填滿螢幕
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    const widthMatch = Math.abs(containerInfo.offsetWidth - screenWidth) <= 2;
    const heightMatch = Math.abs(containerInfo.offsetHeight - screenHeight) <= 50; // 允許地址欄高度差異
    
    console.log('尺寸匹配檢查:', {
        螢幕寬度: screenWidth,
        容器寬度: containerInfo.offsetWidth,
        寬度匹配: widthMatch,
        螢幕高度: screenHeight,
        容器高度: containerInfo.offsetHeight,
        高度匹配: heightMatch
    });
    
    return widthMatch && heightMatch;
}

/**
 * 檢查地圖實例
 */
function checkMapInstance() {
    console.log('檢查地圖實例...');
    
    const map = window.gameMap || window.busMap;
    if (!map) {
        console.log('❌ 地圖實例不存在');
        return false;
    }
    
    const mapInfo = {
        hasContainer: !!map._container,
        isLoaded: map._loaded,
        hasSize: map._size && map._size.x > 0 && map._size.y > 0,
        center: map.getCenter(),
        zoom: map.getZoom(),
        bounds: map.getBounds()
    };
    
    console.log('地圖實例信息:', mapInfo);
    
    return mapInfo.hasContainer && mapInfo.isLoaded && mapInfo.hasSize;
}

/**
 * 測試觸控功能
 */
function testTouchFunctionality() {
    console.log('測試觸控功能...');
    
    const deviceInfo = detectDevice();
    if (!deviceInfo.isMobile) {
        console.log('非移動設備，跳過觸控測試');
        return true;
    }
    
    // 檢查觸控事件支援
    const hasTouchEvents = 'ontouchstart' in window;
    const hasPointerEvents = 'onpointerdown' in window;
    const hasGestures = 'ongesturestart' in window;
    
    console.log('觸控功能支援:', {
        touchEvents: hasTouchEvents,
        pointerEvents: hasPointerEvents,
        gestures: hasGestures
    });
    
    return hasTouchEvents || hasPointerEvents;
}

/**
 * 執行完整測試
 */
function runFullscreenMapTest() {
    console.log('\n開始執行移動設備全螢幕地圖測試...');
    
    // 1. 設備檢測
    const deviceInfo = detectDevice();
    console.log('\n=== 設備信息 ===');
    console.log(deviceInfo);
    
    // 2. Viewport檢查
    console.log('\n=== Viewport檢查 ===');
    const viewportOK = checkViewportSettings();
    
    // 3. 容器尺寸檢查
    console.log('\n=== 容器尺寸檢查 ===');
    const containerOK = checkMapContainerSize();
    
    // 4. 地圖實例檢查
    console.log('\n=== 地圖實例檢查 ===');
    const mapOK = checkMapInstance();
    
    // 5. 觸控功能測試
    console.log('\n=== 觸控功能測試 ===');
    const touchOK = testTouchFunctionality();
    
    // 總結結果
    console.log('\n=== 測試結果總結 ===');
    console.log('設備類型:', deviceInfo.isMobile ? '📱 移動設備' : deviceInfo.isTablet ? '📟 平板設備' : '💻 桌面設備');
    console.log('Viewport設置:', viewportOK ? '✓' : '❌');
    console.log('容器尺寸:', containerOK ? '✓ 全螢幕' : '❌ 未全螢幕');
    console.log('地圖實例:', mapOK ? '✓' : '❌');
    console.log('觸控功能:', touchOK ? '✓' : '❌');
    
    const overallSuccess = viewportOK && containerOK && mapOK && touchOK;
    
    if (overallSuccess) {
        console.log('🎉 全螢幕地圖測試通過！');
        if (typeof window.showGameAlert === 'function') {
            window.showGameAlert('移動設備全螢幕顯示正常', 'success', 3000);
        }
    } else {
        console.log('⚠️ 測試發現問題，需要檢查');
        
        // 提供修復建議
        if (!containerOK) {
            console.log('💡 建議修復: 檢查CSS viewport高度設置');
        }
        if (!mapOK) {
            console.log('💡 建議修復: 重新初始化地圖實例');
        }
        
        if (typeof window.showGameAlert === 'function') {
            window.showGameAlert('發現顯示問題，請查看控制台', 'warning', 4000);
        }
    }
    
    return {
        deviceInfo,
        viewportOK,
        containerOK,
        mapOK,
        touchOK,
        overallSuccess
    };
}

/**
 * 修復常見問題
 */
function fixCommonIssues() {
    console.log('嘗試修復常見問題...');
    
    // 修復1: 重新設置viewport高度
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
    console.log('✓ 重新設置viewport高度');
    
    // 修復2: 強制地圖容器尺寸
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        mapContainer.style.width = '100vw';
        mapContainer.style.height = 'calc(var(--vh, 1vh) * 100)';
        mapContainer.style.position = 'fixed';
        mapContainer.style.top = '0';
        mapContainer.style.left = '0';
        console.log('✓ 重新設置地圖容器樣式');
    }
    
    // 修復3: 重新調整地圖尺寸
    const map = window.gameMap || window.busMap;
    if (map && typeof map.invalidateSize === 'function') {
        setTimeout(() => {
            map.invalidateSize();
            console.log('✓ 重新調整地圖尺寸');
        }, 100);
    }
    
    console.log('修復完成，請重新測試');
}

// 等待頁面完全載入後執行測試
if (document.readyState === 'complete') {
    setTimeout(runFullscreenMapTest, 2000);
} else {
    window.addEventListener('load', () => {
        setTimeout(runFullscreenMapTest, 2000);
    });
}

// 將函數暴露到全域
window.fullscreenMapTest = {
    detectDevice,
    checkViewportSettings,
    checkMapContainerSize,
    checkMapInstance,
    testTouchFunctionality,
    runFullscreenMapTest,
    fixCommonIssues
};

console.log('移動設備全螢幕地圖測試腳本已載入');
console.log('手動執行測試: window.fullscreenMapTest.runFullscreenMapTest()');
console.log('嘗試修復問題: window.fullscreenMapTest.fixCommonIssues()');
