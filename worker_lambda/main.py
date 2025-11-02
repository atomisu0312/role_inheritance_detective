from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, ClientError
import os

app = FastAPI()

# docker-compose.ymlで環境変数を指定することにより、コンテナ起動、直接起動にかかわらず動くようにする
URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "neo4jpassword"))

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
            detail=f"ServiceUnavailableError!!! Neo4j connection failed: {str(e)}"
        )
    except ClientError as e:
        raise HTTPException(
            status_code=503,
            detail=f"ClientError!!! Client Config in your Implements is Wrong: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Some Error!!! An unexpected error occurred: {str(e)}"
        )