import os
from services.pdf_service import create_pdf
from pathlib import Path
import json
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.llm_service import generate_procurement_report
from services.supplier_service import get_all_suppliers
from agents.ranking import rank_suppliers
from Agent1.main import run_agent1
from Agent2.main import run_agent2
from pathlib import Path
import json


app = FastAPI(
    title="Agent 3 Procurement Recommender",
    version="1.0"
)


frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImpactReport(BaseModel):
    risk_score: float
    reserve_days: float
    price_increase: float
    required_volume: int
    affected_route: str
    affected_refineries: list[str]


@app.get("/")
def home():
    return {
        "message": "Agent 3 Running Successfully"
    }


@app.post("/api/generate")
def generate(report: ImpactReport):

    suppliers = get_all_suppliers()

    impact = report.model_dump()

    ranked = rank_suppliers(
        suppliers,
        impact
    )

    ai_report = generate_procurement_report(
    impact,
    ranked[:3]
)

    pdf_file = create_pdf(ai_report)

    return {
    "risk_score": report.risk_score,
    "top_suppliers": ranked[:3],
    "ai_report": ai_report,
    "pdf_file": pdf_file
}

# =========================================================
# GENERATE FROM AGENT 2
# =========================================================

@app.post("/api/generate-from-agent2")
def generate_from_agent2():

    # Path to Agent 2 output
    base_dir = Path(__file__).resolve().parent

    agent2_output = (
        base_dir
        / "Agent2"
        / "scenario_model_output.json"
    )

    # Check that Agent 2 has produced its output
    if not agent2_output.exists():
        return {
            "error": "Agent 2 output not found",
            "path": str(agent2_output)
        }

    # Read Agent 2 output
    import json

    with open(
        agent2_output,
        "r",
        encoding="utf-8"
    ) as file:

        agent2_data = json.load(file)

    # Extract scenario
    scenario = agent2_data["scenario"]

    # Convert Agent 2 output into Agent 3 ImpactReport
    report = ImpactReport(
        risk_score=scenario["risk_score"],
        reserve_days=scenario["reserve_days"],
        price_increase=scenario["price_increase_percent"],
        required_volume=scenario["required_volume"],
        affected_route=scenario["affected_route"],
        affected_refineries=scenario["affected_refineries"]
    )

    # Get suppliers
    suppliers = get_all_suppliers()

    # Convert report into dictionary
    impact = report.model_dump()

    # Rank suppliers
    ranked = rank_suppliers(
        suppliers,
        impact
    )

    # Generate AI procurement recommendation
    ai_report = generate_procurement_report(
        impact,
        ranked[:3]
    )

    # Generate PDF
    pdf_file = create_pdf(ai_report)

    return {
        "source": "Agent 2",
        "risk_score": report.risk_score,
        "reserve_days": report.reserve_days,
        "price_increase": report.price_increase,
        "required_volume": report.required_volume,
        "affected_route": report.affected_route,
        "affected_refineries": report.affected_refineries,
        "top_suppliers": ranked[:3],
        "ai_report": ai_report,
        "pdf_file": pdf_file
    }

@app.post("/api/run-pipeline")
def run_pipeline():

    # -----------------------------
    # AGENT 1
    # -----------------------------
    agent1_data = run_agent1()

    # -----------------------------
    # AGENT 2
    # -----------------------------
    agent2_output = run_agent2()

    scenario = agent2_output["scenario"]

    # -----------------------------
    # CREATE IMPACT REPORT
    # -----------------------------
    report = ImpactReport(
        risk_score=scenario["risk_score"],
        reserve_days=scenario["reserve_days"],
        price_increase=scenario["price_increase_percent"],
        required_volume=scenario["required_volume"],
        affected_route=scenario["affected_route"],
        affected_refineries=scenario["affected_refineries"]
    )

    # -----------------------------
    # AGENT 3 - SUPPLIER RANKING
    # -----------------------------
    suppliers = get_all_suppliers()

    impact = report.model_dump()

    ranked = rank_suppliers(
        suppliers,
        impact
    )

    # -----------------------------
    # GEMINI AI REPORT
    # -----------------------------
    ai_report = generate_procurement_report(
        impact,
        ranked[:3]
    )

    # -----------------------------
    # GENERATE PDF
    # -----------------------------
    pdf_file = create_pdf(
        ai_report
    )

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------
    return {
        "status": "success",
        "agent1": agent1_data,
        "agent2": agent2_output,
        "impact_report": impact,
        "top_suppliers": ranked[:3],
        "ai_report": ai_report,
        "pdf_file": pdf_file
    }

@app.get("/test")
def test():

    suppliers = get_all_suppliers()

    impact = {
        "affected_route": "Hormuz Strait",
        "required_volume": 1500000
    }

    ranked = rank_suppliers(
        suppliers,
        impact
    )

    return ranked[:3]

@app.get("/download/{filename}")
def download_pdf(filename: str):

    reports_dir = Path(__file__).resolve().parent / "reports"
    if Path(filename).name != filename:
        raise HTTPException(status_code=404, detail="Report not found.")

    path = reports_dir / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report not found.")

    return FileResponse(
        path=path,
        filename=filename,
        media_type="application/pdf"
    )