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






// onMounted(() => {

//   console.log('in mounted')
//   const socket = new WebSocket('ws://localhost:8000/ws')
//   console.log(socket)
//   socket.onmessage = (event) => {
//     const updatedData = [...data.value]
//     updatedData[0]['PortfolioValue'] = Number(event.data) // Update the age
//     data.value = updatedData
//     console.log(event.data, "  ", data.value)
//   }

//   socket.onclose = () => {
//     console.log('WebSocket connection closed.')
//   }
//   socket.onerror = (e) => {
//     console.log(e)
//   }

// })

const client_BackendData = ref([])
const connection_BackendData = ref([])
const basket_BackendData = ref([])
const strategy_mtm_chart_BackendData = ref([])

const index_data = ref("hello")
const messages = ref([])
const basket_chart_data = ref([])
const basket_chart_name = ref([])
const strategy_mtm_chart_data = ref([])
const strategy_mtm_chart_name = ref([])
const pulse_signal = ref([])
const time = ref([])
const user_infected = ref([])
const checkBackendConnection = ref(true)
let socket = null

const handleMessage = (message) => {
  if (message.channel === "client_dashboard_data") {
    client_BackendData.value = message.data
  } else if (message.channel === 'basket_dashboard_data') {
    basket_BackendData.value = message.data
  } else if (message.channel === 'connection_dashboard_data') {
    connection_BackendData.value = message.data
  } else if (message.channel === 'strategy_mtm_chart_data') {
    strategy_mtm_chart_BackendData.value = message.data
  }

  updateData()
}

const updateData = () => {
  checkBackendConnection.value = true
  index_data.value = connection_BackendData.value.live_index

  let clients_data = client_BackendData.value.client_data
  let basket_data = basket_BackendData.value.basket_data
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

  if (basket_data) {
    basket_chart_name.value = basket_data.map(obj => Object.keys(obj)[0])
    basket_chart_data.value = basket_data.map(obj => Object.values(obj)[0])
  }
}

onMounted(() => {
  console.log('in mounted')
  socket = new WebSocket('ws://localhost:5000/ws')  // Update this URL to match your backend
  console.log(socket)

  socket.onopen = () => {
    console.log('WebSocket connection opened')
    checkBackendConnection.value = true
  }

  socket.onmessage = (event) => {
    const message = JSON.parse(event.data)
    handleMessage(message)
  }

  socket.onclose = () => {
    console.log('WebSocket connection closed.')
    checkBackendConnection.value = false
  }

  socket.onerror = (e) => {
    console.log('WebSocket error:', e)
    checkBackendConnection.value = false
  }
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>

<template>
  <div class="homePage_Container bg-[#efefef]/30">
    <div v-if="index_data" class="nav_index_container font-semibold bg-white  drop-shadow-sm">
      <p>BANKNIFTY : {{ index_data.BANKNIFTYSPOT ? index_data.BANKNIFTYSPOT : 0 }}</p>
      <p>FINNIFTY : {{ index_data.FINNIFTYSPOT ? index_data.FINNIFTYSPOT : 0 }}</p>
      <p>MIDCPNIFTY : {{ index_data.MIDCPNIFTYSPOT ? index_data.MIDCPNIFTYSPOT : 0 }}</p>
      <p>NIFTY : {{ index_data.NIFTYSPOT ? index_data.NIFTYSPOT : 0 }}</p>
      <p> SENSEX : {{ index_data.SENSEXSPOT ? index_data.SENSEXSPOT : 0 }}</p>
    </div>
    <div class="time-container">
      <p class="timeDiv"> Time:{{ time }}</p>
      <WarningSignal :signals="pulse_signal" />
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

      <div v-for="(value, key) in strategy_mtm_chart_BackendData" :key="key">
        <h3>{{ key }}</h3>
        <ul>
          <li v-for="(nestedValue, nestedKey) in value" :key="nestedKey">
            {{ nestedKey }}: {{ nestedValue }}
          </li>
        </ul>
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