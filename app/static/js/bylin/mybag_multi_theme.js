// 優化版包包頁面的 JavaScript 代碼 - 多主題支援版本

// 包包物品元數據定義
const itemMeta = {
  "magic-circle": [
    {
      name: "普通魔法陣",
      key: "normal",
      img: "/static/img/mybag/magic-circle-normal.png",
      rarity: "common",
      description: "基礎的魔法陣，可以用於簡單的召喚儀式",
      bonus: "捕捉率 +5%",
      dateAcquired: "2024-05-20",
      usageCount: 8
    },
    {
      name: "進階魔法陣",
      key: "advanced",
      img: "/static/img/mybag/magic-circle-advanced.png",
      rarity: "rare",
      description: "進階魔法陣，提供更強大的能量場域",
      bonus: "捕捉率 +15%",
      dateAcquired: "2024-06-01",
      usageCount: 3
    },
    {
      name: "高級魔法陣",
      key: "premium",
      img: "/static/img/mybag/magic-circle-high.png",
      rarity: "legendary",
      description: "傳說中的魔法陣，具有強大的能量控制能力",
      bonus: "捕捉率 +25%",
      dateAcquired: "2024-06-10",
      usageCount: 1
    }
  ],
  "potion": [
    {
      name: "普通藥水",
      key: "normal",
      img: "/static/img/mybag/potion-normal.png",
      rarity: "common",
      description: "普通的捕捉藥水，輕微提升捕捉能力",
      bonus: "捕捉率 1.13 倍",
      dateAcquired: "2024-05-15",
      usageCount: 12
    },
    {
      name: "進階藥水",
      key: "advanced",
      img: "/static/img/mybag/potion-advanced.png",
      rarity: "rare",
      description: "進階捕捉藥水，顯著提升捕捉能力",
      bonus: "捕捉率 1.25 倍",
      dateAcquired: "2024-05-28",
      usageCount: 5
    },
    {
      name: "高級藥水",
      key: "premium",
      img: "/static/img/mybag/potion-high.png",
      rarity: "legendary",
      description: "傳說中的捕捉藥水，大幅提升捕捉能力",
      bonus: "捕捉率 1.50 倍",
      dateAcquired: "2024-06-08",
      usageCount: 2
    }
  ]
};

// 當文檔加載完成時執行
document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 初始化包包頁面...');
  
  // 設置載入動畫
  document.body.classList.add('is-loading');
  
  // 設置背景
  document.body.classList.add('game-background');
  
  // 檢查並應用保存的主題
  applyUserThemePreference();
  
  // 添加主題切換按鈕
  addThemeToggleButton();
  
  // 延遲後隱藏載入動畫
  setTimeout(() => {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
      loadingOverlay.style.opacity = '0';
      loadingOverlay.style.visibility = 'hidden';
      document.body.classList.remove('is-loading');
    }
  }, 1500);
  
  // 初始化動畫效果
  initVisualEffects();
  
  // 初始化事件監聽
  initEventListeners();
  
  // 初始化包包狀態摘要
  initBagStatusSummary();
  
  // 初始化提示顯示
  initTips();
  
  // 初始化滾動行為
  initScrollBehavior();
  
  // 初始化行動裝置手勢
  initMobileGestures();
});

// 檢查並應用用戶主題偏好
function applyUserThemePreference() {
  // 檢查本地存儲的主題偏好
  const savedTheme = localStorage.getItem('bagThemePreference');
  
  if (savedTheme) {
    // 如果有保存的主題，應用它
    if (savedTheme === 'light') {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
  } else {
    // 如果沒有保存的主題，檢查系統偏好
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
  }
}

// 添加主題切換按鈕
function addThemeToggleButton() {
  const themeToggle = document.createElement('div');
  themeToggle.className = 'theme-toggle';
  themeToggle.innerHTML = document.body.classList.contains('light-theme') ? 
    '<i class="fas fa-moon"></i>' : 
    '<i class="fas fa-sun"></i>';
  
  themeToggle.addEventListener('click', function() {
    // 切換主題
    document.body.classList.toggle('light-theme');
    
    // 更新按鈕圖標
    this.innerHTML = document.body.classList.contains('light-theme') ? 
      '<i class="fas fa-moon"></i>' : 
      '<i class="fas fa-sun"></i>';
    
    // 保存用戶偏好
    localStorage.setItem(
      'bagThemePreference', 
      document.body.classList.contains('light-theme') ? 'light' : 'dark'
    );
    
    // 顯示通知
    const themeMode = document.body.classList.contains('light-theme') ? '明亮' : '暗黑';
    showNotification(`已切換至${themeMode}主題模式`, 'info');
  });
  
  document.body.appendChild(themeToggle);
}

// 初始化視覺效果
function initVisualEffects() {
  console.log('✨ 初始化視覺效果');
  
  // 創建魔法粒子效果
  createMagicParticles();
  
  // 啟動所有視覺動畫
  setTimeout(forceStartAllEffects, 1800);
}

// 創建魔法粒子效果
function createMagicParticles() {
  // 添加魔法粒子 CSS 動畫
  if (!document.querySelector('#magic-particles-style')) {
    const style = document.createElement('style');
    style.id = 'magic-particles-style';
    style.textContent = `
      @keyframes sparkleFloat {
        0% {
          transform: translateY(0) rotate(0deg);
          opacity: 1;
        }
        100% {
          transform: translateY(-100vh) rotate(360deg);
          opacity: 0;
        }
      }
      .magic-sparkle {
        animation: sparkleFloat linear infinite !important;
      }
    `;
    document.head.appendChild(style);
  }
  
  // 每隔一段時間創建一個粒子
  setInterval(() => {
    // 根據主題選擇不同的顏色
    const isLightTheme = document.body.classList.contains('light-theme');
    const colors = isLightTheme ? 
      ['#ff9800', '#e91e63', '#2196f3', '#4caf50', '#9c27b0'] : 
      ['#ffd700', '#ff7e5f', '#00e4ff', '#4ade80', '#a78bfa'];
    
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    
    const sparkle = document.createElement('div');
    sparkle.style.cssText = `
      position: fixed;
      width: 8px;
      height: 8px;
      background: ${randomColor};
      border-radius: 50%;
      pointer-events: none;
      z-index: 9998;
      left: ${Math.random() * 100}vw;
      top: 100vh;
      box-shadow: 0 0 15px ${randomColor}, 0 0 30px ${randomColor};
    `;
    
    sparkle.className = 'magic-sparkle';
    sparkle.style.animationDuration = (Math.random() * 3 + 2) + 's';
    document.body.appendChild(sparkle);
    
    setTimeout(() => {
      if (sparkle.parentNode) sparkle.remove();
    }, 5000);
  }, 400);
}

// 強制啟動所有視覺效果
function forceStartAllEffects() {
  console.log('🎨 強制啟動所有視覺效果');
  
  // 確保容器動畫
  const container = document.querySelector('.mybag-container');
  if (container) {
    container.style.opacity = '1';
    container.style.animation = 'containerFadeIn 1s ease-out';
  }
  
  // 確保標題動畫
  const header = document.querySelector('.mybag-header');
  if (header) {
    header.style.animation = 'headerSlideDown 0.8s ease-out 0.2s both';
  }
  
  // 確保卡片進場動畫
  const cards = document.querySelectorAll('.item-card');
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.style.animation = `cardSlideIn 0.6s ease-out ${index * 0.1}s both`;
    }, 100);
  });
  
  // 確保分隔線動畫
  const divider = document.querySelector('.section-divider');
  if (divider) {
    divider.style.animation = 'dividerGlow 2s ease-in-out infinite';
  }
  
  // 確保星星動畫
  const stars = document.querySelectorAll('.section-title i');
  stars.forEach(star => {
    star.style.animation = 'starTwinkle 2s ease-in-out infinite';
  });
}

// 初始化事件監聽
function initEventListeners() {
  console.log('👂 初始化事件監聽');
  
  // 道具卡片點擊事件
  const itemCards = document.querySelectorAll('.item-card');
  itemCards.forEach(card => {
    card.addEventListener('click', handleItemCardClick);
  });
  
  // 搜尋框事件
  const searchInput = document.getElementById('item-search');
  if (searchInput) {
    searchInput.addEventListener('input', handleSearch);
  }
  
  // 過濾按鈕事件
  const filterButtons = document.querySelectorAll('.filter-btn');
  filterButtons.forEach(button => {
    button.addEventListener('click', handleFilter);
  });
  
  // 滾動到頂部按鈕事件
  const scrollTopBtn = document.getElementById('scroll-top-btn');
  if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
  
  // 模態框關閉按鈕事件
  const modalClose = document.querySelector('.modal-close');
  if (modalClose) {
    modalClose.addEventListener('click', closeItemDetailModal);
  }
  
  // 點擊模態框外部區域關閉模態框
  const modal = document.getElementById('item-detail-modal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === this) {
        closeItemDetailModal();
      }
    });
  }
}

// 處理道具卡片點擊
function handleItemCardClick() {
  const itemType = this.getAttribute('data-type');
  const itemCategory = itemType === 'magic-circle' ? '魔法陣' : '神奇藥水';
  
  // 更新類別標題
  const categoryTitle = document.getElementById('category-title');
  if (categoryTitle) {
    categoryTitle.textContent = `${itemCategory}收藏`;
  }
  
  // 獲取道具詳情容器
  const detailContainer = document.getElementById('item-detail-container');
  const detailRow = document.getElementById('item-detail-row');
  
  // 清空詳情行
  if (detailRow) {
    detailRow.innerHTML = '';
  }
  
  // 顯示詳情容器
  if (detailContainer) {
    detailContainer.style.display = 'block';
    
    // 添加 CSS 類用於動畫
    detailContainer.classList.add('fade-slide');
    
    // 滾動到詳情區域
    setTimeout(() => {
      detailContainer.scrollIntoView({
        behavior: 'smooth', 
        block: 'start'
      });
    }, 100);
  }
  
  // 載入道具詳情
  loadItemDetails(itemType);
  
  // 顯示通知
  showNotification(`正在查看${itemCategory}收藏`, 'info');
}

// 載入道具詳情
function loadItemDetails(itemType) {
  console.log(`📦 載入 ${itemType} 道具詳情`);
  
  const detailRow = document.getElementById('item-detail-row');
  if (!detailRow) return;
  
  const items = itemMeta[itemType] || [];
  
  if (items.length === 0) {
    // 顯示空狀態
    const emptyState = document.querySelector('.empty-state');
    if (emptyState) {
      emptyState.style.display = 'block';
    }
    return;
  }
  
  // 隱藏空狀態
  const emptyState = document.querySelector('.empty-state');
  if (emptyState) {
    emptyState.style.display = 'none';
  }
  
  // 渲染每個道具
  items.forEach((item, index) => {
    // 建立道具卡片
    const itemCol = document.createElement('div');
    itemCol.className = 'col-lg-4 col-md-6 col-sm-12 mb-4 item-detail-col';
    itemCol.setAttribute('data-rarity', item.rarity);
    itemCol.setAttribute('data-date', item.dateAcquired);
    itemCol.setAttribute('data-name', item.name.toLowerCase());
    
    // 稀有度標誌的顏色
    const rarityColors = {
      common: 'var(--rarity-common)',
      rare: 'var(--rarity-rare)',
      legendary: 'var(--rarity-legendary)'
    };
    
    // 稀有度文字
    const rarityText = {
      common: '普通',
      rare: '稀有',
      legendary: '傳說'
    };
    
    // 卡片內容
    itemCol.innerHTML = `
      <div class="item-detail-card" data-key="${item.key}">
        <div class="rarity-badge" style="background: ${rarityColors[item.rarity] || 'var(--rarity-common)'}">
          ${rarityText[item.rarity] || '普通'}
        </div>
        <div class="item-detail-image">
          <img src="${item.img}" alt="${item.name}">
          <div class="item-detail-glow" style="background: radial-gradient(circle at center, ${rarityColors[item.rarity] || 'var(--rarity-common)'}80, transparent 70%);"></div>
        </div>
        <div class="item-detail-info">
          <h4>${item.name}</h4>
          <div class="item-detail-stats">
            <div class="stat-badge">
              <i class="fas fa-bolt"></i> ${item.bonus}
            </div>
            <div class="stat-badge">
              <i class="fas fa-history"></i> 已使用 ${item.usageCount} 次
            </div>
          </div>
          <p>${item.description}</p>
          <div class="item-detail-actions">
            <button class="action-btn use-btn">
              <i class="fas fa-magic"></i> 使用
            </button>
            <button class="action-btn info-btn" data-item-index="${index}" data-item-type="${itemType}">
              <i class="fas fa-info-circle"></i> 詳情
            </button>
          </div>
        </div>
      </div>
    `;
    
    // 添加到詳情行
    detailRow.appendChild(itemCol);
    
    // 延遲添加動畫效果
    setTimeout(() => {
      itemCol.style.animation = `fadeSlideIn 0.5s ease-out ${index * 0.1}s forwards`;
    }, 50);
  });
  
  // 為詳情按鈕添加事件監聽
  const infoButtons = document.querySelectorAll('.info-btn');
  infoButtons.forEach(button => {
    button.addEventListener('click', showItemDetailModal);
  });
  
  // 為使用按鈕添加事件監聽
  const useButtons = document.querySelectorAll('.use-btn');
  useButtons.forEach(button => {
    button.addEventListener('click', function() {
      const itemName = this.closest('.item-detail-card').querySelector('h4').textContent;
      showNotification(`已選擇使用 ${itemName}`, 'success');
      
      // 這裡可以添加實際使用道具的邏輯
      console.log(`🔮 使用道具: ${itemName}`);
    });
  });
}

// 顯示道具詳情模態框
function showItemDetailModal(e) {
  e.stopPropagation();
  
  const itemIndex = this.getAttribute('data-item-index');
  const itemType = this.getAttribute('data-item-type');
  
  const item = itemMeta[itemType][itemIndex];
  if (!item) return;
  
  // 稀有度標誌的顏色
  const rarityColors = {
    common: 'var(--rarity-common)',
    rare: 'var(--rarity-rare)',
    legendary: 'var(--rarity-legendary)'
  };
  
  // 稀有度文字
  const rarityText = {
    common: '普通',
    rare: '稀有',
    legendary: '傳說'
  };
  
  // 獲取模態框主體
  const modalBody = document.getElementById('modal-body');
  if (modalBody) {
    modalBody.innerHTML = `
      <div class="modal-item-header">
        <div class="modal-item-image">
          <img src="${item.img}" alt="${item.name}">
          <div class="modal-item-glow" style="background: radial-gradient(circle at center, ${rarityColors[item.rarity] || 'var(--rarity-common)'}80, transparent 70%);"></div>
        </div>
        <div class="modal-item-title">
          <h2>${item.name}</h2>
          <div class="modal-rarity-badge" style="background: ${rarityColors[item.rarity] || 'var(--rarity-common)'}">
            ${rarityText[item.rarity] || '普通'}
          </div>
        </div>
      </div>
      
      <div class="modal-item-description">
        <p>${item.description}</p>
      </div>
      
      <div class="modal-item-stats">
        <div class="modal-stat">
          <div class="modal-stat-icon">
            <i class="fas fa-bolt"></i>
          </div>
          <div class="modal-stat-info">
            <div class="modal-stat-label">能力加成</div>
            <div class="modal-stat-value">${item.bonus}</div>
          </div>
        </div>
        
        <div class="modal-stat">
          <div class="modal-stat-icon">
            <i class="fas fa-calendar-alt"></i>
          </div>
          <div class="modal-stat-info">
            <div class="modal-stat-label">獲得日期</div>
            <div class="modal-stat-value">${formatDate(item.dateAcquired)}</div>
          </div>
        </div>
        
        <div class="modal-stat">
          <div class="modal-stat-icon">
            <i class="fas fa-history"></i>
          </div>
          <div class="modal-stat-info">
            <div class="modal-stat-label">使用次數</div>
            <div class="modal-stat-value">${item.usageCount} 次</div>
          </div>
        </div>
      </div>
      
      <div class="modal-item-actions">
        <button class="modal-action-btn modal-use-btn">
          <i class="fas fa-magic"></i> 使用道具
        </button>
      </div>
    `;
    
    // 為模態框中的使用按鈕添加事件監聽
    const modalUseBtn = modalBody.querySelector('.modal-use-btn');
    if (modalUseBtn) {
      modalUseBtn.addEventListener('click', function() {
        showNotification(`已選擇使用 ${item.name}`, 'success');
        closeItemDetailModal();
        
        // 這裡可以添加實際使用道具的邏輯
        console.log(`🔮 使用道具: ${item.name}`);
      });
    }
  }
  
  // 顯示模態框
  const modal = document.getElementById('item-detail-modal');
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // 防止背景滾動
  }
}

// 關閉道具詳情模態框
function closeItemDetailModal() {
  const modal = document.getElementById('item-detail-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = ''; // 恢復背景滾動
  }
}

// 處理搜尋
function handleSearch() {
  const searchTerm = this.value.toLowerCase().trim();
  const detailItems = document.querySelectorAll('.item-detail-col');
  
  let hasResults = false;
  
  detailItems.forEach(item => {
    const itemName = item.getAttribute('data-name') || '';
    
    if (itemName.includes(searchTerm)) {
      item.style.display = '';
      hasResults = true;
    } else {
      item.style.display = 'none';
    }
  });
  
  // 顯示或隱藏空狀態
  const emptyState = document.querySelector('.empty-state');
  if (emptyState) {
    emptyState.style.display = hasResults ? 'none' : 'block';
  }
}

// 處理過濾
function handleFilter() {
  // 移除所有過濾按鈕的活躍狀態
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // 添加當前按鈕的活躍狀態
  this.classList.add('active');
  
  const filterType = this.getAttribute('data-filter');
  const detailItems = document.querySelectorAll('.item-detail-col');
  
  if (filterType === 'all') {
    // 顯示所有項目
    detailItems.forEach(item => {
      item.style.display = '';
    });
  } else if (filterType === 'rarity') {
    // 按稀有度排序（從高到低）
    const sortedItems = Array.from(detailItems).sort((a, b) => {
      const rarityA = a.getAttribute('data-rarity');
      const rarityB = b.getAttribute('data-rarity');
      
      const rarityOrder = {
        legendary: 3,
        rare: 2,
        common: 1
      };
      
      return rarityOrder[rarityB] - rarityOrder[rarityA];
    });
    
    // 重新排列項目
    const parent = detailItems[0].parentNode;
    sortedItems.forEach(item => {
      parent.appendChild(item);
    });
  } else if (filterType === 'recent') {
    // 按日期排序（從新到舊）
    const sortedItems = Array.from(detailItems).sort((a, b) => {
      const dateA = new Date(a.getAttribute('data-date'));
      const dateB = new Date(b.getAttribute('data-date'));
      
      return dateB - dateA;
    });
    
    // 重新排列項目
    const parent = detailItems[0].parentNode;
    sortedItems.forEach(item => {
      parent.appendChild(item);
    });
  }
  
  showNotification(`已應用 ${this.textContent.trim()} 過濾器`, 'info');
}

// 初始化包包狀態摘要
function initBagStatusSummary() {
  // 計算總道具數量
  let totalItems = 0;
  let rareItems = 0;
  let powerLevel = 0;
  
  // 計算所有類型的道具數量
  Object.keys(itemMeta).forEach(type => {
    const items = itemMeta[type];
    totalItems += items.length;
    
    // 計算稀有和傳說道具
    items.forEach(item => {
      if (item.rarity === 'rare' || item.rarity === 'legendary') {
        rareItems++;
      }
      
      // 計算力量指數（基於稀有度）
      if (item.rarity === 'common') {
        powerLevel += 10;
      } else if (item.rarity === 'rare') {
        powerLevel += 50;
      } else if (item.rarity === 'legendary') {
        powerLevel += 100;
      }
    });
  });
  
  // 更新摘要數據
  const totalItemsCount = document.getElementById('total-items-count');
  const rareItemsCount = document.getElementById('rare-items-count');
  const powerLevelElem = document.getElementById('power-level');
  
  if (totalItemsCount) totalItemsCount.textContent = totalItems;
  if (rareItemsCount) rareItemsCount.textContent = rareItems;
  if (powerLevelElem) powerLevelElem.textContent = powerLevel;
}

// 初始化提示顯示
function initTips() {
  console.log('💡 初始化提示顯示');
  
  // 延遲顯示交互式提示
  setTimeout(() => {
    const interactiveTips = document.getElementById('interactive-tips');
    if (interactiveTips) {
      interactiveTips.classList.add('visible');
      
      // 5秒後自動隱藏
      setTimeout(() => {
        interactiveTips.classList.remove('visible');
      }, 5000);
    }
  }, 3000);
}

// 初始化滾動行為
function initScrollBehavior() {
  console.log('📜 初始化滾動行為');
  
  // 監聽滾動事件，顯示/隱藏回到頂部按鈕
  window.addEventListener('scroll', () => {
    const scrollTopBtn = document.getElementById('scroll-top-btn');
    if (scrollTopBtn) {
      if (window.scrollY > 300) {
        scrollTopBtn.classList.add('visible');
      } else {
        scrollTopBtn.classList.remove('visible');
      }
    }
  });
}

// 初始化行動裝置手勢
function initMobileGestures() {
  console.log('👆 初始化行動裝置手勢');
  
  // 檢查 Hammer.js 是否可用
  if (typeof Hammer !== 'undefined') {
    // 為模態框添加滑動關閉手勢
    const modalContent = document.querySelector('.modal-content');
    if (modalContent) {
      const hammerModal = new Hammer(modalContent);
      hammerModal.get('swipe').set({ direction: Hammer.DIRECTION_DOWN });
      
      hammerModal.on('swipedown', function(e) {
        closeItemDetailModal();
      });
    }
    
    // 為道具卡片添加滑動手勢
    const itemCards = document.querySelectorAll('.item-card');
    itemCards.forEach(card => {
      const hammerCard = new Hammer(card);
      
      hammerCard.on('tap', function(e) {
        card.click(); // 觸發點擊事件
      });
    });
  }
}

// 顯示通知消息
function showNotification(message, type = 'info') {
  console.log(`📢 顯示通知: ${message} (${type})`);
  
  // 通知類型的圖標
  const icons = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  };
  
  // 通知類型的顏色 (適配主題)
  const isLightTheme = document.body.classList.contains('light-theme');
  const colors = {
    success: isLightTheme ? 'linear-gradient(45deg, #2e7d32, #4caf50)' : 'linear-gradient(45deg, #28a745, #20c997)',
    error: isLightTheme ? 'linear-gradient(45deg, #c62828, #f44336)' : 'linear-gradient(45deg, #dc3545, #fd7e14)',
    warning: isLightTheme ? 'linear-gradient(45deg, #ef6c00, #ff9800)' : 'linear-gradient(45deg, #ffc107, #fd7e14)',
    info: isLightTheme ? 'linear-gradient(45deg, #0277bd, #03a9f4)' : 'linear-gradient(45deg, #17a2b8, #6f42c1)'
  };
  
  // 創建通知元素
  const notification = document.createElement('div');
  notification.className = 'notification';
  notification.innerHTML = `
    <i class="${icons[type]}"></i>
    <span>${message}</span>
  `;
  
  // 設置通知樣式
  notification.style.cssText = `
    position: fixed;
    top: 30px;
    right: 30px;
    background: ${colors[type]};
    color: white;
    padding: 15px 25px;
    border-radius: 50px;
    box-shadow: 0 8px 25px var(--shadow-color);
    z-index: 10000;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    backdrop-filter: blur(10px);
    transform: translateX(400px);
    transition: transform 0.3s ease;
    border: 1px solid var(--border-color);
  `;
  
  // 添加到頁面
  document.body.appendChild(notification);
  
  // 滑入動畫
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);
  
  // 自動移除
  setTimeout(() => {
    notification.style.transform = 'translateX(400px)';
    
    // 完成滑出後移除元素
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 300);
  }, 3000);
}

// 格式化日期
function formatDate(dateString) {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}/${month}/${day}`;
}
