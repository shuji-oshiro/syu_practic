import fs from 'fs';
import path from 'path';
import express from 'express';
import nodeCron from 'node-cron';
import nodemailer from 'nodemailer';
import sqlite3 from 'sqlite3';
const app = express();
const PORT = 3000;


const DATA_PATH = path.resolve('src/data/todos.json');
const DB_PATH = path.resolve('src/data/todos.db');




// 中間処理
// JSON形式のリクエストボディを解析するためのミドルウェアを設定
app.use(express.json());

// 静的ファイル（HTML、CSS、JavaScriptなど）を提供するためのミドルウェアを設定
// 'public'ディレクトリ内のファイルが直接アクセス可能になります
app.use(express.static(path.join(__dirname, 'public')));


function sendEmail(to: string, subject: string, text: string) {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: 'your.email@gmail.com',
      pass: 'your-app-password',
    },
  });

  const mailOptions = {
    from: 'your.email@gmail.com',
    to,
    subject,
    text,
  };
  console.info("mailOptions",mailOptions);
  
  // transporter.sendMail(mailOptions, (err: any, info: any) => {
  //   if (err) console.error(err);
  //   else console.log('Email sent: ' + info.response);
  // });
}

nodeCron.schedule('* * * * *', () => {
  console.log('⏰ 1分たったのでメール送信チェック開始');

  const db = new sqlite3.Database(DB_PATH);
  db.all('SELECT * FROM todos WHERE done = 0', (err, rows) => {
    if (err) return console.error(err);

    rows.forEach((todo: any) => {
      if (todo.email) {
        sendEmail(
          todo.email,
          'タスク未完了のお知らせ',
          `まだ完了していないタスク「${todo.title}」があります。`
        );
      }
    });
  });
});

// データベースから取得
app.get('/todos', (req, res) => {

  // DBファイルの作成または開く
  const db = new sqlite3.Database(DB_PATH);

  // テーブルがなければ作成
  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS todos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      done BOOLEAN NOT NULL DEFAULT 0,
      email TEXT NOT NULL
    )`);
  });

  const filter = req.query.filter; // 'all', 'done', 'undone' 

  let sql = 'SELECT * FROM todos';
  let params: any[] = [];

  if (filter === 'done') {
    sql += ' WHERE done = 1';
  } else if (filter === 'undone') {
    sql += ' WHERE done = 0';
  }

  //console.info(sql);
  
  // データベースから取得
  db.all(sql, params, (err, rows) => {
    if (err) {
      res.status(500).send('Database error');
      return;
    }
    //console.info("rows",rows);
    res.json(rows);
  });

});


//データ追加
app.post('/todos/add', (req, res) => {
  const { title, email } = req.body;
  const db = new sqlite3.Database(DB_PATH);

  
  db.run('INSERT INTO todos (title, done, email) VALUES (?, ?, ?)', [title, false, email], function (err) {
    if (err) {
      console.error(err);
      return res.status(500).send('Database error');
    }
    res.status(201).json({ id: this.lastID, title, done: false });
  });
});

//データ更新
app.patch('/todos/toggle', (req, res) => {
 
  const { id, done } = req.body;
  //console.info("id",id, "done",done);
  const todoId = Number(id);
  const todoDone = Number(done);

  const db = new sqlite3.Database(DB_PATH);

  db.run('UPDATE todos SET done = ? WHERE id = ?', [todoDone, todoId], function (err) {
    if (err) {
      console.error(err);
      return res.status(500).send('Database error');
    }
    res.json({ id, done });
  });
});

//データ削除
app.delete('/todos/delete', (req, res) => {
  const { id } = req.body;
  const todoId = Number(id);
  const db = new sqlite3.Database(DB_PATH);
  db.run('DELETE FROM todos WHERE id = ?', [todoId], function (err) {
    if (err) {
      console.error(err);
      return res.status(500).send('Database error');
    }
    res.json({ id });
  });
});




app.listen(PORT, () => {
  console.log(`ToDo GUIサーバーが http://localhost:${PORT} で起動しました`);
});
