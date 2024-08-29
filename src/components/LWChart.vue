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
        type: Object,
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

// Function to get the correct series constructor name for current series type.
function getChartSeriesConstructorName(type) {
    return `add${type.charAt(0).toUpperCase() + type.slice(1)}Series`;
}

// Lightweight Charts™ instances are stored as normal JS variables
// If you need to use a ref then it is recommended that you use `shallowRef` instead
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

// Auto resizes the chart when the browser window is resized.
const resizeHandler = () => {
    if (!chart || !chartContainer.value) return;
    const dimensions = chartContainer.value.getBoundingClientRect();
    chart.resize(dimensions.width, dimensions.height);
};

// Function to generate a random color
const getRandomColor = () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
};

// Creates the chart series and sets the data.
const addSeriesAndData = props => {
    const seriesConstructor = getChartSeriesConstructorName(props.type);
    series = Object.keys(props.data).map(key => {
        const newSeries = chart[seriesConstructor]({
            ...props.seriesOptions,
            color: getRandomColor()
        });
        newSeries.setData(props.data[key]);
        return newSeries;
    });
};

onMounted(() => {
    // Create the Lightweight Charts Instance using the container ref.
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

/*
 * Watch for changes to any of the component properties.

 * If an options property is changed then we will apply those options
 * on top of any existing options previously set (since we are using the
 * `applyOptions` method).
 *
 * If there is a change to the chart type, then the existing series is removed
 * and the new series is created, and assigned the data.
 *
 */
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
    newType => {
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
        series.forEach((s, i) => {
            const key = Object.keys(newData)[i];
            if (key) {
                s.setData(newData[key]);
            }
        });
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
        series.forEach(s => s.applyOptions(newOptions));
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
