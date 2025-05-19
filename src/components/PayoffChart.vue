<template>
  <div class="payoff-chart-container">
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
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
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

const transformData = (rawData) => {
  const transformed = []
  
  // Process each data point
  rawData.forEach(item => {
    // Create a new object with Percentage instead of User
    const transformedItem = {
      Percentage: item.User, // Transform User to Percentage
      Upside: item.Upside,
      Downside: item.Downside
    }
    
    // Add downside point
    transformed.push({
      Percentage: `-${transformedItem.Percentage.replace('%', '')}%`,
      Value: transformedItem.Downside
    })
    
    // Add upside point
    transformed.push({
      Percentage: transformedItem.Percentage,
      Value: transformedItem.Upside
    })
  })
  
  // Sort by percentage
  return transformed.sort((a, b) => {
    const aVal = parseFloat(a.Percentage)
    const bVal = parseFloat(b.Percentage)
    return aVal - bVal
  })
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
  const transformedData = transformData(props.data)
  
  // Calculate the min and max x values
  const xValues = transformedData.map(item => parseFloat(item.Percentage))
  const minX = Math.min(...xValues)
  const maxX = Math.max(...xValues)
  const xAxisMin = Math.floor(minX * 1.1) // 10% padding
  const xAxisMax = Math.ceil(maxX * 1.1)  // 10% padding

  // Destroy existing chart if it exists
  if (chart.value) {
    chart.value.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  
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
    const currentMin = chart.value.scales.x.min
    const currentMax = chart.value.scales.x.max
    const totalRange = xAxisMax - xAxisMin
    const currentRange = currentMax - currentMin
    currentZoomLevel.value = totalRange / currentRange
  }
}

// Watch for data changes
watch(() => props.data, () => {
  initChart()
}, { deep: true })

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.destroy()
  }
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
</style> 