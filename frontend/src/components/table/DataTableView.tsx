import React from 'react';
import type { Style } from '../../types';

interface DataTableViewProps {
  data: any[];
  style?: Style;
}

export const DataTableView: React.FC<DataTableViewProps> = ({
  data,
  style,
}) => {
  if (!data.length) {
    return <div className="viz-message">No rows to display.</div>;
  }

  const columns = Object.keys(data[0]);
  const headerClass = style?.header_bold ? 'table-header-bold' : '';

  return (
    <div className="table-wrapper">
      <table className={`table ${headerClass}`}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col}>{String(row[col] ?? '')}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
