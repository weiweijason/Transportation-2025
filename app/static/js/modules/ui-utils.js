// 模組：ui-utils.js - UI 工具函數

// 顯示加載中提示
function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.visibility = 'visible';
    }
}

// 隱藏加載中提示
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.visibility = 'hidden';
    }
}

// 顯示錯誤訊息
function showErrorMessage(message, isError = true) {
    // 創建自訂的訊息容器
    const alertContainer = document.createElement('div');
    alertContainer.className = `custom-alert alert alert-${isError ? 'danger' : 'warning'} alert-dismissible fade show`;
    alertContainer.style.position = 'fixed';
    alertContainer.style.top = '10px';
    alertContainer.style.left = '50%';
    alertContainer.style.transform = 'translateX(-50%)';
    alertContainer.style.zIndex = '9999';
    alertContainer.style.minWidth = '300px';
    alertContainer.style.maxWidth = '80%';
    alertContainer.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
    
    alertContainer.innerHTML = `
        <div class="d-flex">
            <div class="me-3">
                <i class="fas fa-${isError ? 'exclamation-circle' : 'exclamation-triangle'}"></i>
            </div>
            <div>${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // 自動消失
    setTimeout(() => {
        alertContainer.classList.remove('show');
        setTimeout(() => {
            alertContainer.remove();
        }, 300);
    }, 5000);
}

// 導出模組
export { showLoading, hideLoading, showErrorMessage };