/**
 * 精靈捕捉互動頁面主要邏輯
 * 處理魔法陣選擇、背包數據載入、捕捉動畫等功能
 */

class CaptureInteractive {
  constructor() {
    this.circleCounts = {
      normal: 0,
      advanced: 0,
      premium: 0
    };
    
    this.circleRates = {
      normal: 0.6,
      advanced: 0.8,
      premium: 0.95
    };
    
    this.selectedCircleType = 'premium';
    this.captureInProgress = false;
    
    this.initializeElements();
    this.bindEvents();
    this.loadUserBackpack();
  }
  
  // 初始化DOM元素
  initializeElements() {
    this.elements = {
      magicCircle: document.getElementById('magicCircle'),
      magicCircleInner: document.getElementById('magicCircleInner'),
      captureEffect: document.getElementById('captureEffect'),
      creatureImage: document.getElementById('creatureImage'),
      captureBtn: document.getElementById('captureBtn'),
      cancelBtn: document.getElementById('cancelBtn'),
      resultMessage: document.getElementById('resultMessage'),
      circleTypeItems: document.querySelectorAll('.circle-type-item')
    };
  }
  
  // 綁定事件監聽器
  bindEvents() {
    // 捕捉按鈕點擊事件
    this.elements.captureBtn.addEventListener('click', () => this.handleCapture());
    
    // 取消按鈕點擊事件
    this.elements.cancelBtn.addEventListener('click', () => window.history.back());
    
    // 魔法陣選擇事件
    this.elements.circleTypeItems.forEach(item => {
      item.addEventListener('click', () => this.selectCircleType(item));
    });
  }
  
  // 獲取CSRF Token
  getCsrfToken() {
    return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
  }
  
  // 從Firebase獲取用戶背包數據
  async loadUserBackpack() {
    try {
      console.log('開始載入用戶背包數據...');
      
      const response = await fetch('/game/api/user/backpack', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken()
        },
        credentials: 'same-origin'
      });
      
      console.log('API 響應狀態:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('API 響應數據:', data);
        
        if (data.success && data.backpack) {
          console.log('背包數據結構:', data.backpack);
          
          // 更新魔法陣數量
          this.circleCounts.normal = data.backpack.normal?.count || 0;
          this.circleCounts.advanced = data.backpack.advanced?.count || 0;
          this.circleCounts.premium = data.backpack.premium?.count || 0;
          
          console.log('更新後的魔法陣數量:', this.circleCounts);
          
          // 更新UI顯示
          this.updateCircleItems();
          
          // 設置默認選中的魔法陣
          this.setDefaultSelectedCircle();
          
          console.log('已載入背包數據:', this.circleCounts);
        } else {
          console.warn('API 響應格式錯誤:', data);
          this.setDefaultValues();
        }
      } else {
        console.error('獲取背包數據失敗:', response.status, response.statusText);
        try {
          const errorData = await response.text();
          console.error('錯誤詳情:', errorData);
        } catch (e) {
          console.error('無法讀取錯誤詳情');
        }
        this.setDefaultValues();
      }
    } catch (error) {
      console.error('載入背包數據時出錯:', error);
      this.setDefaultValues();
    }
  }
  
  // 設置默認值
  setDefaultValues() {
    console.log('設置默認魔法陣數量');
    this.circleCounts = {
      normal: 10,
      advanced: 5,
      premium: 3
    };
    this.updateCircleItems();
    this.setDefaultSelectedCircle();
    
    // 顯示提示信息
    this.showNotification('使用默認魔法陣數量（API載入失敗）', 'warning');
  }
  
  // 顯示通知
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const colors = {
      info: '#3498db',
      warning: '#f39c12',
      error: '#e74c3c',
      success: '#27ae60'
    };
    
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${colors[type] || colors.info};
      color: white;
      padding: 10px 15px;
      border-radius: 5px;
      z-index: 9999;
      font-size: 14px;
      max-width: 300px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
  
  // 設置默認選中的魔法陣
  setDefaultSelectedCircle() {
    const priority = ['premium', 'advanced', 'normal'];
    let defaultType = 'normal';
    
    for (const type of priority) {
      if (this.circleCounts[type] > 0) {
        defaultType = type;
        break;
      }
    }
    
    this.selectedCircleType = defaultType;
    
    // 更新UI顯示
    this.elements.circleTypeItems.forEach(item => {
      item.classList.remove('active');
      if (item.dataset.type === this.selectedCircleType) {
        item.classList.add('active');
      }
    });
    
    // 更新魔法陣圖片
    this.initializeMagicCircleImages();
  }
  
  // 更新魔法陣選擇項顯示
  updateCircleItems() {
    this.elements.circleTypeItems.forEach(item => {
      const type = item.dataset.type;
      const countElement = item.querySelector('span');
      
      // 更新數量顯示
      countElement.textContent = this.circleCounts[type];
      
      // 禁用沒有剩餘的魔法陣
      if (this.circleCounts[type] === 0) {
        item.classList.add('disabled');
      } else {
        item.classList.remove('disabled');
      }
    });
  }
  
  // 選擇魔法陣類型
  selectCircleType(item) {
    if (item.classList.contains('disabled')) return;
    
    // 移除其他項目的active狀態
    this.elements.circleTypeItems.forEach(i => i.classList.remove('active'));
    
    // 添加當前項目的active狀態
    item.classList.add('active');
    
    // 更新選擇的類型
    this.selectedCircleType = item.dataset.type;
    
    // 更新魔法陣圖片
    this.updateMagicCircleDisplay();
  }
  
  // 初始化魔法陣背景圖片
  initializeMagicCircleImages() {
    this.updateMagicCircleDisplay();
  }
  
  // 更新魔法陣顯示
  updateMagicCircleDisplay() {
    const basePath = '/static/img/circles/';
    const circleImagePath = `${basePath}${this.selectedCircleType}/magic-circle.png`;
    const circleInnerImagePath = `${basePath}${this.selectedCircleType}/magic-circle-inner.png`;
    
    this.elements.magicCircle.style.backgroundImage = `url("${circleImagePath}")`;
    this.elements.magicCircleInner.style.backgroundImage = `url("${circleInnerImagePath}")`;
    this.elements.magicCircle.className = 'magic-circle ' + this.selectedCircleType;
    this.elements.magicCircleInner.className = 'magic-circle-inner ' + this.selectedCircleType;
  }
  
  // 更新背包中的魔法陣數量
  async updateBackpackItem(itemType, newQuantity) {
    try {
      const currentQuantity = this.circleCounts[itemType];
      const countChange = newQuantity - currentQuantity;
      
      console.log(`準備更新背包: ${itemType}, 當前:${currentQuantity}, 新:${newQuantity}, 變化:${countChange}`);
      
      const response = await fetch('/game/api/user/backpack/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken()
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          item_name: itemType,
          count_change: countChange
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('背包更新API響應:', data);
        if (data.success) {
          console.log(`已更新 ${itemType} 數量為 ${newQuantity}`);
          return true;
        } else {
          console.error('背包更新失敗:', data.message);
          return false;
        }
      }
      console.error('更新背包數據失敗:', response.status);
      return false;
    } catch (error) {
      console.error('更新背包數據時出錯:', error);
      return false;
    }
  }
  
  // 重置捕捉界面狀態
  resetCaptureInterface() {
    console.log('重置捕捉界面狀態');
    
    // 重置視覺元素
    this.elements.magicCircle.classList.remove('active');
    this.elements.magicCircleInner.classList.remove('active');
    this.elements.captureEffect.classList.remove('active');
    this.elements.resultMessage.classList.remove('visible', 'success', 'failure');
    this.elements.creatureImage.classList.remove('captured');
    
    // 隱藏魔法陣
    setTimeout(() => {
      this.elements.magicCircle.style.display = 'none';
      this.elements.magicCircleInner.style.display = 'none';
    }, 1000);
    
    // 重新啟用按鈕
    this.elements.captureBtn.disabled = false;
    this.elements.cancelBtn.disabled = false;
    this.captureInProgress = false;
    
    // 清除所有特效粒子
    document.querySelectorAll('.magic-particle').forEach(p => p.remove());
    document.querySelectorAll('.firework-particle').forEach(p => p.remove());
  }
  
  // 創建粒子效果
  createParticles() {
    const container = document.querySelector('.capture-container');
    
    for (let i = 0; i < 30; i++) {
      const particle = document.createElement('div');
      particle.className = 'magic-particle ' + this.selectedCircleType;
      
      // 隨機位置
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      
      particle.style.left = `${x}%`;
      particle.style.top = `${y}%`;
      
      // 添加動畫
      const delay = Math.random() * 5;
      const duration = 3 + Math.random() * 3;
      
      particle.style.animation = `
        fadeIn 0.5s ${delay}s forwards,
        float ${duration}s ${delay}s infinite alternate
      `;
      
      container.appendChild(particle);
    }
  }
  
  // 創建煙花效果
  createFireworks() {
    const container = document.querySelector('.capture-container');
    
    for (let i = 0; i < 50; i++) {
      const firework = document.createElement('div');
      firework.className = 'firework-particle';
      
      // 隨機顏色
      const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6', '#1abc9c'];
      const randomColor = colors[Math.floor(Math.random() * colors.length)];
      firework.style.backgroundColor = randomColor;
      firework.style.boxShadow = `0 0 8px ${randomColor}`;
      
      // 隨機位置(中心附近)
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const radius = 150;
      const angle = Math.random() * Math.PI * 2;
      
      const x = centerX + Math.cos(angle) * radius * Math.random();
      const y = centerY + Math.sin(angle) * radius * Math.random();
      
      firework.style.left = `${x}px`;
      firework.style.top = `${y}px`;
      
      // 隨機大小
      const size = 3 + Math.random() * 5;
      firework.style.width = `${size}px`;
      firework.style.height = `${size}px`;
      
      // 隨機飛行方向和距離
      const tx = (Math.random() - 0.5) * 200;
      const ty = (Math.random() - 0.5) * 200;
      const duration = 0.5 + Math.random() * 1.5;
      
      firework.style.animation = `
        fireworkFade ${duration}s forwards,
        fireworkMove ${duration}s forwards
      `;
      
      firework.style.setProperty('--tx', `${tx}px`);
      firework.style.setProperty('--ty', `${ty}px`);
      
      container.appendChild(firework);
      
      // 自動移除煙花粒子
      setTimeout(() => {
        firework.remove();
      }, duration * 1000);
    }
  }
    // 顯示捕捉結果模態框
  showCaptureResultModal(isSuccess = true) {
    const modal = new bootstrap.Modal(document.getElementById('captureResultModal'));
    
    if (!isSuccess) {
      // 設置失敗模態框樣式
      document.getElementById('resultModalHeader').className = 'modal-header bg-danger text-white';
      document.getElementById('resultModalTitle').textContent = '捕捉失敗';
      document.getElementById('resultText').textContent = '捕捉失敗！';
      document.getElementById('resultDescription').textContent = '很遺憾，這次沒有成功捕捉到精靈，請再試一次！';
      
      // 隱藏經驗值信息
      const experienceInfo = document.querySelector('.experience-gain-info');
      if (experienceInfo) {
        experienceInfo.style.display = 'none';
      }
    } else {
      // 設置成功模態框樣式
      document.getElementById('resultModalHeader').className = 'modal-header bg-success text-white';
      document.getElementById('resultModalTitle').textContent = '捕捉成功';
      
      // 顯示經驗值信息（如果有捕捉結果數據）
      if (window.lastCaptureResult && window.lastCaptureResult.creature) {
        const creature = window.lastCaptureResult.creature;
        const experienceInfo = document.querySelector('.experience-gain-info');
        const experienceDetails = document.getElementById('experienceDetails');
        
        if (experienceInfo && experienceDetails) {
          experienceInfo.style.display = 'block';
          experienceDetails.textContent = `獲得 20 經驗值！當前等級：${creature.level || 1} 級`;
        }
      }
    }
    
    modal.show();
    
    // 5秒後自動跳轉並顯示倒數計時
    this.startCountdown();
  }
    // 開始倒數計時
  startCountdown() {
    let countdown = 5;
    const countdownElement = document.getElementById('countdown');
    const countdownInterval = setInterval(() => {
      countdown--;
      if (countdownElement) {
        countdownElement.textContent = countdown;
      }
      if (countdown <= 0) {
        clearInterval(countdownInterval);        // 修改重定向邏輯：優先返回到用戶精靈頁面，展示新捕捉的精靈
        window.location.href = "/bylin/myelf";
      }
    }, 1000);
  }
  
  // 處理捕捉邏輯
  async handleCapture() {
    if (this.captureInProgress) return;
    
    // 檢查是否有足夠的魔法陣
    if (this.circleCounts[this.selectedCircleType] <= 0) {
      alert('沒有足夠的魔法陣！');
      return;
    }
    
    this.captureInProgress = true;
    this.elements.captureBtn.disabled = true;
    this.elements.cancelBtn.disabled = true;
    
    console.log(`開始捕捉，當前${this.selectedCircleType}魔法陣數量：${this.circleCounts[this.selectedCircleType]}`);
    
    try {
      // 消耗魔法陣並更新Firebase
      const currentQuantity = this.circleCounts[this.selectedCircleType];
      const newQuantity = currentQuantity - 1;
      
      // 更新Firebase
      const updateSuccess = await this.updateBackpackItem(this.selectedCircleType, newQuantity);
      if (!updateSuccess) {
        this.showNotification('更新背包數據失敗，請稍後再試！', 'error');
        this.resetCaptureInterface();
        return;
      }
      
      // Firebase更新成功後，更新本地數據
      this.circleCounts[this.selectedCircleType] = newQuantity;
      this.updateCircleItems();
      console.log(`魔法陣消耗成功，剩餘${this.selectedCircleType}魔法陣：${this.circleCounts[this.selectedCircleType]}`);
      
      // 執行捕捉動畫
      await this.performCaptureAnimation();
      
      // 模擬捕捉成功率
      const successRate = this.circleRates[this.selectedCircleType];
      const isSuccess = Math.random() < successRate;
      
      // 處理捕捉結果
      await this.handleCaptureResult(isSuccess);
      
    } catch (error) {
      console.error('捕捉過程出錯:', error);
      this.showNotification('捕捉過程中發生錯誤，請稍後再試！', 'error');
      this.resetCaptureInterface();
    }
  }
  
  // 執行捕捉動畫
  async performCaptureAnimation() {
    return new Promise((resolve) => {
      // 更新魔法陣圖片
      this.updateMagicCircleDisplay();
      
      // 顯示魔法陣並啟動視覺效果
      this.elements.magicCircle.style.display = 'block';
      this.elements.magicCircleInner.style.display = 'block';
      this.elements.magicCircle.classList.add('active');
      
      setTimeout(() => { 
        this.elements.magicCircleInner.classList.add('active'); 
      }, 500);
      
      setTimeout(() => { 
        this.elements.captureEffect.classList.add('active'); 
      }, 1000);
      
      // 創建粒子特效
      this.createParticles();
      
      // 動畫完成後resolve
      setTimeout(resolve, 3000);
    });
  }
  
  // 處理捕捉結果
  async handleCaptureResult(isSuccess) {
    if (isSuccess) {
      // 捕捉成功
      this.elements.resultMessage.textContent = '捕捉成功！';
      this.elements.resultMessage.classList.add('success', 'visible');
      this.elements.creatureImage.classList.add('captured');
      this.createFireworks();
        // 調用捕捉處理器
      if (typeof CaptureHandler !== 'undefined') {
        try {
          const creatureId = document.querySelector('[data-creature-id]')?.dataset.creatureId || 
                            window.creatureData?.id;
          
          if (creatureId) {
            const result = await CaptureHandler.captureCreature(creatureId);
            console.log('捕捉處理結果:', result);
            
            // 如果捕捉成功，更新成功消息以包含經驗值信息
            if (result.success && result.creature) {
              const experienceInfo = result.creature.experience !== undefined ? 
                ` 獲得 20 經驗值！當前等級：${result.creature.level || 1}` : '';
              this.elements.resultMessage.textContent = `捕捉成功！${experienceInfo}`;
              
              // 保存捕捉結果供後續使用
              window.lastCaptureResult = result;
            }
          }
        } catch (error) {
          console.error('捕捉處理器調用失敗:', error);
        }
      }
      
      // 顯示成功模態框
      setTimeout(() => {
        this.showCaptureResultModal(true);
      }, 2000);
      
    } else {
      // 捕捉失敗
      this.elements.resultMessage.textContent = '捕捉失敗！';
      this.elements.resultMessage.classList.add('failure', 'visible');
      
      // 顯示失敗模態框
      setTimeout(() => {
        this.showCaptureResultModal(false);
      }, 2000);
      
      // 重置界面
      setTimeout(() => {
        this.resetCaptureInterface();
      }, 3000);
    }
  }
  
  // 獲取魔法陣類型的中文名稱
  getCircleTypeName(type) {
    const names = {
      normal: '普通魔法陣',
      advanced: '進階魔法陣',
      premium: '高級魔法陣'
    };
    return names[type] || type;
  }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
  // 設置背景圖片
  const captureContainer = document.querySelector('.capture-container');
  if (captureContainer) {
    captureContainer.style.backgroundImage = 'url("/static/img/catch_background.jpg")';
  }
  
  // 初始化魔法陣隱藏
  const magicCircle = document.getElementById('magicCircle');
  const magicCircleInner = document.getElementById('magicCircleInner');
  if (magicCircle) magicCircle.style.display = 'none';
  if (magicCircleInner) magicCircleInner.style.display = 'none';
  
  // 從頁面獲取精靈數據
  const creatureElement = document.querySelector('[data-creature-id]');
  if (creatureElement) {
    window.creatureData = {
      id: creatureElement.dataset.creatureId,
      name: creatureElement.dataset.creatureName || '未知精靈'
    };
  }
  
  // 初始化捕捉互動類
  window.captureInteractive = new CaptureInteractive();
});

// 導出類以供其他模塊使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CaptureInteractive;
}
