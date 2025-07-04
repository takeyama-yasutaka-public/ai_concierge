import os
import uuid
from openai import OpenAI
from open_deep_research.graph import builder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

REPORT_STRUCTURE = """Use this structure to create a report on the user-provided prompt:\nalways make the report in Japanese.\n1. はじめに\n2. 本文（複数セクション）\n3. 結論／要点まとめ\n"""

def create_thread():
    return {
        "configurable": {
            # スレッドごとに一意なID
            "thread_id": str(uuid.uuid4()),
            # Web検索APIの種類（tavilyを利用）
            "search_api": "tavily",
            # 検索APIの追加設定（検索結果数は最小限に）
            "search_api_config": {"num_results": 1},
            # 検索の深さ（1なら1段階のみ）
            "max_search_depth": 1,
            # 1回の検索で取得する最大検索結果数（1が最小負荷）
            "max_search_results": 1,
            # 1プロンプトで何回検索クエリを投げるか（1が最小負荷）
            "number_of_queries": 1,
            # プランナー（検索計画立案）に使うプロバイダ
            "planner_provider": "openai",
            # プランナーに使うモデル
            "planner_model": "gpt-4.1-mini",
            # レポート生成（要約）に使うプロバイダ
            "writer_provider": "openai",
            # レポート生成に使うモデル（mini系が最小負荷）
            "writer_model": "gpt-4.1-mini",
            # 再帰的な検索の上限（通常1でOK）
            "recursion_limit": 1,
            # レポートの構成テンプレート
            "report_structure": REPORT_STRUCTURE,
        }
    }

async def run_deep_research(prompt: str) -> str:
    """
    open-deep-researchを用いてWeb検索・要約レポートを生成する非同期関数。
    prompt: ユーザーからの質問・指示文
    return: 生成された日本語レポート（失敗時はエラーメッセージ）
    """
    import traceback
    try:
        thread = create_thread()
        # ステップ1: 初期リサーチ（検索・分析）
        async for _ in graph.astream({"topic": prompt}, thread, stream_mode="updates"):
            pass
        # ステップ2: レポート生成
        async for _ in graph.astream(Command(resume=True), thread, stream_mode="updates"):
            pass
        # 最終状態からレポートを取得
        final_state = graph.get_state(thread)
        report = final_state.values.get('final_report')
        if not report:
            return "検索結果からレポートを生成できませんでした。しばらく時間をおいて再試行してください。"
        return report
    except RuntimeError as e:
        # LangGraphの実行コンテキスト外でget_config()が呼ばれた場合の特別なエラー処理
        if "get_config outside of a runnable context" in str(e):
            # このエラーは依存パッケージのバージョンや実行環境の差異で発生することがある
            traceback.print_exc()
            return "内部エラー：AIリサーチエンジンの実行コンテキストに問題が発生しました。管理者にご連絡ください。"
        # その他のRuntimeErrorもcatchしてサーバーが落ちないようにする
        traceback.print_exc()
        return "内部エラー：AIリサーチエンジンで予期しないエラーが発生しました。"
    except Exception as e:
        # 予期しない例外もcatchしてサーバーが落ちないようにする
        traceback.print_exc()
        if "429" in str(e) or "rate_limit" in str(e).lower():
            return "検索APIのレート制限に達しました。しばらく時間をおいてから再試行してください。"
        return "検索中にエラーが発生しました。しばらく時間をおいて再試行してください。" 