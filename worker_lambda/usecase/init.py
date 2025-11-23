import csv
from pathlib import Path
from neo4j import GraphDatabase
from fastapi.templating import Jinja2Templates
from worker_lambda.config import Settings
from worker_lambda.utils.parse import process_upper_template, extract_resource_key
import hcl2

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

settings = Settings()
logger = settings.logger

# ヘルパー：CSV を遅延読み込みしてジェネレータで返す
def read_csv(csv_dir: str, csv_file: str):
    p = Path(csv_dir) / csv_file
    if not p.exists():
        raise FileNotFoundError(f"{csv_file} not found at {p}")
    with p.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield row


# HCL2を読み込んでdictに変換する関数
def interpret_hcl2(hcl2_dir: str, hcl2_file: str) -> dict:
    with open(Path(hcl2_dir) / hcl2_file, "r") as file:
        hcl2_content = file.read()
    return hcl2.loads(hcl2_content)


# データベースロールを解釈する関数
def interpret_database_role(database_role_params: dict) -> list[dict]:
    database_role_list = []

    for database_role in database_role_params["module"]:
        key = list(database_role.keys())[0]
        role_prefix = database_role[key]["role_prefix"]
        schema_names = database_role[key]["schema_names"]
        database_name = database_role[key]["database_name"]
        for env in ["dev", "stg", "prod"]:
            for type in ["R_ROLE", "RW_ROLE"]:
                database_role_list.append(
                    {
                        "module_id": f"{env}.snowflake_database_role.{key}",
                        "role_id": key,
                        "role_name": process_upper_template(
                            role_prefix, {"var.env": env.upper()}
                        )
                        + "_"
                        + type,
                        "schema_ids": [
                            f"{env}.{extract_resource_key(schema_name)}"
                            for schema_name in schema_names
                        ],
                        "database_id": f"{env}.{extract_resource_key(database_name)}",
                        "env": env,
                        "type": type,
                    }
                )
    return database_role_list


def interpret_schema(schema_params: dict) -> list[dict]:
    schema_list = []

    for param in schema_params["resource"]:
        # logger.info(f"schema_params: {json.dumps(param,ensure_ascii=False, indent=2)}")
        schema = param["snowflake_schema"]
        key = list(schema.keys())[0]
        schema_name = schema[key]["name"]
        database_name = schema[key]["database"]
        for env in ["dev", "stg", "prod"]:
            schema_list.append(
                {
                    "module_id": f"{env}.snowflake_schema.{key}",
                    "schema_id": key,
                    "schema_name": schema_name,
                    "database_name": database_name,
                    "database_id": f"{env}.{extract_resource_key(database_name)}",
                    "env": env,
                }
            )
    return schema_list


def interpret_database(database_params: dict) -> list[dict]:
    database_list = []
    # logger.info(f"database_params: {json.dumps(database_params,ensure_ascii=False, indent=2)}")
    for param in database_params["resource"]:
        database = param["snowflake_database"]
        key = list(database.keys())[0]

        database_name = database[key]["name"]
        for env in ["dev", "stg", "prod"]:
            database_list.append(
                {
                    "module_id": f"{env}.snowflake_database.{key}",
                    "database_name": process_upper_template(
                        database_name, {"var.env": env.upper()}
                    ),
                    "env": env,
                }
            )
    return database_list


# 初期化を行う関数（エンドポイントから実行）
def do_init():
    logger.info("Initialization started")
    csv_dir = Path(settings.STATIC_CSV_DIR)
    hcl2_dir = Path(settings.STATIC_HCL_DIR)

    # Define privilege and environment lists
    PRIV_LIST_RW_ROLE_ON_DATABASE = ["USAGE ON DATABASE"]
    PRIV_LIST_R_ROLE_ON_DATABASE = ["USAGE ON DATABASE"]
    PRIV_LIST_RW_ROLE_ON_SCHEMA = [
        "USAGE ON SCHEMA",
        "CREATE TABLE ON SCHEMA",
        "CREATE VIEW ON SCHEMA",
        "INSERT ON TABLES",
        "UPDATE ON TABLES",
        "TRUNCATE ON TABLES",
        "DELETE ON TABLES",
    ]
    PRIV_LIST_R_ROLE_ON_SCHEMA = [
        "USAGE ON SCHEMA",
        "SELECT ON TABLES",
        "SELECT ON VIEWS",
        "USAGE ON STAGES",
        "USAGE ON FILE FORMATS",
    ]
    ENV_LIST = ["dev", "stg", "prod"]

    logger.info(f"Reading CSV from: {csv_dir}")
    logger.info(f"Reading HCL2 from: {hcl2_dir}")

    access_role_rows = list(read_csv(str(csv_dir), "access_role.csv"))
    functional_role_rows = list(read_csv(str(csv_dir), "functional_role.csv"))
    database_role_inheritance_rows = list(
        read_csv(str(csv_dir), "database_role_inheritance.csv")
    )
    functional_role_inheritance_rows = list(
        read_csv(str(csv_dir), "functional_role_inheritance.csv")
    )
    functional_access_role_inheritance_rows = list(
        read_csv(str(csv_dir), "functional_access_role_inheritance.csv")
    )
    access_role_inheritance_rows = list(
        read_csv(str(csv_dir), "access_role_inheritance.csv")
    )
    database_role_params = interpret_database_role(
        interpret_hcl2(str(hcl2_dir), "common_snowflake/database_role.tf")
    )
    database_params = interpret_database(
        interpret_hcl2(str(hcl2_dir), "common_snowflake/database.tf")
    )
    schema_params = interpret_schema(
        interpret_hcl2(str(hcl2_dir), "common_snowflake/schema.tf")
    )

    database_read_role_params_for_apoc = [
        {
            "name": dict["role_name"],
            "module_id": dict["module_id"],
            "env": dict["env"],
            "database_id": dict["database_id"],
            "schema_ids": dict["schema_ids"],
            "type": dict["type"],
        }
        for dict in database_role_params
        if dict["type"] == "R_ROLE"
    ]
    database_read_write_role_params_for_apoc = [
        {
            "name": dict["role_name"],
            "module_id": dict["module_id"],
            "env": dict["env"],
            "database_id": dict["database_id"],
            "schema_ids": dict["schema_ids"],
            "type": dict["type"],
        }
        for dict in database_role_params
        if dict["type"] == "RW_ROLE"
    ]
    database_params_for_apoc = [
        {
            "name": dict["database_name"],
            "module_id": dict["module_id"],
            "env": dict["env"],
        }
        for dict in database_params
    ]
    schema_params_for_apoc = [
        {
            "name": dict["schema_name"],
            "module_id": dict["module_id"],
            "env": dict["env"],
            "database_id": dict["database_id"],
        }
        for dict in schema_params
    ]
    access_role_params_for_apoc = [{"name": row["name"]} for row in access_role_rows]
    functional_role_params_for_apoc = [
        {"name": row["name"]} for row in functional_role_rows
    ]
    database_role_inheritance_params_for_apoc = [
        {"child": row["child"], "parent": row["parent"]}
        for row in database_role_inheritance_rows
    ]
    functional_role_inheritance_params_for_apoc = [
        {"child": row["child"], "parent": row["parent"]}
        for row in functional_role_inheritance_rows
    ]
    functional_access_role_inheritance_params_for_apoc = [
        {"child": row["child"], "parent": row["parent"]}
        for row in functional_access_role_inheritance_rows
    ]
    access_role_inheritance_params_for_apoc = [
        {"child": row["child"], "parent": row["parent"]}
        for row in access_role_inheritance_rows
    ]

    init_query = templates.env.get_template("init.cipher").render()
    logger.debug(f"Rendered query: {init_query[:200]}...")

    logger.info(f"Connecting to Neo4j at {settings.NEO4J_URI}")

    with GraphDatabase.driver(
        settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    ) as driver:
        with driver.session(database=settings.DATABASE) as session:
            logger.info("Executing Neo4j query...")
            result = session.run(
                init_query,
                {
                    "database_read_role_node_params": database_read_role_params_for_apoc,
                    "database_read_write_role_node_params": database_read_write_role_params_for_apoc,
                    "functional_role_node_params": functional_role_params_for_apoc,
                    "access_role_node_params": access_role_params_for_apoc,
                    "database_role_inheritance_node_params": database_role_inheritance_params_for_apoc,
                    "functional_role_inheritance_node_params": functional_role_inheritance_params_for_apoc,
                    "functional_access_role_inheritance_node_params": functional_access_role_inheritance_params_for_apoc,
                    "access_role_inheritance_node_params": access_role_inheritance_params_for_apoc,
                    "database_node_params": database_params_for_apoc,
                    "schema_node_params": schema_params_for_apoc,
                    "priv_list_rw_role_on_database": PRIV_LIST_RW_ROLE_ON_DATABASE,
                    "priv_list_r_role_on_database": PRIV_LIST_R_ROLE_ON_DATABASE,
                    "priv_list_rw_role_on_schema": PRIV_LIST_RW_ROLE_ON_SCHEMA,
                    "priv_list_r_role_on_schema": PRIV_LIST_R_ROLE_ON_SCHEMA,
                    "env_list": ENV_LIST,
                },
            )
            # クエリ結果を消費（Neo4jのクエリは明示的に結果を消費する必要がある）
            result_list = list(result)
            logger.info(
                f"Query executed successfully. Result count: {len(result_list)}"
            )

    logger.info("Initialization completed successfully")
