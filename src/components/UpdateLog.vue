<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loader"></div>
      <p>Loading Accounts...</p>
    </div>
    <div v-else class="max-w-2xl mx-auto bg-white shadow-2xl rounded-xl overflow-hidden">
      <!-- Header -->
      <div class="bg-blue-600 text-white p-6">
        <h1 class="text-3xl font-bold">Update Log</h1>
      </div>
  
      <!-- Form Container -->
      <form @submit.prevent="openTotpModal" class="p-8 space-y-6">
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
            <option 
              v-for="option in logdetails['Category']" 
              :value="option" 
              :key="option"
            >
              {{ option }}
            </option>
            <option value="custom">Custom Category</option>
          </select>
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
  
        <!-- Sub Category Selector -->
        <div>
          <label class="block text-gray-700 font-semibold mb-2">
            Sub Category
          </label>
          <select 
            v-model="subcategory" 
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            required
          >
            <option value="" disabled>Select a Sub Category</option>
            <option 
              v-for="option in logdetails['Sub Category']" 
              :value="option" 
              :key="option"
            >
              {{ option }}
            </option>
            <option value="custom">Custom Sub Category</option>
          </select>
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
  
    <!-- TOTP Verification Modal -->
    <div v-if="showTotpModal" class="modal-overlay">
      <div class="modal-content">
        <h2 class="modal-title">Enter Password</h2>
        <div class="form-group">
          <input 
            type="password" 
            v-model="totpCode"
            placeholder="Enter password"
            class="form-input"
            :class="{ 'input-error': totpError }"
            @input="totpError = ''"
          />
          <span v-if="totpError" class="error-text">{{ totpError }}</span>
        </div>
        <div class="modal-actions">
          <button 
            @click="showTotpModal = false" 
            class="cancel-button"
          >
            Cancel
          </button>
          <button 
            @click="handleSubmitWithTotp" 
            class="submit-button"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const loading = ref(true)

// Form Data
const logDate = ref('')
const logTime = ref('')
const category = ref('')
const customCategory = ref('')
const subcategory = ref('')
const customSubcategory = ref('')
const messageTitle = ref('')
const messageBody = ref('')
const logdetails = ref({ 'Category': [], 'Sub Category': [] })
const logIndex = ref(null)

// TOTP Modal State
const showTotpModal = ref(false)
const totpCode = ref('')
const totpError = ref('')

// Helper function to convert string to camelCase
function toCamelCase(str) {
  if (!str) return ''
  return str
    .split(/[\s-_]+/)
    .map((word, index) => index === 0 ? word.toLowerCase() : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('')
}

// Open TOTP modal instead of directly submitting
function openTotpModal() {
  showTotpModal.value = true
  totpCode.value = ''
  totpError.value = ''
}

// Handle form submission with TOTP code
async function handleSubmitWithTotp() {
  try {
    if (!totpCode.value) {
      totpError.value = 'Password is required'
      return
    }
    loading.value = true
    await updateLog()
    loading.value = false
    // Close modal on success
    showTotpModal.value = false
  } catch (err) {
    if (!totpError.value) {
      totpError.value = err.message || 'An error occurred'
    }
    console.error('Update with TOTP error:', err)
  }
}

// Update Log Submit Handler
async function updateLog() {
  try {
    // Combine date and time into a full datetime string
    const fullDateTime = `${logDate.value}T${logTime.value}`

    // Determine final category and sub-category with camelCase conversion
    const finalCategory = category.value === 'custom'
      ? toCamelCase(customCategory.value)
      : toCamelCase(category.value)
    const finalSubcategory = subcategory.value === 'custom'
      ? toCamelCase(customSubcategory.value)
      : toCamelCase(subcategory.value)

    // Prepare payload including the index and TOTP code
    const payload = {
      index: logIndex.value,
      Date: fullDateTime,
      Category: finalCategory,
      SubCategory: finalSubcategory,
      Message: {
        Title: messageTitle.value,
        Body: messageBody.value
      },
      totp_code: totpCode.value
    }

    // Get token for authentication
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('User not authenticated')

    // Send update request to the API
    const response = await fetch('https://production2.swancapital.in/updatelog', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      if (response.status === 401) {
        totpError.value = 'Invalid Password. Please try again.'
        throw new Error('Invalid Password')
      }
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
    if (!totpError.value) {
      message.error(error.message || 'Failed to update log.')
    }
    throw error
  }
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
        'Content-Type': 'application/json'
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
    subcategory.value = data["SubCategory"]
    messageTitle.value = data["Message"]['Title']
    messageBody.value = data["Message"]['Body']

  } catch (err) {
    console.error('Error fetching log:', err.message)
  }
}

// API Function: Fetch default log details
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
  
// On component mount, fetch the specific log using the route param and then the log details.
// If the fetched category or sub-category is not in the default list, pre-select custom.
onMounted(async () => {
  const index = route.params.id
  loading.value = true
  await fetchSpecificLog(index)
  await fetchLogsDetails()
  
  if (!logdetails.value['Category'].includes(category.value)) {
    customCategory.value = category.value
    category.value = 'custom'
  }
  if (!logdetails.value['Sub Category'].includes(subcategory.value)) {
    customSubcategory.value = subcategory.value
    subcategory.value = 'custom'
  }
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
  text-align: center;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

/* Button Styles */
.cancel-button {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
  background-color: #6b7280;
  color: white;
  border: none;
  margin-right: 8px;
}

.cancel-button:hover:not(:disabled) {
  background-color: #4b5563;
}

.submit-button {
  padding: 12px 24px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.submit-button:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.submit-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
}

.form-input.input-error {
  border-color: #ef4444;
}

.error-text {
  color: #ef4444;
  font-size: 14px;
  margin-top: 4px;
}

/* Responsive Styles */
@media (max-width: 640px) {
  .modal-content {
    width: 95%;
    padding: 16px;
  }

  .modal-actions {
    flex-direction: column-reverse;
    gap: 8px;
  }

  .modal-actions button {
    width: 100%;
  }
  
  .submit-button {
    width: 100%;
  }
}

/* Focus styles for better accessibility */
button:focus-visible,
input:focus-visible,
select:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.loader {
  border: 4px solid #f3f3f3;
  border-radius: 50%;
  border-top: 4px solid #3b82f6;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
