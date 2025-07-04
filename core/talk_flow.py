"""
AI応答生成専用モジュール。
このファイルは、会話履歴（messages配列）をもとにAIの返答のみを生成します。
要約や知識グラフ（KG）の生成、記憶の保存などは呼び出し元で行います。
"""
from core.config import OPENAI_API_KEY, OPENAI_TALK_MODEL
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from utils.prompt.talk_prompt import talk_prompt

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_TALK_MODEL)

async def talk_mode_flow(user_id: str, messages, kg=None, summary=None):
    """
    AI応答生成のみを担当する関数です。
    - user_id: ユーザーID
    - messages: HumanMessage/AIMessageのリスト（会話履歴＋今回のuser発話を含む）
    - kg: 知識グラフのテキスト
    - summary: 要約のテキスト
    戻り値: {"reply": AIの返答テキスト}
    ※要約やKG生成、記憶の保存はこの関数では行いません。
    """
    # 1. ChatMessageHistoryに履歴を追加
    # LangChainのChatMessageHistoryはAI応答生成時に履歴として使うためのクラスです。
    # messages配列（HumanMessage/AIMessageのリスト）をChatMessageHistoryに変換します。
    chat_history = ChatMessageHistory()
    for msg in messages:
        if isinstance(msg, HumanMessage):
            chat_history.add_user_message(msg.content)
        elif isinstance(msg, AIMessage):
            chat_history.add_ai_message(msg.content)

    # 2. AI応答生成
    # RunnableWithMessageHistoryを使うことで、chat_historyの内容をプロンプトに自動で埋め込んでくれます。
    chain_with_history = RunnableWithMessageHistory(
        talk_prompt | llm,
        lambda session_id: chat_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    # 3. inputは直近のHumanMessage（ユーザー発話）の内容を抽出して使います。
    user_input = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break
    # 4. OpenAI APIを呼び出してAI応答を生成します。
    response = chain_with_history.invoke(
        {
            "input": user_input,
            "chat_history": chat_history.messages,
            "kg": kg or "",
            "summary": summary or ""
        },
        {"configurable": {"session_id": user_id}}
    )
    gpt_response = response.content if hasattr(response, 'content') else str(response)

    # 5. AI応答テキストを返します。
    return {
        "reply": gpt_response
    }
