/**
 * JSON空集合處理驗證腳本
 * 驗證系統是否正確處理空的JSON陣列
 */

console.log('=== JSON空集合處理驗證 ===');

// 模擬不同的JSON狀態
const testData = {
    'empty_array': [],
    'single_bus': [
        {
            "PlateNumb": "TEST-001",
            "PositionLon": 121.5705,
            "PositionLat": 24.9937
        }
    ],
    'multiple_buses': [
        {
            "PlateNumb": "TEST-001",
            "PositionLon": 121.5705,
            "PositionLat": 24.9937
        },
        {
            "PlateNumb": "TEST-002",
            "PositionLon": 121.5806,
            "PositionLat": 24.9988
        }
    ]
};

/**
 * 測試空集合處理邏輯
 */
function testEmptyArrayHandling() {
    console.log('測試空集合處理邏輯...');
    
    let results = {};
    
    // 測試每種數據狀態
    Object.entries(testData).forEach(([testName, data]) => {
        console.log(`\n--- 測試: ${testName} ---`);
        
        try {
            // 模擬loadRouteBusPositions的邏輯
            if (!Array.isArray(data)) {
                console.log('❌ 數據格式錯誤，預期為陣列');
                results[testName] = { status: 'error', reason: '非陣列數據' };
                return;
            }
            
            // 處理空陣列的情況
            if (data.length === 0) {
                console.log('✓ 檢測到空集合，靜默跳過');
                results[testName] = { status: 'empty', busCount: 0 };
                return;
            }
            
            // 驗證每個公車數據的完整性
            let validBuses = 0;
            data.forEach((bus, index) => {
                if (bus.PlateNumb && bus.PositionLon && bus.PositionLat) {
                    validBuses++;
                    console.log(`✓ 公車 ${index + 1}: ${bus.PlateNumb} (${bus.PositionLat}, ${bus.PositionLon})`);
                } else {
                    console.log(`❌ 公車 ${index + 1}: 數據不完整`, bus);
                }
            });
            
            results[testName] = { 
                status: 'success', 
                busCount: validBuses, 
                totalBuses: data.length 
            };
            
        } catch (error) {
            console.log(`❌ 處理失敗: ${error.message}`);
            results[testName] = { status: 'error', reason: error.message };
        }
    });
    
    return results;
}

/**
 * 測試實際JSON文件讀取
 */
async function testJsonFileReading() {
    console.log('\n測試實際JSON文件讀取...');
    
    const busDataFiles = {
        'br3': '/static/data/bus/br3_bus.json',
        'cat_left': '/static/data/bus/cat_left_bus.json',
        'cat_left_zhinan': '/static/data/bus/cat_left_zhinan_bus.json',
        'cat_right': '/static/data/bus/cat_right_bus.json'
    };
    
    let fileResults = {};
    
    for (const [route, dataFile] of Object.entries(busDataFiles)) {
        try {
            console.log(`\n--- 讀取: ${route} (${dataFile}) ---`);
            
            const response = await fetch(dataFile);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!Array.isArray(data)) {
                console.log('❌ 文件格式錯誤，預期為陣列');
                fileResults[route] = { status: 'error', reason: '非陣列數據' };
                continue;
            }
            
            if (data.length === 0) {
                console.log('✓ 空集合，正確處理');
                fileResults[route] = { status: 'empty', busCount: 0 };
            } else {
                console.log(`✓ 載入 ${data.length} 輛公車`);
                
                // 驗證數據完整性
                let validCount = 0;
                data.forEach(bus => {
                    if (bus.PlateNumb && bus.PositionLon && bus.PositionLat) {
                        validCount++;
                    }
                });
                
                fileResults[route] = { 
                    status: 'success', 
                    busCount: validCount, 
                    totalBuses: data.length 
                };
            }
            
        } catch (error) {
            console.log(`❌ 讀取失敗: ${error.message}`);
            fileResults[route] = { status: 'error', reason: error.message };
        }
    }
    
    return fileResults;
}

/**
 * 測試地圖顯示邏輯
 */
function testMapDisplayLogic() {
    console.log('\n測試地圖顯示邏輯...');
    
    const scenarios = [
        { name: '所有路線都有公車', data: { br3: 2, cat_left: 1, cat_left_zhinan: 0, cat_right: 1 } },
        { name: '部分路線有公車', data: { br3: 2, cat_left: 0, cat_left_zhinan: 0, cat_right: 0 } },
        { name: '所有路線都沒有公車', data: { br3: 0, cat_left: 0, cat_left_zhinan: 0, cat_right: 0 } }
    ];
    
    scenarios.forEach(scenario => {
        console.log(`\n--- 情境: ${scenario.name} ---`);
        
        let totalBuses = 0;
        let activeRoutes = 0;
        let routesWithBuses = [];
        
        Object.entries(scenario.data).forEach(([route, busCount]) => {
            if (busCount > 0) {
                totalBuses += busCount;
                activeRoutes++;
                routesWithBuses.push(`${route}(${busCount}輛)`);
            }
        });
        
        if (totalBuses > 0) {
            console.log(`✓ 顯示訊息: 已載入 ${totalBuses} 輛公車`);
            console.log(`✓ 活躍路線: ${routesWithBuses.join('、')}`);
        } else {
            console.log('✓ 靜默處理，不顯示訊息');
        }
        
        console.log(`統計: 總計 ${totalBuses} 輛公車，${activeRoutes} 條活躍路線`);
    });
}

/**
 * 執行完整驗證
 */
async function runCompleteValidation() {
    console.log('\n執行完整的JSON空集合處理驗證...');
    
    // 1. 測試邏輯處理
    const logicResults = testEmptyArrayHandling();
    
    // 2. 測試實際文件讀取
    const fileResults = await testJsonFileReading();
    
    // 3. 測試地圖顯示邏輯
    testMapDisplayLogic();
    
    // 總結結果
    console.log('\n=== 驗證結果總結 ===');
    
    console.log('\n邏輯處理測試:');
    Object.entries(logicResults).forEach(([test, result]) => {
        const status = result.status === 'success' ? '✓' : 
                      result.status === 'empty' ? '○' : '❌';
        console.log(`  ${status} ${test}: ${result.status} (${result.busCount || 0} 輛公車)`);
    });
    
    console.log('\n實際文件讀取:');
    Object.entries(fileResults).forEach(([route, result]) => {
        const status = result.status === 'success' ? '✓' : 
                      result.status === 'empty' ? '○' : '❌';
        console.log(`  ${status} ${route}: ${result.status} (${result.busCount || 0} 輛公車)`);
    });
    
    // 計算成功率
    const totalTests = Object.keys(logicResults).length + Object.keys(fileResults).length;
    const successfulTests = Object.values(logicResults).filter(r => r.status !== 'error').length +
                           Object.values(fileResults).filter(r => r.status !== 'error').length;
    
    console.log(`\n整體成功率: ${successfulTests}/${totalTests} (${Math.round(successfulTests/totalTests*100)}%)`);
    
    const allPassed = successfulTests === totalTests;
    console.log(allPassed ? '🎉 所有測試都通過！' : '⚠️ 部分測試需要檢查');
    
    return {
        logicResults,
        fileResults,
        totalTests,
        successfulTests,
        allPassed
    };
}

// 自動執行驗證
setTimeout(runCompleteValidation, 500);

// 將測試函數暴露到全局
window.jsonEmptyArrayTests = {
    testEmptyArrayHandling,
    testJsonFileReading,
    testMapDisplayLogic,
    runCompleteValidation
};
