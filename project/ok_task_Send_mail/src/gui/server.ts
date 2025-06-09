import dotenv from 'dotenv';
dotenv.config();
import fs from 'fs';
import path from 'path';
import express from 'express';
import cors from 'cors';
import { Request, Response } from 'express';
import { 
  TodoAddSchema,
  TodoGetSchema,
  TodoUpdateSchema,
  TodoTitleUpdateSchema,
  TodoDeleteSchema,
  TodoSendTimeSchema
} from '../types/interface';

import { 
  createTable,
  deleteTaskData,
  getSelectData,
  insertTaskData,
  updateTaskData,
  updateTaskTitle,
 } from '../utils/dbUtils';
import { scheduleDailyMail } from '../jobs/emailScheduler';

const app = express();
const PORT = process.env.PORT || 3000;

const jsonPath = path.resolve('src/data/config.json');
let config: any={};

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));


//テスト用
app.get('/health', (_req: express.Request, res: express.Response) => {
  res.status(200).json({ status: 'ok' });
});

//タスクに設定するデフォルトのメールアドレスを取得
app.get('/init', (req, res) => {
  try{
    console.log("call -> get/init");
    res.status(200).json({ "emails":config["send_email"], "sendTime":config["send_time"] });
  }catch(error){
    res.status(500).json({ msg: '初期データ取得中にエラーが発生しました' });
  }
});

// データベースからタスク情報を取得
app.get('/todos', async(req: Request<{},{},{},{filter:string, user:string}>, res: Response) => {
  console.log("call -> get/todos")
  try{
      const result = TodoGetSchema.safeParse(req.query);
      if (!result.success) {
        res.status(400).json({ msg: '抽出条件の入力値が不正です', detail: result.error.issues });
        return
      }

      const { filter, user } = req.query  
      
      let conditions: any[] = [];
      let params: any[] = [];
      if (filter) {
        conditions.push('done = ?');
        params.push(Number(filter));
      }

      if (user) {
        conditions.push('email = ?');
        params.push(user);
      }

      const rows = await getSelectData(conditions, params);
      //タスクデータと初期値のメールリスト、自動メール送信時間を返す
      res.status(200).json({ "taskdata":rows });

    }catch(err){
      res.status(500).json({ msg: 'タスク取得中にエラーが発生しました' });
    }
});


//タスクデータを追加
app.post('/todos', async(req: Request<{}, {}, {title:string, emailList:string[]}>, res: Response) => {
  console.log("call -> post/todos");

  try{
    const result = TodoAddSchema.safeParse(req.body);
    if (!result.success) {
      res.status(400).json({ msg: '登録する入力値が不正です', detail: result.error.issues });
      return
    }

    const { title, emailList} = req.body;
  
    if (emailList.length === 0) {
      res.status(400).json({ msg: 'メールアドレスが指定されていません' });
      return;
    }
    
    const check_row = await getSelectData(['title = ?'], [title]);
  
    if (check_row.length >0) {
      res.status(500).json({ msg: 'このタスクは既に存在します。別の名前で登録してください' });
      return;
    } 
  
    for (const email of emailList) {
      const params = [title, false ,email]
      await insertTaskData(params);
    }
    res.sendStatus(200)
    
  }catch(err){
    res.status(500).json({ msg: 'タスク登録中にエラーが発生しました' });
  }
});


//タスクデータ実施更新
app.patch('/todos', async(req: Request<{}, {}, {title:string, done:string, email:string}>, res: Response) => {
  console.log("call -> patch/todos");

  try{
    const result = TodoUpdateSchema.safeParse(req.body);
    if (!result.success) {
      res.status(400).json({ msg: '更新する入力値が不正です', detail: result.error.issues });
      return
    }
    const { title, done, email } = req.body;
    const params = [Number(done), title, email];
    await updateTaskData(params);
    res.sendStatus(200);
  }catch(err){
    res.status(500).json({ msg: 'タスク更新中にエラーが発生しました' });
  }
});


//タスクデータ削除
app.delete('/todos', async(req: Request<{}, {}, {title:string}>, res:Response) => {
  console.log("call -> delete/todos");
  
  try{
    const result = TodoDeleteSchema.safeParse(req.body);
    if (!result.success) {
      res.status(400).json({ msg: '削除するタイトルが不正です', detail: result.error.issues });
      return
    }
    const { title } = req.body
    const cnt_update = await deleteTaskData([title]);
    if (cnt_update > 0) res.sendStatus(200); else res.sendStatus(300)

  }catch(err){
    res.status(500).json({ msg: 'タスク削除中にエラーが発生しました' });
  }    
});


// タスクのタイトルを更新
app.patch('/todos/updateTitle', async(req: Request<{}, {}, {oldTitle:string, newTitle:string}>, res: Response) => {
  console.log("call -> patc/todos/updateTitle");

  try{
    const result = TodoTitleUpdateSchema.safeParse(req.body);
    if (!result.success) {
      res.status(400).json({ msg: '更新する入力値が不正です', detail: result.error.issues });
      return
    }
    const { oldTitle, newTitle } = req.body;
    const check_row = await getSelectData(['title = ?'], [newTitle]);
    if (check_row.length >0) {
      res.status(400).json({ msg: 'このタスク名は既に存在します。別の名前で登録してください' });
      return;
    } 
      
    const params = [newTitle, oldTitle]
    await updateTaskTitle(params);
    
    res.sendStatus(200);
  }catch(err){
    res.status(500).json({ msg: 'タスクタイトルの更新中にエラーが発生しました' });
  }
});


//タスクに設定するデフォルトのメールアドレスを更新
app.post('/default_email', async(req: Request<{}, {}, {emailList:string}>, res: Response) => {
  console.log("call -> post/default_email");
  
  try {
    const { emailList } = req.body;

    const temp_emails = emailList
      .split(',')
      .map(line => line.trim())
      .filter(line => line.length > 0 && /^[\w.+-]+@[\w.-]+\.\w+$/.test(line)); // 簡易バリデーション

    if (temp_emails.length === 0) {
      res.status(400).json({ msg: '有効なメールアドレスが存在しません' });
      return;
    }

    config["send_email"] = temp_emails;
    fs.writeFileSync(jsonPath, JSON.stringify(config, null, 2), 'utf-8');
    console.log("更新するメールアドレス：",temp_emails);

    res.status(200).json({ msg: '送付先メールアドレスを更新しました', emails: temp_emails });

  } catch (error) {
    res.status(500).json({ msg: 'メールアドレスの更新中にエラーが発生しました' });
  }
});



//メール送信時刻更新
app.post('/send-time', async(req: express.Request<{}, {}, {update_sendtime:string}>, res: express.Response) => {
  console.log("call -> post/send_time");

  try{    
    const result = TodoSendTimeSchema.safeParse(req.body);
    if (!result.success) {
      res.status(400).json({ msg: '更新する入力値が不正です', detail: result.error.issues });
      return
    }

    const { update_sendtime } = req.body;  
    config["send_time"] = update_sendtime;
  
    fs.writeFileSync(jsonPath, JSON.stringify(config, null, 2), 'utf-8');
    scheduleDailyMail();  

    res.status(200).json({update_sendtime:update_sendtime});
  }catch(error){
    res.status(500).json({ msg: '自動メール送信の時刻更新中にエラーが発生しました' });
  }  
});


// 初期化関数
export async function initializeEmailList(): Promise<void> {

  console.log("call -> initializeEmailList");

  //設定ファイルがあるフォルダが存在しない場合、フォルダ、ファイルを作成する
  const filePath = path.resolve(jsonPath);
  const dirPath = path.dirname(jsonPath);

  if (!fs.existsSync(dirPath)) fs.mkdirSync(dirPath, { recursive: true });
  if (!fs.existsSync(filePath)) fs.writeFileSync(filePath, '');

  config = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

  try {
    await createTable();
  } catch (err) {
    console.error('DB初期化失敗:', err);
  }

  if (process.env.NODE_ENV != 'test'){
    scheduleDailyMail();
  } else{
    console.log("-----Testモード実行中-----")
  }
}


// サーバ起動
app.listen(PORT, () => {
  initializeEmailList();
  console.log(`ToDo GUIサーバーが http://localhost:${PORT} で起動しました`);
});

export { app };

