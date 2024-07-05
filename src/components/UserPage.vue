<script setup>


import { onMounted, onUnmounted } from 'vue'
import BarChart from './Barchart.vue';
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'

import { MyEnum } from '../Enums/Prefix.js';
import { ref } from 'vue'
import { useRoute } from 'vue-router';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue';

import MultiLineChart from './HighCharts.vue'



const route = useRoute();
const user_data = ref('')


const barChartData = [
  { "category": -10 },
  { "category1": 20 },
  { "category2": 30 }
]
const defaultData = [{
  "id": 1,
  "AccountName": "Abhinav",
  "IdealMTM": 0,
  "Day_PL": "25000",
  'Friction': 0,
  'OpenQuantity': 0,
  'NetQuantity': 0,
  "PortfolioValue": "250000",
  "PositionDayPL": "25000000000",
  "HoldingsDayPL": 250000,
  "TotalOrderCount": 250000,
  "OpenOrderCount": 40,
  "CompleteOrderCount": 10,
  "PositionsCount": 20,
  "HoldingsCount": 10,
  "Used_Margin": 50000,
  "AvailableMargin": 250000,
  "Cash": 2500000,
  "Margin": 0,
  "VAR": 0
}];
const columnHelper = createColumnHelper()
const live_trade_book_columns = [
  columnHelper.accessor(row => row.OrderGeneratedDateTime, {
    id: 'OrderGeneratedDateTime',
    cell: info => info.getValue(),
    header: () => 'OrderGeneratedDateTime',
  }),
  columnHelper.accessor(row => row.ExchangeTransactTime, {
    id: 'ExchangeTransactTime',
    cell: info => info.getValue(),
    header: () => 'ExchangeTransactTime',
  }),
  columnHelper.accessor(row => row.ExchangeInstrumentID, {
    id: 'ExchangeInstrumentID',
    cell: info => info.getValue(),
    header: () => 'ExchangeInstrumentID',
  }),
  columnHelper.accessor(row => row.OrderAverageTradedPrice, {
    id: 'OrderAverageTradedPrice',
    cell: info => info.getValue(),
    header: () => 'OrderAverageTradedPrice',
  }),
  columnHelper.accessor(row => row.OrderSide, {
    id: 'OrderSide',
    cell: info => info.getValue(),
    header: () => 'OrderSide',
  }),
  columnHelper.accessor(row => row.LeavesQuantity, {
    id: 'LeavesQuantity',
    cell: info => info.getValue(),
    header: () => 'LeavesQuantity',
  }),
  columnHelper.accessor(row => row.OrderQuantity, {
    id: 'OrderQuantity',
    cell: info => info.getValue(),
    header: () => 'OrderQuantity',
  }),



]
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


const rms_df_columns = [
  columnHelper.accessor(row => row.symbol, {
    id: 'Symbol',
    cell: info => info.getValue(),
    header: () => 'Symbol',
  }),
  columnHelper.accessor(row => row.ltp, {
    id: 'Ltp',
    cell: info => info.getValue(),
    header: () => 'Ltp',
  }),
  columnHelper.accessor(row => row.pnl, {
    id: 'pnl',
    cell: info => info.getValue(),
    header: () => 'PnL',
  }),
  columnHelper.accessor(row => row.buy_qty, {
    id: 'buy_qty',
    cell: info => info.getValue(),
    header: () => 'Buy Qty',
  }),
  columnHelper.accessor(row => row.buy_price, {
    id: 'buy_price',
    cell: info => info.getValue(),
    header: () => 'Buy Price',
  }),
  columnHelper.accessor(row => row.buy_value, {
    id: 'buy_value',
    cell: info => info.getValue(),
    header: () => 'Buy Value',
  }),
  columnHelper.accessor(row => row.net_price, {
    id: 'net_price',
    cell: info => info.getValue(),
    header: () => 'Net Price',
  }),
  columnHelper.accessor(row => row.net_value, {
    id: 'net_value',
    cell: info => info.getValue(),
    header: () => 'Net Value',
  }),
  columnHelper.accessor(row => row.sell_price, {
    id: 'sell_price',
    cell: info => info.getValue(),
    header: () => 'Sell Price',
  }),
  columnHelper.accessor(row => row.sell_qty, {
    id: 'sell_qty',
    cell: info => info.getValue(),
    header: () => 'Sell Qty',
  }),
  columnHelper.accessor(row => row.sell_value, {
    id: 'sell_value',
    cell: info => info.getValue(),
    header: () => 'Sell Value',
  }),
  columnHelper.accessor(row => row.turnover, {
    id: 'turnover',
    cell: info => info.getValue(),
    header: () => 'Turnover',
  }),
]




const messages = ref([])


let eventSource = null


const date = ref()
const data = ref([])
const user_infected = ref([])

const client_live_trade_book = ref([])

const connectToSSE = () => {
  const eventSource = new EventSource(MyEnum.backendURL);

  eventSource.onmessage = (event) => {
    try {
      let response = JSON.parse(event.data);
      user_infected.value = Object.keys(response.pulse)
        .filter(key => (key.startsWith('pulse_trader_xts:') || key.startsWith('pulse_trader_zerodha:')) && response.pulse[key] === false)
        .map(key => key.split(':')[1]);

      let result = response.client_data.find(client => client.name === name.value);

      if (result) {
        user_data.value = result;



        data.value = [{
          AccountName: result.name || '',
          IdealMTM: result.ideal_MTM !== undefined ? Number(result.ideal_MTM) : 0,
          Day_PL: result.MTM !== undefined ? Number(result.MTM) : 0,
          Friction: result.MTM !== undefined && result.ideal_MTM !== undefined
            ? (Number(result.MTM) - Number(result.ideal_MTM)).toFixed(2)
            : '0.00',
          OpenQuantity: result.OpenQuantity !== undefined ? Number(result.OpenQuantity) : 0,
          NetQuantity: result.NetQuantity !== undefined ? Number(result.NetQuantity) : 0,
          RejectedOrderCount: result.Rejected_orders !== undefined ? Number(result.Rejected_orders) : 0,
          PendingOrderCount: result.Pending_orders !== undefined ? Number(result.Pending_orders) : 0,
          MARGIN: result.Live_Client_Margin !== undefined ? Number(result.Live_Client_Margin) : 0,
          VAR: result.Live_Client_Var !== undefined ? Number(result.Live_Client_Var) : 0,
        }];

        let tradeArray = Object.values(result.Live_Trade_Book || {});
        let prev = client_live_trade_book.value.length;
        if (prev < tradeArray.length) {
          client_live_trade_book.value = tradeArray;
        }
      } else {
        console.error('No client data found for the specified name:', name.value);
      }
    } catch (error) {
      console.error('Error parsing event data or updating data:', error);
    }
  };

  eventSource.onopen = () => {
    messages.value.push('Connection opened');
  };

  eventSource.onerror = (error) => {
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

  <div class="px-8 py-8 pageContainer">

    <!-- <TableOriginal /> -->
    <!-- <TableTanstack :data="people" :columns="columnsPeople" />

<div class="my-8">
<TableTanstack :data="cars" :columns="columnsCars" />
</div> -->
    <div class="my-8">
      <TanStackTestTable :data="data" :columns="columns" :hasColor="['IdealMTM', 'Day_PL', 'Friction']" :navigateTo="[]"
        :showPagination=false :hasRowcolor="{ 'columnName': 'AccountName', 'arrayValues': user_infected }" />
    </div>

    <div class="my-8" v-if="user_data">
      <TanStackTestTable :data="user_data['Live_Client_RMS_df']" :columns="rms_df_columns" :hasColor="['pnl']"
        :navigateTo="[]" :showPagination=true />
    </div>



    <!-- <input type="date" v-model="date" /> -->


    <MultiLineChart v-if="user_data" :chartData="[user_data['MTMTable'], user_data['ideal_MTMTable']]"
      :lineNames="['Actual MTM', 'Ideal MTM']" />

    <BarChart v-if="user_data['Live_Client_Positions']" :chartData='user_data["Live_Client_Positions"]' />

    <div class="my-8">
      <TanStackTestTable :data="client_live_trade_book" :columns="live_trade_book_columns" :hasColor="[]"
        :navigateTo="[]" :showPagination=true />
    </div>
    <!-- < p class=" headingContainer">{{ name }}</p>
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
  /* font-family: poppins; */
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