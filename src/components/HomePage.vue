<script setup>
import { onMounted, onUnmounted } from 'vue'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'
import SignalForTable from './SignalForTable.vue'
import { ref,h } from 'vue'
import axios from 'axios';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue'
import MultiLineChart from './HighCharts.vue'
import WarningSignal from './WarningSignal.vue'
import { map } from 'highcharts';
const defaultData = []
const NavigationMap = {
  "AccountName": "/user/"
};

const data = ref(defaultData)

const columnHelper = createColumnHelper()
const columns = [
  columnHelper.accessor(row => row.AccountName, {
    id: 'Working',
    cell: ({row}) => h(SignalForTable, {color: true}),
    header: () => 'Account Name',
  }),
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

const connectToSSE = () => {
  eventSource = new EventSource('https://api.swancapital.in/stream')

  eventSource.onmessage = (event) => {
    try {
        // Parse the event data
        let mapobj = JSON.parse(event.data);
        console.log("response data", mapobj);

        // Check if live_index and client_data are present in the parsed object
        if (mapobj && mapobj.live_index && Array.isArray(mapobj.client_data)) {
            index_data.value = mapobj.live_index;

            let clients_data = mapobj.client_data;

            // Transform client_data and update the data.value
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
                NetQuantity: item.NetQuantity !== undefined ? Number(item.NetQuantity) : 0
            }));

            // Logging other parts of the response for future use
            console.log("basket_data", mapobj.basket_data);
            console.log("live_positions", mapobj.live_positions);
            console.log("pulse", mapobj.pulse);

            // Update additional values
            pulse_signal.value = mapobj.pulse;
            MTMTable.value = clients_data[0]["MTMTable"];
            basket_chart_name.value = mapobj.basket_data.map(obj => Object.keys(obj)[0]);
            basket_chart_data.value = mapobj.basket_data.map(obj => Object.values(obj)[0]);
        } else {
            console.error('Invalid structure of mapobj:', mapobj);
        }
    } catch (error) {
        console.error('Error parsing event data or updating data:', error);
    }
}


  eventSource.onopen = () => {
    messages.value.push('Connection opened')
  }

  eventSource.onerror = () => {
    messages.value.push('Error occurred')
    eventSource.close()
  }
}

onMounted(() => {
  connectToSSE()
  // axios.get('http://localhost:8001/api/message')
  //   .then(function (response) {
  //     console.log(response);
  //   })
  //   .catch((error) => {
  //     console.log(error);
  //   })
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})

</script>

<template>

  <div class="homePage_Container bg-[#efefef]/30">
    
    <SignalForTable :color="true" />


    <WarningSignal :signals="pulse_signal" />
    <div class="mx-auto px-8 py-8">

      <!-- <TableOriginal /> -->
      <!-- <TableTanstack :data="people" :columns="columnsPeople" />

  <div class="my-8">
    <TableTanstack :data="cars" :columns="columnsCars" />
  </div> -->
      <div class="my-8">
        <TanStackTestTable :data="data" :columns="columns" :hasColor="['IdealMTM', 'Day_PL', 'Friction']"
          :navigateTo="NavigationMap" :showPagination=true />
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
</style>