// 在瀏覽器控制台中運行這個測試
async function testGymAPI() {
    console.log(">>> 開始測試基地道館API");
    
    const testData = {
        gym_id: "tutorial-gym-1",
        gym_name: "中正紀念堂基地道館", 
        gym_level: 5,
        lat: 25.03556,
        lng: 121.51972,
        guardian_creature: {
            id: "starter_creature",
            name: "初始精靈",
            image: "/static/images/creatures/default.png",
            type: "water",
            power: 50
        }
    };
    
    console.log(">>> 發送請求數據:", testData);
    
    try {
        const response = await fetch('/auth/tutorial/set-base-gym', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Tutorial-Mode': 'true',
                'X-Tutorial-User-ID': 'tutorial_user_' + Date.now()
            },
            body: JSON.stringify(testData)
        });
        
        console.log(">>> 響應狀態:", response.status);
        console.log(">>> 響應狀態文本:", response.statusText);
        
        const responseText = await response.text();
        console.log(">>> 響應內容:", responseText);
        
        if (response.ok) {
            const data = JSON.parse(responseText);
            console.log("✅ API調用成功:", data);
            return data;
        } else {
            console.log("❌ API調用失敗:", response.status, responseText);
            return null;
        }
        
    } catch (error) {
        console.error("❌ 網絡錯誤:", error);
        return null;
    }
}

// 呼叫測試函數
testGymAPI();
