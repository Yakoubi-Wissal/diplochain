import React from "react";

// columns: array of { header, render: row=>jsx }
// data: array of objects
// pageSize: number
// exportFilename: optional string
export default function PaginatedTable({ columns, data, pageSize = 20, exportFilename }) {
  const [page, setPage] = React.useState(0);
  const totalPages = Math.ceil(data.length / pageSize);
  const pageData = data.slice(page * pageSize, (page + 1) * pageSize);

  const downloadCSV = () => {
    const headers = columns.map(c => c.header);
    const rows = data.map(row => columns.map(c => {
      const cell = c.render(row);
      // extract textContent if element
      if (React.isValidElement(cell)) {
        return cell.props.children || '';
      }
      return String(cell ?? '');
    }));
    const csv = [headers, ...rows].map(r => r.map(v=>`"${String(v).replace(/"/g,'""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = exportFilename || 'export.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      {exportFilename && (
        <button onClick={downloadCSV} style={{ marginBottom: 8 }}>Export CSV</button>
      )}
      <table style={{ width:'100%', borderCollapse:'collapse' }}>
        <thead>
          <tr style={{ borderBottom:'1px solid #555' }}>
            {columns.map(c => (
              <th key={c.header} style={{ padding:8, textAlign:'left', fontSize:12 }}>{c.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {pageData.map((row,i) => (
            <tr key={i} style={{ borderBottom:'1px solid #333' }}>
              {columns.map(c => (
                <td key={c.header} style={{ padding:6 }}>{c.render(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {totalPages > 1 && (
        <div style={{ marginTop:8 }}>
          <button onClick={()=>setPage(p=>Math.max(0,p-1))} disabled={page===0}>Prev</button>
          <span style={{ margin:'0 8px' }}>{page+1}/{totalPages}</span>
          <button onClick={()=>setPage(p=>Math.min(totalPages-1,p+1))} disabled={page+1===totalPages}>Next</button>
        </div>
      )}
    </div>
  );
}
