# app/embeddings_store.py
import os
import pickle
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from .config import settings
from .extractor import list_pdf_and_txt, extract_text_from_pdf
from typing import List

def build_faiss_from_transcripts(transcripts_dir: str = None):
    transcripts_dir = transcripts_dir or settings.TRANSCRIPTS_DIR
    files = list_pdf_and_txt(transcripts_dir)
    docs = []
    for f in files:
        full = f
        if f.lower().endswith(".pdf"):
            text = extract_text_from_pdf(full)
        else:
            with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        if text and len(text.strip())>0:
            docs.append(Document(page_content=text, metadata={"source": os.path.basename(full)}))
    embed = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    vect = FAISS.from_documents(docs, embed) if docs else None
    # persist
    os.makedirs(os.path.dirname(settings.FAISS_STORE_PATH), exist_ok=True)
    with open(settings.FAISS_STORE_PATH, "wb") as fh:
        pickle.dump(vect, fh)
    return vect

def load_faiss():
    if os.path.exists(settings.FAISS_STORE_PATH):
        try:
            with open(settings.FAISS_STORE_PATH, "rb") as fh:
                return pickle.load(fh)
        except Exception as e:
            print("Failed to load FAISS store:", e)
            return None
    return None
