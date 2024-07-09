<template>
    <div class="drop-shadow-sm">
        <div id="chart-container" style="width: 100%; height: 400px;"></div>
    </div>
</template>

<script>
import Highcharts from 'highcharts'
import FullScreen from 'highcharts/modules/full-screen'
import Exporting from 'highcharts/modules/exporting'

// Initialize the modules
FullScreen(Highcharts)
Exporting(Highcharts)

export default {
    name: 'MultiLineChart',
    props: {
        chartData: {
            type: Array,
            required: true
        },
        lineNames: {
            type: Array,
            default: () => []
        }
    },
    data() {
        return {
            chart: null
        }
    },
    mounted() {
        this.initChart()
    },
    watch: {
        chartData: {
            handler: 'updateChart',
            deep: true
        }
    },
    methods: {
        initChart() {
            if (!this.chartData || this.chartData.length === 0) {
                console.warn('No chart data available');
                return;
            }

            const series = this.chartData.map((dataset, index) => ({
                name: this.lineNames[index] || `Dataset ${index + 1}`,
                data: this.processData(dataset)
            }));

            this.chart = Highcharts.chart('chart-container', {
                chart: {
                    type: 'line',
                    zoomType: 'xy',
                    panning: {
                        enabled: true,
                        type: 'xy'
                    },
                    panKey: 'shift',
                    animation: false // Disable animation
                },
                title: {
                    text: 'Multiple Line Chart (9:15 AM to 3:30 PM IST)'
                },
                xAxis: {
                    title: {
                        text: 'Time'
                    },
                    labels: {
                        formatter: function () {
                            const totalMinutes = this.value + (9 * 60 + 15)
                            const hours = Math.floor(totalMinutes / 60)
                            const minutes = totalMinutes % 60
                            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
                        }
                    },
                    tickInterval: 60,
                    min: 0,
                    max: 6 * 60 + 15
                },
                yAxis: {
                    title: {
                        text: 'Values'
                    }
                },
                tooltip: {
                    shared: true,
                    crosshairs: true,
                    formatter: function () {
                        const totalMinutes = this.x + (9 * 60 + 15)
                        const hours = Math.floor(totalMinutes / 60)
                        const minutes = totalMinutes % 60
                        const time = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`

                        let tooltipContent = `<b>${time}</b><br/>`
                        this.points.forEach(point => {
                            tooltipContent += `${point.series.name}: <b>${point.y}</b><br/>`
                        })
                        return tooltipContent
                    }
                },
                legend: {
                    enabled: true
                },
                series: series,
                exporting: {
                    enabled: true,
                    buttons: {
                        contextButton: {
                            menuItems: ["viewFullscreen", "printChart", "separator", "downloadPNG", "downloadJPEG", "downloadPDF", "downloadSVG"]
                        }
                    }
                },
                navigation: {
                    buttonOptions: {
                        enabled: true
                    }
                }
            })
        },

        updateChart() {
            if (this.chart) {
                this.chartData.forEach((dataset, index) => {
                    const data = this.processData(dataset);
                    if (this.chart.series[index]) {
                        this.chart.series[index].setData(data, false);
                    } else {
                        this.chart.addSeries({
                            name: this.lineNames[index] || `Dataset ${index + 1}`,
                            data: data
                        }, false);
                    }
                });
                this.chart.redraw();
            } else {
                this.initChart();
            }
        },
        processData(dataset) {
            try {
                return Object.entries(dataset).map(([time, value]) => {
                    const [hours, minutes] = time.split(' ')[1].split(':').map(Number);
                    if (isNaN(hours) || isNaN(minutes)) {
                        throw new Error(`Invalid time format: ${time}`);
                    }
                    const minutesSince915 = (hours * 60 + minutes) - (9 * 60 + 15);
                    return [minutesSince915, value];
                }).filter(([minutes]) => minutes >= 0 && minutes <= (6 * 60 + 15));
            } catch (error) {
                console.error('Error processing chart data:', error);
                return [];
            }
        },
        toggleFullscreen() {
            if (this.chart) {
                this.chart.fullscreen.toggle()
            }
        }
    }
}
</script>

<style scoped>
.fullscreen-btn {
    margin-top: 10px;
    padding: 5px 10px;
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
}
</style>