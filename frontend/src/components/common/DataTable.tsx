import { Table, Pagination } from "react-bootstrap";

interface Column<T> {
  key: string;
  label: string;
  render?: (row: T) => React.ReactNode;
}

interface Props<T> {
  columns: Column<T>[];
  data: T[];
  page: number;
  pages: number;
  onPageChange: (p: number) => void;
  onRowClick?: (row: T) => void;
  keyField?: string;
}

export default function DataTable<T extends Record<string, any>>({
  columns,
  data,
  page,
  pages,
  onPageChange,
  onRowClick,
  keyField = "id",
}: Props<T>) {
  return (
    <>
      <div className="table-responsive">
        <Table hover striped className="align-middle mb-0">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="text-center py-4" style={{ color: "var(--muted)" }}>
                  No data found
                </td>
              </tr>
            ) : (
              data.map((row) => (
                <tr
                  key={row[keyField]}
                  onClick={() => onRowClick?.(row)}
                  style={{ cursor: onRowClick ? "pointer" : undefined }}
                >
                  {columns.map((col) => (
                    <td key={col.key}>{col.render ? col.render(row) : row[col.key]}</td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </Table>
      </div>
      {pages > 1 && (
        <div className="d-flex justify-content-center mt-3">
          <Pagination size="sm" className="mb-0">
            <Pagination.Prev disabled={page <= 1} onClick={() => onPageChange(page - 1)} />
            {Array.from({ length: Math.min(pages, 7) }, (_, i) => {
              const p = i + 1;
              return (
                <Pagination.Item key={p} active={p === page} onClick={() => onPageChange(p)}>
                  {p}
                </Pagination.Item>
              );
            })}
            {pages > 7 && <Pagination.Ellipsis disabled />}
            <Pagination.Next disabled={page >= pages} onClick={() => onPageChange(page + 1)} />
          </Pagination>
        </div>
      )}
    </>
  );
}
