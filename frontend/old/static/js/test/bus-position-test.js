/**
 * 公車位置功能測試腳本
 * 用於驗證公車標記在地圖上的顯示和交互功能
 */

console.log('公車位置功能測試開始...');

// 測試公車位置載入
function testBusPositionLoading() {
    console.log('測試公車位置載入功能...');
    
    // 檢查必要的函數是否存在
    const requiredFunctions = [
        'initBusPositionLayer',
        'loadAllBusPositions', 
        'updateBusPositions',
        'clearBusMarkers',
        'toggleBusLayer'
    ];
    
    let missingFunctions = [];
    requiredFunctions.forEach(funcName => {
        if (typeof window[funcName] !== 'function') {
            missingFunctions.push(funcName);
        }
    });
    
    if (missingFunctions.length > 0) {
        console.error('缺少以下必要函數:', missingFunctions);
        return false;
    }
    
    console.log('所有必要函數都已載入');
    return true;
}

// 測試公車數據文件
async function testBusDataFiles() {
    console.log('測試公車數據文件...');
    
    const busDataFiles = [
        '/static/data/bus/br3_bus.json',
        '/static/data/bus/cat_left_bus.json',
        '/static/data/bus/cat_left_zhinan_bus.json',
        '/static/data/bus/cat_right_bus.json'
    ];
    
    let results = {};
    
    for (const file of busDataFiles) {
        try {
            const response = await fetch(file);
            if (response.ok) {
                const data = await response.json();
                results[file] = {
                    success: true,
                    busCount: Array.isArray(data) ? data.length : 0,
                    data: data
                };
                console.log(`✓ ${file}: ${results[file].busCount} 輛公車`);
            } else {
                results[file] = {
                    success: false,
                    error: `HTTP ${response.status}`
                };
                console.error(`✗ ${file}: ${results[file].error}`);
            }
        } catch (error) {
            results[file] = {
                success: false,
                error: error.message
            };
            console.error(`✗ ${file}: ${error.message}`);
        }
    }
    
    return results;
}

// 測試地圖是否就緒
function testMapReady() {
    console.log('測試地圖就緒狀態...');
    
    const map = window.gameMap || window.busMap;
    if (!map) {
        console.error('地圖實例不存在');
        return false;
    }
    
    if (!map._loaded) {
        console.error('地圖尚未載入完成');
        return false;
    }
    
    if (!map._container) {
        console.error('地圖容器不存在');
        return false;
    }
    
    console.log('地圖已就緒');
    return true;
}

// 模擬公車位置載入
async function simulateBusPositionLoad() {
    console.log('模擬公車位置載入...');
    
    if (!testMapReady()) {
        console.error('地圖未就緒，無法載入公車位置');
        return false;
    }
    
    try {
        // 初始化公車位置圖層
        if (typeof window.initBusPositionLayer === 'function') {
            const map = window.gameMap || window.busMap;
            window.initBusPositionLayer(map);
            console.log('公車位置圖層初始化完成');
        }
        
        // 載入公車位置
        if (typeof window.loadAllBusPositions === 'function') {
            await window.loadAllBusPositions();
            console.log('公車位置載入完成');
        }
        
        return true;
    } catch (error) {
        console.error('公車位置載入失敗:', error);
        return false;
    }
}

// 執行完整測試
async function runFullTest() {
    console.log('執行完整公車位置功能測試...');
    
    // 1. 測試函數載入
    const functionsLoaded = testBusPositionLoading();
    
    // 2. 測試數據文件
    const dataFileResults = await testBusDataFiles();
    
    // 3. 測試地圖就緒
    const mapReady = testMapReady();
    
    // 4. 模擬載入
    const loadSuccess = await simulateBusPositionLoad();
    
    // 總結測試結果
    console.log('=== 測試結果總結 ===');
    console.log('函數載入:', functionsLoaded ? '✓' : '✗');
    console.log('地圖就緒:', mapReady ? '✓' : '✗');
    console.log('公車位置載入:', loadSuccess ? '✓' : '✗');
    
    console.log('數據文件測試結果:');
    Object.entries(dataFileResults).forEach(([file, result]) => {
        console.log(`  ${file.split('/').pop()}: ${result.success ? '✓' : '✗'} (${result.busCount || 0} 輛公車)`);
    });
    
    const overallSuccess = functionsLoaded && mapReady && loadSuccess;
    console.log(`\n整體測試結果: ${overallSuccess ? '✓ 成功' : '✗ 失敗'}`);
    
    return {
        functionsLoaded,
        mapReady,
        loadSuccess,
        dataFileResults,
        overallSuccess
    };
}

// 自動執行測試（等待DOM載入完成）
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(runFullTest, 3000); // 延遲3秒等待其他模組載入
    });
} else {
    setTimeout(runFullTest, 3000);
}

// 將測試函數暴露到全局
window.testBusPositionFeatures = {
    testBusPositionLoading,
    testBusDataFiles,
    testMapReady,
    simulateBusPositionLoad,
    runFullTest
};
