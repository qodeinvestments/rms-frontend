import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
  } from '@tanstack/vue-table'

const columnHelper = createColumnHelper()

 
const columns_signal_book = ['trade_id', 'uid', 'timestamp', 'system_timestamp',
     'system_tag', 'action', 'action_int', 'qty', 
     'qty_dir', 'symbol', 'price', 'price_provided',
      'value', 'buy_value', 'sell_value','note', 'quantity'
];

export const columns  = columns_signal_book.map(column => {
  return columnHelper.accessor(row => row[column], {
    id: column,
    cell: info => info.getValue(),
    header: () => column,
  });
});
  


