<template>
    <div>
        <div class="drop-shadow-sm">
            <div :id="chartId" style="width: 100%; height: 400px;"></div>
        </div>
        <LineSelector :lines="lineNames" :visible-lines="visibleLines" @update-visibility="updateVisibility" />
    </div>
</template>

<script>
import Highcharts from 'highcharts'
import FullScreen from 'highcharts/modules/full-screen'
import Exporting from 'highcharts/modules/exporting'
import Accessibility from 'highcharts/modules/accessibility'
import LineSelector from './LineSelector.vue'

// Initialize the modules
FullScreen(Highcharts)
Exporting(Highcharts)
Accessibility(Highcharts)

export default {
    name: 'MultiLineChart',
    components: {
        LineSelector
    },
    props: {
        chartData: {
            type: Array,
            required: true,
            validator: function (value) {
                return Array.isArray(value) && value.every(item => typeof item === 'object');
            }
        },
        lineNames: {
            type: Array,
            default: () => []
        },
        chartType: {
            type: String,
            default: 'line'
        },
        yAxisTitle: {
            type: String,
            default: 'Values'
        },
        xAxisTitle: {
            type: String,
            default: 'Time'
        },
        chartTitle: {
            type: String,
            default: 'Multiple Line Chart (9:15 AM to 3:30 PM IST)'
        }
    },
    data() {
        return {
            chart: null,
            chartId: `chart-${Math.random().toString(36).substr(2, 9)}`,
            resizeListener: null,
            visibleLines: []
        }
    },
    computed: {
        autoColors() {
            return this.generateColors(this.chartData.length)
        }
    },
    watch: {
        chartData: {
            handler(newData) {
                this.$nextTick(() => {
                    this.updateChartData(newData);
                });
            },
            deep: true,
            immediate: true
        }
    },
    mounted() {
        this.$nextTick(() => {
            this.initChart()
            this.setupResizeListener()
        })
    },
    beforeUnmount() {
        this.cleanupChart()
    },
    methods: {
        initChart() {
            try {
                const options = this.getChartOptions();
                if (this.chart) {
                    this.chart.destroy();
                }
                this.chart = Highcharts.chart(this.chartId, options);
                this.visibleLines = this.lineNames.map((_, index) => index);
                this.updateChartData(this.chartData);
            } catch (error) {
                console.error('Error initializing chart:', error);
            }
        },
        updateChartData(newData) {
            if (!this.chart) {
                this.initChart();
                return;
            }

            newData.forEach((dataset, index) => {
                const processedData = this.processData(dataset);
                if (this.chart.series[index]) {
                    this.chart.series[index].setData(processedData, false);
                } else {
                    this.chart.addSeries({
                        name: this.lineNames[index] || `Dataset ${index + 1}`,
                        data: processedData,
                        color: this.autoColors[index]
                    }, false);
                }
            });

            // Remove extra series if necessary
            while (this.chart.series.length > newData.length) {
                this.chart.series[this.chart.series.length - 1].remove(false);
            }

            this.chart.redraw();
            this.updateVisibility(this.visibleLines);
        },
        getChartOptions() {
            return {
                chart: {
                    type: this.chartType,
                    zoomType: 'xy',
                    panning: { enabled: true, type: 'xy' },
                    panKey: 'shift',
                    animation: false
                },
                title: { text: this.chartTitle },
                xAxis: {
                    title: { text: this.xAxisTitle },
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
                yAxis: { title: { text: this.yAxisTitle } },
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
                legend: { enabled: false },
                plotOptions: {
                    series: {
                        states: {
                            hover: {
                                enabled: false
                            },
                            inactive: {
                                opacity: 1
                            }
                        }
                    }
                },
                series: [],
                colors: this.autoColors,
                exporting: {
                    enabled: true,
                    buttons: {
                        contextButton: {
                            menuItems: ["viewFullscreen", "printChart", "separator", "downloadPNG", "downloadJPEG", "downloadPDF", "downloadSVG"]
                        }
                    }
                },
                navigation: { buttonOptions: { enabled: true } },
                accessibility: {
                    enabled: true,
                    description: `Chart showing ${this.chartTitle}`,
                    keyboardNavigation: {
                        enabled: true
                    }
                }
            }
        },
        processData(dataset) {
            try {
                return Object.entries(dataset).map(([time, value]) => {
                    const [, timeString] = time.split(' ');
                    const [hours, minutes] = timeString.split(':').map(Number);
                    const minutesSince915 = (hours * 60 + minutes) - (9 * 60 + 15);
                    return [minutesSince915, value];
                }).filter(([minutes]) => minutes >= 0 && minutes <= (6 * 60 + 15));
            } catch (error) {
                console.error('Error processing chart data:', error);
                return [];
            }
        },
        setupResizeListener() {
            this.resizeListener = () => {
                if (this.chart) {
                    this.chart.reflow()
                }
            }
            window.addEventListener('resize', this.resizeListener)
        },
        cleanupChart() {
            if (this.chart) {
                this.chart.destroy()
            }
            if (this.resizeListener) {
                window.removeEventListener('resize', this.resizeListener)
            }
        },
        toggleFullscreen() {
            if (this.chart) {
                this.chart.fullscreen.toggle()
            }
        },
        generateColors(count) {
            const baseColors = [
                '#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9',
                '#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1'
            ]

            if (count <= baseColors.length) {
                return baseColors.slice(0, count)
            }

            const colors = [...baseColors]
            for (let i = baseColors.length; i < count; i++) {
                const hue = (i * 137.508) % 360
                colors.push(`hsl(${hue}, 70%, 60%)`)
            }
            return colors
        },
        updateVisibility(visibleIndexes) {
            if (!this.chart) return;

            this.chart.series.forEach((series, index) => {
                if (visibleIndexes.includes(index)) {
                    series.show();
                } else {
                    series.hide();
                }
            });
            this.visibleLines = visibleIndexes;
        },
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