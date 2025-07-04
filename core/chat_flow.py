from supabase import create_client, Client
from core.config import SUPABASE_URL, SUPABASE_ANON_KEY, OPENAI_API_KEY, OPENAI_SUMMARY_MODEL, OPENAI_KG_MODEL
from utils.memory.history import get_chat_history, save_chat_history
from utils.memory.summary import get_last_summary, save_summary
from utils.memory.kg import get_last_kg, save_kg
from core.talk_flow import talk_mode_flow
from core.deep_research_flow import deep_research_mode_flow
from utils.prompt.summary_prompt import build_summary_prompt
from utils.prompt.kg_prompt import build_kg_prompt
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from datetime import datetime

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
llm_summary = ChatOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_SUMMARY_MODEL)
llm_kg = ChatOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_KG_MODEL)

async def chat_flow(user_id: str, prompt: str, deep_research: bool):
    # 記憶の呼び出し
    chat_history_data = get_chat_history(supabase, user_id, limit=20)
    last_summary = get_last_summary(supabase, user_id)
    last_kg = get_last_kg(supabase, user_id)

    # DB履歴をmessages配列に変換
    messages = []
    for msg in chat_history_data:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['message']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['message']))
    # 今回のユーザー発話を追加
    messages.append(HumanMessage(content=prompt))

    # モード判定
    if not deep_research:
        # トークモード
        result = await talk_mode_flow(user_id, messages, kg=last_kg, summary=last_summary)
    else:
        # ディープリサーチモード
        result = await deep_research_mode_flow(user_id,prompt)

    # AI応答をmessages配列に追加
    messages.append(AIMessage(content=result["reply"]))

    # 要約・KGの生成
    if not deep_research:
        summary_chain = build_summary_prompt(last_summary) | llm_summary
        kg_chain = build_kg_prompt(last_kg) | llm_kg
        summary_response = summary_chain.invoke({"messages": messages})
        summary_text = summary_response.content if hasattr(summary_response, 'content') else str(summary_response)
        kg_response = kg_chain.invoke({"messages": messages})
        kg_text = kg_response.content if hasattr(kg_response, 'content') else str(kg_response)
    else:
        summary_text = ""
        kg_text = ""

    now = datetime.utcnow().isoformat() + "Z"

    # チャット履歴の末尾2件（user, assistant）を保存
    last_two = messages[-2:]
    if len(last_two) == 2:
        save_chat_history(supabase, user_id, "user", last_two[0].content, now)
        save_chat_history(supabase, user_id, "assistant", last_two[1].content, now)

    # 要約・KGの保存
    if not deep_research:
        save_summary(supabase, user_id, summary_text, now)
        if kg_text and kg_text != "なし":
            save_kg(supabase, user_id, kg_text, now)

    return {
        "reply": result["reply"],
        "summary": summary_text,
        "kg": kg_text
    }
