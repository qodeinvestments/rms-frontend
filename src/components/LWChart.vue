<script setup>
import {
    ref,
    onMounted,
    onUnmounted,
    watch,
} from 'vue';
import { createChart, ColorType } from 'lightweight-charts';

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
const tooltip = ref();

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
            crosshairMarkerVisible: false, // Disable crosshair marker on data points
            title: '', // Set empty title initially
        });
        newSeries.setData(props.data[key]);
        return newSeries;
    });
    removeTitles(); // Ensure titles are removed after creation
};

onMounted(() => {
    chart = createChart(chartContainer.value, {
        ...props.chartOptions,
        layout: {
            textColor: 'black',
            background: { type: ColorType.Solid, color: 'white' },
        },
        crosshair: {
            mode: 0, // Keep in Normal mode, or adjust as needed
            vertLine: {
                visible: true, // Disable the vertical line
                labelVisible: true, // Disable labels on the x-axis
            },
            horzLine: {
                visible: true, // Disable the vertical line
                labelVisible: true, // Disable labels on the x-axis
            },
        },
    });

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

    // Add tooltip functionality
    chart.subscribeCrosshairMove(param => {
        if (
            param.point === undefined ||
            !param.time ||
            param.point.x < 0 ||
            param.point.x > chartContainer.value.clientWidth ||
            param.point.y < 0 ||
            param.point.y > chartContainer.value.clientHeight
        ) {
            tooltip.value.style.display = 'none';
        } else {
            // Format time directly from provided data
            const adjustedTime = param.time - 19800;
            const dateTimeStr = new Date(adjustedTime * 1000).toLocaleString(); // Format adjusted time
            tooltip.value.style.display = 'block';
            let tooltipHtml = `<div class="tooltip-date">${dateTimeStr}</div>`;

            Object.keys(props.data).forEach(key => {
                const seriesIndex = Object.keys(props.data).indexOf(key);
                const data = param.seriesData.get(series[seriesIndex]);

                if (data) {
                    tooltipHtml += `
                    <div class="tooltip-series">
                        <span class="tooltip-series-name">${key}:</span>
                        <span class="tooltip-series-value" style="color: ${data.value < 0 ? 'red' : 'green'};">
                            ${data.value.toFixed(2)}
                        </span>
                    </div>
                `;
                }
            });

            tooltip.value.innerHTML = tooltipHtml;

            const toolTipWidth = 120;
            const toolTipHeight = 80;
            const toolTipMargin = 15;

            let left = param.point.x + toolTipMargin;
            if (left > chartContainer.value.clientWidth - toolTipWidth) {
                left = param.point.x - toolTipMargin - toolTipWidth;
            }

            let top = param.point.y + toolTipMargin;
            if (top > chartContainer.value.clientHeight - toolTipHeight) {
                top = param.point.y - toolTipHeight - toolTipMargin;
            }
            tooltip.value.style.left = `${left}px`;
            tooltip.value.style.top = `${top}px`;
        }
    });
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
    <div class="chart-wrapper">
        <div class="lw-chart" ref="chartContainer"></div>
        <div ref="tooltip" class="tooltip"></div>
    </div>
</template>

<style scoped>
.chart-wrapper {
    position: relative;
    width: 100%;
    height: 500px;
}

.lw-chart {
    width: 100%;
    height: 100%;
}

.tooltip {
    position: absolute;
    display: none;
    padding: 8px;
    box-sizing: border-box;
    font-size: 12px;
    text-align: left;
    z-index: 1000;
    top: 12px;
    left: 12px;
    pointer-events: none;
    border: 1px solid #2196F3;
    border-radius: 2px;
    font-family: -apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: white;
    color: black;
    width: fit-content;
}

.tooltip-date {
    font-weight: bold;
    margin-bottom: 4px;
}

.tooltip-series {
    margin-top: 3px;
}

.tooltip-series-name {
    color: #2196F3;
}

.tooltip-series-value {
    float: right;
}
</style>