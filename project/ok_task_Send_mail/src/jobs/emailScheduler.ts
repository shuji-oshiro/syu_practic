import path from 'path';
import sqlite3 from 'sqlite3';
import { sendEmail } from '../utils/email';
import nodeCron, { ScheduledTask } from 'node-cron';


const DB_PATH = process.env.NODE_ENV === 'test'
  ? path.resolve('src/data/test_todos.db')
  : path.resolve('src/data/todos.db');

let mailCronJob: ScheduledTask | null = null; // ✅ モジュールスコープで保持


export function scheduleDailyMail(hour: string, minute: string, title: string, textTemplate: string) {
  
  // すでにジョブがあれば止める
  if (mailCronJob) {
    mailCronJob.stop();
    mailCronJob = null;
  }

  mailCronJob = nodeCron.schedule(`${minute} ${hour} * * *`, () => {
    const db = new sqlite3.Database(DB_PATH);
    db.all('SELECT * FROM todos WHERE done = 0', (err, rows) => {
      if (err) return console.error(err);
      rows.forEach((todo: any) => {
        const mail_text = textTemplate.replace('{task_text}', todo.title);
        if (todo.email) {
          sendEmail(todo.email, title, mail_text);
        }
      });
    });
  }, {
    timezone: 'Asia/Tokyo'
  });

  console.log(`自動メール送信時刻：${hour}:${minute}`)
}
