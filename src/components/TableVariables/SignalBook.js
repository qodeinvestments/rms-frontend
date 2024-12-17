import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
  } from '@tanstack/vue-table'

const columnHelper = createColumnHelper()
  


export const columns = [
    columnHelper.accessor(row => row.trade_id, {
        id: 'trade_id',
        cell: info => info.getValue(),
        header: () => 'trade_id'
    }),
    columnHelper.accessor(row => row.uid, {
        id: 'uid',
        cell: info => info.getValue(),
        header: () => 'uid'
    }),
    columnHelper.accessor(row => row.time_diff, {
        id: 'time_diff',
        cell: info => info.getValue(),
        header: () => 'time_diff'
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

    columnHelper.accessor(row => row.action, {
        id: 'action',
        cell: info => info.getValue(),
        header: () => 'action'
    }),
    columnHelper.accessor(row => row.action_int, {
        id: 'action_int',
        cell: info => info.getValue(),
        header: () => 'action_int'
    }),
    columnHelper.accessor(row => row.qty, {
        id: 'qty',
        cell: info => info.getValue(),
        header: () => 'qty'
    }),
    columnHelper.accessor(row => row.qty_dir, {
        id: 'qty_dir',
        cell: info => info.getValue(),
        header: () => 'qty_dir'
    }),
    columnHelper.accessor(row => row.symbol, {
        id: 'symbol',
        cell: info => info.getValue(),
        header: () => 'symbol'
    }),
    columnHelper.accessor(row => row.price, {
        id: 'price',
        cell: info => info.getValue(),
        header: () => 'price'
    }),
    columnHelper.accessor(row => row.price_provided, {
        id: 'price_provided',
        cell: info => info.getValue(),
        header: () => 'price_provided'
    }),
    columnHelper.accessor(row => row.value, {
        id: 'value',
        cell: info => info.getValue(),
        header: () => 'value'
    }),
    columnHelper.accessor(row => row.buy_value, {
        id: 'buy_value',
        cell: info => info.getValue(),
        header: () => 'buy_value'
    }),
    columnHelper.accessor(row => row.sell_value, {
        id: 'sell_value',
        cell: info => info.getValue(),
        header: () => 'sell_value'
    }),

    columnHelper.accessor(row => row.note, {
        id: 'note',
        cell: info => info.getValue(),
        header: () => 'note'
    }),
    columnHelper.accessor(row => row.quantity, {
        id: 'quantity',
        cell: info => info.getValue(),
        header: () => 'quantity'
    }),
]