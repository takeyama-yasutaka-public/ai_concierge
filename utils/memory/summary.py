"""
要約管理用モジュール。
会話要約の取得・保存に関する関数をまとめています。
"""
from typing import Any

def get_last_summary(supabase, user_id: str) -> str:
    """
    指定したユーザーの最新の会話要約を取得します。
    supabase: Supabaseクライアント
    user_id: ユーザーID
    戻り値: 最新の要約テキスト（なければ「（前回要約なし）」）
    """
    data = supabase.table("summary_log").select("summary").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute().data
    return data[0]["summary"] if data else "（前回要約なし）"


def save_summary(supabase, user_id: str, summary: str, created_at: str):
    """
    会話要約を保存します（最大5000文字）。
    supabase: Supabaseクライアント
    user_id: ユーザーID
    summary: 要約テキスト
    created_at: 作成日時（ISO形式）
    """
    supabase.table("summary_log").insert([
        {"user_id": user_id, "summary": summary[:5000], "created_at": created_at}
    ]).execute() 