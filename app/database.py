import oracledb
import os
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

ORACLE_USER = os.getenv("DB_USER")
ORACLE_PASSWORD = os.getenv("DB_PASSWORD")
ORACLE_DSN = os.getenv("DB_DSN")

POOL_MIN = int(os.getenv("POOL_MIN", 5))
POOL_MAX = int(os.getenv("POOL_MAX", 20))
POOL_INC = int(os.getenv("POOL_INC", 5))

_pool = None
def create_pool():
    global _pool
    try:
        _pool = oracledb.create_pool(
            user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN,
            min=POOL_MIN, max=POOL_MAX, increment=POOL_INC, getmode=oracledb.POOL_GETMODE_WAIT
        )
        print(f"Connection pool created: {POOL_MIN}-{POOL_MAX} connections")
        return _pool
    except oracledb.Error as e:
        error, = e.args
        print(f"Failed to create pool: {error.message}")
        raise
def get_pool():
    global _pool
    if _pool is None:
        _pool = create_pool()
    return _pool
def get_db() -> Generator:
    pool = get_pool()
    connection = pool.acquire()
    try:
        yield connection
    finally:
        connection.close() # Return connection to pool
def close_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        print("Connection pool closed")
        _pool = None