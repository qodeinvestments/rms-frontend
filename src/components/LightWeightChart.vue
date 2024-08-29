<script setup>
import {

    watch,
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
const get_data_keys = () => {

    return Object.keys(data.value).length;
}

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
    {{ get_data_keys() }}
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
