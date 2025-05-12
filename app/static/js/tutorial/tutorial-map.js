/**
 * 教學模式地圖功能
 * 負責地圖初始化、標記添加和路線繪製
 */

const tutorialMap = {
    // 初始化地圖
    initMap: function() {
        // 創建地圖，以貓空纜車接駁路線為中心
        tutorialConfig.map = L.map('tutorialMap', {
            zoomControl: false,  // 移除默認縮放控制按鈕
            attributionControl: false  // 移除歸因控制
        }).setView([25.03556, 121.51972], 14);
        
        // 添加自定義地圖樣式
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(tutorialConfig.map);
        
        // 添加自定義的縮放控制按鈕
        L.control.zoom({
            position: 'topright'
        }).addTo(tutorialConfig.map);
        
        // 為教學目的，啟用部分互動功能
        tutorialConfig.map.dragging.enable();
        tutorialConfig.map.touchZoom.enable();
        tutorialConfig.map.doubleClickZoom.enable();
        tutorialConfig.map.scrollWheelZoom.enable();
        
        // 添加自定義的公車路線覆蓋物
        this.addBusRoutes();
        
        return true;
    },
    
    // 添加公車路線覆蓋物
    addBusRoutes: function() {
        // 貓空左線路線 (示意性數據)
        const leftRoutePoints = [
            [25.03556, 121.51972], // 中正紀念堂
            [25.03756, 121.52172], // 東門站
            [25.03956, 121.52372], // 永康街
            [25.04156, 121.52572]  // 捷運公館站
        ];
        
        // 貓空右線路線 (示意性數據)
        const rightRoutePoints = [
            [25.03556, 121.51972], // 中正紀念堂
            [25.03756, 121.52172], // 東門站
            [25.03456, 121.52372], // 另一條路線點
            [25.03256, 121.52572]  // 另一條路線點
        ];
        
        // 路線指南宮線 (示意性數據)
        const zhiNanRoutePoints = [
            [25.03556, 121.51972], // 中正紀念堂
            [25.03256, 121.51672], // 另一條路線點
            [25.02956, 121.51372], // 另一條路線點
            [25.02656, 121.51072]  // 另一條路線點
        ];
        
        // 添加左線路線
        L.polyline(leftRoutePoints, {
            color: '#4caf50',
            weight: 5,
            opacity: 0.7,
            dashArray: "10, 10"
        }).addTo(tutorialConfig.map);
        
        // 添加右線路線
        L.polyline(rightRoutePoints, {
            color: '#ff9800',
            weight: 5,
            opacity: 0.7,
            dashArray: "10, 10"
        }).addTo(tutorialConfig.map);
        
        // 添加指南宮線路線
        L.polyline(zhiNanRoutePoints, {
            color: '#9c27b0',
            weight: 5,
            opacity: 0.7,
            dashArray: "10, 10"
        }).addTo(tutorialConfig.map);
    },
    
    // 顯示玩家位置和道館
    showPlayerAndGyms: function() {
        // 添加玩家標記 - 更現代化的設計
        const playerIcon = L.divIcon({
            className: 'player-marker',
            html: '<i class="fas fa-street-view"></i>',
            iconSize: [40, 40],
            iconAnchor: [20, 40]
        });
        
        // 玩家位置（使用中正紀念堂作為起點）- 添加定位動畫
        tutorialConfig.playerMarker = L.marker([25.03556, 121.51972], {icon: playerIcon}).addTo(tutorialConfig.map);
        
        // 定位動畫
        tutorialConfig.map.flyTo([25.03556, 121.51972], 15, {
            duration: 2,
            easeLinearity: 0.25
        });
        
        // 添加玩家位置的脈衝動畫效果
        const pulseCircle = L.circle([25.03556, 121.51972], {
            color: '#2ecc71',
            fillColor: '#2ecc71',
            fillOpacity: 0.3,
            radius: 50
        }).addTo(tutorialConfig.map);
        
        // 脈衝動畫
        let pulse = 0;
        const pulseAnimation = setInterval(() => {
            pulse = pulse === 0 ? 100 : 0;
            pulseCircle.setRadius(pulse);
        }, 1000);
        
        // 5秒後停止脈衝動畫
        setTimeout(() => {
            clearInterval(pulseAnimation);
            tutorialConfig.map.removeLayer(pulseCircle);
        }, 5000);
        
        // 添加道館標記 - 針對不同等級使用不同圖標
        tutorialConfig.gyms.forEach(gym => {
            // 判斷道館等級
            const isHighLevel = !gym.id.includes('2'); // 3級道館為高級
            
            const gymIcon = L.divIcon({
                className: `gym-marker ${isHighLevel ? 'high-level' : 'mid-level'}`,
                html: `<i class="fas ${isHighLevel ? 'fa-building' : 'fa-house-user'}"></i>`,
                iconSize: [40, 40],
                iconAnchor: [20, 40]
            });
            
            // 創建標記並添加到地圖
            const marker = L.marker([gym.lat, gym.lng], {icon: gymIcon})
                .addTo(tutorialConfig.map);
            
            // 創建豐富的氣泡窗口內容
            const popupContent = `
                <div class="gym-popup text-center">
                    <h5>${gym.name}</h5>
                    <p class="mb-1"><span class="badge ${isHighLevel ? 'bg-danger' : 'bg-success'}">等級 ${isHighLevel ? '3' : '2'}</span></p>
                    <div class="routes-container mt-2">
                        ${isHighLevel ? 
                            `<span class="route-badge" style="background-color: #4caf50;">貓空左線</span>
                            <span class="route-badge" style="background-color: #ff9800;">貓空右線</span>
                            <span class="route-badge" style="background-color: #9c27b0;">貓左指南宮</span>` : 
                            `<span class="route-badge" style="background-color: #4caf50;">貓空左線</span>
                            <span class="route-badge" style="background-color: #ff9800;">貓空右線</span>`
                        }
                    </div>
                    <p class="mt-2 mb-0"><small>點擊查看道館詳情</small></p>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            
            // 添加點擊事件
            marker.on('click', function() {
                // 選中對應的道館項目
                const gymItems = document.querySelectorAll('.gym-item');
                gymItems.forEach(item => {
                    if (item.getAttribute('data-gym-id') === gym.id) {
                        item.click();
                    }
                });
            });
            
            // 添加到標記數組
            tutorialConfig.gymMarkers.push({
                id: gym.id,
                marker: marker
            });
        });
        
        return true;
    }
};

// 導出模塊
window.tutorialMap = tutorialMap;
