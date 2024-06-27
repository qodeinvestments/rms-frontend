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


const route = useRoute();

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



const messages = ref([])
let eventSource = null

const connectToSSE = () => {
  eventSource = new EventSource('http://localhost:5000/stream')

  eventSource.onmessage = (event) => {
    const Value = Number(JSON.parse(event.data))
    const updatedData = [...data.value]
    updatedData[0]['PortfolioValue'] = Value// Update the age
    data.value = updatedData
    console.log(Value, "  ", data.value)
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


    <p class="headingContainer">{{ name }}</p>
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

    </div>

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