<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import NavBar from './NavBar.vue'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'
import SignalForTable from './SignalForTable.vue'
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue'
import MultiLineChart from './HighCharts.vue'
import WarningSignal from './WarningSignal.vue'
import { MyEnum } from '../Enums/Prefix.js'

import LightWeightChart from './LightWeightChart.vue';

const defaultData = []
const NavigationMap = {
  "AccountName": "/user/"
}

const data = ref(defaultData)
const columnHelper = createColumnHelper()

const columns = [

  columnHelper.accessor(row => row.AccountName, {
    id: 'AccountName',
    cell: info => info.getValue(),
    header: () => 'Account Name',
  }),
  columnHelper.accessor(row => row.IdealMTM, {
    id: 'IdealMTM',
    cell: info => info.getValue(),
    header: () => 'Ideal MTM',
  }),
  columnHelper.accessor(row => row.Day_PL, {
    id: 'Day_PL',
    cell: info => info.getValue(),
    header: () => 'Day_PL',
  }),
  columnHelper.accessor(row => row.Friction, {
    id: 'Friction',
    cell: info => info.getValue(),
    header: () => 'Friction',
  }),
  columnHelper.accessor(row => row.MARGIN, {
    id: 'MARGIN',
    cell: info => info.getValue(),
    header: () => 'Margin',
  }),
  columnHelper.accessor(row => row.VAR, {
    id: 'VAR',
    cell: info => info.getValue(),
    header: () => 'VAR \u20B9',
  }),
  columnHelper.accessor(row => row.VAR_PERCENTAGE, {
    id: 'VAR %',
    cell: info => info.getValue() + "%",
    header: () => 'VAR %',
  }),

  columnHelper.accessor(row => row.NetQuantity, {
    id: 'NetQuantity',
    cell: info => info.getValue(),
    header: () => 'NetQuantity',
  }),
  columnHelper.accessor(row => row.OpenQuantity, {
    id: 'OpenQuantity',
    cell: info => info.getValue(),
    header: () => 'OpenQuantity',
  }),
  columnHelper.accessor(row => row.RejectedOrderCount, {
    id: 'RejectedOrderCount',
    cell: info => info.getValue(),
    header: () => 'RejectedOrderCount',
  }),
  columnHelper.accessor(row => row.PendingOrderCount, {
    id: 'PendingOrderCount',
    cell: info => info.getValue(),
    header: () => 'PendingOrderCount',
  }),


  columnHelper.accessor(row => row.PortfolioValue, {
    id: 'PortfolioValue',
    cell: info => info.getValue(),
    header: () => 'Portfolio Value',
  }),
  columnHelper.accessor(row => row.PositionDayPL, {
    id: 'PositionDayPL',
    cell: info => info.getValue(),
    header: () => 'PositionDayPL',
  }),
  columnHelper.accessor(row => row.HoldingsDayPL, {
    id: 'HoldingsDayPL',
    cell: info => info.getValue(),
    header: () => 'HoldingsDayPL',
  }),

  columnHelper.accessor(row => row.TotalOrderCount, {
    id: 'TotalOrderCount',
    cell: info => info.getValue(),
    header: () => 'TotalOrderCount',
  }),
  columnHelper.accessor(row => row.OpenOrderCount, {
    id: 'OpenOrderCount',
    cell: info => info.getValue(),
    header: () => 'OpenOrderCount',
  }),
  columnHelper.accessor(row => row.CompleteOrderCount, {
    id: 'CompleteOrderCount',
    cell: info => info.getValue(),
    header: () => 'CompleteOrderCount',
  }),
  columnHelper.accessor(row => row.PositionsCount, {
    id: 'PositionsCount',
    cell: info => info.getValue(),
    header: () => 'PositionsCount',
  }),
  columnHelper.accessor(row => row.HoldingsCount, {
    id: 'HoldingsCount',
    cell: info => info.getValue(),
    header: () => 'HoldingsCount',
  }),
  columnHelper.accessor(row => row.Used_Margin, {
    id: 'Used_Margin',
    cell: info => info.getValue(),
    header: () => 'Used_Margin',
  }),
  columnHelper.accessor(row => row.AvailableMargin, {
    id: 'AvailableMargin',
    cell: info => info.getValue(),
    header: () => 'AvailableMargin',
  }),
  columnHelper.accessor(row => row.Cash, {
    id: 'Cash',
    cell: info => info.getValue(),
    header: () => 'Cash',
  }),
]



const client_BackendData = ref({})
const connection_BackendData = ref({})
const basket_BackendData = ref({})
const strategy_mtm_chart_BackendData = ref({})

const index_data = ref("hello")
const basket_chart_data = ref([])
const basket_chart_name = ref([])
const pulse_signal = ref([])
const time = ref([])
const user_infected = ref([])
const checkBackendConnection = ref(false)
const Latency = ref(0)
const max_latency = ref(0);


let socket = null
let reconnectAttempts = 0
const maxReconnectAttempts = 5
const reconnectInterval = 5000 // 5 seconds
const pingInterval = 30000 // 30 seconds

const getCurrentDateTime = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  const milliseconds = String(now.getMilliseconds()).padStart(3, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${milliseconds}`;
}
const measureLatency = (dateStr, dateStr2) => {

  try {

    let [datePart, timePart] = dateStr.split(' ');
    let [day, month, year] = datePart.split('-').map(Number);
    let [hours, minutes, seconds] = timePart.split(':').map(Number);
    let milliseconds = Number(timePart.split('.')[1] || 0);
    let date1 = new Date(year, month - 1, day, hours, minutes, seconds, milliseconds / 1000);

    // Convert the second date string to a Date object
    let [datePart2, timePart2] = dateStr2.split(' ');
    let [year2, month2, day2] = datePart2.split('-').map(Number);
    let [hours2, minutes2, seconds2] = timePart2.split(':').map(Number);
    let milliseconds2 = Number(timePart2.split('.')[1] || 0);
    let date2 = new Date(year2, month2 - 1, day2, hours2, minutes2, seconds2, milliseconds2 / 1000);

    // Calculate the difference in milliseconds
    let latency_value = Math.abs(date2 - date1);

    // Convert latency from milliseconds to seconds with fractional part
    latency_value /= 1000;
    Latency.value = latency_value;
    max_latency.value = Math.max(latency_value, max_latency.value);
  }
  catch (err) {
    console.log(err);
  }

};

const handleMessage = (message) => {


  client_BackendData.value = message.client_data
  connection_BackendData.value = message.connection_data

  if (message.time)
    measureLatency(message['time'], getCurrentDateTime())

  updateData()
}


const updateData = () => {
  checkBackendConnection.value = true
  index_data.value = connection_BackendData.value.live_index

  let clients_data = client_BackendData.value
  let pulse_data = connection_BackendData.value.pulse
  time.value = connection_BackendData.value.time

  if (connection_BackendData.value.pulse) {
    user_infected.value = Object.keys(connection_BackendData.value.pulse)
      .filter(key => (key.startsWith('pulse_trader_xts:') || key.startsWith('pulse_trader_zerodha:')) && connection_BackendData.value.pulse[key] === false)
      .map(key => key.split(':')[1])
  }

  if (clients_data && clients_data.length > 0) {
    data.value = clients_data.map(item => ({


      AccountName: item.name || '',
      IdealMTM: item.ideal_MTM !== undefined ? Number(item.ideal_MTM) : 0,
      Day_PL: item.MTM !== undefined ? Number(item.MTM) : 0,
      Friction: item.MTM !== undefined && item.ideal_MTM !== undefined
        ? (Number(item.MTM) - Number(item.ideal_MTM)).toFixed(2)
        : '0.00',
      RejectedOrderCount: item.Rejected_orders !== undefined ? Number(item.Rejected_orders) : 0,
      PendingOrderCount: item.Pending_orders !== undefined ? Number(item.Pending_orders) : 0,
      OpenQuantity: item.OpenQuantity !== undefined ? Number(item.OpenQuantity) : 0,
      NetQuantity: item.NetQuantity !== undefined ? Number(item.NetQuantity) : 0,
      MARGIN: item.Live_Client_Margin !== undefined ? Number(item.Live_Client_Margin) : 0,
      VAR_PERCENTAGE: item.Live_Client_Var !== undefined && (item.Live_Client_Margin > 0) ? ((Number(item.Live_Client_Var) / Number(item.Live_Client_Margin)) * 100).toPrecision(4) : 0,
      VAR: item.Live_Client_Var !== undefined ? Number(item.Live_Client_Var) : 0,
    }))
  }

  if (connection_BackendData.value.pulse) {
    pulse_signal.value = pulse_data
    pulse_signal.value.backendConnection = checkBackendConnection
  }

}

const connectWebSocket = () => {
  const socket = new WebSocket('ws://localhost:5000/ws');

  socket.onopen = () => {
    console.log('WebSocket connection opened')
    checkBackendConnection.value = true
    reconnectAttempts = 0
    startPingInterval()
  }

  socket.onmessage = (event) => {
    if (event.data === 'ping') {
      socket.send('pong')
    } else {

      const message = JSON.parse(event.data);
      handleMessage(message)
    }
  }

  socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event.reason)
    checkBackendConnection.value = false
    stopPingInterval()
    reconnect()
  }


  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
    checkBackendConnection.value = false
  }
}


const connectBasketChartWebSocket = () => {
  const basketSocket = new WebSocket('ws://localhost:5000/chart/basket');

  basketSocket.onopen = () => {
    console.log('Basket Chart WebSocket connection opened');
  }

  basketSocket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    basket_BackendData.value = message.basket_data;
  }

  basketSocket.onclose = (event) => {
    console.log('Basket Chart WebSocket connection closed:', event.reason);
    // Implement reconnection logic if needed
  }

  basketSocket.onerror = (error) => {
    console.error('Basket Chart WebSocket error:', error);
  }

  return basketSocket;
}


const connectStrategyChartWebSocket = () => {
  const strategySocket = new WebSocket('ws://localhost:5000/chart/strategy');


  strategySocket.onopen = function (e) {
    console.log("strategysocket Connection established");
    // Send the initial set of UIDs
    sendStrategyUIDs(['shortoptions2_sot01_0_1_FINNIFTY_P_0.4_3_FNS2ID1', 'shortoptions2_sot02_0_1_FINNIFTY_P_0.5_2_FNS2ID2', 'shortoptions2_sot03_0_1_FINNIFTY_P_0.4_3_FNS2ID3', 'shortoptions2_sot04_0_1_FINNIFTY_P_0.5_2_FNS2ID4', 'shortoptions2_sot05_0_1_FINNIFTY_P_0.4_3_FNS2ID5', 'shortoptions2_sot06_0_1_FINNIFTY_P_0.5_2_FNS2ID6', 'stg13new_0_x0_20_2_SENSEX_PCT_0.0026_3_0.2_0.7_1_False_10_3.0', 'stg13new_0_x0_190_1_SENSEX_R_1.4_3_0.2_0.7_1_False_14_2.5', 'stg13new_0_x0_235_1_SENSEX_PCT_0.0026_3_0.2_0.7_2_False_28_1.5', 'stg13new_0_x0_185_1_SENSEX_PCT_0.0016_3_0.3_0.8_1_False_14_2.0', 'stg13new_0_x0_235_2_SENSEX_R_1.3_3_0.35_0.8_2_False_28_2.0', 'stg13new_0_x0_205_1_SENSEX_PCT_0.001_3_0.3_0.7_1_False_28_2.0', 'stg13new_0_x0_60_2_SENSEX_R_1.4_3_0.3_0.9_2_False_14_3.0', 'stg13new_0_x0_60_1_SENSEX_PCT_0.0028_3_0.3_0.8_1_False_10_2.0', 'stg13new_0_x0_0_1_SENSEX_PCT_0.0018_3_0.3_0.9_2_False_28_3.0', 'stg13new_0_x0_130_1_SENSEX_R_1.1_3_0.25_0.9_1_False_14_3.0', 'stg13new_0_x0_235_2_SENSEX_PCT_0.0028_3_0.35_0.7_2_False_14_2.5', 'stg13new_0_x0_40_1_SENSEX_PCT_0.0016_3_0.35_0.7_2_False_14_2.0', 'stg13new_0_x0_210_1_SENSEX_R_1.2_3_0.2_0.8_2_False_10_2.0', 'stg13new_0_x0_55_2_SENSEX_R_1.0_3_0.35_0.7_2_False_10_3.0', 'stg13new_0_x0_115_1_SENSEX_R_1.0_3_0.35_0.8_1_False_10_1.5', 'stg13new_0_x0_45_1_SENSEX_R_1.0_3_0.25_0.7_1_False_28_3.0', 'stg13new_0_x0_0_1_SENSEX_PCT_0.0024_3_0.35_0.9_1_False_10_1.5', 'stg13new_0_x0_130_1_SENSEX_R_1.0_3_0.3_0.9_2_False_10_1.5', 'stg13new_0_x0_225_1_SENSEX_PCT_0.0012_3_0.25_0.8_1_False_28_2.5', 'stg13new_0_x0_100_2_SENSEX_PCT_0.002_3_0.35_0.9_2_False_28_2.5', 'stg13new_0_x0_90_1_SENSEX_PCT_0.001_3_0.3_0.9_1_False_10_2.0', 'stg13new_0_x0_10_1_SENSEX_R_1.2_3_0.25_0.8_1_False_14_3.0', 'stg13new_0_x0_175_2_SENSEX_R_1.1_3_0.25_0.8_1_False_28_1.5', 'stg13new_0_x0_140_2_SENSEX_PCT_0.0014_3_0.25_0.7_1_False_28_1.5', 'stg13new_0_x0_130_2_SENSEX_R_1.0_3_0.25_0.9_1_False_28_3.0', 'stg13new_0_x0_75_2_SENSEX_R_1.4_3_0.3_0.7_2_False_28_2.5', 'stg13new_0_x0_225_2_SENSEX_PCT_0.0012_3_0.3_0.9_2_False_28_2.0', 'stg13new_0_x0_170_1_SENSEX_PCT_0.0022_3_0.35_0.7_2_False_14_2.0', 'stg13new_0_x0_75_2_SENSEX_PCT_0.0012_3_0.35_0.8_2_False_10_2.5', 'stg13new_0_x0_195_2_SENSEX_R_1.4_3_0.2_0.8_2_False_28_2.0', 'stg13new_0_x0_235_1_SENSEX_R_1.4_3_0.35_0.8_2_False_14_2.0', 'stg13new_0_x0_110_1_SENSEX_R_1.2_3_0.35_0.8_2_False_14_2.0', 'stg13new_0_x0_155_2_SENSEX_R_1.0_3_0.35_0.9_2_False_10_2.0', 'stg13new_0_x0_75_1_SENSEX_PCT_0.0022_3_0.25_0.9_2_False_14_2.0', 'tridentdir_0_x0_165_1_SENSEX_PCT_0.0016_3_0.35_0.9_2_False_4_1', 'tridentdir_0_x0_180_1_SENSEX_PCT_0.002_3_0.3_0.8_2_False_2_1', 'tridentdir_0_x0_20_2_SENSEX_R_1.0_3_0.35_0.8_2_False_3_1', 'tridentdir_0_x0_100_1_SENSEX_PCT_0.0026_3_0.35_0.9_2_False_3_1', 'tridentdir_0_x0_25_1_SENSEX_PCT_0.0026_3_0.3_0.8_1_False_3_1', 'tridentdir_0_x0_215_2_SENSEX_PCT_0.0028_3_0.35_0.8_1_False_3_1', 'tridentdir_0_x0_50_1_SENSEX_R_1.3_3_0.3_0.8_2_False_2_1', 'tridentdir_0_x0_30_1_SENSEX_R_1.1_3_0.25_0.7_1_False_4_1', 'tridentdir_0_x0_30_2_SENSEX_R_1.3_3_0.3_0.7_2_False_3_1', 'tridentdir_0_x0_180_2_SENSEX_PCT_0.0012_3_0.25_0.8_1_False_2_1', 'tridentdir_0_x0_190_1_SENSEX_R_1.0_3_0.25_0.8_2_False_4_1', 'tridentdir_0_x0_165_2_SENSEX_R_1.0_3_0.3_0.8_2_False_2_1', 'tridentdir_0_x0_15_2_SENSEX_R_1.3_3_0.3_0.9_2_False_3_1', 'tridentdir_0_x0_225_2_SENSEX_PCT_0.001_3_0.3_0.7_2_False_3_1', 'tridentdir_0_x0_130_1_SENSEX_R_1.4_3_0.35_0.9_1_False_3_1', 'tridentdir_0_x0_60_2_SENSEX_R_1.4_3_0.25_0.7_2_False_2_1', 'tridentdir_0_x0_55_2_SENSEX_R_1.3_3_0.3_0.9_1_False_4_1', 'tridentdir_0_x0_0_1_SENSEX_R_1.1_3_0.35_0.9_2_False_3_1', 'tridentdir_0_x0_10_2_SENSEX_R_1.2_3_0.3_0.9_1_False_3_1', 'tridentdir_0_x0_125_2_SENSEX_R_1.2_3_0.3_0.9_2_False_2_1', 'tridentdir_0_x0_50_2_SENSEX_PCT_0.0024_3_0.35_0.9_1_False_3_1', 'tridentdir_0_x0_45_1_SENSEX_PCT_0.0016_3_0.2_0.7_2_False_3_1', 'tridentdir_0_x0_175_2_SENSEX_R_1.3_3_0.2_0.8_2_False_2_1', 'tridentdir_0_x0_130_1_SENSEX_R_1.2_3_0.35_0.9_1_False_3_1', 'tridentdir_0_x0_65_1_SENSEX_R_1.2_3_0.35_0.9_2_False_3_1', 'tridentdir_0_x0_130_2_SENSEX_R_1.1_3_0.35_0.8_2_False_3_1', 'tridentdir_0_x0_75_2_SENSEX_R_1.1_3_0.35_0.9_2_False_3_1', 'tridentdir_0_x0_135_1_SENSEX_PCT_0.0024_3_0.25_0.7_2_False_4_1', 'tridentdir_0_x0_125_2_SENSEX_PCT_0.001_3_0.3_0.8_1_False_4_1', 'tridentdir_0_x0_200_2_SENSEX_R_1.3_3_0.3_0.7_2_False_4_1', 'tridentdir_0_x0_130_1_SENSEX_PCT_0.002_3_0.3_0.7_2_False_2_1', 'tridentdir_0_x0_230_2_SENSEX_PCT_0.0012_3_0.25_0.8_1_False_3_1', 'tridentdir_0_x0_190_2_SENSEX_PCT_0.0014_3_0.3_0.8_1_False_2_1', 'tridentdir_0_x0_155_1_SENSEX_PCT_0.0022_3_0.25_0.7_1_False_3_1', 'tridentdir_0_x0_215_1_SENSEX_PCT_0.002_3_0.3_0.8_2_False_4_1', 'tridentdir_0_x0_80_1_SENSEX_PCT_0.001_3_0.3_0.7_1_False_3_1', 'tridentdir_0_x0_35_1_SENSEX_PCT_0.0014_3_0.2_0.8_2_False_3_1', 'tridentdir_0_x0_205_1_SENSEX_PCT_0.0018_3_0.35_0.8_1_False_4_1', 'tridentdir_0_x0_60_1_SENSEX_R_1.3_3_0.25_0.9_2_False_3_1', 'tridentdir_0_x0_235_2_SENSEX_R_1.1_3_0.2_0.7_1_False_2_1', 'tridentdir_0_x0_65_1_SENSEX_R_1.4_3_0.25_0.8_1_False_2_1', 'tridentdir_0_x0_10_2_SENSEX_PCT_0.001_3_0.3_0.7_2_False_4_1', 'tridentdir_0_x0_135_1_SENSEX_PCT_0.0026_3_0.25_0.8_1_False_3_1', 'tridentdir_0_x0_155_1_SENSEX_R_1.2_3_0.3_0.9_1_False_4_1', 'tridentdir_0_x0_155_1_SENSEX_R_1.4_3_0.3_0.8_1_False_2_1', 'tridentdir_0_x0_235_1_SENSEX_PCT_0.0016_3_0.25_0.7_1_False_2_1', 'tridentdir_0_x0_225_1_SENSEX_PCT_0.0024_3_0.35_0.9_2_False_2_1', 'tridentdir_0_x0_100_1_SENSEX_R_1.3_3_0.25_0.9_2_False_2_1', 'tridentdir_0_x0_100_2_SENSEX_PCT_0.0024_3_0.2_0.9_1_False_2_1', 'blackbird_0_x0_35_1_SENSEX_PCT_0.0018_3_0.25_0.9_2_False_1_100', 'blackbird_0_x0_220_1_SENSEX_PCT_0.0028_3_0.35_0.8_1_False_2_100', 'blackbird_0_x0_185_1_SENSEX_R_1.1_3_0.25_0.9_2_False_2_100', 'blackbird_0_x0_20_2_SENSEX_PCT_0.0012_3_0.2_0.9_2_False_1_250', 'blackbird_0_x0_10_2_SENSEX_PCT_0.001_3_0.2_0.8_1_False_1_250', 'blackbird_0_x0_210_1_SENSEX_PCT_0.002_3_0.3_0.8_2_False_1_200', 'blackbird_0_x0_145_1_SENSEX_PCT_0.0018_3_0.2_0.7_1_False_2_100', 'blackbird_0_x0_180_2_SENSEX_PCT_0.0026_3_0.3_0.8_2_False_1_250', 'blackbird_0_x0_35_1_SENSEX_R_1.1_3_0.2_0.7_2_False_1_200', 'blackbird_0_x0_10_1_SENSEX_R_1.2_3_0.2_0.9_2_False_1_200', 'blackbird_0_x0_50_1_SENSEX_R_1.2_3_0.3_0.9_1_False_1_150', 'blackbird_0_x0_25_2_SENSEX_PCT_0.0022_3_0.25_0.7_2_False_2_250', 'blackbird_0_x0_10_1_SENSEX_PCT_0.0016_3_0.3_0.8_1_False_1_150', 'blackbird_0_x0_25_1_SENSEX_R_1.2_3_0.3_0.7_2_False_2_200', 'blackbird_0_x0_220_2_SENSEX_PCT_0.0028_3_0.3_0.9_2_False_1_200', 'blackbird_0_x0_35_1_SENSEX_R_1.1_3_0.2_0.9_1_False_1_150', 'blackbird_0_x0_55_2_SENSEX_PCT_0.0016_3_0.25_0.8_2_False_1_250', 'blackbird_0_x0_45_2_SENSEX_R_1.1_3_0.2_0.8_1_False_1_100', 'blackbird_0_x0_120_1_SENSEX_PCT_0.001_3_0.3_0.9_2_False_1_100', 'blackbird_0_x0_100_2_SENSEX_PCT_0.0018_3_0.35_0.9_2_False_1_150', 'blackbird_0_x0_0_1_SENSEX_R_1.4_3_0.25_0.7_2_False_1_250', 'blackbird_0_x0_25_1_SENSEX_R_1.4_3_0.2_0.8_1_False_1_200', 'blackbird_0_x0_135_1_SENSEX_PCT_0.0026_3_0.25_0.9_2_False_1_100', 'blackbird_0_x0_20_1_SENSEX_R_1.2_3_0.2_0.9_2_False_1_100', 'blackbird_0_x0_5_2_SENSEX_PCT_0.0028_3_0.3_0.7_1_False_1_150', 'blackbird_0_x0_220_2_SENSEX_PCT_0.0018_3_0.3_0.8_1_False_2_250', 'blackbird_0_x0_210_1_SENSEX_PCT_0.0014_3_0.35_0.9_2_False_1_150', 'blackbird_0_x0_150_1_SENSEX_R_1.4_3_0.2_0.8_2_False_2_100', 'blackbird_0_x0_215_2_SENSEX_R_1.2_3_0.3_0.9_1_False_1_250', 'blackbird_0_x0_40_1_SENSEX_PCT_0.0016_3_0.35_0.7_1_False_1_100', 'blackbird_0_x0_140_1_SENSEX_PCT_0.0012_3_0.25_0.8_2_False_1_100', 'zzsex0_SENSEX_0_s2_30_10_4_2_PCT_0.001_5_3_0.5_PCT_1.8_False_3_0.99_True_True_-4000_1600_800_600_540', 'zzsex0_SENSEX_0_x2_10_60_2_1_PCT_0.0025_5_1_0.3_PCT_0.1_False_2_0.99_False_False_-3400_0_0_0_0', 'spikesex1_SENSEX_0_x1_10_20_1_0_P_50_3_10_0.05_0.02_2_0.05_0.0_ABS_130_False_0_4_0.0_0.8_False_True_-4600_1200_480_200_180', 'zzsex0_SENSEX_0_x1_3_0_4_1_PCT_0.002_3_2_0.5_PCT_2.0_False_0_0.99_True_False_-2900_0_0_0_0', 'spikesex1_SENSEX_0_s2_15_0_3_0_M_8_5_2_0.2_0.01_4_0.1_0.07_ABS_110_True_0_0_0.0_0.8_True_True_-1700_1500_1050_900_630', 'spikesex1_SENSEX_0_x1_45_0_3_0_M_5_5_5_1.5_0.15_1_0.0_0.3_ABS_185_False_0_3_0.0_0.75_False_False_-4900_0_0_0_0', 'spikesex1_SENSEX_0_x1_20_30_1_0_M_5_3_5_0.75_0.15_1_0.0_0.07_ABS_220_True_1_1_0.1_0.75_False_True_-3100_1800_720_500_450', 'spikesex1_SENSEX_0_x1_45_10_3_0_M_6_3_3_0.2_0.2_4_0.2_0.35_ABS_55_True_1_5_0.1_0.25_True_True_-1200_1300_520_600_300', 'spikesex1_SENSEX_0_x1_10_0_2_0_M_5_5_3_0.2_0.05_0_0.0_0.0_ABS_20_False_4_3_0.0_0.8_False_True_-2500_1500_1050_200_60', 'al_0_x0_210_1_SENSEX_PCT_0.0016_3_0.4_0.7_2_False_True', 'al_0_x0_140_1_SENSEX_R_1.2_3_0.5_0.9_3_False_True', 'al_0_x0_170_2_SENSEX_PCT_0.002_3_0.5_0.7_2_False_True', 'al_0_x0_200_1_SENSEX_PCT_0.0016_3_0.4_0.9_2_False_True', 'al_0_x0_130_2_SENSEX_PCT_0.0028_3_0.55_0.9_2_False_True', 'al_0_x0_50_2_SENSEX_R_1.2_3_0.55_0.8_2_False_True', 'al_0_x0_160_2_SENSEX_PCT_0.0026_3_0.4_0.8_3_False_True', 'al_0_x0_190_1_SENSEX_R_1.2_3_0.5_0.8_1_False_True', 'al_0_x0_120_1_SENSEX_R_1.0_3_0.55_0.7_2_False_True', 'al_0_x0_150_2_SENSEX_PCT_0.0018_3_0.55_0.9_3_False_True', 'al_0_x0_150_1_SENSEX_R_1.2_3_0.55_0.9_2_False_True', 'al_0_x0_50_2_SENSEX_R_1.0_3_0.4_0.8_3_False_True', 'al_0_x0_170_2_SENSEX_PCT_0.0014_3_0.45_0.9_2_False_True', 'al_0_x0_70_1_SENSEX_PCT_0.0024_3_0.5_0.8_2_False_True', 'al_0_x0_130_2_SENSEX_R_1.4_3_0.4_0.9_3_False_True', 'als_0_x0_170_1_SENSEX_PCT_0.002_3_0.55_0.7_3_False', 'als_0_x0_10_1_SENSEX_PCT_0.0026_3_0.5_0.8_3_False', 'als_0_x0_80_1_SENSEX_R_1.3_3_0.4_0.9_3_False', 'als_0_x0_190_1_SENSEX_R_1.2_3_0.5_0.9_2_False', 'als_0_x0_220_1_SENSEX_R_1.2_3_0.5_0.9_2_False', 'als_0_x0_40_2_SENSEX_PCT_0.0016_3_0.45_0.7_3_False', 'als_0_x0_180_1_SENSEX_PCT_0.0012_3_0.5_0.7_1_False', 'als_0_x0_30_1_SENSEX_PCT_0.0014_3_0.45_0.9_3_False', 'als_0_x0_60_2_SENSEX_R_1.0_3_0.5_0.8_3_False', 'als_0_x0_230_2_SENSEX_R_1.3_3_0.55_0.7_2_False', 'als_0_x0_20_1_SENSEX_PCT_0.0028_3_0.4_0.9_2_False', 'als_0_x0_110_2_SENSEX_PCT_0.0018_3_0.5_0.8_2_False', 'als_0_x0_10_1_SENSEX_R_1.0_3_0.4_0.9_3_False', 'als_0_x0_70_1_SENSEX_R_1.3_3_0.5_0.7_3_False', 'als_0_x0_160_1_SENSEX_PCT_0.002_3_0.55_0.8_3_False', 'als_0_x0_190_1_SENSEX_PCT_0.002_3_0.45_0.7_1_False', 'als_0_x0_100_1_SENSEX_R_1.2_3_0.4_0.8_3_False', 'als_0_x0_90_1_SENSEX_PCT_0.0012_3_0.55_0.9_3_False', 'als_0_x0_80_1_SENSEX_R_1.0_3_0.45_0.9_3_False', 'als_0_x0_40_1_SENSEX_PCT_0.0012_3_0.45_0.7_3_False', 'als_0_x0_50_1_SENSEX_R_1.1_3_0.5_0.9_3_False', 'als_0_x0_90_1_SENSEX_PCT_0.002_3_0.4_0.8_3_False', 'als_0_x0_170_2_SENSEX_PCT_0.0016_3_0.4_0.7_2_False', 'olre_0_x0_180_1_SENSEX_PCT_0.0012_3_0.45_0.9_1_False_True_True', 'olre_0_x0_230_1_SENSEX_PCT_0.0026_3_0.55_0.8_1_False_True_True', 'olre_0_x0_90_1_SENSEX_PCT_0.0014_3_0.45_0.8_3_False_True_True', 'olre_0_x0_170_2_SENSEX_PCT_0.001_3_0.5_0.8_2_False_True_True', 'olre_0_x0_40_1_SENSEX_PCT_0.002_3_0.55_0.8_3_False_True_True', 'olre_0_x0_10_1_SENSEX_R_1.0_3_0.45_0.7_3_False_True_True', 'olre_0_x0_100_2_SENSEX_PCT_0.0026_3_0.4_0.8_3_False_True_True', 'olre_0_x0_180_1_SENSEX_PCT_0.002_3_0.45_0.9_1_False_True_True', 'olre_0_x0_140_2_SENSEX_PCT_0.0012_3_0.5_0.8_3_False_True_True', 'olre_0_x0_90_2_SENSEX_PCT_0.0016_3_0.5_0.8_2_False_True_True', 'olre_0_x0_170_1_SENSEX_R_1.2_3_0.55_0.8_3_False_True_True', 'olre_0_x0_60_2_SENSEX_R_1.1_3_0.5_0.7_3_False_True_True', 'olre_0_x0_210_2_SENSEX_R_1.1_3_0.4_0.9_2_False_True_True', 'olre_0_x0_150_2_SENSEX_PCT_0.0028_3_0.45_0.9_3_False_True_True', 'olre_0_x0_20_2_SENSEX_PCT_0.001_3_0.45_0.8_3_False_True_True', 'olre_0_x0_60_2_SENSEX_PCT_0.0018_3_0.55_0.9_3_False_True_True', 'olre_0_x0_160_2_SENSEX_PCT_0.002_3_0.45_0.9_2_False_True_True', 'olre_0_x0_140_1_SENSEX_PCT_0.0024_3_0.55_0.7_2_False_True_True', 'olre_0_x0_150_1_SENSEX_PCT_0.0014_3_0.45_0.9_2_False_True_True', 'olre_0_x0_60_2_SENSEX_R_1.0_3_0.4_0.7_2_False_True_True', 'stg5dir_0_x0_190_2_SENSEX_PCT_0.0014_3_0.55_0.9_2_False_0.2', 'stg5dir_0_x0_80_2_SENSEX_R_1.0_3_0.45_0.8_2_False_0.2', 'stg5dir_0_x0_20_1_SENSEX_R_1.4_3_0.4_0.8_2_False_0.2', 'stg5dir_0_x0_30_2_SENSEX_R_1.4_3_0.5_0.8_3_False_0.2', 'stg5dir_0_x0_80_2_SENSEX_R_1.3_3_0.4_0.7_2_False_0.2', 'stg5dir_0_x0_0_2_SENSEX_R_1.0_3_0.4_0.9_2_False_0.2', 'stg5dir_0_x0_0_1_SENSEX_R_1.4_3_0.45_0.7_2_False_0.2', 'stg5dir_0_x0_210_1_SENSEX_PCT_0.001_3_0.45_0.7_1_False_0.2', 'stg5dir_0_x0_110_2_SENSEX_R_1.2_3_0.45_0.9_2_False_0.2', 'stg5dir_0_x0_220_2_SENSEX_R_1.1_3_0.4_0.9_1_False_0.2', 'stg5dir_0_x0_90_2_SENSEX_R_1.2_3_0.4_0.8_2_False_0.2', 'stg5dir_0_x0_120_1_SENSEX_PCT_0.0018_3_0.55_0.7_2_False_0.2', 'stg5dir_0_x0_30_2_SENSEX_PCT_0.0016_3_0.4_0.7_2_False_0.2', 'stg5dir_0_x0_180_1_SENSEX_R_1.1_3_0.55_0.8_2_False_0.2', 'stg5dir_0_x0_220_2_SENSEX_PCT_0.0026_3_0.4_0.9_1_False_0.2', 'stg5dir_0_x0_230_2_SENSEX_PCT_0.0012_3_0.55_0.9_2_False_0.2', 'stg5dir_0_x0_210_2_SENSEX_PCT_0.0016_3_0.4_0.9_1_False_0.2', 'stg5dir_0_x0_30_1_SENSEX_PCT_0.0014_3_0.45_0.7_3_False_0.2', 'stg5dir_0_x0_230_2_SENSEX_PCT_0.002_3_0.55_0.7_2_False_0.2', 'stg5dir_0_x0_10_2_SENSEX_PCT_0.0014_3_0.55_0.8_2_False_0.2', 'stg5dir_0_x0_90_2_SENSEX_PCT_0.0022_3_0.45_0.8_2_False_0.2', 'stg5dir_0_x0_70_1_SENSEX_PCT_0.0024_3_0.45_0.7_3_False_0.2', 'stg5dir_0_x0_150_1_SENSEX_PCT_0.001_3_0.5_0.9_3_False_0.2', 'stg5dir_0_x0_190_1_SENSEX_R_1.3_3_0.4_0.9_1_False_0.2', 'al_0_x0_150_1_SENSEX_R_1.2_3_0.55_0.9_2_False_True', 'als_0_x0_20_1_SENSEX_PCT_0.0028_3_0.4_0.9_2_False', 'als_0_x0_70_1_SENSEX_R_1.3_3_0.5_0.7_3_False', 'als_0_x0_160_1_SENSEX_PCT_0.002_3_0.55_0.8_3_False', 'olre_0_x0_150_2_SENSEX_PCT_0.0028_3_0.45_0.9_3_False_True_True', 'olre_0_x0_60_2_SENSEX_R_1.0_3_0.4_0.7_2_False_True_True', 'stg5dir_0_x0_190_2_SENSEX_PCT_0.0014_3_0.55_0.9_2_False_0.2', 'stg5dir_0_x0_220_2_SENSEX_R_1.1_3_0.4_0.9_1_False_0.2', 'stg5dir_0_x0_90_2_SENSEX_R_1.2_3_0.4_0.8_2_False_0.2', 'stg5dir_0_x0_220_2_SENSEX_PCT_0.0026_3_0.4_0.9_1_False_0.2', 'tridentdir_0_x0_20_2_SENSEX_R_1.0_3_0.35_0.8_2_False_3_1', 'tridentdir_0_x0_30_2_SENSEX_R_1.3_3_0.3_0.7_2_False_3_1', 'tridentdir_0_x0_180_2_SENSEX_PCT_0.0012_3_0.25_0.8_1_False_2_1', 'tridentdir_0_x0_15_2_SENSEX_R_1.3_3_0.3_0.9_2_False_3_1', 'tridentdir_0_x0_10_2_SENSEX_R_1.2_3_0.3_0.9_1_False_3_1', 'tridentdir_0_x0_75_2_SENSEX_R_1.1_3_0.35_0.9_2_False_3_1', 'tridentdir_0_x0_190_2_SENSEX_PCT_0.0014_3_0.3_0.8_1_False_2_1', 'tridentdir_0_x0_155_1_SENSEX_R_1.2_3_0.3_0.9_1_False_4_1', 'blackbird_0_x0_5_2_SENSEX_PCT_0.0028_3_0.3_0.7_1_False_1_150', 'zzsex0_SENSEX_0_x2_10_60_2_1_PCT_0.0025_5_1_0.3_PCT_0.1_False_2_0.99_False_False_-3400_0_0_0_0']);
  };

  strategySocket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    // Handle the received chart data

    strategy_mtm_chart_BackendData.value = data.strategy_mtm_chart_data;

  };
  strategySocket.onerror = function (error) {
    console.log(`[error] ${error.message}`);
  };

  function sendStrategyUIDs(uids) {
    strategySocket.send(JSON.stringify({ strategy_uids: uids }));
  }


  strategySocket.onclose = (event) => {
    console.log('Strategy Chart WebSocket connection closed:', event.reason);
    // Implement reconnection logic if needed
  }

  return strategySocket;
}


const reconnect = () => {
  if (reconnectAttempts < maxReconnectAttempts) {
    reconnectAttempts++
    console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})...`)
    setTimeout(connectWebSocket, reconnectInterval)
  } else {
    console.log('Max reconnection attempts reached. Please refresh the page.')
  }
}

let pingIntervalId = null

const startPingInterval = () => {
  pingIntervalId = setInterval(() => {
    if (socket.readyState === WebSocket.OPEN) {
      socket.send('ping')
    }
  }, pingInterval)
}

const stopPingInterval = () => {
  if (pingIntervalId) {
    clearInterval(pingIntervalId)
    pingIntervalId = null
  }
}


onMounted(() => {
  connectWebSocket()
  connectBasketChartWebSocket()
  connectStrategyChartWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
  stopPingInterval()
})
</script>



<template>
  <div class="homePage_Container bg-[#efefef]/30">
    <LightWeightChart v-if="Object.keys(basket_BackendData).length" :Chartdata="basket_BackendData" />
    <LightWeightChart v-if="Object.keys(strategy_mtm_chart_BackendData).length"
      :Chartdata="strategy_mtm_chart_BackendData" />
    <div v-if="index_data" class="nav_index_container font-semibold bg-white  drop-shadow-sm">
      <p>BANKNIFTY : {{ index_data.BANKNIFTYSPOT ? index_data.BANKNIFTYSPOT : 0 }}</p>
      <p>FINNIFTY : {{ index_data.FINNIFTYSPOT ? index_data.FINNIFTYSPOT : 0 }}</p>
      <p>MIDCPNIFTY : {{ index_data.MIDCPNIFTYSPOT ? index_data.MIDCPNIFTYSPOT : 0 }}</p>
      <p>NIFTY : {{ index_data.NIFTYSPOT ? index_data.NIFTYSPOT : 0 }}</p>
      <p> SENSEX : {{ index_data.SENSEXSPOT ? index_data.SENSEXSPOT : 0 }}</p>
    </div>
    <div class="time-container">
      <p class="timeDiv"> Time:{{ time }}</p>
      <WarningSignal :signals="pulse_signal" :latency="Latency" :max_latency="max_latency" />
    </div>


    <div class="mx-auto px-8 py-8">
      <div class="my-8">
        <p class="table-heading">Accounts</p>
        <TanStackTestTable :data="data" :columns="columns" :hasColor="['IdealMTM', 'Day_PL', 'Friction']"
          :navigateTo="NavigationMap" :showPagination=true
          :hasRowcolor="{ 'columnName': 'AccountName', 'arrayValues': user_infected }" />
      </div>




      <div class="my-8">
        <p class="table-heading">Basket-wise Ideal MTM</p>
        <MultiLineChart :data="basket_chart_data" :keys="basket_chart_name">
        </MultiLineChart>
      </div>




    </div>
  </div>
</template>


<style>
html {
  font-size: 14px;
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
  align-items: center;
  display: flex;
  width: 100%;
}
</style>