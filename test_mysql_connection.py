# test_mysql_connection.py
from sqlalchemy import create_engine, text
import os

# You can hardcode or rely on .env
url = os.getenv("MYSQL_URL", "mysql+pymysql://root:Tarun%409957@127.0.0.1:3306/tcs_agent")
engine = create_engine(url, echo=False, future=True)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW()"))
        print("✅ Connected successfully! MySQL server time:", result.scalar())
except Exception as e:
    print("❌ Connection failed:", type(e).__name__, e)
