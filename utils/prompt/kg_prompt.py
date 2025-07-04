"""
知識グラフ（KG）抽出用プロンプトの定義モジュール。
会話履歴から三つ組み（KG）を抽出するためのプロンプトを定義しています。
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

def build_kg_prompt(last_kg: str):
    """
    前回までのKGと今回の会話履歴をもとに、最新の知識三つ組みリストを生成するプロンプトを作成します。
    last_kg: 前回までのKGテキスト
    戻り値: ChatPromptTemplateインスタンス
    """
    return ChatPromptTemplate.from_messages([
        SystemMessage(content=f"以下は前回までに抽出された知識三つ組みです：\n{last_kg}\nそして、以下が今回の新しい会話履歴です："),
        MessagesPlaceholder(variable_name="messages"),
        SystemMessage(content="これらを統合し、重複を除外しつつ新たな三つ組みがあれば追加し、最新の知識三つ組みリストを日本語で作成してください。会話の流れや文脈を考慮して抽象的な知識や具体的な事実も含めてください。重複や曖昧なものは省き、できるだけ明確な知識を抽出してください。")
    ]) 