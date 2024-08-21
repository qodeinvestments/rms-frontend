<template>
    <Bar :data="chartData" :options="chartOptions" />
</template>

<script>
import { defineComponent, ref, watch, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, BarElement, CategoryScale, LinearScale)

export default defineComponent({
    name: 'HistogramChart',
    components: { Bar },
    props: {
        dataArray: {
            type: Array,
            required: true
        }
    },
    setup(props) {
        const chartData = ref({
            labels: [],
            datasets: [{
                label: 'Value Frequency',  // Add your label here
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.6)'
            }]
        })

        const chartOptions = {
            responsive: true,
            plugins: {
                legend: {
                    display: true, // Ensure the legend is displayed
                    position: 'top', // You can also specify 'bottom', 'left', or 'right'
                },
                tooltip: {
                    enabled: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Seconds'
                    }
                }
            }
        }

        const updateHistogram = () => {
            const binSize = 0.1
            const bins = {}

            props.dataArray.forEach(value => {
                const binIndex = Math.floor(value / binSize)
                bins[binIndex] = (bins[binIndex] || 0) + 1
            })

            const labels = Object.keys(bins).map(key => (parseFloat(key) * binSize).toFixed(2))
            const data = Object.values(bins)

            chartData.value = {
                labels,
                datasets: [{
                    label: 'Value Frequency',  // Ensure the label is here too
                    data,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)'
                }]
            }
        }

        watch(() => props.dataArray, updateHistogram, { deep: true })

        onMounted(updateHistogram)

        return { chartData, chartOptions }
    }
})
</script>
