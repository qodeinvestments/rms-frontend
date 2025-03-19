
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
    columnHelper.accessor(row => row.AccountId, {
      id: 'AccountId',
      cell: info => info.getValue(),
      header: () => 'AccountId',
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
    columnHelper.accessor(row => row.API_DAY_PNL, {
      id: 'API DAY PNL',
      cell: info => info.getValue(),
      header: () => 'API DAY PNL',
    }),
    columnHelper.accessor(row => row.API_NET_PNL, {
      id: 'API NET PNL',
      cell: info => info.getValue(),
      header: () => 'API NET PNL',
    }),

    columnHelper.accessor(row => row.HoldingPnl, {
      id: 'HoldingsDayPL',
      cell: info => info.getValue(),
      header: () => 'HoldingsDayPL',
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
    columnHelper.accessor(row=> row.SlippagePer,{

        id: 'SlippagePer',
        cell: info => {
          const value = info.getValue(); // Get the value
          return (typeof value === 'number' ? value : Number(value)).toFixed(2) + "%"; // Ensure it's a number and format
        },
        header: () => 'Slippage %',
    }
    ),
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
    columnHelper.accessor(row => row.Portfolio_Value, {
      id: 'Portfolio Value',
      cell: info => info.getValue(),
      header: () => 'Portfolio Value',
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
    columnHelper.accessor(row => row.IdealTurnover, {
      id: 'IdealTurnover',
      cell: info => info.getValue(),
      header: () => 'Ideal Turnover',
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
    columnHelper.accessor(row => row.Cashperpf, {
      id: 'Cash/pf',
      cell: info => info.getValue(),
      header: () => 'Cash/PF',
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