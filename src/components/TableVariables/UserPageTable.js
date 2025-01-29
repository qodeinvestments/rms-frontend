  
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
  } from '@tanstack/vue-table'

const columnHelper = createColumnHelper()
  
 
// const zerodha_ob_columns = [
//   'order_timestamp',  'transaction_type','tradingsymbol','product',
//   //  'quantity',  'filled_quantity','disclosed_quantity', 
//   // 'pending_quantity', 'cancelled_quantity',
//    'average_price','status','order_type',
  
//   'variety', 'modified', 'exchange', 'validity',  'price','trigger_price', 'exchange_update_timestamp', 
//   'exchange_timestamp'
//   // 'market_protection', 'meta',
//   // 'tag', 'tags', 'guid','status_message', 'status_message_raw','account_id', 'order_id', 'exchange_order_id','instrument_token','validity_ttl'
// ];

// export const zerodha_order_book_columns = [
//   ...zerodha_ob_columns.map(column => {
//     return columnHelper.accessor(row => row[column], {
//       id: column,
//       cell: info => info.getValue(),
//       header: () => column,
//     });
//   }),
//   // Add the custom column
//   columnHelper.accessor(row => `${row['quantity']}/${row['filled_quantity']}`, {
//     id: 'quantity_ratio',
//     cell: info => info.getValue(),
//     header: () => 'Quantity/Filled Quantity',
//   }),
// ];


const zerodha_ob_columns = [
  'order_timestamp', 'transaction_type', 'tradingsymbol', 'product',
  'average_price', 'status', 'order_type',
  'variety', 'modified', 'exchange', 'validity', 'price', 'trigger_price', 
  'exchange_update_timestamp', 'exchange_timestamp',  'quantity',  'filled_quantity','disclosed_quantity', 
   'pending_quantity', 'cancelled_quantity',
];

// Define custom columns with their desired positions
const customColumns = [
  {
    id: 'quantity_ratio',
    position: 3, // Position where you want to insert (1-based index)
    accessor: row => `${row['quantity']}/${row['filled_quantity']}`,
    header: 'Quantity/Filled Quantity'
  },
];

export const zerodha_order_book_columns = (() => {
  // First, create array of standard columns
  let columns = zerodha_ob_columns.map(column => {
    return columnHelper.accessor(row => row[column], {
      id: column,
      cell: info => info.getValue(),
      header: () => column,
    });
  });

  // Sort custom columns by position to ensure correct insertion order
  const sortedCustomColumns = [...customColumns].sort((a, b) => a.position - b.position);

  // Insert each custom column at its specified position
  sortedCustomColumns.forEach(customCol => {
    const position = Math.min(Math.max(1, customCol.position), columns.length + 1) - 1;
    const customColumn = columnHelper.accessor(customCol.accessor, {
      id: customCol.id,
      cell: info => info.getValue(),
      header: () => customCol.header,
    });
    
    columns.splice(position, 0, customColumn);
  });

  return columns;
})();


const zerodha_pos_columns=[
   'product','tradingsymbol','quantity', 'average_price', 'last_price','pnl', 'm2m', 'unrealised', 'realised','exchange', 'instrument_token',  'overnight_quantity', 'multiplier', 'close_price', 'value',  'buy_quantity', 'buy_price', 'buy_value', 'buy_m2m', 'sell_quantity', 'sell_price', 'sell_value', 'sell_m2m', 'day_buy_quantity', 'day_buy_price', 'day_buy_value', 'day_sell_quantity', 'day_sell_price', 'day_sell_value'
]

export const zerodha_position_book_columns = [
  ...zerodha_pos_columns.map(column => {
    return columnHelper.accessor(row => row[column], {
      id: column,
      cell: info => info.getValue(),
      header: () => column,
    });
  }),

];

const client_holdings=[
  'tradingsymbol', 'quantity', 
  'price', 'average_price','product', 'exchange','instrument_token']

  export const holding_book_columns  = client_holdings.map(column => {
    return columnHelper.accessor(row => row[column], {
      id: column,
      cell: info => info.getValue(),
      header: () => column,
    });
  });


  
  export const live_trade_book_columns_zerodha = [

    columnHelper.accessor(row => row.exchange, {
      id: 'exchange',
      cell: info => info.getValue(),
      header: () => 'exchange',
    }),
    columnHelper.accessor(row => row.tradingsymbol, {
      id: 'tradingsymbol',
      cell: info => info.getValue(),
      header: () => 'tradingsymbol',
    }),
    columnHelper.accessor(row => row.product, {
      id: 'product',
      cell: info => info.getValue(),
      header: () => 'product',
    }),
    columnHelper.accessor(row => row.average_price, {
      id: 'average_price',
      cell: info => info.getValue(),
      header: () => 'average_price',
    }),
    columnHelper.accessor(row => row.quantity, {
      id: 'quantity',
      cell: info => info.getValue(),
      header: () => 'quantity',
    }),
    columnHelper.accessor(row => row.transaction_type, {
      id: 'transaction_type',
      cell: info => info.getValue(),
      header: () => 'transaction_type',
    }),
    columnHelper.accessor(row => row.fill_timestamp, {
      id: 'fill_timestamp',
      cell: info => info.getValue(),
      header: () => 'fill_timestamp',
    }),
    columnHelper.accessor(row => row.order_timestamp, {
      id: 'order_timestamp',
      cell: info => info.getValue(),
      header: () => 'order_timestamp',
    }),
    columnHelper.accessor(row => row.exchange_timestamp, {
      id: 'exchange_timestamp',
      cell: info => info.getValue(),
      header: () => 'exchange_timestamp',
    }),
  
  ]


  export const live_trade_book_columns_xts = [
    columnHelper.accessor(row => row.OrderGeneratedDateTime, {
      id: 'OrderGeneratedDateTime',
      cell: info => info.getValue(),
      header: () => 'OrderGeneratedDateTime',
    }),
    columnHelper.accessor(row => row.ExchangeTransactTime, {
      id: 'ExchangeTransactTime',
      cell: info => info.getValue(),
      header: () => 'ExchangeTransactTime',
    }),
    columnHelper.accessor(row => row.OrderAverageTradedPrice, {
      id: 'OrderAverageTradedPrice',
      cell: info => info.getValue(),
      header: () => 'OrderAverageTradedPrice',
    }),
    columnHelper.accessor(row => row.OrderSide, {
      id: 'OrderSide',
      cell: info => info.getValue(),
      header: () => 'OrderSide',
    }),
    columnHelper.accessor(row => row.OrderQuantity, {
      id: 'OrderQuantity',
      cell: info => info.getValue(),
      header: () => 'OrderQuantity',
    }),
  ]

  export const live_order_book_columns_zerodha = [
    columnHelper.accessor(row => row.status, {
        id: 'status',
        cell: info => info.getValue(),
        header: () => 'status',
    }),
    columnHelper.accessor(row => row.order_timestamp, {
        id: 'order_timestamp',
        cell: info => info.getValue(),
        header: () => 'order_timestamp',
    }),
    columnHelper.accessor(row => row.exchange_update_timestamp, {
        id: 'exchange_update_timestamp',
        cell: info => info.getValue(),
        header: () => 'exchange_update_timestamp',
    }),
    columnHelper.accessor(row => row.exchange_timestamp, {
        id: 'exchange_timestamp',
        cell: info => info.getValue(),
        header: () => 'exchange_timestamp',
    }),
    columnHelper.accessor(row => row.variety, {
        id: 'variety',
        cell: info => info.getValue(),
        header: () => 'variety',
    }),
    columnHelper.accessor(row => row.modified, {
        id: 'modified',
        cell: info => info.getValue(),
        header: () => 'modified',
    }),
    columnHelper.accessor(row => row.exchange, {
        id: 'exchange',
        cell: info => info.getValue(),
        header: () => 'exchange',
    }),
    columnHelper.accessor(row => row.tradingsymbol, {
        id: 'tradingsymbol',
        cell: info => info.getValue(),
        header: () => 'tradingsymbol',
    }),
    columnHelper.accessor(row => row.order_type, {
        id: 'order_type',
        cell: info => info.getValue(),
        header: () => 'order_type',
    }),
    columnHelper.accessor(row => row.transaction_type, {
        id: 'transaction_type',
        cell: info => info.getValue(),
        header: () => 'transaction_type',
    }),
    columnHelper.accessor(row => row.validity, {
        id: 'validity',
        cell: info => info.getValue(),
        header: () => 'validity',
    }),
    columnHelper.accessor(row => row.validity_ttl, {
        id: 'validity_ttl',
        cell: info => info.getValue(),
        header: () => 'validity_ttl',
    }),
    columnHelper.accessor(row => row.product, {
        id: 'product',
        cell: info => info.getValue(),
        header: () => 'product',
    }),
    columnHelper.accessor(row => row.quantity, {
        id: 'quantity',
        cell: info => info.getValue(),
        header: () => 'quantity',
    }),
    columnHelper.accessor(row => row.disclosed_quantity, {
        id: 'disclosed_quantity',
        cell: info => info.getValue(),
        header: () => 'disclosed_quantity',
    }),
    columnHelper.accessor(row => row.price, {
        id: 'price',
        cell: info => info.getValue(),
        header: () => 'price',
    }),
    columnHelper.accessor(row => row.trigger_price, {
        id: 'trigger_price',
        cell: info => info.getValue(),
        header: () => 'trigger_price',
    }),
    columnHelper.accessor(row => row.average_price, {
        id: 'average_price',
        cell: info => info.getValue(),
        header: () => 'average_price',
    }),
    columnHelper.accessor(row => row.filled_quantity, {
        id: 'filled_quantity',
        cell: info => info.getValue(),
        header: () => 'filled_quantity',
    }),
    columnHelper.accessor(row => row.pending_quantity, {
        id: 'pending_quantity',
        cell: info => info.getValue(),
        header: () => 'pending_quantity',
    }),
    columnHelper.accessor(row => row.cancelled_quantity, {
        id: 'cancelled_quantity',
        cell: info => info.getValue(),
        header: () => 'cancelled_quantity',
    }),
    columnHelper.accessor(row => row.market_protection, {
        id: 'market_protection',
        cell: info => info.getValue(),
        header: () => 'market_protection',
    }),
    columnHelper.accessor(row => row.status_message, {
        id: 'status_message',
        cell: info => info.getValue(),
        header: () => 'status_message',
    }),
  ]

  export const fund_summary_columns = [
    columnHelper.accessor(row => row.Date, {
      id: 'Date',
      cell: info => info.getValue(),
      header: () => 'Date',
    }),
    columnHelper.accessor(row => row['Actual MTM'], {
      id: 'Actual MTM',
      cell: info => info.getValue(),
      header: () => 'Actual MTM',
    }),
    columnHelper.accessor(row => row['Ideal MTM'], {
      id: 'Ideal MTM',
      cell: info => info.getValue(),
      header: () => 'Ideal MTM',
    }),
    columnHelper.accessor(row => row['Peak Margin'], {
      id: 'Peak Margin',
      cell: info => info.getValue(),
      header: () => 'Peak Margin',
    })
  ]

  export const live_order_book_columns_xts = [
    columnHelper.accessor(row => row.OrderGeneratedDateTime, {
      id: 'OrderGeneratedDateTime',
      cell: info => info.getValue(),
      header: () => 'OrderGeneratedDateTime',
    }),
    columnHelper.accessor(row => row.OrderType, {
      id: 'OrderType',
      cell: info => info.getValue(),
      header: () => 'OrderType',
    }),
    columnHelper.accessor(row => row.ExchangeTransactTime, {
      id: 'ExchangeTransactTime',
      cell: info => info.getValue(),
      header: () => 'ExchangeTransactTime',
    }),
    columnHelper.accessor(row => row.TradingSymbol, {
      id: 'TradingSymbol',
      cell: info => info.getValue(),
      header: () => 'TradingSymbol',
    }),
    columnHelper.accessor(row => row.OrderAverageTradedPrice, {
      id: 'OrderAverageTradedPrice',
      cell: info => info.getValue(),
      header: () => 'OrderAverageTradedPrice',
    }),
    columnHelper.accessor(row => row.CumulativeQuantity, {
      id: 'CumulativeQuantity',
      cell: info => info.getValue(),
      header: () => 'CumulativeQuantity',
    }),
    columnHelper.accessor(row => row.AppOrderID, {
      id: 'AppOrderID',
      cell: info => info.getValue(),
      header: () => 'AppOrderID',
    }),
    columnHelper.accessor(row => row.OrderSide, {
      id: 'OrderSide',
      cell: info => info.getValue(),
      header: () => 'OrderSide',
    }),
    columnHelper.accessor(row => row.OrderQuantity, {
      id: 'OrderQuantity',
      cell: info => info.getValue(),
      header: () => 'OrderQuantity',
    }),
    columnHelper.accessor(row => row.LeavesQuantity, {
      id: 'LeavesQuantity',
      cell: info => info.getValue(),
      header: () => 'LeavesQuantity',
    }),
    columnHelper.accessor(row => row.OrderStatus, {
      id: 'OrderStatus',
      cell: info => info.getValue(),
      header: () => 'OrderStatus',
    }),
    columnHelper.accessor(row => row.CancelRejectReason, {
      id: 'CancelRejectReason',
      cell: info => info.getValue(),
      header: () => 'CancelRejectReason',
    }),
  ]

  export const signal_position = [
  
    columnHelper.accessor(row => row.Symbol, {
      id: 'Symbol',
      cell: info => info.getValue(),
      header: () => 'Symbol',
    }),
    columnHelper.accessor(row => row.IdealQuantity, {
      id: 'IdealQuantity',
      cell: info => info.getValue(),
      header: () => 'IdealQuantity',
    }),
  ]

  export const columns = [
  
    columnHelper.accessor(row => row.AccountName, {
      id: 'AccountName',
      cell: info => info.getValue(),
      header: () => 'Account Name',
    }),
    columnHelper.accessor(row => row.IdealMTM, {
      id: 'IdealMTM',
      cell: info => info.getValue(),
      header: () => 'Ideal MTM',
    }),
    columnHelper.accessor(row => row.Day_PL, {
      id: 'Day_PL',
      cell: info => info.getValue(),
      header: () => 'Day_PL',
    }),
    columnHelper.accessor(row => row.PNL_PER_UM, {
      id: 'PNL_PER_UM',
      cell: info => {
        const value = info.getValue(); // Get the value
        return (typeof value === 'number' ? value : Number(value)).toFixed(2) + "%"; // Ensure it's a number and format
      },
      header: () => 'PNL Utilized %',
    }),
    columnHelper.accessor(row => row.PNL_PER_M, {
      id: 'PNL_PER_M',
      cell: info => {
        const value = info.getValue(); // Get the value
        return (typeof value === 'number' ? value : Number(value)).toFixed(2) + "%"; // Ensure it's a number and format
      },
      header: () => 'PNL Overall %',
    }),
  
    columnHelper.accessor(row => row.Slippage, {
      id: 'Slippage',
      cell: info => info.getValue(),
      header: () => 'Slippage',
    }),
    columnHelper.accessor(row => row.Ideal_Margin, {
      id: 'Ideal Margin',
      cell: info => info.getValue(),
      header: () => 'Ideal Margin',
    }),
    columnHelper.accessor(row => row.VAR, {
      id: 'VAR',
      cell: info => {
        const value = info.getValue(); // Get the value
        return (typeof value === 'number' ? value : Number(value)).toFixed(2); // Ensure it's a number and format
      },
      header: () => 'VAR \u20B9',
    }),
    columnHelper.accessor(row => row.VAR_PERCENTAGE, {
      id: 'VAR %',
      cell: info => {
        const value = info.getValue(); // Get the value
        return (typeof value === 'number' ? value : Number(value)).toFixed(2) + "%"; // Ensure it's a number and format
      },
      header: () => 'VAR %',
    }),
  
    columnHelper.accessor(row => row.Peak_Margin, {
      id: 'Peak_Margin',
      cell: info => info.getValue(),
      header: () => 'Peak Margin',
    }),
    columnHelper.accessor(row => row.Margin, {
      id: ' Margin',
      cell: info => info.getValue(),
      header: () => 'Margin',
    }),
  
    columnHelper.accessor(row => row.Used_Margin, {
      id: 'Used_Margin',
      cell: info => info.getValue(),
      header: () => 'Used_Margin',
    }),
    columnHelper.accessor(row => row.AvailableMargin, {
      id: 'AvailableMargin',
      cell: info => info.getValue(),
      header: () => 'AvailableMargin',
    }),
    columnHelper.accessor(row => row.Slippage1, {
      id: 'Slippage1',
      cell: info => info.getValue(),
      header: () => 'Ideal Slippage 0.5 MTM',
    }),
    columnHelper.accessor(row => row.Slippage2 ,{
      id: 'Slippage2',
      cell: info => info.getValue(),
      header: () => 'Ideal Slippage 1 MTM',
    }),
    columnHelper.accessor(row => row.Cash, {
      id: 'Cash',
      cell: info => info.getValue(),
      header: () => 'Cash',
    }),
    columnHelper.accessor(row => row.NetQuantity, {
      id: 'NetQuantity',
      cell: info => info.getValue(),
      header: () => 'NetQuantity',
    }),
    columnHelper.accessor(row => row.OpenQuantity, {
      id: 'OpenQuantity',
      cell: info => info.getValue(),
      header: () => 'OpenQuantity',
    }),
    columnHelper.accessor(row => row.openOrderCount, {
      id: 'OpenOrderCount',
      cell: info => info.getValue(),
      header: () => 'OpenOrderCount',
    }),
    columnHelper.accessor(row => row.CompleteOrderCount, {
      id: 'CompleteOrderCount',
      cell: info => info.getValue(),
      header: () => 'CompleteOrderCount',
    }),
    columnHelper.accessor(row => row.RejectedOrderCount, {
      id: 'RejectedOrderCount',
      cell: info => info.getValue(),
      header: () => 'RejectedOrderCount',
    }),
    columnHelper.accessor(row => row.PendingOrderCount, {
      id: 'PendingOrderCount',
      cell: info => info.getValue(),
      header: () => 'PendingOrderCount',
    }),
    columnHelper.accessor(row => row.PortfolioValue, {
      id: 'PortfolioValue',
      cell: info => info.getValue(),
      header: () => 'Portfolio Value',
    }),
    columnHelper.accessor(row => row.PositionDayPL, {
      id: 'PositionDayPL',
      cell: info => info.getValue(),
      header: () => 'PositionDayPL',
    }),
    columnHelper.accessor(row => row.HoldingsDayPL, {
      id: 'HoldingsDayPL',
      cell: info => info.getValue(),
      header: () => 'HoldingsDayPL',
    }),
  
    columnHelper.accessor(row => row.TotalOrderCount, {
      id: 'TotalOrderCount',
      cell: info => info.getValue(),
      header: () => 'TotalOrderCount',
    }),
  
    columnHelper.accessor(row => row.PositionsCount, {
      id: 'PositionsCount',
      cell: info => info.getValue(),
      header: () => 'PositionsCount',
    }),
    columnHelper.accessor(row => row.HoldingsCount, {
      id: 'HoldingsCount',
      cell: info => info.getValue(),
      header: () => 'HoldingsCount',
    }),
  
  ]

  export const combined_df_columns_zerodha = [
    columnHelper.accessor(row => row.system_tag, {
      id: 'system_tag',
      cell: info => info.getValue(),
      header: () => 'system_tag',
    }),
    columnHelper.accessor(row => row.order_fill_lag, {
      id: 'order_fill_lag',
      cell: info => info.getValue(),
      header: () => 'order_fill_lag',
    }),
    columnHelper.accessor(row => row.signal_lag, {
      id: 'signal_lag',
      cell: info => info.getValue(),
      header: () => 'signal_lag',
    }),
    columnHelper.accessor(row => row.place_order_lag, {
      id: 'place_order_lag',
      cell: info => info.getValue(),
      header: () => 'place_order_lag',
    }),
    columnHelper.accessor(row => row.timestamp, {
      id: 'timestamp',
      cell: info => info.getValue(),
      header: () => 'timestamp',
    }),
    columnHelper.accessor(row => row.system_timestamp, {
      id: 'system_timestamp',
      cell: info => info.getValue(),
      header: () => 'system_timestamp',
    }),
    columnHelper.accessor(row => row.symbol, {
      id: 'symbol',
      cell: info => info.getValue(),
      header: () => 'symbol',
    }),
    columnHelper.accessor(row => row.tradingsymbol, {
      id: 'tradingsymbol',
      cell: info => info.getValue(),
      header: () => 'tradingsymbol',
    }),
    columnHelper.accessor(row => row.trade_id, {
      id: 'trade_id',
      cell: info => info.getValue(),
      header: () => 'trade_id',
    }),
    columnHelper.accessor(row => row.uid, {
      id: 'uid',
      cell: info => info.getValue(),
      header: () => 'uid',
    }),
  
    columnHelper.accessor(row => row.action, {
      id: 'action',
      cell: info => info.getValue(),
      header: () => 'action',
    }),
    columnHelper.accessor(row => row.action_int, {
      id: 'action_int',
      cell: info => info.getValue(),
      header: () => 'action_int',
    }),
    columnHelper.accessor(row => row.qty, {
      id: 'qty',
      cell: info => info.getValue(),
      header: () => 'qty',
    }),
    columnHelper.accessor(row => row.qty_dir, {
      id: 'qty_dir',
      cell: info => info.getValue(),
      header: () => 'qty_dir',
    }),
  
    columnHelper.accessor(row => row.price_x, {
      id: 'price_x',
      cell: info => info.getValue(),
      header: () => 'price_x',
    }),
    columnHelper.accessor(row => row.value, {
      id: 'value',
      cell: info => info.getValue(),
      header: () => 'value',
    }),
    columnHelper.accessor(row => row.buy_value, {
      id: 'buy_value',
      cell: info => info.getValue(),
      header: () => 'buy_value',
    }),
    columnHelper.accessor(row => row.sell_value, {
      id: 'sell_value',
      cell: info => info.getValue(),
      header: () => 'sell_value',
    }),
  
    columnHelper.accessor(row => row.note, {
      id: 'note',
      cell: info => info.getValue(),
      header: () => 'note',
    }),
    columnHelper.accessor(row => row.basket, {
      id: 'basket',
      cell: info => info.getValue(),
      header: () => 'basket',
    }),
    columnHelper.accessor(row => row.qty_multiplier, {
      id: 'qty_multiplier',
      cell: info => info.getValue(),
      header: () => 'qty_multiplier',
    }),
    columnHelper.accessor(row => row.effective_qty, {
      id: 'effective_qty',
      cell: info => info.getValue(),
      header: () => 'effective_qty',
    }),
    columnHelper.accessor(row => row.status, {
      id: 'status',
      cell: info => info.getValue(),
      header: () => 'status',
    }),
    columnHelper.accessor(row => row.order_timestamp, {
      id: 'order_timestamp',
      cell: info => info.getValue(),
      header: () => 'order_timestamp',
    }),
    columnHelper.accessor(row => row.exchange_update_timestamp, {
      id: 'exchange_update_timestamp',
      cell: info => info.getValue(),
      header: () => 'exchange_update_timestamp',
    }),
    columnHelper.accessor(row => row.exchange_timestamp, {
      id: 'exchange_timestamp',
      cell: info => info.getValue(),
      header: () => 'exchange_timestamp',
    }),
    columnHelper.accessor(row => row.variety, {
      id: 'variety',
      cell: info => info.getValue(),
      header: () => 'variety',
    }),
    columnHelper.accessor(row => row.modified, {
      id: 'modified',
      cell: info => info.getValue(),
      header: () => 'modified',
    }),
    columnHelper.accessor(row => row.exchange, {
      id: 'exchange',
      cell: info => info.getValue(),
      header: () => 'exchange',
    }),
  
    columnHelper.accessor(row => row.order_type, {
      id: 'order_type',
      cell: info => info.getValue(),
      header: () => 'order_type',
    }),
    columnHelper.accessor(row => row.transaction_type, {
      id: 'transaction_type',
      cell: info => info.getValue(),
      header: () => 'transaction_type',
    }),
    columnHelper.accessor(row => row.validity, {
      id: 'validity',
      cell: info => info.getValue(),
      header: () => 'validity',
    }),
    columnHelper.accessor(row => row.validity_ttl, {
      id: 'validity_ttl',
      cell: info => info.getValue(),
      header: () => 'validity_ttl',
    }),
    columnHelper.accessor(row => row.product, {
      id: 'product',
      cell: info => info.getValue(),
      header: () => 'product',
    }),
    columnHelper.accessor(row => row.quantity_y, {
      id: 'quantity_y',
      cell: info => info.getValue(),
      header: () => 'quantity_y',
    }),
    columnHelper.accessor(row => row.disclosed_quantity, {
      id: 'disclosed_quantity',
      cell: info => info.getValue(),
      header: () => 'disclosed_quantity',
    }),
    columnHelper.accessor(row => row.price_y, {
      id: 'price_y',
      cell: info => info.getValue(),
      header: () => 'price_y',
    }),
    columnHelper.accessor(row => row.trigger_price, {
      id: 'trigger_price',
      cell: info => info.getValue(),
      header: () => 'trigger_price',
    }),
    columnHelper.accessor(row => row.average_price, {
      id: 'average_price',
      cell: info => info.getValue(),
      header: () => 'average_price',
    }),
    columnHelper.accessor(row => row.filled_quantity, {
      id: 'filled_quantity',
      cell: info => info.getValue(),
      header: () => 'filled_quantity',
    }),
    columnHelper.accessor(row => row.pending_quantity, {
      id: 'pending_quantity',
      cell: info => info.getValue(),
      header: () => 'pending_quantity',
    }),
    columnHelper.accessor(row => row.cancelled_quantity, {
      id: 'cancelled_quantity',
      cell: info => info.getValue(),
      header: () => 'cancelled_quantity',
    }),
    columnHelper.accessor(row => row.market_protection, {
      id: 'market_protection',
      cell: info => info.getValue(),
      header: () => 'market_protection',
    }),
    columnHelper.accessor(row => row.OrderQuantityDir, {
      id: 'OrderQuantityDir',
      cell: info => info.getValue(),
      header: () => 'OrderQuantityDir',
    }),
    columnHelper.accessor(row => row.effective_cal_sum, {
      id: 'effective_cal_sum',
      cell: info => info.getValue(),
      header: () => 'effective_cal_sum',
    }),
  
  ]

  export const combined_df_columns_xts = [
    columnHelper.accessor(row => row.system_tag, {
      id: 'system_tag',
      cell: info => info.getValue(),
      header: () => 'system_tag',
    }),
    columnHelper.accessor(row => row.order_fill_lag, {
      id: 'order_fill_lag',
      cell: info => info.getValue(),
      header: () => 'order_fill_lag',
    }),
    columnHelper.accessor(row => row.signal_lag, {
      id: 'signal_lag',
      cell: info => info.getValue(),
      header: () => 'signal_lag',
    }),
  
  
    columnHelper.accessor(row => row.place_order_lag, {
      id: 'place_order_lag',
      cell: info => info.getValue(),
      header: () => 'place_order_lag'
    }),
    columnHelper.accessor(row => row.TradingSymbol, {
      id: 'TradingSymbol',
      cell: info => info.getValue(),
      header: () => 'TradingSymbol'
    }),
    columnHelper.accessor(row => row.timestamp, {
      id: 'timestamp',
      cell: info => info.getValue(),
      header: () => 'timestamp'
    }),
    columnHelper.accessor(row => row.system_timestamp, {
      id: 'system_timestamp',
      cell: info => info.getValue(),
      header: () => 'system_timestamp'
    }),
    columnHelper.accessor(row => row.uid, {
      id: 'uid',
      cell: info => info.getValue(),
      header: () => 'uid'
    }),
    columnHelper.accessor(row => row.action, {
      id: 'action',
      cell: info => info.getValue(),
      header: () => 'action'
    }),
    columnHelper.accessor(row => row.qty, {
      id: 'qty',
      cell: info => info.getValue(),
      header: () => 'qty'
    }),
    columnHelper.accessor(row => row.price, {
      id: 'price',
      cell: info => info.getValue(),
      header: () => 'price'
    }),
    columnHelper.accessor(row => row.value, {
      id: 'value',
      cell: info => info.getValue(),
      header: () => 'value'
    }),
    columnHelper.accessor(row => row.note, {
      id: 'note',
      cell: info => info.getValue(),
      header: () => 'note'
    }),
    columnHelper.accessor(row => row.basket, {
      id: 'basket',
      cell: info => info.getValue(),
      header: () => 'basket'
    }),
    columnHelper.accessor(row => row.effective_qty, {
      id: 'effective_qty',
      cell: info => info.getValue(),
      header: () => 'effective_qty'
    }),
    columnHelper.accessor(row => row.AppOrderID, {
      id: 'AppOrderID',
      cell: info => info.getValue(),
      header: () => 'AppOrderID'
    }),
    columnHelper.accessor(row => row.ExchangeSegment, {
      id: 'ExchangeSegment',
      cell: info => info.getValue(),
      header: () => 'ExchangeSegment'
    }),
    columnHelper.accessor(row => row.OrderType, {
      id: 'OrderType',
      cell: info => info.getValue(),
      header: () => 'OrderType'
    }),
    columnHelper.accessor(row => row.ProductType, {
      id: 'ProductType',
      cell: info => info.getValue(),
      header: () => 'ProductType'
    }),
    columnHelper.accessor(row => row.OrderQuantity, {
      id: 'OrderQuantity',
      cell: info => info.getValue(),
      header: () => 'OrderQuantity'
    }),
    columnHelper.accessor(row => row.OrderStatus, {
      id: 'OrderStatus',
      cell: info => info.getValue(),
      header: () => 'OrderStatus'
    }),
    columnHelper.accessor(row => row.OrderAverageTradedPrice, {
      id: 'OrderAverageTradedPrice',
      cell: info => info.getValue(),
      header: () => 'OrderAverageTradedPrice'
    }),
    columnHelper.accessor(row => row.OrderGeneratedDateTime, {
      id: 'OrderGeneratedDateTime',
      cell: info => info.getValue(),
      header: () => 'OrderGeneratedDateTime'
    }),
    columnHelper.accessor(row => row.ExchangeTransactTime, {
      id: 'ExchangeTransactTime',
      cell: info => info.getValue(),
      header: () => 'ExchangeTransactTime'
    }),
    columnHelper.accessor(row => row.OrderUniqueIdentifier, {
      id: 'OrderUniqueIdentifier',
      cell: info => info.getValue(),
      header: () => 'OrderUniqueIdentifier'
    }),
  ]

  export const rms_df_columns = [
    columnHelper.accessor(row => row.symbol, {
      id: 'Symbol',
      cell: info => info.getValue(),
      header: () => 'Symbol',
    }),
    columnHelper.accessor(row => row.ltp, {
      id: 'Ltp',
      cell: info => {
        const value = info.getValue();
        return value !== undefined ? value.toFixed(2) : 'N/A';
      },
      header: () => 'Ltp',
    }),
    columnHelper.accessor(row => row.pnl, {
      id: 'pnl',
      cell: info => info.getValue().toFixed(2),
      header: () => 'PnL',
    }),
    columnHelper.accessor(row => row.buy_qty, {
      id: 'buy_qty',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Buy Qty',
    }),
    columnHelper.accessor(row => row.buy_price, {
      id: 'buy_price',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Buy Price',
    }),
    columnHelper.accessor(row => row.buy_value, {
      id: 'buy_value',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Buy Value',
    }),
    columnHelper.accessor(row => row.net_price, {
      id: 'net_price',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Net Price',
    }),
    columnHelper.accessor(row => row.net_value, {
      id: 'net_value',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Net Value',
    }),
    columnHelper.accessor(row => row.net_qty, {
      id: '  net_qty',
      cell: info => info.getValue().toFixed(2),
      header: () => ' Net Qty',
    }),
    columnHelper.accessor(row => row.sell_price, {
      id: 'sell_price',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Sell Price',
    }),
    columnHelper.accessor(row => row.sell_qty, {
      id: 'sell_qty',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Sell Qty',
    }),
    columnHelper.accessor(row => row.sell_value, {
      id: 'sell_value',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Sell Value',
    }),
    columnHelper.accessor(row => row.turnover, {
      id: 'turnover',
      cell: info => info.getValue().toFixed(2),
      header: () => 'Turnover',
    }),
  ]

  export const combined_order_zerodha = [
    columnHelper.accessor(row => row.status, {
      id: 'status',
      cell: info => info.getValue(),
      header: () => 'status',
    }),
    columnHelper.accessor(row => row.status_message, {
      id: 'status_message',
      cell: info => info.getValue(),
      header: () => 'status_message',
    }),
    columnHelper.accessor(row => row.status_message_raw, {
      id: 'status_message_raw',
      cell: info => info.getValue(),
      header: () => 'status_message_raw',
    }),
    columnHelper.accessor(row => row.order_timestamp, {
      id: 'order_timestamp',
      cell: info => info.getValue(),
      header: () => 'order_timestamp',
    }),
    columnHelper.accessor(row => row.exchange_update_timestamp, {
      id: 'exchange_update_timestamp',
      cell: info => info.getValue(),
      header: () => 'exchange_update_timestamp',
    }),
    columnHelper.accessor(row => row.exchange_timestamp, {
      id: 'exchange_timestamp',
      cell: info => info.getValue(),
      header: () => 'exchange_timestamp',
    }),
    columnHelper.accessor(row => row.variety, {
      id: 'variety',
      cell: info => info.getValue(),
      header: () => 'variety',
    }),
    columnHelper.accessor(row => row.modified, {
      id: 'modified',
      cell: info => info.getValue(),
      header: () => 'modified',
    }),
    columnHelper.accessor(row => row.exchange, {
      id: 'exchange',
      cell: info => info.getValue(),
      header: () => 'exchange',
    }),
    columnHelper.accessor(row => row.tradingsymbol, {
      id: 'tradingsymbol',
      cell: info => info.getValue(),
      header: () => 'tradingsymbol',
    }),
    columnHelper.accessor(row => row.order_type, {
      id: 'order_type',
      cell: info => info.getValue(),
      header: () => 'order_type',
    }),
    columnHelper.accessor(row => row.transaction_type, {
      id: 'transaction_type',
      cell: info => info.getValue(),
      header: () => 'transaction_type',
    }),
    columnHelper.accessor(row => row.validity, {
      id: 'validity',
      cell: info => info.getValue(),
      header: () => 'validity',
    }),
    columnHelper.accessor(row => row.validity_ttl, {
      id: 'validity_ttl',
      cell: info => info.getValue(),
      header: () => 'validity_ttl',
    }),
    columnHelper.accessor(row => row.product, {
      id: 'product',
      cell: info => info.getValue(),
      header: () => 'product',
    }),
    columnHelper.accessor(row => row.quantity, {
      id: 'quantity',
      cell: info => info.getValue(),
      header: () => 'quantity',
    }),
    columnHelper.accessor(row => row.disclosed_quantity, {
      id: 'disclosed_quantity',
      cell: info => info.getValue(),
      header: () => 'disclosed_quantity',
    }),
    columnHelper.accessor(row => row.price, {
      id: 'price',
      cell: info => info.getValue(),
      header: () => 'price',
    }),
    columnHelper.accessor(row => row.trigger_price, {
      id: 'trigger_price',
      cell: info => info.getValue(),
      header: () => 'trigger_price',
    }),
    columnHelper.accessor(row => row.average_price, {
      id: 'average_price',
      cell: info => info.getValue(),
      header: () => 'average_price',
    }),
    columnHelper.accessor(row => row.filled_quantity, {
      id: 'filled_quantity',
      cell: info => info.getValue(),
      header: () => 'filled_quantity',
    }),
    columnHelper.accessor(row => row.pending_quantity, {
      id: 'pending_quantity',
      cell: info => info.getValue(),
      header: () => 'pending_quantity',
    }),
    columnHelper.accessor(row => row.cancelled_quantity, {
      id: 'cancelled_quantity',
      cell: info => info.getValue(),
      header: () => 'cancelled_quantity',
    }),
    columnHelper.accessor(row => row.market_protection, {
      id: 'market_protection',
      cell: info => info.getValue(),
      header: () => 'market_protection',
    }),
    columnHelper.accessor(row => row.tag, {
      id: 'tag',
      cell: info => info.getValue(),
      header: () => 'tag',
    }),
    columnHelper.accessor(row => row.tags, {
      id: 'tags',
      cell: info => info.getValue(),
      header: () => 'tags',
    }),
    columnHelper.accessor(row => row.OrderQuantityDir, {
      id: 'OrderQuantityDir',
      cell: info => info.getValue(),
      header: () => 'OrderQuantityDir',
    }),
  
  
  ]
  export const combined_order_xts = [
    columnHelper.accessor(row => row.LoginID, {
      id: 'LoginID',
      cell: info => info.getValue(),
      header: () => 'LoginID',
    }),
    columnHelper.accessor(row => row.ClientID, {
      id: 'ClientID',
      cell: info => info.getValue(),
      header: () => 'ClientID',
    }),
    columnHelper.accessor(row => row.AppOrderID, {
      id: 'AppOrderID',
      cell: info => info.getValue(),
      header: () => 'AppOrderID',
    }),
    columnHelper.accessor(row => row.OrderReferenceID, {
      id: 'OrderReferenceID',
      cell: info => info.getValue(),
      header: () => 'OrderReferenceID',
    }),
    columnHelper.accessor(row => row.GeneratedBy, {
      id: 'GeneratedBy',
      cell: info => info.getValue(),
      header: () => 'GeneratedBy',
    }),
    columnHelper.accessor(row => row.ExchangeOrderID, {
      id: 'ExchangeOrderID',
      cell: info => info.getValue(),
      header: () => 'ExchangeOrderID',
    }),
    columnHelper.accessor(row => row.OrderCategoryType, {
      id: 'OrderCategoryType',
      cell: info => info.getValue(),
      header: () => 'OrderCategoryType',
    }),
    columnHelper.accessor(row => row.ExchangeSegment, {
      id: 'ExchangeSegment',
      cell: info => info.getValue(),
      header: () => 'ExchangeSegment',
    }),
    columnHelper.accessor(row => row.OrderSide, {
      id: 'OrderSide',
      cell: info => info.getValue(),
      header: () => 'OrderSide',
    }),
    columnHelper.accessor(row => row.OrderType, {
      id: 'OrderType',
      cell: info => info.getValue(),
      header: () => 'OrderType',
    }),
    columnHelper.accessor(row => row.ProductType, {
      id: 'ProductType',
      cell: info => info.getValue(),
      header: () => 'ProductType',
    }),
    columnHelper.accessor(row => row.TimeInForce, {
      id: 'TimeInForce',
      cell: info => info.getValue(),
      header: () => 'TimeInForce',
    }),
    columnHelper.accessor(row => row.OrderPrice, {
      id: 'OrderPrice',
      cell: info => info.getValue(),
      header: () => 'OrderPrice',
    }),
    columnHelper.accessor(row => row.OrderQuantity, {
      id: 'OrderQuantity',
      cell: info => info.getValue(),
      header: () => 'OrderQuantity',
    }),
    columnHelper.accessor(row => row.OrderStopPrice, {
      id: 'OrderStopPrice',
      cell: info => info.getValue(),
      header: () => 'OrderStopPrice',
    }),
    columnHelper.accessor(row => row.OrderStatus, {
      id: 'OrderStatus',
      cell: info => info.getValue(),
      header: () => 'OrderStatus',
    }),
    columnHelper.accessor(row => row.OrderAverageTradedPrice, {
      id: 'OrderAverageTradedPrice',
      cell: info => info.getValue(),
      header: () => 'OrderAverageTradedPrice',
    }),
    columnHelper.accessor(row => row.LeavesQuantity, {
      id: 'LeavesQuantity',
      cell: info => info.getValue(),
      header: () => 'LeavesQuantity',
    }),
    columnHelper.accessor(row => row.CumulativeQuantity, {
      id: 'CumulativeQuantity',
      cell: info => info.getValue(),
      header: () => 'CumulativeQuantity',
    }),
    columnHelper.accessor(row => row.OrderDisclosedQuantity, {
      id: 'OrderDisclosedQuantity',
      cell: info => info.getValue(),
      header: () => 'OrderDisclosedQuantity',
    }),
    columnHelper.accessor(row => row.OrderGeneratedDateTime, {
      id: 'OrderGeneratedDateTime',
      cell: info => info.getValue(),
      header: () => 'OrderGeneratedDateTime',
    }),
    columnHelper.accessor(row => row.ExchangeTransactTime, {
      id: 'ExchangeTransactTime',
      cell: info => info.getValue(),
      header: () => 'ExchangeTransactTime',
    }),
    columnHelper.accessor(row => row.TradingSymbol, {
      id: 'TradingSymbol',
      cell: info => info.getValue(),
      header: () => 'TradingSymbol',
    }),
    columnHelper.accessor(row => row.LastUpdateDateTime, {
      id: 'LastUpdateDateTime',
      cell: info => info.getValue(),
      header: () => 'LastUpdateDateTime',
    }),
    columnHelper.accessor(row => row.OrderExpiryDate, {
      id: 'OrderExpiryDate',
      cell: info => info.getValue(),
      header: () => 'OrderExpiryDate',
    }),
    columnHelper.accessor(row => row.CancelRejectReason, {
      id: 'CancelRejectReason',
      cell: info => info.getValue(),
      header: () => 'CancelRejectReason',
    }),
    columnHelper.accessor(row => row.OrderUniqueIdentifier, {
      id: 'OrderUniqueIdentifier',
      cell: info => info.getValue(),
      header: () => 'OrderUniqueIdentifier',
    }),
    columnHelper.accessor(row => row.OrderLegStatus, {
      id: 'OrderLegStatus',
      cell: info => info.getValue(),
      header: () => 'OrderLegStatus',
    }),
    columnHelper.accessor(row => row.BoLegDetails, {
      id: 'BoLegDetails',
      cell: info => info.getValue(),
      header: () => 'BoLegDetails',
    }),
    columnHelper.accessor(row => row.IsSpread, {
      id: 'IsSpread',
      cell: info => info.getValue(),
      header: () => 'IsSpread',
    }),
    columnHelper.accessor(row => row.BoEntryOrderId, {
      id: 'BoEntryOrderId',
      cell: info => info.getValue(),
      header: () => 'BoEntryOrderId',
    }),
    columnHelper.accessor(row => row.ApiOrderSource, {
      id: 'ApiOrderSource',
      cell: info => info.getValue(),
      header: () => 'ApiOrderSource',
    }),
    columnHelper.accessor(row => row.MessageCode, {
      id: 'MessageCode',
      cell: info => info.getValue(),
      header: () => 'MessageCode',
    }),
    columnHelper.accessor(row => row.MessageVersion, {
      id: 'MessageVersion',
      cell: info => info.getValue(),
      header: () => 'MessageVersion',
    }),
    columnHelper.accessor(row => row.TokenID, {
      id: 'TokenID',
      cell: info => info.getValue(),
      header: () => 'TokenID',
    }),
    columnHelper.accessor(row => row.ApplicationType, {
      id: 'ApplicationType',
      cell: info => info.getValue(),
      header: () => 'ApplicationType',
    }),
    columnHelper.accessor(row => row.SequenceNumber, {
      id: 'SequenceNumber',
      cell: info => info.getValue(),
      header: () => 'SequenceNumber',
    }),
    columnHelper.accessor(row => row.trade_ids, {
      id: 'trade_ids',
      cell: info => info.getValue(),
      header: () => 'trade_ids',
    }),
    columnHelper.accessor(row => row.OrderQuantityDir, {
      id: 'OrderQuantityDir',
      cell: info => info.getValue(),
      header: () => 'OrderQuantityDir',
    }),
  
  ]

  
  export const combined_trades_zerodha = [
    columnHelper.accessor(row => row.trade_id, {
      id: 'trade_id',
      cell: info => info.getValue(),
      header: () => 'trade_id',
    }),
    columnHelper.accessor(row => row.uid, {
      id: 'uid',
      cell: info => info.getValue(),
      header: () => 'uid',
    }),
    columnHelper.accessor(row => row.timestamp, {
      id: 'timestamp',
      cell: info => info.getValue(),
      header: () => 'timestamp',
    }),
    columnHelper.accessor(row => row.action, {
      id: 'action',
      cell: info => info.getValue(),
      header: () => 'action',
    }),
    columnHelper.accessor(row => row.action_int, {
      id: 'action_int',
      cell: info => info.getValue(),
      header: () => 'action_int',
    }),
    columnHelper.accessor(row => row.symbol, {
      id: 'symbol',
      cell: info => info.getValue(),
      header: () => 'symbol',
    }),
    columnHelper.accessor(row => row.price, {
      id: 'price',
      cell: info => info.getValue(),
      header: () => 'price',
    }),
    columnHelper.accessor(row => row.price_provided, {
      id: 'price_provided',
      cell: info => info.getValue(),
      header: () => 'price_provided',
    }),
    columnHelper.accessor(row => row.buy_value, {
      id: 'buy_value',
      cell: info => info.getValue(),
      header: () => 'buy_value',
    }),
    columnHelper.accessor(row => row.sell_value, {
      id: 'sell_value',
      cell: info => info.getValue(),
      header: () => 'sell_value',
    }),
    columnHelper.accessor(row => row.system_timestamp, {
      id: 'system_timestamp',
      cell: info => info.getValue(),
      header: () => 'system_timestamp',
    }),
    columnHelper.accessor(row => row.note, {
      id: 'note',
      cell: info => info.getValue(),
      header: () => 'note',
    }),
    columnHelper.accessor(row => row.quantity, {
      id: 'quantity',
      cell: info => info.getValue(),
      header: () => 'quantity',
    }),
    columnHelper.accessor(row => row.qty, {
      id: 'qty',
      cell: info => info.getValue(),
      header: () => 'qty',
    }),
    columnHelper.accessor(row => row.qty_dir, {
      id: 'qty_dir',
      cell: info => info.getValue(),
      header: () => 'qty_dir',
    }),
    columnHelper.accessor(row => row.value, {
      id: 'value',
      cell: info => info.getValue(),
      header: () => 'value',
    }),
    columnHelper.accessor(row => row.signal_number, {
      id: 'signal_number',
      cell: info => info.getValue(),
      header: () => 'signal_number',
    }),
    columnHelper.accessor(row => row.basket, {
      id: 'basket',
      cell: info => info.getValue(),
      header: () => 'basket',
    }),
    columnHelper.accessor(row => row.qty_multiplier, {
      id: 'qty_multiplier',
      cell: info => info.getValue(),
      header: () => 'qty_multiplier',
    }),
    columnHelper.accessor(row => row.effective_qty, {
      id: 'effective_qty',
      cell: info => info.getValue(),
      header: () => 'effective_qty',
    }),
  
  ]
  
  export const curr_strategy_mtm = [
    columnHelper.accessor(row => row.UID, {
      id: 'UID',
      cell: info => info.getValue(),
      header: () => 'UID',
    }),
    columnHelper.accessor(row => row.MTM, {
      id: 'MTM',
      cell: info => info.getValue(),
      header: () => 'MTM',
    }),
  ]
  export const curr_basket_mtm = [
    columnHelper.accessor(row => row.basket, {
      id: 'Basket',
      cell: info => info.getValue(),
      header: () => 'Basket',
    }),
    columnHelper.accessor(row => row.MTM, {
      id: 'MTM',
      cell: info => info.getValue(),
      header: () => 'MTM',
    }),
  ]
  export const combined_trades_xts = [
    columnHelper.accessor(row => row.trade_id, {
      id: 'trade_id',
      cell: info => info.getValue(),
      header: () => 'trade_id',
    }),
    columnHelper.accessor(row => row.uid, {
      id: 'uid',
      cell: info => info.getValue(),
      header: () => 'uid',
    }),
    columnHelper.accessor(row => row.timestamp, {
      id: 'timestamp',
      cell: info => info.getValue(),
      header: () => 'timestamp',
    }),
    columnHelper.accessor(row => row.action, {
      id: 'action',
      cell: info => info.getValue(),
      header: () => 'action',
    }),
    columnHelper.accessor(row => row.action_int, {
      id: 'action_int',
      cell: info => info.getValue(),
      header: () => 'action_int',
    }),
    columnHelper.accessor(row => row.qty, {
      id: 'qty',
      cell: info => info.getValue(),
      header: () => 'qty',
    }),
    columnHelper.accessor(row => row.qty_dir, {
      id: 'qty_dir',
      cell: info => info.getValue(),
      header: () => 'qty_dir',
    }),
    columnHelper.accessor(row => row.symbol, {
      id: 'symbol',
      cell: info => info.getValue(),
      header: () => 'symbol',
    }),
    columnHelper.accessor(row => row.price, {
      id: 'price',
      cell: info => info.getValue(),
      header: () => 'price',
    }),
    columnHelper.accessor(row => row.price_provided, {
      id: 'price_provided',
      cell: info => info.getValue(),
      header: () => 'price_provided',
    }),
    columnHelper.accessor(row => row.value, {
      id: 'value',
      cell: info => info.getValue(),
      header: () => 'value',
    }),
    columnHelper.accessor(row => row.buy_value, {
      id: 'buy_value',
      cell: info => info.getValue(),
      header: () => 'buy_value',
    }),
    columnHelper.accessor(row => row.sell_value, {
      id: 'sell_value',
      cell: info => info.getValue(),
      header: () => 'sell_value',
    }),
    columnHelper.accessor(row => row.system_timestamp, {
      id: 'system_timestamp',
      cell: info => info.getValue(),
      header: () => 'system_timestamp',
    }),
    columnHelper.accessor(row => row.note, {
      id: 'note',
      cell: info => info.getValue(),
      header: () => 'note',
    }),
    // columnHelper.accessor(row => row.quantity, {
    //   id: 'quantity',
    //   cell: info => info.getValue(),
    //   header: () => 'quantity',
    // }),
    columnHelper.accessor(row => row.basket, {
      id: 'basket',
      cell: info => info.getValue(),
      header: () => 'basket',
    }),
    columnHelper.accessor(row => row.qty_multiplier, {
      id: 'qty_multiplier',
      cell: info => info.getValue(),
      header: () => 'qty_multiplier',
    }),
    columnHelper.accessor(row => row.effective_qty, {
      id: 'effective_qty',
      cell: info => info.getValue(),
      header: () => 'effective_qty',
    }),
  ]