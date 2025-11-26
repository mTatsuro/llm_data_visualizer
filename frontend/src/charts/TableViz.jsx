import React from "react";

/**
 * @typedef {import("../types").Visualization} Visualization
 */

export function TableViz({ viz }) {
  const { data, style } = viz;
  if (!data || !data.length) {
    return <p>No data.</p>;
  }

  const columns = Object.keys(data[0]);
  const fontWeight = style.header_bold ? "bold" : "normal";

  return (
    <div style={{ overflowX: "auto" }}>
      <table>
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col} style={{ fontWeight }}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {columns.map(col => (
                <td key={col}>{row[col]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
