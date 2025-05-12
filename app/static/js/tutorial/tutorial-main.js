/**
 * 教學模式主要入口文件
 * 負責初始化教學流程
 */

document.addEventListener('DOMContentLoaded', function() {
    // 檢查URL參數，如果是從捕捉頁面返回，則自動進入下一步
    const urlParams = new URLSearchParams(window.location.search);
    const captureSuccess = urlParams.get('capture_success');
    
    // 初始化教學模式
    tutorialConfig.init(defaultCreature, gyms);
    
    // 顯示第一步
    tutorialUI.showStep(0);
    
    // 如果是從捕捉頁面返回，跳到第三步(捕捉精靈)並自動進入下一步
    if (captureSuccess === 'true') {
        tutorialConfig.currentStepIndex = 2;
        tutorialUI.showStep(tutorialConfig.currentStepIndex);
        
        // 在短暫延遲後自動進入下一步
        setTimeout(() => {
            tutorialUI.goToNextStep();
        }, 1500);
    }
});
