// 模組：stop-manager.js - 站點管理

import { stopsLayer, routeColors, uniqueStops } from './config.js';
import { showLoading, hideLoading } from './ui-utils.js';
import { loadCachedArenaLevels, renderAllArenas } from './arena-manager.js';

// 全局緩存道館等級資料
let arenaLevelsCache = {};
let cacheLoaded = false;

// 在載入站點之前預先載入道館等級緩存
async function preloadArenaLevels() {
    if (!cacheLoaded) {
        console.log('預先載入道館等級緩存資料...');
        try {
            arenaLevelsCache = await loadCachedArenaLevels();
            cacheLoaded = true;
            console.log(`成功預載道館等級緩存，共 ${Object.keys(arenaLevelsCache).length} 筆資料`);
        } catch (error) {
            console.error('預載道館等級緩存失敗:', error);
        }
    }
}

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
      // 同時加載所有路線，並在所有加載完成後進行道館合併處理
    Promise.all([
        // 加載貓空右線站點
        new Promise(resolve => loadBusStops('cat-right', resolve)),
        
        // 加載貓空左線(動物園)站點
        new Promise(resolve => loadBusStops('cat-left', resolve)),
        
        // 加載貓空左線(指南宮)站點
        new Promise(resolve => loadBusStops('cat-left-zhinan', resolve)),
        
        // 加載棕3路線站點
        new Promise(resolve => loadBusStops('brown-3', resolve))
    ]).then(() => {
        console.log('所有路線站點加載完成，開始更新道館等級');
        // 所有路線站點加載完成後，更新道館等級
        updateAllArenaLevels();
        hideLoading();
    }).catch(error => {
        console.error('加載站點時出錯:', error);
        hideLoading();
    });
}

// 更新所有道館的等級
function updateAllArenaLevels() {
    console.log('更新所有道館等級...');

    // 針對每個已知的站點/道館，檢查是否經過多條路線
    for (let positionKey in uniqueStops) {
        const stopInfo = uniqueStops[positionKey];
        const stopName = stopInfo.stopName;
        
        // 檢查這個站點是否在 Firebase 中有對應的道館
        checkExistingArenaForStop(stopName).then(arenaData => {
            if (arenaData) {
                console.log(`檢查道館 ${arenaData.name} 的路線數量`);
                
                // 如果存在道館，檢查該站點的所有對應路線
                let routesForThisStop = [];
                for (let key in uniqueStops) {
                    if (uniqueStops[key].stopName === stopName) {
                        routesForThisStop.push(uniqueStops[key].routeName);
                    }
                }
                
                // 移除重複的路線
                routesForThisStop = [...new Set(routesForThisStop)];
                
                if (routesForThisStop.length > 0) {
                    console.log(`站點 ${stopName} 經過的路線:`, routesForThisStop.join(', '));
                    
                    // 更新每條路線
                    routesForThisStop.forEach(routeName => {
                        updateArenaRoutes(arenaData.id, routeName)
                            .then(result => {
                                if (result.success) {
                                    console.log(`成功更新道館 ${arenaData.name} 的路線，目前路線數: ${result.routes.length}, 等級: ${result.level}`);
                                    
                                    // 更新地圖上的道館圖示 (這裡需要實現重新渲染道館的邏輯)
                                    updateArenaDisplay(arenaData.id, result.level);
                                }
                            })
                            .catch(error => {
                                console.error(`更新道館 ${arenaData.name} 路線時出錯:`, error);
                            });
                    });
                }
            }
        }).catch(error => {
            console.error(`檢查站點 ${stopName} 對應道館時出錯:`, error);
        });
    }
}

// 更新地圖上的道館顯示
function updateArenaDisplay(arenaId, newLevel) {
    // 此函數將在道館等級更新後重新渲染道館圖標
    console.log(`更新道館顯示: ${arenaId}, 新等級: ${newLevel}`);
    
    // 取得全局道館數據
    if (!window.busStopsArenas || !window.busStopsArenas[arenaId]) {
        console.warn(`找不到道館數據: ${arenaId}`);
        return;
    }
    
    const arenaData = window.busStopsArenas[arenaId];
    
    // 更新道館等級
    arenaData.level = newLevel;
    
    // 從 Firestore 重新獲取最新的道館數據
    const db = firebase.firestore();
    db.collection('arenas').doc(arenaId).get().then(doc => {
        if (doc.exists) {
            const updatedData = doc.data();
            
            // 更新本地緩存的道館數據
            window.busStopsArenas[arenaId] = updatedData;
            
            // 嘗試從全局存儲中獲取對應的道館標記
            if (window.arenaMarkers && window.arenaMarkers[arenaId]) {
                const marker = window.arenaMarkers[arenaId];
                console.log(`找到現有道館標記: ${updatedData.name}，準備更新等級為 ${newLevel}`);
                
                // 更新圖標
                const arenaColor = '#1565C0';
                const iconSize = 36 + (newLevel - 1) * 6;
                
                // 創建新圖標
                const newIcon = L.divIcon({
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
                            font-size:${16 + (newLevel - 1) * 2}px;
                            font-weight:bold;
                            color:white;
                        ">
                            <span>⚔️</span>
                            <span style="position:absolute;bottom:2px;right:2px;background:white;color:${arenaColor};border-radius:50%;width:18px;height:18px;font-size:12px;display:flex;justify-content:center;align-items:center;">${newLevel}</span>
                        </div>
                    `,
                    iconSize: [iconSize, iconSize],
                    iconAnchor: [iconSize/2, iconSize/2],
                    popupAnchor: [0, -iconSize/2]
                });
                
                // 應用新圖標
                marker.setIcon(newIcon);
                
                // 更新彈出框內容
                let levelDescription = newLevel === 1 ? '基礎道館' : `${newLevel} 級道館 (經過 ${newLevel} 條路線)`;
                
                // 找出原始的路線名稱，如果不存在則使用默認值
                const routeName = updatedData.routeName || '未知路線';
                const stopId = updatedData.stopId || arenaId.replace('arena-', '');
                const stopName = updatedData.stopName || updatedData.name.replace('道館', '');
                
                // 更新彈出框內容
                marker.bindPopup(`
                    <div style="text-align:center;">
                        <h5>${updatedData.name}</h5>
                        <p>等級: ${newLevel} 級</p>
                        <p><small>${levelDescription}</small></p>
                        <p><small>道館ID: ${arenaId}</small></p>
                        <button class="btn btn-danger mt-2 challenge-arena-btn" 
                                onclick="goToArena('${stopId}', '${stopName}', '${routeName}')">
                            前往道館
                        </button>
                    </div>
                `);
                
                console.log(`✅ 道館 ${updatedData.name} 成功更新為 ${newLevel} 級`);
            } else {
                console.warn(`無法找到道館 ${updatedData.name} 的現有標記，但已更新緩存數據。將在下次載入時顯示正確等級。`);
            }
        }
    }).catch(error => {
        console.error(`獲取道館數據時出錯: ${error}`);
    });
}

// 載入特定路線的站點
function loadBusStops(routeKey, callback) {
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
        case 'brown-3':
            apiUrl = '/game/api/bus/brown-3-stops';
            routeName = '棕3路線';
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
            callback();
        })
        .catch(error => {
            console.error(`獲取 ${routeKey} 站點資料失敗:`, error);
            useBackupStops(routeKey, routeName);
            callback();
        });
}

// 處理站點資料
function processStops(data, routeKey, routeName) {
    console.log(`處理 ${routeKey} 站點資料`);
    
    let stops = [];
    // 用於追蹤本批次資料中已處理過的站點名稱
    const processedStopNames = new Set();
    
    // 嘗試解析不同的資料格式
    if (data[0]?.Stops && Array.isArray(data[0].Stops)) {
        // V3 API格式: 包含Stops陣列
        data.forEach(route => {
            if (route.Stops && Array.isArray(route.Stops)) {
                route.Stops.forEach(stop => {
                    // 跳過已處理過的同名站點
                    const normalizedName = stop.StopName?.Zh_tw?.toLowerCase().replace(/\s+/g, '') || '';
                    if (processedStopNames.has(normalizedName)) {
                        console.log(`跳過處理本批次中重複的站點: ${stop.StopName?.Zh_tw}`);
                        return;
                    }
                    
                    if (stop.StopPosition) {
                        stops.push({
                            id: stop.StopID || `stop-${routeKey}-${stops.length}`,
                            name: stop.StopName?.Zh_tw || '未知站名',
                            position: [
                                stop.StopPosition.PositionLat, 
                                stop.StopPosition.PositionLon
                            ]
                        });
                        processedStopNames.add(normalizedName);
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
            
            // 跳過已處理過的同名站點
            const normalizedName = name.toLowerCase().replace(/\s+/g, '');
            if (processedStopNames.has(normalizedName)) {
                console.log(`跳過處理本批次中重複的站點: ${name}`);
                return;
            }
            
            if (position) {
                stops.push({
                    id: id,
                    name: name,
                    position: position
                });
                processedStopNames.add(normalizedName);
            }
        });
    }
    
    // 繪製站點，但不創建道館
    if (stops.length > 0) {
        console.log(`準備繪製 ${routeKey} 路線上的 ${stops.length} 個站點 (排除重複項後)`);
        stops.forEach(stop => {
            drawStop(stop, routeColors[routeKey], routeName, false);
            
            // 不再自動創建道館，而是收集站點信息
            // 記錄該位置的站點，但不創建道館
            const positionKey = `${stop.position[0].toFixed(4)},${stop.position[1].toFixed(4)}`;
            uniqueStops[positionKey] = { 
                stopName: stop.name, 
                routeName: routeName,
                id: stop.id,
                position: stop.position
            };
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
            
        case 'brown-3':
            backupStops = [
                { id: 'stop-br3-1', name: '棕3起點站', position: [25.0400, 121.5500] },
                { id: 'stop-br3-2', name: '棕3中途站', position: [25.0420, 121.5520] },
                { id: 'stop-br3-3', name: '棕3終點站', position: [25.0460, 121.5560] }
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

// 繪製站點 (僅創建道館圖標)
function drawStop(stop, color, routeName, isBackup = false) {
    console.log(`嘗試創建道館: ${stop.name} at [${stop.position[0]}, ${stop.position[1]}]`);
    
    // 檢查站點名稱是否已存在（不區分大小寫且去除空格）
    const normalizeName = name => name.toLowerCase().replace(/\s+/g, '');
    const stopNormalizedName = normalizeName(stop.name);
    
    // 檢查是否已有相同名稱的站點
    let hasExistingNameMatch = false;
    for (let key in uniqueStops) {
        if (normalizeName(uniqueStops[key].stopName) === stopNormalizedName) {
            console.log(`已存在同名道館站點 (${uniqueStops[key].stopName})，跳過創建: ${stop.name}, ${routeName}`);
            
            // 更新現有站點，將此路線添加到其路線列表中
            if (!uniqueStops[key].routes) {
                uniqueStops[key].routes = [uniqueStops[key].routeName];
            }
            if (!uniqueStops[key].routes.includes(routeName)) {
                uniqueStops[key].routes.push(routeName);
                console.log(`將路線 ${routeName} 添加到站點 ${stop.name} 的路線列表中，現有路線: ${uniqueStops[key].routes.join(', ')}`);
            }
            
            hasExistingNameMatch = true;
            // 不要立即返回，繼續檢查位置是否也匹配
        }
    }
    
    // 檢查是否已經存在相近位置的站點
    const positionKey = `${stop.position[0].toFixed(4)},${stop.position[1].toFixed(4)}`;
    if (uniqueStops[positionKey]) {
        console.log(`道館站點已存在於位置 ${positionKey}，跳過創建: ${stop.name}`);
        
        // 更新現有站點，將此路線添加到其路線列表中
        if (!uniqueStops[positionKey].routes) {
            uniqueStops[positionKey].routes = [uniqueStops[positionKey].routeName];
        }
        if (!uniqueStops[positionKey].routes.includes(routeName)) {
            uniqueStops[positionKey].routes.push(routeName);
            console.log(`將路線 ${routeName} 添加到站點 ${uniqueStops[positionKey].stopName} 的路線列表中，現有路線: ${uniqueStops[positionKey].routes.join(', ')}`);
        }
        
        return null;
    }
    
    // 檢查是否有相近的站點
    // 計算經緯度約30米的差值 (0.0003大約是30米)
    const nearbyDistance = 0.0003;
    let hasNearbyMatch = false;
    let nearbyKey = null;
    for (let key in uniqueStops) {
        const [existingLat, existingLng] = key.split(',').map(Number);
        const lat = parseFloat(stop.position[0]);
        const lng = parseFloat(stop.position[1]);
        
        // 如果兩個站牌位置非常接近，視為同一站牌
        if (Math.abs(existingLat - lat) < nearbyDistance && 
            Math.abs(existingLng - lng) < nearbyDistance) {
            console.log(`在附近找到現有道館站點 (${key})，跳過創建: ${stop.name}`);
            
            // 更新現有站點，將此路線添加到其路線列表中
            if (!uniqueStops[key].routes) {
                uniqueStops[key].routes = [uniqueStops[key].routeName];
            }
            if (!uniqueStops[key].routes.includes(routeName)) {
                uniqueStops[key].routes.push(routeName);
                console.log(`將路線 ${routeName} 添加到附近站點 ${uniqueStops[key].stopName} 的路線列表中，現有路線: ${uniqueStops[key].routes.join(', ')}`);
            }
            
            hasNearbyMatch = true;
            nearbyKey = key;
            // 不要立即返回，記錄最佳匹配
        }
    }
    
    // 如果有名稱或位置匹配，則跳過創建
    if (hasExistingNameMatch || hasNearbyMatch) {
        return null;
    }
    
    // 記錄該位置已創建站點
    const positionKeyFull = `${stop.position[0].toFixed(4)},${stop.position[1].toFixed(4)}`;
    uniqueStops[positionKeyFull] = { 
        stopName: stop.name, 
        routeName: routeName,
        routes: [routeName],  // 初始化路線列表
        isBackup: isBackup,
        id: stop.id,
        position: stop.position
    };
    
    console.log(`成功記錄道館站點: ${stop.name} 於位置 ${positionKeyFull}`);
    
    // 基於經過的路線數量設置道館級別 (初始為1級)
    const routes = [routeName];
    const level = routes.length;
    
    // 生成唯一ID
    const arenaId = `arena-${stop.id || positionKeyFull.replace(/\./g, '_').replace(/,/g, '-')}`;
    
    // 創建道館信息對象
    const arena = {
        id: arenaId,
        name: `${stop.name}道館`,
        position: stop.position,
        level: level,
        routes: routes, // 保存路線列表，用於計算等級
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
    
    // 使用 arena-manager.js 中的 createArenaMarker 函數創建道館圖標
    if (window.createArenaMarker) {
        window.createArenaMarker(stop, routeName, arenaId, level, arena);
        console.log(`✅ 成功創建道館: ${arena.name}, ID: ${arenaId}`);
    } else {
        console.error('createArenaMarker 函數未定義，無法創建道館圖標');
    }
    
    return null; // 不再返回標記，由 createArenaMarker 處理
}

// 導出模組
export {
    loadAllBusStops,
    loadBusStops,
    processStops,
    useBackupStops,
    drawStop
};