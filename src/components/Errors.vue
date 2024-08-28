<script setup>


import { onMounted, onUnmounted } from 'vue'
import BarChart from './Barchart.vue';
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
} from '@tanstack/vue-table'
import { inject } from 'vue'
import { MyEnum } from '../Enums/Prefix.js';
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue';
import NavBar from './NavBar.vue';
import MultiLineChart from './HighCharts.vue'

import LightWeightChart from './LightWeightChart.vue';
import EditButton from './EditButton.vue';


const route = useRoute();
const user_data = ref('')
const name = ref('');
const triggerToast = inject('triggerToast')
const data = inject('book')

const columnHelper = createColumnHelper()
const columns_testing = [
    columnHelper.accessor(row => row.time, {
        id: 'Time',
        cell: info => info.getValue(),
        header: () => 'Time',
    }),
    columnHelper.accessor(row => row.message, {
        id: 'message',
        cell: info => info.getValue(),
        header: () => 'message',
    }),

]

const live_order_book_columns = [
    columnHelper.accessor(row => row.user, {
        id: 'User',
        cell: info => info.getValue(),
        header: () => 'User',
    }),

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

    // columnHelper.accessor(row => row.edit, {
    //     id: 'edit',
    //     cell: info => h(EditButton, { id: info.row.original.id }),
    //     header: () => ' ',
    //     enableSorting: false,
    // })


]

const colorColumns = ref([])
const parseCustomDate = (dateString) => {
    let [datePart, timePart] = dateString.split(' ');
    let [day, month, year] = datePart.split('-');
    // No need to parse time if we only care about the date
    return new Date(year, month - 1, day);  // Create a Date object only with year, month, and day
}

const tell_time_match = (a1, a2) => {
    let date1 = parseCustomDate(a1);
    let date2 = parseCustomDate(a2);
    let sameDate = date1.getTime() === date2.getTime();  // Compare the time value (in ms) of the date objects

    return sameDate;
}

const updateColorColumns = (data, time) => {
    const revmap = {
        'my_program_shut_down': 'Testing',
        'trader_xts_shut_down': 'XTS_Trader',
        'trader_zerodha_shut_down': 'Zerodha_Trader',
        'websocket_shut_down': 'Web_Sockets',
        'shut_down_pulse_run_strats': 'Run_Strats',
        'shut_down_pulse_check_net_positions': 'PosMis Generator'
    }
    const newColorColumns = []

    // Check Order_Errors
    let orderErrorsMatch = false
    for (const key in data['Order_Errors']) {
        for (const order of data['Order_Errors'][key]) {
            if (tell_time_match(order['OrderGeneratedDateTime'], time)) {
                orderErrorsMatch = true
                break
            }
        }
        if (orderErrorsMatch) break
    }
    if (orderErrorsMatch) newColorColumns.push('Order_Errors')

    // Check Pulse_Errors
    for (const key in data['Pulse_Errors']) {
        const pulseErrors = data['Pulse_Errors'][key]
        if (pulseErrors.some(error => tell_time_match(error.time, time))) {
            newColorColumns.push(revmap[key])
        }
    }

    // Update colorColumns
    colorColumns.value = newColorColumns
}


const options = ref([]);

let eventSource = null
const client_latency = ref(0)
const past_time_client = ref(0)
const max_client_latency = ref(0)
const book = ref([])
const selectedOption = ref("ALL")

const handleColumnClick = ({ item, index }) => {
    showOnPage.value = item;
    book.value = []

}

// watch(selectedOption, (newValue) => {
//     console.log(newValue, " is the new value")
//     book.value = data['Order_Errors'][newValue]
// })


const map = {
    'Testing': 'my_program_shut_down',
    'XTS_Trader': 'trader_xts_shut_down',
    'Zerodha_Trader': 'trader_zerodha_shut_down',
    'Web_Sockets': 'websocket_shut_down',
    'Run_Strats': 'shut_down_pulse_run_strats',
    'PosMis Generator': 'shut_down_pulse_check_net_positions'
}


const showOnPage = ref('Order_Errors')

watch(data, (newValue) => {
    updateColorColumns(newValue, newValue['time'])
    if (newValue['time']) {
        let ar2 = newValue["time"];
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
    }
    if ('Order_Errors' in data) {
        options.value = Object.keys(data['Order_Errors'])
        options.value.push("ALL")
    }


    if (showOnPage.value === 'Order_Errors') {
        if (selectedOption.value == 'ALL') {
            if (data['Order_Errors']) {
                const combinedArray = Object.values(data['Order_Errors']).flat();
                book.value = combinedArray
            }
        }
        else if (selectedOption.value != '')
            book.value = data['Order_Errors'][selectedOption.value]

    }
    else {

        if (map[showOnPage.value]) {
            book.value = newValue['Pulse_Errors'][map[showOnPage.value]] || []
        }

        else book.value = []
    }


}, { immediate: true });

onMounted(() => {
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
            <NavBar
                :navColumns="['Order_Errors', 'Testing', 'Run_Strats', 'Web_Sockets', 'XTS_Trader', 'Zerodha_Trader', 'PosMis Generator']"
                @column-clicked="handleColumnClick" :colorColumns="colorColumns" />
        </div>
        <div class="userSelectContainer" v-if="book && showOnPage === 'Order_Errors'">
            <label class="table-heading" for="options">Select an User:</label>
            <select class="table-heading" id="options" v-model="selectedOption">
                <option v-for="option in options" :key="option" :value="option">
                    {{ option }}
                </option>
            </select>

        </div>

        <div class="my-8" v-if="book && showOnPage === 'Order_Errors'">
            <p class="table-heading">{{ showOnPage }}</p>
            <TanStackTestTable :data="book" :columns="live_order_book_columns" :hasColor="[]" :navigateTo="[]"
                :showPagination=true />
        </div>
        <div class="my-8" v-else-if="book">
            <p class="table-heading">{{ showOnPage }}</p>
            <TanStackTestTable :data="book" :columns="columns_testing" :hasColor="[]" :navigateTo="[]"
                :showPagination=true />
        </div>

        <!-- 

     


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
.userSelectContainer {
    margin-top: 30px;
}

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