console.log("server.ts start"); 
import fs from 'fs';
import path from 'path';
import express from 'express';
import nodeCron from 'node-cron';
import nodemailer from 'nodemailer';
import dotenv from 'dotenv';
import sqlite3 from 'sqlite3';
import { getCompileCacheDir } from 'module';
const app = express();
const PORT = process.env.PORT || 3000;


//nst DATA_PATH = path.resolve('src/data/todos.json');
const DB_PATH = path.resolve('src/data/todos.db');

//タスクを追加するときに送信するメールアドレスリスト
let send_email_list: string[] = []

dotenv.config({path: path.resolve('.env')});


const default_email = process.env.DEFAULT_EMAIL || '';

// 中間処理
// JSON形式のリクエストボディを解析するためのミドルウェアを設定
app.use(express.json());

// 静的ファイル（HTML、CSS、JavaScriptなど）を提供するためのミドルウェアを設定
// 'public'ディレクトリ内のファイルが直接アクセス可能になります
app.use(express.static(path.join(__dirname, 'public')));

// 型定義
interface Todo {
  title: string;
  email: string;
  done: boolean;
}

interface EmailRequestBody {
  email: string;
}

interface TodoAddRequestBody {
  title: string;
  email_list: string[];
}

interface TodoToggleRequestBody {
  title: string;
  done: boolean;
  email: string;
}

interface TodoDeleteRequestBody {
  title: string;
}

interface TodoUpdateTitleRequestBody {
  oldTitle: string;
  newTitle: string;
}

type SendEmail = (to: string, subject: string, text: string) => void; // 文字列型のa、数値型のbを引数に持ち、真偽値型を返却する関数の型定義


//タスク未完了のメール送信
const sendEmail: SendEmail = (to: string, subject: string, text: string): void => {
  
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.GMAIL_USER,
        pass: process.env.GMAIL_APP_PASSWORD,
      },
  });

  const mailOptions = {
    from: 'your.email@gmail.com',
    to,
    subject,
    text,
  };
  console.info("Sending email with options:", mailOptions);

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.error('Error sending email:', error);
    } else {
      console.log('Email sent:', info.response);
    }
  });

}




//特定時間ごとにタスク未完了のメール送信
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
app.get('/todos', (req: express.Request, res: express.Response) => {
  const db = new sqlite3.Database(DB_PATH);

  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS todos (
      title TEXT,
      email TEXT,
      done BOOLEAN NOT NULL DEFAULT 0,
      PRIMARY KEY (title, email)
    )`);
  });

  const filter = req.query.filter as string | undefined;
  const user = req.query.user as string | undefined;

  let sql = 'SELECT * FROM todos';
  let params: any[] = [];

  if (filter === 'done') {
    sql += ' WHERE done = 1';
  } else if (filter === 'undone') {
    sql += ' WHERE done = 0';
  } else {
    sql += ' WHERE 1=1';
  }
  
  let addtaskflag = true;
  if (user) {
    sql += ` AND email = '${user}'`;
    addtaskflag = false;
  }

  db.all(sql, params, (err: Error | null, rows: Todo[]) => {
    if (err) {
      res.status(500).send('Database error');
      return;
    }
    res.json({ rows, addtaskflag });
  });
});


//タスクデータを追加
app.post('/todos/add', (req: express.Request<{}, {}, TodoAddRequestBody>, res: express.Response) => {
  const { title, email_list } = req.body;
  
  const db = new sqlite3.Database(DB_PATH);
  
  db.get('SELECT * FROM todos WHERE title = ?', [title], (err: Error | null, row: Todo | undefined) => {
    if (err) {
      console.error(err);
      return res.status(500).send('Database error');
    }
    if (row) {
      return res.status(400).send('このタスクは既に存在します。別の名前で登録してください');
    } else {
      for (const email of email_list) {
        db.run('INSERT INTO todos (title, done, email) VALUES (?, ?, ?)', 
          [title, false, email], 
          function(err: Error | null) {
            if (err) {
              console.error(err);
              return res.status(500).send('Database error');
            }
          }
        );
      }
      res.status(201).json({ 
        title, 
        done: false,
        emails: email_list 
      });
    }
  });
});

//データ更新
app.patch('/todos/toggle', (req: express.Request<{}, {}, TodoToggleRequestBody>, res: express.Response) => {
  const { title, done, email } = req.body;
  const todoTitle = title;
  const todoDone = Number(done);
  const todoEmail = email;

  const db = new sqlite3.Database(DB_PATH);

  db.run('UPDATE todos SET done = ? WHERE title = ? AND email = ?', 
    [todoDone, todoTitle, todoEmail], 
    function(err: Error | null) {
      if (err) {
        console.error(err);
        return res.status(500).send('Database error');
      }
      res.json({ title, done, email });
    }
  );
});

//データ削除
app.delete('/todos/delete', (req: express.Request<{}, {}, TodoDeleteRequestBody>, res: express.Response) => {
  const { title } = req.body;
  const db = new sqlite3.Database(DB_PATH);
  db.run('DELETE FROM todos WHERE title = ?', [title], function(err: Error | null) {
    if (err) {
      console.error(err);
      return res.status(500).send('Database error');
    }
    res.json({ title });
  });
});



// タスクのタイトルを更新
app.patch('/todos/updateTitle', (req: express.Request<{}, {}, TodoUpdateTitleRequestBody>, res: express.Response) => {
  const { oldTitle, newTitle } = req.body;
  const db = new sqlite3.Database(DB_PATH);

  db.get('SELECT * FROM todos WHERE title = ?', [newTitle], (err: Error | null, row: Todo | undefined) => {
    if (err) {
      console.error(err);
      return res.status(500).send('Database error');
    }
    if (row) {
      return res.status(400).send('このタスクは既に存在します。別の名前で登録してください');
    }
    db.run('UPDATE todos SET title = ? WHERE title = ?', [newTitle, oldTitle], function(err: Error | null) {
      if (err) {
        console.error(err);
        return res.status(500).send('Database error');
      }
      res.json({ oldTitle, newTitle });
    });
  });
});


//タスク未完了のメール送信先を更新
app.post('/todos/default_email', (req: express.Request<{}, {}, EmailRequestBody>, res: express.Response) => {
  const { email } = req.body;
  if (!email) {
    res.status(400).json({ error: 'メールアドレスが指定されていません' });
    return;
  }
  
  try {
    fs.writeFileSync(path.resolve('src/data/send_email.csv'), email);
    res.json({ email: send_email_list });
  } catch (error) {
    console.error('メールアドレスの保存中にエラーが発生しました:', error);
    res.status(500).json({ error: 'メールアドレスの保存に失敗しました' });
  }
});

app.get('/todos/default_email', (req: express.Request, res: express.Response) => {
  res.json({ send_email_list });
});


app.listen(PORT, () => {

  send_email_list = fs
    .readFileSync(path.resolve('src/data/send_email.csv'), 'utf8')
    .split('\n')
    .map(line => line?.trim())
    .filter(Boolean);

  console.log(`ToDo GUIサーバーが http://localhost:${PORT} で起動しました`);
});




