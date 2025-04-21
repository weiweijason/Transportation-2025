// 模組：user-location.js - 使用者位置管理

import { map } from './config.js';

// 默認台北市中心座標 (當無法獲取用戶位置時使用)
const DEFAULT_POSITION = [25.0330, 121.5654];

// 全局位置變數，供其他模組使用
let userLocation = null;

// 更新用戶位置 - 返回 Promise 以支持異步處理
function updateUserLocation() {
    return new Promise((resolve, reject) => {
        // 檢查地圖實例
        if (!window.busMap) {
            console.warn('地圖實例不存在，無法更新位置');
            reject(new Error('地圖實例不存在'));
            return;
        }

        // 檢查地理位置API是否可用
        if (!navigator.geolocation) {
            console.warn('瀏覽器不支持地理定位');
            useDefaultLocation('瀏覽器不支持地理定位');
            reject(new Error('瀏覽器不支持地理定位'));
            return;
        }

        // 設置位置獲取超時
        const positionOptions = {
            enableHighAccuracy: true,
            timeout: 10000,        // 10秒超時
            maximumAge: 60000      // 位置快取有效期1分鐘
        };

        // 獲取位置
        navigator.geolocation.getCurrentPosition(
            (position) => {
                try {
                    // 獲取位置座標
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const userLatLng = [lat, lng];
                    
                    // 保存全局位置引用
                    userLocation = userLatLng;
                    window.userLocation = userLatLng;
                    
                    // 更新用戶位置標記
                    if (window.userMarker) {
                        window.userMarker.setLatLng(userLatLng);
                        window.userCircle.setLatLng(userLatLng);
                    } else {
                        // 創建用戶位置標記
                        window.userMarker = L.marker(userLatLng, {
                            icon: L.divIcon({
                                className: 'user-marker',
                                html: '<div style="background-color:#4285F4;width:20px;height:20px;border-radius:50%;border:3px solid white;"></div>',
                                iconSize: [20, 20],
                                iconAnchor: [10, 10]
                            })
                        }).addTo(window.busMap);
                        
                        // 創建用戶範圍圓圈
                        window.userCircle = L.circle(userLatLng, {
                            radius: 300,
                            color: '#4285F4',
                            fillColor: '#4285F4',
                            fillOpacity: 0.1,
                            weight: 1
                        }).addTo(window.busMap);
                    }
                    
                    // 更新地圖視角
                    window.busMap.setView(userLatLng, 15);
                    
                    // 更新位置顯示
                    const locationElement = document.getElementById('currentLocation');
                    if (locationElement) {
                        locationElement.textContent = `緯度: ${lat.toFixed(5)}, 經度: ${lng.toFixed(5)}`;
                    }
                    
                    console.log('位置更新成功:', userLatLng);
                    resolve(userLatLng);
                } catch (error) {
                    console.error('處理位置數據時出錯:', error);
                    useDefaultLocation('處理位置數據時出錯');
                    reject(error);
                }
            },
            (error) => {
                // 位置錯誤處理
                let errorMsg = '';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = '您已拒絕位置訪問權限';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = '位置信息不可用';
                        break;
                    case error.TIMEOUT:
                        errorMsg = '位置請求超時';
                        break;
                    default:
                        errorMsg = '獲取位置時發生未知錯誤';
                }
                
                console.warn('定位錯誤:', errorMsg, error);
                useDefaultLocation(errorMsg);
                reject(new Error(errorMsg));
            },
            positionOptions
        );
    });
}

// 使用默認位置
function useDefaultLocation(reason) {
    console.log(`使用默認位置 (${reason})`, DEFAULT_POSITION);
    
    // 設置默認位置
    userLocation = DEFAULT_POSITION;
    window.userLocation = DEFAULT_POSITION;
    
    // 如果地圖存在，更新地圖顯示
    if (window.busMap) {
        if (window.userMarker) {
            window.userMarker.setLatLng(DEFAULT_POSITION);
            window.userCircle.setLatLng(DEFAULT_POSITION);
        } else {
            // 創建用戶位置標記（使用不同顏色表示這是默認位置）
            window.userMarker = L.marker(DEFAULT_POSITION, {
                icon: L.divIcon({
                    className: 'user-marker',
                    html: '<div style="background-color:#FFA500;width:20px;height:20px;border-radius:50%;border:3px solid white;"></div>',
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                })
            }).addTo(window.busMap);
            
            // 創建用戶範圓圈（使用不同顏色表示這是默認位置）
            window.userCircle = L.circle(DEFAULT_POSITION, {
                radius: 300,
                color: '#FFA500',
                fillColor: '#FFA500',
                fillOpacity: 0.1,
                weight: 1
            }).addTo(window.busMap);
        }
        
        // 更新地圖視角
        window.busMap.setView(DEFAULT_POSITION, 14);
    }
    
    // 更新位置顯示
    const locationElement = document.getElementById('currentLocation');
    if (locationElement) {
        locationElement.textContent = `無法獲取位置 (${reason})`;
    }
}

// 檢查兩個位置之間的距離（公尺）
function getDistanceBetween(pos1, pos2) {
    if (!pos1 || !pos2) return Infinity;
    
    try {
        // 使用 Leaflet 的 latLng 類來計算距離
        const latLng1 = L.latLng(pos1[0], pos1[1]);
        const latLng2 = L.latLng(pos2[0], pos2[1]);
        
        return latLng1.distanceTo(latLng2);
    } catch (error) {
        console.error('計算距離時出錯:', error);
        return Infinity;
    }
}

// 檢查用戶是否接近某個位置
function isNearLocation(targetPos, maxDistance = 300) {
    if (!userLocation || !targetPos) return false;
    
    const distance = getDistanceBetween(userLocation, targetPos);
    return distance <= maxDistance;
}

// 導出模組
export { 
    updateUserLocation, 
    useDefaultLocation, 
    getDistanceBetween, 
    isNearLocation,
    DEFAULT_POSITION 
};