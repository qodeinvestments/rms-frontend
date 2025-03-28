<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="container mx-auto">
      <!-- Create New Log Button -->
      <div class="mb-6">
        <a-button  @click="handleCreateNewLog">
          Create New Log
        </a-button>
      </div>

      <!-- Category Select -->
      <a-select 
        v-model:value="selectedCategories"
        mode="multiple" 
        placeholder="Select Categories" 
        class="w-full mb-6"
        :options="categoryOptions"
      >
      </a-select>
      

      <!-- Modern Table -->
      <div class="bg-white shadow-lg rounded-lg overflow-hidden">
        <table class="w-full">
          <thead class="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
            <tr>
              <th class="px-6 py-4 text-left font-semibold">Date</th>
              <th class="px-6 py-4 text-left font-semibold">Category</th>
              <th class="px-6 py-4 text-left font-semibold">Message</th>
              <th class="px-6 py-4 text-center font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="log in filteredLogs" 
              :key="log.id" 
              class="border-b hover:bg-gray-100 transition-colors duration-200"
            >
              <td class="px-6 py-4">{{ log.Date }}</td>
              <td class="px-6 py-4">
                <span 
                  class="px-3 py-1 rounded-full text-xs font-medium"
                  :class="getCategoryClass(log.Category)"
                >
                  {{ log.Category }}
                </span>
              </td>
              <td class="px-6 py-4">{{ log.Message['Title'] }}</td>
              <td class="px-6 py-4 flex justify-center space-x-2">
                <!-- Read Button -->
                <button 
                  @click="handleRead(log)"
                  class="bg-green-500 text-white px-3 py-1 rounded-md hover:bg-green-600 transition-colors"
                >
                  Read
                </button>
                
                <!-- Update Button -->
                <button 
                  @click="handleUpdate(log)"
                  class="bg-blue-500 text-white px-3 py-1 rounded-md hover:bg-blue-600 transition-colors"
                >
                  Update
                </button>
                
                <!-- Delete Button -->
                <button 
                  @click="handleDelete(log)"
                  class="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 transition-colors"
                >
                  Delete
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
import { ref, computed, onMounted } from 'vue'
import { Select, Button, message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
const router = useRouter()

// Reactive State
const logs = ref([])
const selectedCategories = ref([])
const error = ref(null)
const loading = ref(false)

// Computed Properties
const categoryOptions = computed(() => {
  const uniqueCategories = [...new Set(logs.value.map(log => log.Category))]
  return uniqueCategories.map(category => ({
    label: category,
    value: category
  }))
})

const filteredLogs = computed(() => {
  if (selectedCategories.value.length === 0) return logs.value
  return logs.value.filter(log => 
    selectedCategories.value.includes(log.Category)
  )
})

// Category Color Mapping
const getCategoryClass = (category) => {
  const categoryColors = {
    'Execution': 'bg-blue-100 text-blue-800',
    'Broker': 'bg-green-100 text-green-800',
    'Default': 'bg-gray-100 text-gray-800'
  }
  return categoryColors[category] || categoryColors['Default']
}

// Action Handlers
async function handleRead(log) {
  router.push(`/readlog/${log.id}`)
  try {
    message.success('Log read successfully')
  } catch (err) {
    message.error('Failed to read log')
    console.error('Read error:', err)
  }
}



async function handleUpdate(log) {
  router.push(`/updatelog/${log.id}`)
  try {
    message.success('Log Detail Fetched Successfully')
  } catch (err) {
    message.error('Failed to update log')
    console.error('Update error:', err)
  }
}


async function handleDelete(log) {
  try {
    await postData('deletelog', { index: log.id }, null)
    logs.value = logs.value.filter(item => item.id !== log.id)
    message.success('Log deleted successfully')
  } catch (err) {
    message.error('Failed to delete log')
    console.error('Delete error:', err)
  }
}
function handleCreateNewLog() {
  router.push('/newlog')
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

const fetchLogs = () => fetchData('getdailylogs', logs)

// Lifecycle Hook
onMounted(fetchLogs)
</script>

<style scoped>
/* Additional custom styles can be added here if needed */
</style>
