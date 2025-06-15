// 全局變量定義
let userItemsData = [];

// 優化版包包頁面的 JavaScript 代碼 - 多主題支援版本

// 包包物品元數據定義
const itemMeta = {
  "magic-circle": [    {
      name: "普通魔法陣",
      key: "normal",
      img: "/static/img/mybag/magic-circle-normal.png",
      rarity: "common",
      description: "基礎的魔法陣，可以用於簡單的召喚儀式",
      bonus: "捕捉率 +5%",
      dateAcquired: "2024-05-20",
      usageCount: 8,
      story: "在古老的魔法學院中，每位學徒都會學習繪製這種基礎魔法陣。雖然看似簡單，但它蕴含著最純粹的魔法力量。"
    },
    {
      name: "進階魔法陣",
      key: "advanced",
      img: "/static/img/mybag/magic-circle-advanced.png",
      rarity: "rare",
      description: "進階魔法陣，提供更強大的能量場域",
      bonus: "捕捉率 +15%",
      dateAcquired: "2024-06-01",
      usageCount: 3,
      story: "據說這種魔法陣的設計來源於古代精靈的智慧，每一個符文都蘊含著大自然的奧秘與力量。"
    },
    {
      name: "高級魔法陣",
      key: "premium",
      img: "/static/img/mybag/magic-circle-high.png",
      rarity: "legendary",
      description: "傳說中的魔法陣，具有強大的能量控制能力",
      bonus: "捕捉率 +25%",
      dateAcquired: "2024-06-10",
      usageCount: 1,
      story: "這是失落文明留下的神秘魔法陣，據說能夠連接不同的次元空間，只有最勇敢的冒險者才能駕馭它的力量。"
    }
  ],
  "potion": [    {
      name: "普通藥水",
      key: "normal",
      img: "/static/img/mybag/potion-normal.png",
      rarity: "common",
      description: "普通的捕捉藥水，輕微提升捕捉能力",
      bonus: "捕捉率 1.13 倍",
      dateAcquired: "2024-05-15",
      usageCount: 12,
      story: "這是旅行商人最常販售的藥水，由常見的草藥調配而成。雖然效果溫和，但對新手冒險者來說非常實用。"
    },
    {
      name: "進階藥水",
      key: "advanced",
      img: "/static/img/mybag/potion-advanced.png",
      rarity: "rare",
      description: "進階捕捉藥水，顯著提升捕捉能力",
      bonus: "捕捉率 1.25 倍",
      dateAcquired: "2024-05-28",
      usageCount: 5,
      story: "由宮廷煉金術師精心調配的藥水，添加了稀有的月光花精華，在月圓之夜製作效果最佳。"
    },
    {
      name: "高級藥水",
      key: "premium",
      img: "/static/img/mybag/potion-high.png",
      rarity: "legendary",
      description: "傳說中的捕捉藥水，大幅提升捕捉能力",
      bonus: "捕捉率 1.50 倍",
      dateAcquired: "2024-06-08",
      usageCount: 2,
      story: "傳說中由龍族賢者親自調配的神秘藥水，融合了星辰之露和鳳凰之淚，擁有不可思議的神奇力量。"
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
  
  // 返回主選單按鈕事件
  const backToMainBtn = document.getElementById('back-to-main-btn');
  if (backToMainBtn) {
    backToMainBtn.addEventListener('click', function() {
      const detailContainer = document.getElementById('item-detail-container');
      if (detailContainer) {
        detailContainer.style.display = 'none';
        detailContainer.classList.remove('fade-slide');
        
        // 滾動回道具選擇區域
        const itemSelectionSection = document.querySelector('.item-selection-section');
        if (itemSelectionSection) {
          itemSelectionSection.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
        }
      }
      showNotification('已返回道具選擇頁面', 'info');
    });
  }
}

// 處理道具卡片點擊
function handleItemCardClick() {
  const itemType = this.getAttribute('data-type');
  const itemCategory = itemType === 'magic-circle' ? '魔法陣' : '神奇藥水';
  
  // 顯示載入通知
  showNotification(`正在跳轉到${itemCategory}詳情頁面...`, 'info');
    // 跳轉到對應的詳情頁面
  if (itemType === 'magic-circle') {
    window.location.href = '/bylin/magic-circle-details';
  } else if (itemType === 'potion') {
    window.location.href = '/bylin/potion-details';
  }
}

// 載入道具詳情
function loadItemDetails(itemType) {
  console.log(`📦 載入 ${itemType} 道具詳情`);
  
  const detailRow = document.getElementById('item-detail-row');
  if (!detailRow) return;

  // 清空現有的道具列表，確保每次只顯示當前選擇的分類
  detailRow.innerHTML = ''; 
  
  const items = itemMeta[itemType] || [];
  
  if (items.length === 0) {
    // 如果該分類下沒有道具，顯示空狀態提示
    // 可以檢查 detailRow 內是否已經有 .empty-state 元素，或者動態創建
    const existingEmptyState = detailRow.querySelector('.empty-state');
    if (existingEmptyState) {
      existingEmptyState.style.display = 'block';
    } else {
      // 如果 HTML 結構中沒有預設的 .empty-state 結構在 #item-detail-row 內，
      // 則可能需要動態創建或確保 mybag.html 中 #item-detail-row 包含一個可顯示的 .empty-state div
      detailRow.innerHTML = '<div class="col-12 empty-state" style="display: block;"><div class="empty-state-content"><i class="fas fa-search fa-3x"></i><h4>沒有找到符合的道具</h4><p>請嘗試其他分類或稍後再試</p></div></div>';
    }
    return;
  }
  
  // 如果有道具，確保空狀態是隱藏的
  const emptyStateInRow = detailRow.querySelector('.empty-state');
  if (emptyStateInRow) {
    emptyStateInRow.style.display = 'none';
  }
  
  items.forEach((item, index) => {
    const itemCol = document.createElement('div');
    // 使用之前確認過的響應式 class
    itemCol.className = 'col-lg-4 col-md-6 col-sm-12 mb-4 item-detail-col magic-circle-display-card'; 
    itemCol.setAttribute('data-rarity', item.rarity);
    itemCol.setAttribute('data-date', item.dateAcquired);
    itemCol.setAttribute('data-name', item.name.toLowerCase());
    
    const rarityColors = {
      common: 'var(--rarity-common)',
      rare: 'var(--rarity-rare)',
      legendary: 'var(--rarity-legendary)'
    };
    const rarityText = {
      common: '普通',
      rare: '稀有',
      legendary: '傳說'
    };
    
    let actionsHTML = '';
    // 魔法陣只有詳情按鈕
    if (itemType === 'magic-circle') {
      actionsHTML = `
          <button class="action-btn info-btn" data-item-index="${index}" data-item-type="${itemType}">
            <i class="fas fa-info-circle"></i> 詳情
          </button>
      `;
    } else if (itemType === 'potion') { // 藥水有使用和詳情按鈕
        actionsHTML = `
            <button class="action-btn use-btn">
              <i class="fas fa-magic"></i> 使用
            </button>
            <button class="action-btn info-btn" data-item-index="${index}" data-item-type="${itemType}">
              <i class="fas fa-info-circle"></i> 詳情
            </button>
        `;
    }

    itemCol.innerHTML = `
      <div class="item-detail-card" data-key="${item.key}"> {/* 移除 magic-circle-display-card，因為已加在 itemCol 上 */}
        <div class="rarity-badge" style="background: ${rarityColors[item.rarity] || 'var(--rarity-common)'}">
          ${rarityText[item.rarity] || '普通'}
        </div>
        <div class="item-detail-image">
          {/* 確保圖片有 class，例如 magic-circle-image，以便 CSS 控制 */}
          <img src="${item.img}" alt="${item.name}" class="magic-circle-image"> 
          <div class="item-detail-glow" style="background: radial-gradient(circle at center, ${rarityColors[item.rarity] || 'var(--rarity-common)'}80, transparent 70%);"></div>
        </div>
        <div class="item-detail-info">
          {/* 確保名稱有 class，例如 magic-circle-name */}
          <h4 class="magic-circle-name">${item.name}</h4> 
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
            ${actionsHTML}
          </div>
        </div>
      </div>
    `;
    
    detailRow.appendChild(itemCol);
    
    // 卡片出現動畫
    setTimeout(() => {
      itemCol.style.animation = `fadeSlideIn 0.5s ease-out ${index * 0.1}s forwards`;
    }, 50);
  });
  
  // 為新生成的詳情按鈕添加事件監聽
  const infoButtons = detailRow.querySelectorAll('.info-btn');
  infoButtons.forEach(button => {
    button.addEventListener('click', showItemDetailModal);
  });
  
  // 為新生成的使用按鈕添加事件監聽 (如果有的話)
  const useButtons = detailRow.querySelectorAll('.use-btn');
  useButtons.forEach(button => {
    button.addEventListener('click', function() {
      const itemCardElement = this.closest('.item-detail-card');
      if (itemCardElement) {
        const itemNameElement = itemCardElement.querySelector('h4'); // 或者更精確的 selector
        if (itemNameElement) {
            const itemName = itemNameElement.textContent;
            showNotification(`已選擇使用 ${itemName}`, 'success');
            console.log(`🔮 使用道具: ${itemName}`);
            // 可以在這裡添加實際使用道具的邏輯，例如更新 usageCount
        }
      }
    });
  });
}

// 新增一個函數，可以直接用數據來顯示模態框
function showItemDetailModalWithData(item, itemType, itemIndex) {
  if (!item) return;

  const modalBody = document.getElementById('modal-body');
  if (modalBody) {
    // 根據 itemType 決定是否顯示模態框中的 "使用道具" 按鈕
    let modalActionsHTML = '';
    if (itemType === 'potion') { // 只在藥水時顯示使用按鈕
        modalActionsHTML = `
        <div class="modal-item-actions">
            <button class="modal-action-btn modal-use-btn">
            <i class="fas fa-magic"></i> 使用道具
            </button>
        </div>
        `;
    }

    // 準備故事內容（稍後補上）
    const storyContent = item.story || '神秘的故事等待被發現...';

    modalBody.innerHTML = `
      <div class="simplified-modal-content" style="background-image: url('${item.img}')">
        <div class="modal-overlay">
          <div class="modal-title">
            <h2>${item.name}</h2>
          </div>
          
          <div class="modal-function">
            <h3><i class="fas fa-magic"></i> 功能效果</h3>
            <p>${item.bonus}</p>
          </div>
          
          <div class="modal-story">
            <h3><i class="fas fa-book"></i> 道具故事</h3>
            <p>${storyContent}</p>
          </div>
          
          <div class="modal-quantity">
            <h3><i class="fas fa-box"></i> 剩餘數量</h3>
            <p class="quantity-number">${item.usageCount || 1} 個</p>
          </div>
          
          ${modalActionsHTML}
        </div>
      </div>
    `;
    
    // 為模態框中的使用按鈕添加事件監聽 (如果存在)
    const modalUseBtn = modalBody.querySelector('.modal-use-btn');
    if (modalUseBtn) {
      modalUseBtn.addEventListener('click', function() {
        showNotification(`已選擇使用 ${item.name}`, 'success');
        closeItemDetailModal();
        console.log(`🔮 使用道具: ${item.name}`);
      });
    }
  }
  const modal = document.getElementById('item-detail-modal');
  if (modal) {
    // 顯示載入提示
    showNotification('正在載入道具詳情...', 'info');
    
    // 先滾動到頂部，確保用戶能看到提示框
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
    
    // 延遲一點時間後顯示模態框，讓滾動動畫有時間完成
    setTimeout(() => {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }, 300);
  }
}

// 替代方案：根據點擊位置動態調整模態框位置
function showItemDetailModalAtPosition(item, itemType, itemIndex, clickEvent) {
  if (!item) return;

  // 準備故事內容（稍後補上）
  const storyContent = item.story || '神秘的故事等待被發現...';
  
  // 根據 itemType 決定是否顯示模態框中的 "使用道具" 按鈕
  let modalActionsHTML = '';
  if (itemType === 'potion') {
    modalActionsHTML = `
      <div class="modal-item-actions">
          <button class="modal-action-btn modal-use-btn">
          <i class="fas fa-magic"></i> 使用道具
          </button>
      </div>
    `;
  }

  const modalBody = document.getElementById('modal-body');
  if (modalBody) {
    modalBody.innerHTML = `
      <div class="simplified-modal-content" style="background-image: url('${item.img}')">
        <div class="modal-overlay">
          <div class="modal-title">
            <h2>${item.name}</h2>
          </div>
          
          <div class="modal-function">
            <h3><i class="fas fa-magic"></i> 功能效果</h3>
            <p>${item.bonus}</p>
          </div>
          
          <div class="modal-story">
            <h3><i class="fas fa-book"></i> 道具故事</h3>
            <p>${storyContent}</p>
          </div>
          
          <div class="modal-quantity">
            <h3><i class="fas fa-box"></i> 剩餘數量</h3>
            <p class="quantity-number">${item.usageCount || 1} 個</p>
          </div>
          
          ${modalActionsHTML}
        </div>
      </div>
    `;
    
    // 為模態框中的使用按鈕添加事件監聽
    const modalUseBtn = modalBody.querySelector('.modal-use-btn');
    if (modalUseBtn) {
      modalUseBtn.addEventListener('click', function() {
        showNotification(`已選擇使用 ${item.name}`, 'success');
        closeItemDetailModal();
        console.log(`🔮 使用道具: ${item.name}`);
      });
    }
  }
  
  const modal = document.getElementById('item-detail-modal');
  if (modal) {
    // 如果有點擊事件，可以根據點擊位置調整顯示
    if (clickEvent) {
      const viewportHeight = window.innerHeight;
      const clickY = clickEvent.clientY;
      
      // 如果點擊位置在視窗下半部，就滾動到頂部
      if (clickY > viewportHeight * 0.6) {
        showNotification('正在載入道具詳情...', 'info');
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
        
        setTimeout(() => {
          modal.classList.add('active');
          document.body.style.overflow = 'hidden';
        }, 300);
      } else {
        // 如果點擊位置在上半部，直接顯示
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    } else {
      // 預設行為：滾動到頂部
      showNotification('正在載入道具詳情...', 'info');
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
      
      setTimeout(() => {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }, 300);
    }
  }
}

// 顯示道具詳情模態框 (原來的函數，由道具卡片上的詳情按鈕觸發)
function showItemDetailModal(e) {
  if (e) e.stopPropagation(); // 確保事件對象存在
  
  const itemIndex = this.getAttribute('data-item-index');
  const itemType = this.getAttribute('data-item-type');
  
  const item = itemMeta[itemType][itemIndex];
  if (!item) return;
  
  // 直接調用新的帶數據的模態框顯示函數
  showItemDetailModalWithData(item, itemType, itemIndex);
}

// 關閉道具詳情模態框
function closeItemDetailModal() {
  const modal = document.getElementById('item-detail-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = ''; // 恢復背景滾動
    
    // 可選：關閉模態框後滾動回到道具列表區域
    // 如果用戶正在查看道具列表，滾動回去讓他們繼續瀏覽
    const detailContainer = document.getElementById('item-detail-container');
    if (detailContainer && detailContainer.style.display !== 'none') {
      setTimeout(() => {
        detailContainer.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);
    }
  }
}

// 載入簡化的道具列表
function loadSimplifiedItemList(itemType) {
  console.log(`📦 載入簡化的 ${itemType} 道具列表`);
  
  const detailRow = document.getElementById('item-detail-row');
  if (!detailRow) return;

  // 清空現有內容
  detailRow.innerHTML = ''; 
  
  const items = itemMeta[itemType] || [];
  
  if (items.length === 0) {
    detailRow.innerHTML = `
      <div class="col-12 empty-state" style="display: block;">
        <div class="empty-state-content">
          <i class="fas fa-search fa-3x"></i>
          <h4>此分類下暫無道具</h4>
          <p>請嘗試其他分類或稍後再試</p>
        </div>
      </div>
    `;
    return;
  }
  
  items.forEach((item, index) => {
    const itemCol = document.createElement('div');
    itemCol.className = 'col-lg-3 col-md-4 col-sm-6 col-12 mb-3';
    
    const rarityColors = {
      common: '#78909c',
      rare: '#29b6f6', 
      legendary: '#ffb74d'
    };
    
    const rarityText = {
      common: '普通',
      rare: '稀有',
      legendary: '傳說'
    };
    
    itemCol.innerHTML = `
      <div class="simplified-item-card" data-item-index="${index}" data-item-type="${itemType}">
        <div class="item-header">
          <span class="item-name">${item.name}</span>
          <span class="item-rarity" style="color: ${rarityColors[item.rarity]}">${rarityText[item.rarity]}</span>
        </div>
        <div class="item-count">
          <i class="fas fa-box"></i>
          <span>剩餘: ${item.usageCount || 1}個</span>
        </div>
        <div class="item-bonus">
          ${item.bonus}
        </div>
      </div>
    `;
      // 添加點擊事件，點擊時顯示詳細資訊
    const card = itemCol.querySelector('.simplified-item-card');
    card.addEventListener('click', function(event) {
      // 使用新的動態定位函數
      showItemDetailModalAtPosition(item, itemType, index, event);
    });
    
    detailRow.appendChild(itemCol);
  });
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
  // 初始化 userItemsData 
  userItemsData = [];
  
  // 將 itemMeta 轉換為 userItemsData 格式
  Object.keys(itemMeta).forEach(type => {
    const items = itemMeta[type];
    items.forEach(item => {
      userItemsData.push({
        ...item,
        itemType: type
      });
    });
  });
  
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
//       if (item.rarity === 'common') {
//         powerLevel += 10;
//       } else if (item.rarity === 'rare') {
//         powerLevel += 50;
//       } else if (item.rarity === 'legendary') {
//         powerLevel += 100;
//       }
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

// 初始化提示顯示 - 更新為簡化版本
function initTips() {
  console.log('💡 初始化簡化提示顯示');
  
  // 延遲一點執行，確保數據已初始化
  setTimeout(() => {
    updateCompactSummary();
  }, 100);
}

// 更新簡化摘要
function updateCompactSummary() {
  const magicCircleCountElem = document.getElementById('magic-circle-count');
  const potionCountElem = document.getElementById('potion-count');
  
  if (magicCircleCountElem && potionCountElem) {
    // 計算各類道具數量
    const magicCircleCount = userItemsData.filter(item => 
      item.itemType === 'magic-circle'
    ).length;
    
    const potionCount = userItemsData.filter(item => 
      item.itemType === 'potion'
    ).length;
    
    magicCircleCountElem.textContent = magicCircleCount;
    potionCountElem.textContent = potionCount;
    
    console.log(`📊 更新簡化摘要: 魔法陣 ${magicCircleCount}個, 藥水 ${potionCount}個`);
  }
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
