import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import sqlite3 from 'sqlite3';
import express from 'express';
import nodeCron from 'node-cron';
import nodemailer from 'nodemailer';

const app = express();
const PORT = process.env.PORT || 3000;

const DB_PATH = path.resolve('src/data/todos.db');

//タスクを追加するときに送信するメールアドレスリスト
let send_email_list: string[] = []

dotenv.config({path: path.resolve('.env')});


// 中間処理
// JSON形式のリクエストボディを解析するためのミドルウェアを設定
app.use(express.json());

// 静的ファイル（HTML、CSS、JavaScriptなど）を提供するためのミドルウェアを設定
// 'public'ディレクトリ内のファイルが直接アクセス可能になります
app.use(express.static(path.join(__dirname, 'public')));
console.log("publicディレクトリ",path.join(__dirname, 'public'));

// 型定義
interface Todo {
  title: string;
  email: string;
  done: boolean;
}

interface TodoGetRequestBody {
  filter: string | undefined;
  user: string | undefined;
}


interface EmailRequestBody {
  emailList: string;
}

interface TodoAddRequestBody {
  title: string;
  emailList: string[];
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

type SendEmail = (to: string, subject: string, text: string) => void;


//タスク未完了のメール送信
const sendEmail: SendEmail = (to, subject, text): void => {
  
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

// メール送信時刻設定
const x = process.env.SEND_TIME_HOUR || '9';
const y = process.env.SEND_TIME_MINITS || '0';
const mail_title = process.env.MAIL_TITLE || 'タスク未完了のお知らせ';
const mail_text_template = process.env.MAIL_TEXT || 'まだ完了していないタスク「${task_text}」があります。';


console.log(`毎日${x}時${y}分メール送信チェック`);
console.log("送信文書",mail_title,mail_text_template);
//特定時間ごとにタスク未完了者へメール送信
nodeCron.schedule(`${y} ${x} * * *`, () => {

  
  console.log(`${x}時${y}分メール送信チェック開始`);
  const db = new sqlite3.Database(DB_PATH);
  db.all('SELECT * FROM todos WHERE done = 0', (err, rows) => {
    if (err) return console.error(err);

    rows.forEach((todo: any) => {
      try {

        const mail_text = mail_text_template.replace('{task_text}', todo.title);
        if (todo.email) {
          sendEmail(
            todo.email,
            mail_title,
            mail_text
          );
        }
      } catch (error) {
        console.error('メール送信時にエラーが発生しました:', error);
      }
    });

  });
}, {
  timezone: 'Asia/Tokyo'
});


// データベースからタスク情報を取得
app.get('/todos', (req: express.Request<TodoGetRequestBody>, res: express.Response) => {
  const db = new sqlite3.Database(DB_PATH);
  const { filter, user } = req.query  

  console.log(filter,user);

  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS todos (
      title TEXT,
      email TEXT,
      done BOOLEAN NOT NULL DEFAULT 0,
      PRIMARY KEY (title, email)
    )`);
  });

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

  console.log(sql);

  db.all(sql, params, (err: Error | null, rows: Todo[]) => {
    if (err) {
      res.status(500).json({ error: 'タスクデータの取得中にエラーが発生しました' });
      return;
    }
    res.json({ rows, addtaskflag });
  });
});


//タスクデータを追加
app.post('/todos/add', (req: express.Request<{}, {}, TodoAddRequestBody>, res: express.Response) => {
  
  const { title, emailList} = req.body;
  
  console.log("call add");
  
  if (emailList.length === 0) {
    res.status(400).json({ warning: 'メールアドレスが指定されていません' });
    return;
  }


  const db = new sqlite3.Database(DB_PATH);
  
  db.get('SELECT * FROM todos WHERE title = ?', [title], (err: Error | null, row: Todo | undefined) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'タスクデータの読み込み中にエラーが発生しました' });
    }
    if (row) {
      return res.status(500).json({ error: 'このタスクは既に存在します。別の名前で登録してください' });
    } 

    for (const email of emailList) {
      db.run('INSERT INTO todos (title, done, email) VALUES (?, ?, ?)', 
        [title, false, email], 
        function(err: Error | null) {
          if (err) {
            console.error(err);
            return res.status(500).json({ error: 'タスクデータの新規追加中にエラーが発生しました' });
          }
        }
      );
    }
  });
  res.status(201).json({ 
    title, 
    done: false,
    emails: emailList 
  });
});

//タスクデータ実施更新
app.patch('/todos/toggle', (req: express.Request<{}, {}, TodoToggleRequestBody>, res: express.Response) => {
  console.log("call toggle");

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
        return res.status(500).json({ error: 'タスク完了データの更新中にエラーが発生しました' });
      }
      res.json({ title, done, email });
    }
  );
});

//タスクデータ削除
app.delete('/todos/delete', (req: express.Request<{}, {}, TodoDeleteRequestBody>, res: express.Response) => {
  console.log("call delete");

  const { title } = req.body;
  const db = new sqlite3.Database(DB_PATH);
  db.run('DELETE FROM todos WHERE title = ?', [title], function(err: Error | null) {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'タスクデータの削除中にエラーが発生しました' });
    }
    res.json({ title });
  });
});



// タスクのタイトルを更新
app.patch('/todos/updateTitle', (req: express.Request<{}, {}, TodoUpdateTitleRequestBody>, res: express.Response) => {
  console.log("call updateTitle");

  const { oldTitle, newTitle } = req.body;

  // SQLインジェクション対策のための文字列エスケープ
  const sanitizedOldTitle = oldTitle.replace(/[;'"\\]/g, '');
  const sanitizedNewTitle = newTitle.replace(/[;'"\\]/g, '');

  const db = new sqlite3.Database(DB_PATH);

  db.get('SELECT * FROM todos WHERE title = ?', [sanitizedNewTitle], (err: Error | null, row: Todo | undefined) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'データベースエラーが発生しました' });
    }
    if (row) {
      return res.status(400).json({ warning: 'このタスクは既に存在します。別の名前で登録してください' });
    }
    db.run('UPDATE todos SET title = ? WHERE title = ?', [sanitizedNewTitle, sanitizedOldTitle], function(err: Error | null) {
      if (err) {
        console.error(err);
        return res.status(500).json({ error: 'データベースエラーが発生しました' });
      }
      res.json({newTitle: sanitizedNewTitle });
    });
  });
});


//タスクに設定するデフォルトのメールアドレスを更新
app.post('/todos/default_email', (req: express.Request<{}, {}, EmailRequestBody>, res: express.Response) => {
  console.log("call default_email");
  
  try {
    const { emailList } = req.body;
    let temp_send_email_list = emailList.split(',').map(line => line?.trim().replace(/\s+/g, ''))
    console.log("更新するメールアドレス：",temp_send_email_list);

    if (temp_send_email_list.length === 0) {
      res.status(400).json({ warning: '更新できるメールアドレスが存在しません' });
      return;
    }

    fs.writeFileSync(path.resolve('src/data/send_email.csv'), temp_send_email_list.join(','));

    send_email_list = temp_send_email_list;
    res.json({ email: temp_send_email_list });

  } catch (error) {
    console.error('メールアドレスの更新中にエラーが発生しました:', error);
    res.status(500).json({ error: 'メールアドレスの更新中にエラーが発生しました' });
  }
});

//タスクに設定するデフォルトのメールアドレスを取得
app.get('/todos/default_email', (req: express.Request, res: express.Response) => {

  console.log("call default_email");
  res.json({ send_email_list });
});


app.listen(PORT, () => {

  try {
    const filePath = path.resolve('src/data/send_email.csv')
    const dirPath = path.dirname(filePath);

    // ディレクトリが存在しなければ作成
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }

    // ファイルが存在しない場合、空ファイルを作成
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, '');
    }

    send_email_list = fs
      .readFileSync(path.resolve('src/data/send_email.csv'), 'utf8')
      .split(',')
      .filter(Boolean);
    
    console.log(`ToDo GUIサーバーが http://localhost:${PORT} で起動しました`);

  } catch (error) {
    console.error('初期設定中にエラーが発生しました:', error);
  }

});




