import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
  } from '@tanstack/vue-table'
  
  const columnHelper = createColumnHelper()
  
  const columns_gg = ['System', 'Direction', 'DateTime']
  
  export const columns = columns_gg.map(column => {
    if (column === 'Direction') {
      // Render 🟩 if value is 1.0, else 🟥
      return columnHelper.accessor(
        row => row.Direction,
        {
          id: 'Direction',
          header: () => 'Direction',
          cell: info => info.getValue() === 1.0 ? '🟩' : '🟥',
        }
      )
    } else {
      // Default columns
      return columnHelper.accessor(
        row => row[column],
        {
          id: column,
          header: () => column,
          cell: info => info.getValue(),
        }
      )
    }
  })
  