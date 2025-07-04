from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from core.auth import get_user_id_from_token
from core.chat_flow import chat_flow

router = APIRouter()

@router.post("/chat/")
async def chat_endpoint(request: Request):
    """
    チャットAPIエンドポイント。
    - リクエストからユーザーIDとプロンプト、モードを取得
    - chat_flowに処理を委譲し、AI応答・要約・KGを返す
    """
    # 1. ユーザー認証（トークンからuser_idを取得）
    user_id = get_user_id_from_token(request)
    # 2. リクエストボディからプロンプトとモードを取得
    body = await request.json()
    prompt = body.get("prompt")
    deep_research = body.get("deepResearch", False)

    # 3. チャットフロー（AI応答・要約・KG生成）を実行
    result = await chat_flow(user_id, prompt, deep_research)

    # 4. 結果をJSONで返却
    return JSONResponse(result)
