/**
 * 全域成就處理器
 * 在所有頁面中監聽和處理成就通知
 */

(function() {
    'use strict';

    /**
     * 全域成就處理器類
     */
    class GlobalAchievementHandler {
        constructor() {
            this.isInitialized = false;
            this.init();
        }

        /**
         * 初始化處理器
         */
        init() {
            if (this.isInitialized) return;
            
            // 確保DOM載入完成
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.setupGlobalHandler();
                });
            } else {
                this.setupGlobalHandler();
            }
            
            this.isInitialized = true;
        }

        /**
         * 設置全域處理器
         */
        setupGlobalHandler() {
            // 攔截所有fetch請求，檢查成就
            this.interceptFetchRequests();
            
            // 攔截所有XMLHttpRequest，檢查成就
            this.interceptXHRRequests();
            
            // 創建輕量級通知容器（如果成就頁面的通知管理器不存在）
            this.createLightweightNotificationSystem();
        }        /**
         * 攔截fetch請求
         */        interceptFetchRequests() {
            const originalFetch = window.fetch;
            
            window.fetch = async function(...args) {
                try {
                    const response = await originalFetch.apply(this, args);
                    
                    // 只處理成功的請求
                    if (response.ok) {
                        // 複製response以便多次讀取
                        const clonedResponse = response.clone();
                        
                        try {
                            const data = await clonedResponse.json();
                            if (window.globalAchievementHandler) {
                                window.globalAchievementHandler.checkForAchievements(data);
                            }
                        } catch (e) {
                            // 非JSON回應或解析失敗，忽略
                            console.debug('無法解析回應為JSON，跳過成就檢查');
                        }
                    } else {
                        console.warn(`API 請求失敗: ${response.status} ${response.statusText}`);
                    }
                    
                    return response;
                } catch (error) {
                    // 網路錯誤或其他fetch相關錯誤，記錄但不重新拋出錯誤影響原始請求
                    console.warn('Fetch 請求遇到網路錯誤，跳過成就檢查:', error.message);
                    
                    // 重新拋出原始錯誤，讓呼叫者能正確處理
                    throw error;
                }
            };
        }

        /**
         * 攔截XMLHttpRequest
         */
        interceptXHRRequests() {
            const originalOpen = XMLHttpRequest.prototype.open;
            const originalSend = XMLHttpRequest.prototype.send;
            
            XMLHttpRequest.prototype.open = function(method, url, ...args) {
                this._url = url;
                return originalOpen.apply(this, [method, url, ...args]);
            };
            
            XMLHttpRequest.prototype.send = function(...args) {
                this.addEventListener('load', function() {
                    if (this.status >= 200 && this.status < 300) {
                        try {
                            const data = JSON.parse(this.responseText);
                            window.globalAchievementHandler.checkForAchievements(data);
                        } catch (e) {
                            // 非JSON回應，忽略
                        }
                    }
                });
                
                return originalSend.apply(this, args);
            };
        }

        /**
         * 檢查回應中是否包含新成就
         */
        checkForAchievements(data) {
            if (!data || typeof data !== 'object') return;
            
            // 檢查各種可能的成就欄位
            const achievements = data.new_achievements || data.achievements || data.triggered_achievements;
            
            if (achievements && Array.isArray(achievements) && achievements.length > 0) {
                console.log('檢測到新成就:', achievements);
                this.handleNewAchievements(achievements);
            }
        }

        /**
         * 處理新成就
         */
        handleNewAchievements(achievements) {
            achievements.forEach(achievement => {
                // 如果存在專用的成就通知管理器，使用它
                if (window.achievementNotificationManager) {
                    window.achievementNotificationManager.showAchievementNotification(achievement);
                } 
                // 如果存在全域成就通知函數，使用它
                else if (window.showAchievementNotification) {
                    window.showAchievementNotification(achievement);
                }
                // 否則使用輕量級通知
                else {
                    this.showLightweightNotification(achievement);
                }
                
                // 觸發自定義事件
                window.dispatchEvent(new CustomEvent('achievement-unlocked', {
                    detail: achievement
                }));
            });
        }

        /**
         * 創建輕量級通知系統
         */
        createLightweightNotificationSystem() {
            if (document.querySelector('#lightweight-achievement-toast')) return;
            
            const toastContainer = document.createElement('div');
            toastContainer.id = 'lightweight-achievement-toast';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                pointer-events: none;
            `;
            
            document.body.appendChild(toastContainer);
        }

        /**
         * 顯示輕量級成就通知
         */
        showLightweightNotification(achievement) {
            const container = document.querySelector('#lightweight-achievement-toast');
            if (!container) return;
            
            const toast = document.createElement('div');
            toast.style.cssText = `
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 10px;
                margin-bottom: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                transform: translateX(100%);
                transition: transform 0.3s ease;
                pointer-events: auto;
                cursor: pointer;
                max-width: 300px;
            `;
            
            toast.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="font-size: 1.5rem;">🏆</div>
                    <div>
                        <div style="font-weight: bold; font-size: 0.9rem;">成就解鎖！</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">${achievement.achievement_name || achievement.name || '未知成就'}</div>
                        <div style="font-size: 0.75rem; color: #ffd700; margin-top: 0.2rem;">
                            ⭐ +${achievement.reward_points || 0} 點
                        </div>
                    </div>
                </div>
            `;
            
            container.appendChild(toast);
            
            // 顯示動畫
            setTimeout(() => {
                toast.style.transform = 'translateX(0)';
            }, 100);
            
            // 點擊關閉
            toast.addEventListener('click', () => {
                this.removeLightweightNotification(toast);
            });
            
            // 自動關閉
            setTimeout(() => {
                this.removeLightweightNotification(toast);
            }, 5000);
            
            // 播放簡單音效
            this.playSimpleNotificationSound();
        }

        /**
         * 移除輕量級通知
         */
        removeLightweightNotification(toast) {
            if (!toast || !toast.parentNode) return;
            
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }

        /**
         * 播放簡單通知音效
         */
        playSimpleNotificationSound() {
            try {
                // 使用Web Audio API創建簡單音效
                if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
                    const audioContext = new (AudioContext || webkitAudioContext)();
                    const oscillator = audioContext.createOscillator();
                    const gainNode = audioContext.createGain();
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);
                    
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.1);
                    
                    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
                    
                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + 0.3);
                }
            } catch (e) {
                // 音效播放失敗不影響功能
            }
        }

        /**
         * 手動檢查成就
         */
        static checkAchievements(userId) {
            if (!userId) return;
            
            fetch('/achievement/api/user_achievements')
                .then(response => response.json())
                .then(data => {
                    window.globalAchievementHandler.checkForAchievements(data);
                })
                .catch(error => {
                    console.log('檢查成就失敗:', error);
                });
        }
    }

    // 創建全域實例
    window.globalAchievementHandler = new GlobalAchievementHandler();
    
    // 暴露靜態方法
    window.checkAchievements = GlobalAchievementHandler.checkAchievements;

})();
