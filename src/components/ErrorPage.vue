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
import EditButton from './EditButton.vue';

const route = useRoute();
const user_data = ref('')
const name = ref('');



const columnHelper = createColumnHelper()

const columns = [


    columnHelper.accessor(row => row.message, {
        id: 'message',
        cell: info => info.getValue(),
        header: () => 'Message',
    }),
    columnHelper.accessor(row => row.IdealMTM, {
        id: 'IdealMTM',
        cell: info => info.getValue(),
        header: () => 'Ideal MTM',
    }),


]

let eventSource = null
const client_BackendData = ref([])
const connection_BackendData = ref([])
const date = ref()
const data = ref([])
const user_infected = ref([])
const client_latency = ref(0)
const client_details_Latency = ref(0)
const past_time_client = ref(0)
const past_time_clientDetails = ref(0)
const max_client_details_latency = ref(0)
const max_client_latency = ref(0)
const mix_real_ideal_mtm_table = ref({})

const book = ref([])
const handleColumnClick = ({ item, index }) => {
    showOnPage.value = item;
}

const handleMessage = (message) => {
    try {
        if (message.client_data === undefined) return;
        client_BackendData.value = message.client_data

        let result = client_BackendData.value.find(client => client.name === name.value);
        if (result) {
            user_data.value = result;
            data.value = [{
                AccountName: result.name || '',
                IdealMTM: result.ideal_MTM !== undefined ? Number(result.ideal_MTM) : 0,
                Day_PL: result.MTM !== undefined ? Number(result.MTM) : 0,
                Friction: result.MTM !== undefined && result.ideal_MTM !== undefined
                    ? (Number(result.MTM) - Number(result.ideal_MTM)).toFixed(2)
                    : '0.00',
                RejectedOrderCount: result.Rejected_orders !== undefined ? Number(result.Rejected_orders) : 0,
                PendingOrderCount: result.Pending_orders !== undefined ? Number(result.Pending_orders) : 0,
                OpenQuantity: result.OpenQuantity !== undefined ? Number(result.OpenQuantity) : 0,
                NetQuantity: result.NetQuantity !== undefined ? Number(result.NetQuantity) : 0,
                Ideal_Margin: result.Live_Client_Margin !== undefined ? Number(result.Live_Client_Margin) : 0,
                VAR: result.Live_Client_Var !== undefined ? Number(result.Live_Client_Var) : 0,
                Cash: result.cashAvailable !== undefined ? Number(result.cashAvailable) : 0,
                AvailableMargin: result.availableMargin !== undefined ? Number(result.availableMargin) : 0,
                Used_Margin: result.marginUtilized !== undefined ? Number(result.marginUtilized) : 0,
                VAR_PERCENTAGE: result.Live_Client_Var !== undefined && (result.availableMargin > 0) ? ((Number(result.Live_Client_Var) / Number(result.availableMargin)) * 100).toPrecision(4) : 0,
            }];
            mix_real_ideal_mtm_table.value = { "real": result['MTMTable'], "ideal": result['ideal_MTMTable'] }

        } else {
            console.error('No client data found for the specified name:', name.value);
        }
    } catch (error) {
        console.error('Error parsing event data or updating data:', error);
    }
}

const connectToSSE = () => {
    const socket = new WebSocket('wss://api.swancapital.in/ws');

    socket.onmessage = (event) => {
        if (event.data === 'ping') {
            socket.send('pong')
        } else {
            const message = JSON.parse(event.data)
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







const showOnPage = ref('Positions')

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
            <p> Client Detail Latency: <span class="latencyvalue">{{ client_details_Latency }}</span></p>
            <p> Max Client Detail Latency :<span class="latencyvalue"> {{ max_client_details_latency }}</span></p>
        </div>

        <div class="navContainer">
            <NavBar :navColumns="['Positions', 'Order', 'Holdings', 'TradeBook', 'Combined DF']"
                @column-clicked="handleColumnClick" />
        </div>

        <div class="my-8" v-if="book && showOnPage === 'Positions'">
            <p class="table-heading">Live Positions</p>
            <TanStackTestTable :data="book" :columns="rms_df_columns" :hasColor="['pnl']" :navigateTo="[]"
                :showPagination=true />
        </div>




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
        </div>

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