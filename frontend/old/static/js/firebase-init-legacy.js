// Firebase 初始化和配置（非模組版本）
document.addEventListener('DOMContentLoaded', function() {
  // Firebase 配置
  const firebaseConfig = {
    apiKey: "AIzaSyAqq3F7OEPKyTR_gUXc6uxp_baxdFOxu8o",
    authDomain: "testbus-bde50.firebaseapp.com",
    projectId: "testbus-bde50",
    storageBucket: "testbus-bde50.firebasestorage.app",
    messagingSenderId: "385100269076",
    appId: "1:385100269076:web:93363a42b8c99dbb304901",
    measurementId: "G-F5T77MGW62",
    databaseURL: "https://testbus-bde50-default-rtdb.firebaseio.com"
  };

  // 初始化 Firebase
  firebase.initializeApp(firebaseConfig);
  
  // 初始化 Firebase 服務
  const analytics = firebase.analytics();
  const auth = firebase.auth();
  const database = firebase.database();
  const firestore = firebase.firestore();
  
  console.log("Firebase 初始化成功");
  
  // 顯示詳細的初始化日誌
  console.log("Firebase 服務初始化詳情:");
  console.log("- Analytics 已初始化");
  console.log("- Authentication 已初始化");
  console.log("- Realtime Database 已初始化");
  console.log("- Firestore 已初始化");
  
  // 檢查 Firestore 是否可用
  if (firestore) {
    console.log("✅ Firestore 服務初始化成功!");
    
    // 測試 Firestore 連接
    firestore.collection('test').doc('connection-test')
      .set({
        timestamp: firebase.firestore.FieldValue.serverTimestamp(),
        status: 'connected'
      })
      .then(() => {
        console.log("✅ Firestore 連接測試成功! 資料庫可正常寫入");
      })
      .catch(error => {
        console.error("❌ Firestore 連接測試失敗:", error);
      });
  } else {
    console.error("❌ Firestore 服務無法初始化!");
  }
  
  // 將 Firebase 服務掛載到 window 對象以供全局使用
  window.firebaseServices = {
    app: firebase.app(),
    analytics: analytics,
    auth: auth,
    database: database,
    firestore: firestore
  };
});