<script setup>
import { onMounted, onUnmounted } from 'vue'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'
import { ref } from 'vue'
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue'



const defaultData = [
  {
    "id": 1,
    "AccountName": "Abhinav",
    "IdealMTM": 0,
    "PortfolioValue": "250000",
    "Day_PL": "25000",
    "PositionDayPL": "25000000000",
    "HoldingsDayPL": 250000,
    "TotalOrderCount": 250000,
    "OpenOrderCount": 40,
    "CompleteOrderCount": 10,
    "PositionsCount": 20,
    "HoldingsCount": 10,
    "Used_Margin": 50000,
    "AvailableMargin": 250000,
    "Cash": 2500000
  },
  {
    "id": 2,
    "AccountName": "chirag",
    "IdealMTM": 0,
    "PortfolioValue": "250000",
    "Day_PL": "25000",
    "PositionDayPL": "25000000000",
    "HoldingsDayPL": 250000,
    "TotalOrderCount": 250000,
    "OpenOrderCount": 40,
    "CompleteOrderCount": 10,
    "PositionsCount": 20,
    "HoldingsCount": 10,
    "Used_Margin": 50000,
    "AvailableMargin": 250000,
    "Cash": 2500000
  },
  {
    "id": 3,
    "AccountName": "ashwin",
    "IdealMTM": 0,
    "PortfolioValue": "250000",
    "Day_PL": "25000",
    "PositionDayPL": "25000000000",
    "HoldingsDayPL": 250000,
    "TotalOrderCount": 250000,
    "OpenOrderCount": 40,
    "CompleteOrderCount": 10,
    "PositionsCount": 20,
    "HoldingsCount": 10,
    "Used_Margin": 50000,
    "AvailableMargin": 250000,
    "Cash": 2500000
  },

]
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




const messages = ref([])
const MTMTable = ref([])
let eventSource = null

const connectToSSE = () => {
  eventSource = new EventSource('http://localhost:5000/stream')

  eventSource.onmessage = (event) => {
    let client_data = JSON.parse(event.data);

    let mapobj = JSON.parse(client_data);

    const updatedData = [...data.value]
    updatedData[0]['Day_PL'] = Number(mapobj[0]['MTM'])// Update the age
    updatedData[0]['IdealMTM'] = Number(mapobj[0]['ideal_MTM'])// Update the age
    updatedData[0]['AccountName'] = mapobj[0]['name']// Update the age
    MTMTable.value = mapobj[0]["MTMTable"]
    data.value = updatedData
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
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})


</script>

<template>
  <div class="homePage_Container">

    <div class="container mx-auto px-8 py-8">

      <!-- <TableOriginal /> -->
      <!-- <TableTanstack :data="people" :columns="columnsPeople" />

  <div class="my-8">
    <TableTanstack :data="cars" :columns="columnsCars" />
  </div> -->
      <div class="my-8">
        <TanStackTestTable :data="data" :columns="columns" :hasColor="['IdealMTM', 'Day_PL']"
          :navigateTo="NavigationMap" />
      </div>
      <Chart :data="MTMTable" />

    </div>

  </div>


</template>

<style>
html {
  font-family: sans-serif;
  font-size: 14px;
}
</style>