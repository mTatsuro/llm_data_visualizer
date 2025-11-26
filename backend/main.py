import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

from data_utils import load_saas_df
from llm_planner import build_plan_from_prompt
from executor import execute_plan
from models import Transform  # NEW


app = FastAPI()
df = load_saas_df()

print("Loaded SaaS dataframe:")
print(df[["Company Name", "Founded Year", "Valuation", "Valuation_num"]].head())
print(df["Valuation_num"].describe())


class VizRequest(BaseModel):
    prompt: str
    target_viz_id: Optional[str] = None
    current_viz: Optional[Dict[str, Any]] = None  # spec of viz to tweak


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/visualize")
def visualize(req: VizRequest):
    plan = build_plan_from_prompt(
        user_prompt=req.prompt,
        current_viz=req.current_viz,
        target_viz_id=req.target_viz_id,
    )

    lower_prompt = req.prompt.lower()

    # Investor frequency heuristic
    if "investor" in lower_prompt and (
        "frequen" in lower_prompt
        or "most common" in lower_prompt
        or "most often" in lower_prompt
        or "appear most" in lower_prompt
    ):
        plan.chart.viz_type = "table"
        plan.chart.transforms = [
            Transform(op="investor_frequency"),
            Transform(op="sort", by=["Company_Count"], order="desc"),
        ]
        if not plan.chart.style.title:
            plan.chart.style.title = "Top investors by number of companies"

    # ARR–Valuation correlation heuristic
    if "correlation" in lower_prompt and "arr" in lower_prompt and "valuation" in lower_prompt:
        plan.chart.viz_type = "scatter"
        plan.chart.encoding.x = "ARR_num"
        plan.chart.encoding.y = "Valuation_num"
        if not plan.chart.style.title:
            plan.chart.style.title = "Correlation between ARR and Valuation"

    result = execute_plan(df, plan)

    if result["action"] == "new_visualization":
        result["viz_id"] = str(uuid.uuid4())
    else:
        result["viz_id"] = req.target_viz_id

    return result


