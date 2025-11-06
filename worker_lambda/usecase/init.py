import os 
import csv
from pathlib import Path
from neo4j import GraphDatabase
from fastapi.templating import Jinja2Templates


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

STATIC_CSV_DIR = os.getenv("STATIC_CSV_DIR", "../target_dir")
URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "neo4jpassword"))

DATABASE = "neo4j"

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
  rows = read_relation_csv(STATIC_CSV_DIR)
  params_for_apoc = [{"name": row["node"]} for row in rows]
  init_query = templates.env.get_template("init.cipher").render()
  
  with GraphDatabase.driver(URI, auth=AUTH) as driver:
      with driver.session(database=DATABASE) as session:
          session.run(init_query, {"csv_params": params_for_apoc})