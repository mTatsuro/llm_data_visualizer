from typing import Literal, Optional, List
from pydantic import BaseModel

VizType = Literal["pie", "bar", "scatter", "table"]


class TransformAggregation(BaseModel):
    column: str
    agg: Literal["count", "sum", "mean", "median"]
    new_column: str


class Transform(BaseModel):
    op: Literal["groupby", "sort", "select", "filter", "investor_frequency"]
    by: Optional[List[str]] = None
    aggregations: Optional[List[TransformAggregation]] = None
    order: Optional[Literal["asc", "desc"]] = None
    columns: Optional[List[str]] = None
    filter_expr: Optional[str] = None  # e.g. "Founded Year >= 2010"


class Encoding(BaseModel):
    x: Optional[str] = None
    y: Optional[str] = None
    label: Optional[str] = None
    value: Optional[str] = None
    tooltip: Optional[List[str]] = None


class Style(BaseModel):
    color: Optional[str] = None
    header_bold: Optional[bool] = None
    title: Optional[str] = None


class ChartSpec(BaseModel):
    viz_type: VizType
    transforms: List[Transform]
    encoding: Encoding
    style: Style = Style()


class LLMPlan(BaseModel):
    action: Literal["new_visualization", "update_visualization"]
    target_viz_id: Optional[str] = None
    chart: ChartSpec
