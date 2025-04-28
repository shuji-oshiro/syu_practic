const express = require('express');
const app = express();
const PORT = 3000;

app.use(express.json()); // リクエストボディをJSONとしてパース

// 仮のタスクデータ
let tasks = [
  { id: 1, title: 'Do the laundry', completed: false },
  { id: 2, title: 'Write the report', completed: true }
];

// タスク一覧を取得 (GET)
app.get('/tasks', (req, res) => {
  res.json(tasks);
});

// 新しいタスクを作成 (POST)
app.post('/tasks', (req, res) => {
  const { title, completed } = req.body;
  const newTask = {
    id: tasks.length + 1,
    title,
    completed: completed || false
  };
  tasks.push(newTask);
  res.status(201).json(newTask);
});

// タスクを更新 (PUT)
app.put('/tasks/:id', (req, res) => {
  const taskId = parseInt(req.params.id);
  const { title, completed } = req.body;
  
  let task = tasks.find(t => t.id === taskId);
  
  if (!task) {
    return res.status(404).json({ message: 'Task not found' });
  }

  task.title = title || task.title;
  task.completed = completed !== undefined ? completed : task.completed;
  res.json(task);
});

// タスクを削除 (DELETE)
app.delete('/tasks/:id', (req, res) => {
  const taskId = parseInt(req.params.id);
  tasks = tasks.filter(t => t.id !== taskId);
  res.status(204).send();
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
