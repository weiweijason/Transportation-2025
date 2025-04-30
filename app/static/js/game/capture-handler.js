/**
 * 精靈捕捉處理器
 * 處理精靈捕捉相關的所有邏輯，包括身份驗證和 Firebase 資料操作
 */

// 確保在全局範圍下可用
window.CaptureHandler = (function() {
  // 私有變數
  let initialized = false;
  let db = null;
  let auth = null;
  let currentUser = null;
  
  // 初始化 Firebase 服務
  function initialize() {
    if (initialized) return true;
    
    try {
      // 檢查 Firebase 是否已經初始化
      if (!firebase || !firebase.firestore || !firebase.auth) {
        console.error('Firebase 未初始化或未載入必要服務');
        return false;
      }
      
      db = firebase.firestore();
      auth = firebase.auth();
      
      // 檢查用戶登入狀態
      currentUser = auth.currentUser;
      
      // 監聽登入狀態變化
      auth.onAuthStateChanged(function(user) {
        currentUser = user;
        console.log('用戶登入狀態變更:', user ? `已登入: ${user.email}` : '未登入');
      });
      
      initialized = true;
      return true;
    } catch (error) {
      console.error('初始化 CaptureHandler 時出錯:', error);
      return false;
    }
  }
  
  // 從 Cookie 獲取 CSRF 令牌
  function getCSRFToken() {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; csrf_token=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  
  // 檢查用戶是否已登入
  function checkUserLoggedIn() {
    if (!initialize()) {
      throw new Error('CaptureHandler 初始化失敗');
    }
    
    // 檢查 Firebase Auth 用戶
    if (currentUser) {
      console.log('用戶已通過 Firebase Auth 登入:', currentUser.email);
      return Promise.resolve(currentUser);
    }
    
    console.log('未檢測到 Firebase Auth 用戶，嘗試使用後端 Session 驗證...');
    
    // 嘗試直接向後端 API 驗證 (使用 Flask session)
    return new Promise((resolve, reject) => {
      fetch('/game/api/user/verify-auth-status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getCSRFToken() || ''
        },
        credentials: 'same-origin' // 重要：包含 cookies
      })
      .then(response => {
        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('用戶未登入');
          } else {
            throw new Error(`伺服器錯誤: ${response.status}`);
          }
        }
        return response.json();
      })
      .then(userData => {
        if (!userData || !userData.id) {
          throw new Error('獲取用戶資訊失敗');
        }
        
        console.log('從伺服器獲取到用戶資訊:', userData);
        
        // 如果未從 Firebase 登入但有效的 Flask session，嘗試 Firebase 自動登入
        tryAutoLogin(userData);
        
        return resolve(userData);
      })
      .catch(error => {
        console.error('驗證用戶狀態失敗:', error);
        // 嘗試最後的備用方案 - 檢查 cookie 中的 session 標記
        const sessionCookies = document.cookie.match(/(session=|remember_token=|user_id=|logged_in=)/);
        
        if (sessionCookies) {
          console.log('檢測到可能的 session cookies，嘗試獲取當前用戶資訊');
          
          // 嘗試獲取當前用戶資訊
          fetch('/game/api/user/get-current', {
            credentials: 'same-origin'
          })
          .then(response => {
            if (!response.ok) throw new Error('獲取用戶資訊失敗');
            return response.json();
          })
          .then(userData => {
            if (!userData || !userData.id) {
              throw new Error('獲取用戶資訊失敗');
            }
            
            console.log('後備方法獲取到用戶資訊:', userData);
            return resolve(userData);
          })
          .catch(err => {
            console.error('後備獲取用戶資訊失敗:', err);
            return reject(new Error('請先登入再進行捕捉操作'));
          });
        } else {
          return reject(new Error('請先登入再進行捕捉操作'));
        }
      });
    });
  }
  
  // 嘗試自動登入 Firebase (僅在有效的 Flask session 但 Firebase 未登入時)
  function tryAutoLogin(userData) {
    if (!userData || !userData.id || currentUser) return;
    
    console.log('嘗試自動登入 Firebase...');
    
    // 使用自定義令牌登入 (如果後端支援)
    fetch('/auth/get-custom-token', {
      method: 'GET',
      credentials: 'same-origin'
    })
    .then(response => {
      if (!response.ok) throw new Error('獲取自定義令牌失敗');
      return response.json();
    })
    .then(data => {
      if (!data.token) throw new Error('令牌為空');
      
      // 使用自定義令牌登入 Firebase
      return firebase.auth().signInWithCustomToken(data.token);
    })
    .then(userCredential => {
      console.log('成功自動登入 Firebase:', userCredential.user.email);
    })
    .catch(error => {
      console.warn('自動登入 Firebase 失敗 (非致命錯誤):', error);
    });
  }
  
  // 捕捉精靈的主要函數
  async function captureCreature(creatureId) {
    try {
      // 檢查用戶是否已登入
      const user = await checkUserLoggedIn();
      const userId = user.uid || user.id; // 支持 Firebase 用戶對象和自定義對象
      
      if (!userId) {
        throw new Error('無法獲取用戶 ID');
      }
      
      console.log(`嘗試捕捉精靈 ID: ${creatureId}, 用戶 ID: ${userId}`);
      
      // 優先使用後端 API 捕捉精靈 (避免權限問題)
      console.log('優先使用後端 API 捕捉精靈...');
      
      return new Promise((resolve, reject) => {
        fetch('/game/api/capture-interactive', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': getCSRFToken() || ''
          },
          credentials: 'same-origin',
          body: JSON.stringify({ creatureId: creatureId })
        })
        .then(response => {
          if (!response.ok) {
            // 嘗試解析錯誤訊息
            return response.json().then(errorData => {
              // 如果響應包含錯誤訊息，使用它
              throw new Error(errorData.message || `捕捉請求失敗: ${response.status}`);
            }).catch(() => {
              // 如果不能解析 JSON，使用通用錯誤訊息
              throw new Error(`捕捉請求失敗: ${response.status}`);
            });
          }
          return response.json();
        })
        .then(result => {
          console.log('後端捕捉結果:', result);
          // 即使後端返回 success: false，也不拋出錯誤，讓調用者處理
          resolve(result);
        })
        .catch(error => {
          console.error('後端捕捉錯誤:', error);
          
          // 僅在開發環境嘗試 Firebase 直接捕捉 (取消這種降級)
          /*
          console.log('後端 API 捕捉失敗，嘗試使用 Firebase 直接捕捉...');
          
          if (currentUser) {
            // 如果此時已有 Firebase 用戶，嘗試使用 Firebase 直接捕捉
            captureCreatureWithFirebase(creatureId, currentUser.uid)
              .then(result => resolve(result))
              .catch(firebaseError => {
                console.error('Firebase 捕捉失敗:', firebaseError);
                reject(error); // 仍然返回原始錯誤
              });
          } else {
            reject(error);
          }
          */
          
          // 直接返回錯誤，不再嘗試 Firebase 直接捕捉
          reject(error);
        });
      });
    } catch (error) {
      console.error('捕捉過程出錯:', error);
      return { 
        success: false, 
        message: error.message || '捕捉過程中發生錯誤' 
      };
    }
  }
  
  // Firebase 直接捕捉邏輯 (僅保留作為參考，實際上不使用)
  async function captureCreatureWithFirebase(creatureId, userId) {
    try {
      console.warn('注意: Firebase 直接捕捉已被禁用，由於權限問題。使用後端 API 代替。');
      throw new Error('Firebase 直接捕捉已被禁用，由於權限問題');
      
      // 以下代碼保留但不會執行
      // 從 route_creatures 集合獲取精靈資料
      const creatureRef = db.collection('route_creatures').doc(creatureId);
      // ...existing code...
    } catch (error) {
      console.error('Firebase 捕捉過程出錯:', error);
      return { 
        success: false, 
        message: error.message || 'Firebase 捕捉過程中發生錯誤' 
      };
    }
  }
  
  // 公開 API
  return {
    initialize: initialize,
    captureCreature: captureCreature,
    checkUserLoggedIn: checkUserLoggedIn
  };
})();