import sqlite3 from 'sqlite3';
import * as path from 'path';
import { Todo } from '../types/interface';


const DB_PATH = path.resolve('src/data/todos.db');
const TABLE_NAME = process.env.NODE_ENV === 'test'
  ? "todos_dev"
  : "todos";

//ＤＢ作成処理
export const createTable = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH);

    db.serialize(() => {
      db.run(
        `CREATE TABLE IF NOT EXISTS ${TABLE_NAME} (
          title TEXT,
          email TEXT,
          done BOOLEAN NOT NULL DEFAULT 0,
          PRIMARY KEY (title, email)
        )`,
        (err) => {
          if (err) {
            db.close();
            return reject(err);
          }

          db.close((closeErr) => {
            if (closeErr) {
              return reject(closeErr);
            }
            resolve();
          });
        }
      );
    });
  });
};

  //ＤＢデータ取得処理
export const getSelectData = (sql_filter: Array<string>, params: Array<number | string>): Promise<Todo[]> => {
  return new Promise((resolve, reject) => {

    const whereClause = sql_filter.length > 0 ? 'WHERE ' + sql_filter.join(' AND ') : '';
    const sql = `SELECT * FROM ${TABLE_NAME} ${whereClause}`;
    console.log(sql);

    const db = new sqlite3.Database(DB_PATH);
    db.all(sql, params, (err: Error | null, rows: Todo[]) => {
      db.close(); // 必ずクローズ
      if (err) {
        console.error(`ＤＢエラー：データ取得中にエラーが発生しました。：${err}`);
        return reject(err);
      }
      resolve(rows);
    });
  });
};

//ＤＢデータ登録処理
export const insertTaskData = (params: any[]): Promise<number> => {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH);

    db.run(`INSERT INTO ${TABLE_NAME} (title, done, email) VALUES (?, ?, ?)`,
      params,
      function (this: sqlite3.RunResult, err: Error | null) {
        db.close();
        if (err) {
          console.error(`ＤＢエラー：データ登録中にエラーが発生しました。：${err}`);
          return reject(err);
        }
        resolve(this.changes);
      }
    );
  });
};

//ＤＢデータ更新処理　完了フラグ
export const updateTaskData = (params: any[]): Promise<number> => {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH);
    db.run(`UPDATE ${TABLE_NAME} SET todos = ? WHERE title = ? AND email = ?`, 
      params, 
      function (this: sqlite3.RunResult, err: Error | null) {
        db.close();
        if (err) {
          console.error(`ＤＢエラー：データ更新中にエラーが発生しました。：${err}`);
          return reject(err);
        }
        resolve(this.changes);
      }
    );
  });
};

//ＤＢデータ更新処理 タイトル
export const updateTaskTitle = (params: any[]): Promise<number> => {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH);
    db.run(`UPDATE ${TABLE_NAME} SET title = ? WHERE title = ?`, 
      params, 
      function (this: sqlite3.RunResult, err: Error | null) {
        db.close();
        if (err) {
          console.error(`ＤＢエラー：データ更新中にエラーが発生しました。：${err}`);
          return reject(err);
        }
        resolve(this.changes);
      }
    );
  });
};

//ＤＢデータ削除処理
export const deleteTaskData = (params: any[]): Promise<number> => {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH);
    db.run(
      `DELETE FROM ${TABLE_NAME} WHERE title = ?`,
      params,
      function (this: sqlite3.RunResult, err: Error | null) {
        db.close();
        if (err) {
          console.error(`ＤＢエラー：データ削除中にエラーが発生しました。：${err}`);
          return reject(err);
        }
        resolve(this.changes);
      }
    );
  });
};