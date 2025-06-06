//jest.mock('../utils/dbUtils'); 
jest.mock('nodemailer');
import request from 'supertest';
import nodemailer from 'nodemailer';
import { app } from '../gui/server';
import { sendEmail } from '../utils/email';
import { initializeEmailList } from '../gui/server';
import * as path from 'path';
import sqlite3 from 'sqlite3';

// nodemailerのモック
const sendMailMock = jest.fn();
(nodemailer.createTransport as jest.Mock).mockReturnValue({
  sendMail: sendMailMock,
});

describe('sendEmail', () => {
  beforeEach(() => {
    sendMailMock.mockClear();
  });

  it('正しい引数でメール送信を呼び出す', () => {
    sendEmail('test@example.com', 'テスト件名', 'テスト本文');
    expect(sendMailMock).toHaveBeenCalledWith(
      {
        from: 'your.email@gmail.com',
        to: 'test@example.com',
        subject: 'テスト件名',
        text: 'テスト本文',
      },
      expect.any(Function)
    );
  });
});

//初期処理用のＤＢテーブル初期化処理
export const runQuery = (db: sqlite3.Database, sql: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    db.run(sql, (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
};

describe('APIテスト', () => {
  const DB_PATH = path.resolve('src/data/todos.db');
  const db = new sqlite3.Database(DB_PATH);

  
  beforeAll(async() => {
    console.log('テスト実施前の検証用テーブル削除処理')
    await runQuery(db, `DROP TABLE IF EXISTS todos_dev`);
  });


  

  test('初期化処理テスト', async() => {
    await initializeEmailList();    
    const tableExists = await new Promise<boolean>((resolve, reject) => {
      db.get(
        `SELECT name FROM sqlite_master WHERE type='table' AND name='todos_dev'`,
        (err, row) => {
          if (err) return reject(err);
          resolve(!!row); // row があれば true（テーブル存在）
        }
      );
    });  
    expect(tableExists).toBe(true);
  });
  
  
  describe('タスクデータ追加テスト', () => {
    test('OK post/todos', async () => {
      const title = 'test-task-title';
      const emailList = ['test@example.com'];
    
      // タスクを追加（API経由）
      const res = await request(app)
        .post('/todos')
        .send({ title, emailList });
      expect(res.status).toBe(200);
    });
  
    test('NG パラメータ型 post/todos', async () => {
      const title = 'test-task-title';
      const emailList = 'test@example.com';
    
      // タスクを追加（API経由）
      const res = await request(app)
        .post('/todos')
        .send({ title, emailList });
      expect(res.status).toBe(400);
    });
  
    test('NG メールアドレス post/todos', async () => {
      const title = 'test-task-title';
      const emailList = '[testexample.com]';
    
      // タスクを追加（API経由）
      const res = await request(app)
        .post('/todos')
        .send({ title, emailList });
      expect(res.status).toBe(400);
    });
  });

  describe('タスクデータ取得テスト', () => {
    test('OK get/todos filter->ON', async () => {
      const filter = 0;
      const user = 'test@example.com';
    
      // タスクを追加（API経由）
      const res = await request(app)
        .get(`/todos?filter=${filter}&user=${user}`);
      expect(res.status).toBe(200);

      expect(res.body.taskdata.length).toBeGreaterThan(0);
      expect(res.body.sendTime).toBeTruthy();
      expect(Array.isArray(res.body.send_email_list)).toBe(true);
    });

    
    test('OK get/todos filter->ON', async () => {
      const filter = 1;
      const user = 'test@example.com';
    
      // タスクを追加（API経由）
      const res = await request(app)
        .get(`/todos?filter=${filter}&user=${user}`);
      expect(res.status).toBe(200);

      expect(res.body.taskdata.length).toBe(0);
      expect(res.body.sendTime).toBeTruthy();
      expect(Array.isArray(res.body.send_email_list)).toBe(true);
    });

    test('OK get/todos filter->OFF', async () => {    
      // タスクを追加（API経由）
      const res = await request(app)
        .get(`/todos?filter=&user=`);
      expect(res.status).toBe(200);
      expect(res.body.taskdata.length).toBe(1);
      expect(res.body.sendTime).toBeTruthy();
      expect(Array.isArray(res.body.send_email_list)).toBe(true);
    });

    test('NG get/todos filter->OFF', async () => {
      const filter = "aaaaa";
      const user = "aaaa";
    
      // タスクを追加（API経由）
      const res = await request(app)
        .get(`/todos?filter=${filter}&user=${user}`);
      expect(res.status).toBe(200);
      expect(res.body.taskdata.length).toBe(0);
      expect(res.body.sendTime).toBeTruthy();
      expect(Array.isArray(res.body.send_email_list)).toBe(true);
    });

  });
  
  afterAll(async() => {
    console.log('テスト実施後のＤＢクローズ')
    db.close();
  });
  
});



