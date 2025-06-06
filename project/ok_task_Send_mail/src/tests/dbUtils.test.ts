import { getSelectData, 
  createTable, 
  insertTaskData, 
  deleteTaskData,
  updateTaskTitle 
} from '../utils/dbUtils';



test("createDb が todos テーブルを作成する", async () => {
  process.env.NODE_ENV = 'test'; // ← test用のDBを使わせる
  // テーブル作成処理
  await createTable();
});


test('タスクデータ追加テスト', async () => {
  process.env.NODE_ENV = 'test';
  const params = ["test_title", false, "test_messages"];
  expect(await insertTaskData(params)).toBe(1);
});

test('タスクデータの取得テスト', async () => {
  process.env.NODE_ENV = 'test';

  const sql = '';
  const rows = await getSelectData(sql, []);
  expect(rows.length).toBe(1);

});
test('タスクデータのタイトル更新テスト', async () => {
  process.env.NODE_ENV = 'test';
  const params = ["test_new_title", "test_title"];
  expect(await updateTaskTitle(["test_new_title", "test_title"])).toBe(1);

});

test('タスクデータ削除テスト', async () => {
  process.env.NODE_ENV = 'test';
  expect(await deleteTaskData(["test_new_title"])).toBe(1);
});


