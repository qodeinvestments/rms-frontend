<template>
    <div class="chart-wrapper">
        <div ref="chartContainer" class="chart-container"></div>
        <div class="chart-legend">
            <div v-for="(key, index) in keys" :key="key" class="legend-item" :title="`Line color for ${key}`"
                @click="toggleSeriesVisibility(index)">
                <span class="legend-color"
                    :style="{ backgroundColor: colors[index % colors.length], opacity: seriesVisibility[index] ? 1 : 0.5 }"></span>
                <span class="legend-label"
                    :style="{ color: colors[index % colors.length], opacity: seriesVisibility[index] ? 1 : 0.5 }">{{ key
                    }}</span>
            </div>
        </div>
    </div>
</template>

<script>
import { defineComponent, ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { createChart, ColorType } from 'lightweight-charts';
import moment from 'moment-timezone';

moment.tz.setDefault('Asia/Kolkata');

export default defineComponent({
    name: 'LightweightChart',
    props: {
        data: {
            type: Array,
            required: true,
        },
        keys: {
            type: Array,
            required: true,
        },
        height: {
            type: Number,
            default: 400,
        },
        colors: {
            type: Array,
            default: () => [
                '#2962FF', '#FF6D00', '#2E7D32', '#6A1B9A', '#00838F',
                '#AD1457', '#1565C0', '#EF6C00', '#283593', '#4527A0'
            ],
        },
    },
    setup(props) {
        const chartContainer = ref(null);
        const seriesVisibility = ref(props.keys.map(() => true));
        let chart = null;
        let series = [];

        const formattedData = computed(() =>
            props.data.map(dataSet =>
                Object.entries(dataSet || {}).map(([time, value]) => ({
                    time: moment(time).unix(),
                    value: parseFloat(value)
                }))
            )
        );

        const initChart = () => {
            if (!chartContainer.value) return;

            chart = createChart(chartContainer.value, {
                width: chartContainer.value.clientWidth,
                height: props.height,
                layout: {
                    background: { type: ColorType.Solid, color: 'white' },
                },
                grid: {
                    vertLines: { color: '#dedede' },
                    horzLines: { color: '#dedede' },
                },
                timeScale: {
                    timeVisible: true,
                    secondsVisible: true,
                    tickMarkFormatter: (time) => moment.unix(time).format('HH:mm:ss'),
                },
            });

            props.keys.forEach((key, index) => {
                const newSeries = chart.addLineSeries({
                    color: props.colors[index % props.colors.length],
                    lineWidth: 2,
                });
                series.push(newSeries);
                newSeries.setData(formattedData.value[index] || []);
            });
        };

        const updateChart = () => {
            if (!chart || series.length === 0) return;

            formattedData.value.forEach((dataSet, index) => {
                if (series[index]) {
                    series[index].setData(dataSet);
                }
            });
        };

        const debounce = (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        };

        const debouncedUpdateChart = debounce(updateChart, 100);

        const handleResize = debounce(() => {
            if (chart && chartContainer.value) {
                chart.applyOptions({
                    width: chartContainer.value.clientWidth,
                    height: props.height
                });
            }
        }, 100);

        const toggleSeriesVisibility = (index) => {
            seriesVisibility.value[index] = !seriesVisibility.value[index];
            if (seriesVisibility.value[index]) {
                series[index].applyOptions({ visible: true });
            } else {
                series[index].applyOptions({ visible: false });
            }
        };

        onMounted(() => {
            initChart();
            window.addEventListener('resize', handleResize);
        });

        onUnmounted(() => {
            if (chart) {
                chart.remove();
            }
            window.removeEventListener('resize', handleResize);
        });

        watch(() => props.data, debouncedUpdateChart, { deep: true });
        watch(() => props.height, handleResize);

        return {
            chartContainer,
            seriesVisibility,
            toggleSeriesVisibility,
        };
    },
});
</script>

<style scoped>
.chart-wrapper {
    width: 100%;
}

.chart-container {
    width: 100%;
    height: v-bind(height + 'px');
}

.chart-legend {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 20px;
}

.legend-item {
    display: flex;
    align-items: center;
    margin: 0 10px 10px 0;
    cursor: pointer;
}

.legend-color {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    margin-right: 5px;
}

.legend-label {
    font-size: 14px;
}
</style>
