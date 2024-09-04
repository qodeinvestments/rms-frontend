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

const signal_book_data = ref([])
const uids = ref([])
const basket = ref([])

const columnHelper = createColumnHelper()

const latency = ref(0)
const max_latency = ref(0)
const past_time = ref(0)
const histogram = ref(0)
const selected_uid = ref('')

const columns = [
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



// Updated computed property for filtered signal_book_data
const filteredSignalBookData = computed(() => {
    if (selectedUids.value.length === 0 && selectedBasketItems.value.length === 0) {
        return signal_book_data.value;
    }
    return signal_book_data.value.filter(item => {
        const basketMatch = selectedBasketItems.value.length === 0 || selectedBasketItems.value.includes(item.uid.split('_')[0]);
        const uidMatch = selectedUids.value.length === 0 || selectedUids.value.includes(item.uid);
        return basketMatch && uidMatch;
    });
});


const connectClientDetailsWebSocket = () => {
    const clientDetailSocket = new WebSocket('wss://production.swancapital.in/signalbook');

    clientDetailSocket.onopen = function (e) {
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




</script>


<template>
    <div class="px-8 py-8 pageContainer">
        <div class="LatencyTable">
            <p> Latency :<span class="latencyvalue">{{ latency }}</span></p>
            <p> Max Client :<span class="latencyvalue">{{ max_latency }}</span></p>
        </div>

        <!-- Basket multi-select component -->
        <a-select v-model:value="selectedBasketItems" mode="multiple" placeholder="Select Basket Items"
            style="width: 100%; margin-bottom: 10px;"
            :options="filteredBasketOptions.map(item => ({ value: item }))"></a-select>

        <!-- UID multi-select component -->
        <a-select v-model:value="selectedUids" mode="multiple" placeholder="Select UIDs" style="width: 100%"
            :options="filteredOptions.map(item => ({ value: item }))"></a-select>

        <div class="my-8" v-if="filteredSignalBookData.length">
            <p class="table-heading">Signal Book</p>
            <TanStackTestTable :data="filteredSignalBookData" :columns="columns" :hasColor="[]" :navigateTo="[]"
                :showPagination=true />
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