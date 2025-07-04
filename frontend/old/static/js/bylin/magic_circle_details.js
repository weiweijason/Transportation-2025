// 魔法陣詳情頁面的 JavaScript

// 魔法陣數據
const magicCircleData = [
  {
    name: "普通魔法陣",
    key: "normal",
    img: "/static/img/mybag/magic-circle-normal.png",
    rarity: "common",
    description: "基礎的魔法陣，可以用於簡單的召喚儀式",
    bonus: "捕捉率 +5%",
    dateAcquired: "2024-05-20",
    usageCount: 8,
    story: "在古老的魔法學院中，每位學徒都會學習繪製這種基礎魔法陣。雖然看似簡單，但它蘊含著最純粹的魔法力量。"
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
];

// 當文檔加載完成時執行
document.addEventListener('DOMContentLoaded', function() {
  console.log('🔮 初始化魔法陣詳情頁面...');
  
  // 強制確保主題設置
  const savedTheme = localStorage.getItem('user-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  console.log(`強制設置主題: ${savedTheme}`);
  
  // 初始化主題支持
  initThemeSupport();
  
  // 隱藏CSS測試元素
  const cssTest = document.getElementById('css-test');
  if (cssTest) {
    cssTest.style.display = 'none';
    console.log('CSS已正確載入');
  }
  
  // 設置載入動畫
  document.body.classList.add('is-loading');
  
  // 延遲後隱藏載入動畫
  setTimeout(() => {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
      loadingOverlay.style.opacity = '0';
      loadingOverlay.style.visibility = 'hidden';
      document.body.classList.remove('is-loading');
    }
  }, 1500);
  
  // 載入魔法陣數據
  loadMagicCircles();
  
  // 更新統計數據
  updateSummary();
  
  // 初始化滾動按鈕
  initScrollButton();
  
  // 初始化主題管理功能
  initThemeSupport();
});

// 載入魔法陣列表
async function loadMagicCircles() {
  const grid = document.getElementById('magic-circle-grid');
  if (!grid) return;
  
  try {
    // 從API獲取魔法陣數據
    const response = await fetch('/bylin/api/magic-circle-data');
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message);
    }
    
    // 清空現有內容
    grid.innerHTML = '';
    
    // 合併API數據與靜態數據
    const combinedData = magicCircleData.map(staticItem => {
      const apiItem = data.magic_circles.find(api => api.key === staticItem.key);
      return {
        ...staticItem,
        quantity: apiItem ? apiItem.count : 0
      };
    });    
    combinedData.forEach((item, index) => {
      const card = createItemCard(item, index);
      grid.appendChild(card);
    });
    
    // 更新統計數據
    updateSummary();
    
  } catch (error) {
    console.error('載入魔法陣數據失敗:', error);
    showNotification('載入數據失敗: ' + error.message, 'warning');
    
    // 載入失敗時使用預設數據
    magicCircleData.forEach((item, index) => {
      const card = createItemCard(item, index);
      grid.appendChild(card);
    });
  }
}

// 創建道具卡片
function createItemCard(item, index) {
  const card = document.createElement('div');
  card.className = 'item-detail-card';
  card.setAttribute('data-rarity', item.rarity); // 添加稀有度屬性
  
  const rarityClass = `rarity-${item.rarity}`;
  const rarityText = {
    common: '普通',
    rare: '稀有',
    legendary: '傳說'
  };
  
  card.innerHTML = `
    <div class="item-image-section" style="background-image: url('${item.img}')">
      <div class="item-rarity ${rarityClass}">
        ${rarityText[item.rarity]}
      </div>
      <div class="item-image-overlay">
        <h3 class="item-name">${item.name}</h3>
      </div>
    </div>
    
    <div class="item-content">
      <div class="item-function">
        <h4><i class="fas fa-magic"></i> 功能效果</h4>
        <p>${item.bonus}</p>
      </div>
      
      <div class="item-story">
        <h4><i class="fas fa-book"></i> 道具故事</h4>
        <p>${item.story}</p>
      </div>
        <div class="item-quantity">
        <span class="quantity-label">剩餘數量</span>
        <span class="quantity-value">
          <i class="fas fa-box"></i>
          ${item.quantity || 0} 個
        </span>
      </div>
    </div>
  `;
    // 添加動畫延遲
  card.style.animationDelay = `${index * 0.1}s`;
  card.classList.add('fade-in');
  
  // 確保新內容應用主題
  applyThemeToNewContent(card);
  
  return card;
}

// 更新統計摘要
function updateSummary() {
  const totalElement = document.getElementById('total-magic-circles');
  if (totalElement) {
    totalElement.textContent = magicCircleData.length;
  }
}

// 初始化滾動按鈕
function initScrollButton() {
  const scrollTopBtn = document.getElementById('scroll-top-btn');
  if (!scrollTopBtn) return;
  
  // 監聽滾動事件
  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      scrollTopBtn.classList.add('visible');
    } else {
      scrollTopBtn.classList.remove('visible');
    }
  });
  
  // 點擊事件
  scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}

// 顯示通知
function showNotification(message, type = 'info') {
  // 檢測當前主題
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const isLightTheme = currentTheme === 'light';
  
  const colors = {
    success: isLightTheme ? 'linear-gradient(45deg, #4caf50, #8bc34a)' : 'linear-gradient(45deg, #4caf50, #8bc34a)',
    warning: isLightTheme ? 'linear-gradient(45deg, #ff9800, #ffc107)' : 'linear-gradient(45deg, #ff9800, #ffc107)',
    info: isLightTheme ? 'linear-gradient(45deg, #2196f3, #03a9f4)' : 'var(--primary-gradient)'
  };
  
  const textColor = isLightTheme ? 'white' : 'white';
  const shadowColor = isLightTheme ? 'rgba(0, 0, 0, 0.2)' : 'var(--shadow-color)';
  
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  notification.style.cssText = `
    position: fixed;
    top: 30px;
    right: 30px;
    background: ${colors[type] || colors.info};
    color: ${textColor};
    padding: 15px 25px;
    border-radius: 25px;
    box-shadow: 0 5px 15px ${shadowColor};
    z-index: 10000;
    font-weight: 600;
    transform: translateX(400px);
    transition: transform 0.3s ease;
  `;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);
  
  setTimeout(() => {
    notification.style.transform = 'translateX(400px)';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 300);
  }, 3000);
}

// 主題管理功能
function initThemeSupport() {
  // 檢查並應用保存的主題設置
  const savedTheme = localStorage.getItem('user-theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
  
  // 監聽主題變化事件（由base.html的主題切換按鈕觸發）
  document.addEventListener('themeChanged', function(e) {
    document.documentElement.setAttribute('data-theme', e.detail.theme);
  });
  
  // 監聽localStorage變化（當其他頁面切換主題時）
  window.addEventListener('storage', function(e) {
    if (e.key === 'user-theme') {
      document.documentElement.setAttribute('data-theme', e.newValue);
    }
  });
}

// 確保動態內容應用主題
function applyThemeToNewContent(element) {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  if (currentTheme === 'light') {
    // 為新建立的元素強制應用淺色主題樣式
    element.style.color = 'var(--details-text-color)';
    
    // 遞迴處理所有子元素
    const allElements = element.querySelectorAll('*');
    allElements.forEach(el => {
      if (!el.classList.contains('use-potion-btn') && 
          !el.classList.contains('floating-action-btn') &&
          !el.classList.contains('item-rarity')) {
        el.style.color = 'var(--details-text-color)';
      }
    });
    
    // 處理圖標
    const icons = element.querySelectorAll('i, .fa, .fas');
    icons.forEach(icon => {
      if (!icon.closest('.use-potion-btn') && 
          !icon.closest('.floating-action-btn') &&
          !icon.closest('.item-rarity')) {
        icon.style.color = 'var(--accent-color)';
      }
    });
  }
}

// 添加淡入動畫樣式
const style = document.createElement('style');
style.textContent = `
  .fade-in {
    opacity: 0;
    transform: translateY(20px);
    animation: fadeInUp 0.6s ease forwards;
  }
  
  @keyframes fadeInUp {
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;
document.head.appendChild(style);
