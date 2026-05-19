import os
import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

_connection = None


def get_connection():
    global _connection
    if _connection is None:
        _connection = sql.connect(
            server_hostname=os.environ["DATABRICKS_HOST"].replace("https://", ""),
            http_path=os.environ["DATABRICKS_HTTP_PATH"],
            access_token=os.environ["DATABRICKS_TOKEN"],
        )
    return _connection


def execute_query(query: str) -> pd.DataFrame:
    global _connection
    last_error = None
    for attempt in range(2):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)
        except Exception as e:
            last_error = e
            try:
                if _connection is not None:
                    _connection.close()
            except Exception:
                pass
            _connection = None
    raise last_error


def test_connection() -> tuple[bool, str]:
    try:
        df = execute_query("SELECT 1 AS ok")
        return True, "Conexão OK"
    except Exception as e:
        return False, str(e)


def get_table_schema(full_table_name: str) -> pd.DataFrame:
    return execute_query(f"DESCRIBE TABLE {full_table_name}")
