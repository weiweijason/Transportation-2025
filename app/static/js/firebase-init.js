// Firebase 初始化和配置
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getDatabase } from "firebase/database";

// Firebase 配置
const firebaseConfig = {
  apiKey: "AIzaSyAqq3F7OEPKyTR_gUXc6uxp_baxdFOxu8o",
  authDomain: "testbus-bde50.firebaseapp.com",
  projectId: "testbus-bde50",
  storageBucket: "testbus-bde50.firebasestorage.app",
  messagingSenderId: "385100269076",
  appId: "1:385100269076:web:93363a42b8c99dbb304901",
  measurementId: "G-F5T77MGW62",
  databaseURL: "https://testbus-bde50-default-rtdb.firebaseio.com" // 添加您的databaseURL
};

// 初始化 Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const database = getDatabase(app);

// 導出 Firebase 服務以供其他文件使用
export { app, analytics, auth, database };