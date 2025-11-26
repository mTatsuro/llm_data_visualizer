from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict


class Aggregation(BaseModel):
    column: str
    agg: Literal["count", "sum", "mean", "min", "max"]
    new_column: str

    model_config = ConfigDict(extra="ignore")


class Transform(BaseModel):
    op: Literal["groupby", "sort", "select", "filter", "value_counts"]
    by: Optional[List[str]] = None
    order: Optional[Literal["asc", "desc"]] = None
    columns: Optional[List[str]] = None
    filter_expr: Optional[str] = None
    aggregations: Optional[List[Aggregation]] = None

    # For value_counts
    column: Optional[str] = None
    delimiter: Optional[str] = None
    top_n: Optional[int] = None

    model_config = ConfigDict(extra="ignore")


class Encoding(BaseModel):
    x: Optional[str] = None
    y: Optional[str] = None
    label: Optional[str] = None
    value: Optional[str] = None
    color: Optional[str] = None
    tooltip: Optional[List[str]] = None

    model_config = ConfigDict(extra="ignore")


class Style(BaseModel):
    title: Optional[str] = None
    color: Optional[str] = None
    header_bold: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")


class ChartSpec(BaseModel):
    viz_type: Literal["pie", "bar", "scatter", "table"]
    transforms: List[Transform] = []
    encoding: Encoding = Encoding()
    style: Style = Style()

    model_config = ConfigDict(extra="ignore")


class LLMPlan(BaseModel):
    action: Literal["new_visualization", "update_visualization"] = "new_visualization"
    target_viz_id: Optional[str] = None
    chart: ChartSpec

    model_config = ConfigDict(extra="ignore")
