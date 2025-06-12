// Visitor Fight JavaScript Module
class VisitorFight {
    constructor(config) {
        this.roomId = config.roomId;
        this.userRole = config.userRole; // 'host' 或 'visitor'
        this.statusCheckInterval = null;
        this.currentRoomData = null;
        this.countdownTimer = null;
        
        // URL endpoints from Flask config
        this.urls = config.urls;
    }

    // 頁面載入時開始檢查房間狀態
    init() {
        console.log('頁面載入，房間ID:', this.roomId, '用戶角色:', this.userRole);
        this.loadRoomInfo();
        this.startStatusCheck();
    }

    loadRoomInfo() {
        fetch(this.urls.roomStatus.replace('ROOM_ID', this.roomId))
            .then(response => response.json())
            .then(data => {
                if (data.success && data.room_data) {
                    this.currentRoomData = data.room_data;
                    this.updateRoomDisplay(data.room_data);
                } else {
                    this.showStatus('房間不存在或已過期', 'danger');
                }
            })
            .catch(error => {
                console.error('Error loading room info:', error);
                this.showStatus('載入房間信息失敗', 'danger');
            });
    }

    updateRoomDisplay(roomData) {        // 更新房主精靈顯示
        if (roomData.host_creature) {
            document.getElementById('host-creature-display').innerHTML = `
                <img src="${roomData.host_creature.image_url}" alt="${roomData.host_creature.name}">
                <div class="mt-2"><strong>${roomData.host_creature.name}</strong></div>
                <small class="text-muted">${roomData.host_creature.element || roomData.host_creature.type || 'Normal'} | ATK: ${roomData.host_creature.attack || roomData.host_creature.power || 100} | HP: ${roomData.host_creature.hp || 1000}</small>
            `;
        }
        
        // 更新訪客精靈顯示（自己的精靈）
        if (roomData.visitor_creature) {
            document.getElementById('visitor-creature-display').innerHTML = `
                <img src="${roomData.visitor_creature.image_url}" alt="${roomData.visitor_creature.name}">
                <div class="mt-2"><strong>${roomData.visitor_creature.name}</strong></div>
                <small class="text-muted">${roomData.visitor_creature.element || roomData.visitor_creature.type || 'Normal'} | ATK: ${roomData.visitor_creature.attack || roomData.visitor_creature.power || 100} | HP: ${roomData.visitor_creature.hp || 1000}</small>
            `;
        }
        
        // 根據房間狀態更新界面
        this.updateStatusByRoomState(roomData.status, roomData);
    }

    updateStatusByRoomState(status, roomData) {
        switch(status) {
            case 'waiting':
                if (this.userRole === 'host') {
                    this.showStatus('等待對手加入房間...', 'info');
                } else {
                    this.showStatus('已成功加入房間，等待房主開始戰鬥...', 'info');
                }
                break;
                
            case 'ready':
                if (this.userRole === 'host') {
                    this.showStatus('對手已加入！可以開始戰鬥了', 'success');
                    // 顯示開始戰鬥按鈕
                    document.getElementById('action-buttons').innerHTML = `
                        <button class="btn btn-success btn-lg me-2" onclick="visitorFight.startBattle()">
                            <i class="fas fa-fist-raised me-2"></i>開始戰鬥
                        </button>
                        <button class="btn btn-outline-secondary" onclick="visitorFight.goBackWithCleanup()">
                            <i class="fas fa-arrow-left me-2"></i>返回
                        </button>
                    `;
                } else {
                    this.showStatus('雙方都已準備好！等待房主開始戰鬥...', 'warning');
                }
                break;
                
            case 'fighting':
                this.showStatus('戰鬥進行中...', 'primary');
                // 添加戰鬥動畫
                document.querySelectorAll('.arena-slot').forEach(slot => {
                    slot.classList.add('battle-animation');
                });
                break;
                
            case 'finished':
                clearInterval(this.statusCheckInterval);
                this.showBattleResult(roomData.battle_result);
                break;
                
            default:
                this.showStatus('房間狀態未知', 'secondary');
        }
    }

    startStatusCheck() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
        
        this.statusCheckInterval = setInterval(() => {
            if (this.roomId) {
                this.checkRoomStatus();
            }
        }, 2000);
    }

    checkRoomStatus() {
        fetch(this.urls.roomStatus.replace('ROOM_ID', this.roomId))
            .then(response => response.json())
            .then(data => {
                if (data.success && data.room_data) {
                    this.currentRoomData = data.room_data;
                    this.updateStatusByRoomState(data.room_data.status, data.room_data);
                    
                    // 如果房間狀態有變化，更新顯示
                    if (data.room_data.host_creature || data.room_data.visitor_creature) {
                        this.updateRoomDisplay(data.room_data);
                    }
                } else {
                    this.showStatus('房間連接中斷', 'danger');
                    clearInterval(this.statusCheckInterval);
                }
            })
            .catch(error => {
                console.error('Error checking room status:', error);
            });
    }

    startBattle() {
        if (this.userRole !== 'host') {
            this.showStatus('只有房主可以開始戰鬥', 'warning');
            return;
        }
        
        this.showStatus('正在開始戰鬥...', 'info');
        
        fetch(this.urls.startBattle, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: this.roomId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showStatus('戰鬥開始！', 'primary');
                // 戰鬥結果會通過房間狀態檢查自動更新
            } else {
                this.showStatus('戰鬥開始失敗：' + (data.message || '未知錯誤'), 'danger');
            }
        })
        .catch(error => {
            console.error('Error starting battle:', error);
            this.showStatus('戰鬥開始時發生錯誤', 'danger');
        });
    }

    showBattleResult(result) {
        // 移除戰鬥動畫
        document.querySelectorAll('.arena-slot').forEach(slot => {
            slot.classList.remove('battle-animation');
        });
        
        let message = '';
        let isWinner = false;
        
        if (result.winner === 'draw') {
            message = `🤝 平局！雙方實力相當，這是一場精彩的對戰！`;
            this.showStatus(message, 'info');
        } else {
            // 判斷當前用戶是否獲勝
            // userRole: 'host' 或 'visitor'
            // result.winner: 'host' 或 'visitor'
            isWinner = (this.userRole === result.winner);
            
            if (isWinner) {
                message = `🎉 恭喜獲勝！你的 ${result.winner_name} 擊敗了對手的 ${result.loser_name}！`;
                this.showStatus(message, 'success');
            } else {
                message = `😢 很遺憾落敗！對手的 ${result.winner_name} 擊敗了你的 ${result.loser_name}。`;
                this.showStatus(message, 'danger');
            }
            
            // 添加視覺效果
            if (this.userRole === 'host') {
                if (isWinner) {
                    document.getElementById('visitor-slot').classList.add('winner-glow');
                    document.getElementById('host-slot').classList.add('loser-fade');
                } else {
                    document.getElementById('host-slot').classList.add('winner-glow');
                    document.getElementById('visitor-slot').classList.add('loser-fade');
                }
            } else {
                if (isWinner) {
                    document.getElementById('visitor-slot').classList.add('winner-glow');
                    document.getElementById('host-slot').classList.add('loser-fade');
                } else {
                    document.getElementById('host-slot').classList.add('winner-glow');
                    document.getElementById('visitor-slot').classList.add('loser-fade');
                }
            }
        }
        
        // 更新按鈕
        document.getElementById('action-buttons').innerHTML = `
            <button class="btn btn-primary me-2" onclick="visitorFight.cleanupAndRedirect('${this.urls.chooseFight}')">
                <i class="fas fa-redo me-2"></i>再來一戰
            </button>
            <button class="btn btn-success me-2" onclick="visitorFight.cleanupAndRedirect('${this.urls.home}')">
                <i class="fas fa-home me-2"></i>返回主頁
            </button>
            <div class="mt-3">
                <div class="alert alert-warning" id="countdown-alert">
                    <i class="fas fa-clock me-2"></i>
                    <span id="countdown-text">10秒後自動返回主頁並清理房間...</span>
                </div>
            </div>
        `;
        
        // 開始倒數計時
        this.startCountdown();
    }

    startCountdown() {
        let seconds = 10;
        this.countdownTimer = setInterval(() => {
            const countdownText = document.getElementById('countdown-text');
            if (countdownText) {
                countdownText.textContent = `${seconds}秒後自動返回主頁並清理房間...`;
            }
            
            seconds--;
            
            if (seconds < 0) {
                clearInterval(this.countdownTimer);
                // 自動執行清理並跳轉
                this.cleanupAndRedirect(this.urls.home);
            }
        }, 1000);
    }

    showStatus(message, type) {
        const statusDiv = document.getElementById('status-message');
        const statusText = document.getElementById('status-text');
        
        statusDiv.className = `alert alert-${type}`;
        statusText.textContent = message;
    }

    cleanupAndRedirect(url) {
        // 清除倒數計時器
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
        }
        
        // 只有房主才能刪除房間，避免重複刪除
        if (this.userRole === 'host') {
            this.deleteRoom().then(() => {
                window.location.href = url;
            }).catch(error => {
                console.error('清理房間失敗:', error);
                // 即使清理失敗也要跳轉，避免用戶卡住
                window.location.href = url;
            });
        } else {
            // 訪客直接跳轉
            window.location.href = url;
        }
    }

    deleteRoom() {
        return fetch(this.urls.deleteRoom.replace('ROOM_ID', this.roomId), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('房間已成功清理');
            } else {
                console.warn('房間清理失敗:', data.message);
            }
            return data;
        });
    }

    goBackWithCleanup() {
        // 清除倒數計時器
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
        }
        
        // 只有房主才能刪除房間
        if (this.userRole === 'host') {
            this.showStatus('正在清理房間...', 'info');
            this.deleteRoom().then(() => {
                window.location.href = this.urls.chooseFight;
            }).catch(error => {
                console.error('清理房間失敗:', error);
                // 即使清理失敗也要返回
                window.location.href = this.urls.chooseFight;
            });
        } else {
            // 訪客直接返回
            window.location.href = this.urls.chooseFight;
        }
    }

    // 頁面卸載時清理
    setupBeforeUnload() {
        window.addEventListener('beforeunload', () => {
            if (this.statusCheckInterval) {
                clearInterval(this.statusCheckInterval);
            }
            
            // 頁面離開時也嘗試清理房間（只有房主執行）
            if (this.userRole === 'host' && this.roomId) {
                // 使用 navigator.sendBeacon 進行異步清理，不阻塞頁面卸載
                const deleteUrl = this.urls.deleteRoom.replace('ROOM_ID', this.roomId);
                navigator.sendBeacon(deleteUrl);
            }
        });
    }
}

// Global instance to be used by HTML onclick handlers
let visitorFight = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // This will be set by the HTML template
    if (typeof visitorFightConfig !== 'undefined') {
        visitorFight = new VisitorFight(visitorFightConfig);
        visitorFight.init();
        visitorFight.setupBeforeUnload();
    }
});
