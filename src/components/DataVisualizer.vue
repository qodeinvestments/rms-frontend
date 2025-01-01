<script setup>
import { onMounted, onUnmounted } from 'vue';
import { ref } from 'vue';
import Histogram from './Histogram.vue';


const past_time = ref(0);

const WS7L = ref([]);
const WS8L = ref([]);
const signal_delay = ref([]);

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

      
    } catch (error) {
        console.error('Error fetching client details:', error);
    }
};
onMounted(() => {
    fetchClientDetails();
});

</script>

<template>
    <div class="px-8 py-8 pageContainer">
        <button @click="fetchClientDetails" class="refresh-button">
            Refresh Data
        </button>
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


.refresh-button {
    margin-bottom: 20px;
    padding: 10px 15px;
    font-size: 14px;
    width: 200px;
    cursor: pointer;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    align-self: flex-end; /* Align the button to the right */
}

html {
    font-family: poppins;
    font-size: 14px;
}

</style>
