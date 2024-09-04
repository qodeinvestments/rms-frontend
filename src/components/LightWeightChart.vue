<script setup>
import { ref, watch, computed } from 'vue';
import LWChart from './LWChart.vue';

const props = defineProps({
    Chartdata: {
        type: Object,
        required: true,
    },
});

const chartOptions = ref({});
const data = ref(props.Chartdata);
const seriesOptions = ref([]);
const chartType = ref('line');
const lwChart = ref();

const getDataKeys = computed(() => Object.keys(data.value));

// Create a map to store colors for each key
const colorMap = ref(new Map());

watch(
    () => props.Chartdata,
    newData => {
        data.value = newData;
        updateSeriesOptions(false);
    }
);

function randomColor() {
    return `rgb(${Math.round(Math.random() * 255)}, ${Math.round(Math.random() * 255)}, ${Math.round(Math.random() * 255)})`;
}

function updateSeriesOptions(regenerateColors = false) {
    seriesOptions.value = getDataKeys.value.map(key => {
        if (regenerateColors || !colorMap.value.has(key)) {
            colorMap.value.set(key, randomColor());
        }
        return {
            color: colorMap.value.get(key),
            title: key
        };
    });
}

const changeColors = () => {
    updateSeriesOptions(true);
};

// Initial setup
updateSeriesOptions(true);
</script>

<template>
    <div class="chart-wrapper">
        <div class="chart-container">
            <LWChart :type="chartType" :data="data" :autosize="true" :chart-options="chartOptions"
                :series-options="seriesOptions" ref="lwChart" />
        </div>
        <div class="legend">
            <div v-for="(option, index) in seriesOptions" :key="index" class="legend-item">
                <div class="color-box" :style="{ backgroundColor: option.color }"></div>
                <span>{{ option.title }}</span>
            </div>
        </div>
    </div>
    <button type="button" @click="changeColors">Set Random Colors</button>
</template>

<style scoped>
.chart-wrapper {
    display: flex;
    flex-direction: column;
    height: 400px;
}

.chart-container {
    flex-grow: 1;
}

.legend {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    padding: 10px 0;
    background-color: #f5f5f5;
}

.legend-item {
    display: flex;
    align-items: center;
    margin-right: 15px;
    margin-bottom: 5px;
}

.color-box {
    width: 20px;
    height: 20px;
    margin-right: 5px;
}
</style>