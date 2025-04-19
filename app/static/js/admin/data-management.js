/**
 * 貓空纜車資料管理頁面的JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化表格切換功能
    initTableToggles();
    
    // 獲取資料並更新頁面
    fetchDataAndUpdatePage();
});

/**
 * 初始化Bootstrap工具提示
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 初始化表格顯示切換功能
 */
function initTableToggles() {
    // 切換路線表格顯示狀態
    setupTableToggle('toggleRoutesBtn', 'routesTableContainer', 'toggleRoutesIcon');
    
    // 切換站點表格顯示狀態
    setupTableToggle('toggleStopsBtn', 'stopsTableContainer', 'toggleStopsIcon');
}

/**
 * 設置表格顯示切換
 */
function setupTableToggle(btnId, containerId, iconId) {
    const toggleBtn = document.getElementById(btnId);
    const tableContainer = document.getElementById(containerId);
    const toggleIcon = document.getElementById(iconId);
    
    if (toggleBtn && tableContainer && toggleIcon) {
        // 確保初始狀態一致
        tableContainer.style.display = 'block';
        toggleIcon.classList.remove('fa-chevron-up');
        toggleIcon.classList.add('fa-chevron-down');
        
        toggleBtn.addEventListener('click', function() {
            if (tableContainer.style.display === 'none') {
                tableContainer.style.display = 'block';
                toggleIcon.classList.remove('fa-chevron-up');
                toggleIcon.classList.add('fa-chevron-down');
            } else {
                tableContainer.style.display = 'none';
                toggleIcon.classList.remove('fa-chevron-down');
                toggleIcon.classList.add('fa-chevron-up');
            }
        });
    }
}

/**
 * 從後端獲取資料並更新頁面
 */
function fetchDataAndUpdatePage() {
    // 獲取資料概況
    fetch('/admin/api/data-summary')
        .then(response => response.json())
        .then(data => {
            updateDataSummary(data);
        })
        .catch(error => {
            console.error('獲取資料概況時出錯:', error);
        });
        
    // 獲取資料健康狀態
    fetch('/admin/api/data-health')
        .then(response => response.json())
        .then(data => {
            updateHealthStatus(data);
        })
        .catch(error => {
            console.error('獲取資料健康狀態時出錯:', error);
        });
}

/**
 * 更新資料概況
 */
function updateDataSummary(data) {
    // 更新路線和站點計數
    document.getElementById('routes-count').textContent = data.routesCount || '0';
    document.getElementById('stops-count').textContent = data.stopsCount || '0';
    
    // 更新最後更新時間
    document.getElementById('last-update').textContent = data.lastUpdateTimeAgo || '未知';
    
    // 更新API請求數量
    document.getElementById('api-requests').textContent = data.apiRequestsCount || '0';
}

/**
 * 更新健康狀態
 */
function updateHealthStatus(data) {
    // 更新路線資料健康度
    updateProgressBar('routes-health', data.routesHealth);
    
    // 更新站點資料健康度
    updateProgressBar('stops-health', data.stopsHealth);
    
    // 更新時間健康度
    updateProgressBar('time-health', data.timeHealth);
    
    // 更新API健康度
    updateProgressBar('api-health', data.apiHealth);
}

/**
 * 更新進度條
 */
function updateProgressBar(elementId, percentage) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.width = percentage + '%';
        element.setAttribute('aria-valuenow', percentage);
    }
}

/**
 * 格式化時間（多久之前）
 */
function formatTimeAgo(dateString) {
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return '未知時間';
        }
        
        const now = new Date();
        const diffSeconds = Math.floor((now - date) / 1000);
        
        if (diffSeconds < 60) {
            return '剛剛';
        } else if (diffSeconds < 3600) {
            return Math.floor(diffSeconds / 60) + ' 分鐘前';
        } else if (diffSeconds < 86400) {
            return Math.floor(diffSeconds / 3600) + ' 小時前';
        } else {
            return Math.floor(diffSeconds / 86400) + ' 天前';
        }
    } catch (error) {
        console.error('格式化時間錯誤:', error);
        return '未知時間';
    }
}