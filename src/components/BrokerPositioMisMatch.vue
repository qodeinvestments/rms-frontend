<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
} from '@tanstack/vue-table'
import TanStackTestTable from './TanStackTestTable.vue'

const defaultData = {}


const data = ref(defaultData)
const columnHelper = createColumnHelper()

const columns = [

    columnHelper.accessor(row => row.Symbol, {
        id: 'Symbol',
        cell: info => info.getValue(),
        header: () => 'Symbol',
    }),
    columnHelper.accessor(row => row.Quantity, {
        id: 'Difference Quantity',
        cell: info => info.getValue(),
        header: () => 'Quantity',
    }),

]



const client_BackendData = ref({})
const connection_BackendData = ref({})

const time = ref([])
const checkBackendConnection = ref(false)
const Latency = ref(0)
const max_latency = ref(0);
const past_time = ref(0)
const live_weights = ref([]);
let socket = null
let reconnectAttempts = 0
const users = ref([])
const user = ref('')
const fulldata = ref()
const posdata=ref()




const handleMessage = (message) => {
    client_BackendData.value = message.client_data
    connection_BackendData.value = message.connection_data
    if (message.connection_data) {
        fulldata.value = message.connection_data.broker_Position_Mismatch;
        posdata.value=message.connection_data.position_broker_Mismatch;
        users.value=Object.keys(fulldata.value);
    }
   

}




const connectWebSocket = () => {
    const token = localStorage.getItem('access_token'); // Retrieve the access token
    if (!token) {
        alert('User not authenticated');
        return;
    }
    const socket = new WebSocket('wss://production2.swancapital.in/ws');

    socket.onopen = () => {
        console.log('WebSocket connection opened')
        const authMessage = JSON.stringify({ token });
        socket.send(authMessage);
        checkBackendConnection.value = true
        reconnectAttempts = 0
  
    }

    socket.onmessage = (event) => {
        if (event.data === 'ping') {
            socket.send('pong')
        } else {

            const message = JSON.parse(event.data);
            if (message['live_weights']) {
                live_weights.value = message['live_weights'];
            }
            let ar2 = message.time;
            if (past_time.value === 0) past_time.value = ar2;
            let date1 = new Date(past_time.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let diffInMs = date2 - date1;
            let diffInSeconds = diffInMs / 1000;
            Latency.value = diffInSeconds;
            max_latency.value = Math.max(max_latency.value, Latency.value)
            past_time.value = ar2;
            handleMessage(message)
        }
    }

    socket.onclose = (event) => {
        console.log('WebSocket connection closed:', event.reason)
        checkBackendConnection.value = false
  
    }


    socket.onerror = (error) => {
        console.error('WebSocket error:', error)
        checkBackendConnection.value = false
    }
}











onMounted(() => {
    connectWebSocket()
})

onUnmounted(() => {
    if (socket) {
        socket.close()
    }
})
</script>



<template>
    <div class="homePage_Container bg-[#efefef]/30">
       

        <div class="userSelectContainer" v-if="users">
            <label class="table-heading" for="options">Select an User:</label>
            <select class="table-heading" id="options" v-model="user">
                <option v-for="option in users" :key="option" :value="option"
                    :class="(fulldata[option].length > 0 ||  posdata[option].length > 0 )? 'negativecolor' : ''">
                    {{ option }}

                </option>
            </select>
        </div>
       
        <div v-if="user === ''" class="mx-auto py-8 negative">
            <p class="table-heading">Select User !</p>
        </div>
        <div v-else-if="Object.keys(fulldata[user]).length > 0 || Object.keys(posdata[user]).length > 0" class="mx-auto px-8 py-8 flex flex-col gap-8">
            <!-- <p class="table-heading">Position MisMatch : {{ user }}</p> -->
             <div v-if="Object.keys(fulldata[user]).length > 0">
                <TanStackTestTable title="Broker Position MisMatch" :data="fulldata[user]" :columns="columns" :hasColor="[]" :navigateTo="{}"
                :showPagination="true" :hasRowcolor="{}" />

             </div>
             <div v-if="Object.keys(posdata[user]).length > 0">

                <TanStackTestTable title="Position Broker MisMatch" :data="posdata[user]" :columns="columns" :hasColor="[]" :navigateTo="{}"
                :showPagination="true" :hasRowcolor="{}" />

             </div>
           
           
        </div>

        <div v-else class="mx-auto px-8 py-8">
            <p class="table-heading">No Data</p>
        </div>
    </div>
</template>


<style>
html {
    font-size: 14px;
}


.userSelectContainer {
    margin-top: 30px;
}

.table-heading {
    font-size: 22px;
    font-weight: 600;
    margin-left: 30px;
}

.negativecolor {
    color: #d95858 !important;
}
</style>