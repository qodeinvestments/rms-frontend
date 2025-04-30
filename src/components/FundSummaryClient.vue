<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { ref, watch } from 'vue'
import TanStackTestTable from './TanStackTestTable.vue'
import { columns } from '../components/TableVariables/FundSummaryClient.js'; 
import { useRoute } from 'vue-router';

const route = useRoute();
const error = ref(null);
const name=ref("");
const fundsummary=ref([]);

// API Functions
async function postData(endpoint, payload, stateRef) {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('User not authenticated')
  
    const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
  
    if (!response.ok) {
      const errorMessage = await response.text()
      throw new Error(`Error posting to ${endpoint}: ${errorMessage}`)
    }
  
    const data = await response.json()
    if (stateRef) {
      stateRef.value = data || []
    }
      
    return data
  } catch (err) {
    error.value = err.message
    console.error(`Error posting to ${endpoint}:`, err.message)
    throw err
  }
}


const fetchFundSummary = () => postData('fundsummary', {"name":name.value},fundsummary);
 
onMounted(() => {
    name.value = route.params.username;
    fetchFundSummary();
})

onUnmounted(() => {

})


</script>

<template>
    <div class="px-8 py-8 pageContainer">
        <div class="my-8" v-if="fundsummary.length">
            <TanStackTestTable title="Fund Summary" :data="fundsummary" :columns="columns" :hasColor="['Actual MTM']"
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