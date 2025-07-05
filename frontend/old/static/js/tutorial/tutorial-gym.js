/**
 * 教學模式道館功能
 * 負責道館選擇和佔領
 */

console.log('>>> DEBUG: tutorial-gym.js 文件已載入');

const tutorialGym = {    // 顯示道館選擇界面
    showGymSelection: function() {
        console.log('>>> DEBUG: 顯示道館選擇界面');
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
                        <p class="mb-1"><span class="badge bg-danger">等級 5 - 特級基地</span></p>
                        <p class="mb-0"><small>狀態：可建立個人基地</small></p>
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
        console.log('>>> DEBUG: 顯示道館占領界面');
        console.log('>>> DEBUG: 當前選擇的道館:', tutorialConfig.selectedGym);
        
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
                document.getElementById('starterCreatureAttack').textContent = defaultCreature.attack || defaultCreature.power || 50;
                document.getElementById('starterCreatureHP').textContent = defaultCreature.hp || (defaultCreature.power || 50) * 10;
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
            document.getElementById('occupyGymButton').disabled = true;            // 設置占領按鈕事件
            document.getElementById('occupyGymButton').onclick = function() {
                console.log('>>> DEBUG: 建立基地按鈕被點擊！');
                console.log('>>> DEBUG: 所選道館:', tutorialConfig.selectedGym);
                
                // 占領動畫
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>建立基地中...';                console.log('>>> DEBUG: 開始建立基地流程...');
                console.log('>>> DEBUG: tutorialConfig.selectedGym:', tutorialConfig.selectedGym);
                console.log('>>> DEBUG: tutorialConfig.defaultCreature:', tutorialConfig.defaultCreature);                console.log('>>> DEBUG: tutorialConfig.gymMarkers:', tutorialConfig.gymMarkers);
                console.log('>>> DEBUG: 尋找對應的道館標記，目標ID:', tutorialConfig.selectedGym.id);
                  // 檢查是否有道館標記，如果沒有，則創建它們
                if (!tutorialConfig.gymMarkers || tutorialConfig.gymMarkers.length === 0) {
                    console.log('>>> DEBUG: 道館標記陣列為空，重新創建道館標記');
                    // 調用 tutorialMap 的 showPlayerAndGyms 方法來創建道館標記
                    tutorialMap.showPlayerAndGyms();
                    console.log('>>> DEBUG: 創建道館標記完成，現在有', tutorialConfig.gymMarkers.length, '個標記');
                }
                
                // 顯示佔領過程的視覺效果
                const gymMarker = tutorialConfig.gymMarkers.find(marker => marker.id === tutorialConfig.selectedGym.id);
                console.log('>>> DEBUG: 找到的道館標記:', gymMarker);
                console.log('>>> DEBUG: 目前 gymMarkers 陣列長度:', tutorialConfig.gymMarkers.length);
                console.log('>>> DEBUG: gymMarkers 內容:', tutorialConfig.gymMarkers);
                
                if (gymMarker) {
                    console.log('>>> DEBUG: 道館標記存在，開始視覺效果');
                    // 添加視覺效果：道館閃爍
                    let opacity = 1.0;
                    const blinkInterval = setInterval(() => {
                        opacity = opacity === 1.0 ? 0.5 : 1.0;
                        gymMarker.marker.setOpacity(opacity);
                    }, 300);
                    
                    console.log('>>> DEBUG: 開始準備道館數據...');
                    
                    // 確保 defaultCreature 存在，如果不存在則使用默認值
                    const defaultCreature = tutorialConfig.defaultCreature || {
                        id: 'starter_creature',
                        name: '初始精靈',
                        image: '/static/images/creatures/default.png',
                        type: 'normal',
                        power: 50
                    };
                    
                    console.log('>>> DEBUG: 使用的精靈數據:', defaultCreature);
                    
                    // 將選擇的道館和精靈數據發送到服務器
                    const gymData = {
                        gym_id: tutorialConfig.selectedGym.id,
                        gym_name: tutorialConfig.selectedGym.name,
                        gym_level: 5, // 所有基地道館都是5級
                        lat: tutorialConfig.selectedGym.lat,
                        lng: tutorialConfig.selectedGym.lng,
                        guardian_creature: {
                            id: defaultCreature.id,
                            name: defaultCreature.name,
                            image: defaultCreature.image,
                            type: defaultCreature.type,
                            power: defaultCreature.power                        }
                    };
                      // 發送請求到後端
                    console.log(">>> DEBUG: 準備發送道館數據到後端:", gymData);
                    console.log(">>> DEBUG: 請求URL:", `/auth/tutorial/set-base-gym`);
                    console.log(">>> DEBUG: 請求方法: POST");
                    console.log(">>> DEBUG: 請求標頭:", {'Content-Type': 'application/json'});
                    console.log(">>> DEBUG: 請求主體:", JSON.stringify(gymData));
                    
                    // 添加更詳細的 fetch 調試
                    console.log(">>> DEBUG: 開始發送 fetch 請求...");
                      fetch(`/auth/tutorial/set-base-gym`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Tutorial-Mode': 'true',
                            'X-Tutorial-User-ID': 'tutorial_user_' + Date.now()
                        },
                        body: JSON.stringify(gymData)
                    })
                    .then(response => {
                        console.log(">>> DEBUG: 收到後端回應，狀態:", response.status);
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.json();
                    })                    .then(data => {
                        console.log(">>> DEBUG: 基地建立成功，伺服器回應:", data);// 顯示保存到 Firebase 的確認訊息
                        if (data.success) {
                            console.log("✅ 基地道館資料已成功保存到:");
                            console.log("   - user_base_gyms 集合 (全局基地道館)");
                            console.log("   - users/{user_id}/user_arenas 子集合 (用戶道館管理)");
                        }
                        
                        // 繼續視覺效果和UI更新...
                        
                        // 3秒後停止閃爍
                        setTimeout(() => {
                            clearInterval(blinkInterval);
                            gymMarker.marker.setOpacity(1.0);
                            
                            // 更新道館氣泡視窗以顯示佔領狀態
                            const newPopup = `
                                <div class="text-center">
                                    <h5>${tutorialConfig.selectedGym.name}</h5>
                                    <p class="mb-1"><span class="badge bg-danger">等級 5 - 個人基地</span></p>
                                    <p class="mb-0"><small>基地主：您</small></p>
                                    <div class="mt-2">
                                        <img src="${tutorialConfig.defaultCreature.image}" class="img-fluid" style="max-height: 60px; border-radius: 5px;">
                                        <p class="small mb-0 mt-1">${tutorialConfig.defaultCreature.name}</p>
                                    </div>
                                </div>
                            `;
                              gymMarker.marker.bindPopup(newPopup);
                            gymMarker.marker.openPopup();
                            
                            // 只有在Firebase保存成功後才執行完成流程
                            setTimeout(() => {
                                // 更新按鈕為成功狀態
                                document.getElementById('occupyGymButton').innerHTML = '<i class="fas fa-check-circle me-2"></i>建立成功！';
                                document.getElementById('occupyGymButton').className = 'btn btn-success btn-block mt-3 w-100';
                                
                                // 顯示建立成功訊息
                                const occupationNotice = document.querySelector('.occupation-notice');
                                occupationNotice.classList.remove('alert-info');
                                occupationNotice.classList.add('alert-success');
                                occupationNotice.innerHTML = `
                                    <i class="fas fa-check-circle me-2"></i>
                                    <small>太棒了！您已成功建立基地 ${tutorialConfig.selectedGym.name}！道館資料已保存到 Firebase，您的精靈將守護此基地。</small>
                                `;
                                
                                // 更新道館狀態指示
                                const battleStatus = document.querySelector('.battle-status');
                                battleStatus.innerHTML = `
                                    <span class="badge bg-primary">已建立</span>
                                    <span class="text-primary small">由您控制</span>
                                `;
                                
                                // 自動完成教程
                                setTimeout(() => {
                                    tutorialConfig.completeTutorial();
                                }, 2500);
                            }, 500);
                        }, 3000);
                    })                    .catch(error => {
                        console.error(">>> DEBUG: 建立基地道館失敗:", error);
                        console.error(">>> DEBUG: 錯誤詳情:", error.message);
                        console.error(">>> DEBUG: 錯誤堆疊:", error.stack);
                        // 清除閃爍效果
                        clearInterval(blinkInterval);
                        gymMarker.marker.setOpacity(1.0);
                        
                        // 重置按鈕狀態
                        this.disabled = false;
                        this.innerHTML = '<i class="fas fa-home me-2"></i>建立基地';
                        
                        // 顯示錯誤消息
                        const occupationNotice = document.querySelector('.occupation-notice');
                        occupationNotice.classList.remove('alert-info');
                        occupationNotice.classList.add('alert-danger');
                        occupationNotice.innerHTML = `
                            <i class="fas fa-exclamation-circle me-2"></i>
                            <small>建立基地失敗，請稍後再試。</small>
                        `;
                          return;
                    });
                }
            };
        }
        
        return true;
    }
};

// 導出模塊
window.tutorialGym = tutorialGym;
