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
import MultiLineChart from './HighCharts.vue'

import LightWeightChart from './LightWeightChart.vue';


const route = useRoute();
const user_data = ref('')
const name = ref('');


let eventSource = null

const data = ref([])
const client_details_Latency = ref(0)
const past_time_clientDetails = ref(0)
const max_client_details_latency = ref(0)
const mix_real_ideal_mtm_table = ref({})

const userLagData = ref({})

const connectClientLagsDataWebSocket = () => {
    const clientLagDataDetailSocket = new WebSocket('wss://production.swancapital.in/userLagData');

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


        if (data) {
            userLagData.value = data;
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


    return clientLagDataDetailSocket;
};





onMounted(() => {

    name.value = route.params.username;
    connectClientLagsDataWebSocket();
})

onUnmounted(() => {
    if (eventSource) {
        eventSource.close()
    }
})




</script>

<template>

    <div class="px-8 py-8 pageContainer">



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
            <LightWeightChart v-if="userLagData['xts_trader_lat']"
                :Chartdata="{ 'hello': userLagData['xts_trader_lat'] }" />
        </div>
        <div>
            <p class="table-heading">Combined Df Latency </p>
            <LightWeightChart v-if="userLagData['combined_df_latency']"
                :Chartdata="{ 'hello': userLagData['combined_df_latency'] }" />
        </div>

        <div>
            <p class="table-heading">Pos Agg LATENCY </p>
            <LightWeightChart v-if="userLagData['pos_agg_latency']"
                :Chartdata="{ 'hello': userLagData['pos_agg_latency'] }" />
        </div>


        <!--  <BarChart v-if="user_data['Live_Client_Positions']" :chartData='user_data["Live_Client_Positions"]' /> -->
        <div class="LatencyTable">

            <p> Client Detail Latency: <span class="latencyvalue">{{ client_details_Latency }}</span></p>
            <p> Max Client Detail Latency :<span class="latencyvalue"> {{ max_client_details_latency }}</span></p>

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