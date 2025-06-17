// 兌換商店JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // 初始化
    init();
    
    function init() {
        // 隱藏載入覆蓋層
        setTimeout(() => {
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.style.opacity = '0';
                setTimeout(() => {
                    loadingOverlay.style.display = 'none';
                }, 300);
            }
        }, 1000);
        
        // 載入兌換數據
        loadExchangeData();
        
        // 綁定事件
        bindEvents();
    }
    
    function bindEvents() {
        // 藥水兌換按鈕
        const exchangePotionBtn = document.getElementById('exchangePotionBtn');
        if (exchangePotionBtn) {
            exchangePotionBtn.addEventListener('click', exchangePotionFragments);
        }
        
        // 進階魔法陣兌換按鈕
        const exchangeAdvancedBtn = document.getElementById('exchangeAdvancedBtn');
        if (exchangeAdvancedBtn) {
            exchangeAdvancedBtn.addEventListener('click', () => exchangeMagicCircles('normal_to_advanced'));
        }
        
        // 高級魔法陣兌換按鈕
        const exchangeLegendaryBtn = document.getElementById('exchangeLegendaryBtn');
        if (exchangeLegendaryBtn) {
            exchangeLegendaryBtn.addEventListener('click', () => exchangeMagicCircles('advanced_to_legendary'));
        }
    }
    
    function loadExchangeData() {
        fetch('/exchange-shop/api/get-exchange-data', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateUI(data.exchange_data);
            } else {
                showError(data.message || '載入數據失敗');
            }
        })
        .catch(error => {
            console.error('載入數據錯誤:', error);
            showError('網路連接失敗，請稍後再試');
        });
    }
    
    function updateUI(exchangeData) {
        // 更新藥水碎片和藥水數量
        updateElement('potionFragmentsCount', exchangeData.normal_potion_fragments || 0);
        updateElement('normalPotionsCount', exchangeData.normal_potions || 0);
        
        // 更新魔法陣數量
        updateElement('normalMagicCount', exchangeData.magic_circle_normal || 0);
        updateElement('advancedMagicCount', exchangeData.magic_circle_advanced || 0);
        updateElement('advancedMagicCount2', exchangeData.magic_circle_advanced || 0);
        updateElement('legendaryMagicCount', exchangeData.magic_circle_legendary || 0);
        
        // 更新按鈕狀態
        updateButtonStates(exchangeData);
    }
    
    function updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            
            // 添加數字變化動畫
            element.style.transform = 'scale(1.1)';
            element.style.color = '#ff6b9d';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
                element.style.color = '';
            }, 200);
        }
    }
    
    function updateButtonStates(exchangeData) {
        // 藥水兌換按鈕
        const exchangePotionBtn = document.getElementById('exchangePotionBtn');
        const potionExchangeHint = document.getElementById('potionExchangeHint');
        const fragments = exchangeData.normal_potion_fragments || 0;
        
        if (exchangePotionBtn && potionExchangeHint) {
            if (fragments >= 7) {
                exchangePotionBtn.disabled = false;
                const canExchange = Math.floor(fragments / 7);
                potionExchangeHint.textContent = `可兌換 ${canExchange} 瓶藥水`;
                potionExchangeHint.style.color = '#4facfe';
            } else {
                exchangePotionBtn.disabled = true;
                potionExchangeHint.textContent = `還需要 ${7 - fragments} 個碎片`;
                potionExchangeHint.style.color = 'rgba(255, 255, 255, 0.6)';
            }
        }
        
        // 進階魔法陣兌換按鈕
        const exchangeAdvancedBtn = document.getElementById('exchangeAdvancedBtn');
        const advancedExchangeHint = document.getElementById('advancedExchangeHint');
        const normalMagic = exchangeData.magic_circle_normal || 0;
        
        if (exchangeAdvancedBtn && advancedExchangeHint) {
            if (normalMagic >= 10) {
                exchangeAdvancedBtn.disabled = false;
                const canExchange = Math.floor(normalMagic / 10);
                advancedExchangeHint.textContent = `可兌換 ${canExchange} 個進階魔法陣`;
                advancedExchangeHint.style.color = '#4facfe';
            } else {
                exchangeAdvancedBtn.disabled = true;
                advancedExchangeHint.textContent = `還需要 ${10 - normalMagic} 個普通魔法陣`;
                advancedExchangeHint.style.color = 'rgba(255, 255, 255, 0.6)';
            }
        }
        
        // 高級魔法陣兌換按鈕
        const exchangeLegendaryBtn = document.getElementById('exchangeLegendaryBtn');
        const legendaryExchangeHint = document.getElementById('legendaryExchangeHint');
        const advancedMagic = exchangeData.magic_circle_advanced || 0;
        
        if (exchangeLegendaryBtn && legendaryExchangeHint) {
            if (advancedMagic >= 10) {
                exchangeLegendaryBtn.disabled = false;
                const canExchange = Math.floor(advancedMagic / 10);
                legendaryExchangeHint.textContent = `可兌換 ${canExchange} 個高級魔法陣`;
                legendaryExchangeHint.style.color = '#4facfe';
            } else {
                exchangeLegendaryBtn.disabled = true;
                legendaryExchangeHint.textContent = `還需要 ${10 - advancedMagic} 個進階魔法陣`;
                legendaryExchangeHint.style.color = 'rgba(255, 255, 255, 0.6)';
            }
        }
    }
    
    function exchangePotionFragments() {
        const button = document.getElementById('exchangePotionBtn');
        if (button.disabled) return;
        
        // 禁用按鈕防止重複點擊
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 兌換中...';
        
        fetch('/exchange-shop/api/exchange-potion-fragments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess(data.message);
                // 重新載入數據
                setTimeout(() => {
                    loadExchangeData();
                }, 1500);
            } else {
                showError(data.message || '兌換失敗');
            }
        })
        .catch(error => {
            console.error('兌換錯誤:', error);
            showError('網路連接失敗，請稍後再試');
        })
        .finally(() => {
            // 恢復按鈕
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-magic"></i> <span>兌換藥水</span>';
                loadExchangeData(); // 重新檢查按鈕狀態
            }, 1000);
        });
    }
    
    function exchangeMagicCircles(exchangeType) {
        const buttonId = exchangeType === 'normal_to_advanced' ? 'exchangeAdvancedBtn' : 'exchangeLegendaryBtn';
        const button = document.getElementById(buttonId);
        if (button.disabled) return;
        
        // 禁用按鈕防止重複點擊
        button.disabled = true;
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 兌換中...';
        
        fetch('/exchange-shop/api/exchange-magic-circles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                exchange_type: exchangeType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess(data.message);
                // 重新載入數據
                setTimeout(() => {
                    loadExchangeData();
                }, 1500);
            } else {
                showError(data.message || '兌換失敗');
            }
        })
        .catch(error => {
            console.error('兌換錯誤:', error);
            showError('網路連接失敗，請稍後再試');
        })
        .finally(() => {
            // 恢復按鈕
            setTimeout(() => {
                button.innerHTML = originalHTML;
                loadExchangeData(); // 重新檢查按鈕狀態
            }, 1000);
        });
    }
    
    function showSuccess(message) {
        const modal = document.getElementById('successModal');
        const messageElement = document.getElementById('successMessage');
        
        if (modal && messageElement) {
            messageElement.textContent = message;
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            
            // 添加成功音效 (如果需要)
            playSuccessSound();
        }
    }
    
    function showError(message) {
        const modal = document.getElementById('errorModal');
        const messageElement = document.getElementById('errorMessage');
        
        if (modal && messageElement) {
            messageElement.textContent = message;
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            
            // 添加錯誤音效 (如果需要)
            playErrorSound();
        }
    }
    
    function playSuccessSound() {
        // 可以添加成功音效
        try {
            const audio = new Audio('/static/sounds/success.mp3');
            audio.volume = 0.3;
            audio.play().catch(() => {}); // 忽略播放失敗
        } catch (e) {
            // 忽略音效錯誤
        }
    }
    
    function playErrorSound() {
        // 可以添加錯誤音效
        try {
            const audio = new Audio('/static/sounds/error.mp3');
            audio.volume = 0.3;
            audio.play().catch(() => {}); // 忽略播放失敗
        } catch (e) {
            // 忽略音效錯誤
        }
    }
    
    // 添加粒子動畫效果
    function createParticles() {
        const particlesContainer = document.querySelector('.exchange-particles');
        if (!particlesContainer) return;
        
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.style.position = 'absolute';
            particle.style.width = Math.random() * 4 + 2 + 'px';
            particle.style.height = particle.style.width;
            particle.style.background = `hsl(${Math.random() * 360}, 70%, 70%)`;
            particle.style.borderRadius = '50%';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animation = `float ${Math.random() * 3 + 2}s ease-in-out infinite`;
            particle.style.animationDelay = Math.random() * 2 + 's';
            
            particlesContainer.appendChild(particle);
        }
    }
    
    // 創建粒子效果
    createParticles();
});
