// 模組：route-manager.js - 路線管理

import { routeLayer, routeColors, routeCoordinates } from './config.js';
import { showLoading, hideLoading } from './ui-utils.js';

// 獲取並繪製貓空右線
function loadCatRightRoute() {
    console.log('載入貓空右線');
    showLoading();
    
    fetch('/game/api/bus/cat-right-route')
        .then(response => response.json())
        .then(data => {
            console.log('獲取到貓空右線資料:', data);
            
            // 解析路線座標
            if (data && Array.isArray(data)) {
                // 處理路線資料
                let coordinates = [];
                
                // 提取路線座標點
                data.forEach(point => {
                    if (point.PositionLat && point.PositionLon) {
                        coordinates.push([point.PositionLat, point.PositionLon]);
                    }
                });
                
                if (coordinates.length > 0) {
                    // 儲存路線座標
                    routeCoordinates['cat-right'] = coordinates;
                    
                    // 創建路線
                    const polyline = L.polyline(coordinates, {
                        color: routeColors['cat-right'],
                        weight: 5,
                        opacity: 0.8
                    }).addTo(routeLayer);
                    
                    // 添加路線資訊彈窗
                    polyline.bindPopup(`
                        <div style="font-weight:bold;font-size:16px;">貓空纜車右線</div>
                        <div>方向: 貓空 → 動物園</div>
                    `);
                    
                    console.log('貓空右線繪製完成，座標點數量:', coordinates.length);
                } else {
                    console.warn('貓空右線座標解析失敗，使用備用座標');
                    useBackupRoute('cat-right');
                }
            } else {
                console.warn('貓空右線資料格式不正確，使用備用資料');
                useBackupRoute('cat-right');
            }
        })
        .catch(error => {
            console.error('獲取貓空右線資料失敗:', error);
            useBackupRoute('cat-right');
        })
        .finally(() => {
            hideLoading();
        });
}

// 獲取並繪製貓空左線(動物園)
function loadCatLeftRoute() {
    console.log('載入貓空左線(動物園)');
    showLoading();
    
    fetch('/game/api/bus/cat-left-route')
        .then(response => response.json())
        .then(data => {
            console.log('獲取到貓空左線(動物園)資料:', data);
            
            // 解析路線座標
            if (data && Array.isArray(data)) {
                let coordinates = [];
                
                // 提取路線座標點
                data.forEach(point => {
                    if (point.PositionLat && point.PositionLon) {
                        coordinates.push([point.PositionLat, point.PositionLon]);
                    }
                });
                
                if (coordinates.length > 0) {
                    // 儲存路線座標
                    routeCoordinates['cat-left'] = coordinates;
                    
                    // 創建路線
                    const polyline = L.polyline(coordinates, {
                        color: routeColors['cat-left'],
                        weight: 5,
                        opacity: 0.8
                    }).addTo(routeLayer);
                    
                    // 添加路線資訊彈窗
                    polyline.bindPopup(`
                        <div style="font-weight:bold;font-size:16px;">貓空纜車左線(動物園)</div>
                        <div>方向: 動物園 → 貓空</div>
                    `);
                    
                    console.log('貓空左線(動物園)繪製完成，座標點數量:', coordinates.length);
                } else {
                    console.warn('貓空左線(動物園)座標解析失敗，使用備用座標');
                    useBackupRoute('cat-left');
                }
            } else {
                console.warn('貓空左線(動物園)資料格式不正確，使用備用資料');
                useBackupRoute('cat-left');
            }
        })
        .catch(error => {
            console.error('獲取貓空左線(動物園)資料失敗:', error);
            useBackupRoute('cat-left');
        })
        .finally(() => {
            hideLoading();
        });
}

// 獲取並繪製貓空左線(指南宮)
function loadCatLeftZhinanRoute() {
    console.log('載入貓空左線(指南宮)');
    showLoading();
    
    fetch('/game/api/bus/cat-left-zhinan-route')
        .then(response => response.json())
        .then(data => {
            console.log('獲取到貓空左線(指南宮)資料:', data);
            
            // 解析路線座標
            if (data && Array.isArray(data)) {
                let coordinates = [];
                
                // 提取路線座標點
                data.forEach(point => {
                    if (point.PositionLat && point.PositionLon) {
                        coordinates.push([point.PositionLat, point.PositionLon]);
                    }
                });
                
                if (coordinates.length > 0) {
                    // 儲存路線座標
                    routeCoordinates['cat-left-zhinan'] = coordinates;
                    
                    // 創建路線
                    const polyline = L.polyline(coordinates, {
                        color: routeColors['cat-left-zhinan'],
                        weight: 5,
                        opacity: 0.8
                    }).addTo(routeLayer);
                    
                    // 添加路線資訊彈窗
                    polyline.bindPopup(`
                        <div style="font-weight:bold;font-size:16px;">貓空纜車左線(指南宮)</div>
                        <div>方向: 貓空 → 指南宮</div>
                    `);
                    
                    console.log('貓空左線(指南宮)繪製完成，座標點數量:', coordinates.length);
                } else {
                    console.warn('貓空左線(指南宮)座標解析失敗，使用備用座標');
                    useBackupRoute('cat-left-zhinan');
                }
            } else {
                console.warn('貓空左線(指南宮)資料格式不正確，使用備用資料');
                useBackupRoute('cat-left-zhinan');
            }
        })
        .catch(error => {
            console.error('獲取貓空左線(指南宮)資料失敗:', error);
            useBackupRoute('cat-left-zhinan');
        })
        .finally(() => {
            hideLoading();
        });
}

// 獲取並繪製棕3路線
function loadBrown3Route() {
    console.log('載入棕3路線');
    showLoading();
    
    fetch('/game/api/bus/brown-3-route')
        .then(response => response.json())
        .then(data => {
            console.log('獲取到棕3路線資料:', data);
            
            // 解析路線座標
            if (data && Array.isArray(data)) {
                let coordinates = [];
                
                // 提取路線座標點
                data.forEach(point => {
                    if (point.PositionLat && point.PositionLon) {
                        coordinates.push([point.PositionLat, point.PositionLon]);
                    }
                });
                
                if (coordinates.length > 0) {
                    // 儲存路線座標
                    routeCoordinates['brown-3'] = coordinates;
                    
                    // 創建路線
                    const polyline = L.polyline(coordinates, {
                        color: routeColors['brown-3'],
                        weight: 5,
                        opacity: 0.8
                    }).addTo(routeLayer);
                    
                    // 添加路線資訊彈窗
                    polyline.bindPopup(`
                        <div style="font-weight:bold;font-size:16px;">棕3路線</div>
                        <div>方向: 起點 → 終點</div>
                    `);
                    
                    console.log('棕3路線繪製完成，座標點數量:', coordinates.length);
                } else {
                    console.warn('棕3路線座標解析失敗，使用備用座標');
                    useBackupRoute('brown-3');
                }
            } else {
                console.warn('棕3路線資料格式不正確，使用備用資料');
                useBackupRoute('brown-3');
            }
        })
        .catch(error => {
            console.error('獲取棕3路線資料失敗:', error);
            useBackupRoute('brown-3');
        })
        .finally(() => {
            hideLoading();
        });
}

// 使用備用路線資料（當API獲取失敗時）
function useBackupRoute(routeKey) {
    console.log(`使用備用路線資料: ${routeKey}`);
    
    let coordinates = [];
    
    // 根據路線類型提供備用座標
    switch(routeKey) {
        case 'cat-right':
            coordinates = [
                [25.0323, 121.5342], // 貓空站
                [25.0298, 121.5332], // 中途點
                [25.0273, 121.5321]  // 動物園站
            ];
            break;
            
        case 'cat-left':
            coordinates = [
                [25.0273, 121.5321], // 動物園站
                [25.0298, 121.5332], // 中途點
                [25.0323, 121.5342]  // 貓空站
            ];
            break;
              case 'cat-left-zhinan':
            // 修正貓空左線(指南宮)的備用路線座標
            coordinates = [
                [25.0323, 121.5342], // 貓空站
                [25.0330, 121.5360], // 中途點1
                [25.0345, 121.5376], // 中途點2
                [25.0355, 121.5389]  // 指南宮站
            ];
            break;
            
        case 'brown-3':
            // 棕3路線的備用路線座標（示例座標，實際應根據真實路線調整）
            coordinates = [
                [25.0400, 121.5500], // 起點站
                [25.0420, 121.5520], // 中途點1
                [25.0440, 121.5540], // 中途點2
                [25.0460, 121.5560]  // 終點站
            ];
            break;
            
        case 'brown-3':
            coordinates = [
                [25.0330, 121.5350], // 起點
                [25.0340, 121.5360], // 中途點
                [25.0350, 121.5370], // 終點
            ];
            break;
    }
    
    // 儲存路線座標
    routeCoordinates[routeKey] = coordinates;
    
    // 創建路線
    const polyline = L.polyline(coordinates, {
        color: routeColors[routeKey],
        weight: 5,
        opacity: 0.8
    }).addTo(routeLayer);
    
    // 添加路線資訊彈窗
    let routeName = '';
    let direction = '';
    
    switch(routeKey) {
        case 'cat-right':
            routeName = '貓空纜車右線';
            direction = '貓空 → 動物園';
            break;
        case 'cat-left':
            routeName = '貓空纜車左線(動物園)';
            direction = '動物園 → 貓空';
            break;        case 'cat-left-zhinan':
            routeName = '貓空纜車左線(指南宮)';
            direction = '貓空 → 指南宮';
            break;
        case 'brown-3':
            routeName = '棕3路線';
            direction = '起點 → 終點';
            break;
        case 'brown-3':
            routeName = '棕3路線';
            direction = '起點 → 終點';
            break;
    }
    
    polyline.bindPopup(`
        <div style="font-weight:bold;font-size:16px;">${routeName}</div>
        <div>方向: ${direction}</div>
        <div><small>(備用資料)</small></div>
    `);
    
    console.log(`備用路線 ${routeKey} 繪製完成`);
}

// 加載所有路線
function loadAllRoutes() {
    console.log('加載所有路線');
    
    // 清除現有路線圖層
    routeLayer.clearLayers();
    
    // 加載貓空右線
    loadCatRightRoute();
    
    // 加載貓空左線(動物園)
    loadCatLeftRoute();
    
    // 加載貓空左線(指南宮)
    loadCatLeftZhinanRoute();
    
    // 加載棕3路線
    loadBrown3Route();
}

// 導出模組
export {
    loadCatRightRoute,
    loadCatLeftRoute,
    loadCatLeftZhinanRoute,
    loadBrown3Route,
    loadAllRoutes,
    useBackupRoute
};