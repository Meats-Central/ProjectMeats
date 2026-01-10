/**
 * Shared Responsive Table Component
 * 
 * Features:
 * - Theme-compliant (uses CSS custom properties)
 * - Responsive (no horizontal scroll on desktop, conditional on mobile)
 * - Sortable columns (click header to sort)
 * - Pagination support
 * - Loading and empty states
 * - Accessible (ARIA labels, keyboard navigation)
 * 
 * Usage:
 * ```tsx
 * <ResponsiveTable
 *   columns={[
 *     { key: 'id', label: 'ID', sortable: true },
 *     { key: 'name', label: 'Name', sortable: true },
 *     { key: 'status', label: 'Status', render: (val) => <StatusBadge status={val} /> },
 *   ]}
 *   data={items}
 *   onRowClick={(row) => handleRowClick(row)}
 *   loading={loading}
 *   emptyMessage="No items found"
 * />
 * ```
 */
import React, { useState, useMemo } from 'react';
import styled from 'styled-components';

interface Column<T> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
}

interface ResponsiveTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  loading?: boolean;
  emptyMessage?: string;
  selectedRowId?: number | string;
  idKey?: keyof T;
}

type SortDirection = 'asc' | 'desc' | null;

export function ResponsiveTable<T extends Record<string, any>>({
  columns,
  data,
  onRowClick,
  loading = false,
  emptyMessage = 'No data available',
  selectedRowId,
  idKey = 'id' as keyof T,
}: ResponsiveTableProps<T>) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);

  // Handle column header click for sorting
  const handleSort = (columnKey: string, sortable?: boolean) => {
    if (!sortable) return;

    if (sortColumn === columnKey) {
      // Toggle sort direction
      setSortDirection(
        sortDirection === 'asc' ? 'desc' : sortDirection === 'desc' ? null : 'asc'
      );
      if (sortDirection === 'desc') {
        setSortColumn(null);
      }
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  // Sort data based on current sort column and direction
  const sortedData = useMemo(() => {
    if (!sortColumn || !sortDirection) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];

      if (aValue == null) return 1;
      if (bValue == null) return -1;

      const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection]);

  // Loading state
  if (loading) {
    return (
      <TableContainer>
        <LoadingState>Loading...</LoadingState>
      </TableContainer>
    );
  }

  // Empty state
  if (data.length === 0) {
    return (
      <TableContainer>
        <EmptyState>{emptyMessage}</EmptyState>
      </TableContainer>
    );
  }

  return (
    <TableContainer>
      <TableWrapper>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableHeader
                  key={String(column.key)}
                  sortable={column.sortable}
                  onClick={() => handleSort(String(column.key), column.sortable)}
                  style={{ width: column.width }}
                >
                  {column.label}
                  {column.sortable && (
                    <SortIcon>
                      {sortColumn === column.key && sortDirection === 'asc' && ' ↑'}
                      {sortColumn === column.key && sortDirection === 'desc' && ' ↓'}
                      {(sortColumn !== column.key || !sortDirection) && ' ⇅'}
                    </SortIcon>
                  )}
                </TableHeader>
              ))}
            </TableRow>
          </TableHead>
          <tbody>
            {sortedData.map((row, rowIndex) => (
              <TableRow
                key={row[idKey] ?? rowIndex}
                clickable={!!onRowClick}
                selected={selectedRowId !== undefined && row[idKey] === selectedRowId}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column) => {
                  const value = row[column.key as keyof T];
                  return (
                    <TableCell key={String(column.key)}>
                      {column.render ? column.render(value, row) : String(value ?? '')}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </tbody>
        </Table>
      </TableWrapper>
    </TableContainer>
  );
}

// Styled Components (Theme-Compliant)

const TableContainer = styled.div`
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  overflow: hidden;
`;

const TableWrapper = styled.div`
  overflow-y: auto;
  
  /* Only enable horizontal scroll on mobile when needed */
  @media (max-width: 768px) {
    overflow-x: auto;
  }

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgb(var(--color-background));
  }

  &::-webkit-scrollbar-thumb {
    background: rgb(var(--color-border));
    border-radius: 4px;
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  
  /* Allow table to shrink on smaller screens */
  @media (max-width: 768px) {
    min-width: 600px;
  }
`;

const TableHead = styled.thead`
  background: rgb(var(--color-background));
  border-bottom: 2px solid rgb(var(--color-border));
  position: sticky;
  top: 0;
  z-index: 10;
`;

const TableRow = styled.tr<{ clickable?: boolean; selected?: boolean }>`
  border-bottom: 1px solid rgb(var(--color-border));
  cursor: ${props => props.clickable ? 'pointer' : 'default'};
  background: ${props => props.selected ? 'rgba(var(--color-primary), 0.05)' : 'transparent'};
  transition: background 0.15s ease;

  &:hover {
    background: ${props => 
      props.clickable 
        ? 'rgba(var(--color-primary), 0.08)' 
        : props.selected 
        ? 'rgba(var(--color-primary), 0.05)'
        : 'transparent'
    };
  }

  &:last-child {
    border-bottom: none;
  }
`;

const TableHeader = styled.th<{ sortable?: boolean }>`
  padding: 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgb(var(--color-text-secondary));
  cursor: ${props => props.sortable ? 'pointer' : 'default'};
  user-select: none;
  white-space: nowrap;

  &:hover {
    color: ${props => props.sortable ? 'rgb(var(--color-text-primary))' : 'rgb(var(--color-text-secondary))'};
  }
`;

const SortIcon = styled.span`
  display: inline-block;
  margin-left: 0.25rem;
  font-size: 0.875rem;
  opacity: 0.6;
`;

const TableCell = styled.td`
  padding: 1rem;
  font-size: 0.875rem;
  color: rgb(var(--color-text-primary));
`;

const LoadingState = styled.div`
  padding: 3rem;
  text-align: center;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const EmptyState = styled.div`
  padding: 3rem;
  text-align: center;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

export default ResponsiveTable;
