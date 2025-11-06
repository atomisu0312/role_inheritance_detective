import csv
from pathlib import Path
from neo4j import GraphDatabase
from fastapi.templating import Jinja2Templates
from worker_lambda.config import Settings

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

settings = Settings()
logger = settings.logger

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

def do_init():
    logger.info("Initialization started")
    csv_dir = Path(settings.STATIC_CSV_DIR)
    
    logger.info(f"Reading CSV from: {csv_dir}")
    rows = list(read_relation_csv(str(csv_dir)))
    
    params_for_apoc = [{"name": row["node"]} for row in rows]
    
    init_query = templates.env.get_template("init.cipher").render()
    logger.debug(f"Rendered query: {init_query[:200]}...")

    auth = (settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    logger.info(f"Connecting to Neo4j at {settings.NEO4J_URI}")
    
    with GraphDatabase.driver(settings.NEO4J_URI, auth=auth) as driver:
        with driver.session(database=settings.DATABASE) as session:
            logger.info("Executing Neo4j query...")
            result = session.run(init_query, {"csv_params": params_for_apoc})
            # クエリ結果を消費（Neo4jのクエリは明示的に結果を消費する必要がある）
            result_list = list(result)
            logger.info(f"Query executed successfully. Result count: {len(result_list)}")
    
    logger.info("Initialization completed successfully")