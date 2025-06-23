<template>
  <div class="market-holiday-container">
    <h1 class="text-2xl font-bold mb-6">Market Holidays</h1>
    
    <!-- Error Message -->
    <div v-if="error" class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
      {{ error }}
    </div>
    
    <!-- Add Holiday Form -->
    <div class="mb-8 p-4 bg-white rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-4">Add New Holiday</h2>
      <form @submit.prevent="handleSubmit" class="flex gap-4">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
          <input 
            type="date" 
            v-model="newHoliday.date"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Holiday Name</label>
          <input 
            type="text" 
            v-model="newHoliday.dayName"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter holiday name"
            required
          />
        </div>
        <div class="flex items-end">
          <button 
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Adding...' : 'Add Holiday' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h2 class="modal-title">Confirm Delete</h2>
        <div class="warning-banner">
          <i class="fas fa-exclamation-triangle warning-icon"></i>
          <p class="warning-text">Are you sure you want to delete the holiday on {{ formatDate(holidayToDelete?.date) }}?</p>
        </div>
        <div class="modal-actions">
          <button
            @click="cancelDelete"
            class="cancel-button"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            class="submit-button"
            :disabled="isDeleting"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Simple Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Holiday Name</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="holiday in holidays" :key="holiday.date" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              {{ formatDate(holiday.date) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              {{ holiday['day name'] }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right">
              <button
                @click="handleDeleteClick(holiday)"
                class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                Delete
              </button>
            </td>
          </tr>
          <tr v-if="holidays.length === 0">
            <td colspan="3" class="px-6 py-4 text-center text-gray-500">
              No holidays found
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL, WS_BASE_URL } from '../config/url'
const router = useRouter()
const holidays = ref([])
const error = ref('')
const isSubmitting = ref(false)
const isDeleting = ref(false)
const showDeleteModal = ref(false)
const holidayToDelete = ref(null)
const newHoliday = ref({
  date: '',
  dayName: ''
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// API methods
const fetchData = async (endpoint, stateRef) => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("Authentication required. Please log in again.");

    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (response.status === 401) {
      localStorage.removeItem("access_token");
      router.push("/login");
      throw new Error("Session expired. Please log in again.");
    }

    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error: ${errorMessage}`);
    }

    const jsonData = await response.json();
    stateRef.value = jsonData;
  } catch (err) {
    error.value = err.message;
    console.error(`Error fetching ${endpoint}:`, err.message);
    throw err;
  }
};

const postData = async (endpoint, data) => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("Authentication required. Please log in again.");

    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
      }
    );

    if (response.status === 401) {
      localStorage.removeItem("access_token");
      router.push("/login");
      throw new Error("Session expired. Please log in again.");
    }

    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error: ${errorMessage}`);
    }

    return await response.json();
  } catch (err) {
    error.value = err.message;
    console.error(`Error posting to ${endpoint}:`, err.message);
    throw err;
  }
};

const fetchHolidays = async () => {
  try {
    error.value = '' // Clear any previous errors
    await fetchData('market-holidays', holidays)
    // Sort holidays by date in ascending order
    holidays.value.sort((a, b) => new Date(a.date) - new Date(b.date))
  } catch (err) {
    console.error('Failed to fetch holidays:', err)
  }
}

const handleSubmit = async () => {
  try {
    isSubmitting.value = true
    error.value = '' // Clear any previous errors
    
    await postData('handle_market-holidays', {
      type: 'add',
      date: newHoliday.value.date,
      dayname: newHoliday.value.dayName
    })
    
    // Reset form
    newHoliday.value = {
      date: '',
      dayName: ''
    }
    
    // Refresh table
    await fetchHolidays()
  } catch (err) {
    console.error('Failed to add holiday:', err)
  } finally {
    isSubmitting.value = false
  }
}

const handleDeleteClick = (holiday) => {
  holidayToDelete.value = holiday
  showDeleteModal.value = true
}

const cancelDelete = () => {
  showDeleteModal.value = false
  holidayToDelete.value = null
}

const confirmDelete = async () => {
  if (!holidayToDelete.value) return

  try {
    isDeleting.value = true
    error.value = '' // Clear any previous errors
    
    await postData('handle_market-holidays', {
      type: 'delete',
      date: holidayToDelete.value.date
    })
    
    // Refresh table
    await fetchHolidays()
    
    // Close modal
    showDeleteModal.value = false
    holidayToDelete.value = null
  } catch (err) {
    console.error('Failed to delete holiday:', err)
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
  fetchHolidays()
})
</script>

<style scoped>
.market-holiday-container {
  padding: 1rem;
  margin-left: 280px; /* Increased margin to ensure no overlap with sidebar */
  min-height: 100vh;
  width: calc(100% - 280px); /* Adjust width to account for margin */
}

/* Add responsive margin for mobile */
@media (max-width: 768px) {
  .market-holiday-container {
    margin-left: 0;
    width: 100%;
  }
}

.fixed {
  position: fixed;
  z-index: 50;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background-color: #f9fafb;
  font-weight: 600;
}

td, th {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

tr:hover {
  background-color: #f9fafb;
}

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
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: white;
  padding: 32px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 24px;
  text-align: center;
}

.warning-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.warning-icon {
  color: #ef4444;
  font-size: 20px;
}

.warning-text {
  color: #991b1b;
  font-size: 14px;
  margin: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-button {
  padding: 12px 24px;
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button:hover:not(:disabled) {
  background-color: #e5e7eb;
  color: #1f2937;
}

.submit-button {
  padding: 12px 24px;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-button:hover:not(:disabled) {
  background-color: #dc2626;
  transform: translateY(-1px);
}

.submit-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .modal-content {
    padding: 24px;
    width: 95%;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style> 