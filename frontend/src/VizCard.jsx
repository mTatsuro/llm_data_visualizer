import React from "react";
import { PieChartViz } from "./charts/PieChartViz";
import { ScatterPlotViz } from "./charts/ScatterPlotViz";
import { TableViz } from "./charts/TableViz";

/**
 * @typedef {import("./types").Visualization} Visualization
 */

export function VizCard({ viz, selected, onSelect }) {
  const { style, insights } = viz;
  const border = selected ? "2px solid #2563eb" : "1px solid #e5e7eb";

  return (
    <div
      className="viz-card"
      style={{
        border,
        padding: "1rem",
        borderRadius: "0.75rem",
        background: "white",
        boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
        cursor: "pointer"
      }}
      onClick={onSelect}
    >
      <h2>{style?.title || "Untitled visualization"}</h2>

      {viz.viz_type === "pie" && <PieChartViz viz={viz} />}
      {viz.viz_type === "scatter" && <ScatterPlotViz viz={viz} />}
      {viz.viz_type === "table" && <TableViz viz={viz} />}

      {insights && typeof insights.pearson_correlation === "number" && (
        <p style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "#374151" }}>
          Pearson correlation:{" "}
          {insights.pearson_correlation.toFixed(3)}
        </p>
      )}
    </div>
  );
}
