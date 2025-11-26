import json
from typing import Optional, Dict, Any, List
from openai import OpenAI
from models import LLMPlan

client = OpenAI()  # expects OPENAI_API_KEY in environment

SYSTEM_PROMPT = """
You are a data visualization planner for a SaaS companies dataset.

Columns:
- Company Name (string)
- Founded Year (integer)
- HQ (string)
- Industry (string)
- Total Funding (string, parsed numeric column: Total_Funding_num)
- ARR (string, parsed numeric column: ARR_num)
- Valuation (string, parsed numeric column: Valuation_num)
- Employees (string, parsed numeric column: Employees_num)
- Top Investors (string with comma-separated investors)
- Product (string)
- G2 Rating (float)

Your job:
1. Read the user's natural language request.
2. Decide the best visualization type (pie, bar, scatter, table).
3. Describe the necessary data transforms (groupby, aggregations, etc.).
4. Define encodings: which columns go to x, y, label, value, tooltip.
5. Optionally adjust style (color, header_bold, title).
6. If the user is only asking to change visual style of an existing chart,
   set action="update_visualization" and keep the same transforms/encodings.
7. To build a frequency table of investors, you can use the op "investor_frequency"
   which explodes "Top Investors" into individual investors and returns columns:
   "Investor" and "Company_Count".

IMPORTANT:
- Always respond with a SINGLE valid JSON object.
- Do NOT include any backticks or markdown code fences.
- The JSON must have exactly these top-level keys: action, target_viz_id, chart.
- For action, use "new_visualization" or "update_visualization".
- For chart.viz_type, use one of: "pie", "bar", "scatter", "table".
"""


def _extract_field(v: Any) -> Any:
    """
    Extract column/field name from a Vega-Lite-style encoding object, or return as-is.
    """
    if isinstance(v, dict):
        return v.get("field") or v.get("column") or v.get("name")
    return v


def _normalize_llm_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize whatever JSON the model produced into the schema expected by LLMPlan.
    This makes the system robust to small schema drift, Vega-Lite-ish encodings, etc.
    """

    # ---- action ----
    action = data.get("action") or "new_visualization"
    if action not in ("new_visualization", "update_visualization"):
        # Map common synonyms
        lower = str(action).lower()
        if "update" in lower or "modify" in lower or "tweak" in lower:
            action = "update_visualization"
        else:
            action = "new_visualization"
    data["action"] = action

    # ---- chart ----
    chart = data.get("chart") or {}
    data["chart"] = chart

    # viz_type
    viz_type = chart.get("viz_type") or chart.get("type") or chart.get("mark")
    if isinstance(viz_type, dict):
        viz_type = viz_type.get("type") or viz_type.get("name")

    if isinstance(viz_type, str):
        lt = viz_type.lower()
        if lt in ("arc", "pie", "donut"):
            viz_type = "pie"
        elif lt in ("point", "circle", "square", "scatter"):
            viz_type = "scatter"
        elif lt in ("bar", "column"):
            viz_type = "bar"
        elif lt in ("table", "tabular", "grid"):
            viz_type = "table"
        else:
            # Fallback
            viz_type = lt
    else:
        viz_type = "table"

    chart["viz_type"] = viz_type

    # ---- transforms ----
    raw_transforms: List[Any] = (
        chart.get("transforms")
        or chart.get("dataTransforms")
        or chart.get("transform")
        or []
    )

    norm_transforms = []
    for t in raw_transforms:
        if not isinstance(t, dict):
            continue

        op = t.get("op") or t.get("operation") or t.get("type")

        # Map common variants
        if not op:
            desc = (t.get("name", "") + " " + t.get("description", "")).lower()
            if "investor" in desc:
                op = "investor_frequency"

        if isinstance(op, str):
            lo = op.lower()
            if lo in ("aggregate", "group_by", "groupby", "group"):
                op = "groupby"
            elif lo in ("sort", "order", "orderby"):
                op = "sort"
            elif lo in ("select", "project"):
                op = "select"
            elif lo in ("filter", "where"):
                op = "filter"
            elif lo in ("investor_frequency",):
                op = "investor_frequency"
        else:
            # Skip unknown transform types
            continue

        norm: Dict[str, Any] = {
            "op": op,
        }

        # Groupby / sort / select / filter metadata
        norm["by"] = (
            t.get("by")
            or t.get("groupby")
            or t.get("group_by")
            or t.get("group")
        )
        norm["order"] = t.get("order") or t.get("sort_order")
        norm["columns"] = t.get("columns") or t.get("fields") or t.get("select")
        norm["filter_expr"] = (
            t.get("filter_expr") or t.get("expr") or t.get("condition")
        )

        # Aggregations: try to map from Vega-Lite style
        raw_aggs = (
            t.get("aggregations")
            or t.get("aggregates")
            or t.get("aggregate")
            or t.get("fields")
            or []
        )

        norm_aggs = []
        if isinstance(raw_aggs, list):
            for a in raw_aggs:
                if not isinstance(a, dict):
                    continue
                agg_func = (
                    a.get("agg")
                    or a.get("op")
                    or a.get("operation")
                    or a.get("func")
                )
                new_col = (
                    a.get("new_column")
                    or a.get("as")
                    or a.get("alias")
                    or a.get("name")
                )
                col = a.get("column") or a.get("field")
                if agg_func and col and new_col:
                    norm_aggs.append(
                        {
                            "column": col,
                            "agg": agg_func,
                            "new_column": new_col,
                        }
                    )
        if norm_aggs:
            norm["aggregations"] = norm_aggs

        norm_transforms.append(norm)

    chart["transforms"] = norm_transforms

    # ---- encoding ----
    enc = chart.get("encoding") or {}

    # Handle Vega-Lite style encodings: x: {field: "ARR_num", type: "quantitative"}
    for key in ("x", "y", "label", "value"):
        if key in enc:
            enc[key] = _extract_field(enc[key])

    # Special handling for pie charts where the model may use
    # theta/color instead of label/value.
    if chart["viz_type"] == "pie":
        # Label: what each slice represents (category)
        if not enc.get("label"):
            if "color" in enc:
                enc["label"] = _extract_field(enc["color"])
            elif "category" in enc:
                enc["label"] = _extract_field(enc["category"])
            else:
                # Fallback: try groupby columns from transforms
                for t in chart.get("transforms", []):
                    if t.get("op") == "groupby" and t.get("by"):
                        enc["label"] = t["by"][0]
                        break

        # Value: size of each slice
        if not enc.get("value"):
            if "theta" in enc:
                enc["value"] = _extract_field(enc["theta"])
            elif "size" in enc:
                enc["value"] = _extract_field(enc["size"])
            else:
                # Fallback: use the first aggregation's new_column
                for t in chart.get("transforms", []):
                    for agg in t.get("aggregations", []):
                        enc["value"] = agg.get("new_column") or agg.get("column")
                        break
                    if enc.get("value"):
                        break

    # Tooltip: list of fields or objects-with-field
    if "tooltip" in enc and isinstance(enc["tooltip"], list):
        enc["tooltip"] = [_extract_field(t) for t in enc["tooltip"]]

    chart["encoding"] = enc

    # Tooltip: list of fields or objects-with-field
    if "tooltip" in enc and isinstance(enc["tooltip"], list):
        enc["tooltip"] = [_extract_field(t) for t in enc["tooltip"]]

    chart["encoding"] = enc

    # ---- style ----
    style = chart.get("style") or {}
    chart["style"] = style

    return data


def build_plan_from_prompt(
    user_prompt: str,
    current_viz: Optional[Dict[str, Any]] = None,
    target_viz_id: Optional[str] = None,
) -> LLMPlan:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "User prompt: "
                + user_prompt
                + "\n\n"
                + "Current visualization spec (JSON or empty object): "
                + json.dumps(current_viz or {})
                + "\nTarget viz id: "
                + (target_viz_id or "null")
            ),
        },
    ]

    # NOTE: older OpenAI Python SDKs don't support response_format here, so we
    # just ask for JSON in the prompt and parse it ourselves.
    resp = client.responses.create(
        model="gpt-5.1",
        input=messages,
    )

    # Extract text output robustly
    try:
        raw = resp.output[0].content[0].text
    except Exception:
        raw = str(resp)

    text = raw.strip()
    # Strip possible ```json ... ``` fences if the model ignored instructions
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        if lines and lines[0].strip().lower().startswith("json"):
            lines = lines[1:]
        text = "\n".join(lines).strip()

    data = json.loads(text)
    data = _normalize_llm_json(data)
    return LLMPlan.model_validate(data)
