// 模組：arena-manager.js - 道館管理

import { arenaLayer, uniqueStops } from './config.js';

// 創建道館
function createArena(stop, color, routeName, isBackup = false) {
    console.log(`嘗試創建道館: ${stop.name}`);
    
    // 檢查站點名稱是否已存在（不區分大小寫且去除空格）
    const normalizeName = name => name.toLowerCase().replace(/\s+/g, '');
    const stopNormalizedName = normalizeName(stop.name);
    
    // 檢查是否已有相同名稱的站點
    for (let key in uniqueStops) {
        if (normalizeName(uniqueStops[key].stopName) === stopNormalizedName) {
            console.log(`已存在同名道館 (${uniqueStops[key].stopName})，跳過創建: ${stop.name}`);
            return null;
        }
    }
    
    // 檢查是否已經存在相近位置的道館
    const positionKey = `${stop.position[0].toFixed(4)},${stop.position[1].toFixed(4)}`;
    if (uniqueStops[positionKey]) {
        console.log(`道館已存在於位置 ${positionKey}，跳過創建: ${stop.name}`);
        return null;
    }
    
    // 檢查是否有相近的道館
    // 計算經緯度約30米的差值 (0.0003大約是30米)
    const nearbyDistance = 0.0003;
    for (let key in uniqueStops) {
        const [existingLat, existingLng] = key.split(',').map(Number);
        const lat = parseFloat(stop.position[0]);
        const lng = parseFloat(stop.position[1]);
        
        // 如果兩個站牌位置非常接近，視為同一站牌
        if (Math.abs(existingLat - lat) < nearbyDistance && 
            Math.abs(existingLng - lng) < nearbyDistance) {
            console.log(`在附近找到現有道館 (${key})，跳過創建: ${stop.name}`);
            return null;
        }
    }
    
    // 如果沒有找到相同或相近的道館，則創建新道館
    console.log(`創建新道館: ${stop.name}`);
    
    // 記錄該位置已創建道館
    uniqueStops[positionKey] = { 
        stopName: stop.name, 
        routeName: routeName 
    };
    
    // 生成唯一ID
    const arenaId = `arena-${stop.id}`;
    
    // 創建道館級別 (1-3級，隨機生成)
    const level = Math.floor(Math.random() * 3) + 1;
    
    // 使用統一的顏色 - 深藍色
    const arenaColor = '#1565C0';
    
    // 創建道館圖標
    const iconSize = 36 + (level - 1) * 6; // 基礎大小36px，每增加一級增加6px
    
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
    const arenaMarker = L.marker(stop.position, {
        icon: arenaIcon,
        zIndexOffset: 1000 // 確保道館顯示在站點上方
    }).addTo(arenaLayer);
    
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
    
    // 綁定彈出信息 - 簡化版本，只顯示名稱和等級
    arenaMarker.bindPopup(`
        <div style="text-align:center;">
            <h5>${arena.name}</h5>
            <p>等級: ${arena.level} 級</p>
            <button class="btn btn-danger mt-2 challenge-arena-btn" 
                    onclick="showArenaInfo('${arena.stopId}', '${arena.stopName}', '${arena.routeName}')">
                前往道館
            </button>
        </div>
    `);
    
    return arena;
}

// 顯示道館信息 (測試用)
function showArenaInfo(stopId, stopName, routeName) {
    console.log(`顯示道館信息: ${stopName}, ID: ${stopId}, 路線: ${routeName}`);
    
    // 跳轉到測試頁面
    window.location.href = `/game/battle?stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
}

// 導出模組
export { createArena, showArenaInfo };