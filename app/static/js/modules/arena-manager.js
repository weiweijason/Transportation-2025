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
    
    // 道館名稱
    const arenaName = `${stop.name}道館`;
    
    // 生成唯一ID
    const arenaId = `arena-${stop.id}`;
    
    // 首先檢查Firebase是否已存在該道館
    checkArenaInFirebase(arenaName).then(existingArena => {
        if (existingArena) {
            console.log(`Firebase中已存在道館: ${arenaName}，使用現有數據`);
            
            // 記錄該位置已創建道館
            uniqueStops[positionKey] = { 
                stopName: stop.name, 
                routeName: routeName 
            };
            
            // 創建道館圖標 (使用從Firebase獲取的等級)
            const level = existingArena.level || Math.floor(Math.random() * 3) + 1;
            createArenaMarker(stop, routeName, arenaId, level, existingArena);
            
        } else {
            // Firebase中不存在該道館，創建新道館
            console.log(`Firebase中不存在道館: ${arenaName}，創建新道館`);
            
            // 記錄該位置已創建道館
            uniqueStops[positionKey] = { 
                stopName: stop.name, 
                routeName: routeName 
            };
            
            // 創建道館級別 (1-3級，隨機生成)
            const level = Math.floor(Math.random() * 3) + 1;
            
            // 創建新道館數據
            const arena = {
                id: arenaId,
                name: arenaName,
                position: stop.position,
                level: level,
                routeName: routeName,
                stopId: stop.id,
                stopName: stop.name,
                isBackup: isBackup
            };
            
            // 創建道館圖標
            createArenaMarker(stop, routeName, arenaId, level, arena);
            
            // 保存新道館到Firebase
            saveArenaToFirebase(arena);
        }
    }).catch(error => {
        console.error(`檢查Firebase道館時出錯: ${error}`);
        
        // 出錯時，仍然創建本地道館但不保存到Firebase
        console.log(`由於錯誤，僅創建本地道館: ${arenaName}`);
        
        // 記錄該位置已創建道館
        uniqueStops[positionKey] = { 
            stopName: stop.name, 
            routeName: routeName 
        };
        
        // 創建道館級別 (1-3級，隨機生成)
        const level = Math.floor(Math.random() * 3) + 1;
        
        // 創建新道館數據
        const arena = {
            id: arenaId,
            name: arenaName,
            position: stop.position,
            level: level,
            routeName: routeName,
            stopId: stop.id,
            stopName: stop.name,
            isBackup: isBackup
        };
        
        // 創建道館圖標
        createArenaMarker(stop, routeName, arenaId, level, arena);
    });
    
    // 返回道館ID (由於異步操作，這裡只返回ID)
    return arenaId;
}

// 檢查Firebase中是否存在道館
async function checkArenaInFirebase(arenaName) {
    try {
        // 獲取Firebase Firestore數據庫引用
        const db = firebase.firestore();
        
        // 查詢是否已存在同名道館
        const querySnapshot = await db.collection('arenas')
            .where('name', '==', arenaName)
            .limit(1)
            .get();
            
        if (!querySnapshot.empty) {
            // 存在同名道館，返回道館數據
            return querySnapshot.docs[0].data();
        }
        
        // 不存在同名道館
        return null;
    } catch (error) {
        console.error(`查詢Firebase道館時出錯: ${error}`);
        return null;
    }
}

// 創建道館圖標並添加到地圖
function createArenaMarker(stop, routeName, arenaId, level, arenaData) {
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
    
    // 將道館信息存入全局對象
    if (!window.busStopsArenas) {
        window.busStopsArenas = {};
    }
    window.busStopsArenas[arenaId] = arenaData;
    
    // 綁定彈出信息 - 簡化版本，只顯示名稱和等級
    arenaMarker.bindPopup(`
        <div style="text-align:center;">
            <h5>${arenaData.name}</h5>
            <p>等級: ${level} 級</p>
            <button class="btn btn-danger mt-2 challenge-arena-btn" 
                    onclick="showArenaInfo('${stop.id}', '${stop.name}', '${routeName}')">
                前往道館
            </button>
        </div>
    `);
    
    return arenaMarker;
}

// 保存道館信息到Firebase
function saveArenaToFirebase(arena) {
    try {
        console.log(`開始嘗試保存道館 ${arena.name} 到Firebase...`);
        
        // 確認Firebase是否已初始化
        if (typeof firebase === 'undefined' || !firebase.firestore) {
            console.error(`Firebase未初始化，無法保存道館: ${arena.name}`);
            return;
        }
        
        // 獲取Firebase Firestore數據庫引用
        const db = firebase.firestore();
        console.log(`成功獲取Firebase Firestore引用`);
        
        // 首先查詢是否已存在同名道館
        db.collection('arenas')
            .where('name', '==', arena.name)
            .limit(1)
            .get()
            .then((querySnapshot) => {
                if (!querySnapshot.empty) {
                    console.log(`Firebase中已存在同名道館: ${arena.name}，不進行保存`);
                    return;
                }
                
                console.log(`Firebase中不存在道館: ${arena.name}，準備上傳數據`);
                
                // 準備道館數據
                const arenaData = {
                    id: arena.id,
                    name: arena.name,
                    position: [arena.position[0], arena.position[1]],
                    level: arena.level,
                    routeName: arena.routeName,
                    stopIds: [arena.stopId],
                    stopName: arena.stopName,
                    owner: null,
                    ownerPlayerId: null,
                    ownerCreature: null,
                    challengers: [],
                    updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
                    createdAt: firebase.firestore.FieldValue.serverTimestamp()
                };
                
                console.log(`道館數據已準備好: `, JSON.stringify(arenaData, null, 2));
                
                // 保存到Firestore
                return db.collection('arenas').doc(arena.id).set(arenaData)
                    .then(() => {
                        console.log(`✅ 道館 ${arena.name} 已成功保存至Firebase Firestore!`);
                        // 嘗試檢查是否確實保存成功
                        return db.collection('arenas').doc(arena.id).get();
                    })
                    .then((docSnapshot) => {
                        if (docSnapshot && docSnapshot.exists) {
                            console.log(`✅ 確認道館 ${arena.name} 已存在於Firebase中，數據驗證成功!`);
                            console.log(`Firebase文檔ID: ${docSnapshot.id}`);
                        } else {
                            console.warn(`⚠️ 道館似乎已保存，但無法立即驗證: ${arena.name}`);
                        }
                    })
                    .catch(error => {
                        console.error(`❌ 保存道館到Firebase時出錯: ${error.message}`);
                        console.error(`錯誤詳情:`, error);
                    });
            })
            .catch(error => {
                console.error(`❌ 查詢Firebase道館時出錯: ${error.message}`);
                console.error(`錯誤詳情:`, error);
                
                // 嘗試打印Firebase連接狀態
                try {
                    const authStatus = firebase.auth().currentUser ? '已登入' : '未登入';
                    console.log(`Firebase認證狀態: ${authStatus}`);
                } catch (e) {
                    console.log(`無法獲取Firebase認證狀態: ${e.message}`);
                }
            });
    } catch (error) {
        console.error(`❌ 存取Firebase時出錯: ${error.message}`);
        console.error(`錯誤詳情:`, error);
    }
}

// 顯示道館信息
function showArenaInfo(stopId, stopName, routeName) {
    console.log(`顯示道館信息: ${stopName}, ID: ${stopId}, 路線: ${routeName}`);
    
    // 道館名稱
    const arenaName = `${stopName}道館`;
    
    try {
        // 從Firebase獲取道館當前狀況
        const db = firebase.firestore();
        
        db.collection('arenas')
            .where('name', '==', arenaName)
            .limit(1)
            .get()
            .then((querySnapshot) => {
                let arenaData = null;
                
                if (!querySnapshot.empty) {
                    // 如果找到了道館資料
                    arenaData = querySnapshot.docs[0].data();
                }
                
                // 保存道館數據到查詢參數
                const params = new URLSearchParams();
                params.append('stopId', stopId);
                params.append('stopName', stopName);
                params.append('routeName', routeName);
                
                if (arenaData) {
                    params.append('arenaId', arenaData.id);
                    params.append('arenaOwner', arenaData.owner || '');
                    params.append('arenaOwnerPlayerId', arenaData.ownerPlayerId || '');
                    
                    if (arenaData.ownerCreature) {
                        params.append('ownerCreatureName', arenaData.ownerCreature.name || '');
                        params.append('ownerCreaturePower', arenaData.ownerCreature.power || 0);
                    }
                }
                
                // 跳轉到戰鬥頁面
                window.location.href = `/game/battle?${params.toString()}`;
            })
            .catch(error => {
                console.error(`獲取道館資訊時出錯: ${error}`);
                // 錯誤時仍跳轉，但不帶道館資料
                window.location.href = `/game/battle?stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
            });
    } catch (error) {
        console.error(`存取Firebase時出錯: ${error}`);
        // 錯誤時仍跳轉，但不帶道館資料
        window.location.href = `/game/battle?stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
    }
}

// 導出模組
export { createArena, showArenaInfo };