from __future__ import annotations

from typing import Any, Dict, List
import math

import pandas as pd

from models import LLMPlan, Transform


def apply_transforms(df: pd.DataFrame, transforms: List[Transform]) -> pd.DataFrame:
    """Apply a sequence of generic transforms to the dataframe.

    All operations are dataset-agnostic: they depend only on the column names
    referenced in the transform objects.
    """
    out = df.copy()
    for t in transforms or []:
        if t.op == "groupby":
            group_cols = t.by or []
            agg_dict = {}
            for agg in t.aggregations or []:
                agg_dict[agg.new_column] = (agg.column, agg.agg)
            if group_cols and agg_dict:
                out = out.groupby(group_cols).agg(**agg_dict).reset_index()

        elif t.op == "sort" and t.by:
            out = out.sort_values(by=t.by, ascending=(t.order != "desc"))

        elif t.op == "select" and t.columns:
            cols = [c for c in t.columns if c in out.columns]
            if cols:
                out = out[cols]

        elif t.op == "filter" and t.filter_expr:
            try:
                out = out.query(t.filter_expr)
            except Exception:
                # If the filter expression is invalid, ignore it.
                pass

        elif t.op == "value_counts" and t.column:
            col = t.column
            if col in out.columns:
                s = out[col].dropna().astype(str)
                if t.delimiter:
                    s = s.str.split(t.delimiter).explode().str.strip()
                counts = s.value_counts().reset_index()
                counts.columns = [col, "count"]
                out = counts
                if t.top_n is not None:
                    out = out.head(t.top_n)

    return out


def _make_json_safe(obj):
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_safe(v) for v in obj]
    return obj


def execute_plan(df: pd.DataFrame, plan: LLMPlan) -> Dict[str, Any]:
    """Execute an LLM-generated plan against a dataframe.

    Returns a JSON-serializable payload for the frontend.
    """
    chart = plan.chart
    transformed = apply_transforms(df, chart.transforms or [])

    enc = chart.encoding

    # Basic validation by viz type
    errors: List[str] = []

    if chart.viz_type == "pie":
        if not enc.label or enc.label not in transformed.columns:
            errors.append("pie chart requires a valid 'label' column")
        if not enc.value or enc.value not in transformed.columns:
            # If value is missing, default to counts of rows per label
            label_col = enc.label
            if label_col and label_col in transformed.columns:
                vc = (
                    transformed[label_col]
                    .value_counts()
                    .reset_index()
                    .rename(columns={"index": label_col, label_col: "count"})
                )
                transformed = vc
                enc.value = "count"
            else:
                errors.append("pie chart could not infer a numeric 'value' column")

    if chart.viz_type == "scatter":
        for axis in ("x", "y"):
            col = getattr(enc, axis)
            if not col or col not in transformed.columns:
                errors.append(f"scatter plot requires numeric '{axis}' column")
            elif not pd.api.types.is_numeric_dtype(transformed[col]):
                errors.append(f"scatter '{axis}' column '{col}' must be numeric")

    if errors:
        return {
            "action": plan.action,
            "target_viz_id": plan.target_viz_id,
            "viz_type": chart.viz_type,
            "encoding": chart.encoding.model_dump(),
            "style": chart.style.model_dump(),
            "transforms": [t.model_dump() for t in chart.transforms],
            "data": [],
            "errors": errors,
        }

    records = transformed.to_dict(orient="records")

    payload: Dict[str, Any] = {
        "action": plan.action,
        "target_viz_id": plan.target_viz_id,
        "viz_type": chart.viz_type,
        "encoding": chart.encoding.model_dump(),
        "style": chart.style.model_dump(),
        "transforms": [t.model_dump() for t in chart.transforms],
        "data": records,
    }

    # Optional correlation insight for scatter plots
    if chart.viz_type == "scatter" and enc.x and enc.y:
        x, y = enc.x, enc.y
        try:
            corr = transformed[x].corr(transformed[y])
            if corr is not None and math.isfinite(float(corr)):
                payload.setdefault("insights", {})["pearson_correlation"] = float(corr)
        except Exception:
            pass

    return _make_json_safe(payload)
