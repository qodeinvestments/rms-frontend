<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { createChart } from 'lightweight-charts';

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  series: {
    type: Array,
    required: true,
    default: () => []
  }
});

const chartContainer = ref(null);
let chart = null;
let chartSeries = {};

const initChart = () => {
  if (!chartContainer.value) return;

  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 400,
    layout: {
      background: { color: '#ffffff' },
      textColor: '#333',
    },
    grid: {
      vertLines: { color: '#f0f0f0' },
      horzLines: { color: '#f0f0f0' },
    },
    rightPriceScale: {
      visible: true,
      borderColor: '#f0f0f0',
    },
    leftPriceScale: {
      visible: true,
      borderColor: '#f0f0f0',
    },
    timeScale: {
      borderColor: '#f0f0f0',
      timeVisible: true,
      secondsVisible: false,
    },
  });

  // Create series dynamically based on configuration
  props.series.forEach(seriesConfig => {
    chartSeries[seriesConfig.field] = chart.addLineSeries({
      color: seriesConfig.color || '#2962FF',
      lineWidth: 2,
      priceScaleId: seriesConfig.priceScaleId || 'left',
      title: seriesConfig.title || seriesConfig.field,
    });
  });

  updateChartData();
};

const updateChartData = () => {
  if (!chart || !props.data.length) return;

  // Update each series with its corresponding data
  props.series.forEach(seriesConfig => {
    const seriesData = props.data.map(item => ({
      time: new Date(item.timestamp).getTime() / 1000,
      value: item[seriesConfig.field]
    }));
    
    chartSeries[seriesConfig.field].setData(seriesData);
  });

  chart.timeScale().fitContent();
};

// Handle window resize
const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.applyOptions({
      width: chartContainer.value.clientWidth
    });
  }
};

// Watch for data changes
watch(() => props.data, () => {
  updateChartData();
}, { deep: true });

onMounted(() => {
  initChart();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (chart) {
    chart.remove();
    chart = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<template>
  <div ref="chartContainer" class="chart-container"></div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
  margin: 20px 0;
}
</style>