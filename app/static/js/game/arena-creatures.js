/**
 * 擂台精靈選擇系統
 * 負責從Firebase獲取用戶精靈資料並提供選擇功能
 */

// 當前用戶ID
let userId = null;

// 當前選中的擂台ID
let currentArenaId = null;

// 當前選中的精靈ID
let selectedCreatureId = null;

// 用戶的所有精靈
let userCreatures = [];

/**
 * 初始化Firebase和事件監聽器
 */
function initializeArenaCreatures() {
    // 從頁面取得用戶ID
    userId = document.getElementById('user-id').value;
    
    if (!userId) {
        console.error("未登入或找不到用戶ID");
        return;
    }
    
    // 設置過濾按鈕事件
    setupFilterButtons();
}

/**
 * 打開精靈選擇對話框
 * @param {string} arenaId - 要挑戰的擂台ID
 */
function showCreatureSelection(arenaId) {
    currentArenaId = arenaId;
    selectedCreatureId = null;
    
    // 重置選擇狀態
    const creatureList = document.getElementById('creature-selection-list');
    creatureList.innerHTML = `
        <div class="col-12 text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">載入中...</span>
            </div>
            <p class="mt-2">正在載入您的精靈...</p>
        </div>
    `;
    
    // 顯示對話框
    const modal = new bootstrap.Modal(document.getElementById('selectCreatureModal'));
    modal.show();
    
    // 加載用戶的精靈
    loadUserCreatures();
}

/**
 * 加載用戶的精靈
 */
function loadUserCreatures() {
    if (!userId) {
        console.error("未登入或找不到用戶ID");
        return;
    }
    
    firebase.firestore().collection('users').doc(userId).collection('user_creatures').get()
        .then(function(querySnapshot) {
            userCreatures = [];
            querySnapshot.forEach(function(doc) {
                const creatureData = doc.data();
                creatureData.id = doc.id;
                userCreatures.push(creatureData);
            });
            
            // 渲染精靈選擇列表
            renderCreatureSelectionList(userCreatures);
        })
        .catch(function(error) {
            console.error("獲取精靈資料錯誤:", error);
            document.getElementById('creature-selection-list').innerHTML = `
                <div class="col-12 text-center py-4">
                    <p class="text-danger">載入精靈失敗，請重試。</p>
                </div>
            `;
        });
}

/**
 * 渲染精靈選擇列表
 * @param {Array} creatures - 用戶的精靈列表
 */
function renderCreatureSelectionList(creatures) {
    const creatureList = document.getElementById('creature-selection-list');
    
    if (creatures.length === 0) {
        creatureList.innerHTML = `
            <div class="col-12 text-center py-4">
                <img src="https://cdn-icons-png.flaticon.com/512/4698/4698906.png" alt="尚無精靈" style="max-width: 100px; opacity: 0.5;" class="mb-3">
                <p class="text-muted">您還沒有捕捉到任何精靈。</p>
                <a href="/game/catch" class="btn btn-primary mt-2">
                    <i class="fas fa-search me-1"></i>開始捕捉精靈
                </a>
            </div>
        `;
        return;
    }
    
    creatureList.innerHTML = '';
    
    creatures.forEach(creature => {
        const creatureCard = document.createElement('div');
        creatureCard.className = 'col-6 col-sm-4 col-md-3 mb-3';
        creatureCard.innerHTML = `
            <div class="card creature-selection-card h-100" data-creature-id="${creature.id}" data-creature-type="${creature.element_type?.toLowerCase() || creature.type?.toLowerCase()}">
                <div class="creature-image">
                    <img src="${creature.image_url || 'https://placehold.co/150?text=' + encodeURIComponent(creature.name)}" 
                         alt="${creature.name}" class="img-fluid">
                </div>
                <div class="card-body text-center p-2">
                    <h6 class="card-title mb-1">${creature.name}</h6>
                    <div class="creature-type mb-1">
                        <span class="badge bg-${getTypeColor(creature.element_type || creature.type)}">${getTypeText(creature.element_type || creature.type)}</span>
                        <span class="badge bg-secondary">${creature.species || creature.rarity || '一般'}</span>
                    </div>
                    <div class="mt-1">
                        <strong class="text-danger">${creature.attack || creature.power}</strong> <small>力量</small>
                    </div>
                    <button class="btn btn-danger btn-sm w-100 mt-2 select-creature-btn">選擇此精靈</button>
                </div>
            </div>
        `;
        creatureList.appendChild(creatureCard);
        
        // 為每個精靈卡片添加點擊事件
        const card = creatureCard.querySelector('.creature-selection-card');
        const selectBtn = creatureCard.querySelector('.select-creature-btn');
        
        selectBtn.addEventListener('click', function() {
            selectCreature(creature.id, card);
        });
        
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.select-creature-btn')) {
                selectCreature(creature.id, card);
            }
        });
    });
}

/**
 * 設置過濾按鈕事件
 */
function setupFilterButtons() {
    const filterButtons = document.querySelectorAll('.creature-filter button');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 移除所有按鈕的 active 狀態
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // 添加當前按鈕的 active 狀態
            this.classList.add('active');
            
            // 獲取過濾類型
            const filterType = this.getAttribute('data-filter');
            
            // 過濾精靈列表
            filterCreatures(filterType);
        });
    });
}

/**
 * 過濾精靈列表
 * @param {string} type - 過濾類型
 */
function filterCreatures(type) {
    const creatureCards = document.querySelectorAll('.creature-selection-card');
    
    creatureCards.forEach(card => {
        const cardType = card.getAttribute('data-creature-type');
        
        if (type === 'all' || cardType === type) {
            card.closest('.col-6').style.display = '';
        } else {
            card.closest('.col-6').style.display = 'none';
        }
    });
}

/**
 * 選擇精靈
 * @param {string} creatureId - 精靈ID
 * @param {Element} card - 精靈卡片元素
 */
function selectCreature(creatureId, card) {
    // 取消之前選中的精靈
    const selectedCards = document.querySelectorAll('.creature-selection-card.selected');
    selectedCards.forEach(selectedCard => {
        selectedCard.classList.remove('selected');
    });
    
    // 標記當前選中的精靈
    card.classList.add('selected');
    selectedCreatureId = creatureId;
    
    // 查找選擇的精靈數據
    const selectedCreature = userCreatures.find(c => c.id === creatureId);
    
    // 發送挑戰請求
    if (selectedCreature && currentArenaId) {
        // 關閉對話框
        const modal = bootstrap.Modal.getInstance(document.getElementById('selectCreatureModal'));
        modal.hide();
        
        // 同步資料到 Firebase 並發起挑戰
        initiateChallenge(currentArenaId, selectedCreature);
    }
}

/**
 * 發起挑戰
 * @param {string} arenaId - 擂台ID
 * @param {Object} creature - 精靈數據
 */
function initiateChallenge(arenaId, creature) {
    // 顯示載入提示
    Swal.fire({
        title: '正在準備挑戰...',
        text: '正在將您的精靈 ' + creature.name + ' 派往擂台',
        icon: 'info',
        showConfirmButton: false,
        allowOutsideClick: false,
        willOpen: () => {
            Swal.showLoading();
        }
    });
    
    // 同步擂台資料到 Firebase
    syncArenaToFirebase(arenaId);
    
    // 延遲一下確保數據同步完成，然後跳轉到戰鬥頁面
    setTimeout(() => {
        window.location.href = `/game/battle?arena_id=${arenaId}&creature_id=${creature.id}`;
    }, 1000);
}

/**
 * 同步擂台資料到 Firebase
 * @param {string} arenaId - 擂台ID
 */
function syncArenaToFirebase(arenaId) {
    console.log('同步擂台資料到 Firebase:', arenaId);
    
    // 使用 fetch API 發送請求到後端 API
    fetch(`/game/api/arena/sync/${arenaId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('同步結果:', data);
    })
    .catch(error => {
        console.error('同步擂台資料失敗:', error);
    });
}

/**
 * 根據精靈類型獲取顏色
 * @param {string} type - 精靈類型
 * @returns {string} - 對應的Bootstrap顏色class
 */
function getTypeColor(type) {
    switch(String(type).toLowerCase()) {
        case 'water': return 'primary';
        case '水系': return 'primary';
        case 'fire': return 'danger';
        case '火系': return 'danger';
        case 'earth': return 'warning';
        case '土系': return 'warning';
        case 'air': return 'success';
        case '風系': return 'success';
        case 'electric': return 'info';
        case '電系': return 'info';
        case 'dark': return 'dark';
        case '暗系': return 'dark';
        default: return 'secondary';
    }
}

/**
 * 根據精靈類型獲取中文名稱
 * @param {string} type - 精靈類型
 * @returns {string} - 對應的中文名稱
 */
function getTypeText(type) {
    switch(String(type).toLowerCase()) {
        case 'water': return '水系';
        case 'fire': return '火系';
        case 'earth': return '土系';
        case 'air': return '風系';
        case 'electric': return '電系';
        case 'dark': return '暗系';
        default: return '一般';
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', initializeArenaCreatures);