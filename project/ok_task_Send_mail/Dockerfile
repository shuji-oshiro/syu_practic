# ベースイメージ
FROM node:18

# 作業ディレクトリを作成
WORKDIR /app

# パッケージ関連コピーしてインストール
COPY package*.json ./
RUN npm install

# ソースコードをコピー
COPY . .

# 必要なポートを公開
EXPOSE 3000

# サーバー起動（ts-node使用）
CMD ["npx", "ts-node", "src/gui/server.ts"]
