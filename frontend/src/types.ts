export type VizType = 'pie' | 'bar' | 'scatter' | 'table';

export interface Aggregation {
  column: string;
  agg: 'count' | 'sum' | 'mean' | 'min' | 'max';
  new_column: string;
}

export interface Transform {
  op: 'groupby' | 'sort' | 'select' | 'filter' | 'value_counts';
  by?: string[] | null;
  order?: 'asc' | 'desc' | null;
  columns?: string[] | null;
  filter_expr?: string | null;
  aggregations?: Aggregation[] | null;
  column?: string | null;
  delimiter?: string | null;
  top_n?: number | null;
}

export interface Encoding {
  x?: string | null;
  y?: string | null;
  label?: string | null;
  value?: string | null;
  color?: string | null; // optional semantic color for dimension, rarely used
  tooltip?: string[] | null;
}

export interface Style {
  title?: string | null;
  color?: string | null; // chart primary color
  header_bold?: boolean | null;
}

export interface VisualizationResult {
  viz_id: string;
  action: 'new_visualization' | 'update_visualization';
  target_viz_id: string | null;
  viz_type: VizType;
  encoding: Encoding;
  style: Style;
  transforms: Transform[];
  data: any[];
  errors?: string[];
  insights?: Record<string, any>;
}
