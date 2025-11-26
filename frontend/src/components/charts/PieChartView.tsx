import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { Encoding, Style } from '../../types';
import { normalizeColor } from '../../utils/colors';
import { formatShortNumber } from '../../utils/format';

interface PieChartViewProps {
  data: any[];
  encoding: Encoding;
  style?: Style;
}

/**
 * Generic pie-chart renderer.
 *
 * To keep layout reasonable for any dataset:
 * - Only the top N categories by value are shown as individual slices.
 * - Remaining categories are grouped into an "Other" slice.
 * - Values are formatted into short numeric form in tooltips/legend.
 */
export const PieChartView: React.FC<PieChartViewProps> = ({
  data,
  encoding,
  style,
}) => {
  const labelKey = encoding.label || '';
  const valueKey = encoding.value || '';

  if (!labelKey || !valueKey) {
    return <div className="viz-message">Pie chart encoding is incomplete.</div>;
  }

  if (!data.length) {
    return <div className="viz-message">No data to display.</div>;
  }

  // Coerce value column to numbers where possible
  const numericData = data
    .map((row) => {
      const raw = row[valueKey];
      const num = typeof raw === 'number' ? raw : parseFloat(String(raw));
      return Number.isFinite(num)
        ? { ...row, [valueKey]: num }
        : null;
    })
    .filter((d): d is any => d !== null);

  if (!numericData.length) {
    return (
      <div className="viz-message">
        Pie chart cannot be drawn because the value column is not numeric.
      </div>
    );
  }

  // Sort by value desc and keep top N, group the rest into "Other".
  const MAX_SLICES = 10;
  const sorted = [...numericData].sort(
    (a, b) => b[valueKey] - a[valueKey],
  );

  let sliced = sorted;
  if (sorted.length > MAX_SLICES) {
    const top = sorted.slice(0, MAX_SLICES);
    const rest = sorted.slice(MAX_SLICES);
    const otherTotal = rest.reduce(
      (acc, row) => acc + (row[valueKey] ?? 0),
      0,
    );
    if (otherTotal > 0) {
      top.push({
        [labelKey]: 'Other',
        [valueKey]: otherTotal,
      });
    }
    sliced = top;
  }

  const total = sliced.reduce((acc, row) => acc + (row[valueKey] ?? 0), 0) || 1;

  const baseColor = normalizeColor(style?.color) ?? '#6366F1';

  // Palette derived by mixing base color with white using different opacities.
  const colors = sliced.map((_, idx) => {
    const alpha = 0.35 + (0.55 * (idx + 1)) / (sliced.length + 1);
    return `color-mix(in srgb, ${baseColor} ${Math.round(
      alpha * 100,
    )}%, white)`;
  });

  const renderTooltip = ({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: any[];
  }) => {
    if (!active || !payload || !payload.length) return null;
    const entry = payload[0];
    const label = entry?.payload?.[labelKey];
    const value = entry?.payload?.[valueKey] ?? 0;
    const pct = (100 * value) / total;
    return (
      <div
        style={{
          background: 'white',
          borderRadius: 8,
          padding: '0.35rem 0.5rem',
          boxShadow:
            '0 10px 15px -3px rgba(15, 23, 42, 0.15), 0 4px 6px -4px rgba(15, 23, 42, 0.1)',
          border: '1px solid #e5e7eb',
          fontSize: '0.75rem',
        }}
      >
        <div style={{ fontWeight: 600 }}>{label}</div>
        <div>
          {formatShortNumber(value)} ({pct.toFixed(1)}%)
        </div>
      </div>
    );
  };

  const legendFormatter = (value: string) => value;

  return (
    <div className="viz-chart-shell">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={sliced}
            dataKey={valueKey}
            nameKey={labelKey}
            outerRadius="85%"
            isAnimationActive={false}
          >
            {sliced.map((_: any, i: number) => (
              <Cell key={i} fill={colors[i]} />
            ))}
          </Pie>
          <Tooltip content={renderTooltip} />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            formatter={legendFormatter}
          />
        </PieChart>
      </ResponsiveContainer>
      {data.length > sliced.length && (
        <div className="small-muted" style={{ marginTop: '0.2rem' }}>
          Showing top {sliced.length - 1} categories by value; remaining categories
          grouped into <strong>Other</strong>.
        </div>
      )}
    </div>
  );
};
