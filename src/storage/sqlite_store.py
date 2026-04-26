import json
import sqlite3
from datetime import datetime
from pathlib import Path

from src.storage.results_schema import AGENT_DDL, EVAL_RESULTS_DDL, PAIRWISE_DDL


class SQLiteStore:
    def __init__(self, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(EVAL_RESULTS_DDL)
        cur.execute(PAIRWISE_DDL)
        cur.execute(AGENT_DDL)
        self.conn.commit()

    def insert_eval_result(self, row: dict) -> None:
        row = row | {"created_at": datetime.utcnow().isoformat()}
        keys = ",".join(row.keys())
        placeholders = ",".join("?" for _ in row)
        self.conn.execute(f"INSERT INTO eval_results ({keys}) VALUES ({placeholders})", list(row.values()))
        self.conn.commit()

    def insert_pairwise_result(self, row: dict) -> None:
        payload = row | {
            "raw_json": json.dumps(row.get("raw_json", {})),
            "created_at": datetime.utcnow().isoformat(),
        }
        keys = ",".join(payload.keys())
        placeholders = ",".join("?" for _ in payload)
        self.conn.execute(f"INSERT INTO pairwise_results ({keys}) VALUES ({placeholders})", list(payload.values()))
        self.conn.commit()

    def insert_agent_result(self, row: dict) -> None:
        payload = row | {"created_at": datetime.utcnow().isoformat()}
        keys = ",".join(payload.keys())
        placeholders = ",".join("?" for _ in payload)
        self.conn.execute(f"INSERT INTO agent_results ({keys}) VALUES ({placeholders})", list(payload.values()))
        self.conn.commit()

    def query_df(self, query: str):
        import pandas as pd

        return pd.read_sql_query(query, self.conn)
