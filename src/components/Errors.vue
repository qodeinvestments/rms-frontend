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
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue';
import NavBar from './NavBar.vue';

import LightWeightChart from './LightWeightChart.vue';

import { new_order_errors_columns } from '../components/TableVariables/ErrorPageTable.js'; 



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



const colorColumns = ref([])
const parseCustomDate = (dateString) => {
    let [datePart, timePart] = dateString.split(' ');
    let [day, month, year] = datePart.split('-');
    // No need to parse time if we only care about the date
    return new Date(year, month - 1, day);  // Create a Date object only with year, month, and day
}

const tell_time_match = (a1, a2) => {
    if (a1 == null || a2 == null) return false;
    
    let date1 = parseCustomDate(a1);
    let date2 = parseCustomDate(a2);
    
    if (!date1 || !date2 || isNaN(date1.getTime()) || isNaN(date2.getTime())) {
        return false; // Ensure valid date objects
    }
    
    let sameDate = date1.getTime() === date2.getTime(); // Compare the time value (in ms) of the date objects
    return sameDate;
};

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
const selectedNewOrderOption = ref("ALL")
const newOrderOptions = ref([])
const allNewOrderErrors = ref([])  // Add this to store the complete dataset

const handleColumnClick = ({ item, index }) => {
    showOnPage.value = item;
    book.value = []

}



const map = {
    'Testing': 'my_program_shut_down',
    'XTS_Trader': 'trader_xts_shut_down',
    'Zerodha_Trader': 'trader_zerodha_shut_down',
    'Web_Sockets': 'websocket_shut_down',
    'Run_Strats': 'shut_down_pulse_run_strats',
    'PosMis Generator': 'shut_down_pulse_check_net_positions'
}


const showOnPage = ref('New_Order_Errors')

// Add watch for selectedNewOrderOption
watch(selectedNewOrderOption, (newValue) => {
    if (showOnPage.value === 'New_Order_Errors' && allNewOrderErrors.value.length > 0) {

        if (newValue === 'ALL') {
            book.value = allNewOrderErrors.value
            console.log('Setting all data:', book.value.length, 'items')
        } else {
            book.value = allNewOrderErrors.value.filter(item => item.Account === newValue)
            console.log('Filtered data:', book.value.length, 'items')
        }
    }
})

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

    if ('New_Order_Errors' in data) {
        // Store the complete dataset
        allNewOrderErrors.value = data['New_Order_Errors']
        
        // Get unique accounts from New_Order_Errors array
        const accounts = [...new Set(data['New_Order_Errors'].map(item => item.Account))]
 
        newOrderOptions.value = accounts
        newOrderOptions.value.push("ALL")
        
        // Apply current filter to new data
        if (showOnPage.value === 'New_Order_Errors') {

            if (selectedNewOrderOption.value === 'ALL') {
                book.value = allNewOrderErrors.value
            } else {
                book.value = allNewOrderErrors.value.filter(item => item.Account === selectedNewOrderOption.value)
              
            }
        }
    }

    // Handle other error types
    if (showOnPage.value !== 'New_Order_Errors') {
        if (map[showOnPage.value]) {
            book.value = newValue['Pulse_Errors'][map[showOnPage.value]] || []
        } else {
            book.value = []
        }
    }
}, { immediate: true });

// Also add a watch for showOnPage to handle page changes
watch(showOnPage, (newValue) => {
    
    if (newValue === 'New_Order_Errors' && allNewOrderErrors.value.length > 0) {
        if (selectedNewOrderOption.value === 'ALL') {
            book.value = allNewOrderErrors.value
            console.log('Set all data on page change:', book.value.length, 'items')
        } else {
            book.value = allNewOrderErrors.value.filter(item => item.Account === selectedNewOrderOption.value)
        }
    } else if (newValue !== 'New_Order_Errors') {
        // Handle other error types
        if (map[newValue]) {
            book.value = data.value['Pulse_Errors'][map[newValue]] || []
        } else {
            book.value = []
        }
    }
})

onMounted(() => {
    document.title = 'Error Page'
    name.value = route.params.username;
})

onUnmounted(() => {
    document.title = 'Vite App'
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
             
                :navColumns="['New_Order_Errors']"
                @column-clicked="handleColumnClick" 
                :colorColumns="colorColumns" />
                   <!-- :navColumns="['New_Order_Errors', 'Testing', 'Run_Strats', 'Web_Sockets', 'XTS_Trader', 'Zerodha_Trader', 'PosMis Generator']" -->
        </div>


        <div class="userSelectContainer" v-if="showOnPage === 'New_Order_Errors'">
            <label class="table-heading" for="newOrderOptions">Select an Account:</label>
            <select class="table-heading" id="newOrderOptions" v-model="selectedNewOrderOption">
                <option v-for="option in newOrderOptions" :key="option" :value="option">
                    {{ option }}
                </option>
            </select>
        </div>

        <div class="my-8" v-if="showOnPage === 'New_Order_Errors' && book">
            <TanStackTestTable 
                :title="showOnPage" 
                :data="book" 
                :columns="new_order_errors_columns" 
                :hasColor="[]"
                :navigateTo="[]" 
                :showPagination="true" />
        </div>
        <div class="my-8" v-else-if="book">
            <TanStackTestTable 
                :title="showOnPage" 
                :data="book" 
                :columns="columns_testing" 
                :hasColor="[]"
                :navigateTo="[]" 
                :showPagination="true" />
        </div>

    </div>


</template>

<style scoped>
.userSelectContainer {
    margin-top: 30px;
    display: flex;
    align-items: center;
    gap: 10px;
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