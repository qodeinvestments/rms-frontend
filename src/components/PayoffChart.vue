<template>
  <div class="payoff-chart-container">
    <div id="payoff-chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import ApexCharts from 'apexcharts'

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const chart = ref(null)

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

const initChart = () => {
  const transformedData = transformData(props.data)
  
  const options = {
    series: [{
      name: 'Payoff',
      data: transformedData.map(item => ({
        x: parseFloat(item.Percentage),
        y: item.Value
      }))
    }],
    chart: {
      type: 'line',
      height: 400,
      toolbar: {
        show: true
      },
      zoom: {
        enabled: true
      },
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800,
        animateGradually: {
          enabled: true,
          delay: 150
        },
        dynamicAnimation: {
          enabled: true,
          speed: 350
        }
      }
    },
    stroke: {
      curve: 'smooth',
      width: 3,
      colors: ['#2196F3']
    },
    grid: {
      borderColor: '#e7e7e7',
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5
      },
      padding: {
        top: 20,
        right: 20,
        bottom: 20,
        left: 20
      }
    },
    markers: {
      size: 6,
      colors: ['#2196F3'],
      strokeColors: '#fff',
      strokeWidth: 2,
      hover: {
        size: 8
      }
    },
    xaxis: {
      title: {
        text: 'Percentage (%)',
        style: {
          fontSize: '14px',
          fontWeight: 600,
          color: '#263238'
        }
      },
      labels: {
        formatter: (value) => `${value}%`,
        style: {
          colors: '#263238'
        }
      },
      axisBorder: {
        show: true,
        color: '#e7e7e7'
      },
      axisTicks: {
        show: true,
        color: '#e7e7e7'
      }
    },
    yaxis: {
      title: {
        text: 'Value (₹)',
        style: {
          fontSize: '14px',
          fontWeight: 600,
          color: '#263238'
        }
      },
      labels: {
        formatter: (value) => {
          return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
          }).format(value)
        },
        style: {
          colors: '#263238'
        }
      },
      axisBorder: {
        show: true,
        color: '#e7e7e7'
      },
      axisTicks: {
        show: true,
        color: '#e7e7e7'
      }
    },
    tooltip: {
      theme: 'light',
      x: {
        formatter: (value) => `${value}%`
      },
      y: {
        formatter: (value) => new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          maximumFractionDigits: 0
        }).format(value)
      }
    },
    theme: {
      mode: 'light',
      palette: 'palette1'
    },
    annotations: {
      points: [{
        x: 0,
        y: 0,
        marker: {
          size: 4,
          fillColor: '#fff',
          strokeColor: '#2196F3',
          radius: 2
        }
      }]
    }
  }

  if (chart.value) {
    chart.value.destroy()
  }

  chart.value = new ApexCharts(document.querySelector("#payoff-chart"), options)
  chart.value.render()
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
}

#payoff-chart {
  width: 100%;
  height: 400px;
}
</style> 