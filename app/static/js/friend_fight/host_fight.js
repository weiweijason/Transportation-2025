// Host Fight JavaScript Module
class HostFight {
    constructor(config) {
        this.selectedCreatureId = null;
        this.roomId = null;
        this.statusCheckInterval = null;
        this.countdownTimer = null;
        this.currentRoomData = null;
        
        // URL endpoints from Flask config
        this.urls = config.urls;
        this.userId = config.userId;
        this.catchUrl = config.catchUrl;
    }

    openModal() {
        this.loadUserCreatures();
        new bootstrap.Modal(document.getElementById('spriteModal')).show();
    }

    loadUserCreatures() {
        fetch('/game/api/user/creatures')
            .then(response => response.json())
            .then(data => {
                const creatureList = document.getElementById('creature-list');
                creatureList.innerHTML = '';
                
                if (Array.isArray(data) && data.length > 0) {
                    data.forEach(creature => {
                        const creatureCard = this.createCreatureCard(creature);
                        creatureList.appendChild(creatureCard);
                    });
                } else if (data.error) {
                    creatureList.innerHTML = `<div class="col-12 text-center"><p class="text-danger">載入錯誤：${data.error}</p></div>`;
                } else {
                    creatureList.innerHTML = `<div class="col-12 text-center"><p class="text-muted">你還沒有捕捉到任何精靈！<br><a href="${this.catchUrl}">立即去捕捉</a></p></div>`;
                }
            })
            .catch(error => {
                console.error('Error loading creatures:', error);
                this.showStatus('載入精靈失敗', 'danger');
            });
    }

    createCreatureCard(creature) {
        const div = document.createElement('div');
        div.className = 'col-md-4 col-sm-6 mb-3';
        div.innerHTML = `
            <div class="card creature-card h-100" onclick="hostFight.selectCreature('${creature.id}', '${creature.name}', '${creature.image_url}')">
                <img src="${creature.image_url}" class="card-img-top" alt="${creature.name}" style="height: 150px; object-fit: cover;">
                <div class="card-body text-center">
                    <h6 class="card-title">${creature.name}</h6>
                    <span class="badge bg-${this.getElementColor(creature.element)}">${creature.element}</span>
                    <div class="mt-2">
                        <small class="text-muted">力量: ${creature.power}</small>
                    </div>
                </div>
            </div>
        `;
        return div;
    }

    getElementColor(element) {
        const colors = {
            '火': 'danger',
            '水': 'primary', 
            '木': 'success',
            '光': 'warning',
            '暗': 'dark'
        };
        return colors[element] || 'secondary';
    }

    selectCreature(creatureId, creatureName, imageUrl) {
        this.selectedCreatureId = creatureId;
        
        // 清除之前的選擇狀態
        document.querySelectorAll('.creature-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // 標記當前選擇
        event.currentTarget.classList.add('selected');
        
        // 更新顯示
        document.getElementById('player-slot').innerHTML = `
            <img src="${imageUrl}" alt="${creatureName}">
            <div class="mt-2"><strong>${creatureName}</strong></div>
        `;
        
        // 顯示創建按鈕
        document.getElementById('ready-button').style.display = 'inline-block';
        
        // 關閉模態窗口
        bootstrap.Modal.getInstance(document.getElementById('spriteModal')).hide();
    }

    createRoom() {
        if (!this.selectedCreatureId) {
            this.showStatus('請先選擇一個精靈', 'warning');
            return;
        }
        
        const button = document.getElementById('ready-button');
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>創建中...';
        
        fetch(this.urls.createRoom, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                creature_id: this.selectedCreatureId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.roomId = data.room_id;
                document.getElementById('room-id').textContent = this.roomId;
                document.getElementById('room-hint').textContent = '請將此ID分享給你的朋友';
                this.showStatus('房間創建成功！等待對手加入...', 'success');
                
                // 開始檢查房間狀態
                this.startStatusCheck();
                
                button.innerHTML = '<i class="fas fa-clock me-2"></i>等待對手中...';
            } else {
                this.showStatus(data.message || '創建房間失敗', 'danger');
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-check me-2"></i>創建房間並等待對手';
            }
        })
        .catch(error => {
            console.error('Error creating room:', error);
            this.showStatus('創建房間時發生錯誤', 'danger');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-check me-2"></i>創建房間並等待對手';
        });
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
                    const roomData = data.room_data;
                    const status = roomData.status;
                    
                    if (status === 'ready') {
                        clearInterval(this.statusCheckInterval);
                        this.showStatus('對手已加入！正在跳轉到對戰頁面...', 'success');
                        
                        // 跳轉到對戰頁面（房主視角）
                        setTimeout(() => {
                            window.location.href = this.urls.visitorFight.replace('ROOM_ID', this.roomId);
                        }, 1500);
                        
                    } else if (status === 'fighting') {
                        this.showStatus('戰鬥進行中...', 'warning');
                        
                    } else if (status === 'finished') {
                        clearInterval(this.statusCheckInterval);
                        if (roomData.battle_result) {
                            this.showBattleResult(roomData.battle_result);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error checking room status:', error);
            });
    }

    startBattle() {
        this.showStatus('戰鬥開始！', 'primary');
        
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
                this.showBattleResult(data.battle_result);
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
        clearInterval(this.statusCheckInterval);
        
        const isWinner = result.winner === this.userId;
        const message = isWinner ? 
            `🎉 恭喜獲勝！你的 ${result.winner_creature.name} 擊敗了對手的 ${result.loser_creature.name}！` :
            `😢 很遺憾落敗！對手的 ${result.winner_creature.name} 擊敗了你的 ${result.loser_creature.name}。`;
        
        this.showStatus(message, isWinner ? 'success' : 'danger');
        
        // 更新按鈕
        document.getElementById('ready-button').innerHTML = `
            <button class="btn btn-primary me-2" onclick="hostFight.cleanupAndRedirect('${this.urls.chooseFight}')">
                <i class="fas fa-redo me-2"></i>再來一戰
            </button>
            <button class="btn btn-success me-2" onclick="hostFight.cleanupAndRedirect('${this.urls.home}')">
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

    showStatus(message, type) {
        const statusDiv = document.getElementById('status-message');
        const statusText = document.getElementById('status-text');
        
        statusDiv.className = `alert alert-${type} mt-3`;
        statusText.textContent = message;
        statusDiv.style.display = 'block';
    }

    startCountdown() {
        let seconds = 10;
        const countdownText = document.getElementById('countdown-text');
        
        this.countdownTimer = setInterval(() => {
            seconds--;
            if (countdownText) {
                countdownText.textContent = `${seconds}秒後自動返回主頁並清理房間...`;
            }
            
            if (seconds <= 0) {
                clearInterval(this.countdownTimer);
                // 自動執行房間清理並跳轉
                this.cleanupAndRedirect(this.urls.home);
            }
        }, 1000);
    }

    cleanupAndRedirect(url) {
        // 清除倒數計時器
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
        }
        
        // 房主負責清理房間
        this.deleteRoom().then(() => {
            window.location.href = url;
        }).catch(error => {
            console.error('清理房間失敗:', error);
            // 即使清理失敗也要跳轉，避免用戶卡住
            window.location.href = url;
        });
    }

    deleteRoom() {
        if (!this.roomId) {
            return Promise.resolve();
        }
        
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
        // 如果已經創建了房間，先清理再返回
        if (this.roomId) {
            this.showStatus('正在清理房間...', 'info');
            this.deleteRoom().then(() => {
                window.location.href = this.urls.chooseFight;
            }).catch(error => {
                console.error('清理房間失敗:', error);
                // 即使清理失敗也要返回
                window.location.href = this.urls.chooseFight;
            });
        } else {
            // 沒有創建房間，直接返回
            window.location.href = this.urls.chooseFight;
        }
    }

    // 頁面卸載時清理
    setupBeforeUnload() {
        window.addEventListener('beforeunload', () => {
            if (this.statusCheckInterval) {
                clearInterval(this.statusCheckInterval);
            }
            
            // 如果房間還在等待狀態且房間ID存在，清理房間
            if (this.roomId && this.currentRoomData && this.currentRoomData.status === 'waiting') {
                // 使用 navigator.sendBeacon 進行異步清理，不阻塞頁面卸載
                const deleteUrl = this.urls.deleteRoom.replace('ROOM_ID', this.roomId);
                navigator.sendBeacon(deleteUrl);
            }
        });
    }
}

// Global instance to be used by HTML onclick handlers
let hostFight = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // This will be set by the HTML template
    if (typeof hostFightConfig !== 'undefined') {
        hostFight = new HostFight(hostFightConfig);
        hostFight.setupBeforeUnload();
    }
});
