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
  
  // 載入Firebase數據
  loadBackpackData();
  
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

// 從Firebase API載入背包數據
async function loadBackpackData() {
  console.log('🔄 正在從Firebase載入背包數據...');
  
  try {
    const response = await fetch('/bylin/api/backpack');
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || '載入失敗');
    }
    
    console.log('✅ Firebase數據載入成功:', data.backpack);
    
    // 更新全局數據，合併靜態元數據與Firebase數量數據
    userItemsData = {
      'magic-circle': itemMeta['magic-circle'].map(item => {
        const quantity = data.backpack['magic-circle'][item.key] || 0;
        return {
          ...item,
          quantity: quantity,
          usageCount: quantity // 兼容舊版本
        };
      }),
      'potion': itemMeta['potion'].map(item => {
        const quantity = data.backpack['potion'][item.key] || 0;
        return {
          ...item,
          quantity: quantity,
          usageCount: quantity // 兼容舊版本
        };
      })
    };
    
    console.log('🎮 合併後的用戶數據:', userItemsData);
    
    // 重新渲染包包內容
    refreshBagDisplay();
    
    // 更新狀態摘要
    updateBagStatusSummary();
    
  } catch (error) {
    console.error('❌ 載入Firebase數據失敗:', error);
    
    // 載入失敗時使用靜態數據
    userItemsData = {
      'magic-circle': itemMeta['magic-circle'].map(item => ({
        ...item,
        quantity: item.usageCount || 0
      })),
      'potion': itemMeta['potion'].map(item => ({
        ...item,
        quantity: item.usageCount || 0
      }))
    };
    
    // 顯示錯誤通知
    showNotification(`數據載入失敗: ${error.message}`, 'warning');
    
    // 仍然渲染包包（使用靜態數據）
    refreshBagDisplay();
  }
}

// 重新渲染包包顯示
function refreshBagDisplay() {
  console.log('🔄 更新包包顯示狀態...');
  
  // mybag頁面不需要重新渲染卡片，只需要更新數量顯示
  // 實際的卡片是靜態HTML，只需要更新數量和狀態
  
  updateBagStatusSummary();
  
  console.log('✅ 包包狀態更新完成');
}

// 更新狀態摘要
function updateBagStatusSummary() {
  if (!userItemsData) return;
  
  // 計算總數量
  const totalMagicCircles = userItemsData['magic-circle']?.reduce((sum, item) => sum + (item.quantity || 0), 0) || 0;
  const totalPotions = userItemsData['potion']?.reduce((sum, item) => sum + (item.quantity || 0), 0) || 0;
  const totalItems = totalMagicCircles + totalPotions;
  
  // 計算稀有道具數量
  const rareItems = [...(userItemsData['magic-circle'] || []), ...(userItemsData['potion'] || [])]
    .filter(item => (item.rarity === 'rare' || item.rarity === 'legendary') && (item.quantity || 0) > 0)
    .reduce((sum, item) => sum + (item.quantity || 0), 0);
  
  // 計算力量指數（簡單計算：普通道具1分，稀有2分，傳說3分）
  const powerLevel = [...(userItemsData['magic-circle'] || []), ...(userItemsData['potion'] || [])]
    .reduce((sum, item) => {
      const quantity = item.quantity || 0;
      const multiplier = item.rarity === 'legendary' ? 3 : item.rarity === 'rare' ? 2 : 1;
      return sum + (quantity * multiplier);
    }, 0);
  
  // 更新頁面上的數量顯示
  const elements = {
    'total-items-count': totalItems,
    'rare-items-count': rareItems,
    'power-level': powerLevel,
    'magic-circle-count': totalMagicCircles,
    'potion-count': totalPotions
  };
  
  Object.entries(elements).forEach(([id, value]) => {
    const element = document.getElementById(id);
    if (element) {
      // 添加動畫效果
      element.style.transform = 'scale(1.1)';
      element.textContent = value;
      setTimeout(() => {
        element.style.transform = 'scale(1)';
      }, 200);
    }
  });
  
  console.log(`📊 狀態更新: 總計 ${totalItems}個, 魔法陣 ${totalMagicCircles}個, 藥水 ${totalPotions}個, 稀有 ${rareItems}個, 力量 ${powerLevel}`);
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
