<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
    <div class="max-w-2xl mx-auto bg-white shadow-2xl rounded-xl overflow-hidden">
      <!-- Header -->
      <div class="bg-blue-600 text-white p-6">
        <h1 class="text-3xl font-bold">Create New Log</h1>
      </div>

      <!-- Form Container -->
      <form @submit.prevent="submitLog" class="p-8 space-y-6">
        <!-- Date and Time Row -->
        <div class="grid grid-cols-2 gap-6">
          <!-- Date Selector -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">Date</label>
            <input 
              type="date" 
              v-model="logDate" 
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              required
            />
          </div>
          <!-- Time Selector -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">Time</label>
            <input 
              type="time" 
              v-model="logTime" 
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              required
            />
          </div>
        </div>

        <!-- Category Selector with Search -->
        <div>
          <label class="block text-gray-700 font-semibold mb-2">Category</label>
          <a-select
            v-model:value="category"
            show-search
            placeholder="Select a Category"
            class="w-full"
            required
            filter-option
          >
            <a-select-option 
              v-for="option in logdetails['Category']" 
              :value="option" 
              :key="option"
            >
              {{ option }}
            </a-select-option>
            <a-select-option value="custom">Custom Category</a-select-option>
          </a-select>
          <!-- Custom Category Input -->
          <div v-if="category === 'custom'" class="mt-2">
            <input 
              type="text" 
              v-model="customCategory" 
              placeholder="Enter custom category"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              required
            />
          </div>
        </div>

        <!-- Sub Category Selector with Search -->
        <div>
          <label class="block text-gray-700 font-semibold mb-2">Sub Category</label>
          <a-select
            v-model:value="subcategory"
            show-search
            placeholder="Select a Sub Category"
            class="w-full"
            required
            filter-option
          >
            <a-select-option 
              v-for="option in logdetails['Sub Category']" 
              :value="option" 
              :key="option"
            >
              {{ option }}
            </a-select-option>
            <a-select-option value="custom">Custom Sub Category</a-select-option>
          </a-select>
          <!-- Custom Sub Category Input -->
          <div v-if="subcategory === 'custom'" class="mt-2">
            <input 
              type="text" 
              v-model="customSubcategory" 
              placeholder="Enter custom sub category"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              required
            />
          </div>
        </div>

        <!-- Message Section -->
        <div class="space-y-4">
          <div>
            <label class="block text-gray-700 font-semibold mb-2">Message Title</label>
            <input 
              type="text" 
              v-model="messageTitle" 
              placeholder="Enter log title"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              required
            />
          </div>
          <div>
            <label class="block text-gray-700 font-semibold mb-2">Message Body</label>
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
            Create Log
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { message, Select } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
const { Option: ASelectOption } = Select

const router = useRouter()

// Form Data
const logDate = ref('')
const logTime = ref('00:00')
const category = ref('')
const customCategory = ref('')
const subcategory = ref('')
const customSubcategory = ref('')
const messageTitle = ref('')
const messageBody = ref('')
const logdetails = ref({ 'Category': [], 'Sub Category': [] })
const loading = ref(true)

// Function to convert a string to camelCase
function toCamelCase(str) {
  if (!str) return '';
  return str
    .trim()
    .split(/[\s-_]+/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}


// Submit Handler
async function submitLog() {
  try {
    // Combine date and time
    const fullDateTime = `${logDate.value}T${logTime.value}`

    // Determine final category and subcategory values with camelCase conversion
    const finalCategory = category.value === 'custom' 
      ? toCamelCase(customCategory.value) 
      : toCamelCase(category.value)
    const finalSubcategory = subcategory.value === 'custom' 
      ? toCamelCase(customSubcategory.value) 
      : toCamelCase(subcategory.value)

    

    // Prepare payload
    const payload = {
      Date: fullDateTime,
      Category: finalCategory,
      SubCategory: finalSubcategory,
      Message: {
        Title: messageTitle.value,
        Body: messageBody.value
      }
    }

    // Get token for authentication
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('User not authenticated')

    // Send to API
    const response = await fetch('https://production2.swancapital.in/appendlog', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorMessage = await response.text()
      throw new Error(`Error creating log: ${errorMessage}`)
    }

    // Show success message using Ant Design Vue message
    message.success('Log created successfully!')

    // Reset form
    resetForm()

    // Navigate back to log list
    router.push('/dailylogs')
  } catch (error) {
    console.error('Log creation error:', error)
    message.error(error.message)
  }
}

async function fetchData(endpoint, stateRef) {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('User not authenticated')

    const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const errorMessage = await response.text()
      throw new Error(`Error fetching ${endpoint}: ${errorMessage}`)
    }

    const data = await response.json()
    stateRef.value = data || []
  } catch (err) {
    console.error(`Error fetching ${endpoint}:`, err.message)
  }
  loading.value = false
}

const fetchLogsDetails = () => fetchData('getdailylogsdetails', logdetails)

// Reset Form
function resetForm() {
  logDate.value = ''
  logTime.value = ''
  category.value = ''
  customCategory.value = ''
  subcategory.value = ''
  customSubcategory.value = ''
  messageTitle.value = ''
  messageBody.value = ''
}

// On component mount, fetch the log details
onMounted(async () => {
  loading.value = true
  await fetchLogsDetails()
  loading.value = false
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
