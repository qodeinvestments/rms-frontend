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

    columnHelper.accessor(row => row.type, {
        id: 'Type',
        cell: info => info.getValue(),
        header: () => 'Type',
    }),
    columnHelper.accessor(row => row.value, {
        id: 'value',
        cell: info => info.getValue(),
        header: () => 'Value',
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
const user = ref()


// Add watch for user changes
watch(user, (newUser) => {
    if (newUser && connection_BackendData.value && connection_BackendData.value.position_mismatch) {
        updateDataForUser(newUser)
    }
})



const handleMessage = (message) => {
    client_BackendData.value = message.client_data
    connection_BackendData.value = message.connection_data

    if (connection_BackendData.value != undefined) {
        updateDataForUser(user.value)
    }

    updateData()
}

const updateDataForUser = (selectedUser) => {
    if (connection_BackendData.value.position_mismatch && connection_BackendData.value.position_mismatch[selectedUser]) {
        let val = connection_BackendData.value.position_mismatch[selectedUser]
        const result = {};
        for (const key in val) {
            result[key] = Object.entries(val[key]).map(([type, value]) => ({
                type: type,
                value
            }));
        }
        data.value = result;
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
    const socket = new WebSocket('wss://api.swancapital.in/ws');

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
const formatTableName = (key) => {
    // Convert camelCase or snake_case to Title Case
    return key
        .replace(/([A-Z])/g, ' $1')
        .replace(/_/g, ' ')
        .replace(/^./, str => str.toUpperCase());
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
                <option v-for="option in users" :key="option" :value="option">
                    {{ option }}
                </option>
            </select>
        </div>
        <div v-if="Object.keys(data).length > 0" class="mx-auto px-8 py-8">
            <div v-for="(tableData, key) in data" :key="key" class="my-8">
                <p class="table-heading">{{ formatTableName(key) }}</p>
                <TanStackTestTable :data="tableData" :columns="columns" :hasColor="[]" :navigateTo="{}"
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
</style>