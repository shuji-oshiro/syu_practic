import fs from 'fs';
import path from 'path';
import sqlite3 from 'sqlite3';

const TEST_DB_PATH = path.resolve('src/data/test_todos.db');

export function resetTestDatabase(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!fs.existsSync(TEST_DB_PATH)) {
      return resolve(); // ファイルなければそのまま終了
    }

    // DBを開く
    const db = new sqlite3.Database(TEST_DB_PATH, (openErr) => {
      if (openErr) {
        // 開けなかった（＝ロックされてない）→削除を試みる
        try {
          fs.unlinkSync(TEST_DB_PATH);
          console.log('🧪 テストDBを削除しました');
          return resolve();
        } catch (err) {
          return reject(err);
        }
      }

      // 開けた → 正しく閉じてから削除
      db.close((closeErr) => {
        if (closeErr) return reject(closeErr);
        try {
          fs.unlinkSync(TEST_DB_PATH);
          console.log('🧪 テストDBを安全に削除しました');
          resolve();
        } catch (err) {
          reject(err);
        }
      });
    });
  });
}
