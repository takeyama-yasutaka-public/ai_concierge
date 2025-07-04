from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターのインポート
from api.chat import router as chat_router
from api.history import router as history_router
app.include_router(chat_router)
app.include_router(history_router)
