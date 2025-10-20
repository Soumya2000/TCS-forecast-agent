# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .tools import FinancialDataExtractorTool, QualitativeAnalysisTool, MarketDataTool
from .db import SessionLocal, init_db, RequestLog
from .config import settings
import json, traceback
from sqlalchemy.exc import SQLAlchemyError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence  # ✅ replacement for LLMChain

app = FastAPI(title="TCS Financial Forecasting Agent - Gemini (LangChain 1.x)")

# Ensure DB tables exist
init_db()


class ForecastRequest(BaseModel):
    quarters: Optional[int] = 3
    include_market_data: Optional[bool] = False
    task_note: Optional[str] = "Generate qualitative forecast for the upcoming quarter"
    market_price_override: Optional[float] = None


@app.get("/")
def home():
    return {
        "message": "✅ TCS Financial Forecasting API is running.",
        "usage": "Send a POST request to /forecast with JSON input to generate forecasts."
    }


@app.post("/forecast")
def generate_forecast(req: ForecastRequest):
    session = SessionLocal()
    payload = req.dict()
    log = RequestLog(endpoint="/forecast", request_payload=json.dumps(payload), response_payload="")
    try:
        session.add(log)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Warning: DB initial log failed:", e)

    try:
        # 1) Extract metrics
        fin_tool = FinancialDataExtractorTool()
        metrics = fin_tool.run(quarters=req.quarters)

        # 2) Qualitative RAG analysis
        qual_tool = QualitativeAnalysisTool()
        analysis = qual_tool.analyze("guidance OR outlook OR demand OR margin OR headcount OR deal OR opportunity")

        # 3) Forecast synthesis (Gemini)
        llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, temperature=settings.TEMPERATURE)

        synthesizer_prompt = PromptTemplate(
            input_variables=["metrics_json", "analysis_json", "task_note"],
            template="""
You are a senior financial analyst for an IT services company. Use the inputs below to produce a JSON object with keys:
- forecast_summary: short paragraph (2–4 sentences) describing the expected direction for revenue and margins next quarter.
- numeric_estimates: dict with keys revenue_change_qoq_pct, operating_margin_expected, net_profit_change_qoq_pct
- trends: list of bullet strings
- management_sentiment: "positive", "neutral", or "negative"
- risks: list of short strings
- opportunities: list of short strings
- confidence_score: float between 0 and 1
- supporting_evidence: list of short strings referencing evidence and source filenames

Inputs:
Metrics JSON:
{metrics_json}

Transcript Analysis JSON:
{analysis_json}

Task note:
{task_note}

Return only valid JSON.
"""
        )

        # ✅ Modern chain syntax
        chain = RunnableSequence(synthesizer_prompt | llm)

        llm_input = {
            "metrics_json": json.dumps(metrics, indent=2, default=str),
            "analysis_json": json.dumps(analysis.get("analysis", {}), indent=2, default=str),
            "task_note": req.task_note
        }

        response = chain.invoke(llm_input)
        try:
            forecast_json = json.loads(response.content)
        except Exception:
            forecast_json = {"raw_output": response.content, "metrics": metrics, "analysis": analysis}

        # 4) Optional market data
        market = None
        if req.include_market_data:
            market_tool = MarketDataTool()
            if req.market_price_override:
                market = {"ticker": "TCS.NS", "price": req.market_price_override, "source": "override"}
            else:
                market = market_tool.get_current_price()

        final = {
            "request": payload,
            "metrics": metrics,
            "transcript_analysis": analysis,
            "forecast": forecast_json,
            "market": market
        }

        try:
            log.response_payload = json.dumps(final, default=str)
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            print("Warning: DB log update failed:", e)

        return final

    except Exception as e:
        tb = traceback.format_exc()
        try:
            log.response_payload = json.dumps({"error": str(e), "trace": tb})
            session.add(log)
            session.commit()
        except:
            session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
