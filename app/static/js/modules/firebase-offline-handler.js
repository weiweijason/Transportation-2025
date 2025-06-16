// Firebase 離線模式處理器
// 這個模組處理 Firebase 連接失敗的情況，確保應用在離線模式下仍能正常運行

class FirebaseOfflineHandler {
    constructor() {
        this.isOffline = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.retryInterval = 5000; // 5秒
        
        this.setupOfflineDetection();
    }
    
    setupOfflineDetection() {
        // 監聽 Firebase 連接狀態
        if (typeof firebase !== 'undefined' && firebase.firestore) {
            try {
                const db = firebase.firestore();
                
                // 設置離線模式啟用
                db.enableNetwork().catch(() => {
                    console.warn('Firebase網絡已啟用或連接失敗');
                });
                
                // 監聽連接狀態變化
                firebase.firestore().onSnapshotsInSync(() => {
                    if (this.isOffline) {
                        console.log('✅ Firebase 連接已恢復');
                        this.isOffline = false;
                        this.retryCount = 0;
                        this.onConnectionRestored();
                    }
                });
                
            } catch (error) {
                console.warn('設置 Firebase 離線檢測失敗:', error.message);
                this.isOffline = true;
            }
        } else {
            console.warn('Firebase 未初始化，啟用離線模式');
            this.isOffline = true;
        }
        
        // 監聽瀏覽器在線狀態
        window.addEventListener('online', () => {
            console.log('網絡連接已恢復');
            this.attemptReconnection();
        });
        
        window.addEventListener('offline', () => {
            console.log('網絡連接已斷開');
            this.isOffline = true;
        });
    }
    
    async safeFirebaseOperation(operation, fallback = null, timeout = 5000) {
        if (this.isOffline) {
            console.warn('Firebase 離線模式，跳過操作');
            return fallback;
        }
        
        try {
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Firebase操作超時')), timeout);
            });
            
            const result = await Promise.race([operation(), timeoutPromise]);
            return result;
            
        } catch (error) {
            console.warn('Firebase 操作失敗，可能處於離線模式:', error.message);
            this.isOffline = true;
            
            if (error.message.includes('backend') || 
                error.message.includes('offline') || 
                error.message.includes('timeout') ||
                error.message.includes('網絡')) {
                this.scheduleRetry();
            }
            
            return fallback;
        }
    }
    
    scheduleRetry() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(`將在 ${this.retryInterval / 1000} 秒後嘗試重新連接 (${this.retryCount}/${this.maxRetries})`);
            
            setTimeout(() => {
                this.attemptReconnection();
            }, this.retryInterval);
        } else {
            console.warn('已達到最大重試次數，保持離線模式');
        }
    }
    
    async attemptReconnection() {
        if (!this.isOffline) return;
        
        console.log('嘗試重新連接 Firebase...');
        
        try {
            if (typeof firebase !== 'undefined' && firebase.firestore) {
                const db = firebase.firestore();
                
                // 嘗試一個簡單的讀取操作
                await this.safeFirebaseOperation(
                    () => db.collection('arenas').limit(1).get(),
                    null,
                    3000
                );
                
                console.log('✅ Firebase 重新連接成功');
                this.isOffline = false;
                this.retryCount = 0;
                this.onConnectionRestored();
                
            }
        } catch (error) {
            console.warn('Firebase 重新連接失敗:', error.message);
            this.scheduleRetry();
        }
    }
    
    onConnectionRestored() {
        // 連接恢復後的處理
        console.log('🔄 Firebase 連接已恢復，重新載入道館資料...');
        
        // 觸發道館重新載入
        if (typeof window.renderAllArenas === 'function') {
            setTimeout(() => {
                window.renderAllArenas();
            }, 1000);
        }
        
        // 顯示通知給用戶
        if (typeof window.showSuccessMessage === 'function') {
            window.showSuccessMessage('網絡連接已恢復，數據已重新載入');
        }
    }
    
    getConnectionStatus() {
        return {
            isOffline: this.isOffline,
            retryCount: this.retryCount,
            canRetry: this.retryCount < this.maxRetries
        };
    }
}

// 創建全局實例
window.firebaseOfflineHandler = new FirebaseOfflineHandler();

// 為其他模組提供安全的 Firebase 操作包裝器
window.safeFirebaseOperation = (operation, fallback = null, timeout = 5000) => {
    return window.firebaseOfflineHandler.safeFirebaseOperation(operation, fallback, timeout);
};

// 導出以供其他模組使用
export { FirebaseOfflineHandler };
export default window.firebaseOfflineHandler;
