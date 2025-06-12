const achievementsData = [
    {
        category: "🐣 初次邂逅",
        achievements: [
            {  code: "ACH-INIT-001", title: "Hello world", desc: "與你的第一隻精靈相遇。" , completed: true}
        ]
    },
    {
        category: "🧩 屬性蒐集成就",
        achievements: [
            { code: "ACH-TYPE-001", title: "我全都要", desc: "蒐集所有屬性精靈各一隻。", completed: true },
            { code: "ACH-TYPE-002", title: "草：一種日文", desc: "蒐集所有草屬性精靈。", completed: true },
            { code: "ACH-TYPE-003", title: "咕嚕咕嚕", desc: "蒐集所有水屬性精靈。" },
            { code: "ACH-TYPE-004", title: "熱愛105度的你", desc: "蒐集所有火屬性精靈。", completed: true },
            { code: "ACH-TYPE-005", title: "正道的光", desc: "蒐集所有光屬性精靈。", completed: true },
            { code: "ACH-TYPE-006", title: "黑暗之子", desc: "蒐集所有暗屬性精靈。" , completed: true},
            { code: "ACH-TYPE-007", title: "普通Disco", desc: "蒐集所有普通屬性精靈。", completed: true }
        ]
    },
    {
        category: "📦 精靈蒐集數量成就",
        achievements: [
            { code: "ACH-COLL-001", title: "更上一層樓", desc: "蒐集 10 隻精靈。", completed: true },
            { code: "ACH-COLL-002", title: "更上二層樓", desc: "蒐集 20 隻精靈。" , completed: true},
            { code: "ACH-COLL-003", title: "更上三層樓", desc: "蒐集 30 隻精靈。" , completed: true},
            { code: "ACH-COLL-004", title: "更上四層樓", desc: "蒐集 40 隻精靈。" , completed: true},
            { code: "ACH-COLL-005", title: "更上五層樓", desc: "蒐集 50 隻精靈。" , completed: true},
            { code: "ACH-COLL-006", title: "更上六層樓", desc: "蒐集 60 隻精靈。" , completed: true},
            { code: "ACH-COLL-007", title: "世界的真理，我已解明", desc: "蒐集所有精靈。" , completed: true}
        ]
    },
    {
        category: "⚔️ 競技場對戰成就",
        achievements: [
            { code: "ACH-ARENA-001", title: "牛刀小試", desc: "參與一次競技場對戰。", completed: true },
            { code: "ACH-ARENA-002", title: "熱血沸騰", desc: "累積參與 10 次競技場對戰。" , completed: true},
            { code: "ACH-ARENA-003", title: "好戰分子", desc: "累積參與 50 次競技場對戰。", completed: true },
            { code: "ACH-ARENA-004", title: "沉浸在戰鬥的藝術中", desc: "累積參與 100 次競技場對戰。", completed: true }
        ]
    },
    {
        category: "🏆 競技場勝利成就",
        achievements: [
            { code: "ACH-VICTORY-001", title: "勝利的果實", desc: "勝出一場競技場對戰。", completed: true },
            { code: "ACH-VICTORY-002", title: "我一個打十個", desc: "累積勝出 10 場競技場對戰。" , completed: true},
            { code: "ACH-VICTORY-003", title: "還有誰？", desc: "累積勝出 50 場競技場對戰。", completed: true },
            { code: "ACH-VICTORY-004", title: "他簡直是戰神", desc: "累積勝出 100 場競技場對戰。", completed: true }
        ]
    },
    {
        category: "👥 交友成就",
        achievements: [
            { code: "ACH-FRIEND-001", title: "不認識怎麼說話？", desc: "結交一名好友。" , completed: true},
            { code: "ACH-FRIEND-002", title: "不說話怎麼認識？", desc: "結交 10 名好友。", completed: true },
            { code: "ACH-FRIEND-003", title: "四海之內皆兄弟", desc: "結交 50 名好友。", completed: true },
            { code: "ACH-FRIEND-004", title: "天下誰人不識君？", desc: "結交 100 名好友。", completed: true}
        ]
    },
    {
        category: "🏛️ 道館佔領成就",
        achievements: [
            { code: "ACH-GYM-001", title: "此路由我開", desc: "成功佔領一個道館。", completed: true },
            { code: "ACH-GYM-002", title: "此樹由我栽", desc: "成功佔領兩個道館。" , completed: true},
            { code: "ACH-GYM-003", title: "要從此地過", desc: "成功佔領三個道館。" , completed: true},
            { code: "ACH-GYM-004", title: "留下買路財", desc: "成功佔領四個道館。" , completed: true}
        ]
    },
    {
        category: "📅 登入天數成就",
        achievements: [
            { code: "ACH-LOGIN-001", title: "感謝每一次相遇", desc: "累計登入 1 天。", completed: true },
            { code: "ACH-LOGIN-002", title: "感恩每一段緣分", desc: "累計登入 7 天。", completed: true },
            { code: "ACH-LOGIN-003", title: "珍惜旅途的風景", desc: "累計登入 30 天。", completed: true },
            { code: "ACH-LOGIN-004", title: "期待每一個明天", desc: "累計登入 60 天。", completed: true },
            { code: "ACH-LOGIN-005", title: "阿偉你麼還在打電動？", desc: "累計登入 100 天。", completed: true }
        ]
    },
    {
        category: "✨ 特殊成就",
        achievements: [
            { code: "ACH-SPEC-001", title: "在轉動的地球再次相遇", desc: "超過 14 天未上線後再次登入。", completed: true }
        ]
    }
];

// 用戶完成成就在 users/{userId}/achievements 子集 或 users/{userId} 裡的 achievements

function fetchUserAchievements(userId) {
  return db.collection('users').doc(userId).get()
    .then(doc => {
      if (!doc.exists) throw new Error("找不到用戶資料");
      const userData = doc.data();
      // userData.achievements 是完成成就json，["ACH-TYPE-001", "ACH-COLL-001"]
      return userData.achievements || [];
    });
}

function updateAchievementsStatus(userCompletedAchievements) {
  achievementsData.forEach(category => {
    category.achievements.forEach(ach => {
      ach.completed = userCompletedAchievements.includes(ach.code);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const userId = window.currentUserId; 
  if (!userId) return;

  fetchUserAchievements(userId)
    .then(userCompletedAchievements => {
      updateAchievementsStatus(userCompletedAchievements);
      renderAchievements();
    })
    .catch(err => {
      console.error(err);
      // 失敗的話也可以先渲染靜態預設成就
      renderAchievements();
    });
});

function renderAchievements() {
  const container = document.getElementById('achievementAccordion');
  container.innerHTML = ''; // 先清空

  achievementsData.forEach((category, idx) => {
    const item = document.createElement('div');
    item.className = 'accordion-item';

    const headerId = `heading${idx}`;
    const collapseId = `collapse${idx}`;

    const header = document.createElement('h2');
    header.className = 'accordion-header';
    header.id = headerId;

    const button = document.createElement('button');
    button.className = 'accordion-button';
    if (idx !== 0) button.classList.add('collapsed');
    button.type = 'button';
    button.setAttribute('data-bs-toggle', 'collapse');
    button.setAttribute('data-bs-target', `#${collapseId}`);
    button.setAttribute('aria-expanded', idx === 0 ? 'true' : 'false');
    button.setAttribute('aria-controls', collapseId);
    button.textContent = category.category;

    header.appendChild(button);

    const content = document.createElement('div');
    content.id = collapseId;
    content.className = 'accordion-collapse collapse';
    if (idx === 0) content.classList.add('show');
    content.setAttribute('aria-labelledby', headerId);
    content.setAttribute('data-bs-parent', '#achievementAccordion');

    const body = document.createElement('div');
    body.className = 'accordion-body';

    category.achievements.forEach(ach => {
      const achDiv = document.createElement('div');
      achDiv.className = 'achievement-item';
      if (!ach.completed) achDiv.classList.add('not-completed');
      achDiv.innerHTML = `
        <div class="achievement-code">${ach.code}</div>
        <div class="achievement-title">${ach.title}</div>
        <div class="achievement-desc">${ach.desc}</div>
        <div class="status">狀態：${ach.completed ? "已完成" : "未完成"}</div>
      `;
      body.appendChild(achDiv);
    });

    content.appendChild(body);
    item.appendChild(header);
    item.appendChild(content);
    container.appendChild(item);
  });
}
