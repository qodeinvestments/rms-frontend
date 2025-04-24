<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
} from '@tanstack/vue-table'

import { MyEnum } from '../Enums/Prefix.js';
import { ref, watch } from 'vue'
import TanStackTestTable from './TanStackTestTable.vue'
import Histogram from './Histogram.vue';
import { columns } from '../components/TableVariables/SignalBook.js'; 

const fetchData = async (endpoint, stateRef) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');
    const res = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    stateRef.value = endpoint === 'getAccounts' ? Object.keys(data) : data || [];
  } catch (err) {
    console.error(`Error fetching ${endpoint}:`, err.message);
  }
};


const fetchUsers = () => fetchData('users', users);
 
onMounted(() => {
    connectClientDetailsWebSocket();
})

onUnmounted(() => {

})

// Watch for changes in selectedBasketItems
watch(selectedBasketItems, (newSelectedBasketItems) => {
    console.log('Selected Basket items changed:', newSelectedBasketItems);
    // Reset UID selection when basket selection changes
    selectedUids.value = [];
});

// Toggle function for the checker filter
const toggleCheckerFilter = () => {
    showOnlyUnchecked.value = !showOnlyUnchecked.value;
}
</script>


<template>
    <div class="px-8 py-8 pageContainer">
        <div class="my-8" v-if="filteredSignalBookData.length">
            <TanStackTestTable title="PsarTable" :data="filteredSignalBookData" :columns="columns" :hasColor="[]"
                :navigateTo="[]" :showPagination=true :showPin="true"/>
        </div>
       
    </div>
</template>

<style scoped>
.a-select {
    margin-top: 20px;
    margin-bottom: 20px;
}

.pageContainer {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.histogram-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 30px;
}

.filter-controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}

/* Custom button styling without hover effects and background colors */
.custom-checker-btn {
    align-self: flex-start;
    padding: 8px 16px;
    border: 1px solid #d9d9d9;
    border-radius: 2px;
    cursor: pointer;
    transition: border-color 0.3s;
    background: none;
    font-size: 14px;
    color: rgba(0, 0, 0, 0.85);
}

.custom-checker-btn:focus {
    outline: none;
}

/* Simple border change to indicate active state */
.custom-checker-btn:global(.active), 
.custom-checker-btn:global([aria-pressed="true"]) {
    border-color: #1890ff;
    color: #1890ff;
}

.latencyvalue {
    font-weight: bold;
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

html {
    /* font-family: poppins; */
    font-size: 14px;
}
</style>