<script setup>
import { onMounted, onUnmounted, computed, nextTick } from 'vue'
import BarChart from './Barchart.vue';
import { useRouter } from 'vue-router';
import Histogram from './Histogram.vue';
import { API_BASE_URL, WS_BASE_URL } from '../config/url'
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
import LightWeightChart from './LightWeightChart.vue';
import InfoIcon from './InfoIcon.vue'
const route = useRoute();
const user_data = ref('')
const name = ref('');
const broker = ref('')
const columnHelper = createColumnHelper()
const histogram = ref([])
const histogram_order_fill_lag = ref([])
const uids = ref([])
const basket = ref([])
import { live_trade_book_columns_zerodha,live_trade_book_columns_xts,live_order_book_columns_zerodha
  ,fund_summary_columns,live_order_book_columns_xts,signal_position,columns,combined_df_columns_zerodha,
  combined_df_columns_xts,rms_df_columns,combined_order_zerodha,combined_order_xts,combined_trades_zerodha,
  curr_strategy_mtm,system_tag_pnl,curr_basket_mtm,combined_trades_xts,zerodha_order_book_columns,holding_book_columns,zerodha_position_book_columns,rms_prev_day,xts_order_book,xts_pos_book
 } from '../components/TableVariables/UserPageTable.js'; 



const strategyData = ref({})
const strategy_chart_data = ref({})
const basketData = ref({})
const basket_chart_data = ref({})
const selectedUids = ref([]);
const selectedSignalPositions = ref([])
const selectedBasketItems = ref([]);

const filteredBasketOptions = computed(() => basket.value.filter(o => !selectedBasketItems.value.includes(o)));

const filteredUids = computed(() => {
  if (selectedBasketItems.value.length === 0) {
    return uids.value;
  }
  return uids.value.filter(uid => selectedBasketItems.value.includes(uid.split('_')[0]));
});

const filteredOptions = computed(() => filteredUids.value.filter(o => !selectedUids.value.includes(o)));



// Updated computed property for filtered book data
const filteredSignalBookData = computed(() => {
  if (selectedUids.value.length === 0 && selectedBasketItems.value.length === 0) {
    return book.value;
  }
  return book.value.filter(item => {
    const basketMatch = selectedBasketItems.value.length === 0 || selectedBasketItems.value.includes(item.uid.split('_')[0]);
    const uidMatch = selectedUids.value.length === 0 || selectedUids.value.includes(item.uid);
    return basketMatch && uidMatch;
  });
});





let eventSource = null
const client_BackendData = ref([])
const connection_BackendData = ref([])
const date = ref()
const data = ref([])
const basket_latency = ref([])
const basket_max_latency = ref([])
const strategy_latency = ref([])
const strategy_max_latency = ref([])
const past_time_strategy = ref(0)
const past_time_basket = ref(0)
const client_latency = ref(0)
const client_details_Latency = ref(0)
const past_time_client = ref(0)
const past_time_clientDetails = ref(0)
const max_client_details_latency = ref(0)
const max_client_latency = ref(0)
const mix_real_ideal_mtm_table = ref({})
const signal_position_tables = ref({})
const book = ref([])
const position_sum = ref(0)
const handleColumnClick = ({ item, index }) => {
  showOnPage.value = item;
  // If switching to Combined DF, initialize and set concise view
  if (item === 'Combined DF') {
    initializeColumnVisibility();
    // Wait for next tick to ensure tableRef is available
    nextTick(() => {
      if (tableRef.value) {
        setPresetView('concise');
      }
    });
  }
}
const handleMessage = (message) => {
  try {
    if (message.client_data === undefined) return;
    client_BackendData.value = message.client_data
    let result = client_BackendData.value.find(client => client.name === name.value);
 
    broker.value = result.broker;
    if (result) {
      user_data.value = result;
      data.value = [{
        AccountName: result.name || '',
        IdealMTM: result.ideal_MTM !== undefined ? result.ideal_MTM : 0,
        Day_PL: result.MTM !== undefined ? result.MTM : 0,
        PNL_PER_UM: result['PNL Utilized %'] !== undefined ? Number(result['PNL Utilized %']) : 0,
        PNL_PER_M: result['PNL Overall %'] !== undefined ? Number(result['PNL Overall %']) : 0,
        Peak_Margin: result['Peak Margin'] !== undefined ? result['Peak Margin'] : 0,
        Slippage: result.Slippage !== undefined ? result.Slippage : 0,
        Margin: result['Total Margin'] !== undefined ? result['Total Margin'] : 0, //item.Total Margin',
        CompleteOrderCount: result.CompleteOrderCount !== undefined ? Number(result.CompleteOrderCount) : 0,
        openOrderCount: result.openOrderCount !== undefined ? Number(result.openOrderCount) : 0,
        RejectedOrderCount: result.Rejected_orders !== undefined ? Number(result.Rejected_orders) : 0,
        PendingOrderCount: result.Pending_orders !== undefined ? Number(result.Pending_orders) : 0,
        OpenQuantity: result.OpenQuantity !== undefined ? Number(result.OpenQuantity) : 0,
        NetQuantity: result.NetQuantity !== undefined ? Number(result.NetQuantity) : 0,
        Ideal_Margin: result.Live_Client_Margin !== undefined ? Number(result.Live_Client_Margin) : 0,
        VAR: result.Live_Client_Var !== undefined ? Number(result.Live_Client_Var) : 0,
        Cash: result.cashAvailable !== undefined ? Number(result.cashAvailable) : 0,
        AvailableMargin: result.availableMargin !== undefined ? Number(result.availableMargin) : 0,
        Slippage1: result.Slippage1!==undefined? result.Slippage1:0,
        Slippage2: result.Slippage2!==undefined? result.Slippage2:0,
        Used_Margin: result.marginUtilized !== undefined ? result.marginUtilized : 0,
        VAR_PERCENTAGE: result.Live_Client_Var !== undefined && (result['Total Margin'] > 0) ? ((Number(result.Live_Client_Var) / result['Total Margin']) * 100).toPrecision(4) : 0,
      }];
      
      position_sum.value = result.MTM !== undefined ? result.MTM : 0

    } else {
      console.error('No client data found for the specified name:', name.value);
    }
  } catch (error) {
    console.error('Error parsing event data or updating data:', error);
  }
}
const router = useRouter();
const LagPageHandler = () => {
  let str = '/user/lag/' + name.value;
  router.push(str);

}
const connectToSSE = () => {
  const token = localStorage.getItem('access_token'); // Retrieve the access token
  if (!token) {
    alert('User not authenticated');
    return;
  }


  const socket = new WebSocket(`${WS_BASE_URL}ws`);

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
    const authMessage = JSON.stringify({ token });
    socket.send(authMessage);
  }
  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
};


const connectStrategyWebSocket = () => {
  const token = localStorage.getItem('access_token'); // Retrieve the access token
  if (!token) {
      alert('User not authenticated');
      return;
  }
    
  const clientStrategySocket = new WebSocket(`${WS_BASE_URL}chart/strategy`);

  clientStrategySocket.onopen = function (e) {
     // Send the token as the first message for authentication
    // const authMessage = JSON.stringify({ token });
    // clientStrategySocket.send(authMessage);
    console.log("Strategy connection established");
    // Send the initial set of client data
    sendClientDetails();
  };

  clientStrategySocket.onmessage = function (event) {
    const data = JSON.parse(event.data);



    if (data.error === "Access denied") {
      clientStrategySocket.close();
      return;
    }


    let ar2 = data["time"];
    if (past_time_strategy.value === 0) past_time_strategy.value = ar2;
    if (past_time_strategy.value != 0) {
      let date1 = new Date(past_time_strategy.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let diffInMs = date2 - date1;
      let diffInSeconds = diffInMs / 1000;
      strategy_latency.value = diffInSeconds;
      strategy_max_latency.value = Math.max(strategy_max_latency.value, strategy_latency.value)
      past_time_strategy.value = ar2;
    }
    strategyData.value = data
    if (data.live) {
      strategy_chart_data.value = data.live;
    }

    else {
      const gg = strategy_chart_data.value
      for (const i in data.last) {
        if (gg[i].length != 0) {
          const last_data = gg[i][gg[i].length - 1].time;
          if (last_data != data.last[i].time) {
            gg[i].push(data.last[i])
          }
        }
      }
      strategy_chart_data.value = gg;
    }

  };
  clientStrategySocket.onerror = function (error) {
    console.log(`WebSocket error: ${error.message}`);
  };
  clientStrategySocket.onclose = function (event) {
    console.log('Client Detail WebSocket connection closed:', event.reason);
  };
  function sendClientDetails() {
    if (clientStrategySocket && clientStrategySocket.readyState === WebSocket.OPEN) {
      let client_data = {
        "name": name.value,
        "basket": ['ALL'],
        "token": token
      };
      clientStrategySocket.send(JSON.stringify(client_data));
    } else {
      console.log("WebSocket is not open. Unable to send message.");
    }
  }
  return clientStrategySocket;
};


const connectBasketWebSocket = () => {
  const token = localStorage.getItem('access_token'); // Retrieve the access token
  if (!token) {
      alert('User not authenticated');
      return;
  }
    
  const clientBasketSocket = new WebSocket(`${WS_BASE_URL}chart/basket`);
  clientBasketSocket.onopen = function (e) {
     // Send the token as the first message for authentication
    // const authMessage = JSON.stringify({ token });
    // clientBasketSocket.send(authMessage);
    console.log("Basket connection established");
    // Send the initial set of client data
    sendClientDetails();
  };

  clientBasketSocket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    
    if (data.error === "Access denied") {
      clientStrategySocket.close();
      return;
    }

    let ar2 = data["time"];
    mix_real_ideal_mtm_table.value = { "real": data['MTMTable'], "ideal": data['ideal_MTMTable'] }
    signal_position_tables.value = data.signalPosition
    if (past_time_basket.value === 0) past_time_basket.value = ar2;
    if (past_time_basket.value != 0) {
      let date1 = new Date(past_time_basket.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      let diffInMs = date2 - date1;
      let diffInSeconds = diffInMs / 1000;
      basket_latency.value = diffInSeconds;
      basket_max_latency.value = Math.max(basket_max_latency.value, basket_latency.value)
      past_time_basket.value = ar2;
    }
 
   
    basketData.value = data
    if (data.live) {
      basket_chart_data.value = data.live;
    }

    else {
      const gg = basket_chart_data.value
      for (const i in data.last) {
        if (gg[i].length != 0) {
          const last_data = gg[i][gg[i].length - 1].time;
          if (last_data != data.last[i].time) {
            gg[i].push(data.last[i])
          }
        }
      }
      basket_chart_data.value = gg;
    }

  };
  clientBasketSocket.onerror = function (error) {
    console.log(`WebSocket error: ${error.message}`);
  };
  clientBasketSocket.onclose = function (event) {
    console.log('Client Detail WebSocket connection closed:', event.reason);
  };
  function sendClientDetails() {
    if (clientBasketSocket && clientBasketSocket.readyState === WebSocket.OPEN) {
      let client_data = {
        "name": name.value,
        "basket": ['ALL'],
        "token": token
      };
      clientBasketSocket.send(JSON.stringify(client_data));
    } else {
      console.log("WebSocket is not open. Unable to send message.");
    }
  }

  return clientBasketSocket;
};








const connectClientDetailsWebSocket = () => {
  const token = localStorage.getItem('access_token'); // Retrieve the access token
  if (!token) {
      alert('User not authenticated');
      return;
  }
    
  const clientDetailSocket = new WebSocket(`${WS_BASE_URL}clientdetails`);
  clientDetailSocket.onopen = function (e) {
     // Send the token as the first message for authentication
    const authMessage = JSON.stringify({ token });
    clientDetailSocket.send(authMessage);
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
      if (showOnPage.value === 'Combined DF') {
        histogram.value = book.value.map(item => item.signal_lag);
        histogram_order_fill_lag.value = book.value.map(item => item.order_fill_lag)
        uids.value = [...new Set(book.value.map(item => item.uid))];
        basket.value = [...new Set(book.value.map(item => item.uid.split('_')[0]))];
      }

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



// New refs for selected items
const selectedStrategies = ref([]);
const filteredData = computed(() => {
  if (strategyData.value['curr'] === undefined) return []
  if (selectedStrategies.value.length === 0) return strategyData.value['curr'];
  return strategyData.value['curr'].filter(item => selectedStrategies.value.includes(item.UID));

})
// Computed properties for filtered options
const filteredStrategyOptions = computed(() => {
  if (strategyData.value['curr'] === undefined) return [];

  // Get all UIDs from strategyData['curr']
  const allUIDs = strategyData.value['curr'].map(item => item.UID);

  // Filter out UIDs that are present in selectedStrategies
  const filteredUIDs = allUIDs.filter(uid => !selectedStrategies.value.includes(uid));

  return filteredUIDs;
});


const showOnPage = ref('Positions')
const strategyChartData = ref({})
const strategyChartDataWithoutNumber = ref({})
const availableSystemTags = ref([])
const availableSystemTagsWithoutNumber = ref([])
const systemTagNeeded = ref([])
const systemTagWithNumberNeeded = ref([])
const isStrategyChartLoading = ref(false)
const isSystemTagChartLoading = ref(false)
const chartKey = ref(0)
const systemTagChartData = ref({})
const selectedSystemTags = ref([])
const systemTagChartKey = ref(0)

// Add new refs for date filtering
const dateRange = ref([])

// Add computed property for filtered fund summary data
const filteredFundSummaryData = computed(() => {
  if (!book.value || showOnPage.value !== 'Fund Summary') return book.value;
  
  if (!dateRange.value || dateRange.value.length !== 2) return book.value;
  
  const [start, end] = dateRange.value;
  if (!start && !end) return book.value;
  
  return book.value.filter(item => {
    const itemDate = new Date(item.Date);
    const startDate = start ? new Date(start) : null;
    const endDate = end ? new Date(end) : null;
    
    if (startDate && endDate) {
      return itemDate >= startDate && itemDate <= endDate;
    } else if (startDate) {
      return itemDate >= startDate;
    } else if (endDate) {
      return itemDate <= endDate;
    }
    return true;
  });
});

const fetchStrategyChartData = async () => {
  try {
    isStrategyChartLoading.value = true
    const response = await fetch(`${API_BASE_URL}stratcharts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        client: name.value,
        systemTagNeeded: systemTagNeeded.value
      })
    })
    const data = await response.json()
    
    strategyChartData.value = data.chartData
    chartKey.value++
    
    if (data && data.availableSystemTagList) {
      availableSystemTags.value = data.availableSystemTagList
    }
    if(data && data.availableSystemTagWithoutNumberList) {
      availableSystemTagsWithoutNumber.value = data.availableSystemTagWithoutNumberList;
    }
  } catch (error) {
    console.error('Error fetching strategy chart data:', error)
  } finally {
    isStrategyChartLoading.value = false
  }
}

const fetchSystemTagChartData = async () => {
  try {
    isSystemTagChartLoading.value = true
    const response = await fetch(`${API_BASE_URL}stratchartswithoutnumbers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        client: name.value,
        systemTagNeeded: selectedSystemTags.value
      })
    })
    const data = await response.json()
    
    systemTagChartData.value = data.chartData
    systemTagChartKey.value++
  } catch (error) {
    console.error('Error fetching system tag chart data:', error)
  } finally {
    isSystemTagChartLoading.value = false
  }
}

// Add preset views for columns
const presetViews = {
    concise: {
        xts: [
            'system_timestamp',
            'system_tag',
            'action',
            'TradingSymbol',
            'note',
            'price',
            'OrderAverageTradedPrice',
            'OrderQuantity'
        ],
        zerodha: [
            'system_timestamp',
            'system_tag',
            'action',
            'symbol',
            'note',
            'filled_quantity',
            'average_price'
        ]
    }
}

const tableRef = ref(null)
const initialColumnVisibility = ref({})

// Initialize initialColumnVisibility with all columns hidden
const initializeColumnVisibility = () => {
    const columns = broker.value === 'xts' ? combined_df_columns_xts : combined_df_columns_zerodha;
    const conciseColumns = broker.value === 'xts' ? presetViews.concise.xts : presetViews.concise.zerodha;
    
    columns.forEach(column => {
        initialColumnVisibility.value[column.id] = conciseColumns.includes(column.id);
    });
}

// Call initialization when broker changes
watch(broker, () => {
    initializeColumnVisibility();
}, { immediate: true });

// Watch for changes in showOnPage
watch(showOnPage, (newView) => {
    if (newView === 'Combined DF') {
        // Wait for next tick to ensure tableRef is available
        nextTick(() => {
            if (tableRef.value) {
                setPresetView('concise');
            }
        });
    }
});

// Add function to set column visibility based on preset view
const setPresetView = (viewType) => {
    const newVisibility = {}
    
    // Set visibility for all columns
    if (tableRef.value) {
        tableRef.value.table.getAllLeafColumns().forEach(column => {
            // For overall view, set all columns to true
            if (viewType === 'overall') {
                newVisibility[column.id] = true
            } else {
                // For concise view, only show specified columns based on broker type
                const conciseColumns = broker.value === 'xts' ? presetViews.concise.xts : presetViews.concise.zerodha
                newVisibility[column.id] = conciseColumns.includes(column.id)
            }
        })
        
        tableRef.value.columnVisibility = newVisibility
    }
}

onMounted(() => {
  connectToSSE();
  name.value = route.params.username;
  connectClientDetailsWebSocket();
  connectBasketWebSocket();
  connectStrategyWebSocket();
  fetchStrategyChartData();
})
onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})
// Watch for changes in selectedBasketItems
watch(selectedBasketItems, (newSelectedBasketItems) => {
  console.log('Selected Basket items changed:', newSelectedBasketItems);
  // Reset UID selection when basket selection changes
  selectedUids.value = [];
});
</script>
<template>
  <div class="px-8 py-8 pageContainer">

    <div class="heading-container">
      <p class="table-heading LagButton" @click="LagPageHandler()">Lags </p>
    </div>

    <div class="my-8">
      <TanStackTestTable title="Account Details" :data="data" :columns="columns"
        :hasColor="['IdealMTM', 'Day_PL', 'Slippage', 'PNL_PER_UM', 'PNL_PER_M','Slippage1','Slippage2']" :navigateTo="[]" :showPagination=false
        :hasRowcolor="{ 'columnName': 'AccountName', 'arrayValues': [] }"  :defaultSortFirstColumn="true" />
    </div>
    <!--  <input type="date" v-model="date" /> -->
    <div class="chartContainer">
      <p class="table-heading">MTM AND IDEAL MTM</p>
      <LightWeightChart v-if="mix_real_ideal_mtm_table['real']" :Chartdata="mix_real_ideal_mtm_table" />
    </div>



    <!--  <BarChart v-if="user_data['Live_Client_Positions']" :chartData='user_data["Live_Client_Positions"]' /> -->
    <div class="LatencyTable">
      <p> Client Latency :<span class="latencyvalue">{{ client_latency }}</span></p>
      <p> Max Client :<span class="latencyvalue">{{ max_client_latency }}</span></p>
      <p> Client Detail Latency: <span class="latencyvalue">{{ client_details_Latency }}</span></p>
      <p> Max Client Detail Latency :<span class="latencyvalue"> {{ max_client_details_latency }}</span></p>
      <p> Basket Detail Latency :<span class="latencyvalue"> {{ basket_latency }}</span></p>
      <p> Max Basket Latency :<span class="latencyvalue"> {{ basket_max_latency }}</span></p>
      <p> Strategy Detail Latency :<span class="latencyvalue"> {{ strategy_latency }}</span></p>
      <p> Max Strategy Latency :<span class="latencyvalue"> {{ strategy_max_latency }}</span></p>
    </div>
    <div class="navContainer">
      <NavBar
        :navColumns="['Positions', 'Order', 'Combined DF', 'Combined Orders', 'Combined Trades', 'Fund Summary',
        ...(broker === 'zerodha' ? ['Zerodha Order Book', 'Zerodha Position Book'] : []),
          ...(broker === 'xts' ? ['XTS Order Book', 'XTS Position Book'] : []),'Holdings','EOD']"
        @column-clicked="handleColumnClick" :colorColumns="[]" />
    </div>
    <div class="selectContainer" v-if="book && showOnPage === 'Combined DF' && filteredSignalBookData.length">
      <a-select v-model:value="selectedBasketItems" mode="multiple" placeholder="Select Basket Items"
        style="width: 100%; margin-bottom: 10px;"
        :options="filteredBasketOptions.map(item => ({ value: item }))"></a-select>
      <a-select v-model:value="selectedUids" mode="multiple" placeholder="Select UIDs" style="width: 100%"
        :options="filteredOptions.map(item => ({ value: item }))"></a-select>
    </div>


    <div class="my-8" v-if="book && showOnPage === 'Positions'">
      <p class="table-heading">Live MTM : <span :class="position_sum > 0 ? 'green' : 'red'">{{ position_sum }}</span>
      </p>
      <TanStackTestTable title="Position" :data="book" :columns="rms_df_columns" :hasColor="['pnl']" :navigateTo="[]"
        :showPagination=true  :defaultSortFirstColumn="true"/>
    </div>
<!-- 
    <div class="my-8" v-if="book && showOnPage === 'TradeBook'">
      <TanStackTestTable title="Complete Trade Book" :data="book"
        :columns="broker === 'xts' ? live_trade_book_columns_xts : live_trade_book_columns_zerodha" :hasColor="[]"
        :navigateTo="[]" :showPagination=true />
    </div> -->

    <div class="my-8" v-if="book && showOnPage === 'Order'">
      <TanStackTestTable title="Complete Order Book" :data="book"
        :columns="broker === 'xts' ? live_order_book_columns_xts : live_order_book_columns_zerodha" :hasColor="[]"
        :navigateTo="[]" :showPagination=true  :defaultSortFirstColumn="true"/>
    </div>
    <div class="my-8" v-if="book && showOnPage === 'Fund Summary'">
      <div class="date-filter-container">
        <div class="date-headers">
          <span class="date-label">Start Date</span>
          <span class="date-label">End Date</span>
        </div>
        <a-range-picker
          v-model:value="dateRange"
          :show-time="false"
          format="YYYY-MM-DD"
          :placeholder="['Start Date', 'End Date']"
          style="width: 100%; margin-bottom: 20px;"
        />
      </div>
      <TanStackTestTable 
        title="Fund Summary" 
        :data="filteredFundSummaryData" 
        :columns="fund_summary_columns"
        :hasColor="['Actual MTM','Ideal MTM','Settlement Price','Holdings Day PNL']" 
        :navigateTo="[]" 
        :showPagination=true 
      />
    </div>
    <div class="my-8" v-if="book && showOnPage === 'Zerodha Order Book'">
      <TanStackTestTable title="Zerodha Order Book" :data="book" :columns="zerodha_order_book_columns"
        :hasColor="['ContractValue']" :navigateTo="[]" :showPagination=true />
    </div>
    <div class="my-8" v-if="book && showOnPage === 'XTS Order Book'">
      <TanStackTestTable title="XTS Order Book" :data="book" :columns="xts_order_book"
        :hasColor="['ContractValue']" :navigateTo="[]" :showPagination=true />
    </div>
    
    <div class="my-8" v-if="book && showOnPage === 'Zerodha Position Book'">
      <TanStackTestTable title="Zerodha Position Book" :data="book" :columns="zerodha_position_book_columns"
        :hasColor="['quantity','pnl','m2m','unrealised','realised','overnight_quantity','value','Entry Contract Value','Exit Contract Value']" :navigateTo="[]" :showPagination=true />
    </div>

    <div class="my-8" v-if="book && showOnPage === 'XTS Position Book'">
      <TanStackTestTable title="XTS Position Book" :data="book" :columns="xts_pos_book"
        :hasColor="[]" :navigateTo="[]" :showPagination=true />
    </div>

    <div class="my-8" v-if="book && showOnPage === 'Holdings'">
      <TanStackTestTable title="Holdings" :data="book" :columns="holding_book_columns"
        :hasColor="['pnl']" :navigateTo="[]" :showPagination=true />
    </div>

    <div class="my-8" v-if="book && showOnPage === 'EOD'">
      <TanStackTestTable title="EOD" :data="book" :columns="rms_prev_day"
        :hasColor="['Quantity']" :navigateTo="[]" :showPagination=true />
    </div>

    <div class="my-8" v-if="book && showOnPage === 'Combined DF' && filteredSignalBookData.length">
      <!-- Add preset view buttons -->
      <div class="preset-views mb-4">
          <div class="preset-views-buttons">
              <button 
                  @click="setPresetView('concise')" 
                  class="preset-view-btn">
                  Concise View
              </button>
              <button 
                  @click="setPresetView('overall')" 
                  class="preset-view-btn">
                  Overall View
              </button>
              <InfoIcon message="Press 'Concise View' to show only essential columns. Press 'Overall View' to show all available columns." />
          </div>
      </div>

      <TanStackTestTable 
          ref="tableRef"
          title="Combined DF" 
          :data="filteredSignalBookData"
          :columns="broker === 'xts' ? combined_df_columns_xts : combined_df_columns_zerodha" 
          :hasColor="[]"
          :navigateTo="[]" 
          :showPagination=true 
          :initialColumnVisibility="initialColumnVisibility"
      />
    </div>

    <div class="my-8" v-if="book && showOnPage === 'Combined Orders'">
      <TanStackTestTable title="Combined Orders" :data="book"
        :columns="broker === 'xts' ? combined_order_xts : combined_order_zerodha" :hasColor="[]" :navigateTo="[]"
        :showPagination=true />
    </div>

    <div class="my-8" v-if="book && showOnPage === 'Combined Trades'">
      <TanStackTestTable title="Combined Trades" :data="book"
        :columns="broker === 'xts' ? combined_trades_xts : combined_trades_zerodha" :hasColor="[]" :navigateTo="[]"
        :showPagination=true />
    </div>

    <div class="signalPosContainer" v-if="signal_position_tables">
      <p class="table-heading">Signal Positions</p>
      <div class="multiselectContainer">
        <a-select v-model:value="selectedSignalPositions" mode="multiple" placeholder="Select Baskets"
          style="width: 100%" :options="Object.keys(signal_position_tables).map(item => ({ value: item }))"></a-select>
      </div>
      <div v-for=" (basket, index) in signal_position_tables" :key="index">
        <div class="my-8" v-if="selectedSignalPositions.includes(index)">
          <TanStackTestTable :title="index" :data="basket" :columns="signal_position" :hasColor="['IdealQuantity']"
            :navigateTo="[]" :showPagination=true />
        </div>
      </div>
    </div>


    <div class="chartContainer">
      <p class="table-heading">BASKET WISE IDEAL MTM</p>
      <LightWeightChart v-if="Object.keys(basket_chart_data).length > 0" :Chartdata="basket_chart_data" />
    </div>

    <div class="chartContainer">
      <p class="table-heading">Strategy Charts</p>
      <div class="selectContainer" style="margin-top: 20px;">
        <a-select
          v-model:value="systemTagNeeded"
          mode="multiple"
          placeholder="Select Strategies"
          style="width: 100%"
          :options="availableSystemTags.map(tag => ({ value: tag, label: tag }))"
          :loading="isStrategyChartLoading"
        />
        <a-button 
          type="primary" 
          @click="fetchStrategyChartData" 
          class="submit-button"
          :loading="isStrategyChartLoading"
          :disabled="isStrategyChartLoading || systemTagNeeded.length === 0"
        >
          {{ isStrategyChartLoading ? 'Loading...' : 'Generate Chart' }}
        </a-button>
      </div>
    </div>

    <div class="my-8" v-if="Object.keys(strategyChartData).length > 0" >
      <LightWeightChart :key="chartKey" :Chartdata="strategyChartData" />
    </div>

    <div class="chartContainer">
      <p class="table-heading">Strategy System Tag Charts</p>
      <div class="selectContainer" style="margin-top: 20px;">
        <a-select
          v-model:value="selectedSystemTags"
          mode="multiple"
          placeholder="Select System Tags"
          style="width: 100%"
          :options="availableSystemTagsWithoutNumber.map(tag => ({ value: tag, label: tag }))"
          :loading="isSystemTagChartLoading"
        />
        <a-button 
          type="primary" 
          @click="fetchSystemTagChartData" 
          class="submit-button"
          :loading="isSystemTagChartLoading"
          :disabled="isSystemTagChartLoading || selectedSystemTags.length === 0"
        >
          {{ isSystemTagChartLoading ? 'Loading...' : 'Generate System Tag Chart' }}
        </a-button>
      </div>
    </div>

    <div class="my-8" v-if="Object.keys(systemTagChartData).length > 0" >
      <LightWeightChart :key="systemTagChartKey" :Chartdata="systemTagChartData" />
    </div>

    <div class="my-8" v-if="Object.keys(basketData).length > 0">
      <TanStackTestTable title="Current Basket Ideal MTM" :data="basketData['curr']" :columns="curr_basket_mtm"
        :hasColor="['MTM']" :navigateTo="[]" :showPagination=true />
    </div>

    <div class="selectContainer">
      <a-select v-model:value="selectedStrategies" mode="multiple" placeholder="Select Strategies"
        style="width: 100%; margin-bottom: 10px;"
        :options="filteredStrategyOptions.map(item => ({ value: item }))"></a-select>
    </div>
    <div class="my-8" v-if="Object.keys(strategyData).length > 0">
      <TanStackTestTable title="Current Strategy Ideal MTM" :data="filteredData" :columns="curr_strategy_mtm"
        :hasColor="['MTM']" :navigateTo="[]" :showPagination=true />
    </div>
    <div class="my-8" v-if="Object.keys(strategyData).length > 0">
      <TanStackTestTable title="System Tag PNL" :data="strategyData['systemTagPnl']" :columns="system_tag_pnl"
        :hasColor="['PNL']" :navigateTo="[]" :showPagination=true />
    </div>
    <div v-if="histogram_order_fill_lag.length > 0 && showOnPage === 'Combined DF'" class="histogram-container">
      <p class="table-heading">Histogram Of Order Fill Lag Combined DF</p>
      <Histogram :dataArray="histogram_order_fill_lag" />
    </div>

    <div v-if="histogram.length > 0 && showOnPage === 'Combined DF'" class="histogram-container">
      <p class="table-heading">Histogram Of Signal Lag Combined DF</p>
      <Histogram :dataArray="histogram" />
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

.signalPosContainer {
  display: flex;
  width: 100%;
  flex-wrap: wrap;
  margin-bottom: 50px;
}

.red {
  color: red;
}

.chartContainer {
  width: 100%;
  margin-top: 50px;
  margin-bottom: 30px;
}

.multiselectContainer {
  width: 100%;
  margin-top: 50px;
}

p {
  margin: 0;
  padding: 0;
}

.selectContainer {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.histogram-container {
  display: flex;
  flex-direction: column;
  margin-bottom: 30px;
}


.green {
  color: rgb(80, 185, 80);
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

.heading-container {
  align-self: flex-end;
}

.LagButton {
  border: 1px solid white;

  padding: 10px 20px;
  border-radius: 5px;
  background: rgb(231, 108, 108);
  color: white;
  cursor: pointer;
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

.submit-button {
  margin-top: 10px;
  width: 100%;
  background-color: #1890ff !important;
  border-color: #1890ff !important;
  color: white !important;
  height: 40px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.submit-button:hover {
  background-color: #40a9ff !important;
  border-color: #40a9ff !important;
}

.submit-button:disabled {
  background-color: #d9d9d9 !important;
  border-color: #d9d9d9 !important;
  color: rgba(0, 0, 0, 0.25) !important;
  cursor: not-allowed;
}

.submit-button.ant-btn-loading {
  background-color: #1890ff !important;
  border-color: #1890ff !important;
  color: white !important;
  opacity: 0.8;
}

.chart-wrapper {
  width: 100%;
  height: 400px;
  margin-bottom: 50px;
}

.tableContainer {
  width: 100%;
  position: relative;
  z-index: 0;
  margin-top: 50px;
}

.my-8 {
  margin-top: 2rem;
  margin-bottom: 2rem;
  width: 100%;
}

.date-filter-container {
  width: 100%;
  margin-bottom: 20px;
  padding: 0 30px;
}

.date-headers {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 0 12px;
}

.date-label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

/* Add preset view button styles */
.preset-views {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.preset-view-btn {
    padding: 8px 16px;
    border: 1px solid #d9d9d9;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.3s;
    background: white;
    font-size: 14px;
    color: rgba(0, 0, 0, 0.85);
}

.preset-view-btn:hover {
    border-color: #1890ff;
    color: #1890ff;
}

.preset-view-btn:active {
    background-color: #f0f0f0;
}

.preset-views-buttons {
    display: flex;
    gap: 10px;
    align-items: center;
}
</style>