// 精靈公車主要JavaScript文件

// 等待DOM加載完成
document.addEventListener('DOMContentLoaded', function() {
    // 處理提示訊息的自動關閉
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 3000); // 3秒後自動關閉
    });

    // 處理密碼確認驗證
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                event.preventDefault();
                alert('兩次輸入的密碼不一致，請重新確認！');
            }
        });
    }

    // 添加Bootstrap表單驗證樣式
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});