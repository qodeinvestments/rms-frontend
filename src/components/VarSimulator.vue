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
          
           <!-- Toggle for Basket Multi-Select Visibility -->
          <div class="mb-8">
            <label class="inline-flex items-center">
              <input 
                type="checkbox" 
                v-model="basketToggle" 
                class="form-checkbox h-5 w-5 text-blue-600"
              />
              <span class="ml-2 text-gray-700">Enable Basket Selection</span>
            </label>
          </div>

        <!-- Multi-select Basket selection (only shown if toggle is enabled) -->
        <div v-if="basketToggle" class="mb-8">
          <label for="basket-select" class="block text-sm font-medium text-gray-700 mb-2">
            Select Basket(s)
          </label>
          <!-- Multi-select with mode="multiple" -->
          <a-select 
            id="basket-select"
            v-model="selectedBaskets"
            mode="multiple"
            class="w-full"
            placeholder="Select one or more baskets"
          >
            <a-select-option 
              v-for="basket in baskets" 
              :key="basket" 
              :value="basket"
            >
              {{ basket }}
            </a-select-option>
          </a-select>
        </div>
  
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
  
        <!-- Response Data Table (side by side) -->
        <div v-if="responseData" class="mt-8 p-6 bg-gray-50 border border-gray-100 rounded-md">
          <h3 class="text-lg font-semibold text-gray-800 mb-3">Response Data</h3>
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
  const selectedUser = ref('')
  const loading = ref(true)
  const error = ref(null)
  const isSubmitting = ref(false)
  const responseData = ref(null)  // Store the response data
  const optionsDetails=ref({})

// --- Multi-Select Basket State ---
// Define your basket options
const baskets = ref([
  'swanlongoptions_v2',
  'swan_positional',
  'swanlongoptions',
  'thetaN',
  'delta_trail',
  'ikigai',
  'swan_dma'
])
// Store the selected baskets for the current user (as an array)
const selectedBaskets = ref([])
// Object to maintain basket selections per user
const userBasketsMulti = reactive({})

// Toggle to show/hide the multi-select
const basketToggle = ref(false)
  
  // Additional input at the top
  const percentage = ref(10)
  
  // "trades" array for the currently selected user
  const trades = ref([])
  const userTrades = reactive({})
  
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


    // Fetch Users
  const fetchOptionsDetails = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await fetchData('optionexpirydetails')
      optionsDetails.value = data || {}
      
     
    } catch (err) {
      error.value = err.message || 'Failed to load users. Please try again later.'
    } finally {
      loading.value = false
    }
  }

// Watch for user changes to save/load trades and basket selections
watch(selectedUser, (newUser, oldUser) => {
  // Clear the response data when a new user is selected
  responseData.value = null;
  
  // Save the old user's trades and basket selection if applicable
  if (oldUser && oldUser.id) {
    userTrades[oldUser.id] = trades.value
    userBasketsMulti[oldUser.id] = selectedBaskets.value
  }
  
  // Load new user's trades and baskets; use an empty array as default for baskets
  if (newUser && newUser.id) {
    trades.value = userTrades[newUser.id] || []
    selectedBaskets.value = userBasketsMulti[newUser.id] || []
  } else {
    trades.value = []
    selectedBaskets.value = []
  }
})
  
  // Computed: isFormValid
  const isFormValid = computed(() => {
    if (trades.value.length==0)return true
    if (!selectedUser.value) return false
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
        userId: selectedUser.value.id,
        userName: selectedUser.value.name,
        trades: [...trades.value],
        percentage: percentage.value,
        baskets: [...selectedBaskets.value]
      }
  
      // POST trades with token
      const data = await fetchData('varsimulator', 'POST', payload)

      // Store response data for display
      responseData.value = data
  
    } catch (err) {
      alert(err.message || 'Failed to submit trades. Please try again.')
    } finally {
      isSubmitting.value = false
    }
  }
  
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
  </style>
  