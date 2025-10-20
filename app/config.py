# app/config.py
import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    # Gemini / Google
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyANSyL8j-5bks664XVIlTd1FlE-OAUgv8o")  # or path to service account json if using that approach
    # LangChain ChatGoogleGenerativeAI uses the environment variable GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS.
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # adjust to your access e.g., "gemini-pro"
    # Data paths (use /mnt/data by default since you uploaded files there)
    DATA_DIR = os.getenv("DATA_DIR", "C:\\Users\\suman\\OneDrive\\Desktop\\Desktop\\DATASCIENCE & AI\\New folder\\data")
    REPORTS_DIR = os.path.join(DATA_DIR)
    TRANSCRIPTS_DIR = os.path.join(DATA_DIR)
    # MySQL URL placeholder
    MYSQL_URL = os.getenv("MYSQL_URL", "mysql+pymysql://root:Tarun%409957@127.0.0.1:3306/tcs_agent")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    FAISS_STORE_PATH = os.getenv("FAISS_STORE_PATH", "data/faiss_store.pkl")
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "6"))
    # LLM parameters
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

settings = Settings()
