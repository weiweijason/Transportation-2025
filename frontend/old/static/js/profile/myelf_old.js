/**
 * 我的精靈頁面 JavaScript
 * 處理 Firebase 連接和精靈數據管理
 */

// 全局變量
let db;
let currentUserId;
let userCreatures = [];
let filteredCreatures = [];
let currentSortField = 'name';
let currentSortOrder = 'asc';

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
    }

    // 添加排序順序切換
    const sortOrderBtn = document.getElementById('sort-order-btn');
    if (sortOrderBtn) {
        sortOrderBtn.addEventListener('click', toggleSortOrder);
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

        console.log(`成功載入 ${userCreatures.length} 隻精靈`);
        
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
    const typeStats = getTypeStatistics();
    
    // 更新統計面板
    updateElement('total-count', totalCount);
    updateElement('species-count', getUniqueSpeciesCount());
    updateElement('total-power', getTotalPower());
    updateElement('average-level', getAverageLevel());
}

/**
 * 獲取類型統計
 */
function getTypeStatistics() {
    const stats = {
        water: 0, fire: 0, wood: 0, 
        light: 0, dark: 0, normal: 0
    };
    
    userCreatures.forEach(creature => {
        const type = creature.element_type || 'normal';
        if (stats[type] !== undefined) {
            stats[type]++;
        } else {
            stats.normal++;
        }
    });
    
    return stats;
}

/**
 * 獲取唯一種類數量
 */
function getUniqueSpeciesCount() {
    const uniqueSpecies = new Set(userCreatures.map(c => c.name));
    return uniqueSpecies.size;
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
    return Math.round(totalLevel / userCreatures.length);
}

/**
 * 渲染全部精靈
 */
function renderAllCreatures() {
    const container = document.getElementById('creature-list');
    if (!container) return;

    if (filteredCreatures.length === 0) {
        if (userCreatures.length === 0) {
            showEmptyState();
        } else {
            showNoResults();
        }
        return;
    }

    container.innerHTML = '';
    
    // 排序精靈
    const sortedCreatures = sortCreatures(filteredCreatures);
    
    sortedCreatures.forEach(creature => {
        const creatureCard = createCreatureCard(creature);
        container.appendChild(creatureCard);
    });
}

/**
 * 按類型渲染精靈
 */
function renderCreaturesByTypes() {
    const types = ['water', 'fire', 'wood', 'light', 'dark', 'normal'];
    
    types.forEach(type => {
        const creatures = filteredCreatures.filter(c => (c.element_type || 'normal') === type);
        const container = document.getElementById(`${type}-creatures-list`);
        
        if (!container) return;
        
        if (creatures.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-4">
                    <p class="text-muted">尚無${getTypeText(type)}精靈</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        const sortedCreatures = sortCreatures(creatures);
        
        sortedCreatures.forEach(creature => {
            const creatureCard = createCreatureCard(creature);
            container.appendChild(creatureCard);
        });
    });
}

/**
 * 創建精靈卡片
 */
function createCreatureCard(creature) {
    const col = document.createElement('div');
    col.className = 'col-6 col-md-4 col-lg-3 mb-3';
    
    const attack = creature.attack || creature.power || 0;
    const hp = creature.hp || 100;
    const level = creature.level || 1;
    
    col.innerHTML = `
        <div class="card creature-card h-100 shadow-sm" style="cursor: pointer;" onclick="showCreatureDetail('${creature.id}')">
            <div class="creature-image position-relative">
                <img src="${creature.image_url || getDefaultImage(creature.element_type)}" 
                     alt="${creature.name}" class="card-img-top" style="height: 150px; object-fit: cover;">
                <div class="position-absolute top-0 start-0 m-2">
                    <span class="badge bg-${getTypeColor(creature.element_type)}">${getTypeText(creature.element_type)}</span>
                </div>
                <div class="position-absolute top-0 end-0 m-2">
                    <span class="badge bg-dark">Lv.${level}</span>
                </div>
            </div>
            <div class="card-body text-center">
                <h6 class="card-title mb-2">${creature.name}</h6>
                <div class="creature-type mb-2">
                    <span class="badge bg-secondary">${creature.species || '一般種'}</span>
                </div>
                <div class="row text-center">
                    <div class="col-6">
                        <small class="text-muted">攻擊</small>
                        <div class="fw-bold text-danger">${attack}</div>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">生命</small>
                        <div class="fw-bold text-success">${hp}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

/**
 * 顯示精靈詳情
 */
function showCreatureDetail(creatureId) {
    const creature = userCreatures.find(c => c.id === creatureId);
    if (!creature) return;

    // 更新模態框內容
    updateElement('modal-creature-name', creature.name);
    updateElement('modal-creature-attack', creature.attack || creature.power || 0);
    updateElement('modal-creature-hp', creature.hp || 100);
    updateElement('modal-creature-level', creature.level || 1);
    updateElement('modal-creature-exp', creature.experience || 0);
    updateElement('modal-creature-species', creature.species || '一般種');
    updateElement('modal-creature-captured', formatDate(creature.captured_at));

    // 更新圖片
    const imageElement = document.getElementById('modal-creature-image');
    if (imageElement) {
        imageElement.src = creature.image_url || getDefaultImage(creature.element_type);
        imageElement.alt = creature.name;
    }

    // 更新類型標籤
    const typeElement = document.getElementById('modal-creature-type');
    if (typeElement) {
        typeElement.innerHTML = `
            <span class="badge bg-${getTypeColor(creature.element_type)} fs-6">
                ${getTypeText(creature.element_type)}
            </span>
        `;
    }

    // 更新路線資訊
    const routeInfo = document.getElementById('modal-creature-route-info');
    const routeElement = document.getElementById('modal-creature-route');
    if (creature.bus_route_name && routeInfo && routeElement) {
        routeElement.textContent = creature.bus_route_name;
        routeInfo.style.display = 'block';
    } else if (routeInfo) {
        routeInfo.style.display = 'none';
    }

    // 顯示模態框
    const modal = new bootstrap.Modal(document.getElementById('creatureDetailModal'));
    modal.show();
}

/**
 * 處理搜尋
 */
function handleCreatureSearch(event) {
    const searchTerm = event.target.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        filteredCreatures = [...userCreatures];
    } else {
        filteredCreatures = userCreatures.filter(creature => 
            creature.name.toLowerCase().includes(searchTerm) ||
            (creature.species && creature.species.toLowerCase().includes(searchTerm))
        );
    }
    
    renderAllCreatures();
    renderCreaturesByTypes();
    updateTabCounts();
}

/**
 * 處理排序
 */
function handleCreatureSort(event) {
    currentSortField = event.target.value;
    renderAllCreatures();
    renderCreaturesByTypes();
}

/**
 * 切換排序順序
 */
function toggleSortOrder() {
    const btn = document.getElementById('sort-order-btn');
    if (!btn) return;
    
    currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    btn.dataset.order = currentSortOrder;
    
    // 更新圖標
    const icon = btn.querySelector('i');
    if (icon) {
        icon.className = currentSortOrder === 'asc' ? 
            'fas fa-sort-alpha-down' : 'fas fa-sort-alpha-up';
    }
    
    renderAllCreatures();
    renderCreaturesByTypes();
}

/**
 * 排序精靈
 */
function sortCreatures(creatures) {
    return [...creatures].sort((a, b) => {
        let aValue, bValue;
        
        switch (currentSortField) {
            case 'name':
                aValue = a.name || '';
                bValue = b.name || '';
                break;
            case 'power':
                aValue = a.attack || a.power || 0;
                bValue = b.attack || b.power || 0;
                break;
            case 'level':
                aValue = a.level || 1;
                bValue = b.level || 1;
                break;
            case 'captured_at':
                aValue = a.captured_at || 0;
                bValue = b.captured_at || 0;
                break;
            default:
                aValue = a.name || '';
                bValue = b.name || '';
        }
        
        if (typeof aValue === 'string') {
            const result = aValue.localeCompare(bValue);
            return currentSortOrder === 'asc' ? result : -result;
        } else {
            const result = aValue - bValue;
            return currentSortOrder === 'asc' ? result : -result;
        }
    });
}

/**
 * 更新分頁計數
 */
function updateTabCounts() {
    const stats = getTypeStatistics();
    
    updateElement('all-count', filteredCreatures.length);
    updateElement('water-count', filteredCreatures.filter(c => (c.element_type || 'normal') === 'water').length);
    updateElement('fire-count', filteredCreatures.filter(c => (c.element_type || 'normal') === 'fire').length);
    updateElement('wood-count', filteredCreatures.filter(c => (c.element_type || 'normal') === 'wood').length);
    updateElement('light-count', filteredCreatures.filter(c => (c.element_type || 'normal') === 'light').length);
    updateElement('dark-count', filteredCreatures.filter(c => (c.element_type || 'normal') === 'dark').length);
    updateElement('normal-count', filteredCreatures.filter(c => (c.element_type || 'normal') === 'normal').length);
}

/**
 * 顯示載入狀態
 */
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    const tabs = document.querySelector('.creature-tabs');
    
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
    if (tabs) {
        tabs.style.display = show ? 'none' : 'block';
    }
}

/**
 * 顯示錯誤訊息
 */
function showError(message) {
    const errorElement = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    if (errorElement && errorText) {
        errorText.textContent = message;
        errorElement.style.display = 'block';
    }
    
    showLoading(false);
}

/**
 * 顯示空狀態
 */
function showEmptyState() {
    const container = document.getElementById('creature-list');
    if (!container) return;
    
    container.innerHTML = `
        <div class="col-12 text-center py-5">
            <img src="https://cdn-icons-png.flaticon.com/512/4698/4698906.png" 
                 alt="尚無精靈" style="max-width: 120px; opacity: 0.5;" class="mb-3">
            <h5 class="text-muted mb-2">您還沒有捕捉到任何精靈</h5>
            <p class="text-muted">快去地圖上尋找並捕捉您的第一隻精靈吧！</p>
            <a href="/game/catch" class="btn btn-primary mt-2">
                <i class="fas fa-search me-1"></i>開始捕捉精靈
            </a>
        </div>
    `;
}

/**
 * 顯示無搜尋結果
 */
function showNoResults() {
    const container = document.getElementById('creature-list');
    if (!container) return;
    
    container.innerHTML = `
        <div class="col-12 text-center py-4">
            <i class="fas fa-search text-muted mb-3" style="font-size: 3rem; opacity: 0.5;"></i>
            <h5 class="text-muted mb-2">找不到符合條件的精靈</h5>
            <p class="text-muted">請嘗試其他搜尋條件</p>
        </div>
    `;
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
 * 工具函數：獲取預設圖片
 */
function getDefaultImage(elementType) {
    const defaultImages = {
        water: 'https://via.placeholder.com/150/4FC3F7/FFFFFF?text=水',
        fire: 'https://via.placeholder.com/150/F44336/FFFFFF?text=火',
        wood: 'https://via.placeholder.com/150/4CAF50/FFFFFF?text=草',
        light: 'https://via.placeholder.com/150/FFC107/FFFFFF?text=光',
        dark: 'https://via.placeholder.com/150/424242/FFFFFF?text=暗',
        normal: 'https://via.placeholder.com/150/9E9E9E/FFFFFF?text=一般'
    };
    
    return defaultImages[elementType] || defaultImages.normal;
}

/**
 * 工具函數：格式化日期
 */
function formatDate(timestamp) {
    if (!timestamp) return '未知日期';
    
    try {
        // 如果是Firebase Timestamp格式
        if (timestamp && timestamp.seconds) {
            const date = new Date(timestamp.seconds * 1000);
            return date.toLocaleDateString('zh-TW');
        }
        
        // 如果是數字時間戳
        if (typeof timestamp === 'number') {
            const date = new Date(timestamp * 1000);
            return date.toLocaleDateString('zh-TW');
        }
        
        // 其他格式
        const date = new Date(timestamp);
        return date.toLocaleDateString('zh-TW');
    } catch (e) {
        return '未知日期';
    }
}
