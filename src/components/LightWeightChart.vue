<script setup>
import {

    watch,
    defineProps
} from 'vue';
// This starter template is using Vue 3 <script setup> SFCs
import { ref } from 'vue';
const props = defineProps({
    Chartdata: {
        type: Object,
        required: true,
    },
});


import LWChart from './LWChart.vue';

const chartOptions = ref({});
const data = ref(props.Chartdata); // Changed to reactive reference
const seriesOptions = ref({
    color: 'rgb(45, 77, 205)',
});

watch(
    () => props.Chartdata,
    newData => {
        data.value = newData
    }
);
const chartType = ref('line');
const lwChart = ref();

function randomShade() {
    return Math.round(Math.random() * 255);
}

const randomColor = (alpha = 1) => {
    return `rgba(${randomShade()}, ${randomShade()}, ${randomShade()}, ${alpha})`;
};

const colorsTypeMap = {
    area: [
        ['topColor', 0.4],
        ['bottomColor', 0],
        ['lineColor', 1],
    ],
    bar: [
        ['upColor', 1],
        ['downColor', 1],
    ],
    baseline: [
        ['topFillColor1', 0.28],
        ['topFillColor2', 0.05],
        ['topLineColor', 1],
        ['bottomFillColor1', 0.28],
        ['bottomFillColor2', 0.05],
        ['bottomLineColor', 1],
    ],
    candlestick: [
        ['upColor', 1],
        ['downColor', 1],
        ['borderUpColor', 1],
        ['borderDownColor', 1],
        ['wickUpColor', 1],
        ['wickDownColor', 1],
    ],
    histogram: [['color', 1]],
    line: [['color', 1]],
};

const changeColors = () => {
    const options = {};
    const colorsToSet = colorsTypeMap[chartType.value];
    colorsToSet.forEach(c => {
        options[c[0]] = randomColor(c[1]);
    });
    seriesOptions.value = options;
};




</script>

<template>
    <div class="chart-container" style="height: 400px;">
        <LWChart :type="chartType" :data="data" :autosize="true" :chart-options="chartOptions"
            :series-options="seriesOptions" ref="lwChart" />
    </div>
    <button type="button" @click="changeColors">Set Random Colors</button>
</template>

<style scoped>
.chart-container {
    height: calc(100% - 3.2em);
}
</style>
