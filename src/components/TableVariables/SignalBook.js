import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
  } from '@tanstack/vue-table'

const columnHelper = createColumnHelper()

 
const columns_signal_book = [ 'timestamp', 'system_timestamp',
     'system_tag', 'action',  'symbol',  'price','qty','quantity','trade_id', 'uid',
     'qty_dir', , 'price_provided',
      'value', 'buy_value', 'sell_value','note', 'action_int'
];

export const columns  = columns_signal_book.map(column => {
  return columnHelper.accessor(row => row[column], {
    id: column,
    cell: info => info.getValue(),
    header: () => column,
  });
});
  


