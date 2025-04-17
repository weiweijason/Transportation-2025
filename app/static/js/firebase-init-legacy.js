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
  
  console.log("Firebase 初始化成功");
  
  // 將 Firebase 服務掛載到 window 對象以供全局使用
  window.firebaseServices = {
    app: firebase.app(),
    analytics: analytics,
    auth: auth,
    database: database
  };
});