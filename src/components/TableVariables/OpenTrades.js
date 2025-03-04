import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
  } from '@tanstack/vue-table'

const columnHelper = createColumnHelper()

 
const columns_signal_book = [ 'system_timestamp', 'timestamp', 'system_tag', 'symbol', 'price', 'quantity','action','price_provided', 'value', 'buy_value', 'sell_value',  'note', ,'trade_id', 'uid', 'action_int', 'qty', 'qty_dir',
];

export const columns  = columns_signal_book.map(column => {
  return columnHelper.accessor(row => row[column], {
    id: column,
    cell: info => info.getValue(),
    header: () => column,
  });
});
  


