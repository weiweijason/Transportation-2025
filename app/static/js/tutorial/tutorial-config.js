/**
 * 教學模式配置檔案
 * 包含教程步驟定義、初始化變量等
 */

// 教程步驟內容
const tutorialSteps = [
    {
        title: "歡迎來到精靈公車世界！",
        text: "在這個世界中，您可以探索城市的公車路線，捕捉精靈，並與其他玩家競爭占領公車站牌道館。讓我們開始基礎教學吧！",
        action: "initMap"
    },
    {
        title: "探索公車路線",
        text: "這是遊戲的主要地圖，展示了貓空纜車的公車接駁路線。藍點表示您的位置，紅色建築表示公車站牌道館，閃爍的點是可以捕捉的精靈。",
        action: "showPlayerAndGyms"
    },
    {
        title: "捕捉精靈",
        text: "看！您附近的站牌出現了一隻精靈。點擊它來嘗試捕捉。在遊戲中，精靈會在公車路線周圍隨機出現，您需要接近精靈才能捕捉它們。",
        showElement: "catchInterface",
        action: "showCreatureCapture"
    },
    {
        title: "選擇道館",
        text: "恭喜您捕捉到第一隻精靈！現在，讓我們選擇一個公車站牌道館來占領。道館等級取決於經過的公車路線數量。",
        showElement: "gymSelection",
        hideElement: "catchInterface",
        action: "showGymSelection"
    },
    {
        title: "占領道館",
        text: "很好！這個道館目前無人占領。您可以使用剛捕捉到的精靈來占領它，守護精靈的戰鬥力越強，您的道館就越難被其他玩家挑戰成功。",
        showElement: "gymOccupation",
        hideElement: "gymSelection",
        action: "showGymOccupation"
    }
];

// 全局配置對象
const tutorialConfig = {
    // 當前狀態
    currentStepIndex: 0,
    selectedGym: null,
    countdownInterval: null,

    // 地圖元素
    map: null,
    playerMarker: null,
    gymMarkers: [],
    creatureMarker: null,

    // 數據
    defaultCreature: null,
    gyms: null,
    
    // 初始化函數
    init: function(defaultCreatureData, gymsData) {
        this.defaultCreature = defaultCreatureData;
        this.gyms = gymsData;
        
        // 初始化 UI 控制
        this.initUIControls();
    },
    
    // 初始化 UI 控制元素
    initUIControls: function() {
        // 將 DOM 元素引用存儲為屬性
        this.elements = {
            tutorialDialog: document.getElementById('tutorialDialog'),
            tutorialTitle: document.getElementById('tutorialTitle'),
            tutorialText: document.getElementById('tutorialText'),
            tutorialNext: document.getElementById('tutorialNext'),
            tutorialPrev: document.getElementById('tutorialPrev'),
            tutorialProgress: document.getElementById('tutorialProgress'),
            catchInterface: document.getElementById('catchInterface'),
            gymSelection: document.getElementById('gymSelection'),
            gymOccupation: document.getElementById('gymOccupation'),
            currentStepElement: document.getElementById('currentStep'),
            totalStepsElement: document.getElementById('totalSteps'),
            nextBtnText: document.getElementById('nextBtnText'),
            tutorialComplete: document.getElementById('tutorialComplete')
        };
        
        // 設置總步驟數
        this.elements.totalStepsElement.textContent = tutorialSteps.length;
        
        // 設置按鈕事件
        this.elements.tutorialNext.addEventListener('click', () => tutorialUI.goToNextStep());
        this.elements.tutorialPrev.addEventListener('click', () => tutorialUI.goToPrevStep());
    },
    
    // 根據步驟名稱執行相應的動作
    executeAction: function(actionName) {
        if (!actionName) return false;
        
        switch(actionName) {
            case 'initMap':
                return tutorialMap.initMap();
            case 'showPlayerAndGyms':
                return tutorialMap.showPlayerAndGyms();
            case 'showCreatureCapture':
                return tutorialCreature.showCreatureCapture();
            case 'showGymSelection':
                return tutorialGym.showGymSelection();
            case 'showGymOccupation':
                return tutorialGym.showGymOccupation();
            default:
                console.warn(`未知的動作: ${actionName}`);
                return false;
        }
    },
    
    // 完成教程
    completeTutorial: function() {
        this.elements.tutorialComplete.style.display = 'flex';
    }
};

// 導出到全局
window.tutorialConfig = tutorialConfig;
window.tutorialSteps = tutorialSteps;
