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
            crosshairMarkerVisible: true,
            title: '',
            lineWidth: 2,
            priceLineVisible: false,
            lastValueVisible: true,
        });
        newSeries.setData(props.data[key]);
        return newSeries;
    });
    removeTitles();
};

onMounted(() => {
    chart = createChart(chartContainer.value, {
        ...props.chartOptions,
        layout: {
            textColor: '#64748b',
            background: { type: ColorType.Solid, color: 'white' },
            fontSize: 12,
            fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
        },
        grid: {
            vertLines: {
                color: '#e2e8f0',
                style: 1,
            },
            horzLines: {
                color: '#e2e8f0',
                style: 1,
            },
        },
        crosshair: {
            mode: 1,
            vertLine: {
                color: '#2563eb',
                width: 1,
                style: 3,
                labelBackgroundColor: '#2563eb',
            },
            horzLine: {
                color: '#2563eb',
                width: 1,
                style: 3,
                labelBackgroundColor: '#2563eb',
            },
        },
        rightPriceScale: {
            borderVisible: false,
        },
        timeScale: {
            borderVisible: false,
            timeVisible: true,
            secondsVisible: false,
        },
        handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: true,
        },
        handleScale: {
            mouseWheel: true,
            pinch: true,
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
            const adjustedTime = param.time - 19800;
            const dateTimeStr = new Date(adjustedTime * 1000).toLocaleString();
            tooltip.value.style.display = 'block';
            let tooltipHtml = `<div class="tooltip-date">${dateTimeStr}</div>`;

            Object.keys(props.data).forEach(key => {
                const seriesIndex = Object.keys(props.data).indexOf(key);
                const data = param.seriesData.get(series[seriesIndex]);

                if (data) {
                    const value = data.value.toFixed(2);
                    const trend = data.value < 0 ? 'down' : 'up';
                    tooltipHtml += `
                        <div class="tooltip-series">
                            <span class="tooltip-series-name">${key}</span>
                            <span class="tooltip-series-value" data-trend="${trend}">
                                ${value}
                            </span>
                        </div>
                    `;
                }
            });

            tooltip.value.innerHTML = tooltipHtml;

            const toolTipWidth = 200;
            const toolTipHeight = 120;
            const toolTipMargin = 15;

            // Improved positioning logic
            let left = param.point.x + toolTipMargin;
            if (left > chartContainer.value.clientWidth - toolTipWidth) {
                left = param.point.x - toolTipMargin - toolTipWidth;
            }

            let top = param.point.y - toolTipHeight - toolTipMargin;
            if (top < 0) {
                top = param.point.y + toolTipMargin;
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

// Keep all your existing watch functions
watch(() => props.autosize, enabled => {
    if (!enabled) {
        window.removeEventListener('resize', resizeHandler);
        return;
    }
    window.addEventListener('resize', resizeHandler);
});

watch(() => props.type, () => {
    if (series.length && chart) {
        series.forEach(s => chart.removeSeries(s));
    }
    addSeriesAndData(props);
});

watch(() => props.data, newData => {
    if (!series.length) return;
    Object.keys(newData).forEach((key, index) => {
        if (series[index]) {
            series[index].setData(newData[key]);
        }
    });
    removeTitles();
});

watch(() => props.chartOptions, newOptions => {
    if (!chart) return;
    chart.applyOptions(newOptions);
});

watch(() => props.seriesOptions, newOptions => {
    if (!series.length) return;
    series.forEach((s, index) => {
        if (newOptions[index]) {
            s.applyOptions({ ...newOptions[index], title: '' });
        }
    });
});

watch(() => props.priceScaleOptions, newOptions => {
    if (!chart) return;
    chart.priceScale().applyOptions(newOptions);
});

watch(() => props.timeScaleOptions, newOptions => {
    if (!chart) return;
    chart.timeScale().applyOptions(newOptions);
});
</script>

<template>
    <div class="chart-container">
        <div class="chart-wrapper">
            <div class="chart-area" ref="chartContainer"></div>
            <div ref="tooltip" class="tooltip"></div>
        </div>
    </div>
</template>

<style scoped>
.chart-container {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 14px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(229, 231, 235, 0.5);
    padding: 1.5rem;
    margin: 1rem 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chart-container:hover {
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
}

.chart-wrapper {
    position: relative;
    width: 100%;
    height: 500px;
    border-radius: 10px;
    overflow: hidden;
}

.chart-area {
    width: 100%;
    height: 100%;
    transition: opacity 0.2s ease;
}

.tooltip {
    position: absolute;
    display: none;
    padding: 1rem;
    border-radius: 10px;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-size: 0.875rem;
    z-index: 1000;
    pointer-events: none;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(229, 231, 235, 0.5);
    min-width: 200px;
    transform-origin: top left;
    animation: tooltipFade 0.2s ease-out forwards;
}

.tooltip-date {
    font-weight: 600;
    color: #1e293b;
    padding-bottom: 0.75rem;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
    font-size: 0.875rem;
}

.tooltip-series {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    font-size: 0.875rem;
}

.tooltip-series-name {
    color: #64748b;
    font-weight: 500;
}

.tooltip-series-value {
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}

.tooltip-series-value[data-trend="up"] {
    color: #10b981;
}

.tooltip-series-value[data-trend="down"] {
    color: #ef4444;
}

@keyframes tooltipFade {
    from {
        opacity: 0;
        transform: scale(0.95) translateY(5px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

@media (max-width: 768px) {
    .chart-container {
        padding: 1rem;
    }

    .chart-wrapper {
        height: 400px;
    }

    .tooltip {
        font-size: 0.75rem;
        padding: 0.75rem;
        min-width: 180px;
    }
}
</style>