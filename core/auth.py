from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Request, HTTPException
import os

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def get_user_id_from_token(request: Request) -> str:
    """
    リクエストのAuthorizationヘッダーからJWTトークンを取得し、
    デコードしてuser_idを返す関数。
    - トークンが無い場合や無効な場合は401エラーを返す。
    - トークンの有効期限切れも明示的にエラー返却。
    """
    # 1. Authorizationヘッダーからトークンを取得
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="トークンがありません")

    token = auth_header.split(" ")[1]
    # 2. JWTトークンをデコードしてuser_idを取得
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="user_idが見つかりません")
        return user_id
    except ExpiredSignatureError:
        # トークンの有効期限切れ
        raise HTTPException(status_code=401, detail="認証トークンの有効期限が切れています。再ログインしてください。")
    except JWTError:
        # その他のJWTデコードエラー
        raise HTTPException(status_code=401, detail="無効なトークンです")
