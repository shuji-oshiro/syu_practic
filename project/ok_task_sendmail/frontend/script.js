async function loadUsers() {
    const res = await fetch('/api/users');
    const users = await res.json();
}

async function loadTasks() {
    console.log("タスクデータ取得開始");
    const res = await fetch('/api/task');
    const tasks = await res.json();
        
    const list = document.getElementById('task-list');
    list.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        li.innerHTML = `
          <table class="task-table">
            <thead>
              <tr>
                <th colspan="2">
                  <div class="task-header">
                    <span><strong>${task.title}</strong>（${task.due_date}）</span>
                    <button onclick="deleteTask(${task.id})">タスク削除</button>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              ${task.users.map(user => `
                <tr class="user-row">
                  <td>ユーザー：${user.username}</td>
                  <td class="right-align">
                    <button onclick='completeTask(${task.id}, ${JSON.stringify(user.username)})'>完了</button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;
        list.appendChild(li);
    });
    
}

async function addTask() {
    const title = document.getElementById('title').value;
    const due_date = document.getElementById('due_date').value;
    
    await fetch(`/api/task?title=${encodeURIComponent(title)}&due_date=${due_date}`, {
        method: 'POST'
    });
    loadTasks();
}

async function deleteTask(id) {
    await fetch(`/api/task/${id}`, { method: 'DELETE' });
    loadTasks();
}

async function completeTask(id, username) {
  console.log("削除処理実行")
  console.log(id, username)
    await fetch(`/api/task/${id}/user/${encodeURIComponent(username)}`, {
        method: 'DELETE'
    });
    loadTasks();
}

window.onload = async () => {
    await loadUsers();
    loadTasks();
};
