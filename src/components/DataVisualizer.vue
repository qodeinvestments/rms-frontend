<script setup>
import { onMounted, onUnmounted } from 'vue'
import { MyEnum } from '../Enums/Prefix.js';
import { ref, watch } from 'vue'
import Histogram from './Histogram.vue';



const latency = ref(0)
const max_latency = ref(0)
const past_time = ref(0)

const WS3L = ref([])
const WS4L = ref([])



const connectClientDetailsWebSocket = () => {
    const clientDetailSocket = new WebSocket('wss://production.swancapital.in/lagsData');

    clientDetailSocket.onopen = function (e) {
        console.log("Client details connection established");
    };
    clientDetailSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        WS3L.value = data.WS3L
        WS4L.value = data.WS4L



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



</script>
<template>
    <div class="px-8 py-8 pageContainer">
        <div class="LatencyTable">
            <p> Latency :<span class="latencyvalue">{{ latency }}</span></p>
            <p> Max Client :<span class="latencyvalue">{{ max_latency }}</span></p>
        </div>
        <div v-if="WS3L.length > 0" class="histogram-container">
            <p class="heading">WebSocket 3 Lag</p>
            <Histogram :dataArray="WS3L" />
        </div>
        <div v-if="WS4L.length > 0" class="histogram-container">
            <p class="heading">WebSocket 4 Lag</p>
            <Histogram :dataArray="WS4L" />
        </div>
    </div>


</template>

<style scoped>
.histogram-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 30px;
}

.heading {
    font-size: 20px;
    font-weight: bold;
}

.pageContainer {
    height: 100%;
    display: flex;
    flex-direction: column;
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
    font-family: poppins;
    font-size: 14px;
}
</style>