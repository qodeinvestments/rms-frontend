<script setup>
import { onMounted, onUnmounted } from 'vue'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'
import SignalForTable from './SignalForTable.vue'
import { ref, h } from 'vue'
import axios from 'axios';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue'
import MultiLineChart from './HighCharts.vue'
import WarningSignal from './WarningSignal.vue'
import { map } from 'highcharts';
import { MyEnum } from '../Enums/Prefix.js';
const defaultData = []
const NavigationMap = {
  "AccountName": "/user/"
};

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
  columnHelper.accessor(row => row.MARGIN, {
    id: 'MARGIN',
    cell: info => info.getValue(),
    header: () => 'Margin',
  }),
  columnHelper.accessor(row => row.VAR, {
    id: 'VAR',
    cell: info => info.getValue(),
    header: () => 'VAR',
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



const index_data = ref("hello")
const messages = ref([])
const MTMTable = ref([])
const basket_chart_data = ref([])
const basket_chart_name = ref([])
let eventSource = null
const pulse_signal = ref([])
const time = ref([])
const user_infected = ref([])
const checkBackendConnection = ref(true)

const connectToSSE = () => {
  const eventSource = new EventSource(MyEnum.backendURL);

  eventSource.onmessage = (event) => {
    try {
      // Parse the event data
      let mapobj = JSON.parse(event.data);

      console.log(mapobj)
      // Check if live_index and client_data are present in the parsed object
      if (mapobj && mapobj.live_index && Array.isArray(mapobj.client_data)) {
        checkBackendConnection.value = true;
        index_data.value = mapobj.live_index;

        let clients_data = mapobj.client_data;
        time.value = mapobj.time;


        user_infected.value = Object.keys(mapobj.pulse)
          .filter(key => (key.startsWith('pulse_trader_xts:') || key.startsWith('pulse_trader_zerodha:')) && mapobj.pulse[key] === false)
          .map(key => key.split(':')[1]);




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
          VAR: item.Live_Client_Var !== undefined ? Number(item.Live_Client_Var) : 0,
        }));

        // Logging other parts of the response for future use
        // console.log("basket_data", mapobj.basket_data);
        // console.log("live_positions", mapobj.live_positions);
        // console.log("pulse", mapobj.pulse);

        // Update additional values
        pulse_signal.value = mapobj.pulse;
        pulse_signal.value.backendConnection = checkBackendConnection;
        MTMTable.value = clients_data[0]["MTMTable"];
        basket_chart_name.value = mapobj.basket_data.map(obj => Object.keys(obj)[0]);
        basket_chart_data.value = mapobj.basket_data.map(obj => Object.values(obj)[0]);
      } else {
        checkBackendConnection.value = false;
        console.error('Invalid structure of mapobj:', mapobj);
      }
    } catch (error) {
      checkBackendConnection.value = false;
      console.error('Error parsing event data or updating data:', error);
    }
  };

  eventSource.onopen = () => {
    checkBackendConnection.value = false;
    messages.value.push('Connection opened');
  };

  eventSource.onerror = (error) => {
    checkBackendConnection.value = false;
    messages.value.push('Error occurred');

    if (error.target.readyState === EventSource.CLOSED) {
      messages.value.push('Connection closed');
      setTimeout(() => {
        connectToSSE();  // Attempt to reconnect
      }, 2000);  // Retry connection after 5 seconds
    } else if (error.target.readyState === EventSource.CONNECTING) {
      messages.value.push('Reconnecting...');
    }

    // If the error is due to a 404, attempt to reconnect
    if (error.status === 404) {
      messages.value.push('404 error occurred, attempting to reconnect');
      eventSource.close();
      setTimeout(() => {
        connectToSSE();  // Attempt to reconnect
      }, 2000);  // Retry connection after 5 seconds
    }
  };
};




onMounted(() => {
  connectToSSE();
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})

</script>

<template>


  <div class="homePage_Container bg-[#efefef]/30">
    <div class="nav_index_container font-semibold bg-white  drop-shadow-sm">
      <p>BANKNIFTY : {{ index_data.BANKNIFTYSPOT }}</p>
      <p>FINNIFTY : {{ index_data.FINNIFTYSPOT }}</p>
      <p>MIDCPNIFTY : {{ index_data.MIDCPNIFTYSPOT }}</p>
      <p>NIFTY : {{ index_data.NIFTYSPOT }}</p>
      <p> SENSEX : {{ index_data.SENSEXSPOT }}</p>
    </div>

    <div class="time-container">
      <p class="timeDiv"> Time:{{ time }}</p>
      <WarningSignal :signals="pulse_signal" />
    </div>

    <div class="mx-auto px-8 py-8">

      <!-- <TableOriginal /> -->
      <!-- <TableTanstack :data="people" :columns="columnsPeople" />

  <div class="my-8">
    <TableTanstack :data="cars" :columns="columnsCars" />
  </div> -->
      <div class="my-8">
        <TanStackTestTable :data="data" :columns="columns" :hasColor="['IdealMTM', 'Day_PL', 'Friction']"
          :navigateTo="NavigationMap" :showPagination=true
          :hasRowcolor="{ 'columnName': 'AccountName', 'arrayValues': user_infected }" />
      </div>


      <!-- 
      <Chart v-if="basket_chart_data.length > 0" :data="basket_chart_data" :labels="chart_labels" /> -->

      <MultiLineChart v-if="basket_chart_data.length > 0" :chartData="basket_chart_data"
        :lineNames="basket_chart_name" />
    </div>
  </div>
</template>

<style>
html {
  font-size: 14px;
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