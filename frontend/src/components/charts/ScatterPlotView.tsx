import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import type { Encoding, Style } from '../../types';
import { normalizeColor } from '../../utils/colors';
import { formatShortNumber } from '../../utils/format';

interface ScatterPlotViewProps {
  data: any[];
  encoding: Encoding;
  style?: Style;
}

export const ScatterPlotView: React.FC<ScatterPlotViewProps> = ({
  data,
  encoding,
  style,
}) => {
  const xKey = encoding.x || '';
  const yKey = encoding.y || '';

  if (!xKey || !yKey) {
    return (
      <div className="viz-message">Scatter plot encoding is incomplete.</div>
    );
  }

  if (!data.length) {
    return <div className="viz-message">No data to display.</div>;
  }

  const baseColor = normalizeColor(style?.color) ?? '#3B82F6';

  return (
    <div className="viz-chart-shell">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} />
          <YAxis dataKey={yKey} tickFormatter={formatShortNumber} />
          <Tooltip
            formatter={(value: any) => formatShortNumber(value)}
            labelFormatter={(label: any) => String(label)}
          />
          <Scatter data={data} fill={baseColor} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};
