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
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router';
import TanStackTestTable from './TanStackTestTable.vue'
import Chart from './Chart.vue';
import NavBar from './NavBar.vue';
import MultiLineChart from './HighCharts.vue'

import LightWeightChart from './LightWeightChart.vue';


const route = useRoute();
const user_data = ref('')
const name = ref('');



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

  columnHelper.accessor(row => row.OrderQuantity, {
    id: 'OrderQuantity',
    cell: info => info.getValue(),
    header: () => 'OrderQuantity',
  }),
]
const live_order_book_columns = [

  columnHelper.accessor(row => row.OrderGeneratedDateTime, {
    id: 'OrderGeneratedDateTime',
    cell: info => info.getValue(),
    header: () => 'OrderGeneratedDateTime',
  }),
  columnHelper.accessor(row => row.OrderType, {
    id: 'OrderType',
    cell: info => info.getValue(),
    header: () => 'OrderType',
  }),

  columnHelper.accessor(row => row.ExchangeTransactTime, {
    id: 'ExchangeTransactTime',
    cell: info => info.getValue(),
    header: () => 'ExchangeTransactTime',
  }),
  columnHelper.accessor(row => row.TradingSymbol, {
    id: 'TradingSymbol',
    cell: info => info.getValue(),
    header: () => 'TradingSymbol',
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

  columnHelper.accessor(row => row.OrderQuantity, {
    id: 'OrderQuantity',
    cell: info => info.getValue(),
    header: () => 'OrderQuantity',
  }),
  columnHelper.accessor(row => row.LeavesQuantity, {
    id: 'LeavesQuantity',
    cell: info => info.getValue(),
    header: () => 'LeavesQuantity',
  }),
  columnHelper.accessor(row => row.OrderStatus, {
    id: 'OrderStatus',
    cell: info => info.getValue(),
    header: () => 'OrderStatus',
  }),
  columnHelper.accessor(row => row.CancelRejectReason, {
    id: 'CancelRejectReason',
    cell: info => info.getValue(),
    header: () => 'CancelRejectReason',
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
  columnHelper.accessor(row => row.Ideal_Margin, {
    id: 'Ideal Margin',
    cell: info => info.getValue(),
    header: () => 'Ideal Margin',
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
]
const combined_df_columns = [
  columnHelper.accessor(row => row.uid, {
    id: 'uid',
    cell: info => info.getValue(),
    header: () => 'uid'
  }),
  columnHelper.accessor(row => row.place_order_lag, {
    id: 'place_order_lag',
    cell: info => info.getValue(),
    header: () => 'place_order_lag'
  }),
  columnHelper.accessor(row => row.TradingSymbol, {
    id: 'TradingSymbol',
    cell: info => info.getValue(),
    header: () => 'TradingSymbol'
  }),
  columnHelper.accessor(row => row.timestamp, {
    id: 'timestamp',
    cell: info => info.getValue(),
    header: () => 'timestamp'
  }),
  columnHelper.accessor(row => row.system_timestamp, {
    id: 'system_timestamp',
    cell: info => info.getValue(),
    header: () => 'system_timestamp'
  }),
  columnHelper.accessor(row => row.action, {
    id: 'action',
    cell: info => info.getValue(),
    header: () => 'action'
  }),
  columnHelper.accessor(row => row.qty, {
    id: 'qty',
    cell: info => info.getValue(),
    header: () => 'qty'
  }),
  columnHelper.accessor(row => row.price, {
    id: 'price',
    cell: info => info.getValue(),
    header: () => 'price'
  }),
  columnHelper.accessor(row => row.value, {
    id: 'value',
    cell: info => info.getValue(),
    header: () => 'value'
  }),

  columnHelper.accessor(row => row.note, {
    id: 'note',
    cell: info => info.getValue(),
    header: () => 'note'
  }),
  columnHelper.accessor(row => row.basket, {
    id: 'basket',
    cell: info => info.getValue(),
    header: () => 'basket'
  }),
  columnHelper.accessor(row => row.effective_qty, {
    id: 'effective_qty',
    cell: info => info.getValue(),
    header: () => 'effective_qty'
  }),
  columnHelper.accessor(row => row.AppOrderID, {
    id: 'AppOrderID',
    cell: info => info.getValue(),
    header: () => 'AppOrderID'
  }),
  columnHelper.accessor(row => row.ExchangeSegment, {
    id: 'ExchangeSegment',
    cell: info => info.getValue(),
    header: () => 'ExchangeSegment'
  }),
  columnHelper.accessor(row => row.ExchangeInstrumentID, {
    id: 'ExchangeInstrumentID',
    cell: info => info.getValue(),
    header: () => 'ExchangeInstrumentID'
  }),
  columnHelper.accessor(row => row.OrderType, {
    id: 'OrderType',
    cell: info => info.getValue(),
    header: () => 'OrderType'
  }),
  columnHelper.accessor(row => row.ProductType, {
    id: 'ProductType',
    cell: info => info.getValue(),
    header: () => 'ProductType'
  }),
  columnHelper.accessor(row => row.OrderQuantity, {
    id: 'OrderQuantity',
    cell: info => info.getValue(),
    header: () => 'OrderQuantity'
  }),
  columnHelper.accessor(row => row.OrderStatus, {
    id: 'OrderStatus',
    cell: info => info.getValue(),
    header: () => 'OrderStatus'
  }),
  columnHelper.accessor(row => row.OrderAverageTradedPrice, {
    id: 'OrderAverageTradedPrice',
    cell: info => info.getValue(),
    header: () => 'OrderAverageTradedPrice'
  }),
  columnHelper.accessor(row => row.OrderGeneratedDateTime, {
    id: 'OrderGeneratedDateTime',
    cell: info => info.getValue(),
    header: () => 'OrderGeneratedDateTime'
  }),
  columnHelper.accessor(row => row.ExchangeTransactTime, {
    id: 'ExchangeTransactTime',
    cell: info => info.getValue(),
    header: () => 'ExchangeTransactTime'
  }),

  columnHelper.accessor(row => row.OrderUniqueIdentifier, {
    id: 'OrderUniqueIdentifier',
    cell: info => info.getValue(),
    header: () => 'OrderUniqueIdentifier'
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
    cell: info => {
      const value = info.getValue();
      return value !== undefined ? value.toFixed(2) : 'N/A';
    },
    header: () => 'Ltp',
  }),
  columnHelper.accessor(row => row.pnl, {
    id: 'pnl',
    cell: info => info.getValue().toFixed(2),
    header: () => 'PnL',
  }),
  columnHelper.accessor(row => row.buy_qty, {
    id: 'buy_qty',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Buy Qty',
  }),
  columnHelper.accessor(row => row.buy_price, {
    id: 'buy_price',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Buy Price',
  }),
  columnHelper.accessor(row => row.buy_value, {
    id: 'buy_value',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Buy Value',
  }),
  columnHelper.accessor(row => row.net_price, {
    id: 'net_price',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Net Price',
  }),
  columnHelper.accessor(row => row.net_value, {
    id: 'net_value',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Net Value',
  }),
  columnHelper.accessor(row => row.net_qty, {
    id: '  net_qty',
    cell: info => info.getValue().toFixed(2),
    header: () => ' Net Qty',
  }),

  columnHelper.accessor(row => row.sell_price, {
    id: 'sell_price',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Sell Price',
  }),
  columnHelper.accessor(row => row.sell_qty, {
    id: 'sell_qty',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Sell Qty',
  }),
  columnHelper.accessor(row => row.sell_value, {
    id: 'sell_value',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Sell Value',
  }),
  columnHelper.accessor(row => row.turnover, {
    id: 'turnover',
    cell: info => info.getValue().toFixed(2),
    header: () => 'Turnover',
  }),
]


let eventSource = null


const client_BackendData = ref([])
const connection_BackendData = ref([])
const date = ref()
const data = ref([])
const user_infected = ref([])
const client_latency = ref(0)
const client_details_Latency = ref(0)
const past_time_client = ref(0)
const past_time_clientDetails = ref(0)
const max_client_details_latency = ref(0)
const max_client_latency = ref(0)
const mix_real_ideal_mtm_table = ref({})
const rms_latency = ref({})

const book = ref([])
const userLagData = ref({})
const handleColumnClick = ({ item, index }) => {
  showOnPage.value = item;
}

const handleMessage = (message) => {

  try {

    if (message.client_data === undefined) return;
    client_BackendData.value = message.client_data

    let result = client_BackendData.value.find(client => client.name === name.value);
    if (result) {
      user_data.value = result;
      data.value = [{
        AccountName: result.name || '',
        IdealMTM: result.ideal_MTM !== undefined ? Number(result.ideal_MTM) : 0,
        Day_PL: result.MTM !== undefined ? Number(result.MTM) : 0,
        Friction: result.MTM !== undefined && result.ideal_MTM !== undefined
          ? (Number(result.MTM) - Number(result.ideal_MTM)).toFixed(2)
          : '0.00',
        RejectedOrderCount: result.Rejected_orders !== undefined ? Number(result.Rejected_orders) : 0,
        PendingOrderCount: result.Pending_orders !== undefined ? Number(result.Pending_orders) : 0,
        OpenQuantity: result.OpenQuantity !== undefined ? Number(result.OpenQuantity) : 0,
        NetQuantity: result.NetQuantity !== undefined ? Number(result.NetQuantity) : 0,
        Ideal_Margin: result.Live_Client_Margin !== undefined ? Number(result.Live_Client_Margin) : 0,
        VAR: result.Live_Client_Var !== undefined ? Number(result.Live_Client_Var) : 0,
        Cash: result.cashAvailable !== undefined ? Number(result.cashAvailable) : 0,
        AvailableMargin: result.availableMargin !== undefined ? Number(result.availableMargin) : 0,
        Used_Margin: result.marginUtilized !== undefined ? Number(result.marginUtilized) : 0,
        VAR_PERCENTAGE: result.Live_Client_Var !== undefined && (result.availableMargin > 0) ? ((Number(result.Live_Client_Var) / Number(result.availableMargin)) * 100).toPrecision(4) : 0,
      }];
      mix_real_ideal_mtm_table.value = { "real": result['MTMTable'], "ideal": result['ideal_MTMTable'] }

    } else {
      console.error('No client data found for the specified name:', name.value);
    }
  } catch (error) {
    console.error('Error parsing event data or updating data:', error);
  }

}



const connectToSSE = () => {
  const socket = new WebSocket('wss://api.swancapital.in/ws');

  socket.onmessage = (event) => {
    if (event.data === 'ping') {
      socket.send('pong')
    } else {
      const message = JSON.parse(event.data)
      let ar2 = message["time"];
      if (past_time_client.value === 0) past_time_client.value = ar2;
      if (past_time_client.value != 0) {
        let date1 = new Date(past_time_client.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
        let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
        let diffInMs = date2 - date1;
        let diffInSeconds = diffInMs / 1000;
        client_latency.value = diffInSeconds;
        max_client_latency.value = Math.max(max_client_latency.value, client_latency.value)
        past_time_client.value = ar2;
      }


      handleMessage(message)
    }
  }
  socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event.reason)
  }

  socket.onopen = () => {
    console.log('WebSocket connection opened')
  }
  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
};


const connectClientDetailsWebSocket = () => {
  const clientDetailSocket = new WebSocket('wss://api.swancapital.in/clientdetails');

  clientDetailSocket.onopen = function (e) {
    console.log("Client details connection established");
    // Send the initial set of client data
    sendClientDetails();
  };

  // clientDetailSocket.onmessage = function (event) {
  //   const data = JSON.parse(event.data);
  //   console.log("Received data:", data);
  //   let Book_data = Object.values(data.table_data || {});
  //   book.value = Book_data;
  //   // Handle the received data here
  // };
  clientDetailSocket.onmessage = function (event) {
    const data = JSON.parse(event.data);


    let ar2 = data["time"];
    if (past_time_clientDetails.value === 0) past_time_clientDetails.value = ar2;
    if (past_time_clientDetails.value != 0) {
      let date1 = new Date(past_time_clientDetails.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let diffInMs = date2 - date1;
      let diffInSeconds = diffInMs / 1000;
      client_details_Latency.value = diffInSeconds;
      max_client_details_latency.value = Math.max(max_client_details_latency.value, client_details_Latency.value)
      past_time_clientDetails.value = ar2;
    }


    if (data.table_data) {
      book.value = Object.values(data.table_data);
    } else {
      book.value = [];
    }
  };

  clientDetailSocket.onerror = function (error) {
    console.log(`WebSocket error: ${error.message}`);
  };

  clientDetailSocket.onclose = function (event) {
    console.log('Client Detail WebSocket connection closed:', event.reason);
  };

  function sendClientDetails() {
    if (clientDetailSocket && clientDetailSocket.readyState === WebSocket.OPEN) {
      let client_data = {
        "name": name.value,
        "type": showOnPage.value
      };
      clientDetailSocket.send(JSON.stringify({ client_data: client_data }));
    } else {
      console.log("WebSocket is not open. Unable to send message.");
    }
  }

  // Call sendClientDetails whenever name or type changes
  watch([name, showOnPage], () => {
    sendClientDetails();
    // Reset book when changing views
    book.value = [];
  });

  return clientDetailSocket;
};



const connectClientLagsDataWebSocket = () => {
  const clientLagDataDetailSocket = new WebSocket('wss://api.swancapital.in/userLagData');

  clientLagDataDetailSocket.onopen = function (e) {
    console.log("ClientLagData details connection established");
    // Send the initial set of client data
    sendClientUserLagDataDetails();
  };
  clientLagDataDetailSocket.onmessage = function (event) {
    const data = JSON.parse(event.data);


    let ar2 = data["time"];
    if (past_time_clientDetails.value === 0) past_time_clientDetails.value = ar2;
    if (past_time_clientDetails.value != 0) {
      let date1 = new Date(past_time_clientDetails.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let diffInMs = date2 - date1;
      let diffInSeconds = diffInMs / 1000;
      client_details_Latency.value = diffInSeconds;
      max_client_details_latency.value = Math.max(max_client_details_latency.value, client_details_Latency.value)
      past_time_clientDetails.value = ar2;
    }


    if (data.table_data) {
      userLagData.value = Object.values(data.table_data);
    } else {
      userLagData.value = [];
    }
  };

  clientLagDataDetailSocket.onerror = function (error) {
    console.log(`WebSocket error: ${error.message}`);
  };

  clientLagDataDetailSocket.onclose = function (event) {
    console.log('ClientLagData Detail WebSocket connection closed:', event.reason);
  };

  function sendClientUserLagDataDetails() {
    if (clientLagDataDetailSocket && clientLagDataDetailSocket.readyState === WebSocket.OPEN) {
      let client_data = {
        "name": name.value,
      };
      clientLagDataDetailSocket.send(JSON.stringify({ client_data: client_data }));
    } else {
      console.log("WebSocket is not open. Unable to send message.");
    }
  }

  // Call sendClientDetails whenever name or type changes
  watch([name, showOnPage], () => {
    sendClientUserLagDataDetails();
    // Reset userLagData when changing views
    userLagData.value = {};
  });

  return clientLagDataDetailSocket;
};




const showOnPage = ref('Positions')

onMounted(() => {
  connectToSSE();
  name.value = route.params.username;
  connectClientLagsDataWebSocket();
  connectClientDetailsWebSocket();
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
      <p class="table-heading">Account Details </p>
      <TanStackTestTable :data="data" :columns="columns" :hasColor="['IdealMTM', 'Day_PL', 'Friction']" :navigateTo="[]"
        :showPagination=false :hasRowcolor="{ 'columnName': 'AccountName', 'arrayValues': [] }" />
    </div>

    <!--  <input type="date" v-model="date" /> -->




    <LightWeightChart v-if="user_data['MTMTable']" :Chartdata="mix_real_ideal_mtm_table" />

    <div>
      <p class="table-heading">RMS LATENCY </p>
      <LightWeightChart v-if="userLagData['rms_latency']" :Chartdata="{ 'hello': userLagData['rms_latency'] }" />
    </div>

    <div>
      <p class="table-heading">MTM Margin LATENCY </p>
      <LightWeightChart v-if="userLagData['mtm_margin_latency']"
        :Chartdata="{ 'hello': userLagData['mtm_margin_latency'] }" />
    </div>
    <div>
      <p class="table-heading">System Tag LATENCY </p>
      <LightWeightChart v-if="userLagData['sys_tag_lat']" :Chartdata="{ 'hello': userLagData['sys_tag_lat'] }" />
    </div>
    <div>
      <p class="table-heading">Xts Trader LATENCY </p>
      <LightWeightChart v-if="userLagData['xts_trader_lat']" :Chartdata="{ 'hello': userLagData['xts_trader_lat'] }" />
    </div>
    <div>
      <p class="table-heading">Pos Agg LATENCY </p>
      <LightWeightChart v-if="userLagData['pos_agg_latency']"
        :Chartdata="{ 'hello': userLagData['pos_agg_latency'] }" />
    </div>








    <!--  <BarChart v-if="user_data['Live_Client_Positions']" :chartData='user_data["Live_Client_Positions"]' /> -->
    <div class="LatencyTable">
      <p> Client Latency :<span class="latencyvalue">{{ client_latency }}</span></p>
      <p> Max Client :<span class="latencyvalue">{{ max_client_latency }}</span></p>
      <p> Client Detail Latency: <span class="latencyvalue">{{ client_details_Latency }}</span></p>
      <p> Max Client Detail Latency :<span class="latencyvalue"> {{ max_client_details_latency }}</span></p>

    </div>

    <div class="navContainer">
      <NavBar :navColumns="['Positions', 'Order', 'Holdings', 'TradeBook', 'Combined DF']"
        @column-clicked="handleColumnClick" />
    </div>

    <div class="my-8" v-if="book && showOnPage === 'Positions'">
      <p class="table-heading">Live Positions</p>
      <TanStackTestTable :data="book" :columns="rms_df_columns" :hasColor="['pnl']" :navigateTo="[]"
        :showPagination=true />
    </div>




    <div class="my-8" v-if="book && showOnPage === 'TradeBook'">
      <p class="table-heading">Complete Trade Book</p>
      <TanStackTestTable :data="book" :columns="live_trade_book_columns" :hasColor="[]" :navigateTo="[]"
        :showPagination=true />
    </div>


    <div class="my-8" v-if="showOnPage === 'Order'">
      <p class="table-heading">Complete Order Book</p>
      <TanStackTestTable :data="book" :columns="live_order_book_columns" :hasColor="[]" :navigateTo="[]"
        :showPagination=true />
    </div>


    <div class="my-8" v-if="showOnPage === 'Combined DF'">
      <p class="table-heading">Combined DF</p>
      <TanStackTestTable :data="book" :columns="combined_df_columns" :hasColor="[]" :navigateTo="[]"
        :showPagination=true />
    </div>

  </div>


</template>

<style scoped>
.pageContainer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.latencyvalue {
  font-weight: bold;
}

.navContainer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
}

.LatencyTable {
  display: flex;
  width: 100;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 20px;
  flex-direction: column;
}

.table-heading {
  font-size: 22px;
  font-weight: 600;
  margin-left: 30px;
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