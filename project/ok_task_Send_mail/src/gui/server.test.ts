import { sendEmail } from './server';
import nodemailer from 'nodemailer';
import request from 'supertest';
import { Express } from 'express';
import * as serverModule from './server';

// nodemailerのモック
jest.mock('nodemailer');
const sendMailMock = jest.fn();
(nodemailer.createTransport as jest.Mock).mockReturnValue({
  sendMail: sendMailMock,
});

// appインスタンスを取得
const app: Express = serverModule['app'] || (serverModule as any).default || serverModule;

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


describe('タスク追加・取得・削除の統合テスト', () => {
  const testTitle = '統合テストタスク';
  const testEmail = 'integration@example.com';

  it('タスクを追加し、取得し、削除し、再取得で消えていることを確認', async () => {
    // 1. タスク追加
    const addRes = await request(app)
      .post('/todos/add')
      .send({ title: testTitle, emailList: [testEmail] });
    expect(addRes.status).toBe(201);

    // 2. タスク取得
    const getRes = await request(app)
      .get('/todos')
      .query({ user: testEmail });
    expect(getRes.status).toBe(200);
    expect(getRes.body.rows.some((todo: any) => todo.title === testTitle)).toBe(true);

    // 3. タスク削除
    const delRes = await request(app)
      .delete('/todos/delete')
      .send({ title: testTitle });
    expect(delRes.status).toBe(200);

    // 4. 再取得して消えていることを確認
    const getRes2 = await request(app)
      .get('/todos')
      .query({ user: testEmail });
    expect(getRes2.status).toBe(200);
    expect(getRes2.body.rows.some((todo: any) => todo.title === testTitle)).toBe(false);
  });
});