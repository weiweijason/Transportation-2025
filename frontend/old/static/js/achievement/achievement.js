/**
 * 成就系統前端JavaScript
 * 與後端API整合，顯示使用者成就進度
 */

class AchievementManager {
    constructor() {
        this.achievements = null;
        this.filteredAchievements = null;
        this.currentFilter = 'all';
        this.searchQuery = '';
        this.init();
    }

    /**
     * 初始化成就系統
     */
    async init() {
        try {
            await this.loadAchievements();
            this.setupEventListeners();
            this.renderAchievements();
            this.updateStats();
        } catch (error) {
            console.error('初始化成就系統失敗:', error);
            this.showError('載入成就資料失敗，請重新整理頁面再試。');
        }
    }    /**
     * 從後端API載入成就資料
     */
    async loadAchievements() {
        try {
            // 檢查是否為演示模式
            const isDemo = window.location.pathname.includes('/demo');
            const apiUrl = isDemo ? '/achievement/api/demo_achievements' : '/achievement/api/user_achievements';
            
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP錯誤! 狀態: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.status === 'success') {
                this.achievements = data;
                this.filteredAchievements = data;
            } else {
                throw new Error(data.message || '載入成就資料失敗');
            }
        } catch (error) {
            console.error('載入成就資料錯誤:', error);
            throw error;
        }
    }

    /**
     * 設置事件監聽器
     */
    setupEventListeners() {
        // 篩選標籤事件
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                this.setFilter(filter);
            });
        });

        // 搜尋功能
        const searchInput = document.querySelector('#achievement-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.applyFilters();
            });
        }
    }

    /**
     * 設置篩選器
     */
    setFilter(filter) {
        this.currentFilter = filter;
        
        // 更新篩選標籤的活動狀態
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        this.applyFilters();
    }

    /**
     * 應用篩選器和搜尋
     */
    applyFilters() {
        if (!this.achievements || !this.achievements.categories) return;

        const filteredCategories = {};
        
        for (const [categoryKey, categoryData] of Object.entries(this.achievements.categories)) {
            const filteredAchievements = categoryData.achievements.filter(achievement => {
                // 篩選器邏輯
                let passFilter = true;
                if (this.currentFilter === 'completed') {
                    passFilter = achievement.completed;
                } else if (this.currentFilter === 'incomplete') {
                    passFilter = !achievement.completed;
                }
                
                // 搜尋邏輯
                let passSearch = true;
                if (this.searchQuery) {
                    passSearch = achievement.name.toLowerCase().includes(this.searchQuery) ||
                               achievement.description.toLowerCase().includes(this.searchQuery);
                }
                
                return passFilter && passSearch;
            });
            
            if (filteredAchievements.length > 0) {
                filteredCategories[categoryKey] = {
                    ...categoryData,
                    achievements: filteredAchievements
                };
            }
        }
        
        this.filteredAchievements = {
            ...this.achievements,
            categories: filteredCategories
        };
        
        this.renderAchievements();
    }

    /**
     * 更新統計資料
     */
    updateStats() {
        if (!this.achievements || !this.achievements.stats) return;
        
        const stats = this.achievements.stats;
        
        // 總成就數
        const totalCard = document.querySelector('.stat-card.total-achievements');
        if (totalCard) {
            totalCard.innerHTML = `
                <div class="stat-icon">
                    <i class="fas fa-trophy"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-number">${stats.total}</div>
                    <div class="stat-label">總成就數</div>
                </div>
            `;
        }
        
        // 已完成成就數
        const completedCard = document.querySelector('.stat-card.completed-achievements');
        if (completedCard) {
            completedCard.innerHTML = `
                <div class="stat-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-number">${stats.completed}</div>
                    <div class="stat-label">已完成</div>
                </div>
            `;
        }
        
        // 完成率
        const rateCard = document.querySelector('.stat-card.completion-rate');
        if (rateCard) {
            rateCard.innerHTML = `
                <div class="stat-icon">
                    <i class="fas fa-percent"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-number">${stats.completion_rate}%</div>
                    <div class="stat-label">完成率</div>
                </div>
            `;
        }
        
        // 最近完成
        const recentCard = document.querySelector('.stat-card.recent-achievements');
        if (recentCard) {
            recentCard.innerHTML = `
                <div class="stat-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-number">${stats.recent}</div>
                    <div class="stat-label">最近完成</div>
                </div>
            `;
        }        // 更新頁面標題
        const titleElement = document.querySelector('.achievement-title');
        if (titleElement) {
            titleElement.innerHTML = `
                <i class="fas fa-trophy"></i>
                我的成就 
                <span class="achievement-count">${stats.completed}/${stats.total}</span>
            `;
        }

        // 更新搜尋容器
        const searchContainer = document.querySelector('.achievement-search-container');
        if (searchContainer) {
            searchContainer.innerHTML = `
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" id="achievement-search" placeholder="搜尋成就...">
                </div>
            `;
            
            // 重新綁定搜尋事件
            const searchInput = document.querySelector('#achievement-search');
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    this.searchQuery = e.target.value.toLowerCase();
                    this.applyFilters();
                });
            }
        }

        // 更新篩選按鈕
        const incompleteTab = document.querySelector('.filter-tab[data-filter="incomplete"]');
        if (incompleteTab) {
            incompleteTab.innerHTML = `
                <i class="fas fa-hourglass-half"></i> 未完成 (${stats.total - stats.completed})
            `;
        }
    }

    /**
     * 渲染成就列表
     */
    renderAchievements() {
        const container = document.querySelector('#achievementAccordion');
        if (!container || !this.filteredAchievements) return;

        container.innerHTML = '';

        for (const [categoryKey, categoryData] of Object.entries(this.filteredAchievements.categories)) {
            const categoryElement = this.createCategoryElement(categoryKey, categoryData);
            container.appendChild(categoryElement);
        }
    }

    /**
     * 創建成就類別元素
     */
    createCategoryElement(categoryKey, categoryData) {
        const achievements = categoryData.achievements;
        const completedCount = achievements.filter(a => a.completed).length;
        const totalCount = achievements.length;
        const completionRate = totalCount > 0 ? (completedCount / totalCount * 100).toFixed(1) : 0;

        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'achievement-category';
        categoryDiv.innerHTML = `
            <div class="category-header" data-bs-toggle="collapse" data-bs-target="#category-${categoryKey}" aria-expanded="false">
                <div class="category-info">
                    <div class="category-icon">
                        <i class="${categoryData.icon}"></i>
                    </div>
                    <div class="category-details">
                        <h3 class="category-title">${categoryData.display_name}</h3>
                        <div class="category-progress">
                            <span class="progress-text">${completedCount}/${totalCount} 已完成</span>
                            <div class="progress-bar-container">
                                <div class="progress-bar" style="width: ${completionRate}%"></div>
                            </div>
                            <span class="progress-percent">${completionRate}%</span>
                        </div>
                    </div>
                </div>
                <div class="category-toggle">
                    <i class="fas fa-chevron-down"></i>
                </div>
            </div>
            <div class="collapse" id="category-${categoryKey}">
                <div class="category-content">
                    <div class="achievements-grid">
                        ${achievements.map(achievement => this.createAchievementCard(achievement)).join('')}
                    </div>
                </div>
            </div>
        `;

        return categoryDiv;
    }

    /**
     * 創建成就卡片
     */
    createAchievementCard(achievement) {
        const progress = achievement.progress || 0;
        const target = achievement.target_value || 1;
        const progressPercent = target > 0 ? (progress / target * 100) : 0;
        const isCompleted = achievement.completed || false;
        
        const completedDate = achievement.completed_at ? 
            new Date(achievement.completed_at * 1000).toLocaleDateString('zh-TW') : '';

        return `
            <div class="achievement-card ${isCompleted ? 'completed' : ''}">
                <div class="achievement-icon">
                    <i class="${achievement.icon}"></i>
                    ${isCompleted ? '<div class="completion-badge"><i class="fas fa-check"></i></div>' : ''}
                </div>
                <div class="achievement-content">
                    <h4 class="achievement-name">${achievement.name}</h4>
                    <p class="achievement-description">${achievement.description}</p>
                    <div class="achievement-progress">
                        <div class="progress-info">
                            <span class="progress-text">${progress}/${target}</span>
                            <span class="progress-percent">${progressPercent.toFixed(1)}%</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: ${Math.min(progressPercent, 100)}%"></div>
                        </div>
                    </div>
                    ${isCompleted ? `
                        <div class="achievement-completion">
                            <i class="fas fa-calendar-check"></i>
                            <span>完成於 ${completedDate}</span>
                            <div class="reward-points">
                                <i class="fas fa-star"></i>
                                +${achievement.reward_points} 點
                            </div>
                        </div>
                    ` : ''}
                </div>
                ${!isCompleted && achievement.hidden ? '<div class="achievement-hidden">隱藏成就</div>' : ''}
            </div>
        `;
    }

    /**
     * 顯示錯誤訊息
     */
    showError(message) {
        const container = document.querySelector('.achievement-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle"></i>
                    ${message}
                </div>
            `;
        }
    }

    /**
     * 重新載入成就資料
     */
    async refresh() {
        try {
            await this.loadAchievements();
            this.renderAchievements();
            this.updateStats();
        } catch (error) {
            console.error('重新載入成就失敗:', error);
            this.showError('重新載入失敗，請稍後再試。');
        }
    }
}

/**
 * 成就通知管理器
 * 處理新成就的彈出式通知
 */
class AchievementNotificationManager {
    constructor() {
        this.notificationQueue = [];
        this.isShowing = false;
        this.init();
    }

    init() {
        // 創建通知容器
        this.createNotificationContainer();
        
        // 監聽全域成就事件
        window.addEventListener('achievement-unlocked', (event) => {
            this.showAchievementNotification(event.detail);
        });
    }

    createNotificationContainer() {
        if (document.querySelector('#achievement-notifications')) return;
        
        const container = document.createElement('div');
        container.id = 'achievement-notifications';
        container.className = 'achievement-notifications';
        container.innerHTML = `
            <div class="notification-overlay"></div>
            <div class="notification-content">
                <div class="notification-header">
                    <i class="fas fa-trophy achievement-trophy"></i>
                    <h3>成就解鎖！</h3>
                    <button class="notification-close" aria-label="關閉">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="notification-body">
                    <div class="achievement-notification-card">
                        <div class="achievement-notification-icon">
                            <i class="fas fa-star"></i>
                        </div>
                        <div class="achievement-notification-info">
                            <h4 class="achievement-notification-name"></h4>
                            <p class="achievement-notification-description"></p>
                            <div class="achievement-notification-reward">
                                <i class="fas fa-star"></i>
                                <span class="reward-points">+0 點</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="notification-footer">
                    <button class="btn btn-primary" onclick="this.closest('.achievement-notifications').style.display='none'">
                        太棒了！
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(container);
        
        // 綁定關閉事件
        container.querySelector('.notification-close').addEventListener('click', () => {
            this.hideNotification();
        });
        
        container.querySelector('.notification-overlay').addEventListener('click', () => {
            this.hideNotification();
        });
    }

    showAchievementNotification(achievement) {
        this.notificationQueue.push(achievement);
        if (!this.isShowing) {
            this.processQueue();
        }
    }

    processQueue() {
        if (this.notificationQueue.length === 0) {
            this.isShowing = false;
            return;
        }

        this.isShowing = true;
        const achievement = this.notificationQueue.shift();
        
        // 更新通知內容
        const container = document.querySelector('#achievement-notifications');
        if (container) {
            const iconElement = container.querySelector('.achievement-notification-icon i');
            const nameElement = container.querySelector('.achievement-notification-name');
            const descElement = container.querySelector('.achievement-notification-description');
            const rewardElement = container.querySelector('.reward-points');
            
            if (iconElement) iconElement.className = achievement.icon || 'fas fa-star';
            if (nameElement) nameElement.textContent = achievement.achievement_name || achievement.name || '未知成就';
            if (descElement) descElement.textContent = achievement.description || '恭喜完成此成就！';
            if (rewardElement) rewardElement.textContent = `+${achievement.reward_points || 0} 點`;
            
            // 顯示通知
            container.style.display = 'flex';
            container.classList.add('show');
            
            // 播放音效（如果支持）
            this.playAchievementSound();
            
            // 添加慶祝動畫
            this.triggerCelebrationAnimation();
        }
    }

    hideNotification() {
        const container = document.querySelector('#achievement-notifications');
        if (container) {
            container.classList.remove('show');
            setTimeout(() => {
                container.style.display = 'none';
                // 處理下一個通知
                setTimeout(() => {
                    this.processQueue();
                }, 500);
            }, 300);
        }
    }

    playAchievementSound() {
        try {
            // 創建音效（如果支持Web Audio API）
            if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
                const audioContext = new (AudioContext || webkitAudioContext)();
                
                // 創建簡單的成就音效
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
                oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
                oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
                
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.5);
            }
        } catch (e) {
            // 音效播放失敗不影響功能
            console.log('音效播放不支援');
        }
    }

    triggerCelebrationAnimation() {
        // 添加慶祝粒子效果
        const container = document.querySelector('#achievement-notifications');
        if (container) {
            // 創建粒子元素
            for (let i = 0; i < 20; i++) {
                const particle = document.createElement('div');
                particle.className = 'celebration-particle';
                particle.style.cssText = `
                    position: absolute;
                    width: 6px;
                    height: 6px;
                    background: linear-gradient(45deg, #ffd700, #ffed4e);
                    border-radius: 50%;
                    pointer-events: none;
                    z-index: 9999;
                    animation: celebrate 1s ease-out forwards;
                    left: 50%;
                    top: 50%;
                    transform-origin: center;
                `;
                
                // 隨機方向和距離
                const angle = (Math.PI * 2 * i) / 20;
                const distance = 50 + Math.random() * 100;
                const x = Math.cos(angle) * distance;
                const y = Math.sin(angle) * distance;
                
                particle.style.setProperty('--dx', x + 'px');
                particle.style.setProperty('--dy', y + 'px');
                
                container.appendChild(particle);
                
                // 移除粒子
                setTimeout(() => {
                    if (particle.parentNode) {
                        particle.parentNode.removeChild(particle);
                    }
                }, 1000);
            }
        }
    }
}

// 當DOM載入完成後初始化成就管理器
document.addEventListener('DOMContentLoaded', () => {
    window.achievementManager = new AchievementManager();
});

// 為全局使用導出
window.AchievementManager = AchievementManager;
