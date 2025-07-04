import os
import hashlib
from pinecone import Pinecone
from utils.deep_research.generate_ascii_id import generate_ascii_id

# --- Pineconeクライアントとインデックスの初期化 ---
PINECONE_HOST = os.getenv("PINECONE_HOST")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")

# インデックスは事前に管理画面で作成しておく
index = pc.Index(index_name, host=PINECONE_HOST)

async def query_vector(namespace: str, vector: list[float], top_k: int = 1):
    """
    ベクトルデータベース（Pinecone）から類似ベクトルを検索する関数
    Args:
        namespace (str): 名前空間（ユーザーIDなど）
        vector (list[float]): 検索対象のベクトル
        top_k (int): 取得する類似ベクトルの数
    Returns:
        list: 類似度の高いベクトルのリスト（スコア・メタデータ付き）
    """
    try:
        res = index.query(
            namespace=namespace,
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        return res.matches
    except Exception as e:
        return []

async def upsert_vector(namespace: str, id: str, vector: list[float], metadata: dict = None):
    """
    ベクトルデータをPineconeに保存（アップサート）する関数
    Args:
        namespace (str): 名前空間（ユーザーIDなど）
        id (str): ベクトルの一意ID
        vector (list[float]): 保存するベクトルデータ
        metadata (dict, optional): ベクトルに付随するメタデータ
    Returns:
        bool: 保存が成功した場合はTrue、失敗した場合はFalse
    """
    try:
        index.upsert(
            namespace=namespace,
            vectors=[{
                "id": id,
                "values": vector,
                "metadata": metadata or {}
            }]
        )
        return True
    except Exception as e:
        return False
