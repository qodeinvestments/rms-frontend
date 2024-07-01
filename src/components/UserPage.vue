<script setup>


import { onMounted, onUnmounted } from 'vue'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'
import { ref } from 'vue'
import { useRoute } from 'vue-router';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue'



const route = useRoute();
const user_data = ref('')

const defaultData = [{
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
}];
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




const messages = ref([])


let eventSource = null



const data = ref([])


const connectToSSE = () => {
  eventSource = new EventSource('http://localhost:5000/stream')


  eventSource.onmessage = (event) => {

    let c_d = JSON.parse(event.data);
    let response = JSON.parse(c_d)
    let result = response.client_data.find(client => client.name === name.value);
    result = result
    user_data.value = result;

    data.value = [{
      AccountName: result.name,
      IdealMTM: Number(result.ideal_MTM),
      Day_PL: Number(result.MTM),
      RejectedOrderCount: Number(result.Rejected_orders),
      PendingOrderCount: Number(result.Pending_orders)

    }]
  }

  eventSource.onopen = () => {
    messages.value.push('Connection opened')
  }
  eventSource.onerror = () => {
    messages.value.push('Error occurred')
    eventSource.close()
  }
}

const name = ref('');

onMounted(() => {
  connectToSSE();
  name.value = route.params.username;
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})




</script>

<template>

  <div class="container mx-auto px-8 py-8 pageContainer">
    <div class="container mx-auto px-8 py-8">

      <!-- <TableOriginal /> -->
      <!-- <TableTanstack :data="people" :columns="columnsPeople" />

<div class="my-8">
<TableTanstack :data="cars" :columns="columnsCars" />
</div> -->
      <div class="my-8">
        <TanStackTestTable :data="data" :columns="columns" :hasColor="['IdealMTM', 'Day_PL']" :navigateTo="[]"
          :showPagination=false />
      </div>


    </div>

    <!-- <p class="headingContainer">{{ name }}</p>
    <div class="profitContainer">
      <div class="priceContainer">
        <p class="labeltag">Portfolio Value : </p>
        <p>3423424</p>
      </div>
      <div class="priceContainer">
        <p class="labeltag">Day Profit And Loss : </p>
        <p>3423424</p>
      </div>
      <div class="priceContainer">
        <p class="labeltag">Ideal Profit And Loss : </p>
        <p>3423424</p>
      </div>

    </div> -->


    <Chart v-if="user_data" :data="user_data['MTMTable']" :lineNames="['MTM']" />
  </div>


</template>

<style scoped>
.pageContainer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.profitContainer {
  border: 1px solid black;
  height: auto;
  padding: 20px;

  width: fit-content;
  border-radius: 10px;
  display: flex;
  font-size: 30px;
  align-items: flex-start;
  flex-direction: column;

}

.priceContainer {
  display: flex;
  align-items: baseline;
  gap: 20px;
}

html {
  font-family: poppins;
  font-size: 14px;
}

.labeltag {
  font-size: 20px;
}

.headingContainer {
  font-size: 30px;
  font-weight: bold;

}
</style>