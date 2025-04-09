<template>
    <div class="bg-gray-100 p-4 rounded-lg">

      <!-- Card with form and option chain -->
      <div class="bg-white rounded-xl shadow-lg overflow-hidden">
        <!-- Form Section -->
        <div class="p-2 bg-gradient-to-r from-blue-500 to-purple-600">
          <form
            @submit.prevent="submitForm"
            class="flex flex-wrap gap-3 items-end"
          >
            <!-- Index Selection -->
            <div class="flex-1 min-w-48">
              <label class="font-semibold block mb-2 text-white">Index</label>
              <select
                v-model="selectedIndex"
                class="border border-gray-300 rounded-lg w-full p-2 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              >
                <option v-for="idx in indices" :key="idx" :value="idx">{{ idx }}</option>
              </select>
            </div>
            


            <!-- Category Selector with Search -->
            <div class="flex-1 min-w-48">
              <label class="block text-gray-700 font-semibold mb-2">Expiry Dates</label>
              <a-select
                v-model:value="selectedDate"
                show-search
                placeholder="Select a Expiry Dates"
                class="w-full"
                required
                filter-option
              >
                <a-select-option 
                  v-for="option in optionsDetails[selectedIndex]" 
                  :value="option" 
                  :key="option"
                >
                  {{ option }}
                </a-select-option>
              </a-select>
            </div>
            
            <!-- Submit Button -->
            <div>
              <button
                type="submit"
                class="bg-white text-blue-600 font-bold py-2 px-4 rounded-lg hover:bg-blue-50 transition-colors shadow-sm"
              >
                Fetch Chain
              </button>
            </div>
          </form>
        </div>
        
        <!-- Option Chain Section -->
        <div class="p-2">
          <!-- Header & Last fetched time -->
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold text-gray-800">Option Chain Data</h2>
            <div v-if="lastFetchedTime" class="text-gray-500 text-sm">
              Last Updated: {{ formatDateTime(lastFetchedTime) }}
            </div>
          </div>
          
          <!-- Error message if any -->
          <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
            {{ error }}
          </div>
  
          <!-- Single scroll container for both CE and PE tables -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 overflow-auto rounded-lg border border-gray-200 max-h-[400px] p-4">
  
            <!-- CE Column -->
            <div class="bg-gray-50 rounded-xl shadow-md p-4">
              <div class="flex justify-between items-center mb-3">
                <h3 class="text-lg font-bold text-blue-600">Call Options (CE)</h3>
                <div class="flex space-x-2">
                  <span class="inline-block w-3 h-3 rounded-full bg-green-500"></span>
                  <span class="text-xs text-gray-600">ITM</span>
                  <span class="inline-block w-3 h-3 rounded-full bg-yellow-500"></span>
                  <span class="text-xs text-gray-600">ATM</span>
                  <span class="inline-block w-3 h-3 rounded-full bg-red-500"></span>
                  <span class="text-xs text-gray-600">OTM</span>
                </div>
              </div>
  
              <!-- CE Search Input -->
              <div class="relative mb-3">
                <input
                  v-model="ceSearchTerm"
                  type="text"
                  placeholder="Search CE Symbol..."
                  class="border border-gray-300 rounded-lg w-full p-2 pl-8 focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-2 top-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 
                    11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
  
              <!-- CE Table (no separate scrollbar here) -->
              <table class="w-full border-collapse text-left">
                <thead>
                  <tr class="bg-gray-100">
                    <th class="py-2 px-3 font-semibold text-gray-700 text-sm">Symbol</th>
                    <th class="py-2 px-3 font-semibold text-gray-700 text-sm">LTP</th>
                    <th class="py-2 px-3 font-semibold text-gray-700 text-sm">Moneyness</th>
                    <th class="py-2 px-3 font-semibold text-gray-700 text-sm text-center">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(row, index) in filteredCeData"
                    :key="index"
                    class="border-t border-gray-200 hover:bg-gray-50 transition-colors"
                    :class="getRowClass(row.moneyness)"
                  >
                    <td class="py-2 px-3 font-medium text-sm">{{ row.symbol }}</td>
                    <td class="py-2 px-3 text-sm">₹{{ row.ltp }}</td>
                    <td class="py-2 px-3 text-sm">
                      <span
                        :class="getMoneynessPillClass(row.moneyness)"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ row.moneyness }}
                      </span>
                    </td>
                    <td class="py-2 px-3 text-center">
                      <button
                        @click="copySymbol(row.symbol)"
                        class="bg-blue-500 text-white rounded-lg p-1.5 hover:bg-blue-600 transition-colors"
                        title="Copy Symbol"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M8 16H6a2 
                            2 0 01-2-2V6a2 2 0 012-2h8a2 
                            2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 
                            2 0 00-2-2h-8a2 2 0 00-2 2v8a2 
                            2 0 002 2z"
                          />
                        </svg>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="filteredCeData.length === 0">
                    <td colspan="4" class="py-4 px-3 text-center text-gray-500 text-sm">No data available</td>
                  </tr>
                </tbody>
              </table>
            </div>
  
            <!-- PE Column -->
            <div class="bg-gray-50 rounded-xl shadow-md p-4">
              <div class="flex justify-between items-center mb-3">
                <h3 class="text-lg font-bold text-purple-600">Put Options (PE)</h3>
                <div class="flex space-x-2">
                  <span class="inline-block w-3 h-3 rounded-full bg-green-500"></span>
                  <span class="text-xs text-gray-600">ITM</span>
                  <span class="inline-block w-3 h-3 rounded-full bg-yellow-500"></span>
                  <span class="text-xs text-gray-600">ATM</span>
                  <span class="inline-block w-3 h-3 rounded-full bg-red-500"></span>
                  <span class="text-xs text-gray-600">OTM</span>
                </div>
              </div>
  
              <!-- PE Search Input -->
              <div class="relative mb-3">
                <input
                  v-model="peSearchTerm"
                  type="text"
                  placeholder="Search PE Symbol..."
                  class="border border-gray-300 rounded-lg w-full p-2 pl-8 focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-2 top-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 
                    11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
  
              <!-- PE Table (no separate scrollbar here) -->
              <table class="w-full border-collapse text-left">
                <thead>
                  <tr class="bg-gray-100">
                    <th class="py-2 px-3 font-semibold text-gray-700 text-sm">Symbol</th>
                    <th class="py-2 px-3 font-semibold text-gray-700 text-sm">LTP</th>
                    <th class="py-2 px-3 font-semibold text-gray-700 text-sm">Moneyness</th>
                    <th class="py-2 px-3 font-semibold text-gray-700 text-sm text-center">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(row, index) in filteredPeData"
                    :key="index"
                    class="border-t border-gray-200 hover:bg-gray-50 transition-colors"
                    :class="getRowClass(row.moneyness)"
                  >
                    <td class="py-2 px-3 font-medium text-sm">{{ row.symbol }}</td>
                    <td class="py-2 px-3 text-sm">₹{{ row.ltp }}</td>
                    <td class="py-2 px-3 text-sm">
                      <span
                        :class="getMoneynessPillClass(row.moneyness)"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ row.moneyness }}
                      </span>
                    </td>
                    <td class="py-2 px-3 text-center">
                      <button
                        @click="copySymbol(row.symbol)"
                        class="bg-purple-500 text-white rounded-lg p-1.5 hover:bg-purple-600 transition-colors"
                        title="Copy Symbol"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M8 16H6a2 
                            2 0 01-2-2V6a2 2 0 012-2h8a2 
                            2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 
                            2 0 00-2-2h-8a2 2 0 00-2 2v8a2 
                            2 0 002 2z"
                          />
                        </svg>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="filteredPeData.length === 0">
                    <td colspan="4" class="py-4 px-3 text-center text-gray-500 text-sm">No data available</td>
                  </tr>
                </tbody>
              </table>
            </div>
  
          </div> <!-- End of single scroll container -->
        </div>
      </div>
  
      <!-- Toast for copy success -->
      <div
        v-if="showToast"
        class="fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 
            100-16 8 8 0 
            000 16zm3.707-9.293a1 1 0 
            00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 
            00-1.414 1.414l2 2a1 1 0 
            001.414 0l4-4z"
            clip-rule="evenodd"
          />
        </svg>
        <span>{{ toastMessage }}</span>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { message, Select } from 'ant-design-vue'
  const { Option: ASelectOption } = Select


  // Define props including the new "optionDetails" prop
  const props = defineProps({
    optionsDetails: {
      type: Object,
      required: false,
      default: () => ({})
    }
  })
  /**
   * Options for the index dropdown
   */
  const indices = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'FINNIFTY']
  
  // Reactive state
  const selectedIndex = ref(indices[0])
  const selectedDate = ref('')
  const error = ref("")
  
  // Toast notification
  const showToast = ref(false)
  const toastMessage = ref('')
  
  /**
   * tableData is an object with two arrays: CE and PE.
   * Example structure:
   * {
   *   CE: [ { symbol, ltp, moneyness }, ... ],
   *   PE: [ { symbol, ltp, moneyness }, ... ]
   * }
   */
  const tableData = ref({
    CE: [],
    PE: []
  })
  
  // Two separate search terms: one for CE, one for PE
  const ceSearchTerm = ref('')
  const peSearchTerm = ref('')
  
  // Stores the time (Date string) when data was last fetched
  const lastFetchedTime = ref(null)
  
  // On mount, restore cached data (if any) and set default date to today
  onMounted(() => {
    // Set default date to today
    const today = new Date()
    selectedDate.value = today.toISOString().split('T')[0]
    
    const cachedData = localStorage.getItem('optionchainData')
    if (cachedData) {
      try {
        const parsed = JSON.parse(cachedData)
        // Ensure parsed structure is what you expect
        if (parsed.data && parsed.data.CE && parsed.data.PE) {
          tableData.value = parsed.data
        }
        if (parsed.fetchedAt) {
          lastFetchedTime.value = parsed.fetchedAt
        }
      } catch (err) {
        console.error('Error restoring cached data:', err)
      }
    }
  })
  
  /**
   * Computed filtered data for CE
   */
  const filteredCeData = computed(() => {
    const ceData = tableData.value.CE || []
    if (!ceSearchTerm.value) return ceData
    return ceData.filter(row =>
      row.symbol.toLowerCase().includes(ceSearchTerm.value.toLowerCase())
    )
  })
  
  /**
   * Computed filtered data for PE
   */
  const filteredPeData = computed(() => {
    const peData = tableData.value.PE || []
    if (!peSearchTerm.value) return peData
    return peData.filter(row =>
      row.symbol.toLowerCase().includes(peSearchTerm.value.toLowerCase())
    )
  })
  
  /**
   * Parse the selected date to year/month/day
   */
  function parseSelectedDate(dateStr) {
    const dateObj = new Date(dateStr)
    if (isNaN(dateObj)) return { year: '', month: '', day: '' }
    const year = dateObj.getFullYear().toString().slice(-2)
    const month = String(dateObj.getMonth() + 1).padStart(2, '0')
    const day = String(dateObj.getDate()).padStart(2, '0')
    return { year, month, day }
  }
  
  /**
   * Submits the form data
   */
  async function submitForm() {
    error.value = ""
    
    if (!selectedDate.value) {
      error.value = "Please select a date"
      return
    }
    
    const { year, month, day } = parseSelectedDate(selectedDate.value)
    const formData = { index: selectedIndex.value, year, month, day }
    console.log('Submitting Form Data:', formData)
    await postData('optionchain', formData)
  }
  
  /**
   * API postData
   */
  async function postData(endpoint, payload) {
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
        throw new Error(`Error fetching option chain data: ${errorMessage}`)
      }
  
      // Expecting data in the form { CE: [...], PE: [...] }
      const data = await response.json()
      tableData.value = data || { CE: [], PE: [] }
  
      // Update the lastFetchedTime
      lastFetchedTime.value = new Date().toISOString()
  
      // Cache in localStorage
      localStorage.setItem('optionchainData', JSON.stringify({
        data: tableData.value,
        fetchedAt: lastFetchedTime.value
      }))
  
      return data
    } catch (err) {
      error.value = err.message
      console.error(`Error posting to ${endpoint}:`, err.message)
      throw err
    }
  }
  
  /**
   * Copies the symbol to clipboard and shows toast
   */
  async function copySymbol(symbol) {
    try {
      await navigator.clipboard.writeText(symbol)
      toastMessage.value = `Symbol "${symbol}" copied!`
      showToast.value = true
      
      // Hide toast after 3 seconds
      setTimeout(() => {
        showToast.value = false
      }, 3000)
    } catch (err) {
      console.error('Failed to copy symbol:', err)
      error.value = "Failed to copy to clipboard"
    }
  }
  
  /**
   * Helper to format the last fetched time
   */
  function formatDateTime(dateString) {
    if (!dateString) return ''
    const date = new Date(dateString)
    if (isNaN(date)) return ''
    const yyyy = date.getFullYear()
    const mm = String(date.getMonth() + 1).padStart(2, '0')
    const dd = String(date.getDate()).padStart(2, '0')
    const hh = String(date.getHours()).padStart(2, '0')
    const min = String(date.getMinutes()).padStart(2, '0')
    const ss = String(date.getSeconds()).padStart(2, '0')
    return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`
  }
  
  /**
   * Get CSS class for row based on moneyness
   */
  function getRowClass(moneyness) {
    if (!moneyness) return ''
    
    switch(moneyness.toUpperCase()) {
      case 'ITM': return 'bg-green-50'
      case 'ATM': return 'bg-yellow-50'
      case 'OTM': return 'bg-red-50'
      default: return ''
    }
  }
  
  /**
   * Get CSS class for moneyness pill
   */
  function getMoneynessPillClass(moneyness) {
    if (!moneyness) return 'bg-gray-200 text-gray-800'
    
    switch(moneyness.toUpperCase()) {
      case 'ITM': return 'bg-green-100 text-green-800'
      case 'ATM': return 'bg-yellow-100 text-yellow-800'
      case 'OTM': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-200 text-gray-800'
    }
  }
  </script>