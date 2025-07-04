# AI コンシェルジュ

## 1. プロジェクト概要（Overview）

### プロジェクト名

AI コンシェルジュ - AI Know -（アイノ）

### 対象・目的

AI Know は、チャット型の AI コンシェルジュサービスとして、ユーザーの質問に自然な形で対応し、必要に応じて深掘り調査を行うことが可能な WEB アプリケーションです。トークモードとディープリサーチモードを使い分け、柔軟かつ精度の高い回答を提供します。

### 特徴

- Next.js + FastAPI + Supabase のモダンスタック構成
- GPT-4.1 mini をベースとした自然対話モデル
- 独自実装の Summary Memory / KG Memory を活用した高度な履歴理解
- ディープリサーチモードでは、Tavily 検索や RAG を活用した外部知識検索に対応
- OpenAI Embedding + Pinecone によるベクトル検索

### 想定ユースケース

- 自社サービスへの AI コンシェルジュ導入
- カスタマーサポートの効率化
- 社内情報検索や FAQ 対応の自動化
- RAG 構成を使った情報調査ツールの基盤として

## 2. システム構成（System Architecture）

### システム全体の構成

[Next.js (Vercel)]
↓↑
[FastAPI (Amazon Lightsail)]
↓↑
[Supabase (DB/Storage/Auth)]

### 主な構成要素

- フロントエンド: Next.js
- バックエンド: FastAPI
- 認証/データ管理: Supabase
- データベース: Supabase PostgreSQL
- 外部 API: OpenAI, Tavily, Pinecone

### デプロイ環境

- フロントエンド: Vercel
- バックエンド: Amazon Lightsail

## 3. 主な機能（Main Features）

### チャットフロー（Next.js）

- Supabase によるユーザー認証
- チャット履歴の取得（historyAPI）
- 質問入力＆モード選択（トーク / リサーチ）
- 回答の表示

### チャットフロー（FastAPI）

- ユーザー ID と履歴の検証
- Summary Memory / KG Memory の読込
- モード選択に応じた分岐
- トークモード：PromptTemplate を用いた対話生成
- ディープリサーチ：RAG 構成 + 外部検索
- チャット履歴の保存
- SummaryMemory / KGMemory の更新

### ディープリサーチ詳細

- SearchTool：Tavily を活用した情報検索＋ Embedding ＋ Pinecone 登録
- RetrieverTool：登録済み情報からのベクトル検索

## 4. 技術スタック（Tech Stack）

### フロントエンド

- フレームワーク: Next.js
- ホスティング: Vercel
- バックエンド連携: REST API

### バックエンド

- フレームワーク: FastAPI
- 言語: Python
- 実行環境: Amazon Lightsail + Docker

### データベース / ストレージ

- Supabase（PostgreSQL, Storage, Auth）

### 外部 API / ライブラリ

- OpenAI API (GPT-4.1 mini, Embedding)
- LangChain / LangGraph
- Pinecone（ベクトル DB）
- Tavily（外部検索）
- OpenDeepResearch

## 5. ディレクトリ構造（Project Structure）

ai_concierge
├── api/
│ ├── chat.py
│ └── history.py
├── core/
│ ├── auth.py
│ ├── chat_flow.py
│ ├── config.py
│ ├── deep_research_flow.py
│ └── talk_flow.py
├── supabase/
│ └── migrations/
│ └── 20240630_create_chat_tables.sql
├── utils/
│ ├── deep_research/
│ ├── memory/
│ └── prompt/
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env

## 6. 使用について

このプロジェクトはポートフォリオ作品として公開しているものであり、実運用や商用利用を目的としたものではありません。
無断での使用・転載・再配布は禁止しております。
