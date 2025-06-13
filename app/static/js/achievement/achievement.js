// Achievement data with enhanced metadata
const achievementsData = [
    {
        category: "🐣 初次邂逅",
        icon: "fas fa-seedling",
        color: "#27ae60",
        achievements: [
            { code: "ACH-INIT-001", title: "Hello world", desc: "與你的第一隻精靈相遇。", completed: true, rarity: 1 }
        ]
    },
    {
        category: "🧩 屬性蒐集成就",
        icon: "fas fa-th-large",
        color: "#3498db",
        achievements: [
            { code: "ACH-TYPE-001", title: "我全都要", desc: "蒐集所有屬性精靈各一隻。", completed: true, rarity: 3 },
            { code: "ACH-TYPE-002", title: "草：一種日文", desc: "蒐集所有草屬性精靈。", completed: true, rarity: 2 },
            { code: "ACH-TYPE-003", title: "咕嚕咕嚕", desc: "蒐集所有水屬性精靈。", rarity: 2 },
            { code: "ACH-TYPE-004", title: "熱愛105度的你", desc: "蒐集所有火屬性精靈。", completed: true, rarity: 2 },
            { code: "ACH-TYPE-005", title: "正道的光", desc: "蒐集所有光屬性精靈。", completed: true, rarity: 2 },
            { code: "ACH-TYPE-006", title: "黑暗之子", desc: "蒐集所有暗屬性精靈。", completed: true, rarity: 2 },
            { code: "ACH-TYPE-007", title: "普通Disco", desc: "蒐集所有普通屬性精靈。", completed: true, rarity: 2 }
        ]
    },
    {
        category: "📦 精靈蒐集數量成就",
        icon: "fas fa-box",
        color: "#9b59b6",
        achievements: [
            { code: "ACH-COLL-001", title: "更上一層樓", desc: "蒐集 10 隻精靈。", completed: true, rarity: 1 },
            { code: "ACH-COLL-002", title: "更上二層樓", desc: "蒐集 20 隻精靈。", completed: true, rarity: 1 },
            { code: "ACH-COLL-003", title: "更上三層樓", desc: "蒐集 30 隻精靈。", completed: true, rarity: 2 },
            { code: "ACH-COLL-004", title: "更上四層樓", desc: "蒐集 40 隻精靈。", completed: true, rarity: 2 },
            { code: "ACH-COLL-005", title: "更上五層樓", desc: "蒐集 50 隻精靈。", completed: true, rarity: 2 },
            { code: "ACH-COLL-006", title: "更上六層樓", desc: "蒐集 60 隻精靈。", completed: true, rarity: 3 },
            { code: "ACH-COLL-007", title: "世界的真理，我已解明", desc: "蒐集所有精靈。", completed: true, rarity: 4 }
        ]
    },
    {
        category: "⚔️ 競技場對戰成就",
        icon: "fas fa-sword-crossed",
        color: "#e74c3c",
        achievements: [
            { code: "ACH-ARENA-001", title: "牛刀小試", desc: "參與一次競技場對戰。", completed: true, rarity: 1 },
            { code: "ACH-ARENA-002", title: "熱血沸騰", desc: "累積參與 10 次競技場對戰。", completed: true, rarity: 2 },
            { code: "ACH-ARENA-003", title: "好戰分子", desc: "累積參與 50 次競技場對戰。", completed: true, rarity: 3 },
            { code: "ACH-ARENA-004", title: "沉浸在戰鬥的藝術中", desc: "累積參與 100 次競技場對戰。", completed: true, rarity: 4 }
        ]
    },
    {
        category: "🏆 競技場勝利成就",
        icon: "fas fa-trophy",
        color: "#f39c12",
        achievements: [
            { code: "ACH-VICTORY-001", title: "勝利的果實", desc: "勝出一場競技場對戰。", completed: true, rarity: 1 },
            { code: "ACH-VICTORY-002", title: "我一個打十個", desc: "累積勝出 10 場競技場對戰。", completed: true, rarity: 2 },
            { code: "ACH-VICTORY-003", title: "還有誰？", desc: "累積勝出 50 場競技場對戰。", completed: true, rarity: 3 },
            { code: "ACH-VICTORY-004", title: "他簡直是戰神", desc: "累積勝出 100 場競技場對戰。", completed: true, rarity: 4 }
        ]
    },
    {
        category: "👥 交友成就",
        icon: "fas fa-users",
        color: "#1abc9c",
        achievements: [
            { code: "ACH-FRIEND-001", title: "不認識怎麼說話？", desc: "結交一名好友。", completed: true, rarity: 1 },
            { code: "ACH-FRIEND-002", title: "不說話怎麼認識？", desc: "結交 10 名好友。", completed: true, rarity: 2 },
            { code: "ACH-FRIEND-003", title: "四海之內皆兄弟", desc: "結交 50 名好友。", completed: true, rarity: 3 },
            { code: "ACH-FRIEND-004", title: "天下誰人不識君？", desc: "結交 100 名好友。", completed: true, rarity: 4 }
        ]
    },
    {
        category: "🏛️ 道館佔領成就",
        icon: "fas fa-building",
        color: "#8e44ad",
        achievements: [
            { code: "ACH-GYM-001", title: "此路由我開", desc: "成功佔領一個道館。", completed: true, rarity: 1 },
            { code: "ACH-GYM-002", title: "此樹由我栽", desc: "成功佔領兩個道館。", completed: true, rarity: 2 },
            { code: "ACH-GYM-003", title: "要從此地過", desc: "成功佔領三個道館。", completed: true, rarity: 2 },
            { code: "ACH-GYM-004", title: "留下買路財", desc: "成功佔領四個道館。", completed: true, rarity: 3 }
        ]
    },
    {
        category: "📅 登入天數成就",
        icon: "fas fa-calendar-check",
        color: "#2ecc71",
        achievements: [
            { code: "ACH-LOGIN-001", title: "感謝每一次相遇", desc: "累計登入 1 天。", completed: true, rarity: 1 },
            { code: "ACH-LOGIN-002", title: "感恩每一段緣分", desc: "累計登入 7 天。", completed: true, rarity: 1 },
            { code: "ACH-LOGIN-003", title: "珍惜旅途的風景", desc: "累計登入 30 天。", completed: true, rarity: 2 },
            { code: "ACH-LOGIN-004", title: "期待每一個明天", desc: "累計登入 60 天。", completed: true, rarity: 3 },
            { code: "ACH-LOGIN-005", title: "阿偉你麼還在打電動？", desc: "累計登入 100 天。", completed: true, rarity: 4 }
        ]
    },
    {
        category: "✨ 特殊成就",
        icon: "fas fa-sparkles",
        color: "#ff6b6b",
        achievements: [
            { code: "ACH-SPEC-001", title: "在轉動的地球再次相遇", desc: "超過 14 天未上線後再次登入。", completed: true, rarity: 3 }
        ]
    }
];

// Global variables
let currentFilter = 'all';
let searchQuery = '';

// Fetch user achievements from Firebase
function fetchUserAchievements(userId) {
  return db.collection('users').doc(userId).get()
    .then(doc => {
      if (!doc.exists) throw new Error("找不到用戶資料");
      const userData = doc.data();
      return userData.achievements || [];
    });
}

// Update achievements status based on user data
function updateAchievementsStatus(userCompletedAchievements) {
  achievementsData.forEach(category => {
    category.achievements.forEach(ach => {
      ach.completed = userCompletedAchievements.includes(ach.code);
    });
  });
}

// Calculate achievement statistics
function calculateStats() {
  const allAchievements = achievementsData.flatMap(cat => cat.achievements);
  const totalAchievements = allAchievements.length;
  const completedAchievements = allAchievements.filter(ach => ach.completed).length;
  const completionRate = totalAchievements > 0 ? Math.round((completedAchievements / totalAchievements) * 100) : 0;
  
  // For demo purposes, set recent achievements to a sample number
  // In a real app, this would be calculated based on recent completion dates
  const recentAchievements = Math.min(completedAchievements, 5);
  
  return {
    total: totalAchievements,
    completed: completedAchievements,
    rate: completionRate,
    recent: recentAchievements
  };
}

// Update statistics display
function updateStatsDisplay() {
  const stats = calculateStats();
  
  // Animate numbers
  animateNumber('totalAchievements', stats.total);
  animateNumber('completedAchievements', stats.completed);
  animateNumber('recentAchievements', stats.recent);
  
  // Update completion rate with animation
  setTimeout(() => {
    document.getElementById('completionRate').textContent = `${stats.rate}%`;
  }, 500);
}

// Animate number counting
function animateNumber(elementId, targetNumber) {
  const element = document.getElementById(elementId);
  let currentNumber = 0;
  const increment = Math.ceil(targetNumber / 20);
  const timer = setInterval(() => {
    currentNumber += increment;
    if (currentNumber >= targetNumber) {
      currentNumber = targetNumber;
      clearInterval(timer);
    }
    element.textContent = currentNumber;
  }, 50);
}

// Get rarity stars HTML
function getRarityStars(rarity) {
  const maxStars = 5;
  let starsHtml = '';
  for (let i = 0; i < maxStars; i++) {
    if (i < rarity) {
      starsHtml += '<i class="fas fa-star"></i>';
    } else {
      starsHtml += '<i class="far fa-star"></i>';
    }
  }
  return starsHtml;
}

// Get achievement icon based on category
function getAchievementIcon(category) {
  const iconMap = {
    "🐣 初次邂逅": "fas fa-seedling",
    "🧩 屬性蒐集成就": "fas fa-th-large", 
    "📦 精靈蒐集數量成就": "fas fa-box",
    "⚔️ 競技場對戰成就": "fas fa-fist-raised",
    "🏆 競技場勝利成就": "fas fa-trophy",
    "👥 交友成就": "fas fa-users",
    "🏛️ 道館佔領成就": "fas fa-building",
    "📅 登入天數成就": "fas fa-calendar-check",
    "✨ 特殊成就": "fas fa-sparkles"
  };
  return iconMap[category] || "fas fa-award";
}

// Filter achievements based on current filter and search query
function filterAchievements() {
  const filteredData = achievementsData.map(category => {
    const filteredAchievements = category.achievements.filter(ach => {
      // Filter by completion status
      let passesFilter = true;
      if (currentFilter === 'completed') {
        passesFilter = ach.completed;
      } else if (currentFilter === 'incomplete') {
        passesFilter = !ach.completed;
      }
      
      // Filter by search query
      if (searchQuery) {
        const searchMatch = ach.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           ach.desc.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           ach.code.toLowerCase().includes(searchQuery.toLowerCase());
        passesFilter = passesFilter && searchMatch;
      }
      
      return passesFilter;
    });
    
    return {
      ...category,
      achievements: filteredAchievements
    };
  }).filter(category => category.achievements.length > 0);
  
  return filteredData;
}

// Render achievements with improved design
function renderAchievements() {
  const container = document.getElementById('achievementAccordion');
  container.innerHTML = '';
  
  const filteredData = filterAchievements();
  
  if (filteredData.length === 0) {
    container.innerHTML = `
      <div class="text-center py-5">
        <i class="fas fa-search fa-3x text-muted mb-3"></i>
        <h4 class="text-muted">沒有找到符合條件的成就</h4>
        <p class="text-muted">試試調整搜尋條件或篩選選項</p>
      </div>
    `;
    return;
  }

  filteredData.forEach((category, idx) => {
    const categoryDiv = document.createElement('div');
    categoryDiv.className = 'accordion-item';

    const headerId = `heading${idx}`;
    const collapseId = `collapse${idx}`;
    
    // Calculate category completion stats
    const totalInCategory = category.achievements.length;
    const completedInCategory = category.achievements.filter(ach => ach.completed).length;
    const categoryProgress = totalInCategory > 0 ? Math.round((completedInCategory / totalInCategory) * 100) : 0;

    const header = document.createElement('div');
    header.className = 'accordion-header';
    header.id = headerId;
    header.setAttribute('data-category', idx);
    
    header.innerHTML = `
      <div class="d-flex align-items-center flex-grow-1">
        <i class="${category.icon || getAchievementIcon(category.category)} me-3" style="color: ${category.color || '#3498db'}"></i>
        <div>
          <div class="category-title">${category.category}</div>
          <div class="category-progress">
            <small class="text-muted">${completedInCategory}/${totalInCategory} 完成 (${categoryProgress}%)</small>
          </div>
        </div>
      </div>
    `;

    const content = document.createElement('div');
    content.id = collapseId;
    content.className = 'accordion-content';
    content.setAttribute('data-parent', '#achievementAccordion');

    const achievementList = document.createElement('div');
    achievementList.className = 'achievement-list';

    category.achievements.forEach((ach, achIdx) => {
      const achDiv = document.createElement('div');
      achDiv.className = `achievement-item ${!ach.completed ? 'not-completed' : ''}`;
      achDiv.style.animationDelay = `${achIdx * 0.1}s`;
      
      achDiv.innerHTML = `
        <div class="achievement-header-content">
          <div class="achievement-icon">
            <i class="${getAchievementIcon(category.category)}"></i>
          </div>
          <div class="achievement-content">
            <div class="achievement-code">${ach.code}</div>
            <div class="achievement-title">${ach.title}</div>
          </div>
        </div>
        <div class="achievement-desc">${ach.desc}</div>
        <div class="achievement-status">
          <div class="status-badge ${ach.completed ? 'completed' : 'incomplete'}">
            ${ach.completed ? '✓ 已完成' : '○ 未完成'}
          </div>
          <div class="achievement-rarity">
            <div class="rarity-stars">
              ${getRarityStars(ach.rarity || 1)}
            </div>
          </div>
        </div>
      `;
      
      achievementList.appendChild(achDiv);
    });

    content.appendChild(achievementList);
    categoryDiv.appendChild(header);
    categoryDiv.appendChild(content);
    container.appendChild(categoryDiv);    // Add click handler for accordion
    header.addEventListener('click', () => {
      const isActive = header.classList.contains('active');
      
      // Close all other accordions
      document.querySelectorAll('.accordion-header').forEach(h => {
        h.classList.remove('active');
      });
      document.querySelectorAll('.accordion-content').forEach(c => {
        c.classList.remove('active');
        c.style.maxHeight = '0';
      });
      
      if (!isActive) {
        header.classList.add('active');
        content.classList.add('active');
        // 使用 setTimeout 確保 DOM 完全渲染後再計算高度
        setTimeout(() => {
          content.style.maxHeight = content.scrollHeight + 20 + 'px'; // 增加一些緩衝空間
        }, 10);
        
        // 平滑滾動到展開的區域        // 如果展開的是最後一個項目或接近底部，確保有足夠的滾動空間
        setTimeout(() => {
          const headerRect = header.getBoundingClientRect();
          const windowHeight = window.innerHeight;
          const footerHeight = 100; // 估計 footer 高度
          
          // 如果手風琴標題在視窗下半部分，進行滾動調整
          if (headerRect.top > windowHeight * 0.6) {
            const scrollOffset = Math.max(0, headerRect.top - (windowHeight * 0.3));
            window.scrollTo({
              top: window.pageYOffset + scrollOffset,
              behavior: 'smooth'
            });
          }
          
          // 確保展開的內容不會被 footer 遮擋
          setTimeout(() => {
            const contentRect = content.getBoundingClientRect();
            const bottomVisible = contentRect.bottom + footerHeight;
            
            if (bottomVisible > windowHeight) {
              const additionalScroll = bottomVisible - windowHeight + 20;
              window.scrollTo({
                top: window.pageYOffset + additionalScroll,
                behavior: 'smooth'
              });
            }
          }, 400);
        }, 300);
      }
    });
  });
    // Auto-open first category
  if (filteredData.length > 0) {
    const firstHeader = container.querySelector('.accordion-header');
    const firstContent = container.querySelector('.accordion-content');
    if (firstHeader && firstContent) {
      firstHeader.classList.add('active');
      firstContent.classList.add('active');
      // 延遲計算高度確保內容完全載入
      setTimeout(() => {
        firstContent.style.maxHeight = firstContent.scrollHeight + 20 + 'px';
      }, 100);
    }
  }
}

// 新增：重新計算所有展開內容的高度（用於響應式調整）
function recalculateAccordionHeights() {
  document.querySelectorAll('.accordion-content.active').forEach(content => {
    content.style.maxHeight = 'none'; // 臨時移除限制
    const newHeight = content.scrollHeight;
    content.style.maxHeight = '0'; // 重置
    setTimeout(() => {
      content.style.maxHeight = newHeight + 20 + 'px';
    }, 10);
  });
}

// 新增：視窗大小改變時重新計算高度
window.addEventListener('resize', () => {
  clearTimeout(window.resizeTimeout);
  window.resizeTimeout = setTimeout(recalculateAccordionHeights, 250);
});

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  const userId = window.currentUserId; 
  if (!userId) return;
  // Setup search functionality
  const searchInput = document.getElementById('achievementSearch');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value;
      renderAchievements();
      // 重新計算展開內容高度
      setTimeout(recalculateAccordionHeights, 100);
    });
  }

  // Setup filter functionality
  const filterTabs = document.querySelectorAll('.filter-tab');
  filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs
      filterTabs.forEach(t => t.classList.remove('active'));
      // Add active class to clicked tab
      tab.classList.add('active');
      
      // Update current filter
      currentFilter = tab.getAttribute('data-filter');
      renderAchievements();
      // 重新計算展開內容高度
      setTimeout(recalculateAccordionHeights, 100);
    });
  });

  // Fetch user data and render
  fetchUserAchievements(userId)
    .then(userCompletedAchievements => {
      updateAchievementsStatus(userCompletedAchievements);
      updateStatsDisplay();
      renderAchievements();
    })
    .catch(err => {
      console.error('獲取成就資料錯誤:', err);
      // Show fallback with default data
      updateStatsDisplay();
      renderAchievements();
    });
});

// Add some utility functions for enhanced UX
function showAchievementDetails(achievementCode) {
  // This could open a modal with more detailed achievement information
  console.log('顯示成就詳情:', achievementCode);
}

function shareAchievement(achievementCode) {
  // This could implement social sharing functionality
  console.log('分享成就:', achievementCode);
}
