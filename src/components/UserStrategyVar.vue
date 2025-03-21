<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { createColumnHelper } from '@tanstack/vue-table'
import TanStackTestTable from './TanStackTestTable.vue'

// Reactive state definitions
const var_calculation_data = ref([])
const error = ref(null)
const loading = ref(false)
const uids = ref([])      // not used in this snippet but declared
const basket = ref([])    // not used in this snippet but declared

// Placeholder for WebSocket connection function; replace with your actual function
function connectClientDetailsWebSocket() {
  console.log('Connecting WebSocket client details...')
}

// Create a column helper instance
const columnHelper = createColumnHelper()

// Compute columns based on the first element of var_calculation_data
const columns = computed(() => {
  if (var_calculation_data.value.length === 0) return []
  const keys = Object.keys(var_calculation_data.value[0])
  return keys.map(column => {
    return columnHelper.accessor(row => row[column], {
      id: column,
      cell: info => info.getValue(),
      header: () => column,
    })
  })
})

// API function to fetch data and update a reactive state
const fetchData = async (endpoint, stateRef) => {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('User not authenticated')

    const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorMessage = await response.text()
      throw new Error(`Error fetching ${endpoint}: ${errorMessage}`)
    }

    const data = await response.json()
    stateRef.value = data || []
  } catch (err) {
    error.value = err.message
    console.error(`Error fetching ${endpoint}:`, err.message)
  }
}

// Function to fetch var_calculations data
const var_calculations = () => fetchData('uservarcalculations', var_calculation_data)

// Lifecycle hooks
onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([var_calculations()])
  } finally {
    loading.value = false
  }
  connectClientDetailsWebSocket()
})

onUnmounted(() => {
  // Cleanup if needed
})
</script>

<template>
  <div class="px-8 py-8 pageContainer">
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div class="my-8" v-else-if="var_calculation_data.length">
      <TanStackTestTable 
        title="PsarTable" 
        :data="var_calculation_data" 
        :columns="columns" 
        :hasColor="Object.keys(var_calculation_data[0])"
        :navigateTo="[]" 
        :showPagination="true" 
        :showPin="true"
      />
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