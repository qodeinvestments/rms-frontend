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




const defaultData = [
  {
    "id": 1,
    "AccountName": "Abhinav",
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
const data = ref(defaultData)

const columnHelper = createColumnHelper()

const columns = [
  columnHelper.accessor(row => row.AccountName, {
    id: 'AccountName',
    cell: info => info.getValue(),
    header: () => 'Account Name',
  }),
  columnHelper.accessor(row => row.PortfolioValue, {
    id: 'PortfolioValue',
    cell: info => info.getValue(),
    header: () => 'Portfolio Value',
  }),
  columnHelper.accessor(row => row.Day_PL, {
    id: 'Day_PL',
    cell: info => info.getValue(),
    header: () => 'Day_PL',
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






onMounted(() => {

  console.log('in mounted')
  const socket = new WebSocket('ws://localhost:8000/ws')
  console.log(socket)
  socket.onmessage = (event) => {
    const updatedData = [...data.value]
    updatedData[0]['PortfolioValue'] = Number(event.data) // Update the age
    data.value = updatedData
    console.log(event.data, "  ", data.value)
  }

  socket.onclose = () => {
    console.log('WebSocket connection closed.')
  }
  socket.onerror = (e) => {
    console.log(e)
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
        <TanStackTestTable :data="data" :columns="columns" />
      </div>
    </div>

  </div>


</template>

<style>
html {
  font-family: sans-serif;
  font-size: 14px;
}

table {
  border: 1px solid lightgray;
}

tbody {
  border-bottom: 1px solid lightgray;
}

th {
  border-bottom: 1px solid lightgray;
  border-right: 1px solid lightgray;
  padding: 2px 4px;
}

tfoot {
  color: gray;
}

tfoot th {
  font-weight: normal;
}
</style>
