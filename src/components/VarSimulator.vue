<template>
  <div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <ParentOptionChain :optionsDetails="optionsDetails" />
    <div class="max-w-7xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-center text-gray-800 mb-8">
        User Trade Management
      </h1>
      
      <!-- Loading state for users -->
      <div v-if="loading" class="flex justify-center my-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>

      <!-- Error state for users -->
      <div v-if="error" class="p-4 mb-6 text-sm bg-red-100 text-red-700 rounded-lg">
        {{ error }}
      </div>

      <!-- User selection dropdown -->
      <div v-if="users.length && !loading" class="mb-8">
        <label for="user-select" class="block text-sm font-medium text-gray-700 mb-2">
          Select Users
        </label>
        <a-select 
          id="user-select"
          v-model:value="selectedUserIds"
          mode="multiple"
          style="width: 100%"
          placeholder="Select one or more users"
          :options="userOptions"
          @change="handleUserChange"
        >
        </a-select>
      </div>

      <!-- Individual User Settings -->
      <div v-if="selectedUsers.length" class="mb-8">
        <div class="bg-white shadow overflow-hidden rounded-lg">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User Name
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Basket Selection
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Percentage
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="user in selectedUsers" :key="user.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ user.name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <a-select 
                    v-model:value="userSettings[user.id].selectedBaskets"
                    mode="multiple"
                    style="width: 100%; min-width: 200px;"
                    :max-tag-count="3"
                    :max-tag-placeholder="() => '...'"
                    placeholder="Select baskets for this user"
                    :options="getBasketOptions(user.id)"
                    :default-value="baskets.value"
                    @change="(value) => handleBasketChange(value, user.id)"
                    class="basket-select"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <input 
                    type="number"
                    :id="'percentage-' + user.id"
                    v-model="userSettings[user.id].percentage"
                    class="w-24 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter %"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Trade form -->
      <form v-if="selectedUsers.length" @submit.prevent="submitTrades" class="space-y-6">
        <h2 class="text-xl font-semibold text-gray-700">
          Add Trades for Selected Users ({{ selectedUsers.length }} selected)
        </h2>
        
        <div
          v-for="(trade, index) in trades" 
          :key="index"
          class="p-4 bg-gray-50 rounded-md relative"
        >
          <div class="absolute top-2 right-2">
            <button 
              type="button"
              @click="removeTrade(index)"
              class="text-red-500 hover:text-red-700"
            >
              <span class="sr-only">Remove</span>
              &times;
            </button>
          </div>

          <!-- 2 columns: Symbol and Quantity -->
          <div class="grid grid-cols-2 gap-6">
            <!-- Symbol field -->
            <div>
              <label
                :for="`symbol-${index}`"
                class="block text-sm font-medium text-gray-700 mb-1"
              >
                Symbol
              </label>
              <input
                :id="`symbol-${index}`"
                type="text"
                v-model="trade.symbol"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="E.g. NIFTY25040923250PE"
                required
              />
            </div>

            <!-- Quantity field -->
            <div>
              <label
                :for="`quantity-${index}`"
                class="block text-sm font-medium text-gray-700 mb-1"
              >
                Quantity
              </label>
              <input
                :id="`quantity-${index}`"
                type="number"
                v-model="trade.quantity"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter quantity"
                required
              />
            </div>
          </div>
        </div>

        <!-- Add new trade button -->
        <div class="flex justify-center">
          <button
            type="button"
            @click="addTrade"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <span class="mr-1">+</span> Add Trade
          </button>
        </div>

        <!-- Submit button -->
        <div class="pt-4">
          <button
            type="submit"
            :disabled="isSubmitting || !isFormValid"
            class="w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <span v-if="isSubmitting">
              <span
                class="inline-block animate-spin h-4 w-4 border-t-2 border-white rounded-full mr-2"
              ></span>
              Submitting...
            </span>
            <span v-else>Submit Trades</span>
          </button>
        </div>
      </form>

      <!-- Response Data Table (side by side) -->
      <div v-if="responseData" class="mt-8 p-6 bg-gray-50 border border-gray-100 rounded-md">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">Response Data</h3>
        <h4 class="text-lg font-semibold text-gray-800 mb-3">Premium : <span class="px-4 py-2 border"> {{ responseData["Price"]}}</span></h4>
        <div class="flex gap-8">
          <!-- Table for TableOld -->
          <div class="w-1/2">
            <h4 class="text-xl font-semibold text-gray-700 mb-4">TableOld</h4>
            <table class="min-w-full table-auto">
              <thead>
                <tr>
                  <th class="px-4 py-2 border text-left">Metric</th>
                  <th class="px-4 py-2 border text-left">Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(value, key) in responseData.TableOld" :key="key">
                  <td class="px-4 py-2 border">{{ key }}</td>
                  <td class="px-4 py-2 border" :class="{'positive': value >= 0, 'negative': value < 0}">
                    {{ formatIndianNumber(value) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Table for TableNew -->
          <div class="w-1/2">
            <h4 class="text-xl font-semibold text-gray-700 mb-4">TableNew</h4>
            <table class="min-w-full table-auto">
              <thead>
                <tr>
                  <th class="px-4 py-2 border text-left">Metric</th>
                  <th class="px-4 py-2 border text-left">Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(value, key) in responseData.TableNew" :key="key">
                  <td class="px-4 py-2 border">{{ key }}</td>
                  <td class="px-4 py-2 border" :class="{'positive': value >= 0, 'negative': value < 0}">
                    {{ formatIndianNumber(value) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="flex gap-8">
          <!-- Table for Old Quantity -->
          <div class="w-1/2">
            <table class="min-w-full table-auto">
              <thead>
                <tr>
                  <th class="px-4 py-2 border text-left">Index</th>
                  <th class="px-4 py-2 border text-left">CE</th>
                  <th class="px-4 py-2 border text-left">PE</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(qtyObj, key) in responseData['Old Quantity']" :key="key">
                  <td class="px-4 py-2 border">{{ key }}</td>
                  <td class="px-4 py-2 border"
                      :class="{'positive': qtyObj.CE >= 0, 'negative': qtyObj.CE < 0}">
                    {{ formatIndianNumber(qtyObj.CE) }}
                  </td>
                  <td class="px-4 py-2 border"
                      :class="{'positive': qtyObj.PE >= 0, 'negative': qtyObj.PE < 0}">
                    {{ formatIndianNumber(qtyObj.PE) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Table for New_Quantity -->
          <div class="w-1/2">
            <table class="min-w-full table-auto">
              <thead>
                <tr>
                  <th class="px-4 py-2 border text-left">Index</th>
                  <th class="px-4 py-2 border text-left">CE</th>
                  <th class="px-4 py-2 border text-left">PE</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(qtyObj, key) in responseData['New_Quantity']" :key="key">
                  <td class="px-4 py-2 border">{{ key }}</td>
                  <td class="px-4 py-2 border"
                      :class="{'positive': qtyObj.CE >= 0, 'negative': qtyObj.CE < 0}">
                    {{ formatIndianNumber(qtyObj.CE) }}
                  </td>
                  <td class="px-4 py-2 border"
                      :class="{'positive': qtyObj.PE >= 0, 'negative': qtyObj.PE < 0}">
                    {{ formatIndianNumber(qtyObj.PE) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import ParentOptionChain from './ParentOptionChain.vue'
// State variables
const users = ref([])
const selectedUserIds = ref([])
const selectedUsers = ref([])
const loading = ref(true)
const error = ref(null)
const isSubmitting = ref(false)
const responseData = ref(null)
const optionsDetails = ref({})
const baskets = ref([])

// --- Multi-Select Basket State ---
// Store the selected baskets for the current user (as an array)
const selectedBaskets = ref([])
// Object to maintain basket selections per user
const userBasketsMulti = reactive({})

// Toggle to show/hide the multi-select
const basketToggle = ref(false)

// New flag for "Select All" functionality in basket selection
const isbasketAllSelected = ref(false)

// Computed property for basket options with Select All/Deselect All
const getBasketOptions = (userId) => {
  const allSelected = userSettings[userId]?.selectedBaskets?.length === baskets.value.length
  return [
    {
      label: allSelected ? 'Deselect All' : 'Select All',
      value: 'SELECT_ALL_OPTION'
    },
    ...baskets.value.map(basket => ({
      label: basket,
      value: basket
    }))
  ]
}

// Handle basket toggle change
const handleBasketToggleChange = (event) => {
  if (event.target.checked) {
    // When checkbox is checked, select all baskets
    selectedBaskets.value = [...baskets.value]
    isbasketAllSelected.value = true
  } else {
    // When checkbox is unchecked, clear selections
    selectedBaskets.value = []
    isbasketAllSelected.value = false
  }
}

// Handle basket change for a specific user
const handleBasketChange = (value, userId) => {
  // Find if SELECT_ALL_OPTION is in the new selection
  const selectAllIndex = value.indexOf('SELECT_ALL_OPTION')
  
  if (selectAllIndex !== -1) {
    // Remove the SELECT_ALL_OPTION from the value array
    value.splice(selectAllIndex, 1)
    
    const currentlySelectedCount = userSettings[userId].selectedBaskets.length
    const totalBaskets = baskets.value.length
    
    if (currentlySelectedCount === totalBaskets) {
      // If all baskets were selected, deselect all
      userSettings[userId].selectedBaskets = []
    } else {
      // If not all were selected, select all
      userSettings[userId].selectedBaskets = [...baskets.value]
    }
  } else {
    // Normal selection handling
    userSettings[userId].selectedBaskets = value
  }
}

// Additional input at the top
const percentage = ref(10)

// "trades" array for the currently selected user
const trades = ref([])
const userTrades = reactive({})

// User Settings store
const userSettings = reactive({})

// Fetch Options Details
const fetchOptionsDetails = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await fetchData('optionexpirydetails')
    optionsDetails.value = data || {}
    if (data && Array.isArray(data["BASKETS"])) {
      baskets.value = data["BASKETS"]
    } else {
      console.error('Invalid BASKETS data:', data["BASKETS"])
      baskets.value = []
    }
  } catch (err) {
    console.error('Error fetching options details:', err)
    error.value = err.message || 'Failed to load options details. Please try again later.'
    baskets.value = []
  } finally {
    loading.value = false
  }
}

// Initialize settings for a user
const initializeUserSettings = (userId) => {
  if (!userSettings[userId]) {
    userSettings[userId] = {
      selectedBaskets: [...baskets.value],
      percentage: 10
    }
  }
}

// Handle user selection change
const handleUserChange = (newSelectedIds) => {
  selectedUserIds.value = newSelectedIds
  selectedUsers.value = users.value.filter(user => newSelectedIds.includes(user.id))
  
  // Initialize settings for newly selected users
  selectedUsers.value.forEach(user => {
    if (!userSettings[user.id]) {
      initializeUserSettings(user.id)
    }
  })
}

// Watch for basket changes to update all user settings
watch(baskets, (newBaskets) => {
  if (newBaskets && newBaskets.length > 0) {
    // Update all existing users with the new baskets
    Object.keys(userSettings).forEach(userId => {
      userSettings[userId] = {
        ...userSettings[userId],
        selectedBaskets: [...newBaskets]
      }
    })
  }
}, { immediate: true })

// Watch for user changes to save/load trades
watch(selectedUsers, (newUsers, oldUsers) => {
  // Clear the response data when users change
  responseData.value = null
  
  // Save trades for old users
  if (oldUsers.length > 0) {
    oldUsers.forEach(user => {
      if (user.id) {
        userTrades[user.id] = trades.value
      }
    })
  }
  
  // Load trades for new users or initialize empty
  if (newUsers.length > 0) {
    trades.value = userTrades[newUsers[0].id] || []
  } else {
    trades.value = []
  }
})

// Utility function for authenticated fetch
const fetchData = async (endpoint, method = 'GET', body = null) => {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('User not authenticated')

    const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: body ? JSON.stringify(body) : null
    })

    if (!response.ok) {
      const errorMessage = await response.text()
      throw new Error(`Error fetching ${endpoint}: ${errorMessage}`)
    }

    return await response.json()
  } catch (err) {
    console.error(`Error in fetchData(${endpoint}):`, err)
    throw err
  }
}

// Format numbers in Indian style (with commas)
const formatIndianNumber = (value) => {
  if (value === null || value === undefined || value === '') return value;

  const num = Number(value);
  if (isNaN(num)) return value;

  const isNegative = num < 0;
  const absoluteNum = Math.abs(num);

  const formattedDecimal = absoluteNum.toFixed(2);
  const [integerPart, decimalPart] = formattedDecimal.split('.');

  const lastThree = integerPart.slice(-3);
  const remaining = integerPart.slice(0, -3);

  const withCommas = remaining
      ? remaining.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree
      : lastThree;

  return `${isNegative ? '-' : ''}${withCommas}.${decimalPart}`;
};

// Fetch Users
const fetchUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await fetchData('getAccounts')
    const testdata = data || {}
    
    // Make an array of objects with `id` and `name`.
    users.value = Object.keys(testdata)
      .filter(key => testdata[key] === true)
      .map(key => ({
        id: key,
        name: key
      }))
  } catch (err) {
    error.value = err.message || 'Failed to load users. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Computed: isFormValid
const isFormValid = computed(() => {
  if (trades.value.length == 0) return true
  if (!selectedUsers.value.length) return false
  if (!percentage.value) return false
  if (!trades.value.length) return false
  return trades.value.every(trade => trade.symbol && trade.quantity !== '')
})

// Add a new empty trade row
const addTrade = () => {
  trades.value.push({ symbol: '', quantity: '' })
}

// Remove a trade entry by index
const removeTrade = (tradeIndex) => {
  if (trades.value.length > 1) {
    trades.value.splice(tradeIndex, 1)
  }
}

// Submit trades
const submitTrades = async () => {
  isSubmitting.value = true

  try {
    const payload = {
      users: selectedUsers.value.map(user => ({
        userId: user.id,
        userName: user.name,
        percentage: userSettings[user.id].percentage,
        baskets: userSettings[user.id].selectedBaskets
      })),
      trades: [...trades.value]
    }

    const data = await fetchData('varsimulator', 'POST', payload)
    responseData.value = data

  } catch (err) {
    alert(err.message || 'Failed to submit trades. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

// Computed property for user options
const userOptions = computed(() => 
  users.value.map(user => ({
    label: user.name,
    value: user.id
  }))
)

// onMounted
onMounted(() => {
  fetchUsers()
  fetchOptionsDetails()
})
</script>

<style scoped>
.positive {
  color: green;
}

.negative {
  color: red;
}

.basket-select {
  :deep(.ant-select-selector) {
    min-width: 200px !important;
  }
}
</style>