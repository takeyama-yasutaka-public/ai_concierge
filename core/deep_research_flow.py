import os
import uuid
import hashlib
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from open_deep_research.graph import builder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from utils.deep_research.run_deep_research import run_deep_research
from utils.deep_research.generate_ascii_id import generate_ascii_id
from utils.deep_research.vector import upsert_vector

# Pinecone（ベクトルDB）初期化
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")
dimension = int(os.getenv("PINECONE_DIM", 1536))
region = os.getenv("PINECONE_REGION")

# インデックスがなければ作成
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=region)
    )

index = pc.Index(index_name)

# OpenAIクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LangGraphメモリ管理初期化
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

REPORT_STRUCTURE = """Use this structure to create a report on the user-provided prompt:\nalways make the report in Japanese.\n1. はじめに\n2. 本文（複数セクション）\n3. 結論／要点まとめ\n"""

def should_use_existing_answer(prompt: str) -> bool:
    """
    ユーザーの意図を判定して、既存の回答を使うべきかどうかを判断する関数
    Args:
        prompt (str): ユーザーの質問
    Returns:
        bool: 既存の回答を使うべき場合はTrue、新規検索すべき場合はFalse
    """
    # 新規検索を求めるキーワード
    search_keywords = [
        "最新", "新", "今", "現在", "最近", "調べ", "検索", "探", "調査"
    ]
    # 既存情報を求めるキーワード
    existing_keywords = [
        "知っ", "覚え", "保存", "以前", "既存", "過去", "前", "記憶"
    ]
    for keyword in search_keywords:
        if keyword in prompt:
            return False
    for keyword in existing_keywords:
        if keyword in prompt:
            return True
    return True

async def has_rag_memory(user_id: str, prompt: str, threshold: float = 0.3) -> bool:
    """
    Pineconeで過去の類似質問があるか判定（閾値以上ならTrue）
    """
    try:
        vector_id = generate_ascii_id(prompt)
        emb = client.embeddings.create(input=prompt, model="text-embedding-3-small")
        vector = emb.data[0].embedding
        res = index.query(
            namespace=user_id,
            vector=vector,
            top_k=1,
            include_metadata=True
        )
        if res.matches and res.matches[0].score > threshold:
            return True
        return False
    except Exception:
        return False

async def get_rag_answer(user_id: str, prompt: str) -> str:
    """
    Pineconeから最も類似した過去回答（summary）を取得
    """
    try:
        emb = client.embeddings.create(input=prompt, model="text-embedding-3-small")
        vector = emb.data[0].embedding
        res = index.query(
            namespace=user_id,
            vector=vector,
            top_k=1,
            include_metadata=True
        )
        if res.matches and res.matches[0].metadata:
            metadata = res.matches[0].metadata
            answer = metadata.get('summary', '')
            if answer:
                return answer
        return ""
    except Exception:
        return ""

async def get_deep_research_answer(user_id: str, prompt: str, report: str) -> dict:
    """
    Webリサーチ結果をベクトル化しPineconeへ保存、その内容を返す
    """
    emb = client.embeddings.create(input=report, model="text-embedding-3-small")
    vec = emb.data[0].embedding
    vector_id = generate_ascii_id(prompt)
    await upsert_vector(
        namespace=user_id,
        id=vector_id,
        vector=vec,
        metadata={"summary": report, "original_prompt": prompt}
    )
    return {"reply": report}

async def deep_research_mode_flow(user_id: str, prompt: str) -> dict:
    """
    deep_researchモードのメインフロー。
    1. should_use_existing_answerで既存回答利用判定
    2. 既存回答利用ならRAG検索し、見つかれば返す
    3. なければWebリサーチ・要約・保存
    """
    try:
        if should_use_existing_answer(prompt):
            if await has_rag_memory(user_id, prompt):
                answer = await get_rag_answer(user_id, prompt)
                return {"reply": answer}
        report = await run_deep_research(prompt)
        return await get_deep_research_answer(user_id, prompt, report)
    except Exception as e:
        return {"reply": f"情報収集・保存中にエラーが発生しました: {str(e)}"}