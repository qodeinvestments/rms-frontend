<template>

</template>

<script setup>


import { onMounted, onUnmounted } from 'vue'
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
} from '@tanstack/vue-table'
import { ref } from 'vue'
import { useRoute } from 'vue-router';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue';

import MultiLineChart from './HighCharts.vue'



const route = useRoute();
const user_data = ref('')

const defaultData = [{
    "id": 1,
    "AccountName": "Abhinav",
    "IdealMTM": 0,
    "Day_PL": "25000",
    'Friction': 0,
    'OpenQuantity': 0,
    'NetQuantity': 0,
    "PortfolioValue": "250000",
    "PositionDayPL": "25000000000",
    "HoldingsDayPL": 250000,
    "TotalOrderCount": 250000,
    "OpenOrderCount": 40,
    "CompleteOrderCount": 10,
    "PositionsCount": 20,
    "HoldingsCount": 10,
    "Used_Margin": 50000,
    "AvailableMargin": 250000,
    "Cash": 2500000
}];
const columnHelper = createColumnHelper()
const live_trade_book_columns = [
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
    columnHelper.accessor(row => row.ExchangeInstrumentID, {
        id: 'ExchangeInstrumentID',
        cell: info => info.getValue(),
        header: () => 'ExchangeInstrumentID',
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
    columnHelper.accessor(row => row.LeavesQuantity, {
        id: 'LeavesQuantity',
        cell: info => info.getValue(),
        header: () => 'LeavesQuantity',
    }),
    columnHelper.accessor(row => row.OrderQuantity, {
        id: 'OrderQuantity',
        cell: info => info.getValue(),
        header: () => 'OrderQuantity',
    }),



]
const columns = [
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
    columnHelper.accessor(row => row.Friction, {
        id: 'Friction',
        cell: info => info.getValue(),
        header: () => 'Friction',
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
    columnHelper.accessor(row => row.OpenOrderCount, {
        id: 'OpenOrderCount',
        cell: info => info.getValue(),
        header: () => 'OpenOrderCount',
    }),
    columnHelper.accessor(row => row.CompleteOrderCount, {
        id: 'CompleteOrderCount',
        cell: info => info.getValue(),
        header: () => 'CompleteOrderCount',
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
    columnHelper.accessor(row => row.Cash, {
        id: 'Cash',
        cell: info => info.getValue(),
        header: () => 'Cash',
    }),
]




const messages = ref([])


let eventSource = null


const date = ref()
const data = ref([])

const client_live_trade_book = ref([])

const connectToSSE = () => {
    eventSource = new EventSource('http://localhost:5000/stream')


    eventSource.onmessage = (event) => {

        let c_d = JSON.parse(event.data);
        let response = JSON.parse(c_d)
        let result = response.client_data.find(client => client.name === name.value);


        user_data.value = result;

        data.value = [{
            AccountName: result.name,
            IdealMTM: Number(result.ideal_MTM),
            Day_PL: Number(result.MTM),
            Friction: (Number(result.MTM) - Number(result.ideal_MTM)).toFixed(2),
            OpenQuantity: Number(result.OpenQuantity),
            NetQuantity: Number(result.NetQuantity),
            RejectedOrderCount: Number(result.Rejected_orders),
            PendingOrderCount: Number(result.Pending_orders)

        }]
        let tradeArray = Object.values(result.Live_Trade_Book);
        let prev = client_live_trade_book.value.length
        if (prev < tradeArray.length)
            client_live_trade_book.value = tradeArray;


    }

    eventSource.onopen = () => {
        messages.value.push('Connection opened')
    }
    eventSource.onerror = () => {
        messages.value.push('Error occurred')
        eventSource.close()
    }
}

const name = ref('');

onMounted(() => {
    connectToSSE();
    name.value = route.params.username;
})

onUnmounted(() => {
    if (eventSource) {
        eventSource.close()
    }
})




</script>


<style></style>