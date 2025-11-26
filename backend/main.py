from __future__ import annotations

import uuid
from typing import Any, Dict, Optional, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_utils import load_dataset, build_schema
from executor import execute_plan
from llm_planner import build_plan_from_prompt

app = FastAPI(title="Natural-language Viz Backend", version="2.0")

# Allow local dev from any origin by default; tighten if needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data & schema at startup (for this example, single CSV).
df = load_dataset()
schema = build_schema(df)


class VizRequest(BaseModel):
    prompt: str
    current_viz: Optional[Dict[str, Any]] = None
    target_viz_id: Optional[str] = None


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/visualize")
def visualize(req: VizRequest) -> Dict[str, Any]:
    """Main entry point: turn a NL prompt into a visualization spec + data.

    This endpoint is intentionally generic:
    - It knows nothing about the specific columns in the CSV.
    - All semantics (which columns to use, which transforms to apply)
      come from the LLM, which sees a JSON schema of the dataframe.
    """
    plan = build_plan_from_prompt(
        user_prompt=req.prompt,
        schema=schema,
        current_viz=req.current_viz,
        target_viz_id=req.target_viz_id,
    )

    result = execute_plan(df, plan)

    # Assign a viz_id for frontend to track multiple visualizations
    if result.get("action") == "new_visualization":
        result["viz_id"] = str(uuid.uuid4())
    else:
        result["viz_id"] = req.target_viz_id

    return result
