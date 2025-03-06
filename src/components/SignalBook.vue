<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
} from '@tanstack/vue-table'

import { MyEnum } from '../Enums/Prefix.js';
import { ref, watch } from 'vue'
import TanStackTestTable from './TanStackTestTable.vue'
import Histogram from './Histogram.vue';
import { columns } from '../components/TableVariables/SignalBook.js'; 


const signal_book_data = ref([])
const uids = ref([])
const basket = ref([])

const columnHelper = createColumnHelper()

const latency = ref(0)
const max_latency = ref(0)
const past_time = ref(0)
const histogram = ref(0)
const selected_uid = ref('')

// Add filter for checker status
const showOnlyUnchecked = ref(false)

const selectedUids = ref([]);
const selectedBasketItems = ref([]);

const filteredBasketOptions = computed(() => basket.value.filter(o => !selectedBasketItems.value.includes(o)));

const filteredUids = computed(() => {
    if (selectedBasketItems.value.length === 0) {
        return uids.value;
    }
    return uids.value.filter(uid => selectedBasketItems.value.includes(uid.split('_')[0]));
});

const filteredOptions = computed(() => filteredUids.value.filter(o => !selectedUids.value.includes(o)));

// Updated computed property for filtered signal_book_data with checker filter
const filteredSignalBookData = computed(() => {
    let filteredData = signal_book_data.value;
    
    // Apply checker filter if enabled
    if (showOnlyUnchecked.value) {
        filteredData = filteredData.filter(item => item.checker === 'False');
    }
    
    // Apply existing filters
    if (selectedUids.value.length > 0 || selectedBasketItems.value.length > 0) {
        filteredData = filteredData.filter(item => {
            const basketMatch = selectedBasketItems.value.length === 0 || selectedBasketItems.value.includes(item.uid.split('_')[0]);
            const uidMatch = selectedUids.value.length === 0 || selectedUids.value.includes(item.uid);
            return basketMatch && uidMatch;
        });
    }
    
    return filteredData;
});


const connectClientDetailsWebSocket = () => {
    const token = localStorage.getItem('access_token'); // Retrieve the access token
    if (!token) {
        alert('User not authenticated');
        return;
    }
    
    const clientDetailSocket = new WebSocket('wss://production2.swancapital.in/signalbook');

    clientDetailSocket.onopen = function (e) {
            
    // Send the token as the first message for authentication
        const authMessage = JSON.stringify({ token });
        clientDetailSocket.send(authMessage);
        console.log("Client details connection established");
    };
    clientDetailSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        signal_book_data.value = Object.values(data['table_data'])
        uids.value = [...new Set(signal_book_data.value.map(item => item.uid))];
        basket.value = [...new Set(signal_book_data.value.map(item => item.uid.split('_')[0]))];
        histogram.value = signal_book_data.value.map(item => item.time_diff);
        let ar2 = data["time"];
        if (past_time.value === 0) past_time.value = ar2;
        if (past_time.value != 0) {
            let date1 = new Date(past_time.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let diffInMs = date2 - date1;
            let diffInSeconds = diffInMs / 1000;
            latency.value = diffInSeconds;
            max_latency.value = Math.max(max_latency.value, latency.value)
            past_time.value = ar2;
        }
    };


    clientDetailSocket.onerror = function (error) {
        console.log(`WebSocket error: ${error.message}`);
    };

    clientDetailSocket.onclose = function (event) {
        console.log('Client Detail WebSocket connection closed:', event.reason);
    };

    return clientDetailSocket;
};

const showOnPage = ref('Positions')

onMounted(() => {
    connectClientDetailsWebSocket();
})

onUnmounted(() => {

})

// Watch for changes in selectedBasketItems
watch(selectedBasketItems, (newSelectedBasketItems) => {
    console.log('Selected Basket items changed:', newSelectedBasketItems);
    // Reset UID selection when basket selection changes
    selectedUids.value = [];
});

// Toggle function for the checker filter
const toggleCheckerFilter = () => {
    showOnlyUnchecked.value = !showOnlyUnchecked.value;
}
</script>


<template>
    <div class="px-8 py-8 pageContainer">
        <div class="LatencyTable">
            <p> Latency :<span class="latencyvalue">{{ latency }}</span></p>
            <p> Max Client :<span class="latencyvalue">{{ max_latency }}</span></p>
        </div>

        <div class="filter-controls">
            <!-- Basket multi-select component -->
            <a-select v-model:value="selectedBasketItems" mode="multiple" placeholder="Select Basket Items"
                style="width: 100%; margin-bottom: 10px;"
                :options="filteredBasketOptions.map(item => ({ value: item }))"></a-select>

            <!-- UID multi-select component -->
            <a-select v-model:value="selectedUids" mode="multiple" placeholder="Select UIDs" style="width: 100%; margin-bottom: 10px;"
                :options="filteredOptions.map(item => ({ value: item }))"></a-select>
            
            <!-- Checker filter toggle button with custom styling -->
            <button 
                @click="toggleCheckerFilter" 
                class="custom-checker-btn">
                {{ showOnlyUnchecked ? 'Showing Unchecked Only' : 'Show All Items' }}
            </button>
        </div>

        <div class="my-8" v-if="filteredSignalBookData.length">
            <!-- <p class="table-heading">Signal Book</p> -->
            <TanStackTestTable title="PsarTable" :data="filteredSignalBookData" :columns="columns" :hasColor="[]"
                :navigateTo="[]" :showPagination=true :showPin="true"/>
        </div>
        <div v-if="histogram.length > 0" class="histogram-container">
            <p class="table-heading">Histogram Of Time Difference</p>
            <Histogram :dataArray="histogram" />
        </div>
    </div>
</template>

<style scoped>
.a-select {
    margin-top: 20px;
    margin-bottom: 20px;
}

.pageContainer {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.histogram-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 30px;
}

.filter-controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}

/* Custom button styling without hover effects and background colors */
.custom-checker-btn {
    align-self: flex-start;
    padding: 8px 16px;
    border: 1px solid #d9d9d9;
    border-radius: 2px;
    cursor: pointer;
    transition: border-color 0.3s;
    background: none;
    font-size: 14px;
    color: rgba(0, 0, 0, 0.85);
}

.custom-checker-btn:focus {
    outline: none;
}

/* Simple border change to indicate active state */
.custom-checker-btn:global(.active), 
.custom-checker-btn:global([aria-pressed="true"]) {
    border-color: #1890ff;
    color: #1890ff;
}

.latencyvalue {
    font-weight: bold;
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

html {
    /* font-family: poppins; */
    font-size: 14px;
}
</style>