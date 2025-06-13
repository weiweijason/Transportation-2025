/**
 * 我的精靈頁面 JavaScript
 * 處理 Firebase 連接和精靈數據管理
 */

// 全局變量
let db;
let currentUserId;
let userCreatures = [];
let filteredCreatures = [];
let sortOrder = 'asc';
let currentSearchTerm = '';
let currentCreature = null; // 當前查看的精靈

/**
 * 初始化頁面
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeFirebase();
    initializeUI();
    loadUserData();
});

/**
 * 初始化 Firebase
 */
function initializeFirebase() {
    if (!firebase.apps.length) {
        firebase.initializeApp(window.firebaseConfig);
    }
    db = firebase.firestore();
}

/**
 * 初始化 UI 元素
 */
function initializeUI() {
    // 添加搜尋功能
    const searchInput = document.getElementById('creature-search');
    if (searchInput) {
        searchInput.addEventListener('input', handleCreatureSearch);
    }

    // 添加排序功能
    const sortSelect = document.getElementById('creature-sort');
    if (sortSelect) {
        sortSelect.addEventListener('change', handleCreatureSort);
    }    // 添加排序順序切換
    const sortOrderBtn = document.getElementById('sort-order-btn');
    if (sortOrderBtn) {
        sortOrderBtn.addEventListener('click', toggleSortOrder);
    }
    
    // 添加我的最愛按鈕事件
    const favoriteBtn = document.getElementById('favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', toggleFavorite);
    }

    // 添加分頁切換監聽
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            updateTabCounts();
        });
    });
}

/**
 * 載入用戶數據
 */
function loadUserData() {
    currentUserId = window.currentUserId;
    
    if (!currentUserId) {
        console.error("未登入或找不到用戶ID");
        showError("請先登入以查看您的精靈");
        return;
    }

    console.log("正在從 Firebase 獲取用戶數據, 用戶ID:", currentUserId);
    showLoading(true);
    
    // 獲取用戶精靈數據
    loadUserCreatures()
        .then(() => {
            showLoading(false);
        })
        .catch(error => {
            console.error("載入數據失敗:", error);
            showError("載入精靈數據失敗，請重新整理頁面");
            showLoading(false);
        });
}

/**
 * 載入用戶的精靈
 */
async function loadUserCreatures() {
    try {
        const querySnapshot = await db.collection('users')
            .doc(currentUserId)
            .collection('user_creatures')
            .get();
        
        userCreatures = [];
        querySnapshot.forEach(doc => {
            const creatureData = doc.data();
            creatureData.id = doc.id; // 添加文檔 ID
            userCreatures.push(creatureData);
        });

        console.log(`成功載入 ${userCreatures.length} 隻精靈`);        // 調試：顯示前幾隻精靈的數據結構，幫助確認字段名稱
        if (userCreatures.length > 0) {
            console.log(`成功載入 ${userCreatures.length} 隻精靈`);
            console.log('精靈數據範例:', userCreatures.slice(0, 3));
            
            // 詳細輸出前3隻精靈的屬性映射結果
            userCreatures.slice(0, 3).forEach((creature, index) => {
                const originalType = creature.type;
                const originalElementType = creature.element_type;
                const unifiedType = getCreatureElementType(creature);
                const typeText = getTypeText(unifiedType);
                const typeColor = getTypeColor(unifiedType);
                
                console.log(`精靈 ${index + 1} - ${creature.name}:`, {
                    name: creature.name,
                    original: { 
                        type: originalType, 
                        element_type: originalElementType,
                        species: creature.species 
                    },
                    processed: {
                        unified_type: unifiedType,
                        display_text: typeText,
                        color_class: typeColor,
                        species_display: creature.species || '一般種'
                    }
                });
            });
        }
        
        // 初始化過濾列表
        filteredCreatures = [...userCreatures];
        
        // 更新統計數據
        updateStatistics();
        
        // 渲染精靈列表
        if (userCreatures.length > 0) {
            renderAllCreatures();
            renderCreaturesByTypes();
        } else {
            showEmptyState();
        }
        
        // 更新分頁計數
        updateTabCounts();

    } catch (error) {
        console.error("獲取精靈資料錯誤:", error);
        throw error;
    }
}

/**
 * 更新統計數據
 */
function updateStatistics() {
    const totalCount = userCreatures.length;
    
    // 更新統計面板
    updateElement('total-count', totalCount);
    updateElement('total-power', getTotalPower());
    updateElement('average-power', getAveragePower());
}

/**
 * 獲取類型統計
 */
function getTypeStatistics() {
    const stats = {
        water: 0, fire: 0, wood: 0, 
        light: 0, dark: 0, normal: 0,
        favorite: 0
    };
    
    userCreatures.forEach(creature => {
        // 使用統一的屬性獲取方法
        const type = getCreatureElementType(creature);
        if (stats.hasOwnProperty(type)) {
            stats[type]++;
        } else {
            stats.normal++;
        }
        
        // 統計我的最愛
        if (creature.favorite === true) {
            stats.favorite++;
        }
    });
    
    return stats;
}

/**
 * 獲取獨特種類數量
 */
function getUniqueSpeciesCount() {
    const uniqueNames = new Set(userCreatures.map(creature => creature.name));
    return uniqueNames.size;
}

/**
 * 獲取總戰力
 */
function getTotalPower() {
    return userCreatures.reduce((total, creature) => {
        return total + (creature.attack || creature.power || 0);
    }, 0);
}

/**
 * 獲取平均等級
 */
function getAverageLevel() {
    if (userCreatures.length === 0) return 1;
    const totalLevel = userCreatures.reduce((total, creature) => {
        return total + (creature.level || 1);
    }, 0);
    return Math.round(totalLevel / userCreatures.length * 10) / 10;
}

/**
 * 獲取平均戰力
 */
function getAveragePower() {
    if (userCreatures.length === 0) return 0;
    const totalPower = getTotalPower();
    return Math.round(totalPower / userCreatures.length);
}

/**
 * 渲染所有精靈
 */
function renderAllCreatures() {
    const container = document.getElementById('creature-list');
    renderCreatureGrid(container, filteredCreatures);
}

/**
 * 按類型渲染精靈
 */
function renderCreaturesByTypes() {
    const types = ['water', 'fire', 'wood', 'light', 'dark', 'normal'];
    
    types.forEach(type => {
        const creatures = filteredCreatures.filter(creature => 
            getCreatureElementType(creature) === type
        );
        const container = document.getElementById(`${type}-creatures-list`);
        if (container) {
            renderCreatureGrid(container, creatures);
        }
    });
    
    // 渲染我的最愛
    const favoriteCreatures = filteredCreatures.filter(creature => 
        creature.favorite === true
    );
    const favoriteContainer = document.getElementById('favorite-creatures-list');
    if (favoriteContainer) {
        renderCreatureGrid(favoriteContainer, favoriteCreatures);
    }
}

/**
 * 渲染精靈網格
 */
function renderCreatureGrid(container, creatures) {
    if (!container) return;
    
    container.innerHTML = '';
      if (creatures.length === 0) {
        const containerId = container.id;
        let emptyMessage = '沒有找到符合條件的精靈';
        
        if (containerId === 'favorite-creatures-list') {
            emptyMessage = '還沒有加入任何精靈到我的最愛';
        }
        
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-heart text-muted mb-3" style="font-size: 3rem; opacity: 0.3;"></i>
                <p class="text-muted">${emptyMessage}</p>
            </div>
        `;
        return;
    }
    
    creatures.forEach(creature => {
        const creatureCard = createCreatureCard(creature);
        container.appendChild(creatureCard);
    });
}

/**
 * 創建精靈卡片
 */
function createCreatureCard(creature) {
    const cardElement = document.createElement('div');
    cardElement.className = 'col-6 col-md-4 col-lg-3 mb-3';
    
    const attack = creature.attack || creature.power || 0;
    const hp = creature.hp || 100;
    // 使用統一的屬性獲取方法
    const elementType = getCreatureElementType(creature);
    // 直接使用 species 欄位，不做轉換（保持原始 Firebase 資料）
    const creatureSpecies = creature.species || '一般種';
    
    cardElement.innerHTML = `
        <div class="card creature-card h-100 ${creature.favorite === true ? 'favorite-creature' : ''}" data-creature-id="${creature.id}">
            <div class="creature-image">
                ${creature.favorite === true ? '<div class="favorite-badge"><i class="fas fa-heart"></i></div>' : ''}
                <img src="${creature.image_url || getDefaultImage(elementType)}" 
                     alt="${creature.name}" class="img-fluid" 
                     onerror="this.src='${getDefaultImage(elementType)}'"
                     style="width: 100%; height: 160px; object-fit: contain; background: #f8f9fa;">
            </div>
            <div class="card-body text-center p-2">
                <h6 class="card-title mb-1">${creature.name}</h6>
                <div class="creature-type mb-2">
                    <span class="badge bg-${getTypeColor(elementType)}">${getTypeText(elementType)}</span>
                    <span class="badge bg-secondary">${creatureSpecies}</span>
                </div>
                <div class="creature-stats">
                    <div class="stat-item">
                        <span class="stat-icon">⚔️</span>
                        <span>${attack}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-icon">❤️</span>
                        <span>${hp}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 添加點擊事件
    cardElement.addEventListener('click', () => showCreatureDetail(creature));
    
    return cardElement;
}

/**
 * 顯示精靈詳情模態框
 */
function showCreatureDetail(creature) {
    currentCreature = creature; // 設置當前精靈
    const modal = new bootstrap.Modal(document.getElementById('creatureDetailModal'));
    
    // 填充模態框數據
    updateElement('modal-creature-name', creature.name);
    updateElement('modal-creature-attack', creature.attack || creature.power || 0);
    updateElement('modal-creature-hp', creature.hp || 100);
    updateElement('modal-creature-exp', creature.experience || 0);
    // 直接使用 species 欄位，不做轉換（保持原始 Firebase 資料）
    updateElement('modal-creature-species', creature.species || '一般種');
    
    // 設置圖片
    const imageElement = document.getElementById('modal-creature-image');
    if (imageElement) {
        // 使用統一的屬性獲取方法
        const elementType = getCreatureElementType(creature);
        imageElement.src = creature.image_url || getDefaultImage(elementType);
        imageElement.onerror = function() {
            this.src = getDefaultImage(elementType);
        };
        // 確保圖片正確顯示
        imageElement.style.maxHeight = '200px';
        imageElement.style.width = 'auto';
        imageElement.style.objectFit = 'contain';
    }
    
    // 設置類型標籤
    const typeContainer = document.getElementById('modal-creature-type');
    if (typeContainer) {
        // 使用統一的屬性獲取方法
        const elementType = getCreatureElementType(creature);
        typeContainer.innerHTML = `
            <span class="badge bg-${getTypeColor(elementType)} fs-6">${getTypeText(elementType)}</span>
        `;
    }
    
    // 設置捕獲時間
    const capturedElement = document.getElementById('modal-creature-captured');
    if (capturedElement) {
        capturedElement.textContent = formatDate(creature.captured_at);
    }
    
    // 設置路線信息
    const routeInfo = document.getElementById('modal-creature-route-info');
    const routeElement = document.getElementById('modal-creature-route');
    if (creature.bus_route_name && routeInfo && routeElement) {
        routeInfo.style.display = 'block';
        routeElement.textContent = creature.bus_route_name;
    } else if (routeInfo) {
        routeInfo.style.display = 'none';
    }
    
    // 更新我的最愛按鈕狀態
    updateFavoriteButton(creature.favorite === true);
    
    modal.show();
}

/**
 * 處理搜尋
 */
function handleCreatureSearch(event) {
    currentSearchTerm = event.target.value.toLowerCase().trim();
    applyFiltersAndSort();
}

/**
 * 處理排序
 */
function handleCreatureSort(event) {
    const sortBy = event.target.value;
    sortCreatures(sortBy);
}

/**
 * 切換排序順序
 */
function toggleSortOrder() {
    sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    
    const btn = document.getElementById('sort-order-btn');
    const icon = btn.querySelector('i');
    
    if (sortOrder === 'asc') {
        icon.className = 'fas fa-sort-alpha-down';
        btn.title = '升序排列';
    } else {
        icon.className = 'fas fa-sort-alpha-up';
        btn.title = '降序排列';
    }
    
    // 重新應用當前排序
    const sortSelect = document.getElementById('creature-sort');
    if (sortSelect) {
        sortCreatures(sortSelect.value);
    }
}

/**
 * 切換我的最愛狀態
 */
async function toggleFavorite() {
    if (!currentCreature) {
        console.error('沒有選中的精靈');
        return;
    }    try {
        // 更新按鈕狀態（樂觀更新）
        const newFavoriteStatus = !(currentCreature.favorite === true);
        updateFavoriteButton(newFavoriteStatus);
        
        // 調用後端 API 而不是直接操作 Firebase
        const response = await fetch(`/game/api/user/creatures/${currentCreature.id}/toggle-favorite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 更新本地數據
            currentCreature.favorite = result.favorite;
            
            // 更新 userCreatures 陣列中的對應精靈
            const creatureIndex = userCreatures.findIndex(c => c.id === currentCreature.id);
            if (creatureIndex !== -1) {
                userCreatures[creatureIndex].favorite = result.favorite;
            }
            
            // 重新渲染列表
            applyFiltersAndSort();
            
            console.log(`精靈 ${currentCreature.name} ${result.message}`);
            
            // 確保按鈕狀態與後端回傳的狀態一致
            updateFavoriteButton(result.favorite);
        } else {
            throw new Error(result.message);
        }
        
    } catch (error) {
        console.error('更新我的最愛狀態失敗:', error);
        // 恢復按鈕狀態
        updateFavoriteButton(currentCreature.favorite === true);
        alert('更新失敗，請稍後再試');
    }
}

/**
 * 更新我的最愛按鈕狀態
 */
function updateFavoriteButton(isFavorite) {
    const favoriteBtn = document.getElementById('favorite-btn');
    const favoriteText = document.getElementById('favorite-text');
    const favoriteIcon = favoriteBtn.querySelector('i');
    
    if (isFavorite) {
        favoriteBtn.className = 'btn btn-warning';
        favoriteIcon.className = 'fas fa-heart me-1';
        favoriteText.textContent = '移出我的最愛';
    } else {
        favoriteBtn.className = 'btn btn-outline-warning';
        favoriteIcon.className = 'far fa-heart me-1';
        favoriteText.textContent = '加入我的最愛';
    }
}

/**
 * 應用過濾和排序
 */
function applyFiltersAndSort() {
    // 先過濾
    filteredCreatures = userCreatures.filter(creature => {
        if (!currentSearchTerm) return true;
          const name = (creature.name || '').toLowerCase();
        const species = (creature.species || creature.type || creature.creature_type || '').toLowerCase();
        const elementType = getTypeText(creature.element_type || 'normal').toLowerCase();
          return name.includes(currentSearchTerm) || 
               species.includes(currentSearchTerm) || 
               elementType.includes(currentSearchTerm);
    });
    
    // 再排序
    const sortSelect = document.getElementById('creature-sort');
    if (sortSelect) {
        sortCreatures(sortSelect.value, false);
    }
    
    // 重新渲染
    renderAllCreatures();
    renderCreaturesByTypes();
    updateTabCounts();
}

/**
 * 排序精靈
 */
function sortCreatures(sortBy, shouldRender = true) {
    filteredCreatures.sort((a, b) => {
        let valueA, valueB;
        
        switch (sortBy) {
            case 'name':
                valueA = (a.name || '').toLowerCase();
                valueB = (b.name || '').toLowerCase();
                break;
            case 'power':
                valueA = a.attack || a.power || 0;
                valueB = b.attack || b.power || 0;
                break;
            case 'level':
                valueA = a.level || 1;
                valueB = b.level || 1;
                break;
            case 'captured_at':
                valueA = a.captured_at || 0;
                valueB = b.captured_at || 0;
                break;
            default:
                return 0;
        }
        
        if (typeof valueA === 'string') {
            return sortOrder === 'asc' 
                ? valueA.localeCompare(valueB)
                : valueB.localeCompare(valueA);
        } else {
            return sortOrder === 'asc' 
                ? valueA - valueB
                : valueB - valueA;
        }
    });
    
    if (shouldRender) {
        renderAllCreatures();
        renderCreaturesByTypes();
    }
}

/**
 * 更新分頁計數
 */
function updateTabCounts() {
    const typeStats = getTypeStatistics();
    
    updateElement('all-count', filteredCreatures.length);
    updateElement('water-count', typeStats.water);
    updateElement('fire-count', typeStats.fire);
    updateElement('wood-count', typeStats.wood);
    updateElement('light-count', typeStats.light);
    updateElement('dark-count', typeStats.dark);
    updateElement('normal-count', typeStats.normal);
    updateElement('favorite-count', typeStats.favorite);
}

/**
 * 顯示載入狀態
 */
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    const content = document.getElementById('creatureTabContent');
    
    if (spinner) spinner.style.display = show ? 'block' : 'none';
    if (content) content.style.display = show ? 'none' : 'block';
}

/**
 * 顯示錯誤訊息
 */
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    if (errorDiv && errorText) {
        errorText.textContent = message;
        errorDiv.style.display = 'block';
    }
    
    // 隱藏載入狀態
    showLoading(false);
}

/**
 * 顯示空狀態
 */
function showEmptyState() {
    const container = document.getElementById('creature-list');
    if (container) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <img src="https://cdn-icons-png.flaticon.com/512/4698/4698906.png" 
                     alt="尚無精靈" style="max-width: 120px; opacity: 0.5;" class="mb-3">
                <h5 class="text-muted mb-2">還沒有精靈</h5>
                <p class="text-muted mb-3">您還沒有捕捉到任何精靈，快去探索吧！</p>
                <a href="/game/catch" class="btn btn-primary">
                    <i class="fas fa-search me-1"></i>開始捕捉精靈
                </a>
            </div>
        `;
    }
}

/**
 * 工具函數：更新元素內容
 */
function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
}

/**
 * 獲取精靈的統一屬性類型 (處理多種數據格式)
 */
function getCreatureElementType(creature) {
    // 根據您的數據結構：優先使用 type，其次使用 element_type
    // 這樣可以確保 type: "dark" 不會被 element_type: 1 覆蓋
    let elementType = creature.type || creature.element_type;
    
    // 處理數值形式的 element_type (僅當 type 不存在時使用)
    if (typeof elementType === 'number') {
        switch(elementType) {
            case 0: return 'fire';    // FIRE = 0
            case 1: return 'water';   // WATER = 1
            case 2: return 'wood';    // WOOD = 2
            case 3: return 'light';   // LIGHT = 3
            case 4: return 'dark';    // DARK = 4
            case 5: return 'normal';  // NORMAL = 5
            default: return 'normal';
        }
    }
    
    // 處理字符串形式，統一轉為小寫
    if (typeof elementType === 'string') {
        const normalizedType = elementType.toLowerCase();
        
        // 處理英文字符串 (Firebase 數據格式)
        switch(normalizedType) {
            case 'water': return 'water';
            case 'fire': return 'fire';
            case 'wood': case 'grass': return 'wood';
            case 'light': return 'light';
            case 'dark': return 'dark';
            case 'normal': return 'normal';
            // 處理中文映射（向下兼容）
            case '水系': return 'water';
            case '火系': return 'fire';
            case '草系': case '木系': return 'wood';
            case '光系': return 'light';
            case '暗系': return 'dark';
            case '一般': case '普通': return 'normal';
            default: return 'normal';
        }
    }
    
    return 'normal'; // 默認返回普通系
}

/**
 * 根據精靈類型獲取顏色
 */
function getTypeColor(type) {
    // 如果傳入的是精靈對象，先獲取統一的屬性類型
    if (typeof type === 'object' && type !== null) {
        type = getCreatureElementType(type);
    }
    
    switch(String(type).toLowerCase()) {
        case 'water': return 'primary';
        case 'fire': return 'danger';
        case 'wood': case 'grass': return 'success';
        case 'light': return 'warning';
        case 'dark': return 'dark';
        case 'normal': return 'secondary';
        default: return 'secondary';
    }
}

/**
 * 根據精靈類型獲取中文名稱
 */
function getTypeText(type) {
    // 如果傳入的是精靈對象，先獲取統一的屬性類型
    if (typeof type === 'object' && type !== null) {
        type = getCreatureElementType(type);
    }
    
    switch(String(type).toLowerCase()) {
        case 'water': return '水系';
        case 'fire': return '火系';
        case 'wood': case 'grass': return '草系';
        case 'light': return '光系';
        case 'dark': return '暗系';
        case 'normal': return '一般';
        default: return '一般';
    }
}

/**
 * 首字母大寫
 */
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * 獲取預設圖片
 */
function getDefaultImage(type) {
    const typeImages = {
        water: 'https://cdn-icons-png.flaticon.com/512/2871/2871431.png',
        fire: 'https://cdn-icons-png.flaticon.com/512/785/785116.png',
        wood: 'https://cdn-icons-png.flaticon.com/512/1795/1795543.png',
        light: 'https://cdn-icons-png.flaticon.com/512/869/869869.png',
        dark: 'https://cdn-icons-png.flaticon.com/512/2871/2871394.png',
        normal: 'https://cdn-icons-png.flaticon.com/512/188/188918.png'
    };
    
    return typeImages[type] || typeImages.normal;
}

/**
 * 格式化日期
 */
function formatDate(timestamp) {
    if (!timestamp) return '未知日期';
    
    try {
        // 如果是Firebase Timestamp格式
        if (timestamp && timestamp.seconds) {
            const date = new Date(timestamp.seconds * 1000);
            return date.toLocaleDateString('zh-TW', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        // 如果是Unix timestamp
        if (typeof timestamp === 'number') {
            const date = new Date(timestamp * 1000);
            return date.toLocaleDateString('zh-TW', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        // 其他格式嘗試直接轉換
        const date = new Date(timestamp);
        return date.toLocaleDateString('zh-TW', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (e) {
        console.warn('日期格式化失敗:', timestamp, e);
        return '未知日期';
    }
}