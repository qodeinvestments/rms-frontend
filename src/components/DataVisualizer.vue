<script setup>
import { onMounted, onUnmounted } from 'vue';
import { ref } from 'vue';
import Histogram from './Histogram.vue';

const latency = ref(0);
const max_latency = ref(0);
const past_time = ref(0);

const WS7L = ref([]);
const WS8L = ref([]);
const signal_delay = ref([]);

let intervalId = null;

const fetchClientDetails = async () => {
    try {
        const response = await fetch('https://production.swancapital.in/lagsData');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        WS7L.value = data.WS7L;
        WS8L.value = data.WS8L;
        signal_delay.value = data.signal_delay;

        let ar2 = data["time"];
        if (past_time.value === 0) past_time.value = ar2;
        if (past_time.value != 0) {
            let date1 = new Date(past_time.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let diffInMs = date2 - date1;
            let diffInSeconds = diffInMs / 1000;
            latency.value = diffInSeconds;
            max_latency.value = Math.max(max_latency.value, latency.value);
            past_time.value = ar2;
        }
    } catch (error) {
        console.error('Error fetching client details:', error);
    }
};

onMounted(() => {
    // Fetch data periodically (e.g., every 5 seconds)
    fetchClientDetails();
    intervalId = setInterval(fetchClientDetails, 5000);
});

onUnmounted(() => {
    if (intervalId) {
        clearInterval(intervalId);
    }
});
</script>

<template>
    <div class="px-8 py-8 pageContainer">
        <div class="LatencyTable">
            <p> Latency :<span class="latencyvalue">{{ latency }}</span></p>
            <p> Max Client :<span class="latencyvalue">{{ max_latency }}</span></p>
        </div>
        <div v-if="WS7L.length > 0" class="histogram-container">
            <p class="heading">WebSocket 7 Lag</p>
            <Histogram :dataArray="WS7L" />
        </div>
        <div v-if="WS8L.length > 0" class="histogram-container">
            <p class="heading">WebSocket 8 Lag</p>
            <Histogram :dataArray="WS8L" />
        </div>
        <div v-if="signal_delay.length > 0" class="histogram-container">
            <p class="heading">Signal Delay</p>
            <Histogram :dataArray="signal_delay" />
        </div>
    </div>
</template>

<style scoped>
.histogram-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 30px;
}

.chartContainer {
    width: 100%;
    margin-bottom: 50px;
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
