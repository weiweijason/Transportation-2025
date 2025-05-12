/**
 * 教學模式道館功能
 * 負責道館選擇和佔領
 */

const tutorialGym = {
    // 顯示道館選擇界面
    showGymSelection: function() {
        // 重新顯示所有道館
        tutorialConfig.map.setView([25.03556, 121.51972], 14);
        
        // 移除精靈標記（如果存在）
        if (tutorialConfig.creatureMarker) {
            tutorialConfig.map.removeLayer(tutorialConfig.creatureMarker);
        }
        
        // 為道館項目添加點擊事件
        const gymItems = document.querySelectorAll('.gym-item');
        gymItems.forEach(item => {
            item.addEventListener('click', function() {
                // 移除之前的選中狀態
                gymItems.forEach(i => i.classList.remove('selected'));
                
                // 添加當前選中狀態
                this.classList.add('selected');
                
                // 獲取所選道館信息
                const gymId = this.getAttribute('data-gym-id');
                const lat = parseFloat(this.getAttribute('data-lat'));
                const lng = parseFloat(this.getAttribute('data-lng'));
                
                // 保存所選道館
                tutorialConfig.selectedGym = tutorialConfig.gyms.find(g => g.id === gymId) || {
                    id: gymId,
                    name: this.querySelector('h6').textContent,
                    lat: lat,
                    lng: lng
                };
                
                // 移動地圖到所選道館 - 動畫效果
                tutorialConfig.map.flyTo([lat, lng], 16, {
                    duration: 1.5
                });
                
                // 顯示道館資訊的氣泡視窗
                const gymInfo = `
                    <div class="text-center">
                        <h5>${tutorialConfig.selectedGym.name}</h5>
                        <p class="mb-1"><span class="badge bg-success">等級 ${tutorialConfig.selectedGym.id.includes('2') ? '2' : '3'}</span></p>
                        <p class="mb-0"><small>控制者：無人佔領</small></p>
                    </div>
                `;
                
                // 找到對應的標記並打開氣泡窗
                tutorialConfig.gymMarkers.forEach(marker => {
                    if (marker.id === gymId) {
                        marker.marker.bindPopup(gymInfo).openPopup();
                    }
                });
                
                // 啟用下一步按鈕
                tutorialConfig.elements.tutorialNext.disabled = false;
            });
        });
        
        // 直到選擇道館前禁用下一步按鈕
        tutorialConfig.elements.tutorialNext.disabled = true;
        
        return true;
    },
    
    // 顯示道館占領界面
    showGymOccupation: function() {
        // 確保已選擇道館
        if (tutorialConfig.selectedGym) {
            // 使用動畫效果飛到所選道館
            tutorialConfig.map.flyTo([tutorialConfig.selectedGym.lat, tutorialConfig.selectedGym.lng], 17, {
                duration: 1.5
            });
            
            // 更新道館界面
            document.getElementById('battleArenaName').textContent = tutorialConfig.selectedGym.name || '道館';
            
            // 更新界面顯示的精靈數據
            const defaultCreature = tutorialConfig.defaultCreature;
            if (defaultCreature) {
                document.getElementById('starterCreatureImg').src = defaultCreature.image;
                document.getElementById('starterCreatureName').textContent = defaultCreature.name;
                document.getElementById('starterCreaturePower').textContent = defaultCreature.power || 50;
            }
            
            // 選擇精靈項目添加點擊事件
            const creatureItem = document.querySelector('.creature-selection-item');
            creatureItem.addEventListener('click', function() {
                this.classList.toggle('selected');
                if (this.classList.contains('selected')) {
                    this.style.borderColor = '#4CAF50';
                    document.getElementById('occupyGymButton').disabled = false;
                } else {
                    this.style.borderColor = '#dee2e6';
                    document.getElementById('occupyGymButton').disabled = true;
                }
            });
            
            // 初始禁用佔領按鈕，直到選擇了精靈
            document.getElementById('occupyGymButton').disabled = true;
            
            // 設置占領按鈕事件
            document.getElementById('occupyGymButton').onclick = function() {
                // 占領動畫
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>占領中...';
                
                // 顯示佔領過程的視覺效果
                const gymMarker = tutorialConfig.gymMarkers.find(marker => marker.id === tutorialConfig.selectedGym.id);
                if (gymMarker) {
                    // 添加視覺效果：道館閃爍
                    let opacity = 1.0;
                    const blinkInterval = setInterval(() => {
                        opacity = opacity === 1.0 ? 0.5 : 1.0;
                        gymMarker.marker.setOpacity(opacity);
                    }, 300);
                    
                    // 將選擇的道館和精靈數據發送到服務器
                    const gymData = {
                        gym_id: tutorialConfig.selectedGym.id,
                        gym_name: tutorialConfig.selectedGym.name,
                        gym_level: tutorialConfig.selectedGym.id.includes('2') ? 2 : 3,
                        lat: tutorialConfig.selectedGym.lat,
                        lng: tutorialConfig.selectedGym.lng,
                        guardian_creature: {
                            id: tutorialConfig.defaultCreature.id,
                            name: tutorialConfig.defaultCreature.name,
                            image: tutorialConfig.defaultCreature.image,
                            type: tutorialConfig.defaultCreature.type,
                            power: tutorialConfig.defaultCreature.power
                        }
                    };
                    
                    // 發送請求到後端
                    fetch(`/auth/tutorial/set-base-gym`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(gymData)
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log("佔領成功，伺服器回應:", data);
                        // 繼續視覺效果和UI更新...
                        
                        // 3秒後停止閃爍
                        setTimeout(() => {
                            clearInterval(blinkInterval);
                            gymMarker.marker.setOpacity(1.0);
                            
                            // 更新道館氣泡視窗以顯示佔領狀態
                            const newPopup = `
                                <div class="text-center">
                                    <h5>${tutorialConfig.selectedGym.name}</h5>
                                    <p class="mb-1"><span class="badge bg-success">等級 ${tutorialConfig.selectedGym.id.includes('2') ? '2' : '3'}</span></p>
                                    <p class="mb-0"><small>控制者：您</small></p>
                                    <div class="mt-2">
                                        <img src="${tutorialConfig.defaultCreature.image}" class="img-fluid" style="max-height: 60px; border-radius: 5px;">
                                        <p class="small mb-0 mt-1">${tutorialConfig.defaultCreature.name}</p>
                                    </div>
                                </div>
                            `;
                            
                            gymMarker.marker.bindPopup(newPopup);
                            gymMarker.marker.openPopup();
                        }, 3000);
                    })
                    .catch(error => {
                        console.error("佔領道館失敗:", error);
                        // 清除閃爍效果
                        clearInterval(blinkInterval);
                        gymMarker.marker.setOpacity(1.0);
                        
                        // 重置按鈕狀態
                        this.disabled = false;
                        this.innerHTML = '<i class="fas fa-flag me-2"></i>佔領道館';
                        
                        // 顯示錯誤消息
                        const occupationNotice = document.querySelector('.occupation-notice');
                        occupationNotice.classList.remove('alert-info');
                        occupationNotice.classList.add('alert-danger');
                        occupationNotice.innerHTML = `
                            <i class="fas fa-exclamation-circle me-2"></i>
                            <small>佔領道館失敗，請稍後再試。</small>
                        `;
                        
                        return;
                    });
                }
                
                // 佔領完成
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-check-circle me-2"></i>占領成功！';
                    this.className = 'btn btn-success btn-block mt-3 w-100';
                    
                    // 顯示佔領成功訊息
                    const occupationNotice = document.querySelector('.occupation-notice');
                    occupationNotice.classList.remove('alert-info');
                    occupationNotice.classList.add('alert-success');
                    occupationNotice.innerHTML = `
                        <i class="fas fa-check-circle me-2"></i>
                        <small>太棒了！您已成功佔領 ${tutorialConfig.selectedGym.name}！您的精靈將守護此道館，直到被其他玩家挑戰成功。</small>
                    `;
                    
                    // 更新道館狀態指示
                    const battleStatus = document.querySelector('.battle-status');
                    battleStatus.innerHTML = `
                        <span class="badge bg-primary">已佔領</span>
                        <span class="text-primary small">由您控制</span>
                    `;                    
                    // 自動完成教程
                    setTimeout(() => {
                        tutorialConfig.completeTutorial();
                    }, 2500);
                }, 3500);
            };
        }
        
        return true;
    }
};

// 導出模塊
window.tutorialGym = tutorialGym;
