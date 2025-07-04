"""
知識グラフ（KG）管理用モジュール。
会話から抽出した三つ組み（KG）の取得・保存に関する関数をまとめています。
"""
from typing import Any

def get_last_kg(supabase, user_id: str) -> str:
    """
    指定したユーザーの最新の知識三つ組み（KG）を取得します。
    supabase: Supabaseクライアント
    user_id: ユーザーID
    戻り値: 最新のKGテキスト（なければ「（前回KGなし）」）
    """
    data = supabase.table("kg_facts").select("object").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute().data
    return data[0]["object"] if data else "（前回KGなし）"


def save_kg(supabase, user_id: str, kg_text: str, created_at: str):
    """
    知識三つ組み（KG）を保存します（最大5000文字）。
    supabase: Supabaseクライアント
    user_id: ユーザーID
    kg_text: KGテキスト
    created_at: 作成日時（ISO形式）
    """
    supabase.table("kg_facts").insert([
        {"user_id": user_id, "subject": "会話", "relation": "知識", "object": kg_text[:5000], "created_at": created_at}
    ]).execute() 