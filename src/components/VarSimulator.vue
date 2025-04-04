<template>
    <div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-lg p-8">
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
            Select a User
          </label>
          <select 
            id="user-select"
            v-model="selectedUser"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option disabled value="">Please select a user</option>
            <option
              v-for="user in users"
              :key="user.id"
              :value="user"
            >
              {{ user.name }}
            </option>
          </select>
        </div>
  
        <!-- Trade form -->
        <form v-if="selectedUser" @submit.prevent="submitTrades" class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-700">
            Add Trades for {{ selectedUser.name }}
          </h2>
  
          <!-- Single "Percentage" input -->
          <div>
            <label for="percentage" class="block text-sm font-medium text-gray-700 mb-2">
              Percentage
            </label>
            <input 
              type="number"
              id="percentage"
              v-model="percentage"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter percentage"
            />
          </div>
  
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
  
        <!-- Results section -->
        <!-- <div v-if="result" class="mt-8 p-6 bg-green-50 border border-green-100 rounded-md">
          <h3 class="text-lg font-semibold text-green-800 mb-3">Submission Successful</h3>
          <pre class="text-sm text-gray-800 bg-gray-100 p-3 rounded overflow-auto max-h-60">
            {{ JSON.stringify(result, null, 2) }}
          </pre>
        </div> -->
  
        <!-- Response Data Table -->
        <div v-if="responseData" class="mt-8 p-6 bg-gray-50 border border-gray-100 rounded-md">
          <h3 class="text-lg font-semibold text-gray-800 mb-3">Response Data</h3>
          <table class="min-w-full table-auto">
            <thead>
              <tr>
                <th class="px-4 py-2 border text-left">Metric</th>
                <th class="px-4 py-2 border text-left">Value</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(value, key) in responseData" :key="key">
                <td class="px-4 py-2 border">{{ key }}</td>
                <td class="px-4 py-2 border">{{  formatIndianNumber(value) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted, watch, computed } from 'vue'
  
  // -------------------------------------------------
  // State variables
  // -------------------------------------------------
  const users = ref([])
  const selectedUser = ref('')
  const loading = ref(true)
  const error = ref(null)
  const isSubmitting = ref(false)
  const result = ref(null)
  const responseData = ref(null)  // Store the response data
  
  // Additional input at the top
  const percentage = ref('')  // or numeric if you prefer: ref(0)
  
  // "trades" array for the currently selected user
  const trades = ref([])
  const userTrades = reactive({})
  
  // -------------------------------------------------
  // Utility function for authenticated fetch
  // -------------------------------------------------
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
  

  // Add this after the existing imports
// Add after imports
const formatIndianNumber = (value) => {
    if (value === null || value === undefined || value === '') return value;

    const num = Number(value);
    if (isNaN(num)) return value;

    // Handle the negative sign
    const isNegative = num < 0;
    const absoluteNum = Math.abs(num);

    // Format to 2 decimal places first
    const formattedDecimal = absoluteNum.toFixed(2);
    const [integerPart, decimalPart] = formattedDecimal.split('.');
    
    const lastThree = integerPart.slice(-3);
    const remaining = integerPart.slice(0, -3);

    const withCommas = remaining
        ? remaining.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree
        : lastThree;

    // Decimal part is now always present due to toFixed(2)
    const formattedNumber = `${withCommas}.${decimalPart}`;

    // Add back the negative sign if necessary
    return isNegative ? `-${formattedNumber}` : formattedNumber;
};


  // -------------------------------------------------
  // Fetch Users
  // -------------------------------------------------
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
  
  // -------------------------------------------------
  // Watch for user changes
  // -------------------------------------------------
  watch(selectedUser, (newUser, oldUser) => {
    // 1. Save old user's trades (if any)
    if (oldUser && oldUser.id) {
      userTrades[oldUser.id] = trades.value
    }
  
    // 2. Load new user's trades
    if (newUser && newUser.id) {
      // If we haven't stored anything yet for this user, init an empty array
      if (!userTrades[newUser.id]) {
        userTrades[newUser.id] = [
          { symbol: '', quantity: '' }
        ]
      }
      trades.value = userTrades[newUser.id]
    } else {
      // No user selected
      trades.value = []
    }
  })
  
  // -------------------------------------------------
  // Computed: isFormValid
  // -------------------------------------------------
  const isFormValid = computed(() => {
    // Must have selectedUser
    if (!selectedUser.value) return false
  
    // Must have a percentage (and not empty string)
    if (!percentage.value) return false
  
    // Must have at least one trade
    if (!trades.value.length) return false
  
    // Every trade must have symbol and quantity
    return trades.value.every(trade => {
      return trade.symbol && trade.quantity !== ''
    })
  })
  
  // -------------------------------------------------
  // Add a new empty trade row
  // -------------------------------------------------
  const addTrade = () => {
    trades.value.push({ symbol: '', quantity: '' })
  }
  
  // -------------------------------------------------
  // Remove a trade entry by index
  // -------------------------------------------------
  const removeTrade = (tradeIndex) => {
    if (trades.value.length > 1) {
      trades.value.splice(tradeIndex, 1)
    }
  }
  
  // -------------------------------------------------
  // Submit trades
  // -------------------------------------------------
  const submitTrades = async () => {
    isSubmitting.value = true
    result.value = null
  
    try {
      const payload = {
        userId: selectedUser.value.id,
        userName: selectedUser.value.name,
        trades: [...trades.value],
        percentage: percentage.value
      }
  
      // POST trades with token
      const data = await fetchData('varsimulator', 'POST', payload)
      result.value = data
  
      // Fetch response data (replace with actual response)
      responseData.value = data
  
    } catch (err) {
      alert(err.message || 'Failed to submit trades. Please try again.')
    } finally {
      isSubmitting.value = false
    }
  }
  
  // -------------------------------------------------
  // onMounted
  // -------------------------------------------------
  onMounted(() => {
    fetchUsers()
  })
  </script>
  
  <style scoped>
  /* Optional: Place your CSS here */
  </style>
  