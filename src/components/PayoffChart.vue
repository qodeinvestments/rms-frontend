<template>
  <div class="payoff-chart-container">
    <div v-if="!data || !data.length" class="no-data-message">
      Select an account and strategy, then click "Generate Payoff Chart" to view the data
    </div>
    <template v-else>
      <div class="chart-toolbar">
        <button @click="zoomIn" class="toolbar-btn" title="Zoom In">
          <span>+</span>
        </button>
        <button @click="zoomOut" class="toolbar-btn" title="Zoom Out">
          <span>−</span>
        </button>
        <button @click="resetZoom" class="toolbar-btn" title="Reset Zoom">
          <span>↺</span>
        </button>
      </div>
      <canvas
        v-if="data && data.length"
        ref="chartCanvas"
        :key="data.length + '-' + (data[0]?.Percentage ?? '')"
      ></canvas>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'

// Register Chart.js components
Chart.register(...registerables, zoomPlugin)

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const chartCanvas = ref(null)
const chart = ref(null)
const currentZoomLevel = ref(1)

// Helper to safely destroy the chart
function destroyChart() {
  if (chart.value) {
    try {
      chart.value.destroy();
    } catch (e) {
      // ignore
    }
    chart.value = null;
  }
}

const zoomIn = () => {
  if (chart.value) {
    const zoomOptions = chart.value.options.plugins.zoom.zoom
    const currentMin = chart.value.scales.x.min
    const currentMax = chart.value.scales.x.max
    const range = currentMax - currentMin
    const newRange = range * 0.5 // Zoom in by 50%
    const center = (currentMin + currentMax) / 2
    
    chart.value.zoom(1.5)
    chart.value.update('none')
  }
}

const zoomOut = () => {
  if (chart.value) {
    const zoomOptions = chart.value.options.plugins.zoom.zoom
    const currentMin = chart.value.scales.x.min
    const currentMax = chart.value.scales.x.max
    const range = currentMax - currentMin
    const newRange = range * 2 // Zoom out by 100%
    const center = (currentMin + currentMax) / 2
    
    chart.value.zoom(0.5)
    chart.value.update('none')
  }
}

const resetZoom = () => {
  if (chart.value) {
    chart.value.resetZoom()
    currentZoomLevel.value = 1
  }
}

const initChart = () => {
  // Add detailed debugging logs
  console.log('Chart initialization attempt:', {
    hasData: !!props.data,
    dataLength: props.data?.length,
    hasCanvas: !!chartCanvas.value,
    data: props.data
  })

  // Check if we have valid data and canvas
  if (!props.data || !props.data.length || !chartCanvas.value) {
    console.warn('Chart initialization skipped:', {
      missingData: !props.data,
      emptyData: !props.data?.length,
      missingCanvas: !chartCanvas.value
    })
    return
  }

  // Defensive: get context
  const ctx = chartCanvas.value && chartCanvas.value.getContext('2d');
  if (!ctx) {
    console.error('No canvas context');
    return;
  }

  try {
    const transformedData = props.data
    
    // Validate data structure
    if (!transformedData.every(item => 
      typeof item.Percentage === 'string' && 
      typeof item.Value === 'number'
    )) {
      console.error('Invalid data structure:', transformedData)
      return
    }

    // Calculate the min and max x values
    const xValues = transformedData.map(item => parseFloat(item.Percentage))
    if (xValues.some(isNaN)) {
      console.error('Invalid percentage values in data:', xValues)
      return
    }

    const minX = Math.min(...xValues)
    const maxX = Math.max(...xValues)
    const xAxisMin = Math.floor(minX * 1.1) // 10% padding
    const xAxisMax = Math.ceil(maxX * 1.1)  // 10% padding

    // Destroy existing chart if it exists
    destroyChart();

    // Create new chart with error handling
    try {
      chart.value = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [{
            label: 'Payoff',
            data: transformedData.map(item => ({
              x: parseFloat(item.Percentage),
              y: item.Value
            })),
            borderColor: '#2196F3',
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
            borderWidth: 2.5,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: '#2196F3',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            tension: 0, // Straight lines
            fill: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  return new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: 'INR',
                    maximumFractionDigits: 0
                  }).format(context.parsed.y)
                },
                title: (context) => {
                  return `${context[0].parsed.x}%`
                }
              }
            },
            zoom: {
              pan: {
                enabled: true,
                mode: 'x',
                modifierKey: null
              },
              zoom: {
                wheel: {
                  enabled: true,
                  modifierKey: null
                },
                pinch: {
                  enabled: true
                },
                mode: 'x',
                drag: {
                  enabled: false
                },
                limits: {
                  min: 0.5,
                  max: 10
                }
              },
              limits: {
                x: {
                  min: xAxisMin,
                  max: xAxisMax
                }
              }
            }
          },
          scales: {
            x: {
              type: 'linear',
              min: xAxisMin,
              max: xAxisMax,
              title: {
                display: true,
                text: 'Percentage (%)',
                font: {
                  size: 14,
                  weight: 'bold'
                }
              },
              ticks: {
                callback: (value) => `${value}%`
              },
              grid: {
                color: '#e7e7e7'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Value (₹)',
                font: {
                  size: 14,
                  weight: 'bold'
                }
              },
              ticks: {
                callback: (value) => new Intl.NumberFormat('en-IN', {
                  style: 'currency',
                  currency: 'INR',
                  maximumFractionDigits: 0
                }).format(value)
              },
              grid: {
                color: '#e7e7e7'
              }
            }
          }
        }
      })

      // Add zoom level change listener
      chart.value.options.plugins.zoom.zoom.onZoom = () => {
        if (chart.value) {
          const currentMin = chart.value.scales.x.min
          const currentMax = chart.value.scales.x.max
          const totalRange = xAxisMax - xAxisMin
          const currentRange = currentMax - currentMin
          currentZoomLevel.value = totalRange / currentRange
        }
      }
    } catch (chartError) {
      console.error('Error creating chart:', chartError)
      destroyChart();
    }
  } catch (error) {
    console.error('Error in chart initialization:', error)
    destroyChart();
  }
}

// Update the watch to handle data changes more safely
watch(() => props.data, async (newData) => {
  destroyChart();
  console.log('Data prop changed:', {
    hasNewData: !!newData,
    newDataLength: newData?.length,
    newData: newData
  })
  // Only initialize if we have actual data
  if (newData && newData.length > 0) {
    console.log('Attempting to initialize chart with new data')
    await nextTick();
    console.log('nextTick callback executing, canvas state:', !!chartCanvas.value)
    initChart();
  } else {
    console.log('No data available yet, skipping chart initialization')
    // If we have an existing chart, destroy it
    destroyChart();
  }
}, { deep: true })

// Remove the onMounted initialization since we don't want to initialize without data
onMounted(() => {
  console.log('Component mounted, waiting for data...')
})

// Update onUnmounted to safely destroy chart
onUnmounted(() => {
  destroyChart();
})
</script>

<style scoped>
.payoff-chart-container {
  width: 100%;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
  height: 400px;
  position: relative;
}

.chart-toolbar {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  display: flex;
  gap: 4px;
  background: white;
  padding: 4px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbar-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #2196F3;
  transition: all 0.2s ease;
}

.toolbar-btn:hover {
  background: #f5f5f5;
  border-color: #2196F3;
}

.toolbar-btn:active {
  background: #e3f2fd;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}

.no-data-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-size: 1.1rem;
  text-align: center;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px dashed #ddd;
}
</style> 