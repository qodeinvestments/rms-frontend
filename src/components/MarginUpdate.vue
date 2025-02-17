<template>
  <div class="admin-container">
    <h1 class="admin-title">Margin Update</h1>

    <!-- Actions Section -->
    <div class="actions-section">
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search accounts..." 
          class="search-input"
        />
      </div>

      <div class="submit-container">
      <button 
        @click="gotoMarginSettings()" 
        class="margin-button"
      >
        Margin Settings
      </button>
      <button 
        @click="showTotpModal = true" 
        class="submit-button"
      >
        Submit
      </button>
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

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loader"></div>
      <p>Loading Accounts...</p>
    </div>
    <!-- Error State -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="fetchAccounts" class="retry-button">Retry</button>
    </div>
    <!-- Users Table -->
    <div v-if="!loading && !error" class="table-container">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Account</th>
            <th>Portfolio Value</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(account, index) in filteredAccounts" :key="index">
            <td>{{index}}</td>
            <td>{{ marginData['pf'][account.user_id] }}</td>
            <td>
              <button 
                @click="openEditModal(account.user_id)"
                class="edit-button"
                :disabled="updateLoading"
              >
                {{ updateLoading && editingIndex === index ? 'Saving...' : 'Edit' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
// State management
const swan_baskets = ref([]);
const loading = ref(false);
const error = ref(null);
const editingIndex = ref(-1);
const updateLoading = ref(false);
const updateError = ref(null);
const accounts = ref([]);
const marginData = ref([]);
const searchQuery = ref('');
const showTotpModal = ref(false);
const totpCode = ref('');
const totpError = ref('');

// Computed property for filtered accounts
const filteredAccounts = computed(() => {
  if (!searchQuery.value) return accounts.value; // Return the original object if no query

  // Filter keys and rebuild the object
  return Object.keys(accounts.value)
    .filter(key => key.toLowerCase().includes(searchQuery.value.toLowerCase()))
    .reduce((filtered, key) => {
      filtered[key] = accounts.value[key];
      return filtered;
    }, {});
});


const gotoMarginSettings = () =>{
  router.push("/marginSettings");
}



import * as XLSX from 'xlsx';

const handleSubmitWithTotp = async () => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('User not authenticated');
    }

    const response = await fetch('https://production2.swancapital.in/UpdateMarginForAllAccounts', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        totp_code: totpCode.value
      })
    });

    const jsonResponse = await response.json();

    if (!response.ok) {
        if (response.status === 401) {
            totpError.value = 'Invalid Password. Please try again.';
            return;
        }
        throw new Error(jsonResponse.detail || jsonResponse.message || 'An error occurred');
    }

    // Download Excel file
    const download = (data, title) => {
      try {
          if (!data || !Array.isArray(data.data)) {
              throw new Error('Invalid data format received');
          }
          
          const currentDate = new Date();
          const formattedDate = currentDate.toLocaleString('en-US', {
              year: 'numeric',
              month: '2-digit', 
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
          }).replace(/[/:]/g, '_');

          const file_name = `margin_update_${formattedDate}.xlsx`;
          
          const wb = XLSX.utils.book_new();
          const ws = XLSX.utils.json_to_sheet(data.data);
          XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
          XLSX.writeFile(wb, file_name);
      } catch (error) {
          console.error('Download error:', error);
          throw error;
      }
    };

    // Trigger download with error handling
    if (jsonResponse.dataframe) {
        download(jsonResponse.dataframe, "margin_update");
        showTotpModal.value = false;
        totpCode.value = '';
        alert("All Accounts Margins Updated Successfully!");
    } else {
        throw new Error('No data received from server');
    }
  } catch (error) {
    if (!totpError.value) {
      alert(`Error: ${error.message}`);
    }
    console.error('Error updating margin:', error.message);
    throw error;
  }
};

// API functions
const fetchData = async (endpoint, stateRef) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error fetching ${endpoint}: ${errorMessage}`);
    }

    const data = await response.json();
    stateRef.value = (data || []);
  } catch (err) {
    error.value = err.message;
    console.error(`Error fetching ${endpoint}:`, err.message);
  }
};

const router = useRouter();

const openEditModal = (account) => {
  console.log(account);
  router.push("/marginupdate/" + account);
};

const fetchAccounts = () => fetchData('getPositionSizingClients', accounts);
const fetchBasket = () => fetchData('getBasket', swan_baskets);
const fetchMarginData = () => fetchData("MarginData", marginData);

// Initialize
onMounted(async () => {
  loading.value = true;
  try {
    await Promise.all([fetchBasket(), fetchAccounts(), fetchMarginData()]);
  } finally {
    loading.value = false;
  }
});
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



.actions-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.search-container {
  flex: 0 1 300px; /* Allow shrinking but limit initial width */
}



.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
}

.search-input::placeholder {
  color: #9ca3af;
}

.submit-container {
  display: flex;
  gap: 16px; /* Adds spacing between buttons */
  justify-content: flex-start;
  align-items: center;
}

.margin-button {
  padding: 12px 24px;
  background-color: #10B981; /* Green color */
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.margin-button:hover:not(:disabled) {
  background-color: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
}

.margin-button:active:not(:disabled) {
  transform: translateY(0);
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

  .search-input,
  .submit-button {
    width: 100%;
  }
}
.admin-container {
  padding: 24px;
}

.admin-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 24px;
  text-align: center;
}

/* Table Styles */
.table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: auto;
  min-width: 600px;
}

.admin-table th {
  background-color: #f3f4f6;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #4b5563;
  border-bottom: 2px solid #e5e7eb;
}

.admin-table td {
  padding: 12px 16px;
  color: #1f2937;
  border-bottom: 1px solid #e5e7eb;
}

.admin-table tr:hover {
  background-color: #f9fafb;
}

/* Button Styles */
.edit-button, .save-button, .cancel-button {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.edit-button {
  background-color: #3b82f6;
  color: white;
  border: none;
}

.edit-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.save-button {
  background-color: #10b981;
  color: white;
  border: none;
}

.save-button:hover:not(:disabled) {
  background-color: #059669;
}

.cancel-button {
  background-color: #6b7280;
  color: white;
  border: none;
  margin-right: 8px;
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
#basket-search {
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
  margin-bottom: 12px;
}

#basket-search:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}


/* Form Styles */
.form-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

/* Error Message */
.error-message {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #dc2626;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.retry-button {
  background-color: #dc2626;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  margin-left: 10px;
  cursor: pointer;
}

.retry-button:hover {
  background-color: #b91c1c;
}

/* Basket Section */
.basket-section {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  background-color: #f9fafb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.basket-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
  text-align: center;
  border-bottom: 1px solid #d1d5db;
  padding-bottom: 8px;
}

.basket-input-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
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
  .admin-container {
    padding: 16px;
  }

  .modal-content {
    width: 95%;
    padding: 16px;
  }

  .basket-input-group {
    grid-template-columns: 1fr;
  }

  .admin-table {
    min-width: 100%;
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

</style>