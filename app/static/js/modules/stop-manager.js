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

// 繪製站點 (使用道館圖示)
function drawStop(stop, color, routeName, isBackup = false) {
    console.log(`嘗試繪製道館站點: ${stop.name} at [${stop.position[0]}, ${stop.position[1]}]`);
    
    // 檢查站點名稱是否已存在（不區分大小寫且去除空格）
    const normalizeName = name => name.toLowerCase().replace(/\s+/g, '');
    const stopNormalizedName = normalizeName(stop.name);
    
    // 檢查是否已有相同名稱的站點
    for (let key in uniqueStops) {
        if (normalizeName(uniqueStops[key].stopName) === stopNormalizedName) {
            console.log(`已存在同名道館站點 (${uniqueStops[key].stopName})，跳過繪製: ${stop.name}`);
            return null;
        }
    }
    
    // 檢查是否已經存在相近位置的站點
    const positionKey = `${stop.position[0].toFixed(4)},${stop.position[1].toFixed(4)}`;
    if (uniqueStops[positionKey]) {
        console.log(`道館站點已存在於位置 ${positionKey}，跳過繪製: ${stop.name}`);
        return null;
    }
    
    // 檢查是否有相近的站點
    // 計算經緯度約30米的差值 (0.0003大約是30米)
    const nearbyDistance = 0.0003;
    for (let key in uniqueStops) {
        const [existingLat, existingLng] = key.split(',').map(Number);
        const lat = parseFloat(stop.position[0]);
        const lng = parseFloat(stop.position[1]);
        
        // 如果兩個站牌位置非常接近，視為同一站牌
        if (Math.abs(existingLat - lat) < nearbyDistance && 
            Math.abs(existingLng - lng) < nearbyDistance) {
            console.log(`在附近找到現有道館站點 (${key})，跳過繪製: ${stop.name}`);
            return null;
        }
    }
    
    // 記錄該位置已創建站點
    const positionKeyFull = `${stop.position[0].toFixed(4)},${stop.position[1].toFixed(4)}`;
    uniqueStops[positionKeyFull] = { 
        stopName: stop.name, 
        routeName: routeName,
        isBackup: isBackup
    };
    
    console.log(`成功記錄道館站點: ${stop.name} 於位置 ${positionKeyFull}`);
    
    // 創建道館級別 (1-3級，隨機生成)
    const level = Math.floor(Math.random() * 3) + 1;
    
    // 使用統一的顏色 - 深藍色
    const arenaColor = '#1565C0';
    
    // 創建道館圖標大小 - 比普通站點大
    const iconSize = 36 + (level - 1) * 6; // 基礎大小36px，每增加一級增加6px
    
    // 創建道館圖標
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
                cursor:pointer;
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
    const marker = L.marker(stop.position, {
        icon: arenaIcon,
        zIndexOffset: 1000  // 確保道館顯示在其他圖層上方
    }).addTo(stopsLayer);
    
    // 生成唯一ID
    const arenaId = `arena-${stop.id || positionKeyFull.replace(/\./g, '_').replace(/,/g, '-')}`;
    
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
    
    // 綁定彈出信息
    marker.bindPopup(`
        <div style="text-align:center;">
            <h5>${arena.name}</h5>
            <p>等級: ${level} 級</p>
            <button class="btn btn-danger mt-2 challenge-arena-btn" 
                    onclick="showArenaInfo('${stop.id || 'stop-' + positionKeyFull.replace(/\./g, '_').replace(/,/g, '-')}', '${stop.name}', '${routeName}')">
                前往道館
            </button>
        </div>
    `);
    
    // 添加點擊事件，直接進入道館
    marker.on('click', function() {
        marker.openPopup();
    });
    
    return marker;
}

// 導出模組
export {
    loadAllBusStops,
    loadBusStops,
    processStops,
    useBackupStops,
    drawStop
};