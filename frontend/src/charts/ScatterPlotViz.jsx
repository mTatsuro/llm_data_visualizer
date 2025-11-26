import React from "react";
import {
  ScatterChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Scatter,
  ResponsiveContainer
} from "recharts";

/**
 * @typedef {import("../types").Visualization} Visualization
 */

export function ScatterPlotViz({ viz }) {
  const { data, encoding, style } = viz;
  const { x, y } = encoding;

  if (!x || !y) {
    return <p>Scatter plot encoding is incomplete.</p>;
  }

  return (
    <div style={{ height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid />
          <XAxis dataKey={x} />
          <YAxis dataKey={y} />
          <Tooltip />
          <Scatter data={data} fill={style.color || "#60a5fa"} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
