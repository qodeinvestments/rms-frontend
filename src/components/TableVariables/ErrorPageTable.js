import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
  } from '@tanstack/vue-table'

const columnHelper = createColumnHelper()
  
 


 
const order_errors_ob_columns = [
   
'OrderGeneratedDateTime', 'ExchangeTransactTime', 'OrderType', 
'TradingSymbol', 'OrderSide', 'LeavesQuantity', 'OrderQuantity', 
'OrderStatus', 'CancelRejectReason',
"status", "status_message", "order_timestamp",  "variety", "modified", "exchange", "tradingsymbol",
"order_type", "transaction_type", "validity", "validity_ttl", "product",
"quantity", "disclosed_quantity", "price", "trigger_price", "average_price",
"filled_quantity", "pending_quantity", "cancelled_quantity",
"market_protection"
  ];
  
export const  order_errors_columns  = order_errors_ob_columns.map(column => {
return columnHelper.accessor(row => row[column], {
    id: column,
    cell: info => info.getValue(),
    header: () => column,
});
});


const new_order_errors_ob_columns = [
   'Account',
   'Reason',
   'Order Id',
   'Status',
    'Time',
    'Symbol',
    'Order Type',
    'Transaction Type',
    'Quantity',
    'Price',
    // 'Average Price',
    // 'Filled Quantity',
    'Pending Quantity'
  ];
  
export const  new_order_errors_columns  = new_order_errors_ob_columns.map(column => {
return columnHelper.accessor(row => row[column], {
    id: column,
    cell: info => info.getValue(),
    header: () => column,
});
});