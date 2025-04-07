<template>
    <div class="p-6 max-w-3xl mx-auto">
      <!-- Form Section -->
      <form
        @submit.prevent="submitForm"
        class="flex flex-col space-y-4 bg-white p-6 rounded-md shadow-md"
      >
        <!-- Index Selection -->
        <div>
          <label class="font-semibold block mb-1">Select Index</label>
          <select
            v-model="selectedIndex"
            class="border border-gray-300 rounded w-full p-2 focus:outline-none focus:ring-2"
          >
            <option v-for="idx in indices" :key="idx" :value="idx">{{ idx }}</option>
          </select>
        </div>
  
        <!-- Single Date Picker -->
        <div>
          <label class="font-semibold block mb-1">Select Date</label>
          <input
            type="date"
            v-model="selectedDate"
            class="border border-gray-300 rounded w-full p-2 focus:outline-none focus:ring-2"
          />
        </div>
  
        <!-- Submit Button -->
        <button
          type="submit"
          class="bg-blue-600 text-white font-semibold py-2 px-4 rounded hover:bg-blue-700 transition-colors"
        >
          Submit
        </button>
      </form>
  
      <!-- Table + Search Section -->
      <div class="mt-8 bg-white p-6 rounded-md shadow-md">
        <h2 class="text-xl font-bold mb-4">Option Chain</h2>
  
        <!-- Search Input -->
        <div class="mb-4">
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Search Symbol..."
            class="border border-gray-300 rounded w-full p-2 focus:outline-none focus:ring-2"
          />
        </div>
  
        <!-- Table Wrapper with fixed height & scroll -->
        <div class="overflow-y-auto max-h-64">
          <table class="w-full border-collapse text-left">
            <thead>
              <tr class="border-b-2">
                <th class="py-2 px-2">Symbol</th>
                <th class="py-2 px-2">LTP</th>
                <th class="py-2 px-2">Copy</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, index) in filteredData"
                :key="index"
                class="border-b cursor-pointer hover:bg-gray-100"
              
              >
                <td class="py-2 px-2">{{ row.symbol }}</td>
                <td class="py-2 px-2">{{ row.ltp }}</td>
                <td class="py-2 px-2">
                  <!-- Copy Button -->
                  <button
                    @click.stop="copySymbol(row.symbol)"
                    class="bg-blue-500 text-white font-semibold py-1 px-2 rounded hover:bg-blue-600 transition-colors"
                  >
                    Copy
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, defineEmits } from 'vue'
  
  const emit = defineEmits(['symbolSelected'])
  
  /**
   * Options for the index dropdown
   */
  const indices = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'FINNIFTY']
  
  // Reactive state
  const selectedIndex = ref(indices[0])
  
  // Single date picker bound to this ref
  const selectedDate = ref('')
  
  const error = ref("")
  
  // Table & Search
  const tableData = ref([
    { symbol: 'NIFTY23MAR10000CE', ltp: 120.5 },
    { symbol: 'BANKNIFTY23APR32000PE', ltp: 230.0 },
    { symbol: 'SENSEX23MAR40000CE', ltp: 95.75 },
    { symbol: 'FINNIFTY23JAN17000PE', ltp: 102.0 }
  ])
  const searchTerm = ref('')
  
  // Computed to filter the table data based on the search term
  const filteredData = computed(() => {
    if (!searchTerm.value) return tableData.value
    return tableData.value.filter(row =>
      row.symbol.toLowerCase().includes(searchTerm.value.toLowerCase())
    )
  })
  
  /**
   * Extracts year, month, day from a given date string in 'YYYY-MM-DD' format
   * and returns { year, month, day } each as two-digit strings if possible.
   */
  function parseSelectedDate(dateStr) {
    const dateObj = new Date(dateStr)
    if (isNaN(dateObj)) {
      // If user hasn't selected a valid date, handle it (e.g., blank or throw error)
      return { year: '', month: '', day: '' }
    }
    // Last two digits of full year
    const year = dateObj.getFullYear().toString().slice(-2)
    // (Month is zero-based in JS, so +1, then pad with leading '0' if needed)
    const month = String(dateObj.getMonth() + 1).padStart(2, '0')
    // Day also needs leading '0' if < 10
    const day = String(dateObj.getDate()).padStart(2, '0')
    return { year, month, day }
  }
  
  /**
   * Submits the form data.
   */
  async function submitForm() {
    // parse the selected date into year, month, day
    const { year, month, day } = parseSelectedDate(selectedDate.value)
  
    const formData = {
      index: selectedIndex.value,
      year,
      month,
      day
    }
  
    console.log('Submitting Form Data:', formData)
    await postData('optionchain', formData, tableData)
  }
  
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

  
  /**
   * Copies the given symbol to the clipboard and shows an alert.
   */
  async function copySymbol(symbol) {
    try {
      await navigator.clipboard.writeText(symbol)
      alert(`Symbol "${symbol}" copied to clipboard!`)
    } catch (err) {
      console.error('Failed to copy symbol:', err)
    }
  }
  </script>
  
  <style scoped>
  /* Minimal or Tailwind-based styling. Adjust to your preferences if needed. */
  </style>
  