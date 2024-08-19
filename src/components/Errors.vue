<script setup>


import { onMounted, onUnmounted } from 'vue'
import BarChart from './Barchart.vue';
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
} from '@tanstack/vue-table'

import { MyEnum } from '../Enums/Prefix.js';
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue';
import NavBar from './NavBar.vue';
import MultiLineChart from './HighCharts.vue'

import LightWeightChart from './LightWeightChart.vue';


const route = useRoute();
const user_data = ref('')
const name = ref('');



const columnHelper = createColumnHelper()

const columns = [



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
    columnHelper.accessor(row => row.OrderQuantity, {
        id: 'OrderQuantity',
        cell: info => info.getValue(),
        header: () => 'OrderQuantity',
    }),
    columnHelper.accessor(row => row.OrderSide, {
        id: 'OrderSide',
        cell: info => info.getValue(),
        header: () => 'OrderSide',
    }),
    columnHelper.accessor(row => row.order_id, {
        id: 'order_id',
        cell: info => info.getValue(),
        header: () => 'order_id',
    }),
    columnHelper.accessor(row => row.message, {
        id: 'message',
        cell: info => info.getValue(),
        header: () => 'Message',
    }),
    columnHelper.accessor(row => row.time, {
        id: 'Time',
        cell: info => info.getValue(),
        header: () => 'Time',
    }),


]

let eventSource = null
const client_latency = ref(0)
const past_time_client = ref(0)
const max_client_latency = ref(0)


const book = ref([])
const handleColumnClick = ({ item, index }) => {
    showOnPage.value = item;
}

const handleMessage = (message) => {
    try {
        if (message === undefined) return;
        book.value = message['Order_Errors']['PAPER TRADING 2']
    } catch (error) {
        console.error('Error parsing event data or updating data:', error);
    }
}

const connectToSSE = () => {
    const socket = new WebSocket('wss://api.swancapital.in/errors');

    socket.onmessage = (event) => {
        if (event.data === 'ping') {
            socket.send('pong')
        } else {
            const message = JSON.parse(event.data);
            let ar2 = message["time"];
            if (past_time_client.value === 0) past_time_client.value = ar2;
            if (past_time_client.value != 0) {
                let date1 = new Date(past_time_client.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
                let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
                let diffInMs = date2 - date1;
                let diffInSeconds = diffInMs / 1000;
                client_latency.value = diffInSeconds;
                max_client_latency.value = Math.max(max_client_latency.value, client_latency.value)
                past_time_client.value = ar2;
            }


            handleMessage(message)
        }
    }
    socket.onclose = (event) => {
        console.log('WebSocket connection closed:', event.reason)
    }

    socket.onopen = () => {
        console.log('WebSocket connection opened')
    }
    socket.onerror = (error) => {
        console.error('WebSocket error:', error)
    }
};







const showOnPage = ref('Orders')

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

<template>

    <div class="px-8 py-8 pageContainer">






        <!--  <BarChart v-if="user_data['Live_Client_Positions']" :chartData='user_data["Live_Client_Positions"]' /> -->
        <div class="LatencyTable">
            <p> Client Latency :<span class="latencyvalue">{{ client_latency }}</span></p>
            <p> Max Client :<span class="latencyvalue">{{ max_client_latency }}</span></p>
        </div>

        <div class="navContainer">
            <NavBar :navColumns="['Orders']" @column-clicked="handleColumnClick" />
        </div>

        <div class="my-8" v-if="book && showOnPage === 'Orders'">
            <p class="table-heading">{{ showOnPage }}</p>
            <TanStackTestTable :data="book" :columns="columns" :hasColor="[]" :navigateTo="[]" :showPagination=true />
        </div>


        <!-- 

        <div class="my-8" v-if="book && showOnPage === 'TradeBook'">
            <p class="table-heading">Complete Trade Book</p>
            <TanStackTestTable :data="book" :columns="live_trade_book_columns" :hasColor="[]" :navigateTo="[]"
                :showPagination=true />
        </div>


        <div class="my-8" v-if="showOnPage === 'Order'">
            <p class="table-heading">Complete Order Book</p>
            <TanStackTestTable :data="book" :columns="live_order_book_columns" :hasColor="[]" :navigateTo="[]"
                :showPagination=true />
        </div>


        <div class="my-8" v-if="showOnPage === 'Combined DF'">
            <p class="table-heading">Combined DF</p>
            <TanStackTestTable :data="book" :columns="combined_df_columns" :hasColor="[]" :navigateTo="[]"
                :showPagination=true />
        </div> -->

    </div>


</template>

<style scoped>
.pageContainer {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.latencyvalue {
    font-weight: bold;
}

.navContainer {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
}

.LatencyTable {
    display: flex;
    width: 100;
    align-items: flex-end;
    justify-content: flex-end;
    padding: 20px;
    flex-direction: column;
}

.table-heading {
    font-size: 22px;
    font-weight: 600;
    margin-left: 30px;
}

.profitContainer {
    border: 1px solid black;
    height: auto;
    padding: 20px;

    width: fit-content;
    border-radius: 10px;
    display: flex;
    font-size: 30px;
    align-items: flex-start;
    flex-direction: column;

}

.priceContainer {
    display: flex;
    align-items: baseline;
    gap: 20px;
}

html {
    /* font-family: poppins; */
    font-size: 14px;
}

.labeltag {
    font-size: 20px;
}

.headingContainer {
    font-size: 30px;
    font-weight: bold;

}
</style>