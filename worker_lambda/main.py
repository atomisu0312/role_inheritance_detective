from fastapi import FastAPI, HTTPException, Request
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, ClientError
from fastapi.templating import Jinja2Templates
import os
import logging
import asyncio
import csv
from pathlib import Path
app = FastAPI()

# 排他制御用のフラグとロック
init_in_progress = False
init_lock = asyncio.Lock()

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# docker-compose.ymlで環境変数を指定することにより、コンテナ起動、直接起動にかかわらず動くようにする
URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "neo4jpassword"))

DATABASE = "neo4j"
STATIC_CSV_DIR = os.getenv("STATIC_CSV_DIR", "../target_dir")

@app.get("/")
async def root() -> dict:
    """Neo4jに接続できるかどうかを確認する

    Raises:
        HTTPException: Neo4jに接続できない場合(503エラーを返す)

    Returns:
        dict: 接続成功時のメッセージ
    """
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            return {"message": "Connection successful!"}
    except ServiceUnavailable as e:
        raise HTTPException(
            status_code=503,
            detail=f"ServiceUnavailableError!!! Neo4j connection failed: {str(e)}",
        )
    except ClientError as e:
        raise HTTPException(
            status_code=503,
            detail=f"ClientError!!! Client Config in your Implements is Wrong: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Some Error!!! An unexpected error occurred: {str(e)}",
        )


@app.get("/test")
async def test(request: Request) -> dict:
    """テスト用のAPI"""
    # テンプレートを文字列としてレンダリング
    rendered_text = templates.env.get_template("test.j2").render(
        sample_node_name="SampleNode"
    )

    # ログに出力
    logger.info(f"Rendered template: {rendered_text}")

    return {"message": "Template rendered", "rendered_text": rendered_text}

# ヘルパー：CSV を遅延読み込みしてジェネレータで返す
def read_relation_csv(csv_dir: str):
    p = Path(csv_dir) / "relation.csv"
    if not p.exists():
        raise FileNotFoundError(f"relation.csv not found at {p}")
    with p.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        # 必要なカラムチェック（例: 'node' カラム）
        if 'node' not in reader.fieldnames:
            raise ValueError("relation.csv must contain 'node' column")
        for row in reader:
            yield row

@app.post("/init")
async def init(request: Request) -> dict:
    """Neo4jのノードを初期化するAPI（同時実行を防止）"""
    global init_in_progress
    
    # 既に実行中なら即座にエラーを返す
    async with init_lock:
        if init_in_progress:
            raise HTTPException(
                status_code=409,
                detail="Initialization is already in progress. Please wait for the current operation to complete."
            )
        init_in_progress = True
    
    try:
        # 別スレッドに処理を移管
        def do_init():
            rows = read_relation_csv(STATIC_CSV_DIR)
            with GraphDatabase.driver(URI, auth=AUTH) as driver:
                with driver.session(database=DATABASE) as session:
                    # クエリの詳細はテンプレートに記述
                    session.run(templates.env.get_template("init.cipher.j2").render(test_csv_rows = rows))
                    logger.info("Initialized successfully")
        await asyncio.to_thread(do_init)
    except Exception as e:
        logger.error(f"Error initializing Neo4j: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        async with init_lock:
            init_in_progress = False
    return {"message": "Initialized successfully"}