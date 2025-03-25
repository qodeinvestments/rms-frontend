<template>
  <div class="px-8 py-8 pageContainer">
    <!-- LOADING / ERROR STATES -->
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <!-- MAIN CONTENT -->
    <div v-else>
      <!-- Percentage Input Section Above the First Table -->
      <div class="my-4 percentage-section">
        <InputNumber
          v-model:value="inputPercentage"
          :min="1"
          :max="100"
          placeholder="Enter percentage (1-100)"
          size="large"
          style="width: 200px; margin-right: 8px;"
        />
        <Button size="large" @click="applyPercentage">
          Apply Percentage
        </Button>
      </div>

      <!-- FIRST TABLE (PSAR TABLE) -->
      <div class="my-8" v-if="var_calculation_data.length">
        <TanStackTestTable
          title="All User Var Table"
          :data="var_calculation_data"
          :columns="columns"
          :hasColor="Object.keys(var_calculation_data[0])"
          :navigateTo="[]"
          :showPagination="true"
        />
      </div>

      <!-- DROPDOWN + APPLY BUTTON FOR CLIENT SELECTION -->
      <div class="my-4">
        <Select
          v-model:value="selectedClient"
          size="large"
          placeholder="Select an account"
          style="width: 400px; margin-right: 8px;"
        >
          <Select.Option 
            v-for="account in accountNames" 
            :key="account" 
            :value="account"
          >
            {{ account }}
          </Select.Option>
        </Select>
        <Button size="large" @click="applyClientSelection">
          Apply
        </Button>
      </div>

      <!-- SECOND TABLE (USER VAR TABLE) -->
      <div class="my-8" v-if="user_var_calculation_data.length">
        <TanStackTestTable
          :title="`${selectedClient} User Var Table`" 
          :data="user_var_calculation_data"
          :columns="user_value_table_columns"
          :hasColor="Object.keys(user_var_calculation_data[0])"
          :navigateTo="[]"
          :showPagination="true"
        />
      </div>


      <div class="my-4 percentage-section">
        <InputNumber
          v-model:value="elmpercentage"
          :min="1"
          :max="100"
          placeholder="Enter percentage (1-100)"
          size="large"
          style="width: 200px; margin-right: 8px;"
        />
        <Button size="large" @click="applyelmpercentage">
          Apply ELM Percentage
        </Button>
      </div>


      <!-- SECOND TABLE (USER VAR TABLE) -->
      <div class="my-8" v-if="elmcalculatordata.length">
        <TanStackTestTable
          :title="`${selectedClient} User Var Table`" 
          :data="elmcalculatordata"
          :columns="elm_table_columns"
          :hasColor="Object.keys(elmcalculatordata[0])"
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
import { Select, Button, InputNumber } from 'ant-design-vue'
import TanStackTestTable from './TanStackTestTable.vue'

// -------------------------------------------------------
// REACTIVE STATE
// -------------------------------------------------------
const var_calculation_data = ref([])
const user_var_calculation_data = ref([])
const elmcalculatordata = ref([])
const accounts = ref({})       // Expected format: { "Account A": true, "Account B": true }
const selectedClient = ref('Delthro Vega') // Default selected account
const inputPercentage = ref(10)  // Default percentage value is 10
const elmpercentage= ref(20)  // Default percentage value is 2
const error = ref(null)
const loading = ref(false)

// -------------------------------------------------------
// COLUMN HELPER FOR TABLE
// -------------------------------------------------------
const columnHelper = createColumnHelper()
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

const user_value_table_columns = computed(() => {
  if (user_var_calculation_data.value.length === 0) return []
  const keys = Object.keys(user_var_calculation_data.value[0])
  return keys.map(column => {
    return columnHelper.accessor(row => row[column], {
      id: column,
      cell: info => info.getValue(),
      header: () => column,
    })
  })
})

const elm_table_columns = computed(() => {
  if (elmcalculatordata.value.length === 0) return []
  const keys = Object.keys(elmcalculatordata.value[0])
  return keys.map(column => {
    return columnHelper.accessor(row => row[column], {
      id: column,
      cell: info => info.getValue(),
      header: () => column,
    })
  })
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
// Changed var_calculations to a POST request that sends {"percentage": <value>}
const var_calculations = (percentage) => postData('uservarcalculations', { percentage }, var_calculation_data)
const fetchAccounts = () => fetchData('getAccounts', accounts)
const calculate_elm  = (percentage) => postData('elmcalculator', { percentage }, elmcalculatordata)
// user_var_table now takes a clientName argument
const user_var_table = (clientName) => {
  return postData('uservartable', { client: clientName }, user_var_calculation_data)
}

// -------------------------------------------------------
// COMPUTED ARRAY FOR THE DROPDOWN
// -------------------------------------------------------
const accountNames = computed(() => Object.keys(accounts.value))

// -------------------------------------------------------
// LIFECYCLE HOOKS
// -------------------------------------------------------
onMounted(async () => {
  loading.value = true
  try {
    // Load initial data.
    await Promise.all([
      var_calculations(inputPercentage.value),
      calculate_elm(elmpercentage.value),
      fetchAccounts(),
      user_var_table('Delthro Vega'), // default client value
    ])
  } finally {
    loading.value = false
  }
  connectClientDetailsWebSocket()
})

onUnmounted(() => {
  // Cleanup if needed
})

// Example: existing websocket connection function
function connectClientDetailsWebSocket() {
  console.log('Connecting WebSocket client details...')
}

// -------------------------------------------------------
// HANDLER WHEN USER CLICKS "APPLY" FOR CLIENT SELECTION
// -------------------------------------------------------
async function applyClientSelection() {
  console.log(selectedClient.value, "is the selected client")
  if (!selectedClient.value) return
  try {
    loading.value = true
    // Re-fetch user var data for the newly selected account
    await user_var_table(selectedClient.value)
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

// -------------------------------------------------------
// HANDLER FOR APPLYING PERCENTAGE CHANGE
// -------------------------------------------------------
async function applyPercentage() {
  // Validate that inputPercentage is between 1 and 100
  if (inputPercentage.value < 1 || inputPercentage.value > 100) {
    alert("Please enter a number between 1 and 100.")
    return
  }
  try {
    loading.value = true
    // Re-fetch var_calculation_data with the new percentage value
    await var_calculations(inputPercentage.value)
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function applyelmpercentage() {
  // Validate that elmpercentage is between 1 and 100
  if (elmpercentage.value < 1 || elmpercentage.value > 100) {
    alert("Please enter a number between 1 and 100.")
    return
  }
  try {
    loading.value = true
    // Re-fetch elm_calculation_data with the new percentage value
    await calculate_elm(elmpercentage.value)
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}
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
