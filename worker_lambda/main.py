from fastapi import FastAPI, HTTPException, Request
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, ClientError
import asyncio
from worker_lambda.usecase.init import do_init
from worker_lambda.config import Settings

app = FastAPI()
settings = Settings()
logger = settings.logger

# 排他制御用のフラグとロック
init_in_progress = False
init_lock = asyncio.Lock()

# docker-compose.ymlで環境変数を指定することにより、コンテナ起動、直接起動にかかわらず動くようにする
URI = settings.NEO4J_URI
AUTH = (settings.NEO4J_USER, settings.NEO4J_PASSWORD)

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
        await asyncio.to_thread(do_init)
    except Exception as e:
        logger.error(f"Error initializing Neo4j: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        async with init_lock:
            init_in_progress = False
    return {"message": "Initialized successfully"}