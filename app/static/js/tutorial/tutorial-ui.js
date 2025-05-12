/**
 * 教學模式 UI 控制
 * 負責步驟切換、UI 顯示/隱藏等
 */

const tutorialUI = {
    // 顯示當前步驟
    showStep: function(index) {
        const step = tutorialSteps[index];
        const elements = tutorialConfig.elements;
        
        // 保存當前步驟
        tutorialConfig.currentStepIndex = index;
        
        // 更新對話框內容
        elements.tutorialTitle.textContent = step.title;
        elements.tutorialText.textContent = step.text;
        elements.currentStepElement.textContent = index + 1;
        
        // 更新進度條
        const progressPercentage = ((index + 1) / tutorialSteps.length) * 100;
        elements.tutorialProgress.style.width = progressPercentage + '%';
        
        // 顯示/隱藏特定元素
        if (step.showElement) {
            document.getElementById(step.showElement).style.display = 'block';
        }
        
        if (step.hideElement) {
            document.getElementById(step.hideElement).style.display = 'none';
        }
        
        // 執行步驟特定動作
        if (step.action) {
            tutorialConfig.executeAction(step.action);
        }
        
        // 更新按鈕
        if (index === 0) {
            elements.tutorialPrev.style.display = 'none';
            elements.nextBtnText.textContent = '開始';
        } else {
            elements.tutorialPrev.style.display = 'block';
            elements.nextBtnText.textContent = '下一步';
        }
        
        // 最後一步
        if (index === tutorialSteps.length - 1) {
            elements.nextBtnText.textContent = '完成';
        }
    },
    
    // 前往下一步
    goToNextStep: function() {
        if (tutorialConfig.currentStepIndex < tutorialSteps.length - 1) {
            tutorialConfig.currentStepIndex++;
            this.showStep(tutorialConfig.currentStepIndex);
        } else {
            tutorialConfig.completeTutorial();
        }
    },
    
    // 返回上一步
    goToPrevStep: function() {
        if (tutorialConfig.currentStepIndex > 0) {
            tutorialConfig.currentStepIndex--;
            this.showStep(tutorialConfig.currentStepIndex);
        }
    }
};

// 導出模塊
window.tutorialUI = tutorialUI;
