<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'
import { inject } from 'vue'
import SignalForTable from './SignalForTable.vue'
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue'
import MultiLineChart from './HighCharts.vue'
import WarningSignal from './WarningSignal.vue'
import { MyEnum } from '../Enums/Prefix.js'
import Histogram from './Histogram.vue'
import { columns } from '../components/TableVariables/HomePageTable.js'; 
import webSocketService from '../services/websocketService';
import OHLCChart from './OHLCCHART.vue'

import LightWeightChart from './LightWeightChart.vue';
import CustomSelect from './CustomSelect.vue'

const defaultData = []
const NavigationMap = {
  "AccountName": "/user/"
}

const data = ref(defaultData)
const columnHelper = createColumnHelper()
// Add new refs for OHLC chart
const selectedIndex = ref(null)
const chartData = ref(null)
const isLoading = ref(false)


const client_BackendData = ref({})
const connection_BackendData = ref({})
const index_data = ref({})
const previous_day_close_index_data = ref({
  BANKNIFTYSPOT: 51117.80,
  FINNIFTYSPOT: 23722.15,
  MIDCPNIFTYSPOT: 13007.45,
  NIFTYSPOT: 24936.40,
  SENSEXSPOT: 81559.54
})
const pulse_signal = ref([])
const extra_data=ref([])
const time = ref([])
const serverData = ref({})
const checkBackendConnection = ref(false)
const checkServerDataConnection = ref(false)
const Latency = ref(0)
const max_latency = ref(0);
const past_time = ref(0);

let socket = null

const give_percentage_change = (a, b) => {
  if (!a || !b) return 0;
  const val = ((a - b) / a) * 100;
  return val;
}

const handleMessage = (message) => {
  client_BackendData.value = message.client_data
  connection_BackendData.value = message.connection_data
  if (message.connection_data)
    previous_day_close_index_data.value = message.connection_data['history_live_index']
  updateData()
}

const updateData = () => {


  if (connection_BackendData.value != undefined) {
    index_data.value = connection_BackendData.value.live_index
    let pulse_data = connection_BackendData.value.pulse
    time.value = connection_BackendData.value.time
    if (connection_BackendData.value.pulse) {
      pulse_signal.value = pulse_data
      pulse_signal.value.backendConnection = checkBackendConnection
      pulse_signal.value.position_mismatch = connection_BackendData.value.position_mismatch
      extra_data.value.broker_Position_Mismatch=connection_BackendData.value.broker_Position_Mismatch
      extra_data.value.position_broker_Mismatch = connection_BackendData.value.position_broker_Mismatch
      extra_data.value.custom_pulse=connection_BackendData.value.custom_pulse;
    }

  }

  let clients_data = client_BackendData.value
  if (clients_data && clients_data.length > 0) {
    data.value = clients_data.map(item => ({

      
      AccountName: item.name || '',
      AccountId : item.AccountId || '',
      IdealMTM: item.ideal_MTM !== undefined ? item.ideal_MTM : 0,
      Day_PL: item.MTM !== undefined ? item.MTM : 0,
      IdealTurnover:item.IdealTurnover!==undefined?item.IdealTurnover:0,
      Slippage2:item.Slippage2!==undefined?item.Slippage2:0,
      PNL_PER_UM: item['PNL Utilized %'] !== undefined ? Number(item['PNL Utilized %']) : 0,
      PNL_PER_M: item['PNL Overall %'] !== undefined ? Number(item['PNL Overall %']) : 0,
      Peak_Margin: item['Peak Margin'] !== undefined ? item['Peak Margin'] : 0,
      Slippage: item.Slippage !== undefined ? item.Slippage : 0,
      SlippagePer : item.SlippagePer !== undefined ? item.SlippagePer : 0,
      CompleteOrderCount: item.CompleteOrderCount !== undefined ? Number(item.CompleteOrderCount) : 0,
      openOrderCount: item.openOrderCount !== undefined ? Number(item.openOrderCount) : 0,
      RejectedOrderCount: item.Rejected_orders !== undefined ? Number(item.Rejected_orders) : 0,
      PendingOrderCount: item.Pending_orders !== undefined ? Number(item.Pending_orders) : 0,
      OpenQuantity: item.OpenQuantity !== undefined ? Number(item.OpenQuantity) : 0,
      NetQuantity: item.NetQuantity !== undefined ? Number(item.NetQuantity) : 0,
      HoldingPnl : item.HoldingPnl !==undefined ? Number(item.HoldingPnl):0,
      Ideal_Margin: item.Live_Client_Margin !== undefined ? Number(item.Live_Client_Margin) : 0,
      // VAR: item.Live_Client_Var !== undefined ? item.Live_Client_Var : 0,
      Cash: item.cashAvailable !== undefined ? Number(item.cashAvailable) : 0,
      AvailableMargin: item.availableMargin !== undefined ? Number(item.availableMargin) : 0,
      Used_Margin: item.marginUtilized !== undefined ? item.marginUtilized : 0,
      // VAR_PERCENTAGE: item.Live_Client_Var !== undefined && ( item['Total Margin'] > 0) ? ((Number(item.Live_Client_Var) / Number( item['Total Margin'])) * 100).toPrecision(4) : 0,
      API_NET_PNL: item['API NET PNL'] !== undefined ? item['API NET PNL'] : 0,
      API_DAY_PNL: item['API DAY PNL'] !== undefined ? item['API DAY PNL'] : 0,
      Portfolio_Value:item['Portfolio Value'] !== undefined ? item['Portfolio Value'] : 0,
      Cashperpf :Number(item['Cashperpf'] !== undefined ? item['Cashperpf'] : 0,  ['Cashperpf']) 

    }))
  }



}


// SVG content for arrows
const arrowDownSvg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" class="w-3 h-3">
  <path fill="currentColor" d="M169.4 470.6c12.5 12.5 32.8 12.5 45.3 0l160-160c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 370.8V64c0-17.7-14.3-32-32-32s-32 14.3-32 32v306.7L54.6 265.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160z"/>
</svg>`

const arrowUpSvg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" class="w-3 h-3">
  <path fill="currentColor" d="M214.6 41.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 141.2V448c0 17.7 14.3 32 32 32s32-14.3 32-32V141.2L329.4 246.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z"/>
</svg>`

// Loading spinner component
const LoadingSpinner = {
  template: `
    <div class="loading-spinner">
      <div class="spinner"></div>
    </div>
  `
}

// Add new method to toggle chart visibility
const toggleChart = async (key) => {
  if (selectedIndex.value === key) {
    // If clicking the same index, close the chart
    selectedIndex.value = null
    chartData.value = null
    return
  }
  
  selectedIndex.value = key
  isLoading.value = true
  chartData.value = null
  
  // try {
  //   const response = await fetch('https://production2.swancapital.in/Psar', {
  //     method: 'POST',
  //     headers: {
  //       'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  //       'Content-Type': 'application/json'
  //     },
  //     body: JSON.stringify({
  //       symbol: formatIndexName(key),
  //       timeframe: '5m',
  //       indicators: []
  //     })
  //   })
    
  //   if (!response.ok) throw new Error('Failed to fetch chart data')
  //   chartData.value = await response.json()
  // } catch (error) {
  //   console.error('Error fetching chart data:', error)
  // } finally {
  //   isLoading.value = false
  // }
}

// Add method to get arrow direction
const getArrowDirection = (key) => {
  return selectedIndex.value === key ? 'up' : 'down'
}


const formatDate = (timestamp) => {
  try {
    if (!timestamp) return '--';
    // Convert to string if it's not already
    const timeStr = String(timestamp);
    const [date] = timeStr.split(' ');
    return date || '--';
  } catch (error) {
    return '--';
  }
};

const formatTime = (timestamp) => {
  try {
    if (!timestamp) return '--';
    // Convert to string if it's not already
    const timeStr = String(timestamp);
    const [, time] = timeStr.split(' ');
    return time ? time.split('.')[0] : '--';
  } catch (error) {
    return '--';
  }
};

const connectServerDataWebSocket = () => {
  const token = localStorage.getItem('access_token'); // Retrieve the access token
  if (!token) {
      alert('User not authenticated');
      return;
  }
    
  const socket = new WebSocket('wss://production2.swancapital.in/serverData');

  socket.onopen = () => {
     // Send the token as the first message for authentication
    const authMessage = JSON.stringify({ token });
    socket.send(authMessage);
    console.log('ServerData WebSocket connection opened')
    checkServerDataConnection.value = true;
  }

  socket.onmessage = (event) => {
    if (event.data === 'ping') {
      socket.send('pong')
    } else {

      const message = JSON.parse(event.data);
      serverData.value = message
    }
  }

  socket.onclose = (event) => {
    console.log('ServerData WebSocket connection closed:', event.reason)
    checkServerDataConnection.value = false
  }


  socket.onerror = (error) => {
    console.error('ServerData WebSocket error:', error)
    checkServerDataConnection.value = false
  }
}

const connectWebSocket = () => {
  const token = localStorage.getItem('access_token'); // Retrieve the access token
  if (!token) {
    alert('User not authenticated');
    return;
  }

  const socket = new WebSocket('wss://production2.swancapital.in/ws');

  socket.onopen = () => {
    console.log('WebSocket connection opened');
    
    // Send the token as the first message for authentication
    const authMessage = JSON.stringify({ token });
    socket.send(authMessage);
    checkBackendConnection.value = true
  };


  socket.onmessage = (event) => {
    if (event.data === 'ping') {
      socket.send('pong')
    } else {

      const message = JSON.parse(event.data);
      let ar2 = message.time;
      if (past_time.value === 0) past_time.value = ar2;
      let date1 = new Date(past_time.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let diffInMs = date2 - date1;
      let diffInSeconds = diffInMs / 1000;
      Latency.value = diffInSeconds;
      max_latency.value = Math.max(max_latency.value, Latency.value)
      past_time.value = ar2;
      handleMessage(message)

    }
  }

  socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event.reason)
    checkBackendConnection.value = false
  }


  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
    checkBackendConnection.value = false
  }
}

const triggerToast = inject('triggerToast')

const showSuccessToast = () => {
  triggerToast('Operation successful!', 'success')
}

const formatIndexName = (name) => {
  return name.replace('SPOT', '').toUpperCase()
}
const formatNumber = (value) => {
  const val = value.toFixed(2)
  return val ? val.toLocaleString() : '0'
}
const getDifference = (key) => {
  return (index_data.value[key].toFixed(2) - previous_day_close_index_data.value[key]).toFixed(2);
}
const getPercentage = (key) => {
  const change = give_percentage_change(index_data.value[key], previous_day_close_index_data.value[key]);
  return change.toFixed(2);
}
const formatPercentage = (value) => {
  return `${value}%`
}
const getPercentageClass = (key) => {
  const percentage = getPercentage(key)
  return percentage > 0 ? 'positive' : percentage < 0 ? 'negative' : 'neutral'
}

onMounted(() => {
  connectWebSocket()
  // connectServerDataWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>



<template>
  <div class="homepage-container  bg-[#efefef]/30">

    <!-- Index Data Cards -->
    <div v-if="index_data" class="index-cards-container">
      <div v-for="(value, key) in index_data" :key="key" 
           class="index-card">
        <div class="index-header">
          <span class="index-name">{{ formatIndexName(key) }}</span>
          <button @click="toggleChart(key)" class="toggle-button">
            <div v-html="arrowDownSvg" 
                :class="['arrow-icon', selectedIndex === key ? 'rotate-180' : '']">
            </div>
          </button>
        </div>
        <div class="index-content">
          <span :class="['index-value', getPercentageClass(key)]">
            {{ formatNumber(value) }}
          </span>
          <div class="index-change">
            <img v-if="getPercentageClass(key) === 'positive'" 
                 class="trend-icon" 
                 src="../assets/arrow-up-long-solid.svg" 
                 alt="Up">
            <img v-else 
                 class="trend-icon" 
                 src="../assets/arrow-down-long-solid.svg" 
                 alt="Down">
            <span :class="['percentage', getPercentageClass(key)]">
              {{ getDifference(key) }}
              <span class="percentage-bracket">
                ({{ formatPercentage(getPercentage(key)) }})
              </span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- OHLC Chart Section -->
    <transition name="chart-fade">
      <div v-if="selectedIndex" class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">{{ formatIndexName(selectedIndex) }} Percentage Move</h3>
        </div>
        <div v-if="isLoading" class="loading-container">
          <LoadingSpinner />
        </div>
        <div class="flex-container">
          <div class="flex-item">
            <p>09:15 O :</p>
            <p :class="connection_BackendData['long_options_indicator'][formatIndexName(selectedIndex)]['09:15 O']>0 ? 'green' : 'red' " >
            {{ connection_BackendData['long_options_indicator'][formatIndexName(selectedIndex)]["09:15 O"] }} %
            </p>
          </div>
          <div class="flex-item">
            <p>09:15 C :</p>
            <p :class="connection_BackendData['long_options_indicator'][formatIndexName(selectedIndex)]['09:15 C'] >0 ? 'green' : 'red' " >
              {{ connection_BackendData['long_options_indicator'][formatIndexName(selectedIndex)]["09:15 C"] }} %
            </p>
          </div>
          <div class="flex-item">
            <p>12:00 O :</p>
            <p :class="connection_BackendData['long_options_indicator'][formatIndexName(selectedIndex)]['12:00 O']>0 ? 'green' : 'red' " >
              {{ connection_BackendData['long_options_indicator'][formatIndexName(selectedIndex)]["12:00 O"] }} %
            </p>
          </div>
          <div class="flex-item">
            <p>12:00 C :</p>
            <p :class="connection_BackendData['long_options_indicator'][formatIndexName(selectedIndex)]['12:00 C']>0 ? 'green' : 'red' " >
              {{ connection_BackendData['long_options_indicator'][formatIndexName(selectedIndex)]["12:00 C"] }} %
            </p>
          </div>
        </div>
      </div>
    </transition>



    <div class="time-container">
    <p class="timeDiv flex gap-4 items-center flex-wrap">
      <!-- Time Display -->
      <span class="time-block">
        <span class="font-medium">Date:</span> {{ formatDate(time) }}
        <span class="font-medium ml-4">Time:</span> {{ formatTime(time) }}
      </span>
    </p>
    <WarningSignal :signals="pulse_signal" :latency="Latency" :max_latency="max_latency" :extra_data="extra_data" />
  </div>
    <!-- <button @click="showSuccessToast">Show Success Toast</button> -->

    <div class="mx-auto px-8 py-8">
      <div class="my-8">
        <!-- <p class="table-heading">Accounts</p> -->
        <TanStackTestTable title="Accounts" :data="data" :columns="columns"
          :hasColor="['IdealMTM', 'Day_PL', 'Slippage','SlippagePer','PNL_PER_UM', 'HoldingsDayPL','PNL_PER_M','Slippage2','API DAY PNL','API NET PNL']" :navigateTo="NavigationMap"
          :showPagination=true :hasRowcolor="{ 'columnName': 'AccountName', 'arrayValues': [] }"
          :compareRules="[ { primary: 'Cash', secondary: 'Portfolio Value', percentage: 3 } ]"
          
          />


      </div>

    </div>
  </div>
</template>


<style>
  .green{
    color:green;
  }
  .red{
    color:red;
  }
  .flex-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 20px;
    padding: 10px;
  }

  .flex-item {
    font-weight: bold;
    flex: 1 1 200px; /* grow, shrink, and a minimum width */
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 4px;
    text-align: center;
  }

  .flex-item p {
    margin: 5px 0;
  }
.homepage-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 1.5rem;
}
.index-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.index-card {
  background: white;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid rgba(229, 231, 235, 0.5);
  transition: transform 0.2s, box-shadow 0.2s;
}

.index-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.index-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
}

.toggle-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.toggle-button:hover {
  transform: scale(1.1);
}

.arrow-icon {
  display: inline-flex;
  width: 16px;
  height: 16px;
  color: #64748b;
  transition: transform 0.3s ease;
}

.arrow-icon.rotate-180 {
  transform: rotate(180deg);
}

/* Chart Container Styles */
.chart-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.chart-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
}

/* Chart Transition Animation */
.chart-fade-enter-active,
.chart-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.chart-fade-enter-from,
.chart-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.index-content {
 display: flex;
 flex-direction: column;
 gap: 0.5rem;
}

.index-value {
 font-size: 1.1rem;
 font-weight: 700;
}

.index-change {
 display: flex;
 align-items: center;
 gap: 0.5rem;
}

.trend-icon {
 width: 12px;
 height: auto;
}

.positive { color: #39a97c; }
.negative { color: #d95858; }
.neutral { color: #9e9e9e; }

.trend-icon {
  width: 12px;
  height: auto;
}

html {
  font-size: 14px;
}

.opening-brac {
  padding-right: 3px;
}

.closing-brac {
  padding-left: 3px;
}

.index-value-container {
  display: flex;
  gap: 5px;
  justify-items: center;
  align-items: center;

}

.nav-index-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  padding: 10px;
}

.index-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 10px;
  position: relative;
  min-width: 150px;
}

.index-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.image_width {
  width: 10px;
  height: auto;
}

.index-value {
  font-size: 1.0em;
}

.percentage {
  font-size: 1.0em;
}

.positive {
  color: #39a97c;
}

.negative {
  color: #d95858;
}

.neutral {
  color: #9e9e9e;
}


.table-heading {
  font-size: 22px;
  font-weight: 600;
  margin-left: 30px;
}


.nav_index_container {
  /* padding-top: 20px; */
  display: flex;
  margin-top: 10px;
  align-items: center;
  /* gap: 60px; */
  padding: 10px 30px;
  font-size: 16px;
  justify-content: space-between;
}

.time-container {
  display: flex;
  margin-top: 20px;
  margin-left: 30px;
  font-weight: 600;
}

.timeDiv {
  justify-content: center;
  align-items: flex-start;
  display: flex;
  flex-direction: column;
  width: 100%;

}



/* Time Block Styling */
.time-block {
  padding: 0.5rem 1rem;
  background-color: #ebf5ff;
  border-radius: 0.375rem;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  font-weight: 500;
  display: inline-flex;
  gap: 0.5rem;
}

.time-block .font-medium {
  color: #1e3a8a;
}

/* Responsive Design */
@media (max-width: 640px) {
  .time-container {
    margin: 0.5rem;
    padding: 0.75rem;
  }
  .time-block {
    width: 100%;
    justify-content: space-between;
  }
}

.select-container {
  display: flex;
  width: 100%;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 10px;
}
</style>