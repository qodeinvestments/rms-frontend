<script setup>
import { onMounted, onUnmounted } from 'vue'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'

import { ref } from 'vue'
import axios from 'axios';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue'
import MultiLineChart from './HighCharts.vue'
import WarningSignal from './WarningSignal.vue'
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
let eventSource = null

const connectToSSE = () => {
  eventSource = new EventSource('http://139.5.189.188:5000')

  eventSource.onmessage = (event) => {
    let Response = JSON.parse(event.data);

    let mapobj = JSON.parse(Response);
    index_data.value = mapobj.live_index;
    let clients_data = mapobj.client_data


    // const updatedData = [...data.value]
    // updatedData[0]['Day_PL'] = Number(mapobj[0]['MTM'])// Update the age
    // updatedData[0]['IdealMTM'] = Number(mapobj[0]['ideal_MTM'])// Update the age
    // updatedData[0]['AccountName'] = mapobj[0]['name']// Update the age

    data.value = clients_data.map(item => ({
      AccountName: item.name,
      IdealMTM: Number(item.ideal_MTM),
      Day_PL: Number(item.MTM),
      Friction: (Number(item.MTM) - Number(item.ideal_MTM)).toFixed(2),
      RejectedOrderCount: Number(item.Rejected_orders),
      PendingOrderCount: Number(item.Pending_orders),
      OpenQuantity: Number(item.OpenQuantity),
      NetQuantity: Number(item.NetQuantity)

    }));

    MTMTable.value = clients_data[0]["MTMTable"]
    basket_chart_data.value = mapobj.basket_data
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

    <div class="nav_index_container font-semibold bg-white  drop-shadow-sm">
      <p>BANKNIFTY : {{ index_data.BANKNIFTYSPOT }}</p>
      <p>FINNIFTY : {{ index_data.FINNIFTYSPOT }}</p>
      <p>MIDCPNIFTY : {{ index_data.MIDCPNIFTYSPOT }}</p>
      <p>NIFTY : {{ index_data.NIFTYSPOT }}</p>
      <p> SENSEX : {{ index_data.SENSEXSPOT }}</p>
    </div>


    <WarningSignal />
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
        :lineNames="['Directional', 'NikBuy', 'Non-Directional']" />
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