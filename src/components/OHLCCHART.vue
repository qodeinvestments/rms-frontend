<!-- OHLCChart.vue -->
<template>
  <div class="chart-wrapper">
    <div v-if="isLoading" class="chart-loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <span class="loading-text">Loading market data...</span>
      </div>
    </div>

    <div  class="chart-header">
      <h2 class="chart-title">Market Data</h2>
      <div class="controls-container">
        <!-- Symbol Dropdown -->
        <div class="dropdown-container" @click="toggleSymbolDropdown">
          <div class="selected-value">
            {{ config.symbol || 'Select Symbol' }}
            <span class="dropdown-arrow" :class="{ 'rotate': isSymbolDropdownOpen }">▼</span>
          </div>
          <div v-if="isSymbolDropdownOpen" class="dropdown-menu">
            <div 
              v-for="symbol in symbols" 
              :key="symbol"
              class="dropdown-item"
              @click="selectSymbol(symbol)"
            >
              {{ symbol }}
            </div>
          </div>
        </div>

        <!-- Timeframe Dropdown -->
        <div class="dropdown-container" @click="toggleTimeframeDropdown">
          <div class="selected-value">
            {{ config.timeframe || 'Select Timeframe' }}
            <span class="dropdown-arrow" :class="{ 'rotate': isTimeframeDropdownOpen }">▼</span>
          </div>
          <div v-if="isTimeframeDropdownOpen" class="dropdown-menu">
            <div 
              v-for="tf in timeframes" 
              :key="tf"
              class="dropdown-item"
              @click="selectTimeframe(tf)"
            >
              {{ tf }}
            </div>
          </div>
        </div>

        <!-- Indicator Settings Button -->
        <button 
          @click="showIndicatorModal"
          class="settings-button"
        >
          <span class="settings-icon">⚙</span>
          Indicators
        </button>


        <!-- Apply config -->
        <button 
          @click="submitConfig"
          class="submit-button"
        >
          Apply
        </button>
      </div>
    </div>
    
    <div ref="chartContainer" class="chart-container">
      <!-- Price Display -->
      <div class="price-display">
        <span class="price-item">O: <span class="price-value">-</span></span>
        <span class="price-item">H: <span class="price-value">-</span></span>
        <span class="price-item">L: <span class="price-value">-</span></span>
        <span class="price-item">C: <span class="price-value">-</span></span>
        <span v-if="indicators.psar.enabled" class="price-item">
          <span class="indicator-dot psar-dot"></span>
          PSAR: <span class="price-value">-</span>
        </span>
        <span v-if="indicators.ma.enabled" class="price-item">
          <span class="indicator-dot ma-dot"></span>
          MA: <span class="price-value">-</span>
        </span>
      </div>

      <!-- Loading State -->
      <div v-if="!data || data.length === 0" class="loading-overlay">
        <div class="loading-spinner"></div>
      </div>
    </div>

    <!-- Indicator Settings Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="isIndicatorModalOpen" class="modal-wrapper">
          <div class="modal-backdrop" @click="closeIndicatorModal"></div>
          <div class="modal-container">
            <div class="modal-content">
              <div class="modal-header">
                <h3>Indicator Settings</h3>
                <button class="close-button" @click="closeIndicatorModal">×</button>
              </div>
              
              <div class="modal-body">
                <!-- PSAR Settings -->
                <div class="indicator-group">
                  <label class="indicator-checkbox">
                    <input 
                      type="checkbox"
                      v-model="indicators.psar.enabled"
                    />
                    <span class="checkbox-label">Parabolic SAR</span>
                  </label>
                  
                  <div v-if="indicators.psar.enabled" class="indicator-settings">
                    <!-- PSAR Variation at the top -->
                    <div class="setting-group">
                      <label for="psarLine">PSAR Variation</label>
                      <select 
                        id="psarLine" 
                        v-model="indicators.psar.selectedPsarLine"
                        class="number-input"
                      >
                        <option 
                          v-for="line in psarLines" 
                          :key="line" 
                          :value="line"
                        >
                          {{ line }}
                        </option>
                      </select>
                    </div>

                    <!-- AF Settings - only shown when custom is selected -->
                    <div v-if="indicators.psar.selectedPsarLine === 'custom'" class="af-settings">
                      <div class="setting-group">
                        <label>Acceleration Factor</label>
                        <input 
                          type="number"
                          v-model="indicators.psar.af"
                          step="0.001"
                          class="number-input"
                        />
                      </div>
                      <div class="setting-group">
                        <label>Maximum AF</label>
                        <input 
                          type="number"
                          v-model="indicators.psar.maxAf"
                          step="0.001"
                          class="number-input"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <!-- MA Settings -->
                <div class="indicator-group">
                  <label class="indicator-checkbox">
                    <input 
                      type="checkbox"
                      v-model="indicators.ma.enabled"
                    />
                    <span class="checkbox-label">Moving Average</span>
                  </label>
                  
                  <div v-if="indicators.ma.enabled" class="indicator-settings">
                    <div class="setting-group">
                      <label>Period</label>
                      <input 
                        type="number"
                        v-model="indicators.ma.period"
                        class="number-input"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="modal-footer">
                <button class="cancel-button" @click="closeIndicatorModal">Cancel</button>
                <button class="save-button" @click="saveIndicatorSettings">Save</button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { createChart } from 'lightweight-charts'

// Emits
const emit = defineEmits(['submit-config'])

// Props
const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => [],
  }
})

// Chart refs and instances
const chartContainer = ref(null)
let chart = null
let candlestickSeries = null
let psarSeries = null
let maSeries = null
let lastCandleData = null
let lastPsarValue = null
let lastMaValue = null

// Loading and UI State
const isLoading = ref(false)
const isSymbolDropdownOpen = ref(false)
const isTimeframeDropdownOpen = ref(false)
const isIndicatorModalOpen = ref(false)

// Available options
const symbols = ['NIFTY', 'SENSEX' ,'BANKNIFTY' , 'MIDCAPNIFTY' ,'FINNIFTY']
const timeframes = ['1m', '5m', '15m', '1h', '1d']

// For PSAR line selection:
const psarLines = [
  'psar1',
  'psar2',
  'psar3',
  'psar4',
  'psar5',
  'psar6',
  'psar7',
  'psar8',
  'psar9',
  'psar10',
  'psar11',
  'psar12',
  'psar13',
  'custom'
]

// Configuration state
const config = ref({
  symbol: 'NIFTY',
  timeframe: '5m',
  indicators: []
})

// Indicator state
const indicators = ref({
  psar: {
    enabled: false,
    af: 0.001,
    maxAf: 0.001,
    selectedPsarLine: 'psar1'
  },
  ma: {
    enabled: false,
    period: 20
  }
})

// Dropdown handlers
const toggleSymbolDropdown = () => {
  isSymbolDropdownOpen.value = !isSymbolDropdownOpen.value
  isTimeframeDropdownOpen.value = false
}

const toggleTimeframeDropdown = () => {
  isTimeframeDropdownOpen.value = !isTimeframeDropdownOpen.value
  isSymbolDropdownOpen.value = false
}

const selectSymbol = (symbol) => {
  config.value.symbol = symbol
  isSymbolDropdownOpen.value = false
}

const selectTimeframe = (tf) => {
  config.value.timeframe = tf
  isTimeframeDropdownOpen.value = false
}

// Modal handlers
const showIndicatorModal = () => {
  isIndicatorModalOpen.value = true
}

const closeIndicatorModal = () => {
  isIndicatorModalOpen.value = false
}
const saveIndicatorSettings = () => {
  updateIndicators()
  closeIndicatorModal()
  // Force the chart to re-check which PSAR line we want
  updateChartData()
}
// Price display updates
const updatePriceDisplay = (candleData, psarValue, maValue) => {
  const priceDisplay = document.querySelector('.price-display')
  if (!priceDisplay) return

  const priceValues = priceDisplay.querySelectorAll('.price-value')
  if (!candleData) {
    priceValues.forEach(value => value.textContent = '-')
    return
  }

  // Update OHLC values
  priceValues[0].textContent = candleData.open?.toFixed(2) || '-'
  priceValues[1].textContent = candleData.high?.toFixed(2) || '-'
  priceValues[2].textContent = candleData.low?.toFixed(2) || '-'
  priceValues[3].textContent = candleData.close?.toFixed(2) || '-'

  // Update indicator values if they exist
  if (indicators.value.psar.enabled && priceValues[4]) {
    priceValues[4].textContent = psarValue?.value?.toFixed(2) || '-'
  }
  if (indicators.value.ma.enabled && priceValues[5]) {
    priceValues[5].textContent = maValue?.value?.toFixed(2) || '-'
  }
}


// Update and submit config
const updateIndicators = () => {
  config.value.indicators = []
  
  if (indicators.value.psar.enabled) {
    config.value.indicators.push({
      name: 'Psar',
      setting: {
        af: Number(indicators.value.psar.af),
        'max-af': Number(indicators.value.psar.maxAf),
        // Let our backend or other code know which psar line is selected
        psarLine: indicators.value.psar.selectedPsarLine
      }
    })
  }
  
  if (indicators.value.ma.enabled) {
    config.value.indicators.push({
      name: 'MA',
      setting: {
        period: Number(indicators.value.ma.period)
      }
    })
  }
}

// Update submitConfig
const submitConfig = () => {
  updateIndicators()
  isLoading.value = true
  emit('submit-config', config.value)
}

const createChartInstance = () => {
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 500,
    layout: {
      background: { type: 'solid', color: '#ffffff' },
      textColor: '#333333',
    },
    grid: {
      vertLines: { color: '#f0f0f0' },
      horzLines: { color: '#f0f0f0' },
    },
    crosshair: {
      mode: 1,
      vertLine: {
        labelVisible: true,
        labelBackgroundColor: '#2962FF',
      },
      horzLine: {
        labelVisible: true,
        labelBackgroundColor: '#2962FF',
      },
    },
    timeScale: {
      timeVisible: true,
      borderColor: '#f0f0f0',
    },
  })

  // Main candlestick series
  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderVisible: false,
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
  })

  // Subscribe to crosshair movement
  chart.subscribeCrosshairMove((param) => {
    if (!param || param.time === undefined) {
      updatePriceDisplay(lastCandleData, lastPsarValue, lastMaValue)
      return
    }

    const candleData = param.seriesData.get(candlestickSeries)
    const psarValue = psarSeries ? param.seriesData.get(psarSeries) : null
    const maValue = maSeries ? param.seriesData.get(maSeries) : null

    if (candleData) lastCandleData = candleData
    if (psarValue) lastPsarValue = psarValue
    if (maValue) lastMaValue = maValue

    updatePriceDisplay(candleData, psarValue, maValue)
  })
}

// Update chart data to the new array-of-objects format
const updateChartData = () => {
  if (!Array.isArray(props.data) || props.data.length === 0) return

  // Transform and set candlestick data
  const transformedData = props.data.map(item => {
    // Convert timestamp to Unix seconds if it's a string or Date object
    const timestamp = typeof item.timestamp === 'string' 
      ? new Date(item.timestamp).getTime() / 1000
      : item.timestamp instanceof Date 
        ? item.timestamp.getTime() / 1000
        : item.timestamp

    return {
      time: timestamp,
      open: item.o,
      high: item.h,
      low: item.l,
      close: item.c
    }
  })
  candlestickSeries.setData(transformedData)

  // Handle PSAR
  const psarKey = indicators.value.psar.selectedPsarLine // e.g. 'psar1'
  if (
    indicators.value.psar.enabled &&
    props.data.some(d => d[psarKey] !== undefined)
  ) {
    // If psarSeries is already on the chart, remove it first
    if (psarSeries) {
      chart.removeSeries(psarSeries)
      psarSeries = null
    }
    // Create new PSAR series for the selected line
    psarSeries = chart.addLineSeries({
      color: '#2962FF',
      lineWidth: 1, // Changed to match your Python plot
      pointsVisible: false, // Changed to match your Python plot
      title: psarKey.toUpperCase()
    })
    const psarData = props.data.map(item => {
      const timestamp = typeof item.timestamp === 'string' 
        ? new Date(item.timestamp).getTime() / 1000
        : item.timestamp instanceof Date 
          ? item.timestamp.getTime() / 1000
          : item.timestamp

      return {
        time: timestamp,
        value: item[psarKey]
      }
    })
    psarSeries.setData(psarData)
  } else if (psarSeries) {
    // Remove PSAR series if no psar data or psar not enabled
    chart.removeSeries(psarSeries)
    psarSeries = null
  }

  // Handle MA
  if (
    indicators.value.ma.enabled &&
    props.data.some(d => d.ma !== undefined)
  ) {
    if (!maSeries) {
      maSeries = chart.addLineSeries({
        color: '#FF9800',
        lineWidth: 2,
        title: 'MA'
      })
    }
    const maData = props.data.map(item => {
      const timestamp = typeof item.timestamp === 'string' 
        ? new Date(item.timestamp).getTime() / 1000
        : item.timestamp instanceof Date 
          ? item.timestamp.getTime() / 1000
          : item.timestamp

      return {
        time: timestamp,
        value: item.ma
      }
    })
    maSeries.setData(maData)
  } else if (maSeries) {
    // Remove MA series if none found or MA not enabled
    chart.removeSeries(maSeries)
    maSeries = null
  }

  chart.timeScale().fitContent()
}

const handleClickOutside = (e) => {
  if (!e.target.closest('.dropdown-container')) {
    isSymbolDropdownOpen.value = false
    isTimeframeDropdownOpen.value = false
  }
}

onMounted(() => {
  if (chartContainer.value) {
    isLoading.value = true
    createChartInstance()
    updateChartData()
    window.addEventListener('resize', handleResize)
    document.addEventListener('click', handleClickOutside)
    setTimeout(() => {
      isLoading.value = false
    }, 300)
  }
})

// Cleanup function
onBeforeUnmount(() => {
  if (chart) {
    chart.unsubscribeCrosshairMove()
    if (psarSeries) {
      chart.removeSeries(psarSeries)
      psarSeries = null
    }
    if (maSeries) {
      chart.removeSeries(maSeries)
      maSeries = null
    }
    chart.remove()
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('click', handleClickOutside)
  }
})

const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.applyOptions({ width: chartContainer.value.clientWidth })
  }
}

watch(() => props.data, () => {
    if (chart) {
      isLoading.value = true
      try {
        updateChartData()
      } finally {
      // Add a small delay to make the transition smoother
        setTimeout(() => {
          isLoading.value = false
        }, 300)
      }
    }
}, { deep: true })




</script>
<!-- OHLCChart.vue styles -->
<style scoped>
.chart-wrapper {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 24px;
  margin: 20px 0;
  position: relative;
  overflow: hidden;
}

.chart-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 50;
  backdrop-filter: blur(4px);
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-text {
  color: #2962FF;
  font-weight: 500;
  font-size: 1.1rem;
  animation: pulse 1.5s infinite ease-in-out;
}

.chart-header {
  margin-bottom: 24px;
}

.chart-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 20px 0;
}

.controls-container {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

/* Dropdown Styles */
.dropdown-container {
  position: relative;
  min-width: 160px;
  cursor: pointer;
  z-index: 20;
}

.selected-value {
  padding: 10px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.selected-value:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.dropdown-arrow {
  font-size: 0.8rem;
  transition: transform 0.2s;
}

.dropdown-arrow.rotate {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 30;
}

.dropdown-item {
  padding: 10px 16px;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background: #f8fafc;
}

/* Price Display */
.price-display {
  position: absolute;
  top: 10px;
  left: 0px;
  right: 10px;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
  z-index: 5;
  font-family: 'Roboto Mono', monospace;
  font-size: 13px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(4px);
  max-width: calc(100% - 100px);
}

.price-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
  white-space: nowrap;
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.5);
}

.price-value {
  color: #1a1a1a;
  font-weight: 600;
  min-width: 70px;
  display: inline-block;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 2px;
}

.psar-dot {
  background: #2962FF;
}

.ma-dot {
  background: #FF9800;
}

/* Button Styles */
.settings-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.settings-button:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.settings-icon {
  font-size: 1.1rem;
}

.submit-button {
  padding: 10px 24px;
  background: #2962FF;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.submit-button:hover {
  background: #1e4bd8;
}

/* Modal Styles */
.modal-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-container {
  position: relative;
  z-index: 1001;
  width: 90%;
  max-width: 600px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 4px;
  color: #64748b;
  transition: color 0.2s;
}

.close-button:hover {
  color: #1a1a1a;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.indicator-group {
  margin-bottom: 24px;
}

.indicator-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.checkbox-label {
  font-weight: 500;
}

.indicator-settings {
  margin-top: 12px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.setting-group {
  margin-bottom: 12px;
}

.setting-group label {
  display: block;
  margin-bottom: 6px;
  color: #64748b;
  font-size: 0.9rem;
}

.number-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.number-input:focus {
  outline: none;
  border-color: #2962FF;
  box-shadow: 0 0 0 2px rgba(41, 98, 255, 0.1);
}

.cancel-button {
  padding: 8px 16px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-button:hover {
  background: #e2e8f0;
}

.save-button {
  padding: 8px 24px;
  background: #2962FF;
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.save-button:hover {
  background: #1e4bd8;
}

.chart-container {
  position: relative;
  height: 500px;
  width: 100%;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2962FF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .price-display {
    overflow-x: auto;
    white-space: nowrap;
    flex-wrap: nowrap;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  
  .price-display::-webkit-scrollbar {
    display: none;
  }

  .price-value {
    min-width: 60px;
  }

  .controls-container {
    flex-direction: column;
    align-items: stretch;
  }

  .dropdown-container {
    width: 100%;
  }
}

.af-settings {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}
</style>
