/**
 * UI效果相關函數模組
 * 處理各種視覺效果和動畫
 */

// 閃光動畫
function animateSparkles() {
  const sparkles = document.querySelectorAll('.catch-sparkle');
  sparkles.forEach(sparkle => {
    // 重置動畫
    sparkle.style.animation = 'none';
    sparkle.offsetHeight; // 觸發重排
    
    // 隨機位置
    const top = 10 + Math.random() * 80;
    const left = 10 + Math.random() * 80;
    sparkle.style.top = `${top}%`;
    sparkle.style.left = `${left}%`;
    
    // 隨機大小
    const size = 10 + Math.random() * 20;
    sparkle.style.width = `${size}px`;
    sparkle.style.height = `${size}px`;
    
    // 隨機動畫
    const duration = 1 + Math.random() * 2;
    const delay = Math.random() * 0.5;
    sparkle.style.animation = `float ${duration}s ease-in-out ${delay}s infinite alternate`;
  });
}