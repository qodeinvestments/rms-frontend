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

    columnHelper.accessor(row => row.symbol, {
        id: 'Symbol',
        cell: info => info.getValue(),
        header: () => 'Symbol',
    }),
    columnHelper.accessor(row => row['Signal Net'], {
        id: 'Signal Net',
        cell: info => info.getValue(),
        header: () => 'Signal Net',
    }),
    columnHelper.accessor(row => row['Live Net Positions'], {
        id: 'Live Net Positions',
        cell: info => info.getValue(),
        header: () => 'Live Net Positions',
    }),
    columnHelper.accessor(row => row.Difference, {
        id: 'Difference',
        cell: info => info.getValue(),
        header: () => 'Difference',
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
const maxReconnectAttempts = 5
const reconnectInterval = 5000 // 5 seconds
const pingInterval = 30000 // 30 seconds
const users = ref([])
const user = ref('')
const fulldata = ref()


// Add watch for user changes
watch(user, (newUser) => {
    if (newUser && connection_BackendData.value && connection_BackendData.value.position_mismatch) {
        updateDataForUser(newUser)
    }
})



const handleMessage = (message) => {
    client_BackendData.value = message.client_data
    connection_BackendData.value = message.connection_data
    if (message.connection_data)
        fulldata.value = message.connection_data.position_mismatch;
    if (connection_BackendData.value != undefined) {
        updateDataForUser(user.value)
    }

    updateData()
}

const updateDataForUser = (selectedUser) => {
    if (connection_BackendData.value.position_mismatch && connection_BackendData.value.position_mismatch[selectedUser]) {
        let val = connection_BackendData.value.position_mismatch[selectedUser]
        data.value = val;
    }
}
const updateData = () => {
    if (connection_BackendData.value != undefined) {
        time.value = connection_BackendData.value.time
        if (connection_BackendData.value.pulse) {
            users.value = Object.keys(connection_BackendData.value.position_mismatch)
        }
    }
}


const connectWebSocket = () => {
    const socket = new WebSocket('wss://production.swancapital.in/ws');

    socket.onopen = () => {
        console.log('WebSocket connection opened')
        checkBackendConnection.value = true
        reconnectAttempts = 0
        startPingInterval()
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
        stopPingInterval()
        reconnect()
    }


    socket.onerror = (error) => {
        console.error('WebSocket error:', error)
        checkBackendConnection.value = false
    }
}






const reconnect = () => {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++
        console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})...`)
        setTimeout(connectWebSocket, reconnectInterval)
    } else {
        console.log('Max reconnection attempts reached. Please refresh the page.')
    }
}


let pingIntervalId = null

const startPingInterval = () => {
    pingIntervalId = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send('ping')
        }
    }, pingInterval)
}

const stopPingInterval = () => {
    if (pingIntervalId) {
        clearInterval(pingIntervalId)
        pingIntervalId = null
    }
}



onMounted(() => {
    connectWebSocket()
})

onUnmounted(() => {
    if (socket) {
        socket.close()
    }
    stopPingInterval()
})
</script>



<template>
    <div class="homePage_Container bg-[#efefef]/30">

        <div class="userSelectContainer" v-if="users">
            <label class="table-heading" for="options">Select an User:</label>
            <select class="table-heading" id="options" v-model="user">
                <option v-for="option in users" :key="option" :value="option"
                    :class="fulldata[option].length > 0 ? 'negativecolor' : ''">
                    {{ option }}

                </option>
            </select>
        </div>
        <div v-if="user === ''" class="mx-auto py-8 negative">
            <p class="table-heading">Select User !</p>
        </div>
        <div v-else-if="Object.keys(data).length > 0" class="mx-auto px-8 py-8">
            <p class="table-heading">Position MisMatch : {{ user }}</p>
            <TanStackTestTable :data="data" :columns="columns" :hasColor="[]" :navigateTo="{}" :showPagination="true"
                :hasRowcolor="{}" />
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