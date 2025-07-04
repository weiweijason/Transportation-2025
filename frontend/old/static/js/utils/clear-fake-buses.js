/**
 * 清除虛假公車數據腳本
 * 用於清除地圖上顯示的測試/虛假公車標記
 */

console.log('=== 清除虛假公車數據 ===');

// 虛假公車車號列表
const fakeBusPlateNumbers = [
    'ZHN-888',    // 指南宮測試車號
    'CAT-001',    // 貓空左線測試車號  
    'RIGHT-789'   // 貓空右線測試車號
];

/**
 * 清除地圖上的虛假公車標記
 */
function clearFakeBusMarkers() {
    console.log('開始清除地圖上的虛假公車標記...');
    
    let clearedCount = 0;
    
    // 檢查是否有公車位置圖層
    if (window.busPositionLayer) {
        const layers = window.busPositionLayer.getLayers();
        console.log(`當前地圖上有 ${layers.length} 個公車標記`);
        
        // 遍歷所有圖層，查找並移除虛假公車
        layers.forEach(layer => {
            if (layer.getPopup) {
                const popup = layer.getPopup();
                if (popup) {
                    const popupContent = popup.getContent();
                    
                    // 檢查彈出窗口內容是否包含虛假車號
                    fakeBusPlateNumbers.forEach(fakeNumber => {
                        if (popupContent.includes(fakeNumber)) {
                            console.log(`移除虛假公車標記: ${fakeNumber}`);
                            window.busPositionLayer.removeLayer(layer);
                            clearedCount++;
                        }
                    });
                }
            }
        });
    } else {
        console.log('公車位置圖層不存在');
    }
    
    console.log(`清除完成，共移除 ${clearedCount} 個虛假公車標記`);
    return clearedCount;
}

/**
 * 強制重新載入公車位置
 */
async function forceReloadBusPositions() {
    console.log('強制重新載入公車位置...');
    
    try {
        // 清除現有標記
        if (typeof window.clearBusMarkers === 'function') {
            window.clearBusMarkers();
            console.log('✓ 已清除所有現有公車標記');
        }
        
        // 重新載入數據
        if (typeof window.loadAllBusPositions === 'function') {
            await window.loadAllBusPositions();
            console.log('✓ 重新載入完成');
        } else {
            console.log('❌ loadAllBusPositions 函數不可用');
        }
        
    } catch (error) {
        console.error('重新載入失敗:', error);
    }
}

/**
 * 驗證JSON文件是否已清空
 */
async function verifyJsonFilesCleared() {
    console.log('驗證JSON文件是否已清空...');
    
    const busDataFiles = {
        'cat_left': '/static/data/bus/cat_left_bus.json',
        'cat_left_zhinan': '/static/data/bus/cat_left_zhinan_bus.json',
        'cat_right': '/static/data/bus/cat_right_bus.json'
    };
    
    let allCleared = true;
    
    for (const [route, dataFile] of Object.entries(busDataFiles)) {
        try {
            const response = await fetch(dataFile);
            if (response.ok) {
                const data = await response.json();
                
                if (Array.isArray(data) && data.length === 0) {
                    console.log(`✓ ${route}: 已清空`);
                } else {
                    console.log(`❌ ${route}: 仍有 ${data.length} 項數據`);
                    allCleared = false;
                    
                    // 檢查是否包含虛假車號
                    data.forEach(bus => {
                        if (fakeBusPlateNumbers.includes(bus.PlateNumb)) {
                            console.log(`  ⚠️ 發現虛假車號: ${bus.PlateNumb}`);
                        }
                    });
                }
            } else {
                console.log(`❌ ${route}: 無法讀取文件 (HTTP ${response.status})`);
                allCleared = false;
            }
        } catch (error) {
            console.log(`❌ ${route}: 讀取錯誤 - ${error.message}`);
            allCleared = false;
        }
    }
    
    if (allCleared) {
        console.log('🎉 所有相關JSON文件都已正確清空');
    } else {
        console.log('⚠️ 部分文件仍需清理');
    }
    
    return allCleared;
}

/**
 * 執行完整清理流程
 */
async function performCompleteClearance() {
    console.log('\n執行完整的虛假公車數據清理...');
    
    try {
        // 1. 驗證JSON文件狀態
        console.log('\n第1步: 驗證JSON文件狀態');
        const filesCleared = await verifyJsonFilesCleared();
        
        // 2. 清除地圖上的虛假標記
        console.log('\n第2步: 清除地圖上的虛假標記');
        const markersCleared = clearFakeBusMarkers();
        
        // 3. 強制重新載入
        console.log('\n第3步: 強制重新載入公車位置');
        await forceReloadBusPositions();
        
        // 4. 最終驗證
        console.log('\n第4步: 最終驗證');
        const finalLayers = window.busPositionLayer ? window.busPositionLayer.getLayers().length : 0;
        console.log(`當前地圖上有 ${finalLayers} 個公車標記`);
        
        // 總結
        console.log('\n=== 清理結果總結 ===');
        console.log(`JSON文件清空: ${filesCleared ? '✓' : '❌'}`);
        console.log(`移除虛假標記: ${markersCleared} 個`);
        console.log(`當前公車標記: ${finalLayers} 個`);
        
        if (filesCleared && finalLayers === 0) {
            console.log('🎉 虛假公車數據清理完成！');
            
            if (typeof window.showGameAlert === 'function') {
                window.showGameAlert('虛假公車數據已清除，地圖已更新', 'success', 3000);
            }
        } else {
            console.log('⚠️ 可能仍有殘留數據，請檢查');
        }
        
        return { filesCleared, markersCleared, finalLayers };
        
    } catch (error) {
        console.error('清理過程中發生錯誤:', error);
        return { error: error.message };
    }
}

/**
 * 快速清理函數（僅清除地圖標記）
 */
function quickClearFakeBuses() {
    console.log('快速清除虛假公車標記...');
    
    if (typeof window.clearBusMarkers === 'function') {
        window.clearBusMarkers();
        console.log('✓ 所有公車標記已清除');
        
        if (typeof window.showGameAlert === 'function') {
            window.showGameAlert('已清除地圖上的公車標記', 'info', 2000);
        }
    } else {
        console.log('❌ clearBusMarkers 函數不可用');
    }
}

// 自動執行清理（延遲執行以確保其他模組載入完成）
setTimeout(() => {
    if (document.readyState === 'complete') {
        performCompleteClearance();
    }
}, 2000);

// 將函數暴露到全域以便手動調用
window.fakeBusClearance = {
    clearFakeBusMarkers,
    forceReloadBusPositions,
    verifyJsonFilesCleared,
    performCompleteClearance,
    quickClearFakeBuses,
    fakeBusPlateNumbers
};

console.log('虛假公車清理腳本已載入，2秒後自動執行清理...');
console.log('您也可以手動執行: window.fakeBusClearance.performCompleteClearance()');
