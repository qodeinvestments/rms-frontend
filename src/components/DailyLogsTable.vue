<template>
  <div class="min-h-screen bg-gray-50 p-8">
        <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loader"></div>
      <p>Loading Accounts...</p>
    </div>
    <div v-else class="container mx-auto">
      <!-- Create New Log Button -->
      <div class="mb-6">
        <a-button  @click="handleCreateNewLog">
          Create New Log
        </a-button>
      </div>

      <!-- Category Select (on its own line) -->
      <div class="mb-6">
        <a-select 
          v-model:value="selectedCategories"
          mode="multiple" 
          placeholder="Select Categories" 
          class="w-full"
          :options="categoryOptions"
        ></a-select>
      </div>

      <!-- Sub Category Select (on its own line) -->
      <div class="mb-6">
        <a-select 
          v-model:value="selectedSubCategories"
          mode="multiple" 
          placeholder="Select Sub Categories" 
          class="w-full"
          :options="subCategoryOptions"
        ></a-select>
      </div>

      <!-- Date Filters: Start and End Date Side by Side -->
      <div class="flex gap-4 mb-6">
        <!-- Start Date Filter -->
        <div class="w-1/2">
          <label class="block text-gray-700 font-semibold mb-2">Start Date</label>
          <input 
            type="date" 
            v-model="startDate" 
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
        </div>
        
        <!-- End Date Filter -->
        <div class="w-1/2">
          <label class="block text-gray-700 font-semibold mb-2">End Date</label>
          <input 
            type="date" 
            v-model="endDate" 
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
        </div>
      </div>

      <!-- Modern Table -->
      <div class="bg-white shadow-lg rounded-lg overflow-hidden">
        <table class="w-full">
          <thead class="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
            <tr>
              <th class="px-6 py-4 text-left font-semibold">Date</th>
              <th class="px-6 py-4 text-left font-semibold">Category</th>
              <th class="px-6 py-4 text-left font-semibold">Sub Category</th>
              <th class="px-6 py-4 text-left font-semibold">Created By</th>
              <th class="px-6 py-4 text-left font-semibold">Created Time</th>
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
              <td class="px-6 py-4">{{ log['SubCategory'] }}</td>
              <td class="px-6 py-4">{{ log['Created By'] }}</td>
              <td class="px-6 py-4">{{  log['Created Time']}}</td>
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
                  @click="openDeleteModal(log)"
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
import { ref, computed, onMounted } from 'vue'
import { Select, Button, message } from 'ant-design-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive State
const logs = ref([])
const selectedCategories = ref([])
const selectedSubCategories = ref([])
const error = ref(null)
const loading = ref(false)

// New Date Filter State
const startDate = ref('')
const endDate = ref('')

// TOTP Modal State
const showTotpModal = ref(false)
const totpCode = ref('')
const totpError = ref('')
const logToDelete = ref(null)

// Computed Properties
const categoryOptions = computed(() => {
  const uniqueCategories = [...new Set(logs.value.map(log => log.Category))]
  return uniqueCategories.map(category => ({
    label: category,
    value: category
  }))
})

const subCategoryOptions = computed(() => {
  const uniqueSubCategories = [
    ...new Set(logs.value.map(log => log['SubCategory']))
  ]
  return uniqueSubCategories.map(subCat => ({
    label: subCat,
    value: subCat
  }))
})

const filteredLogs = computed(() => {
  let result = logs.value

  // Filter by selected categories
  if (selectedCategories.value.length > 0) {
    result = result.filter(log =>
      selectedCategories.value.includes(log.Category)
    )
  }

  // Filter by selected sub categories
  if (selectedSubCategories.value.length > 0) {
    result = result.filter(log =>
      selectedSubCategories.value.includes(log['SubCategory'])
    )
  }

  // Filter by start date if provided
  if (startDate.value) {
    const start = new Date(startDate.value)
    result = result.filter(log => new Date(log.Date) >= start)
  }

  // Filter by end date if provided
  if (endDate.value) {
    const end = new Date(endDate.value)
    // Set end to the end of the day to be inclusive
    end.setHours(23, 59, 59, 999)
    result = result.filter(log => new Date(log.Date) <= end)
  }

  return result
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

function openDeleteModal(log) {
  logToDelete.value = log
  showTotpModal.value = true
  totpCode.value = ''
  totpError.value = ''
}

async function confirmDelete() {
  try {
    if (!totpCode.value) {
      totpError.value = 'Password is required'
      return
    }

    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('User not authenticated')

    const response = await fetch('https://production2.swancapital.in/deletelog', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        index: logToDelete.value.id,
        totp_code: totpCode.value
      }),
    })

    if (!response.ok) {
      if (response.status === 401) {
        totpError.value = 'Invalid Password. Please try again.'
        return
      }
      const errorMessage = await response.text()
      throw new Error(`Error deleting log: ${errorMessage}`)
    }

    // Remove the deleted log from the list
    logs.value = logs.value.filter(item => item.id !== logToDelete.value.id)
    
    // Close modal and show success message
    showTotpModal.value = false
    message.success('Log deleted successfully')
  } catch (err) {
    if (!totpError.value) {
      message.error(`Failed to delete log: ${err.message}`)
    }
    console.error('Delete error:', err)
  }
}

// Handle form submission with TOTP code
async function handleSubmitWithTotp() {
  try {
    if (!totpCode.value) {
      totpError.value = 'Password is required'
      return
    }
    loading.value=true
    await confirmDelete()
    loading.value=false
    
    // Close modal on success
    showTotpModal.value = false
  } catch (err) {
    if (!totpError.value) {
      totpError.value = err.message || 'An error occurred'
    }
    console.error('Update with TOTP error:', err)
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
  loading.value = true
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
  loading.value = false
}

const fetchLogs = () => fetchData('getdailylogs', logs)

// Lifecycle Hook
onMounted(fetchLogs)
</script>

<style scoped>


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

/* Responsive adjustments */
@media (max-width: 640px) {
  .search-container {
    flex-direction: column;
    gap: 8px;
  }

  .submit-button {
    width: 100%;
  }
}

.cancel-button {
  background-color: #6b7280;
  color: white;
  border: none;
  margin-right: 8px;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.cancel-button:hover:not(:disabled) {
  background-color: #4b5563;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  transition: opacity 0.2s ease;
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
  transition: transform 0.2s ease;
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
}

.form-group input, .form-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  color: #1f2937;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
}

.form-group input:focus, .form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled, .form-select:disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}

.input-error {
  border-color: #ef4444 !important;
}

/* Select Styles */
.form-select {
  min-height: 38px;
  padding: 8px;
}

.form-select option {
  padding: 8px;
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
}

/* Transitions */
.modal-overlay {
  transition: opacity 0.2s ease;
}

.modal-content {
  transition: transform 0.2s ease;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .loader {
    animation: none;
  }
  
  .modal-overlay,
  .modal-content {
    transition: none;
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
