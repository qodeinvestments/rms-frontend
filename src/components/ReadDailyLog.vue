<template>
    <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div class="max-w-4xl mx-auto bg-white shadow-xl rounded-xl overflow-hidden">
        <!-- Header -->
        <div class="bg-blue-600 text-white p-6">
          <h1 class="text-2xl font-bold">Log Details</h1>
        </div>
        
    
  
        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
        </div>
  
        <!-- Error State -->
        <div v-else-if="error" class="p-6 bg-red-50 text-red-700">
          <p class="font-semibold">{{ error }} There is an error</p>
        </div>
       
        <!-- Log Content -->
        <div v-else-if="logs " class="p-6 space-y-6">
          <!-- Log Card -->
          <div class="bg-gray-50 rounded-lg p-6 border border-gray-200 shadow-sm">
            <!-- Date and Category -->
            <div class="flex justify-between items-center mb-4">
              <div class="flex items-center space-x-3">
                <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  {{ logs.Category }}
                </span>
                <time class="text-gray-500 text-sm">
                  {{ formatDate(logs.Date) }}
                </time>
              </div>
            </div>
            <!-- Message Details -->
            <div class="space-y-4">
              <h2 class="text-xl font-bold text-gray-800">
                {{ logs["Message"]['Title'] || 'Untitled Log' }}
              </h2>
              <p class="text-gray-600 leading-relaxed">
                {{ logs["Message"]['Body']|| 'No additional details available.' }}
              </p>
            </div>
          </div>
        </div>
  
        <!-- No Logs State -->
        <div v-else class="p-6 text-center text-gray-500">
          <p>No logs found for this entry.</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { API_BASE_URL, WS_BASE_URL } from '../config/url'
  // Reactive State
  const logs = ref([])
  const error = ref(null)
  const loading = ref(true)
  const route = useRoute()
  
  // Date Formatting Function
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // API Function
  async function fetchSpecificLogs(index) {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) throw new Error('User not authenticated')
  
      const response = await fetch(`${API_BASE_URL}getspecificlog`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ index }),
      })
  
      if (!response.ok) {
        const errorMessage = await response.text()
        throw new Error(`Error fetching log: ${errorMessage}`)
      }
  
      const data = await response.json()
      logs.value = data || []
    } catch (err) {
      error.value = err.message
      console.error('Error fetching log:', err.message)
    } finally {
      loading.value = false
    }
  }
  
  onMounted(async () => {
    const index = route.params.id
    await fetchSpecificLogs(index)
  })
  </script>
  
  <style scoped>
  /* Additional custom styles if needed */
  </style>