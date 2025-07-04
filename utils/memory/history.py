"""
履歴管理用モジュール。
チャット履歴の取得・保存に関する関数をまとめています。
"""
from typing import List, Dict, Any

def get_chat_history(supabase, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    指定したユーザーのチャット履歴を最新から順に最大limit件取得します。
    supabase: Supabaseクライアント
    user_id: ユーザーID
    limit: 取得する履歴の最大件数（デフォルト20件）
    戻り値: 履歴データのリスト
    """
    data = (
        supabase.table("chat_history")
        .select("role, message, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
    )[::-1]
    return data

def save_chat_history(supabase, user_id: str, role: str, message: str, created_at: str):
    """
    チャット履歴を1件保存します。
    supabase: Supabaseクライアント
    user_id: ユーザーID
    role: 'user'または'assistant'
    message: メッセージ本文
    created_at: 作成日時（ISO形式）
    """
    supabase.table("chat_history").insert([
        {"user_id": user_id, "role": role, "message": message, "created_at": created_at}
    ]).execute() 