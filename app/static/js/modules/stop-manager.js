// 模組：stop-manager.js - 站點管理

import { stopsLayer, routeColors, uniqueStops } from './config.js';
import { showLoading, hideLoading } from './ui-utils.js';

// 載入並繪製所有貓空路線的站點
function loadAllBusStops() {
    console.log('載入所有貓空路線的站點');
    showLoading();
    
    // 清除現有站點圖層
    stopsLayer.clearLayers();
    
    // 重置站點追蹤器
    Object.keys(uniqueStops).forEach(key => {
        delete uniqueStops[key];
    });
    
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
            // 呼叫全局的createArena函數，由arena-manager.js暴露
            if (window.createArena) {
                window.createArena(stop, routeColors[routeKey], routeName);
            }
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
        // 呼叫全局的createArena函數，由arena-manager.js暴露
        if (window.createArena) {
            window.createArena(stop, routeColors[routeKey], routeName, true);
        }
    });
    
    console.log(`備用站點 ${routeKey} 繪製完成，共 ${backupStops.length} 個站點`);
}

// 繪製站點
function drawStop(stop, color, routeName, isBackup = false) {
    console.log(`繪製站點: ${stop.name} at [${stop.position[0]}, ${stop.position[1]}]`);
    
    // 不再繪製站點標記（小圓點）
    // 只記錄站點資訊用於創建道館，但不添加到地圖上
}

// 導出模組
export {
    loadAllBusStops,
    loadBusStops,
    processStops,
    useBackupStops,
    drawStop
};