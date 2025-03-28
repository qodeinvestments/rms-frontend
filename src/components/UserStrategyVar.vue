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
        <a-select 
            v-model:value="varcalculation"
            mode="multiple" 
            placeholder="Select Columns" 
            style="width: 100%; margin-bottom: 10px;"
            :options="categoryOptions">
        </a-select>
            
        <TanStackTestTable
          :key="varcalculation.join('-')" 
          title="All User Var Table"
          :data="give_var_calculation_data()"
          :columns="filteredColumns"
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
        <a-select 
            v-model:value="uservarcalculation"
            mode="multiple" 
            placeholder="Select Columns" 
            style="width: 100%; margin-bottom: 10px;"
            :options="categoryOptions">
        </a-select>
        <TanStackTestTable
          :key="uservarcalculation.join('-')" 
          :title="`${selectedClient} User Var Table`" 
          :data="give_user_var_calculation_data()"
          :columns="filteredUserVarColumns"
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
          :title="`$ELM Table`" 
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
const elmpercentage= ref(2)  // Default percentage value is 2
const error = ref(null)
const loading = ref(false)
const varcalculation = ref(['Broker','System','Basket'])
const uservarcalculation = ref(['Broker','System','Basket'])
// Category options for the multi-select
const categoryOptions = [
  { label: 'Broker', value: 'Broker' },
  { label: 'System', value: 'System' },
  { label: 'Basket', value: 'Basket' }
]
// -------------------------------------------------------
// COLUMN HELPER FOR TABLE
// -------------------------------------------------------
const filteredColumns = computed(() => {
  // Guard against empty data
  if (!var_calculation_data.value.length) return [];
  // Use the filterColumns function to get the keys you want based on the current selection.
  const keysToKeep = filterColumns(var_calculation_data.value[0], varcalculation.value);
  return keysToKeep.map(key => {
    return columnHelper.accessor(row => row[key], {
      id: key,
      cell: info => info.getValue(),
      header: () => key,
    });
  });
});

const filteredUserVarColumns = computed(() => {
  // Guard against empty data
  if (!user_var_calculation_data.value.length) return [];
  // Use the filterColumns function to get the keys you want based on the current selection.
  const keysToKeep = filterColumns(user_var_calculation_data.value[0], uservarcalculation.value);
  return keysToKeep.map(key => {
    return columnHelper.accessor(row => row[key], {
      id: key,
      cell: info => info.getValue(),
      header: () => key,
    });
  });
});





const filterColumns = (masterObj, options) => {
  const result = [];
  result.push('User');

  // Get an array of keys from the master object.
  const master = Object.keys(masterObj);

  const systemGroup = new Set(['Upside', 'Upside%', 'Downside', 'Downside%']);
  const brokerGroup = new Set(['BrokerUpside', 'BrokerUpside%', 'BrokerDownside', 'BrokerDownside%']);
  const combinedSet = new Set([...systemGroup, ...brokerGroup,'User']);

  if (options.includes('System')) {
    master.forEach(col => {
      if (systemGroup.has(col)) {
        result.push(col);
      }
    });
  }

  if (options.includes('Broker')) {
    master.forEach(col => {
      if (brokerGroup.has(col)) {
        result.push(col);
      }
    });
  }

  if (options.includes('Basket')) {
    const alreadyAdded = new Set( combinedSet );
    master.forEach(col => {
      if (!alreadyAdded.has(col)) {
        result.push(col);
      }
    });
  }
 
  return result;
}

const give_var_calculation_data = () => {
  // The original data array
  const data = var_calculation_data.value;
  const keysToKeep = filterColumns(var_calculation_data.value[0], varcalculation.value);
  const updatedData = data.map(item => {
    const newItem = {};
    keysToKeep.forEach(key => {
      if (item.hasOwnProperty(key)) {
        newItem[key] = item[key];
      }
    });
    newItem.summary = `${newItem.User} has a downside of ${newItem.Downside}`;
    return newItem;
  });

  return updatedData;
};

const give_user_var_calculation_data=()=>{
    // The original data array
    const data = user_var_calculation_data.value;
    const keysToKeep = filterColumns(user_var_calculation_data.value[0], uservarcalculation.value);
    const updatedData = data.map(item => {
      const newItem = {};
      keysToKeep.forEach(key => {
        if (item.hasOwnProperty(key)) {
          newItem[key] = item[key];
        }
      });
      newItem.summary = `${newItem.User} has a downside of ${newItem.Downside}`;
      return newItem;
    });

  return updatedData;

}

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

})

onUnmounted(() => {
  // Cleanup if needed
})


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
