
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
  } from '@tanstack/vue-table'

const columnHelper = createColumnHelper()
export const columns = [
    columnHelper.accessor(row => row.AccountName, {
      id: 'AccountName',
      cell: info => info.getValue(),
      header: () => 'Account Name',
    }),

    columnHelper.accessor(row => row.Day_PL, {
      id: 'Day_PL',
      cell: info => info.getValue(),
      header: () => 'Day_PL',
    }),
    
    columnHelper.accessor(row => row.Portfolio_Value, {
      id: 'Portfolio Value',
      cell: info => info.getValue(),
      header: () => 'Portfolio Value',
    }),
   
  
  ]