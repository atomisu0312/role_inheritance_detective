"""設定クラス"""
import os
import logging

class Settings:
    """アプリケーション設定"""
    
    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jpassword")
    DATABASE = "neo4j"
    STATIC_CSV_DIR = os.getenv("STATIC_CSV_DIR", "../target_dir/params")
    STATIC_HCL_DIR = os.getenv("STATIC_HCL_DIR", "../target_dir/terraform")
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
