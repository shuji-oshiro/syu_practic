import fs from 'fs';
import path from 'path';
import nodeCron, { ScheduledTask } from 'node-cron';
import { Todo } from '../types/interface';
import { sendEmail } from '../utils/email';
import { getSelectData } from '../utils/dbUtils';


const jsonPath = path.resolve('src/data/config.json');

let mailCronJob: ScheduledTask | null = null; // ✅ モジュールスコープで保持


//自動メール送信タイマー処理
export function scheduleDailyMail() {
  try {
    const config = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
    const [hour, minute] = config["send_time"].split(":");
    const mail_title = config["title_text"];
    const mail_text_template = config["msg_text"];

    // 既存のジョブがあれば停止
    if (mailCronJob) {
      mailCronJob.stop();
      mailCronJob = null;
    }

    // スケジュール設定（非同期対応）
    mailCronJob = nodeCron.schedule(
      `${minute} ${hour} * * *`,
      async () => {
        try {
          const rows: Todo[] = await getSelectData("SELECT * FROM todos WHERE done = ?", [0]);

          for (const todo of rows) {
            const mail_text = mail_text_template.replace('{task_text}', todo.title);
            if (todo.email) {
              sendEmail(todo.email, mail_title, mail_text);
            }
          }
        } catch (err) {
          console.error("メール送信処理中にエラー:", err);
        }
      },
      {
        timezone: 'Asia/Tokyo',
      }
    );

    console.log(`自動メール送信スケジュール：${hour}:${minute}（Asia/Tokyo）`);

  } catch (error) {
    console.error("自動メール送信設定読み込み中にエラー:", error);
  }
}
