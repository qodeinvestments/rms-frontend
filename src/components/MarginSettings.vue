<template>
    <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div class="container mx-auto">
        <!-- Header Section -->
        <div class="mb-8 text-center">
          <h1 class="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 mb-2">
            Client Margin Configuration
          </h1>
          <p class="text-gray-600">Manage your client margins and expiry dates efficiently</p>
        </div>
  
        <!-- Search and Filter Card -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Search Bar -->
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-4">
                <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </span>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search clients..."
                class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-gray-50"
              />
            </div>
            
            <!-- Prefix Filter -->
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-4">
                <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/>
                </svg>
              </span>
              <select
                v-model="selectedPrefix"
                class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-gray-50 appearance-none cursor-pointer"
              >
                <option value="">All Prefixes</option>
                <option v-for="prefix in uniquePrefixes" :key="prefix" :value="prefix">
                  {{ prefix }}
                </option>
              </select>
            </div>
          </div>
        </div>
        <!-- Notification Panel (displays when there are errors) -->
        <div v-if="hasErrors" class="mt-6 mb-6 bg-red-50 border border-red-200 rounded-lg p-4 shadow-sm">
        <div class="flex items-start">
            <svg class="w-5 h-5 text-red-500 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
            <p class="text-sm font-medium text-red-800">Please correct the following errors:</p>
            <ul class="mt-1 text-xs text-red-700 list-disc list-inside space-y-1">
                <li v-if="errorCount.expiryDate">{{ errorCount.expiryDate }} clients missing expiry date</li>
                <li v-if="errorCount.excessMargin">{{ errorCount.excessMargin }} clients missing excess margin</li>
                <li v-if="errorCount.minimumMargin">{{ errorCount.minimumMargin }} clients missing minimum margin</li>
                <li v-if="errorCount.drawdownMargin">{{ errorCount.drawdownMargin }} clients missing drawdown margin %</li>
            </ul>
            </div>
        </div>
        </div>
  
        <!-- Table Card -->
        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr class="bg-gradient-to-r from-indigo-50 to-blue-50">
                  <th class="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-wider">
                    <div class="flex items-center">
                      <input 
                        type="checkbox" 
                        @change="toggleAllSelection" 
                        :checked="allSelected"
                        class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                      />
                    </div>
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-wider">Client</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-wider">Expiry Date</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-wider">Excess Margin</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-wider">Minimum Margin</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-wider">Drawdown Margin %</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="client in filteredClients" 
                    :key="client.id" 
                    :class="['hover:bg-gray-50 transition-colors duration-150', client.hasError ? 'bg-red-50' : '']">
                  <td class="px-6 py-4">
                    <div class="flex items-center">
                      <input 
                        type="checkbox" 
                        v-model="client.selected"
                        class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                      />
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm font-semibold text-gray-900">{{ client.client }}</div>
                  </td>
                 <!-- Expiry Date -->
                    <td class="px-6 py-4">
                        <input
                            type="date"
                            v-model="client.expiryDate"
                            @input="validateClient(client)"
                            :class="['px-4 py-2 border-2 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-gray-50', 
                                    client.errors?.expiryDate ? 'border-red-300' : 'border-gray-200']"
                        />
                        <div class="h-5 py-1 px-2">
                            <p v-if="client.errors?.expiryDate" class="text-xs text-red-500">{{ client.errors.expiryDate }}</p>
                        </div>
                    </td>
  
                    <!-- Excess Margin -->
                    <td class="px-6 py-4">
                        <input
                            type="number"
                            v-model="client.excessMargin"
                            @input="validateClient(client)"
                            placeholder="Enter excess margin"
                            :class="['px-4 py-2 border-2 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-gray-50 w-full',
                                    client.errors?.excessMargin ? 'border-red-300' : 'border-gray-200']"
                        />
                        <div class="h-5 py-1 px-2">
                            <p v-if="client.errors?.excessMargin" class="text-xs text-red-500">{{ client.errors.excessMargin }}</p>
                        </div>
                    </td>
  
                    <!-- Minimum Margin -->
                    <td class="px-6 py-4">
                        <input
                            type="number"
                            v-model="client.minimumMargin"
                            @input="validateClient(client)"
                            placeholder="Enter minimum margin"
                            :class="['px-4 py-2 border-2 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-gray-50 w-full',
                                    client.errors?.minimumMargin ? 'border-red-300' : 'border-gray-200']"
                        />
                        <div class="h-5 py-1 px-2">
                            <p v-if="client.errors?.minimumMargin" class="text-xs text-red-500">{{ client.errors.minimumMargin }}</p>
                        </div>
                    </td>
  
                    <!-- Drawdown Margin % -->
                    <td class="px-6 py-4">
                        <input
                            type="number"
                            v-model="client.drawdownMargin"
                            @input="validateClient(client)"
                            placeholder="Enter drawdown margin %"
                            :class="['px-4 py-2 border-2 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-gray-50 w-full',
                                    client.errors?.drawdownMargin ? 'border-red-300' : 'border-gray-200']"
                        />
                        <div class="h-5 py-1 px-2">
                            <p v-if="client.errors?.drawdownMargin" class="text-xs text-red-500">{{ client.errors.drawdownMargin }}</p>
                        </div>
                    </td>
  
                  <td class="px-6 py-4">
                    <div class="flex space-x-2">
                      <button
                        @click="submitSingleClient(client)"
                        class="inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-150 shadow-md hover:shadow-lg"
                      >
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        Save
                      </button>
                      <button
                        @click="resetSingleClient(client)"
                        class="inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-150"
                      >
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Reset
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
    
  
        <!-- Action Buttons -->
        <div class="mt-8 flex justify-between">
          <!-- Selected Count Badge -->
          <div class="flex items-center">
            <span class="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-indigo-100 text-indigo-800">
              {{ selectedCount }} clients selected
            </span>
          </div>
  
          <!-- Button Group -->
          <div class="flex space-x-4">
            <button
              @click="resetAllClients"
              class="flex items-center px-6 py-3 rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 transition shadow"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Reset All
            </button>
  
            <button
              @click="submitSelectedClients"
              :disabled="selectedCount === 0"
              :class="[
                'flex items-center px-6 py-3 rounded-md text-white transition shadow',
                selectedCount === 0 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-indigo-600 hover:bg-indigo-700'
              ]"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Save Selected
            </button>
  
            <button
              @click="submitAllClients"
              class="flex items-center px-6 py-3 rounded-md text-white bg-green-600 hover:bg-green-700 transition shadow"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Save All Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { watch } from "vue";
  import { getData, postData } from '../utils/apiUtils.js'
  
  const clients = ref([])
  const searchQuery = ref('')
  const selectedPrefix = ref('')
  
  const uniquePrefixes = computed(() => {
    const prefixes = new Set(
      clients.value.map(client => {
        const match = client.client.match(/^[A-Za-z]+/)
        return match ? match[0] : ''
      })
    )
    return Array.from(prefixes).sort()
  })
  
  const filteredClients = computed(() => {
    let filtered = clients.value
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(client => 
        client.client.toLowerCase().includes(query)
      )
    }
    
    if (selectedPrefix.value) {
      filtered = filtered.filter(client => 
        client.client.startsWith(selectedPrefix.value)
      )
    }
    
    return filtered
  })
  
  const selectedCount = computed(() => {
    return clients.value.filter(client => client.selected).length
  })
  
  const allSelected = computed(() => {
    return clients.value.length > 0 && clients.value.every(client => client.selected)
  })
  
  const hasErrors = computed(() => {
    return clients.value.some(client => client.hasError)
  })
  
  const errorCount = computed(() => {
    return {
      expiryDate: clients.value.filter(client => client.errors?.expiryDate).length,
      excessMargin: clients.value.filter(client => client.errors?.excessMargin).length,
      minimumMargin: clients.value.filter(client => client.errors?.minimumMargin).length,
      drawdownMargin: clients.value.filter(client => client.errors?.drawdownMargin).length
    }
  })
  
  const toggleAllSelection = (event) => {
    const isChecked = event.target.checked
    clients.value.forEach(client => {
      client.selected = isChecked
    })
  }
  const validateClient = (client) => {
    client.errors = {};
    client.hasError = false;
  
    // Check if any field has been entered
    const hasAnyValue = client.expiryDate || client.excessMargin || client.minimumMargin || client.drawdownMargin;
  
    if (hasAnyValue) {
        if (!client.expiryDate) {
            client.errors.expiryDate = "Expiry date is required";
            client.hasError = true;
        }
  
        if (!client.excessMargin && client.excessMargin !== 0) {
            client.errors.excessMargin = "Excess margin is required";
            client.hasError = true;
        }
  
        if (!client.minimumMargin && client.minimumMargin !== 0) {
            client.errors.minimumMargin = "Minimum margin is required";
            client.hasError = true;
        }
  
        if (!client.drawdownMargin && client.drawdownMargin !== 0) {
            client.errors.drawdownMargin = "Drawdown margin % is required";
            client.hasError = true;
        }
    }
  
    return !client.hasError;
  };
  
  
  const validateClients = (clientsToValidate) => {
    let isValid = true
    
    clientsToValidate.forEach(client => {
      if (!validateClient(client)) {
        isValid = false
      }
    })
    
    return isValid
  }
  
  const fetchClients = async () => {
    try {
      const data = await getData('getclientDetails')
      clients.value = data['clients'].map(client => ({
        client,
        id: Math.random().toString(36).substring(2, 11), // Temporary ID for demo
        expiryDate: '',
        excessMargin: '',
        minimumMargin: '',
        drawdownMargin: '',
        selected: false,
        errors: {},
        hasError: false
      }))
    } catch (error) {
      console.error('Error fetching clients:', error)
    }
  }
  
  const submitSingleClient = async (client) => {
    if (!validateClient(client)) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      return
    }
    
    try {
      const payload = {
        clientId: client.id,
        expiryDate: client.expiryDate,
        excessMargin: client.excessMargin,
        minimumMargin: client.minimumMargin,
        drawdownMargin: client.drawdownMargin
      }
      await postData('client/update', payload)
      alert(`Successfully updated ${client.client}`)
    } catch (error) {
      alert(`Error updating ${client.client}: ${error.message}`)
    }
  }
  
  const submitSelectedClients = async () => {
    const selectedClients = clients.value.filter(client => client.selected)
    
    if (selectedClients.length === 0) {
      alert('Please select at least one client')
      return
    }
    
    if (!validateClients(selectedClients)) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      return
    }
    
    try {
      const payload = selectedClients.map(client => ({
        clientId: client.id,
        expiryDate: client.expiryDate,
        excessMargin: client.excessMargin,
        minimumMargin: client.minimumMargin,
        drawdownMargin: client.drawdownMargin
      }))
      
      await postData('client/update-selected', payload)
      alert(`Successfully updated ${selectedClients.length} clients`)
    } catch (error) {
      alert(`Error updating selected clients: ${error.message}`)
    }
  }
  
  const submitAllClients = async () => {
    if (!validateClients(clients.value)) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      return
    }
    
    try {
      const payload = clients.value.map(client => ({
        clientId: client.id,
        expiryDate: client.expiryDate,
        excessMargin: client.excessMargin,
        minimumMargin: client.minimumMargin,
        drawdownMargin: client.drawdownMargin
      }))
      await postData('client/update-all', payload)
      alert('Successfully updated all clients')
    } catch (error) {
      alert(`Error updating clients: ${error.message}`)
    }
  }
  
  // New reset functions
  const resetSingleClient = (client) => {
    client.expiryDate = '';
    client.excessMargin = '';
    client.minimumMargin = '';
    client.drawdownMargin = '';
    client.errors = {};
    client.hasError = false;
    // Keep the selection state as is
  }
  
  const resetAllClients = () => {
    clients.value.forEach(client => {
      client.expiryDate = '';
      client.excessMargin = '';
      client.minimumMargin = '';
      client.drawdownMargin = '';
      client.errors = {};
      client.hasError = false;
      // Keep the selection state as is
    });
  }
  
  watch(
  () => clients.value.map(client => client.hasError),
  () => {
    hasErrors.value = clients.value.some(client => client.hasError);
  },
  { deep: true }
  );
  
  
  onMounted(() => {
    fetchClients()
  })
  </script>
  
  <style scoped>
  .container {
    max-width: 1200px;
  }
  
  input[type="number"] {
    -moz-appearance: textfield;
  }
  
  input[type="number"]::-webkit-outer-spin-button,
  input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  
  /* Custom select arrow */
  select {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236366F1'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
    background-position: right 1rem center;
    background-repeat: no-repeat;
    background-size: 1.5em 1.5em;
  }
  
  input[type="checkbox"] {
    cursor: pointer;
  }
  </style>