import React from "react";
import {
  PieChart,
  Pie,
  Tooltip,
  Legend,
  Cell,
  ResponsiveContainer
} from "recharts";

/**
 * @typedef {import("../types").Visualization} Visualization
 */

const COLORS = [
  "#60a5fa",
  "#f97316",
  "#10b981",
  "#f59e0b",
  "#6b21a8",
  "#ef4444",
  "#14b8a6",
  "#8b5cf6"
];

export function PieChartViz({ viz }) {
  const { data, encoding, style } = viz;
  const labelKey = encoding.label;
  const valueKey = encoding.value;

  if (!labelKey || !valueKey) {
    return <p>Pie chart encoding is incomplete.</p>;
  }

  return (
    <div style={{ height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart
          margin={{ top: 20, right: 160, bottom: 20, left: 20 }}
        >
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={labelKey}
            outerRadius={110}
            label
          >
            {data.map((_, index) => (
              <Cell
                key={index}
                fill={style.color || COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
