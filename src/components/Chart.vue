<template>
    <div class="chart-container">
        <Line :data="chartData" :options="chartOptions" />
    </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale)

export default {
    name: 'MTMChart',
    components: {
        Line
    },
    props: {
        data: {
            type: Object,
            required: true
        }
    },
    computed: {
        chartData() {
            return {
                labels: Object.keys(this.data),
                datasets: [
                    {
                        label: 'MTM Data',
                        backgroundColor: '#000000',
                        borderColor: '#000000',
                        data: Object.values(this.data),
                        fill: false,
                        pointRadius: 0, // Remove dots
                        borderWidth: 2 // Make the line a bit thicker
                    }
                ]
            }
        }
    },
    data() {
        return {
            chartOptions: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false, // Remove animation
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    }
}
</script>

<style scoped>
.chart-container {
    position: relative;
    height: 40vh;
    width: 80vw;
}
</style>