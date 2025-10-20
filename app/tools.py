from typing import Dict, Any, List
from .extractor import extract_metrics_for_reports, load_documents
from .embeddings_store import load_faiss, build_faiss_from_transcripts
from .config import settings

# ✅ Modern imports for LangChain 1.x
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

import os, json


class FinancialDataExtractorTool:
    def __init__(self, report_dir: str = None):
        self.report_dir = report_dir or settings.REPORTS_DIR

    def run(self, quarters: int = 3) -> Dict[str, Dict]:
        return extract_metrics_for_reports(report_dir=self.report_dir, quarters=quarters)


class QualitativeAnalysisTool:
    def __init__(self, transcripts_dir: str = None):
        self.transcripts_dir = transcripts_dir or settings.TRANSCRIPTS_DIR
        self.vect = load_faiss()
        if self.vect is None:
            self.vect = build_faiss_from_transcripts(self.transcripts_dir)
        # Initialize Gemini via LangChain wrapper
        self.llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, temperature=settings.TEMPERATURE)

    def semantic_search(self, query: str, k: int = None):
        k = k or settings.MAX_SEARCH_RESULTS
        if not self.vect:
            return []
        hits = self.vect.similarity_search_with_score(query, k=k)
        out = []
        for doc, score in hits:
            snippet = doc.page_content
            if len(snippet) > 2000:
                snippet = snippet[:2000]
            out.append({"snippet": snippet, "metadata": doc.metadata, "score": float(score)})
        return out

    def analyze(self, query: str) -> Dict[str, Any]:
        hits = self.semantic_search(query)
        snippets = "\n\n----\n\n".join(
            [f"[source: {h['metadata'].get('source','unknown')}]\n{h['snippet']}" for h in hits]
        )

        # ✅ Updated for LangChain 1.x
        prompt = PromptTemplate(
            input_variables=["snippets", "query"],
            template="""
You are a helpful financial analyst. Given the transcript snippets below, produce a JSON object with keys:
- themes: list of 3-6 short bullets
- management_sentiment: "positive", "neutral", or "negative" with justification
- forward_statements: short quotes or paraphrases
- risks: short list of risks
- opportunities: short list of opportunities
- evidence: list of "<text snippet> — <source>"

Snippets:
{snippets}

Query: {query}

Return only valid JSON.
"""
        )

        # Create the chain (Prompt → Gemini)
        chain = RunnableSequence(prompt | self.llm)

        try:
            response = chain.invoke({"snippets": snippets, "query": query})
            parsed = json.loads(response.content)
        except Exception:
            parsed = {"raw_analysis": response.content if response else "Error parsing response"}

        return {"search_hits": hits, "analysis": parsed}


class MarketDataTool:
    def get_current_price(self, ticker: str = "TCS.NS"):
        return {"ticker": ticker, "price": None, "note": "not implemented - plug market API"}
