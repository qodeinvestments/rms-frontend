<script setup>


import { onMounted, onUnmounted } from 'vue'
import BarChart from './Barchart.vue';

import { ref, watch } from 'vue'
import { useRoute } from 'vue-router';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue';
import MultiLineChart from './HighCharts.vue'

import LightWeightChart from './LightWeightChart.vue';


const user_data = ref('')

let eventSource = null

const data = ref([])
const client_details_Latency = ref(0)
const past_time_clientDetails = ref(0)
const max_client_details_latency = ref(0)
const mix_real_ideal_mtm_table = ref({})

const serverData = ref({})

const connectServerDataWebSocket = () => {
    const ServerDataSocket = new WebSocket('wss://production.swancapital.in/serverData');

    ServerDataSocket.onopen = function (e) {
        console.log("ServerDataSocket details connection established");
    };
    ServerDataSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);


        let ar2 = data["time"];
        if (past_time_clientDetails.value === 0) past_time_clientDetails.value = ar2;
        if (past_time_clientDetails.value != 0) {
            let date1 = new Date(past_time_clientDetails.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let diffInMs = date2 - date1;
            let diffInSeconds = diffInMs / 1000;
            client_details_Latency.value = diffInSeconds;
            max_client_details_latency.value = Math.max(max_client_details_latency.value, client_details_Latency.value)
            past_time_clientDetails.value = ar2;
        }


        if (data) {
            serverData.value = data;
        } else {
            serverData.value = [];
        }
    };

    ServerDataSocket.onerror = function (error) {
        console.log(`WebSocket error: ${error.message}`);
    };

    ServerDataSocket.onclose = function (event) {
        console.log('ServerDataSocket Detail WebSocket connection closed:', event.reason);
    };



    return ServerDataSocket;
};





onMounted(() => {

    connectServerDataWebSocket();
})

onUnmounted(() => {
    if (eventSource) {
        eventSource.close()
    }
})




</script>

<template>

    <div class="px-8 py-8 pageContainer">
        <div>
            {{ client_details_Latency }}
            {{ max_client_details_latency }}
        </div>
        <div>
            <p class="table-heading">CPU USAGE </p>
            <LightWeightChart v-if="serverData['CPU']" :Chartdata="{ 'data': serverData['CPU'] }" />
        </div>
        <div>
            <p class="table-heading">RAM USAGE </p>
            <LightWeightChart v-if="serverData['RAM']" :Chartdata="{ 'data': serverData['RAM'] }" />
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