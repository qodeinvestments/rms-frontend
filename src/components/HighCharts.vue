<template>
    <div>
        <highcharts :options="chartOptions"></highcharts>
    </div>
</template>

<script>
import Highcharts from 'highcharts';
import HighchartsVue from 'highcharts-vue';
import moment from 'moment-timezone';

export default {
    name: 'CombinedChart',
    props: {
        data: {
            type: Array,
            required: true,
        },
        keys: {
            type: Array,
            required: true,
        },
    },
    components: {
        highcharts: HighchartsVue.component,
    },
    computed: {
        chartOptions() {
            return {
                chart: {
                    zoomType: 'x',
                },
                title: {
                    text: 'Directional and Non-Directional Data',
                },
                xAxis: {
                    type: 'datetime',
                    labels: {
                        formatter: function () {
                            return moment(this.value).tz('Asia/Kolkata').format('HH:mm:ss');
                        }
                    },
                },
                yAxis: {
                    title: {
                        text: 'Values',
                    },
                },
                tooltip: {
                    formatter: function () {
                        return `<b>${this.series.name}</b><br/>${moment(this.x).tz('Asia/Kolkata').format('YYYY-MM-DD HH:mm:ss')}<br/>Value: ${this.y}`;
                    }
                },
                series: this.keys.map((key, index) => ({
                    name: key,
                    data: this.formatData(this.data[index]),
                })),
            };
        },
    },
    methods: {
        formatData(data) {
            return Object.keys(data).map(key => [
                moment.tz(key, 'Asia/Kolkata').valueOf(),
                data[key]
            ]);
        },
    },
};
</script>

<style scoped>
/* Add any necessary styling here */
</style>