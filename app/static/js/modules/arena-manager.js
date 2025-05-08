// 模組：arena-manager.js - 道館管理

import { arenaLayer, uniqueStops } from './config.js';

// 緩存道館等級資料
let cachedArenaLevels = {};

// 全局存儲所有道館標記的對象
window.arenaMarkers = window.arenaMarkers || {};

// 從伺服器獲取緩存的道館等級資料
function loadCachedArenaLevels() {
    console.log('正在載入道館等級數據...');
    return fetch('/game/api/arena/cached-levels')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success && data.arenas) {
                console.log(`成功從API獲取 ${Object.keys(data.arenas).length} 個道館等級資料`);
                cachedArenaLevels = data.arenas;
                return data.arenas;
            } else {
                console.error('獲取道館等級數據返回格式不正確:', data);
                return {};
            }
        })
        .catch(error => {
            console.error('獲取道館等級數據時出錯:', error);
            return {};
        });
}

// 渲染所有道館 - 新功能：從緩存中載入所有道館並渲染到地圖
function renderAllArenas() {
    console.log('開始渲染所有緩存的道館...');
    
    // 清除現有道館圖層
    arenaLayer.clearLayers();
    
    // 清除已存在的道館標記
    window.arenaMarkers = {};
    
    // 清除已有記錄
    for (let key in uniqueStops) {
        delete uniqueStops[key];
    }
    
    // 從本地JSON文件獲取緩存的道館資料
    loadCachedArenaLevels()
        .then(arenas => {
            if (!arenas || Object.keys(arenas).length === 0) {
                console.warn('沒有找到任何緩存道館資料');
                return;
            }
            
            console.log(`準備渲染 ${Object.keys(arenas).length} 個道館`);
            
            // 避免重複，使用已處理的道館ID集合
            const processedArenaIds = new Set();
            
            // 逐個繪製道館
            Object.values(arenas).forEach(arena => {
                // 確保該道館還沒被處理過
                if (processedArenaIds.has(arena.id)) {
                    console.log(`跳過重複道館: ${arena.name}`);
                    return;
                }
                
                processedArenaIds.add(arena.id);
                
                if (arena.position && Array.isArray(arena.position) && arena.position.length === 2) {
                    // 創建道館資料
                    const stop = {
                        id: arena.stopIds ? arena.stopIds[0] : arena.id.replace('arena-', ''),
                        name: arena.stopName || arena.name.replace('道館', ''),
                        position: arena.position
                    };
                    
                    const routeName = arena.routes && arena.routes.length > 0 ? arena.routes[0] : '未知路線';
                    
                    // 創建道館標記 - 使用正確的等級
                    createArenaMarker(stop, routeName, arena.id, arena.level || 1, arena);
                    
                    // 記錄該位置已創建道館
                    const positionKey = `${arena.position[0].toFixed(4)},${arena.position[1].toFixed(4)}`;
                    uniqueStops[positionKey] = { 
                        stopName: stop.name, 
                        routeName: routeName
                    };
                }
            });
            
            console.log(`✅ 成功渲染 ${processedArenaIds.size} 個道館，跳過 ${Object.keys(arenas).length - processedArenaIds.size} 個重複道館`);
        })
        .catch(error => {
            console.error('渲染道館時出錯:', error);
        });
}

// 創建道館
function createArena(stop, color, routeName, isBackup = false) {
    console.log(`嘗試創建道館: ${stop.name} - 但僅使用 arena_levels.json 數據，跳過創建`);
    
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
    
    // 記錄該位置已創建了虛擬道館，但實際上不繪製 - 避免從其他來源再次創建
    uniqueStops[positionKey] = { 
        stopName: stop.name, 
        routeName: routeName 
    };
    
    // 返回 null 表示沒有創建新道館
    // 實際道館繪製僅由 renderAllArenas 函數通過 arena_levels.json 中的數據處理
    return null;
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
    
    // 確保使用正確的等級 - 從 arena_levels.json 中獲取的等級值
    const displayLevel = arenaData.level || level || 1;
    console.log(`創建道館標記: ${arenaData.name}, 等級: ${displayLevel}, id: ${arenaId}`);
    
    // 創建道館圖標
    const iconSize = 36 + (displayLevel - 1) * 6; // 基礎大小36px，每增加一級增加6px
    
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
                font-size:${16 + (displayLevel - 1) * 2}px;
                font-weight:bold;
                color:white;
            ">
                <span>⚔️</span>
                <span style="position:absolute;bottom:2px;right:2px;background:white;color:${arenaColor};border-radius:50%;width:18px;height:18px;font-size:12px;display:flex;justify-content:center;align-items:center;">${displayLevel}</span>
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
    
    // 綁定彈出信息 - 包含道館等級的解釋
    let levelDescription = '';
    if (displayLevel === 1) {
        levelDescription = '基礎道館';
    } else if (displayLevel > 1) {
        levelDescription = `${displayLevel} 級道館 (經過 ${displayLevel} 條路線)`;
    }
    
    arenaMarker.bindPopup(`
        <div style="text-align:center;">
            <h5>${arenaData.name}</h5>
            <p>等級: ${displayLevel} 級</p>
            <p><small>${levelDescription}</small></p>
            <p><small>道館ID: ${arenaId}</small></p>
            <button class="btn btn-danger mt-2 challenge-arena-btn" 
                    onclick="goToArena('${stop.id}', '${stop.name}', '${routeName}')">
                前往道館
            </button>
        </div>
    `);
    
    // 將標記添加到全局 arenaMarkers 對象中以便後續訪問
    window.arenaMarkers[arenaId] = arenaMarker;
    
    return arenaMarker;
}

// 將函數暴露為全域函數，使其他模組可以呼叫
window.createArenaMarker = createArenaMarker;
window.createArena = createArena;
window.checkExistingArenaForStop = checkExistingArenaForStop;
window.updateArenaRoutes = updateArenaRoutes;

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
                    routes: arena.routes || [arena.routeName], // 確保routes屬性存在
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

// 從 arena_levels.json 獲取道館等級
function getArenaLevelFromCache(stopName) {
    console.log(`嘗試從 arena_levels.json 獲取 ${stopName} 道館的等級`);
    
    // 使用緩存的道館等級資料
    if (!cachedArenaLevels || Object.keys(cachedArenaLevels).length === 0) {
        console.log('沒有緩存道館資料可用，默認返回等級 1');
        return 1;
    }
    
    // 遍歷所有道館資料，查找匹配的站點名稱
    for (const arenaId in cachedArenaLevels) {
        const arena = cachedArenaLevels[arenaId];
        if (arena.stopName === stopName) {
            console.log(`在緩存中找到匹配道館: ${stopName}，等級: ${arena.level}`);
            return arena.level;
        }
    }
    
    // 沒有找到匹配的道館，返回默認等級 1
    console.log(`在緩存中未找到匹配道館: ${stopName}，默認返回等級 1`);
    return 1;
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
                    console.log(`找到現有道館資料: ${arenaName}`, arenaData);
                    
                    // 保存道館數據到查詢參數
                    const params = new URLSearchParams();
                    params.append('stopId', stopId);
                    params.append('stopName', stopName);
                    params.append('routeName', routeName);
                    params.append('arenaId', arenaData.id);
                    
                    if (arenaData.owner) {
                        params.append('arenaOwner', arenaData.owner);
                        params.append('arenaOwnerPlayerId', arenaData.ownerPlayerId || '');
                    }
                    
                    if (arenaData.ownerCreature) {
                        params.append('ownerCreatureName', arenaData.ownerCreature.name || '');
                        params.append('ownerCreaturePower', arenaData.ownerCreature.power || 0);
                    }
                    
                    // 跳轉到戰鬥頁面
                    window.location.href = `/game/battle?${params.toString()}`;
                } else {
                    // 道館不存在於Firebase中，顯示404錯誤頁面
                    console.log(`道館 ${arenaName} 不存在於Firebase中，顯示404錯誤頁面`);
                    window.location.href = `/game/battle?error=404&stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
                }
            })
            .catch(error => {
                console.error(`獲取道館資訊時出錯: ${error}`);
                // 錯誤時顯示錯誤頁面
                window.location.href = `/game/battle?error=500&stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
            });
    } catch (error) {
        console.error(`存取Firebase時出錯: ${error}`);
        // 錯誤時顯示錯誤頁面
        window.location.href = `/game/battle?error=500&stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
    }
}

// 直接前往指定道館頁面
function goToArena(stopId, stopName, routeName) {
    console.log(`直接前往道館: ${stopName}, ID: ${stopId}, 路線: ${routeName}`);
    
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
                    console.log(`找到現有道館資料: ${arenaName}`, arenaData);
                    
                    // 直接導航到擂台頁面，而不是道館列表頁面
                    window.location.href = `/game/battle?arena_id=${arenaData.id}`;
                } else {
                    // 道館不存在於Firebase中，顯示404錯誤頁面
                    console.log(`道館 ${arenaName} 不存在於Firebase中，顯示404錯誤頁面`);
                    window.location.href = `/game/battle?error=404&stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
                }
            })
            .catch(error => {
                console.error(`獲取道館資訊時出錯: ${error}`);
                // 錯誤時顯示錯誤頁面
                window.location.href = `/game/battle?error=500&stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
            });
    } catch (error) {
        console.error(`存取Firebase時出錯: ${error}`);
        // 錯誤時顯示錯誤頁面
        window.location.href = `/game/battle?error=500&stopId=${stopId}&stopName=${encodeURIComponent(stopName)}&routeName=${encodeURIComponent(routeName)}`;
    }
}

// 將goToArena函數暴露為全域函數
window.goToArena = goToArena;

// 檢查是否已有路線對應的道館
function checkExistingArenaForStop(stopName) {
    // 使用Promise包裝，以便於處理異步操作
    return new Promise((resolve, reject) => {
        try {
            // 使用Firebase查詢是否已存在同名道館
            const db = firebase.firestore();
            const arenaName = `${stopName}道館`;
            
            db.collection('arenas')
                .where('name', '==', arenaName)
                .limit(1)
                .get()
                .then((querySnapshot) => {
                    if (!querySnapshot.empty) {
                        // 找到現有道館
                        const arenaData = querySnapshot.docs[0].data();
                        console.log(`找到現有道館: ${arenaName}`, arenaData);
                        resolve(arenaData);
                    } else {
                        // 沒有找到道館
                        console.log(`沒有找到道館: ${arenaName}`);
                        resolve(null);
                    }
                })
                .catch(error => {
                    console.error(`查詢Firebase道館時出錯: ${error}`);
                    resolve(null);
                });
        } catch (error) {
            console.error(`檢查現有道館時出錯: ${error}`);
            resolve(null);
        }
    });
}

// 更新道館路線
function updateArenaRoutes(arenaId, routeName) {
    return new Promise((resolve, reject) => {
        try {
            const db = firebase.firestore();
            
            // 獲取道館參考
            const arenaRef = db.collection('arenas').doc(arenaId);
            
            // 獲取當前道館數據
            arenaRef.get().then(doc => {
                if (doc.exists) {
                    const arenaData = doc.data();
                    console.log(`更新道館路線: ${arenaId}`, arenaData);
                    
                    // 檢查是否已有routes屬性，並確保是數組
                    let routes = Array.isArray(arenaData.routes) ? [...arenaData.routes] : [];
                    
                    // 檢查路線是否已存在
                    if (!routes.includes(routeName)) {
                        routes.push(routeName);
                        
                        // 更新等級
                        const level = routes.length;
                        
                        // 更新Firebase文檔
                        arenaRef.update({
                            routes: routes,
                            level: level,
                            updatedAt: firebase.firestore.FieldValue.serverTimestamp()
                        })
                        .then(() => {
                            console.log(`✅ 道館 ${arenaData.name} 路線更新為: ${routes.join(', ')}, 等級: ${level}`);
                            resolve({
                                success: true,
                                routes: routes,
                                level: level
                            });
                        })
                        .catch(error => {
                            console.error(`❌ 更新道館路線時出錯: ${error}`);
                            reject(error);
                        });
                    } else {
                        console.log(`道館 ${arenaData.name} 已有路線 ${routeName}，無需更新`);
                        resolve({
                            success: true,
                            routes: routes,
                            level: routes.length
                        });
                    }
                } else {
                    console.error(`找不到道館文檔: ${arenaId}`);
                    reject(new Error('找不到道館文檔'));
                }
            }).catch(error => {
                console.error(`獲取道館數據時出錯: ${error}`);
                reject(error);
            });
        } catch (error) {
            console.error(`更新道館路線時出錯: ${error}`);
            reject(error);
        }
    });
}

// 導出模組
export { createArena, showArenaInfo, checkExistingArenaForStop, updateArenaRoutes, loadCachedArenaLevels, renderAllArenas };