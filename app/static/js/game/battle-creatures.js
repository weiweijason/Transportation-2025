/**
 * 擂台戰鬥精靈選擇功能
 * 使用 Firebase 從 users/[user_id]/user_creatures 獲取用戶的精靈
 */

// 全局變數
let userCreatures = [];
let selectedCreature = null;
let userId = null;

/**
 * 初始化精靈選擇功能
 */
function initBattleCreatures() {
    // 從隱藏欄位獲取用戶ID
    userId = document.getElementById('user-id').value;
    
    if (!userId) {
        console.error("未登入或找不到用戶ID");
        return;
    }
    
    // 獲取用戶精靈
    loadUserCreatures();
    
    // 設置過濾按鈕事件
    setupFilterButtons();
}

/**
 * 加載用戶的精靈
 */
function loadUserCreatures() {
    if (!userId) {
        console.error("未登入或找不到用戶ID");
        return;
    }
    
    // 顯示載入中
    document.getElementById('creatureList').innerHTML = `
        <div class="col-12 text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">載入中...</span>
            </div>
            <p class="mt-2">正在載入您的精靈...</p>
        </div>
    `;
    
    firebase.firestore().collection('users').doc(userId).collection('user_creatures').get()
        .then(function(querySnapshot) {
            userCreatures = [];
            querySnapshot.forEach(function(doc) {
                const creatureData = doc.data();
                creatureData.id = doc.id;
                userCreatures.push(creatureData);
            });
            
            // 根據攻擊力排序（由高到低）
            userCreatures.sort((a, b) => (b.attack || b.power) - (a.attack || a.power));
            
            // 渲染精靈選擇列表
            renderCreatureList(userCreatures);
        })
        .catch(function(error) {
            console.error("獲取精靈資料錯誤:", error);
            document.getElementById('creatureList').innerHTML = `
                <div class="col-12 text-center py-4">
                    <p class="text-danger">載入精靈失敗，請重試。</p>
                </div>
            `;
        });
}

/**
 * 渲染精靈列表
 * @param {Array} creatures - 用戶的精靈列表
 */
function renderCreatureList(creatures) {
    const creatureList = document.getElementById('creatureList');
    
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
        const typeColor = getTypeColor(creature.element_type || creature.type);
        const elementType = creature.element_type?.toLowerCase() || creature.type?.toLowerCase();
        
        const creatureCard = document.createElement('div');
        creatureCard.className = 'col-md-3 col-sm-6 mb-4';
        creatureCard.innerHTML = `
            <div class="card creature-card h-100" data-creature-id="${creature.id}" data-creature-type="${elementType}">
                <div class="creature-image">
                    <img src="${creature.image_url || 'https://placehold.co/150?text=' + encodeURIComponent(creature.name)}" 
                        alt="${creature.name}" class="img-fluid">
                </div>
                <div class="card-body creature-card-body p-3">
                    <h5 class="card-title">${creature.name}</h5>
                    <div class="d-flex justify-content-between mb-2">
                        <span class="badge bg-${typeColor}">${getTypeText(creature.element_type || creature.type)}</span>
                        <span class="badge bg-secondary">${creature.species || creature.rarity || '普通'}</span>
                    </div>                    <div class="d-flex justify-content-between align-items-center">
                        <div class="power-badge">
                            <small class="text-muted">ATK: ${creature.attack || creature.power || 100} | HP: ${creature.hp || (creature.power || 100) * 10}</small>
                        </div>
                        <div class="level-badge">
                            <small class="text-muted">Lv.${creature.level || 1}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        creatureList.appendChild(creatureCard);
        
        // 為每個精靈卡片添加點擊事件
        const card = creatureCard.querySelector('.creature-card');
        
        card.addEventListener('click', function(e) {
            selectCreature(creature.id, card);
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
    const creatureCards = document.querySelectorAll('.creature-card');
    
    creatureCards.forEach(card => {
        const cardType = card.getAttribute('data-creature-type');
        
        if (type === 'all' || cardType === type) {
            card.closest('.col-md-3').style.display = '';
        } else {
            card.closest('.col-md-3').style.display = 'none';
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
    const selectedCards = document.querySelectorAll('.creature-card.creature-selected');
    selectedCards.forEach(selectedCard => {
        selectedCard.classList.remove('creature-selected');
    });
    
    // 標記當前選中的精靈
    card.classList.add('creature-selected');
    selectedCreature = userCreatures.find(c => c.id === creatureId);
    
    // 啟用戰鬥按鈕
    document.getElementById('battleButton').disabled = false;
    
    // 添加震動效果
    card.style.animation = 'shake 0.5s';
    setTimeout(() => {
        card.style.animation = '';
    }, 500);
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
        case 'wood': return 'success';
        case '草系': return 'success';
        case 'light': return 'warning';
        case '光系': return 'warning';
        case 'dark': return 'dark';
        case '暗系': return 'dark';
        case 'normal': return 'secondary';
        case '一般': return 'secondary';
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
        case 'wood': return '草系';
        case 'light': return '光系';
        case 'dark': return '暗系';
        case 'normal': return '一般';
        default: return '一般';
    }
}

/**
 * 開始戰鬥，由挑戰按鈕觸發
 */
function startBattle() {
    if (!selectedCreature) {
        showGameAlert('請選擇一隻精靈進行挑戰', 'warning');
        return;
    }
    
    // 獲取URL中的擂台ID參數
    const urlParams = new URLSearchParams(window.location.search);
    const arenaId = urlParams.get('arena_id');
    
    if (!arenaId) {
        console.error("未提供擂台ID");
        showGameAlert('缺少擂台ID，無法挑戰', 'danger');
        return;
    }
    
    console.log('開始挑戰擂台:', arenaId, '使用精靈:', selectedCreature.name);
    showLoading();
    
    // 準備挑戰資料
    const challengeData = {
        arenaId: arenaId,
        creatureId: selectedCreature.id,
        creatureName: selectedCreature.name,
        creaturePower: selectedCreature.attack || selectedCreature.power
    };
    
    // 發送挑戰請求
    fetch('/game/api/arena/challenge', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(challengeData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('挑戰擂台失敗');
        }
        return response.json();
    })
    .then(data => {
        console.log('挑戰結果:', data);
        
        // 使用現有的戰鬥動畫和結果顯示功能
        if (typeof playBattleAnimation === 'function') {
            // 預先更新擂台數據，以便動畫後能顯示最新狀態
            window.arenaData = data.arena;
            
            // 播放戰鬥動畫
            playBattleAnimation(data.result, selectedCreature, data.arena.ownerCreature, function() {
                // 更新擂台顯示
                if (typeof updateArenaDisplay === 'function') {
                    updateArenaDisplay(data.arena);
                }
                
                // 顯示戰鬥結果
                if (typeof showBattleResult === 'function') {
                    showBattleResult(data.result, data.message, selectedCreature, data.arena);
                }
                
                hideLoading();
            });
        } else {
            // 如果沒有動畫功能，直接顯示結果
            showSimpleBattleResult(data.result, data.message, selectedCreature, data.arena);
            hideLoading();
        }
    })
    .catch(error => {
        console.error('挑戰擂台錯誤:', error);
        hideLoading();
        showGameAlert('挑戰擂台失敗，請稍後再試', 'danger');
    });
}

/**
 * 顯示簡單的戰鬥結果（沒有動畫時使用）
 */
function showSimpleBattleResult(isWin, message, challenger, arena) {
    let resultHTML = `
        <div class="alert alert-${isWin ? 'success' : 'danger'} mt-4">
            <h4 class="alert-heading">${isWin ? '戰鬥勝利！' : '戰鬥失敗！'}</h4>
            <p>${message}</p>
            <hr>            <p class="mb-0">
                您的精靈: ${challenger.name} (ATK: ${challenger.attack || challenger.power || 100} | HP: ${challenger.hp || (challenger.power || 100) * 10})
                ${arena.ownerCreature ? `vs 對手精靈: ${arena.ownerCreature.name} (ATK: ${arena.ownerCreature.attack || arena.ownerCreature.power || 100} | HP: ${arena.ownerCreature.hp || (arena.ownerCreature.power || 100) * 10})` : ''}
            </p>
        </div>
    `;
    
    const resultContainer = document.createElement('div');
    resultContainer.innerHTML = resultHTML;
    
    // 將結果插入到戰鬥區域
    const battleArea = document.querySelector('.battle-area-content');
    battleArea.appendChild(resultContainer);
    
    // 滾動到結果
    resultContainer.scrollIntoView({ behavior: 'smooth' });
}

/**
 * 顯示遊戲提示
 */
function showGameAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertContainer.style.top = '80px';
    alertContainer.style.right = '20px';
    alertContainer.style.zIndex = '9999';
    alertContainer.style.maxWidth = '300px';
    alertContainer.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
    
    alertContainer.innerHTML = `
        <div class="d-flex">
            <div class="me-3">
                <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            </div>
            <div>${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // 自動消失
    setTimeout(() => {
        alertContainer.classList.remove('show');
        setTimeout(() => {
            alertContainer.remove();
        }, 300);
    }, 5000);
}

/**
 * 顯示載入中
 */
function showLoading() {
    if (document.getElementById('loadingOverlay')) {
        document.getElementById('loadingOverlay').style.visibility = 'visible';
    }
}

/**
 * 隱藏載入中
 */
function hideLoading() {
    if (document.getElementById('loadingOverlay')) {
        document.getElementById('loadingOverlay').style.visibility = 'hidden';
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', initBattleCreatures);