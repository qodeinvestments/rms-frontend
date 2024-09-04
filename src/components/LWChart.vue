<script setup>
import {
    ref,
    onMounted,
    onUnmounted,
    watch,
} from 'vue';
import { createChart } from 'lightweight-charts';

const props = defineProps({
    type: {
        type: String,
        default: 'line',
    },
    data: {
        type: Object,
        required: true,
    },
    autosize: {
        default: true,
        type: Boolean,
    },
    chartOptions: {
        type: Object,
    },
    seriesOptions: {
        type: Array,
        default: () => [],
    },
    timeScaleOptions: {
        type: Object,
        default: () => ({
            timeVisible: true,
            secondsVisible: false,
        }),
    },
    priceScaleOptions: {
        type: Object,
    },
});

function getChartSeriesConstructorName(type) {
    return `add${type.charAt(0).toUpperCase() + type.slice(1)}Series`;
}

let series = [];
let chart;

const chartContainer = ref();

const fitContent = () => {
    if (!chart) return;
    chart.timeScale().fitContent();
};

const getChart = () => {
    return chart;
};

defineExpose({ fitContent, getChart });

const resizeHandler = () => {
    if (!chart || !chartContainer.value) return;
    const dimensions = chartContainer.value.getBoundingClientRect();
    chart.resize(dimensions.width, dimensions.height);
};

const removeTitles = () => {
    series.forEach(s => {
        s.applyOptions({ title: '' });
    });
};

const addSeriesAndData = (props) => {
    const seriesConstructor = getChartSeriesConstructorName(props.type);
    series = Object.keys(props.data).map((key, index) => {
        const options = props.seriesOptions[index] || {};
        const newSeries = chart[seriesConstructor]({
            ...options,
            title: '', // Set empty title initially
        });
        newSeries.setData(props.data[key]);
        return newSeries;
    });
    removeTitles(); // Ensure titles are removed after creation
};

onMounted(() => {
    chart = createChart(chartContainer.value, props.chartOptions);
    addSeriesAndData(props);

    if (props.priceScaleOptions) {
        chart.priceScale().applyOptions(props.priceScaleOptions);
    }

    if (props.timeScaleOptions) {
        chart.timeScale().applyOptions(props.timeScaleOptions);
    }

    chart.timeScale().fitContent();

    if (props.autosize) {
        window.addEventListener('resize', resizeHandler);
    }
});

onUnmounted(() => {
    if (chart) {
        chart.remove();
        chart = null;
    }
    if (series.length) {
        series = [];
    }
    window.removeEventListener('resize', resizeHandler);
});

watch(
    () => props.autosize,
    enabled => {
        if (!enabled) {
            window.removeEventListener('resize', resizeHandler);
            return;
        }
        window.addEventListener('resize', resizeHandler);
    }
);

watch(
    () => props.type,
    () => {
        if (series.length && chart) {
            series.forEach(s => chart.removeSeries(s));
        }
        addSeriesAndData(props);
    }
);

watch(
    () => props.data,
    newData => {
        if (!series.length) return;
        Object.keys(newData).forEach((key, index) => {
            if (series[index]) {
                series[index].setData(newData[key]);
            }
        });
        removeTitles(); // Ensure titles are removed after data update
    }
);

watch(
    () => props.chartOptions,
    newOptions => {
        if (!chart) return;
        chart.applyOptions(newOptions);
    }
);

watch(
    () => props.seriesOptions,
    newOptions => {
        if (!series.length) return;
        series.forEach((s, index) => {
            if (newOptions[index]) {
                s.applyOptions({ ...newOptions[index], title: '' }); // Ensure title remains empty
            }
        });
    }
);

watch(
    () => props.priceScaleOptions,
    newOptions => {
        if (!chart) return;
        chart.priceScale().applyOptions(newOptions);
    }
);

watch(
    () => props.timeScaleOptions,
    newOptions => {
        if (!chart) return;
        chart.timeScale().applyOptions(newOptions);
    }
);
</script>

<template>
    <div class="lw-chart" ref="chartContainer"></div>
</template>

<style scoped>
.lw-chart {
    height: 100%;
}
</style>