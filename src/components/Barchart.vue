<template>
  <div>
    <highcharts :options="chartOptions" @rendered="onChartRendered"></highcharts>
  </div>
</template>

<script>
import { defineComponent, ref, watch, onMounted } from 'vue';
import Highcharts from 'highcharts';

export default defineComponent({
  name: 'BarChart',
  props: {
    chartData: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const chartRef = ref(null);
    const chartOptions = ref({
      chart: {
        type: 'bar'
      },
      title: {
        text: 'NIFTY Data Bar Chart'
      },
      xAxis: {
        categories: Object.keys(props.chartData)
      },
      yAxis: {
        title: {
          text: 'Values'
        }
      },
      series: [
        {
          name: 'Data',
          data: Object.values(props.chartData)
        }
      ]
    });

    const onChartRendered = (chart) => {
      chartRef.value = chart;
    };

    watch(
      () => props.chartData,
      (newData) => {
        if (chartRef.value) {
          const categories = Object.keys(newData);
          const data = Object.values(newData);

          chartRef.value.xAxis[0].setCategories(categories, false);
          chartRef.value.series[0].setData(data, true);
        }
      },
      { deep: true }
    );

    return {
      chartOptions,
      onChartRendered
    };
  }
});
</script>
