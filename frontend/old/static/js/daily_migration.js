/**
 * 每日簽到系統 JavaScript
 * 處理每日簽到、獎勵發放和成就觸發
 */

class DailyMigration {
    constructor() {
        this.migrationData = null;
        this.initializeElements();
        this.bindEvents();
        this.loadMigrationStatus();
    }

    initializeElements() {
        this.elements = {
            statusBadge: document.getElementById('migration-status-badge'),
            migrationBtn: document.getElementById('migration-btn'),
            migrationTitle: document.getElementById('migration-title'),
            migrationSubtitle: document.getElementById('migration-subtitle'),
            rewardsPreview: document.getElementById('rewards-preview'),
            totalMigrations: document.getElementById('total-migrations'),
            consecutiveDays: document.getElementById('consecutive-days'),
            totalExperience: document.getElementById('total-experience'),
            consecutiveProgressBar: document.getElementById('consecutive-progress-bar'),
            nextMilestone: document.getElementById('next-milestone'),
            achievementReminder: document.getElementById('achievement-reminder'),
            upcomingAchievement: document.getElementById('upcoming-achievement'),
            historyCalendar: document.getElementById('history-calendar'),
            rewardsDisplay: document.getElementById('rewards-display')
        };
    }

    bindEvents() {
        this.elements.migrationBtn.addEventListener('click', () => this.performMigration());
        
        // 監聽成就觸發事件
        window.addEventListener('achievementTriggered', (event) => {
            this.showAchievementModal(event.detail);
        });
    }    async loadMigrationStatus() {
        try {
            this.showLoading();
            
            const response = await fetch('/daily-migration/api/get-migration-status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            if (data.success) {
                this.migrationData = data.migration_data;
                this.updateUI();
                this.loadMigrationHistory();
            } else {
                throw new Error(data.message || '獲取簽到狀態失敗');
            }
        } catch (error) {
            console.error('載入簽到狀態失敗:', error);
            let errorMessage = '載入失敗，請重新整理頁面';
            
            if (error.message.includes('Failed to fetch')) {
                errorMessage = '網路連接失敗，請檢查網路連接或重新整理頁面';
            } else if (error.message.includes('HTTP')) {
                errorMessage = '伺服器回應錯誤，請重新整理頁面';
            }
            
            this.showError(errorMessage);
        }
    }

    updateUI() {
        if (!this.migrationData) return;

        // 更新狀態徽章
        this.updateStatusBadge();
        
        // 更新遷移按鈕和文字
        this.updateMigrationButton();
        
        // 更新統計數據
        this.updateStats();
        
        // 更新獎勵預覽
        this.updateRewardsPreview();
        
        // 檢查即將解鎖的成就
        this.checkUpcomingAchievements();
    }

    updateStatusBadge() {
        const { statusBadge } = this.elements;
        const { has_migrated_today } = this.migrationData;

        statusBadge.className = 'migration-status-badge';
          if (has_migrated_today) {
            statusBadge.classList.add('completed');
            statusBadge.innerHTML = '<i class="fas fa-check"></i> <span>今日已完成</span>';
        } else {
            statusBadge.classList.add('available');
            statusBadge.innerHTML = '<i class="fas fa-exclamation"></i> <span>等待簽到</span>';
        }
    }

    updateMigrationButton() {
        const { migrationBtn, migrationTitle, migrationSubtitle } = this.elements;
        const { has_migrated_today, consecutive_days } = this.migrationData;        if (has_migrated_today) {
            migrationBtn.disabled = true;
            migrationBtn.innerHTML = '<i class="fas fa-check me-2"></i><span>今日已完成</span>';
            migrationTitle.textContent = '今日簽到已完成';
            migrationSubtitle.textContent = '明天再來獲取新的獎勵！';
        } else {
            migrationBtn.disabled = false;
            migrationBtn.innerHTML = '<i class="fas fa-rocket me-2"></i><span>開始簽到</span>';
            migrationTitle.textContent = '準備開始新的一天';
            
            if (consecutive_days > 0) {
                migrationSubtitle.textContent = `連續第 ${consecutive_days + 1} 天的冒險`;
            } else {
                migrationSubtitle.textContent = '每天都是全新的冒險開始';
            }
        }
    }

    updateStats() {
        const { totalMigrations, consecutiveDays, totalExperience, consecutiveProgressBar, nextMilestone } = this.elements;
        const { total_migrations, consecutive_days } = this.migrationData;

        totalMigrations.textContent = total_migrations;
        consecutiveDays.textContent = consecutive_days;
        
        // 計算累計經驗（簡化計算）
        const estimatedExp = total_migrations * 50;
        totalExperience.textContent = estimatedExp.toLocaleString();

        // 更新連續獎勵進度條
        const milestones = [7, 14, 30, 60, 100];
        const nextMilestoneValue = milestones.find(m => m > consecutive_days) || 100;
        const prevMilestone = milestones.filter(m => m <= consecutive_days).pop() || 0;
        
        const progress = ((consecutive_days - prevMilestone) / (nextMilestoneValue - prevMilestone)) * 100;
        consecutiveProgressBar.style.width = `${Math.min(progress, 100)}%`;
        nextMilestone.textContent = `${nextMilestoneValue}天`;
    }

    updateRewardsPreview() {
        const { consecutive_days } = this.migrationData;
        const consecutiveBonus = document.querySelector('.consecutive-bonus');
        
        if (consecutive_days >= 1) {
            consecutiveBonus.style.display = 'flex';
            const multiplier = Math.min(1 + (consecutive_days * 0.1), 3.0);
            consecutiveBonus.innerHTML = `
                <i class="fas fa-fire text-danger"></i>
                <span>連續獎勵 x${multiplier.toFixed(1)}</span>
            `;
        } else {
            consecutiveBonus.style.display = 'none';
        }
    }

    checkUpcomingAchievements() {
        const { achievementReminder, upcomingAchievement } = this.elements;
        const { total_migrations } = this.migrationData;

        const achievements = [
            { threshold: 1, name: '感謝每一次相遇', id: 'ACH-LOGIN-001' },
            { threshold: 7, name: '感恩每一段緣分', id: 'ACH-LOGIN-002' },
            { threshold: 30, name: '珍惜旅途的風景', id: 'ACH-LOGIN-003' },
            { threshold: 60, name: '期待每一個明天', id: 'ACH-LOGIN-004' },
            { threshold: 100, name: '阿偉你麼還在打電動？', id: 'ACH-LOGIN-005' }
        ];

        const upcomingAch = achievements.find(ach => ach.threshold > total_migrations);
        
        if (upcomingAch) {
            const remaining = upcomingAch.threshold - total_migrations;
            achievementReminder.style.display = 'block';
            upcomingAchievement.innerHTML = `
                <strong>${upcomingAch.name}</strong><br>
                <small>還需要 ${remaining} 天</small>
            `;
        } else {
            achievementReminder.style.display = 'none';
        }
    }

    async loadMigrationHistory() {
        try {
            const response = await fetch('/daily-migration/api/get-migration-history');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            if (data.success) {
                this.renderHistoryCalendar(data.history);
            }
        } catch (error) {
            console.error('載入遷移歷史失敗:', error);
        }
    }

    renderHistoryCalendar(history) {
        const { historyCalendar } = this.elements;
        const today = new Date();
        const calendar = [];

        // 生成最近30天的日期
        for (let i = 29; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            
            const migration = history.find(h => h.date === dateStr);
            const isToday = i === 0;
            
            calendar.push({
                date: dateStr,
                day: date.getDate(),
                migrated: !!migration,
                isToday,
                experience: migration ? migration.experience : 0,
                items: migration ? migration.items : []
            });
        }

        historyCalendar.innerHTML = calendar.map(day => {
            let className = 'calendar-day';
            if (day.isToday) className += ' today';
            else if (day.migrated) className += ' migrated';
            else className += ' empty';

            return `
                <div class="${className}" 
                     title="${day.migrated ? `${day.date} - 獲得 ${day.experience} 經驗值` : day.date}"
                     data-date="${day.date}">
                    ${day.day}
                </div>
            `;
        }).join('');
    }    async performMigration() {
        if (this.migrationData?.has_migrated_today) {
            this.showWarning('今天已經完成簽到了！');
            return;
        }

        try {
            this.elements.migrationBtn.disabled = true;
            this.elements.migrationBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i><span>簽到中...</span>';

            const response = await fetch('/daily-migration/api/perform-migration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
              if (data.success) {
                // 顯示成功動畫
                this.showMigrationSuccess(data);
                
                // 檢查成就觸發 - 確保成就數據存在
                console.log('簽到成功響應數據:', data);
                console.log('觸發的成就數據:', data.triggered_achievements);
                
                if (data.triggered_achievements && Array.isArray(data.triggered_achievements) && data.triggered_achievements.length > 0) {
                    console.log('檢測到觸發的成就，數量:', data.triggered_achievements.length);
                    setTimeout(() => {
                        data.triggered_achievements.forEach((achievement, index) => {
                            console.log(`顯示第 ${index + 1} 個成就:`, achievement);
                            setTimeout(() => {
                                this.showAchievementModal(achievement);
                                // 同時觸發全局成就事件
                                window.dispatchEvent(new CustomEvent('achievementTriggered', {
                                    detail: achievement
                                }));
                            }, index * 2000);
                        });
                    }, 2000);
                } else {
                    console.log('沒有觸發新成就或成就數據格式不正確');
                }
                
                // 重新載入狀態
                setTimeout(() => {
                    this.loadMigrationStatus();
                }, 3000);
                
            } else {
                throw new Error(data.message || '簽到失敗');
            }} catch (error) {
            console.error('簽到失敗:', error);
            let errorMessage = '簽到過程中發生錯誤';
            
            if (error.message.includes('Failed to fetch')) {
                errorMessage = '網路連接失敗，請檢查網路連接或稍後再試';
            } else if (error.message.includes('HTTP')) {
                errorMessage = '伺服器回應錯誤，請稍後再試';
            } else {
                errorMessage = error.message || '簽到過程中發生錯誤';
            }
            
            this.showError(errorMessage);
            this.elements.migrationBtn.disabled = false;
            this.elements.migrationBtn.innerHTML = '<i class="fas fa-rocket me-2"></i><span>開始簽到</span>';
        }
    }

    showMigrationSuccess(data) {
        const { rewardsDisplay } = this.elements;
        const { rewards } = data;

        // 更新獎勵顯示
        let rewardsHtml = `
            <div class="reward-showcase">
                <i class="fas fa-star me-2"></i>經驗值 +${rewards.experience}
            </div>
        `;

        rewards.items.forEach(item => {
            rewardsHtml += `
                <div class="reward-showcase">
                    <i class="fas fa-gift me-2"></i>${item.name} x${item.quantity}
                </div>
            `;
        });

        if (rewards.consecutive_days > 0) {
            rewardsHtml += `
                <div class="reward-showcase">
                    <i class="fas fa-fire me-2"></i>連續獎勵 x${rewards.bonus_multiplier.toFixed(1)}
                </div>
            `;
        }

        rewardsDisplay.innerHTML = rewardsHtml;

        // 顯示成功彈窗
        const modal = new bootstrap.Modal(document.getElementById('migrationSuccessModal'));
        modal.show();
    }    showAchievementModal(achievement) {
        // 設置成就名稱和描述
        document.getElementById('achievement-name').textContent = achievement.name || '未知成就';
        document.getElementById('achievement-description').textContent = 
            achievement.description || `恭喜獲得「${achievement.name || '未知成就'}」成就！`;
        
        // 如果有圖標信息，更新圖標
        const achievementIcon = document.querySelector('#achievementModal .achievement-icon');
        if (achievementIcon && achievement.icon) {
            achievementIcon.className = `${achievement.icon} achievement-icon`;
        }
        
        // 顯示成就彈窗
        const modal = new bootstrap.Modal(document.getElementById('achievementModal'));
        modal.show();

        // 觸發全域成就檢查
        if (window.globalAchievementHandler) {
            window.globalAchievementHandler.handleNewAchievements([achievement]);
        }
        
        // 記錄成就觸發事件
        console.log('觸發成就:', achievement);
    }

    showLoading() {
        this.elements.statusBadge.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>載入中...</span>';
        this.elements.migrationBtn.disabled = true;
        this.elements.migrationBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i><span>載入中...</span>';
    }

    showError(message) {
        console.error('每日遷移錯誤:', message);
        
        // 顯示錯誤提示
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.daily-migration-container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // 3秒後自動關閉
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }

    showWarning(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-warning alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.daily-migration-container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    // 檢查是否在每日遷移頁面
    if (document.querySelector('.daily-migration-container')) {
        new DailyMigration();
    }
});

// 全域函數供其他腳本調用
window.DailyMigration = DailyMigration;
