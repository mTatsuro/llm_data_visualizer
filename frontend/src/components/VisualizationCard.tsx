import React from 'react';
import type { VisualizationResult } from '../types';
import { PieChartView } from './charts/PieChartView';
import { BarChartView } from './charts/BarChartView';
import { ScatterPlotView } from './charts/ScatterPlotView';
import { DataTableView } from './table/DataTableView';

interface VisualizationCardProps {
  viz: VisualizationResult;
  isActive: boolean;
  onSelect: () => void;
}

const vizLabel: Record<string, string> = {
  pie: 'Pie chart',
  bar: 'Bar chart',
  scatter: 'Scatter plot',
  table: 'Table',
};

export const VisualizationCard: React.FC<VisualizationCardProps> = ({
  viz,
  isActive,
  onSelect,
}) => {
  const { viz_type, style, encoding, data, errors, insights, viz_id } = viz;
  const title = style?.title || 'Untitled visualization';

  const corr =
    insights && typeof insights.pearson_correlation === 'number'
      ? insights.pearson_correlation
      : null;

  return (
    <div
      className={`viz-card ${isActive ? 'active' : ''}`}
      onClick={onSelect}
      role="button"
    >
      <div className="viz-card-header">
        <div className="viz-card-title">{title}</div>
        <div className="viz-card-meta">
          <span className="viz-type-pill">{vizLabel[viz_type] ?? viz_type}</span>
          <span className="viz-id-pill">{viz_id.slice(0, 8)}</span>
        </div>
      </div>
      <div className="viz-card-body">
        {errors && errors.length > 0 && (
          <div style={{ marginBottom: '0.3rem' }}>
            <span className="badge-error">
              ⚠ {errors.length === 1 ? errors[0] : 'Multiple issues with this spec'}
            </span>
          </div>
        )}

        {viz_type === 'pie' && (
          <PieChartView data={data} encoding={encoding} style={style} />
        )}
        {viz_type === 'bar' && (
          <BarChartView data={data} encoding={encoding} style={style} />
        )}
        {viz_type === 'scatter' && (
          <ScatterPlotView data={data} encoding={encoding} style={style} />
        )}
        {viz_type === 'table' && <DataTableView data={data} style={style} />}

        {(!data || data.length === 0) && !errors?.length && (
          <div className="viz-message">
            This visualization has no data rows after applying transforms.
          </div>
        )}

        {corr !== null && (
          <div className="insights-row">
            Pearson correlation: <strong>{corr.toFixed(3)}</strong>
          </div>
        )}
      </div>
    </div>
  );
};
