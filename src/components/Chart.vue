<template>
    <div class="chart-container drop-shadow-sm" ref="chartContainer">
        <Line :data="chartData" :options="chartOptions" ref="chart" />
        <button @click="resetZoom" class="reset-zoom">Reset Zoom</button>
        <button @click="toggleFullScreen" class="full-screen">
            {{ isFullScreen ? 'Exit Full Screen' : 'Full Screen' }}
        </button>
    </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, zoomPlugin)

export default {
    name: 'MTMChart',
    components: {
        Line
    },
    props: {
        data: {
            type: [Object, Array],
            required: true
        },
        lineNames: {
            type: Array,
            default: () => []
        }
    },
    computed: {
        chartData() {
            let datasets;
            let labels;

            if (Array.isArray(this.data)) {
                labels = Object.keys(this.data.reduce((acc, curr) => ({ ...acc, ...curr }), {}));
                datasets = this.data.map((dataset, index) => ({
                    label: this.lineNames[index] || `Dataset ${index + 1}`,
                    backgroundColor: this.getColor(index),
                    borderColor: this.getColor(index),
                    data: labels.map(label => dataset[label] || null),
                    fill: false,
                    pointRadius: 0,
                    borderWidth: 2
                }));
            } else {
                labels = Object.keys(this.data);
                datasets = [{
                    label: this.lineNames[0] || 'Dataset 1',
                    backgroundColor: this.getColor(0),
                    borderColor: this.getColor(0),
                    data: Object.values(this.data),
                    fill: false,
                    pointRadius: 0,
                    borderWidth: 2
                }];
            }

            return { labels, datasets };
        }
    },
    data() {
        return {
            isFullScreen: false,
            chartOptions: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true
                    }
                },
                elements: {
                    line: {
                        tension: 0,
                        spanGaps: true
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function (context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += `( ${context.parsed.y})`;
                                }
                                return label;
                            }
                        }
                    },
                    zoom: {
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'xy',
                        },
                        pan: {
                            enabled: true,
                            mode: 'xy',
                        },
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index',
                }
            }
        }
    },
    mounted() {
        document.addEventListener('fullscreenchange', this.fullScreenChanged);
        document.addEventListener('webkitfullscreenchange', this.fullScreenChanged);
        document.addEventListener('mozfullscreenchange', this.fullScreenChanged);
        document.addEventListener('MSFullscreenChange', this.fullScreenChanged);
    },
    beforeUnmount() {
        document.removeEventListener('fullscreenchange', this.fullScreenChanged);
        document.removeEventListener('webkitfullscreenchange', this.fullScreenChanged);
        document.removeEventListener('mozfullscreenchange', this.fullScreenChanged);
        document.removeEventListener('MSFullscreenChange', this.fullScreenChanged);
    },
    methods: {
        resetZoom() {
            if (this.$refs.chart && this.$refs.chart.chart) {
                this.$refs.chart.chart.resetZoom();
            }
        },
        getColor(index) {
            const colors = ['#000000', '#FF0000', '#00FF00', '#0000FF', '#FFA500', '#800080', '#008080'];
            return colors[index % colors.length];
        },
        toggleFullScreen() {
            if (!this.isFullScreen) {
                if (this.$refs.chartContainer.requestFullscreen) {
                    this.$refs.chartContainer.requestFullscreen();
                } else if (this.$refs.chartContainer.mozRequestFullScreen) {
                    this.$refs.chartContainer.mozRequestFullScreen();
                } else if (this.$refs.chartContainer.webkitRequestFullscreen) {
                    this.$refs.chartContainer.webkitRequestFullscreen();
                } else if (this.$refs.chartContainer.msRequestFullscreen) {
                    this.$refs.chartContainer.msRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.mozCancelFullScreen) {
                    document.mozCancelFullScreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
            }
        },
        fullScreenChanged() {
            this.isFullScreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
        },
    }
}
</script>

<style scoped>
.chart-container {
    position: relative;
    height: 40vh;
    width: 80vw;
    background-color: white;
}

.chart-container:fullscreen {
    height: 100vh;
    width: 100vw;
    background-color: white;
}

.reset-zoom,
.full-screen {
    position: absolute;
    padding: 5px 10px;
    background-color: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
}

.reset-zoom {
    top: 10px;
    right: 10px;
}

.full-screen {
    top: 10px;
    right: 110px;
}

.reset-zoom:hover,
.full-screen:hover {
    background-color: #e0e0e0;
}
</style>
