from fastapi import APIRouter, Request, HTTPException
from core.auth import get_user_id_from_token
from core.chat_flow import get_chat_history, supabase
from itertools import groupby

router = APIRouter()

@router.get("/history/")
async def get_chat_history_api(request: Request):
    """
    認証ユーザーの直近20件のチャット履歴を返すAPI
    """
    try:
        user_id = get_user_id_from_token(request)
        chat_history_data = get_chat_history(supabase, user_id, limit=20)
        # created_atで昇順ソート
        chat_history_data = sorted(
            chat_history_data,
            key=lambda msg: msg.get("created_at")
        )
        # 同じcreated_atのセットがあれば必ずユーザー→AIの順で並べる
        messages = []
        for created_at, group in groupby(chat_history_data, key=lambda msg: msg.get("created_at")):
            group_list = list(group)
            users = [m for m in group_list if m["role"] == "user"]
            ais = [m for m in group_list if m["role"] == "assistant"]
            # 交互に並べる
            for u, a in zip(users, ais):
                messages.append({"sender": "ユーザー", "message": u["message"]})
                messages.append({"sender": "AI", "message": a["message"]})
            # 余りがあれば追加
            for u in users[len(ais):]:
                messages.append({"sender": "ユーザー", "message": u["message"]})
            for a in ais[len(users):]:
                messages.append({"sender": "AI", "message": a["message"]})
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"履歴取得エラー: {str(e)}") 