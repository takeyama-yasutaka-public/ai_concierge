"""
要約生成用プロンプトの定義モジュール。
会話履歴の要約を生成するためのプロンプトを定義しています。
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

def build_summary_prompt(last_summary: str):
    """
    前回までの要約と今回の会話履歴をもとに、最新の要約を生成するプロンプトを作成します。
    last_summary: 前回までの要約テキスト
    戻り値: ChatPromptTemplateインスタンス
    """
    return ChatPromptTemplate.from_messages([
        SystemMessage(content=f"以下は前回までの会話要約です：\n{last_summary}\nそして、以下が今回の新しい会話履歴です："),
        MessagesPlaceholder(variable_name="messages"),
        SystemMessage(content="これらを統合し、重複や矛盾を整理した最新の要約を日本語で作成してください。事実・意図・感情・話題の流れも含めてください。")
    ]) 