import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import type { Encoding, Style } from '../../types';
import { normalizeColor } from '../../utils/colors';
import { formatShortNumber } from '../../utils/format';

interface BarChartViewProps {
  data: any[];
  encoding: Encoding;
  style?: Style;
}

export const BarChartView: React.FC<BarChartViewProps> = ({
  data,
  encoding,
  style,
}) => {
  if (!data.length) {
    return <div className="viz-message">No data to display.</div>;
  }

  const keys = Object.keys(data[0]);
  const xKey =
    encoding.x ||
    encoding.label ||
    (keys.length ? keys[0] : undefined) ||
    '';
  const yKey =
    encoding.y ||
    encoding.value ||
    (keys.length > 1 ? keys[1] : undefined) ||
    '';

  if (!xKey || !yKey) {
    return <div className="viz-message">Bar chart encoding is incomplete.</div>;
  }

  const baseColor = normalizeColor(style?.color) ?? '#4F46E5';

  return (
    <div className="viz-chart-shell">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} />
          <YAxis tickFormatter={formatShortNumber} />
          <Tooltip
            formatter={(value: any) => formatShortNumber(value)}
            labelFormatter={(label: any) => String(label)}
          />
          <Bar dataKey={yKey} fill={baseColor} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
