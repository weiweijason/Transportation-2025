/**
 * 教學模式精靈捕捉功能
 * 負責精靈顯示、捕捉互動等
 */

const tutorialCreature = {
    // 顯示精靈捕捉界面
    showCreatureCapture: function() {
        // 添加精靈標記 - 使用動畫效果
        const creatureIcon = L.divIcon({
            className: 'creature-marker',
            html: '<i class="fas fa-dragon"></i><div class="pulse-ring"></div>',
            iconSize: [40, 40]
        });
        
        const defaultCreature = tutorialConfig.defaultCreature;
        
        // 在玩家附近添加精靈（站牌附近）
        tutorialConfig.creatureMarker = L.marker([defaultCreature.lat, defaultCreature.lng], {icon: creatureIcon})
            .addTo(tutorialConfig.map)
            .bindPopup('<div class="text-center"><b>精靈出現了！</b><br>點擊捕捉</div>');
        
        // 移動地圖以顯示精靈
        tutorialConfig.map.flyTo([defaultCreature.lat, defaultCreature.lng], 16, {
            duration: 1.5
        });
        
        // 開始倒數計時器 (模擬精靈會消失)
        let countdown = 30;
        const countdownElement = document.getElementById('catchCountdown');
        countdownElement.textContent = countdown;
        
        const countdownInterval = setInterval(() => {
            countdown--;
            countdownElement.textContent = countdown;
            if (countdown <= 0) {
                clearInterval(countdownInterval);
            }
        }, 1000);
        
        // 保存計時器引用以便後續清除
        tutorialConfig.countdownInterval = countdownInterval;
        
        // 設置捕捉界面
        document.getElementById('creatureImage').src = defaultCreature.image;
        document.getElementById('creatureName').textContent = defaultCreature.name;
        
        // 設置精靈類型和稀有度
        const creatureTypeElement = document.getElementById('creatureType');
        creatureTypeElement.textContent = defaultCreature.type;
        creatureTypeElement.className = 'creature-type badge';
        
        document.getElementById('creatureRarity').textContent = defaultCreature.rarity || '普通';
        
        // 根據類型設置樣式
        if (defaultCreature.type === '水系') {
            creatureTypeElement.classList.add('bg-primary');
        } else if (defaultCreature.type === '火系') {
            creatureTypeElement.classList.add('bg-danger');
        } else if (defaultCreature.type === '風系') {
            creatureTypeElement.classList.add('bg-success');
        } else if (defaultCreature.type === '土系') {
            creatureTypeElement.classList.add('bg-warning');
        }
        
        // 設置能量條
        const powerPercentage = (defaultCreature.power / 100) * 100;
        document.getElementById('powerBar').style.width = powerPercentage + '%';
        
        // 設置捕捉按鈕事件
        document.getElementById('catchButton').onclick = function() {
            // 清除倒數計時
            clearInterval(tutorialConfig.countdownInterval);
            
            // 捕捉動畫
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>前往捕捉...';
            
            // 轉向到互動式捕捉頁面
            window.location.href = `/auth/tutorial/interactive-capture/${defaultCreature.id}`;
        };
        
        return true;
    },
    
    // 處理捕捉成功後的操作
    handleCaptureSuccess: function() {
        const defaultCreature = tutorialConfig.defaultCreature;
        
        // 填充精靈選擇界面
        document.getElementById('starterCreatureImg').src = defaultCreature.image || "/static/img/default-creature.png";
        document.getElementById('starterCreatureName').textContent = defaultCreature.name;
        
        const typeElement = document.getElementById('starterCreatureType');
        typeElement.textContent = defaultCreature.type;
        typeElement.className = 'creature-select-type badge';
        
        if (defaultCreature.type === '水系') {
            typeElement.classList.add('bg-primary');
        } else if (defaultCreature.type === '火系') {
            typeElement.classList.add('bg-danger');
        } else if (defaultCreature.type === '風系') {
            typeElement.classList.add('bg-success');
        } else if (defaultCreature.type === '土系') {
            typeElement.classList.add('bg-warning');
        }
        
        document.getElementById('starterCreaturePower').textContent = defaultCreature.power;
        
        // 更新捕捉按鈕狀態
        const catchButton = document.getElementById('catchButton');
        catchButton.innerHTML = '<i class="fas fa-check-circle me-2"></i>捕捉成功！';
        catchButton.className = 'btn btn-success btn-lg';
        
        // 移除精靈標記
        if (tutorialConfig.creatureMarker) {
            tutorialConfig.map.removeLayer(tutorialConfig.creatureMarker);
        }
    }
};

// 導出模塊
window.tutorialCreature = tutorialCreature;
