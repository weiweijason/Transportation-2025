/**
 * 精靈捕捉互動頁面主要邏輯
 * 處理魔法陣選擇、背包數據載入、捕捉動畫等功能
 */

class CaptureInteractive {  constructor() {
    this.circleCounts = {
      normal: 0,
      advanced: 0,
      premium: 0
    };
    
    // 新的機率計算系統：基於精靈稀有度和魔法陣類型
    this.circleRatesByRarity = {
      premium: { // 高級魔法陣
        'SSR': 0.5,
        'SR': 0.8, 
        'R': 1.0,
        'N': 1.0
      },
      advanced: { // 進階魔法陣
        'SSR': 0.25,
        'SR': 0.5,
        'R': 0.8,
        'N': 1.0
      },
      normal: { // 普通魔法陣
        'SSR': 0.0,
        'SR': 0.25,
        'R': 0.5,
        'N': 0.8
      }
    };
    
    this.selectedCircleType = 'premium';
    this.captureInProgress = false;
    this.playerAddition = 1.0; // 玩家精靈加成，默認無加成
    this.creatureRarity = 'N'; // 當前精靈稀有度，默認為N
      this.initializeElements();
    this.bindEvents();
    this.extractCreatureRarity(); // 先提取精靈稀有度
    
    // 異步加載數據
    this.initializeData();
  }
  
  // 初始化所有數據
  async initializeData() {
    try {
      // 並行加載背包數據和玩家加成
      await Promise.all([
        this.loadUserBackpack(),
        this.loadPlayerAddition()
      ]);
      
      // 所有數據載入完成後，更新界面
      this.updateCircleItems();
      this.setDefaultSelectedCircle();
      
    } catch (error) {
      console.error('初始化數據失敗:', error);
      this.setDefaultValues();
    }
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
    // 從頁面提取精靈稀有度信息
  extractCreatureRarity() {
    try {
      // 優先從 window.creatureData 獲取
      if (window.creatureData && window.creatureData.rarity) {
        this.creatureRarity = window.creatureData.rarity;
        console.log('從 window.creatureData 提取到精靈稀有度:', this.creatureRarity);
        return;
      }
      
      // 從容器的 data 屬性獲取
      const creatureContainer = document.querySelector('[data-creature-id]');
      if (creatureContainer && creatureContainer.dataset.creatureRarity) {
        this.creatureRarity = creatureContainer.dataset.creatureRarity;
        console.log('從容器提取到精靈稀有度:', this.creatureRarity);
        return;
      }
      
      // 從頁面上的稀有度標籤獲取
      const rarityElement = document.querySelector('.rarity-badge');
      if (rarityElement) {
        this.creatureRarity = rarityElement.textContent.trim() || 'N';
        console.log('從稀有度標籤提取到精靈稀有度:', this.creatureRarity);
        return;
      }
      
      // 默認稀有度
      this.creatureRarity = 'N';
      console.log('使用默認精靈稀有度: N');
      
    } catch (error) {
      console.error('提取精靈稀有度失敗:', error);
      this.creatureRarity = 'N';
    }
  }
  
  // 從Firebase讀取玩家精靈加成狀態
  async loadPlayerAddition() {
    try {
      console.log('開始載入玩家精靈加成狀態...');
      
      const response = await fetch('/game/api/user/addition', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken()
        },
        credentials: 'same-origin'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.addition) {
          this.playerAddition = parseFloat(data.addition) || 1.0;
          console.log('成功載入玩家精靈加成:', this.playerAddition);
          this.showNotification(`精靈加成已啟用：${((this.playerAddition - 1) * 100).toFixed(0)}%`, 'success');
        } else {
          this.playerAddition = 1.0;
          console.log('玩家無精靈加成狀態');
        }
      } else {
        console.warn('無法獲取玩家精靈加成狀態，使用默認值');
        this.playerAddition = 1.0;
      }
    } catch (error) {
      console.error('載入玩家精靈加成狀態失敗:', error);
      this.playerAddition = 1.0;
    }
  }
  
  // 計算當前選擇魔法陣對特定稀有度精靈的捕捉成功率
  calculateCaptureRate(circleType = null, rarity = null) {
    const selectedCircle = circleType || this.selectedCircleType;
    const targetRarity = rarity || this.creatureRarity;
    
    // 基礎捕捉率（基於魔法陣類型和精靈稀有度）
    const baseRate = this.circleRatesByRarity[selectedCircle]?.[targetRarity] || 0;
    
    // 應用玩家精靈加成
    const finalRate = Math.min(baseRate * this.playerAddition, 1.0); // 最大成功率為100%
    
    console.log(`捕捉率計算: ${selectedCircle}魔法陣 + ${targetRarity}稀有度 = ${baseRate} * ${this.playerAddition}加成 = ${finalRate}`);
    
    return finalRate;
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
    this.playerAddition = 1.0;
    
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
    
    // 選擇有庫存且能夠捕捉當前精靈的魔法陣
    for (const type of priority) {
      const hasStock = this.circleCounts[type] > 0;
      const canCapture = this.calculateCaptureRate(type, this.creatureRarity) > 0;
      
      if (hasStock && canCapture) {
        defaultType = type;
        break;
      }
    }
    
    // 如果沒有合適的魔法陣，仍然選擇最高級的可用魔法陣
    if (defaultType === 'normal') {
      for (const type of priority) {
        if (this.circleCounts[type] > 0) {
          defaultType = type;
          break;
        }
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
    
    console.log(`默認選中魔法陣: ${defaultType}, 成功率: ${(this.calculateCaptureRate() * 100).toFixed(1)}%`);
  }
    // 更新魔法陣選擇項顯示
  updateCircleItems() {
    this.elements.circleTypeItems.forEach(item => {
      const type = item.dataset.type;
      const countElement = item.querySelector('span');
      const rateElement = item.querySelector('.circle-rate');
      
      // 更新數量顯示
      countElement.textContent = this.circleCounts[type];
      
      // 更新成功率顯示（基於當前精靈稀有度）
      if (rateElement) {
        const captureRate = this.calculateCaptureRate(type, this.creatureRarity);
        const percentage = Math.round(captureRate * 100);
        rateElement.textContent = `成功率：${percentage}%`;
        
        // 如果成功率為0，顯示特殊樣式
        if (captureRate === 0) {
          rateElement.style.color = '#e74c3c';
          rateElement.textContent = `成功率：0%（無法捕捉${this.creatureRarity}級精靈）`;
        } else {
          rateElement.style.color = '';
        }
      }
      
      // 禁用沒有剩餘的魔法陣或無法捕捉的魔法陣
      const captureRate = this.calculateCaptureRate(type, this.creatureRarity);
      if (this.circleCounts[type] === 0 || captureRate === 0) {
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
          // 使用捕捉結果中的等級，或者使用窗口中的用戶數據，或者默認為1
          const userLevel = creature.level || (window.userData ? window.userData.level : 1);
          experienceDetails.textContent = `獲得 20 經驗值！當前等級：${userLevel} 級`;
        }
      } else if (window.userData) {
        // 如果沒有捕捉結果，但有用戶數據，也顯示經驗值信息        const experienceInfo = document.querySelector('.experience-gain-info');
        
        if (experienceInfo) {
          experienceInfo.style.display = 'block';
          // 使用最新的用戶等級，優先從捕捉結果中獲取
          let userLevel = 1;
          let experienceGained = 20;
          
          if (window.lastCaptureResult && window.lastCaptureResult.user_level_info) {
            userLevel = window.lastCaptureResult.user_level_info.new_level;
            experienceGained = window.lastCaptureResult.user_level_info.experience_gained || 20;
          } else if (window.userData && window.userData.level) {
            userLevel = window.userData.level;
          }
          
          // 使用全局的更新函數（如果存在）
          if (typeof window.updateExperienceDisplay === 'function') {
            window.updateExperienceDisplay(userLevel, experienceGained);
          } else {
            // 備用方法：直接更新
            const experienceDetails = document.getElementById('experienceDetails');
            if (experienceDetails) {
              experienceDetails.textContent = `獲得 ${experienceGained} 經驗值！當前等級：${userLevel} 級`;
            }
          }
          console.log(`經驗值提示更新: ${experienceGained} 經驗值, 當前等級: ${userLevel}`);
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
      }      if (countdown <= 0) {
        clearInterval(countdownInterval);
        // 修改重定向邏輯：返回到遊戲地圖頁面
        window.location.href = "/game/catch";
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
    
    // 檢查當前魔法陣是否能捕捉該稀有度的精靈
    const captureRate = this.calculateCaptureRate();
    if (captureRate === 0) {
      alert(`${this.getCircleTypeName(this.selectedCircleType)}無法捕捉${this.creatureRarity}級精靈！請使用更高級的魔法陣。`);
      return;
    }
    
    this.captureInProgress = true;
    this.elements.captureBtn.disabled = true;
    this.elements.cancelBtn.disabled = true;
    
    console.log(`開始捕捉，當前${this.selectedCircleType}魔法陣數量：${this.circleCounts[this.selectedCircleType]}`);
    console.log(`精靈稀有度：${this.creatureRarity}，計算成功率：${(captureRate * 100).toFixed(1)}%`);
    
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
      
      // 使用新的機率計算系統進行捕捉判定
      const isSuccess = Math.random() < captureRate;
      console.log(`捕捉判定：隨機數 < ${captureRate} = ${isSuccess ? '成功' : '失敗'}`);
      
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
              // 優先使用後端返回的用戶等級信息
              let userLevel = 1; // 默認等級
              let experienceGained = 20; // 默認經驗值
                // 檢查是否有用戶等級更新信息
              if (result.user_level_info && result.user_level_info.new_level) {
                userLevel = result.user_level_info.new_level;
                experienceGained = result.user_level_info.experience_gained || 20;
                console.log('使用後端返回的用戶等級信息:', result.user_level_info);
                
                // 更新全局用戶數據
                if (window.userData) {
                  window.userData.level = userLevel;
                  window.userData.experience = result.user_level_info.current_experience || 0;
                }
                
                // 立即更新經驗值顯示（如果函數存在）
                if (typeof window.updateExperienceDisplay === 'function') {
                  window.updateExperienceDisplay(userLevel, experienceGained);
                }
              } else if (result.creature.level) {
                // 備選：使用精靈數據中的等級（如果有的話）
                userLevel = result.creature.level;
              } else if (window.userData && window.userData.level) {
                // 最後備選：使用窗口中的用戶數據
                userLevel = window.userData.level;
              }
              
              const experienceInfo = ` 獲得 ${experienceGained} 經驗值！當前等級：${userLevel} 級`;
              this.elements.resultMessage.textContent = `捕捉成功！${experienceInfo}`;
              
              console.log(`更新等級顯示: ${userLevel} 級, 獲得經驗值: ${experienceGained}`);
              
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
      name: creatureElement.dataset.creatureName || '未知精靈',
      rarity: creatureElement.dataset.creatureRarity || 'N'
    };
  }
  
  // 初始化捕捉互動類
  window.captureInteractive = new CaptureInteractive();
});

// 導出類以供其他模塊使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CaptureInteractive;
}
