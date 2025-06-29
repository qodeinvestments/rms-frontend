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
        <Button size="large" @click="applyPercentage" style="margin-right: 8px;">
          Apply Percentage
        </Button>
        <Button size="large" @click="refreshVarCalculationData" style="margin-right: 8px;" >
          🔄 Refresh
        </Button>
      </div>

      <!-- FIRST TABLE (PSAR TABLE) -->
       
      <div class="my-8" v-if="var_calculation_data.length">
        <!-- The existing category selector -->
        <a-select 
            v-model:value="varcalculation"
            mode="multiple" 
            placeholder="Select Columns" 
            style="width: 100%; margin-bottom: 10px;"
            :options="categoryOptions">
        </a-select>
        
        <!-- New column selector for addition calculation -->
        <a-select 
            v-model:value="columnsForAddition"
            mode="multiple" 
            placeholder="Select columns to add" 
            style="width: 100%; margin-bottom: 10px;"
            :options="additionColumnOptions">
        </a-select>

        <a-select
          v-model:value="selectedAggregateUsers"
          mode="multiple"
          placeholder="Select users to aggregate"
          style="width: 100%; margin-bottom: 1rem;"
          :options="userOptions"
        />
          
        
        <TanStackTestTable
          :key="`${varcalculation.join('-')}-${columnsForAddition.length}`" 
          title="All User Var Table"
          :data="tableDataWithAggregate"
          :columns="updatedFilteredColumns"
          :hasColor="[...new Set([...Object.keys(var_calculation_data[0]), 'customUpside','customDownside'])]"
          :navigateTo="[]"
          :showPagination="true"
          :defaultSortFirstColumn="true"
        />
      </div>
      <!-- Add PayoffChart component -->
      <div class="my-8 payoff-chart-section">
        <h2 class="payoff-chart-title">Payoff Chart Analysis</h2>
        
        <!-- Percentage Input for Payoff Chart -->
        <div class="payoff-percentage-input" style="margin-bottom: 1rem;">
          <InputNumber
            v-model:value="payoffPercentage"
            :min="10"
            :max="100"
            placeholder="Enter percentage (10-100)"
            size="large"
            style="width: 200px; margin-right: 8px;"
          />
        </div>
        
        <!-- Account selection dropdown -->
        <a-select 
          v-model:value="selectedPayoffAccounts"
          mode="multiple"
          placeholder="Select accounts for payoff chart"
          style="width: 100%; margin-bottom: 10px;"
          :options="accountNames.map(account => ({ label: account, value: account }))"
        />
        
        <!-- Strategy selection dropdown -->
        <a-select 
          v-model:value="selectedPayoffStrategies"
          mode="multiple"
          placeholder="Select strategies for payoff chart"
          style="width: 100%; margin-bottom: 10px;"
          :options="payoffStrategyOptions"
        />

        <!-- Submit button for payoff chart -->
        <Button 
          size="large"
          @click="fetchPayoffChartData"
          :loading="payoffChartLoading"
          style="margin-bottom: 20px;"
        >
          Generate Payoff Chart
        </Button>

        <PayoffChart :data="payoffChartData" />
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
          :defaultSortFirstColumn="true"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { createColumnHelper } from '@tanstack/vue-table'
import { Select, Button, InputNumber } from 'ant-design-vue'
import TanStackTestTable from './TanStackTestTable.vue'
import PayoffChart from './PayoffChart.vue'
import { API_BASE_URL, WS_BASE_URL } from '../config/url'

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

// 1. Track which users to aggregate
const selectedAggregateUsers = ref([])

// 2. Build the dropdown options from your raw data
const userOptions = computed(() => 
  var_calculation_data.value
    .map(row => ({
      label: row.User,
      value: row.User
    }))
    .sort((a, b) => a.label.localeCompare(b.label))
);


// 3. Compute the averaged/summed row from the *processed* data
const aggregatedRow = computed(() => {
  const sel = selectedAggregateUsers.value
  if (!sel.length) return null

  // 1) pull the rows that are actually going into the table
  const baseRows = processedVarCalculationData.value
  const rows = baseRows.filter(r => sel.includes(r.User))
  const count = rows.length

  if (!count) return null

  // 2) build the list of keys to aggregate (everything except "User")
  const keys = Object.keys(baseRows[0]).filter(k => k !== 'User')

  // 3) reduce them into one row
  const sumRow = { User: 'Aggregate' }
  keys.forEach(key => {
    // total up
    const total = rows.reduce((acc, r) => {
      const v = parseFloat(r[key])
      return acc + (isNaN(v) ? 0 : v)
    }, 0)

    // if it's a "%" column, average it; otherwise keep the sum
    sumRow[key] = key.endsWith('%') 
      ? total / count 
      : total
  })

  return sumRow
})

// 4. Merge into your existing processed data
const tableDataWithAggregate = computed(() => {
  const base = processedVarCalculationData.value.slice()
  return aggregatedRow.value
    ? [aggregatedRow.value, ...base]
    : base
})

// New ref for columns to be added
const columnsForAddition = ref([])

// Category options for the multi-select
const categoryOptions = [
  { label: 'Broker', value: 'Broker' },
  { label: 'System', value: 'System' },
  { label: 'Basket', value: 'Basket' }
]

// Options for addition columns
const additionColumnOptions = computed(() => {
  if (!var_calculation_data.value.length) return [];
  const keys = Object.keys(var_calculation_data.value[0]);
  const prefixSet = new Set();

  keys.forEach(key => {
    if (key.endsWith('Upside')) {
      const prefix = key.slice(0, -'Upside'.length);
      if (prefix) prefixSet.add(prefix);
    } else if (key.endsWith('Downside')) {
      const prefix = key.slice(0, -'Downside'.length);
      if (prefix) prefixSet.add(prefix);
    }
  });

  return Array.from(prefixSet)
    .sort() // sort alphabetically in ascending order
    .map(prefix => ({
      label: prefix,
      value: prefix
    }));
});

// Add this new computed property after additionColumnOptions
const payoffStrategyOptions = computed(() => {
  if (!var_calculation_data.value.length) return [];
  
  // Start with the 'Normal' option
  const options = [{ label: 'Normal', value: 'Normal' }];
  
  // Get unique strategy prefixes (similar to additionColumnOptions but as a separate computation)
  const prefixSet = new Set();
  const keys = Object.keys(var_calculation_data.value[0]);
  
  keys.forEach(key => {
    if (key.endsWith('Upside')) {
      const prefix = key.slice(0, -'Upside'.length);
      if (prefix) prefixSet.add(prefix);
    } else if (key.endsWith('Downside')) {
      const prefix = key.slice(0, -'Downside'.length);
      if (prefix) prefixSet.add(prefix);
    }
  });

  // Add other strategy options
  const strategyOptions = Array.from(prefixSet)
    .sort()
    .map(prefix => ({
      label: prefix,
      value: prefix
    }));

  return [...options, ...strategyOptions];
});




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

// Updated filtered columns computed property: inject two new columns instead of the single Addition column
const updatedFilteredColumns = computed(() => {
  const baseColumns = filteredColumns.value;
  
  // If no columns are selected for addition, return the base columns as-is.
  if (!columnsForAddition.value.length) return baseColumns;
  
  // Create the Custom Upside column
  const customUpsideColumn = columnHelper.accessor(
    row => row.customUpside,
    {
      id: 'customUpside',
      cell: info => info.getValue(),
      header: () => 'Custom Upside',
    }
  );
  
  // Create the Custom Downside column
  const customDownsideColumn = columnHelper.accessor(
    row => row.customDownside,
    {
      id: 'customDownside',
      cell: info => info.getValue(),
      header: () => 'Custom Downside',
    }
  );


  
  // Find the "User" column and separate it from the other base columns.
  const userColumn = baseColumns.find(col => col.id === 'User');
  const otherColumns = baseColumns.filter(col => col.id !== 'User');
  
  // If the "User" column exists, place it first, then our new two columns, then the rest.
  if (userColumn) {
    return [userColumn, customUpsideColumn, customDownsideColumn, ...otherColumns];
  } else {
    return [customUpsideColumn, customDownsideColumn, ...baseColumns];
  }
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





const refreshVarCalculationData= async()=> {
    try {
      loading.value = true;
      await var_calculations(inputPercentage.value);
    } catch (err) {
      console.error("Error refreshing data:", err);
    } finally {
      loading.value = false;
    }
  }

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

const processedVarCalculationData = computed(() => {
  const filteredData = give_var_calculation_data();
  
  // If no columns are selected for addition, return the filtered data unchanged.
  if (!columnsForAddition.value.length) return filteredData;
  
  // Map over filtered data to compute customUpside and customDownside
  return filteredData.map(row => {
    const newRow = { ...row };
    
    // Compute customUpside: sum values from selected columns (append "Upside" to column name)
    newRow.customUpside = columnsForAddition.value.reduce((sum, col) => {
      const key = col + 'Upside'; // explicitly create the key
      const originalValue = var_calculation_data.value.find(item => item.User === row.User)?.[key];
      return sum + (originalValue !== undefined && !isNaN(Number(originalValue)) ? Number(originalValue) : 0);
    }, 0);
    
    // Compute customDownside: sum values from selected columns (append "Downside" to column name)
    newRow.customDownside = columnsForAddition.value.reduce((sum, col) => {
      const key = col + 'Downside';
      const originalValue = var_calculation_data.value.find(item => item.User === row.User)?.[key];
      return sum + (originalValue !== undefined && !isNaN(Number(originalValue)) ? Number(originalValue) : 0);
    }, 0);
    
    return newRow;
  });
});


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

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
  document.title = 'Var Page';
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
  document.title = 'Vite App'
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

// Add these refs in the script section with other refs
const selectedPayoffAccounts = ref([])
const selectedPayoffStrategies = ref([])
const payoffChartData = ref([])
const payoffChartLoading = ref(false)
const payoffPercentage = ref(10) // Default value of 10

// Update the fetchPayoffChartData function
async function fetchPayoffChartData() {
  if (!selectedPayoffAccounts.value.length) {
    console.warn('No accounts selected for payoff chart')
    alert('Please select at least one account')
    return
  }

  // Validate percentage
  if (payoffPercentage.value < 10 || payoffPercentage.value > 100) {
    alert('Please enter a percentage between 10 and 100')
    return
  }

  try {
    console.log('Fetching payoff chart data:', {
      accounts: selectedPayoffAccounts.value,
      strategies: selectedPayoffStrategies.value,
      percentage: payoffPercentage.value
    })
    
    payoffChartLoading.value = true
    const response = await postData('payoffchart', {
      clients: selectedPayoffAccounts.value,
      strategies: selectedPayoffStrategies.value,
      percentage: payoffPercentage.value
    }, payoffChartData)
    
    console.log('Payoff chart data received:', {
      response,
      transformedData: payoffChartData.value
    })
  } catch (err) {
    console.error('Error fetching payoff chart data:', err)
    alert('Error fetching payoff chart data')
  } finally {
    payoffChartLoading.value = false
  }
}

// Add a watch to monitor payoffChartData changes
watch(() => payoffChartData.value, (newData) => {
  console.log('Payoff chart data updated:', {
    hasData: !!newData,
    dataLength: newData?.length,
    data: newData
  })
}, { deep: true })
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

.payoff-chart-section {
  margin: 2rem 0 4rem 0; /* Increased bottom margin */
}

.payoff-chart-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e8e8e8;
}
</style>