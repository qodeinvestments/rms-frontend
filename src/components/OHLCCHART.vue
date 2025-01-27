<!-- OHLCChart.vue -->
<template>
    <div class="chart-wrapper">
      <div class="chart-header">
        <div class="chart-title-section">
          <h2 class="chart-title">Market Data</h2>
          <div class="indicator-selector">
            <a-select
              v-model:value="selectedIndicators"
              mode="multiple"
              placeholder="Select Indicators"
              style="width: 250px"
              :options="indicatorOptions"
              :maxTagCount="3"
              @change="handleIndicatorChange"
            >
            </a-select>
            <a-button 
              v-if="selectedIndicators.length > 0"
              type="text"
              @click="showSettingsModal"
              class="settings-button"
            >
              <template #icon><setting-outlined /></template>
            </a-button>
          </div>
        </div>
        <div class="chart-controls">
          <button 
            v-for="period in timePeriods" 
            :key="period"
            @click="changePeriod(period)"
            :class="['period-button', { active: selectedPeriod === period }]"
          >
            {{ period }}
          </button>
        </div>
      </div>
      
      <div ref="chartContainer" class="chart-container">
        <div v-if="!data || Object.keys(data).length === 0" class="loading-overlay">
          <div class="loading-spinner"></div>
          <span>Loading chart data...</span>
        </div>
      </div>
  
      <!-- Indicator Settings Modal -->
      <a-modal
        v-model:visible="isSettingsVisible"
        title="Indicator Settings"
        @ok="handleSettingsSave"
        width="600px"
      >
        <div v-for="indicator in selectedIndicators" :key="indicator" class="indicator-settings">
          <h3>{{ getIndicatorName(indicator) }}</h3>
          <div class="settings-group">
            <template v-if="indicator === 'psar'">
              <a-form-item label="Acceleration Factor">
                <a-input-number 
                  v-model:value="indicatorSettings.psar.accelerationFactor" 
                  :min="0.01" 
                  :max="0.1" 
                  :step="0.01"
                />
              </a-form-item>
              <a-form-item label="Maximum AF">
                <a-input-number 
                  v-model:value="indicatorSettings.psar.maxAF" 
                  :min="0.1" 
                  :max="0.5" 
                  :step="0.05"
                />
              </a-form-item>
            </template>
            <template v-if="indicator === 'ma'">
              <a-form-item label="Period">
                <a-input-number 
                  v-model:value="indicatorSettings.ma.period" 
                  :min="1" 
                  :max="200"
                />
              </a-form-item>
              <a-form-item label="Type">
                <a-select v-model:value="indicatorSettings.ma.type">
                  <a-select-option value="sma">Simple</a-select-option>
                  <a-select-option value="ema">Exponential</a-select-option>
                </a-select>
              </a-form-item>
            </template>
            <!-- Add more indicator settings templates as needed -->
          </div>
        </div>
      </a-modal>
    </div>
  </template>
  <script setup>
  import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
  import { createChart } from 'lightweight-charts'
  import { SettingOutlined } from '@ant-design/icons-vue'
  
  const props = defineProps({
    data: {
      type: Object,
      required: true
    }
  })
  
  const chartContainer = ref(null)
  const selectedPeriod = ref('1D')
  const timePeriods = ['1H', '1D', '1W', '1M']
  const isSettingsVisible = ref(false)
  let chart = null
  let candlestickSeries = null
  let psarSeries = null
  
  // Indicator related data
  const selectedIndicators = ref([])
  const indicatorOptions = [
    { value: 'psar', label: 'Parabolic SAR' },
    { value: 'ma', label: 'Moving Average' },
    { value: 'bollinger', label: 'Bollinger Bands' },
    { value: 'rsi', label: 'RSI' }
  ]
  
  const indicatorSettings = ref({
    psar: {
      accelerationFactor: 0.02,
      maxAF: 0.2
    },
    ma: {
      period: 20,
      type: 'sma'
    },
    bollinger: {
      period: 20,
      stdDev: 2
    },
    rsi: {
      period: 14
    }
  })
  
  const getIndicatorName = (indicator) => {
    return indicatorOptions.find(opt => opt.value === indicator)?.label || indicator
  }
  
  const showSettingsModal = () => {
    isSettingsVisible.value = true
  }
  
  const handleSettingsSave = () => {
    isSettingsVisible.value = false
    updateChartData() // Refresh chart with new settings
  }
  
  const handleIndicatorChange = (values) => {
    selectedIndicators.value = values
    updateChartData()
  }

  
  const createChartInstance = () => {
    chart = createChart(chartContainer.value, {
      width: chartContainer.value.clientWidth,
      height: 500,
      layout: {
        background: { 
          type: 'solid', 
          color: '#ffffff' 
        },
        textColor: '#333333',
        fontSize: 12,
        fontFamily: 'Poppins, sans-serif',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          width: 1,
          color: '#2962FF',
          style: 0,
          labelBackgroundColor: '#2962FF',
        },
        horzLine: {
          width: 1,
          color: '#2962FF',
          style: 0,
          labelBackgroundColor: '#2962FF',
        },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: '#f0f0f0',
      },
      rightPriceScale: {
        borderColor: '#f0f0f0',
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    })
  
    candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
      priceFormat: {
        type: 'price',
        precision: 2,
      },
    })
  
    psarSeries = chart.addLineSeries({
      color: '#2962FF',
      lineWidth: 2,
      priceLineVisible: false,
      crosshairMarkerVisible: true,
      crosshairMarkerRadius: 4,
      crosshairMarkerBorderColor: '#2962FF',
      crosshairMarkerBackgroundColor: '#ffffff',
    })
  }
  
// Update the updateChartData function to handle indicators
const updateChartData = () => {
  if (!props.data || !props.data.timestamp) return

  const transformedData = Object.keys(props.data.timestamp).map(index => ({
    time: new Date(props.data.timestamp[index]).getTime() / 1000,
    open: props.data.open[index],
    high: props.data.high[index],
    low: props.data.low[index],
    close: props.data.close[index]
  }))

  candlestickSeries.setData(transformedData)

  // Update indicators based on selection
  if (selectedIndicators.value.includes('psar')) {
    const psarData = Object.keys(props.data.timestamp).map(index => ({
      time: new Date(props.data.timestamp[index]).getTime() / 1000,
      value: props.data.psar[index]
    }))
    psarSeries.setData(psarData)
  }

  chart.timeScale().fitContent()
}
  const handleResize = () => {
    if (chart && chartContainer.value) {
      chart.applyOptions({
        width: chartContainer.value.clientWidth,
      })
    }
  }
  
  const changePeriod = (period) => {
    selectedPeriod.value = period
    // Implement period change logic here
  }
  
  // Watch for data changes
  watch(() => props.data, () => {
    if (chart) {
      updateChartData()
    }
  }, { deep: true })
  
  onMounted(() => {
    if (chartContainer.value) {
      createChartInstance()
      updateChartData()
      window.addEventListener('resize', handleResize)
    }
  })
  
  onBeforeUnmount(() => {
    if (chart) {
      chart.remove()
      window.removeEventListener('resize', handleResize)
    }
  })
  </script>
  
  <style scoped>


.chart-title-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.indicator-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-button {
  padding: 4px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.indicator-settings {
  margin-bottom: 24px;
}

.indicator-settings h3 {
  margin-bottom: 16px;
  color: #1a1a1a;
  font-size: 1rem;
}

.settings-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}
  .chart-wrapper {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    padding: 20px;
    margin: 20px 0;
  }
  
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .chart-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
  }
  
  .chart-controls {
    display: flex;
    gap: 8px;
  }
  
  .period-button {
    padding: 6px 12px;
    border: 1px solid #e5e7eb;
    background: #ffffff;
    border-radius: 6px;
    font-size: 0.875rem;
    color: #4b5563;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .period-button:hover {
    background: #f9fafb;
  }
  
  .period-button.active {
    background: #2962FF;
    color: #ffffff;
    border-color: #2962FF;
  }
  
  .chart-container {
    position: relative;
    height: 500px;
    width: 100%;
  }
  
  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.9);
    gap: 12px;
  }
  
  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #2962FF;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  </style>