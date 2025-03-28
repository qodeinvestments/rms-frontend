<template>
    <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div class="max-w-2xl mx-auto bg-white shadow-2xl rounded-xl overflow-hidden">
        <!-- Header -->
        <div class="bg-blue-600 text-white p-6">
          <h1 class="text-3xl font-bold">Update Log</h1>
        </div>
    
        <!-- Form Container -->
        <form @submit.prevent="updateLog" class="p-8 space-y-6">
          <!-- Date and Time Row -->
          <div class="grid grid-cols-2 gap-6">
            <!-- Date Selector -->
            <div>
              <label class="block text-gray-700 font-semibold mb-2">
                Date
              </label>
              <input 
                type="date" 
                v-model="logDate" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                required
              />
            </div>
    
            <!-- Time Selector -->
            <div>
              <label class="block text-gray-700 font-semibold mb-2">
                Time
              </label>
              <input 
                type="time" 
                v-model="logTime" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                required
              />
            </div>
          </div>
    
          <!-- Category Selector -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              Category
            </label>
            <select 
              v-model="category" 
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              required
            >
              <option value="" disabled>Select a Category</option>
              <option value="Execution">Execution</option>
              <option value="Broker">Broker</option>
            </select>
          </div>
    
          <!-- Message Section -->
          <div class="space-y-4">
            <div>
              <label class="block text-gray-700 font-semibold mb-2">
                Message Title
              </label>
              <input 
                type="text" 
                v-model="messageTitle" 
                placeholder="Enter log title"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                required
              />
            </div>
    
            <div>
              <label class="block text-gray-700 font-semibold mb-2">
                Message Body
              </label>
              <textarea 
                v-model="messageBody" 
                placeholder="Enter log details"
                rows="4"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none"
                required
              ></textarea>
            </div>
          </div>
    
          <!-- Submit Button -->
          <div>
            <button 
              type="submit" 
              class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-all duration-300 ease-in-out transform hover:scale-101 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            >
              Update Log
            </button>
          </div>
        </form>
      </div>
    </div>
  </template>
    
  <script setup>
  import { ref, onMounted } from 'vue'
  import { message } from 'ant-design-vue'
  import { useRouter, useRoute } from 'vue-router'
  
  const router = useRouter()
  const route = useRoute()
  
  // Form Data
  const logDate = ref('')
  const logTime = ref('')
  const category = ref('')
  const messageTitle = ref('')
  const messageBody = ref('')
  
  // We'll store the log index to update (as returned from the backend or from route params)
  const logIndex = ref(null)
  
  // Update Log Submit Handler
  async function updateLog() {
    try {
      // Combine date and time into a full datetime string
      const fullDateTime = `${logDate.value}T${logTime.value}`
  
      // Prepare payload including the index
      const payload = {
        index: logIndex.value,
        Date: fullDateTime,
        Category: category.value,
        Message: {
          Title: messageTitle.value,
          Body: messageBody.value
        }
      }
  
      // Get token for authentication
      const token = localStorage.getItem('access_token')
      if (!token) throw new Error('User not authenticated')
  
      // Send update request to the API
      const response = await fetch('https://production2.swancapital.in/updatelog', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })
  
      if (!response.ok) {
        const errorMessage = await response.text()
        throw new Error(`Error updating log: ${errorMessage}`)
      }
  
      const data = await response.json()
  
      // Display success message
      message.success(data.detail || 'Log updated successfully!')
  
      // Navigate back to daily logs list
      router.push('/dailylogs')
  
    } catch (error) {
      console.error('Log update error:', error)
      message.error(error.message || 'Failed to update log.')
    }
  }
  
  // Reset Form (optional)
  function resetForm() {
    logDate.value = ''
    logTime.value = ''
    category.value = ''
    messageTitle.value = ''
    messageBody.value = ''
  }
  
  // API Function: Fetch the specific log to pre-fill the form
  async function fetchSpecificLog(index) {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) throw new Error('User not authenticated')
  
      const response = await fetch('https://production2.swancapital.in/getspecificlog', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ index })
      })
  
      if (!response.ok) {
        const errorMessage = await response.text()
        throw new Error(`Error fetching log: ${errorMessage}`)
      }
  
      const data = await response.json()
  
      // Store the log index (either from the data or fallback to the route param)
      logIndex.value = data.id || index
  
      // Parse the date and time from the backend timestamp
      const dateTime = new Date(data['Date'])
      logDate.value = dateTime.toISOString().split('T')[0]
      logTime.value = dateTime.toTimeString().slice(0, 5)
      category.value = data["Category"]
      messageTitle.value = data["Message"]['Title']
      messageBody.value = data["Message"]['Body']
  
    } catch (err) {
      console.error('Error fetching log:', err.message)
    }
  }
  
  // On component mount, fetch the specific log using the index from route params
  onMounted(async () => {
    const index = route.params.id
    await fetchSpecificLog(index)
  })
  </script>
    
  <style scoped>
  input, select, textarea {
    transition: all 0.3s ease;
  }
  
  input:focus, select:focus, textarea:focus {
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
    border-color: #3b82f6;
  }
  </style>
  