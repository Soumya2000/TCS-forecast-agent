# app/extractor.py
import pdfplumber
import os
import re
from typing import Dict, List
from .config import settings
from tqdm import tqdm

def list_pdf_and_txt(directory: str):
    files = []
    for fname in os.listdir(directory):
        if fname.lower().endswith((".pdf", ".txt")):
            files.append(os.path.join(directory, fname))
    return sorted(files)

def extract_text_from_pdf(path: str) -> str:
    text_parts = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    text_parts.append(txt)
    except Exception as e:
        # fallback to empty string
        print(f"pdfplumber failed for {path}: {e}")
    return "\n".join(text_parts)

def load_documents(directory: str):
    files = list_pdf_and_txt(directory)
    docs = {}
    for path in files:
        if path.lower().endswith(".pdf"):
            txt = extract_text_from_pdf(path)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                txt = fh.read()
        docs[os.path.basename(path)] = txt
    return docs

# lightweight regex patterns tuned for TCS annual/quarterly style (adjustable)
METRIC_PATTERNS = {
    "total_revenue": r"(?:total\s+revenue|revenue\s+for\s+the\s+quarter|revenue\s+for\s+the\s+year|revenue\s+from\s+operations)[:\s]*₹?\s*([0-9,\.]+)",
    "net_profit": r"(?:net\s+profit|profit\s+after\s+tax|net\s+income|profit\s+for\s+the\s+year)[:\s]*₹?\s*([0-9,\.]+)",
    "operating_margin": r"(?:operating\s+margin|operating\s+profit\s+margin)[:\s]*\(?([0-9]{1,3}\.?[0-9]?)\%?\)?",
    "eps": r"(?:earnings\s+per\s+share|eps)[:\s]*₹?\s*([0-9,\.]+)"
}

def parse_number(raw: str):
    if raw is None:
        return None
    r = raw.replace(",", "").replace("(", "-").replace(")", "").strip()
    try:
        return float(r)
    except:
        r2 = re.sub(r"[^\d\.\-]", "", r)
        try:
            return float(r2)
        except:
            return None

def extract_metrics_from_text(text: str):
    text_low = text.lower()
    metrics = {}
    for key, pat in METRIC_PATTERNS.items():
        m = re.search(pat, text_low, flags=re.IGNORECASE)
        if m:
            val_raw = m.group(1)
            val = parse_number(val_raw)
            metrics[key] = val
    return metrics

def extract_metrics_for_reports(report_dir: str = None, quarters: int = 3):
    report_dir = report_dir or settings.REPORTS_DIR
    docs = load_documents(report_dir)
    # sort by mtime descending to get recent files
    files = sorted(docs.keys(), key=lambda f: os.path.getmtime(os.path.join(report_dir, f)), reverse=True)
    selected = files[:quarters]
    out = {}
    for fname in selected:
        txt = docs[fname]
        metrics = extract_metrics_from_text(txt)
        out[fname] = metrics
    return out
