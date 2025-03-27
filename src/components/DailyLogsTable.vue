<template>
  <div class="px-8 py-8 pageContainer">
    <!-- LOADING / ERROR STATES -->
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <!-- MAIN CONTENT -->
    <div v-else>
      <!-- FIRST TABLE (PSAR TABLE) -->
      <div class="my-8" v-if="logs.length">
        <a-select 
          v-model:value="selectedCategories"
          mode="multiple" 
          placeholder="Select Categories" 
          style="width: 100%; margin-bottom: 10px;"
          :options="categoryOptions"
        >
        </a-select>

        <TanStackTestTable
          title="All User Var Table"
          :data="filteredLogs"
          :columns="columns"
          :hasColor="Object.keys(logs[0] || {})"
          :navigateTo="[]"
          :showPagination="true"
        />
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { createColumnHelper } from '@tanstack/vue-table'
import { Select } from 'ant-design-vue'
import TanStackTestTable from './TanStackTestTable.vue'
  
// -------------------------------------------------------
// REACTIVE STATE
// -------------------------------------------------------
const logs = ref([])
const error = ref(null)
const loading = ref(false)
const selectedCategories = ref([])

// -------------------------------------------------------
// COLUMN HELPER FOR TABLE
// -------------------------------------------------------
const columnHelper = createColumnHelper()
const columns = computed(() => {
  if (logs.value.length === 0) return []
  const keys = Object.keys(logs.value[0])
  return keys.map(column => {
    return columnHelper.accessor(row => row[column], {
      id: column,
      cell: info => info.getValue(),
      header: () => column,
    })
  })
})

// -------------------------------------------------------
// COMPUTED PROPERTIES
// -------------------------------------------------------
const categoryOptions = computed(() => {
  const uniqueCategories = [...new Set(logs.value.map(log => log.Category))]
  return uniqueCategories.map(category => ({
    label: category,
    value: category
  }))
})

const filteredLogs = computed(() => {
  if (selectedCategories.value.length === 0) return logs.value
  return logs.value.filter(log => 
    selectedCategories.value.includes(log.Category)
  )
})
  
// -------------------------------------------------------
// API FUNCTIONS (fetch/post helpers)
// -------------------------------------------------------
async function fetchData(endpoint, stateRef) {
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
  
// -------------------------------------------------------
// SPECIFIC DATA LOADERS
// -------------------------------------------------------
const getlogs = () => fetchData('getdailylogs', logs)
  
// -------------------------------------------------------
// LIFECYCLE HOOKS
// -------------------------------------------------------
onMounted(async () => {
  loading.value = true
  try {
    // Load initial data.
    await Promise.all([
      getlogs()
    ])
  } finally {
    loading.value = false
  }
})
  
onUnmounted(() => {
  // Cleanup if needed
})
</script>
  
<style scoped>
.pageContainer {
  height: 100%;
  display: flex;
  flex-direction: column;
}
  
.my-4 {
  margin: 1rem 0;
}
  
.my-8 {
  margin: 2rem 0;
}
  
.percentage-section {
  display: flex;
  align-items: center;
}
</style>