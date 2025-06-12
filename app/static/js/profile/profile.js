/**
 * profile.js - 處理用戶個人資料頁面的JavaScript邏輯
 * 主要功能包括:
 * - 從Firebase獲取用戶資料
 * - 顯示用戶精靈列表
 * - 顯示用戶擂台列表
 * - 更新用戶統計資訊
 */

// Firebase配置在HTML模板中以變數形式傳入

// 初始化Firebase
function initFirebase(firebaseConfig) {
    if (!firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
    }
    return firebase.firestore();
}

// 加載用戶資料
function loadUserData(userId, db) {
    if (!userId) {
        console.error("未登入或找不到用戶ID");
        return;
    }
    
    // 從Firestore獲取用戶資料
    db.collection('users').doc(userId).get()
        .then(function(doc) {
            if (doc.exists) {
                const userData = doc.data();
                updateUserProfile(userData);
                
                // 獲取用戶已捕獲的精靈
                loadUserCreatures(userId, db);
                
                // 獲取用戶擁有的擂台
                loadUserArenas(userId, db);
            } else {
                console.error("找不到用戶資料!");
            }
        })
        .catch(function(error) {
            console.error("獲取用戶資料錯誤:", error);
        });
}

// 更新用戶資料顯示
function updateUserProfile(userData) {
    // 設定用戶等級
    const userLevel = userData.level || 1;
    document.getElementById('user-level').textContent = userLevel;
    
    // 設定經驗值
    const userExp = userData.experience || 0;
    const nextLevelExp = userLevel * 100; // 假設每級需要100*等級的經驗值
    document.getElementById('exp-text').textContent = `${userExp}/${nextLevelExp}`;
    
    // 更新經驗值進度條
    const expPercentage = (userExp / nextLevelExp) * 100;
    document.getElementById('exp-progress').style.width = `${expPercentage}%`;
    
    // 更新戰鬥次數
    const battleCount = userData.fight_count || 0;
    document.getElementById('battle-count').textContent = battleCount;
}

// 加載用戶的精靈
function loadUserCreatures(userId, db) {
    db.collection('users').doc(userId).collection('user_creatures').get()
        .then(function(querySnapshot) {
            const creatures = [];
            querySnapshot.forEach(function(doc) {
                creatures.push(doc.data());
            });
            
            // 更新顯示已捕獲的精靈數量
            document.getElementById('captured-count').textContent = creatures.length;
            
            // 如果有精靈，顯示精靈列表
            if (creatures.length > 0) {
                renderCreatures(creatures);
                
                // 按元素類型分類精靈
                const waterCreatures = creatures.filter(c => c.element_type === 'water');
                const fireCreatures = creatures.filter(c => c.element_type === 'fire');
                const earthCreatures = creatures.filter(c => c.element_type === 'earth');
                const airCreatures = creatures.filter(c => c.element_type === 'air');
                
                // 更新各類型分頁的內容
                if (waterCreatures.length > 0) {
                    renderCreaturesByType('water-creatures', waterCreatures);
                }
                if (fireCreatures.length > 0) {
                    renderCreaturesByType('fire-creatures', fireCreatures);
                }
                if (earthCreatures.length > 0) {
                    renderCreaturesByType('earth-creatures', earthCreatures);
                }
                if (airCreatures.length > 0) {
                    renderCreaturesByType('air-creatures', airCreatures);
                }
            }
        })
        .catch(function(error) {
            console.error("獲取精靈資料錯誤:", error);
        });
}

// 加載用戶的擂台
function loadUserArenas(userId, db) {
    db.collection('arenas').where('owner_id', '==', userId).get()
        .then(function(querySnapshot) {
            const arenas = [];
            querySnapshot.forEach(function(doc) {
                arenas.push(doc.data());
            });
            
            // 更新顯示擁有的擂台數量
            document.getElementById('arena-count').textContent = arenas.length;
            
            // 如果有擂台，顯示擂台列表
            if (arenas.length > 0) {
                renderArenas(arenas);
            }
        })
        .catch(function(error) {
            console.error("獲取擂台資料錯誤:", error);
        });
}

// 渲染精靈列表
function renderCreatures(creatures) {
    const creatureList = document.getElementById('creature-list');
    creatureList.innerHTML = '';
    
    if (creatures.length === 0) {
        // 如果沒有精靈，顯示空狀態
        creatureList.innerHTML = `
        <div class="col-12 text-center py-4">
            <img src="https://cdn-icons-png.flaticon.com/512/4698/4698906.png" alt="尚無精靈" style="max-width: 100px; opacity: 0.5;" class="mb-3">
            <p class="text-muted">你還沒有捕捉到任何精靈。</p>
            <a href="/game/catch" class="btn btn-primary mt-2">
                <i class="fas fa-search me-1"></i>開始捕捉精靈
            </a>
        </div>`;
        return;
    }
    
    creatures.forEach(creature => {
        const creatureCard = document.createElement('div');
        creatureCard.className = 'col-6 col-md-4 col-lg-3 mb-4'; // 增加底部間距
        creatureCard.innerHTML = `
            <div class="card creature-card">
                <div class="creature-image">
                    <img src="${creature.image_url || 'https://placehold.co/150?text=' + encodeURIComponent(creature.name)}" 
                         alt="${creature.name}">
                </div>                <div class="card-body text-center">
                    <h6 class="card-title">${creature.name}</h6>
                    <div class="creature-type mb-1">
                        <span class="badge bg-${getTypeColor(creature.element_type)}">${getTypeText(creature.element_type)}</span>
                        <span class="badge bg-secondary">${creature.species}</span>
                    </div>
                    <div class="creature-power">
                        <small class="text-muted">ATK: ${creature.attack || creature.power || 100} | HP: ${creature.hp || (creature.power || 100) * 10}</small>
                    </div>
                </div>
            </div>
        `;
        creatureList.appendChild(creatureCard);
    });
}

// 按類型渲染精靈列表
function renderCreaturesByType(containerId, creatures) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (creatures.length === 0) {
        // 如果該類型沒有精靈，顯示空狀態
        container.innerHTML = `
        <div class="text-center py-4">
            <p class="text-muted">尚無${getTypeText(containerId.split('-')[0])}精靈</p>
        </div>`;
        return;
    }
    
    const row = document.createElement('div');
    row.className = 'row';
    container.appendChild(row);
    
    creatures.forEach(creature => {
        const creatureCard = document.createElement('div');
        creatureCard.className = 'col-6 col-md-4 col-lg-3 mb-4'; // 增加底部間距
        creatureCard.innerHTML = `
            <div class="card creature-card">
                <div class="creature-image">
                    <img src="${creature.image_url || 'https://placehold.co/150?text=' + encodeURIComponent(creature.name)}" 
                         alt="${creature.name}">
                </div>                <div class="card-body text-center">
                    <h6 class="card-title">${creature.name}</h6>
                    <div class="creature-type mb-1">
                        <span class="badge bg-${getTypeColor(creature.element_type)}">${getTypeText(creature.element_type)}</span>
                        <span class="badge bg-secondary">${creature.species}</span>
                    </div>
                    <div class="creature-power">
                        <small class="text-muted">ATK: ${creature.attack || creature.power || 100} | HP: ${creature.hp || (creature.power || 100) * 10}</small>
                    </div>
                </div>
            </div>
        `;
        row.appendChild(creatureCard);
    });
}

// 渲染擂台列表
function renderArenas(arenas) {
    const arenaList = document.getElementById('arena-list');
    arenaList.innerHTML = '';
    
    arenas.forEach(arena => {
        const arenaCard = document.createElement('div');
        arenaCard.className = 'col-md-6 mb-3';
        arenaCard.innerHTML = `
            <div class="card arena-card h-100">
                <div class="card-body">
                    <h5 class="card-title">${arena.name || '未命名擂台'}</h5>
                    <div class="arena-details">
                        <div class="mb-2">
                            <span class="badge bg-primary">等級 ${arena.level || 1}</span>
                            <span class="badge bg-success">獎勵 ${arena.reward || 10} 經驗值</span>
                        </div>
                        <p class="small text-muted">${arena.description || '沒有描述'}</p>
                    </div>
                </div>
                <div class="card-footer d-flex justify-content-between align-items-center">
                    <small class="text-muted">已佔領: ${formatDate(arena.captured_at)}</small>
                    <a href="/game_arena/get_arena/${arena.id}" class="btn btn-sm btn-outline-danger">查看</a>
                </div>
            </div>
        `;
        arenaList.appendChild(arenaCard);
    });
}

// 根據精靈類型獲取顏色
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

// 根據精靈類型獲取中文名稱
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

// 格式化日期
function formatDate(timestamp) {
    if (!timestamp) return '未知日期';
    
    // 如果是Firebase Timestamp格式
    if (timestamp && timestamp.seconds) {
        const date = new Date(timestamp.seconds * 1000);
        return date.toLocaleDateString('zh-TW');
    }
    
    // 如果是其他格式，嘗試轉換為日期
    try {
        const date = new Date(timestamp);
        return date.toLocaleDateString('zh-TW');
    } catch (e) {
        return '未知日期';
    }
}

// 導出函數以便在頁面中使用
window.profileManager = {
    initFirebase,
    loadUserData
};