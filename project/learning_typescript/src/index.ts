// src/index.ts
// src/index.ts
import * as fs from "fs";

const FILE = "todos.json";

type Todo = {
  title: string;
  done: boolean;
};

// JSONファイルからToDoを読み込み
function loadTodos(): Todo[] {
  if (!fs.existsSync(FILE)) return [];
  const data = fs.readFileSync(FILE, "utf-8");
  return JSON.parse(data);
}

// JSONファイルにToDoを書き込み
function saveTodos(todos: Todo[]) {
  fs.writeFileSync(FILE, JSON.stringify(todos, null, 2));
}

// コマンド処理
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case "add":
    const item = args.slice(1).join(" ");
    const todos = loadTodos();
    todos.push({ title: item, done: false });
    saveTodos(todos);
    console.log(`✅ 追加: "${item}"`);
    break;

  case "list":
    const list = loadTodos();
    const filter = args[1]; // 追加引数: done / todo

    const filtered = list.filter((t) => {
      if (filter === "done") return t.done;
      if (filter === "todo") return !t.done;
      return true; // 何も指定がなければ全件
    });

    if (filtered.length === 0) {
      console.log("📭 ToDoがありません");
    } else {
      list.forEach((t, i) => {
        const status = t.done ? "✅" : "❌";
        console.log(`${i + 1}. [${status}] ${t.title}`);
      });
    }
    break;


  case "remove":
    const index = parseInt(args[1]) - 1;
    const current = loadTodos();
    if (index >= 0 && index < current.length) {
      const removed = current.splice(index, 1);
      saveTodos(current);
      console.log(`🗑️ 削除: "${removed[0]}"`);
    } else {
      console.log("⚠️ 正しい番号を指定してください");
    }
    break;
    case "done":
      const doneIndex = parseInt(args[1]) - 1;
      const items = loadTodos();
      if (doneIndex >= 0 && doneIndex < items.length) {
        items[doneIndex].done = true;
        saveTodos(items);
        console.log(`🎉 完了: "${items[doneIndex].title}"`);
      } else {
        console.log("⚠️ 正しい番号を指定してください");
      }
      break;

  default:
    console.log("使い方: add/list/remove");
}
