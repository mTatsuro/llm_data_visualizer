from typing import Dict, Any, List
import math

import pandas as pd
from models import LLMPlan, Transform


def apply_transforms(df: pd.DataFrame, transforms: List[Transform]) -> pd.DataFrame:
    """
    Apply the high-level transforms coming from the LLM onto the raw dataframe.
    """
    result = df.copy()
    for t in transforms:
        if t.op == "groupby":
            group_cols = t.by or []
            agg_dict = {}
            for agg in t.aggregations or []:
                agg_dict[agg.new_column] = (agg.column, agg.agg)
            if group_cols and agg_dict:
                result = result.groupby(group_cols).agg(**agg_dict).reset_index()

        elif t.op == "sort":
            if t.by:
                result = result.sort_values(
                    by=t.by,
                    ascending=(t.order != "desc"),
                )

        elif t.op == "select":
            if t.columns:
                cols = [c for c in t.columns if c in result.columns]
                result = result[cols]

        elif t.op == "filter" and t.filter_expr:
            try:
                result = result.query(t.filter_expr)
            except Exception:
                # If the filter expression is invalid, just ignore it
                pass

        elif t.op == "investor_frequency":
            if "Top Investors" in result.columns:
                investors = (
                    result["Top Investors"]
                    .dropna()
                    .astype(str)
                    .str.split(",", expand=False)
                    .explode()
                    .str.strip()
                )
                freq = investors.value_counts().reset_index()
                freq.columns = ["Investor", "Company_Count"]
                result = freq

    return result


def _make_json_safe(obj):
    """
    Recursively walk a Python object and replace non-finite floats
    (NaN, +inf, -inf) with None so JSON serialization doesn't break.
    """
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_safe(v) for v in obj]
    return obj


def _prepare_pie_data(df: pd.DataFrame, chart) -> pd.DataFrame:
    """
    Ensure encoding.label and encoding.value are set and use them to build a
    sane pie-chart-friendly dataframe (aggregated and top-N limited).

    Rules:
    - If the model explicitly set encoding.value to a valid numeric column,
      we respect that and aggregate by sum.
    - Otherwise, we default to simple row counts per label (frequency).
    - For this SaaS dataset, if no label is specified we prefer "Industry"
      as the label column.
    """
    enc = chart.encoding

    # ---- choose label column ----
    label_col = enc.label

    # If the model's label is missing or invalid, choose one.
    if not label_col or label_col not in df.columns:
        # Prefer dataset-specific "good" category columns, especially Industry.
        preferred_labels = [
            "Industry",
            "industry",
            "Sector",
            "Category",
            "Type",
        ]
        label_col = None
        for col in preferred_labels:
            if col in df.columns:
                label_col = col
                break

        # If we still didn't find anything, fall back to first non-numeric column,
        # otherwise just the first column.
        if not label_col:
            non_num_cols = df.select_dtypes(exclude="number").columns.tolist()
            if non_num_cols:
                label_col = non_num_cols[0]
            else:
                label_col = df.columns[0]

        enc.label = label_col  # save back into encoding

    # ---- if the model gave us a valid numeric value column, use it ----
    value_col = enc.value
    if (
        value_col
        and value_col in df.columns
        and pd.api.types.is_numeric_dtype(df[value_col])
    ):
        # Aggregate numeric values by label
        grouped = df.groupby(label_col, as_index=False)[value_col].sum()
        grouped = grouped.sort_values(value_col, ascending=False)

        # Top-N and "Other"
        N = 10
        if len(grouped) > N:
            top = grouped.iloc[:N].copy()
            other_total = grouped.iloc[N:][value_col].sum()
            if pd.notna(other_total) and other_total > 0:
                top.loc[len(top)] = {label_col: "Other", value_col: other_total}
            grouped = top

        if not chart.style.title:
            chart.style.title = f"{label_col} breakdown by {value_col} (top {min(N, len(grouped))})"

        return grouped

    # ---- otherwise: default to simple counts per label ----
    vc = df[label_col].value_counts().reset_index()
    vc.columns = [label_col, "count"]
    value_col = "count"
    enc.value = value_col  # tell the frontend which column to use

    # Top-N and "Other"
    N = 10
    vc = vc.sort_values(value_col, ascending=False)
    if len(vc) > N:
        top = vc.iloc[:N].copy()
        other_total = vc.iloc[N:][value_col].sum()
        if pd.notna(other_total) and other_total > 0:
            top.loc[len(top)] = {label_col: "Other", value_col: other_total}
        vc = top

    if not chart.style.title:
        chart.style.title = f"{label_col} breakdown (top {min(N, len(vc))})"

    return vc


def _prepare_scatter_data(df: pd.DataFrame, chart) -> pd.DataFrame:
    """
    Ensure encoding.x and encoding.y are set to valid numeric columns for scatter plots.

    For this SaaS dataset, we prefer:
        x = "Founded Year"
        y = "Valuation_num"  (parsed numeric valuation)

    If that pair isn't available, we fall back to any two numeric columns.
    We also rescale very large money values into billions for readability.
    """
    enc = chart.encoding

    def is_numeric_col(col: str) -> bool:
        return col is not None and col in df.columns and pd.api.types.is_numeric_dtype(df[col])

    # Start from what the model asked for, but only keep if numeric
    x = enc.x if is_numeric_col(enc.x) else None
    y = enc.y if is_numeric_col(enc.y) else None

    # Preferred pairs only if x/y aren't already valid numerics
    preferred_pairs = [
        ("Founded Year", "Valuation_num"),
        ("Founded Year", "ARR_num"),
        ("Founded Year", "Employees_num"),
    ]

    if not (is_numeric_col(x) and is_numeric_col(y)):
        for px, py in preferred_pairs:
            if is_numeric_col(px) and is_numeric_col(py):
                x, y = px, py
                break

    # If still missing, fall back to any two numeric columns
    if not (is_numeric_col(x) and is_numeric_col(y)):
        numeric_cols = [c for c in df.columns if is_numeric_col(c)]
        if len(numeric_cols) >= 2:
            x, y = numeric_cols[0], numeric_cols[1]
        elif len(numeric_cols) == 1:
            x = numeric_cols[0]
            for col in df.columns:
                if col != x:
                    y = col
                    break

    # Absolute last resort: use the first two columns
    if x is None or y is None:
        cols = list(df.columns)
        if cols:
            x = x or cols[0]
        if len(cols) > 1:
            y = y or cols[1]

    # Work only with the two relevant columns and drop NaNs
    work = df[[x, y]].dropna().copy()

    # Rescale large money columns into billions for readability
    money_cols = {
        "Valuation_num": "Valuation ($B)",
        "ARR_num": "ARR ($B)",
        "Total_Funding_num": "Funding ($B)",
    }
    if y in money_cols:
        new_y = money_cols[y]
        work[new_y] = work[y] / 1e9
        y = new_y

    # Save final encodings
    enc.x = x
    enc.y = y

    # Sort by x so the X axis is in order
    if x in work.columns:
        work = work.sort_values(by=x)

    # Title
    if not chart.style.title and x and y:
        if x == "Founded Year" and y.startswith("Valuation"):
            chart.style.title = "Company valuation (in $B) by founded year"
        else:
            chart.style.title = f"{y} vs {x}"

    return work


def execute_plan(df: pd.DataFrame, plan: LLMPlan) -> Dict[str, Any]:
    chart = plan.chart
    transformed = apply_transforms(df, chart.transforms or [])

    # Special handling for pie charts: always ensure a good encoding and data
    if chart.viz_type == "pie":
        transformed = _prepare_pie_data(transformed, chart)

    # Special handling for scatter plots: always ensure x and y are valid
    if chart.viz_type == "scatter":
        transformed = _prepare_scatter_data(transformed, chart)

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

    # For correlation-type requests, compute stats if both x and y are numeric
    if chart.viz_type == "scatter" and chart.encoding.x and chart.encoding.y:
        x = chart.encoding.x
        y = chart.encoding.y
        if x in transformed.columns and y in transformed.columns:
            try:
                corr = transformed[x].corr(transformed[y])
                if corr is not None and math.isfinite(float(corr)):
                    payload.setdefault("insights", {})[
                        "pearson_correlation"
                    ] = float(corr)
            except Exception:
                pass

    return _make_json_safe(payload)
