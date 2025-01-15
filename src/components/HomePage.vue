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


import LightWeightChart from './LightWeightChart.vue';
import CustomSelect from './CustomSelect.vue'

const defaultData = []
const NavigationMap = {
  "AccountName": "/user/"
}

const data = ref(defaultData)
const columnHelper = createColumnHelper()



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
const time = ref([])
const serverData = ref({})
const checkBackendConnection = ref(false)
const checkServerDataConnection = ref(false)
const Latency = ref(0)
const max_latency = ref(0);
const past_time = ref(0)
const live_weights = ref([]);

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
    }

  }

  let clients_data = client_BackendData.value
  if (clients_data && clients_data.length > 0) {
    data.value = clients_data.map(item => ({


      AccountName: item.name || '',
      IdealMTM: item.ideal_MTM !== undefined ? item.ideal_MTM : 0,
      Day_PL: item.MTM !== undefined ? item.MTM : 0,
      Slippage1:item.Slippage1!==undefined?item.Slippage1:0,
      Slippage2:item.Slippage2!==undefined?item.Slippage2:0,
      PNL_PER_UM: item['PNL Utilized %'] !== undefined ? Number(item['PNL Utilized %']) : 0,
      PNL_PER_M: item['PNL Overall %'] !== undefined ? Number(item['PNL Overall %']) : 0,
      Peak_Margin: item['Peak Margin'] !== undefined ? item['Peak Margin'] : 0,
      Slippage: item.Slippage !== undefined ? item.Slippage : 0,
      CompleteOrderCount: item.CompleteOrderCount !== undefined ? Number(item.CompleteOrderCount) : 0,
      openOrderCount: item.openOrderCount !== undefined ? Number(item.openOrderCount) : 0,
      RejectedOrderCount: item.Rejected_orders !== undefined ? Number(item.Rejected_orders) : 0,
      PendingOrderCount: item.Pending_orders !== undefined ? Number(item.Pending_orders) : 0,
      OpenQuantity: item.OpenQuantity !== undefined ? Number(item.OpenQuantity) : 0,
      NetQuantity: item.NetQuantity !== undefined ? Number(item.NetQuantity) : 0,
      Ideal_Margin: item.Live_Client_Margin !== undefined ? Number(item.Live_Client_Margin) : 0,
      VAR: item.Live_Client_Var !== undefined ? item.Live_Client_Var : 0,
      Margin: item['Total Margin'] !== undefined ? item['Total Margin'] : 0, //item.Total Margin',
      Cash: item.cashAvailable !== undefined ? Number(item.cashAvailable) : 0,
      AvailableMargin: item.availableMargin !== undefined ? Number(item.availableMargin) : 0,
      Used_Margin: item.marginUtilized !== undefined ? item.marginUtilized : 0,
      VAR_PERCENTAGE: item.Live_Client_Var !== undefined && ( item['Total Margin'] > 0) ? ((Number(item.Live_Client_Var) / Number( item['Total Margin'])) * 100).toPrecision(4) : 0,
      API_NET_PNL: item['API NET PNL'] !== undefined ? item['API NET PNL'] : 0,
      API_DAY_PNL: item['API DAY PNL'] !== undefined ? item['API DAY PNL'] : 0,

    }))
  }



}


const connectServerDataWebSocket = () => {
  const token = localStorage.getItem('access_token'); // Retrieve the access token
  if (!token) {
      alert('User not authenticated');
      return;
  }
    
  const socket = new WebSocket('wss://production.swancapital.in/serverData');

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

  const socket = new WebSocket('wss://production.swancapital.in/ws');

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
      if (message['live_weights']) {
        live_weights.value = message['live_weights'];
      }
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
  <div class="homePage_Container bg-[#efefef]/30">

    <div v-if="index_data" class="nav-index-container font-semibold bg-white drop-shadow-sm">
      <div v-for="(value, key) in index_data" :key="key" class="index-item">
        <span class="index-name">{{ formatIndexName(key) }}</span>
        <div class="index-value-container">
          <span :class="['index-value', getPercentageClass(key)]">{{ formatNumber(value) }}</span>
          <img v-if="getPercentageClass(key) === 'positive'" class="image_width" src="../assets/arrow-up-long-solid.svg"
            alt="">
          <img v-else class="image_width" src="../assets/arrow-down-long-solid.svg" alt="">
          <span :class="['percentage', getPercentageClass(key)]">{{ getDifference(key) }}</span>
          <span :class="['percentage', getPercentageClass(key)]">
            <span class="opening-brac">(</span>{{ formatPercentage(getPercentage(key)) }}<span
              class="closing-brac">)</span>
          </span>
        </div>
      </div>
    </div>

    <div class="time-container">

      <p class="timeDiv">
        <span>
          Time:{{ time }}
        </span>
        <span v-if="serverData['CPU']">
          CPU : {{ serverData['CPU'][serverData['CPU'].length - 1].value }} %
        </span>
        <span v-if="serverData['RAM']">
          RAM : {{ serverData['RAM'][serverData['RAM'].length - 1].value }} %
        </span>
        <span v-if="serverData['Redis']">
          Redis Used : {{ serverData['Redis'][serverData['Redis'].length - 1].used_memory_gb.toFixed(2) }} GB
        </span>
        <span v-if="serverData['Redis']">
          Redis Used Peak : {{ serverData['Redis'][serverData['Redis'].length - 1].used_memory_peak_gb.toFixed(2)
          }} GB
        </span>
        <span v-if="serverData['Redis']">
          System Memory : {{ serverData['Redis'][serverData['Redis'].length -
            1].total_system_memory_gb.toFixed(2)
          }} GB
        </span>
        <span v-if="serverData['Redis']">
          Redis Used Percentage : {{ serverData['Redis'][serverData['Redis'].length -
            1].memory_percent.toFixed(2)
          }} %
        </span>
        <span v-if="serverData['Redis']">
          Redis Allocated Memory : {{ serverData['Redis'][serverData['Redis'].length -
            1].available_memory_gb.toFixed(2)
          }} GB
        </span>

      </p>
      <WarningSignal :signals="pulse_signal" :latency="Latency" :max_latency="max_latency" />
    </div>
    <!-- <button @click="showSuccessToast">Show Success Toast</button> -->

    <div class="mx-auto px-8 py-8">
      <div class="my-8">
        <!-- <p class="table-heading">Accounts</p> -->
        <TanStackTestTable title="Accounts" :data="data" :columns="columns"
          :hasColor="['IdealMTM', 'Day_PL', 'Slippage', 'PNL_PER_UM', 'PNL_PER_M','Slippage1','Slippage2','API DAY PNL','API NET PNL']" :navigateTo="NavigationMap"
          :showPagination=true :hasRowcolor="{ 'columnName': 'AccountName', 'arrayValues': [] }" />


      </div>

    </div>
  </div>
</template>


<style>
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


.select-container {
  display: flex;
  width: 100%;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 10px;
}
</style>