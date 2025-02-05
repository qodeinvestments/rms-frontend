<template>
  <!-- Keeping existing HTML structure -->
  <div class="data-fetch-container bg-gray-50">
    
    <!-- Add TOTP Modal -->
    <!-- TOTP Verification Modal -->
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
            @click="cancelTotpModal" 
            class="cancel-button2"
          >
            Cancel
          </button>
          <button 
            @click="handleTotpSubmit" 
            class="submit-button"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
    <div class="header">
      <h1 class="account-heading">Account: {{ account }}</h1>
      <div class="portfolio-section">
        <div class="portfolio-label">Portfolio Value:</div>
        <div class="portfolio-input-group">
          <span class="currency-symbol">₹</span>
          <input 
            type="number" 
            v-model="portfolioValue" 
            class="portfolio-input"
            @input="validatePortfolioValue"
            :class="{ 'error-input': portfolioError }"
          />
          <button 
            @click="showTotpModalWithAction('portfolio')" 
            class="update-button"
            :disabled="portfolioError || isUpdatingPortfolio"
          >
            <i v-if="!isUpdatingPortfolio" class="ph-bold ph-check"></i>
            <i v-else class="ph-bold ph-spinner animate-spin"></i>
          </button>
        </div>
        <span v-if="portfolioError" class="error-text text-sm text-red-500 mt-1">
          {{ portfolioError }}
        </span>
      </div>
    </div>

    <!-- Existing template structure remains the same -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading data...</p>
    </div>



    <!-- Main Data Table -->
    <div v-if="filteredData && filteredData.length > 0 && !loading && !error" class="content-wrapper">
      <!-- Existing content structure -->
      <div class="stats-selector">
        <label for="stat-option" class="stat-label">Choose a Statistic:</label>
        <select v-model="selectedStat" id="stat-option" class="stat-dropdown">
          <option value="sum">Sum</option>
          <option value="avg">Average</option>
          <option value="max">Maximum</option>
          <option value="min">Minimum</option>
        </select>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Strategy</th>
              <th>Qty Limit ({{ computeStat('qtylimit') }})</th>
              <th>CV Limit ({{ computeStat('cvlimit') }})</th>
              <th>Factor 1 ({{ computeStat('factor1') }})</th>
              <th>Factor 2 ({{ computeStat('factor2') }})</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in filteredData" :key="index">
              <td class="strategy-cell">{{ row.strategy }}</td>
              <td>
                <input 
                  type="number" 
                  v-model="row.qtylimit" 
                  class="editable-input"
                  @input="validateField(row, 'qtylimit')"
                  :class="{ 'error-input': row.errors?.qtylimit }"
                />
                <span v-if="row.errors?.qtylimit" class="error-text text-sm text-red-500 mt-1">
                  {{ row.errors.qtylimit }}
                </span>
              </td>
              <td>
                <input 
                  type="number" 
                  v-model="row.cvlimit" 
                  class="editable-input"
                  @input="validateField(row, 'cvlimit')"
                  :class="{ 'error-input': row.errors?.cvlimit }"
                />
                <span v-if="row.errors?.cvlimit" class="error-text text-sm text-red-500 mt-1">
                  {{ row.errors.cvlimit }}
                </span>
              </td>
              <td>
                <input 
                  type="number" 
                  v-model="row.factor1" 
                  class="editable-input"
                  @input="validateField(row, 'factor1')"
                  :class="{ 'error-input': row.errors?.factor1 }"
                />
                <span v-if="row.errors?.factor1" class="error-text text-sm text-red-500 mt-1">
                  {{ row.errors.factor1 }}
                </span>
              </td>
              <td>
                <input 
                  type="number" 
                  v-model="row.factor2" 
                  class="editable-input"
                  @input="validateField(row, 'factor2')"
                  :class="{ 'error-input': row.errors?.factor2 }"
                />
                <span v-if="row.errors?.factor2" class="error-text text-sm text-red-500 mt-1">
                  {{ row.errors.factor2 }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="action-buttons">
        <button 
            @click="showTotpModalWithAction('portfolio')" 
            class="save-button"
            :disabled="hasErrors || isSaving"
        >
          <span class="button-icon">{{ isSaving ? '⌛' : '💾' }}</span>
          {{ isSaving ? 'Saving...' : 'Save Changes' }}
        </button>
        <button @click="confirmCancel" class="cancel-button">
          <span class="button-icon">✖</span>
          Cancel
        </button>
      </div>
    </div>
        <!-- Client Multiplier Table -->
        <div v-if="!loading && !error" class="content-wrapper">
      <h2 class="text-xl font-semibold mb-4 text-gray-700">Client Multiplier Settings</h2>
        <!-- New Multi-Select Component -->
        <div class="select-container">
        <a-select
          v-model:value="selectedFeatures"
          mode="multiple"
          placeholder="Select Features"
          style="width: 100%"
          :options="featuresOptionsWithAll"
          :maxTagCount="3"
          @change="handleFeatureChange"
          :disabled="isUpdatingMultiplier"
        ></a-select>
  </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Strategy</th>
              <th>Multiplier Value</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(value, key) in client_multiplier" :key="key">
              <td class="strategy-cell">{{ key }}</td>
              <td>
                <input 
                  type="number" 
                  v-model="client_multiplier[key]" 
                  class="editable-input"
                  @input="validateMultiplier(key)"
                  :class="{ 'error-input': multiplierErrors[key] }"
                />
                <span v-if="multiplierErrors[key]" class="error-text text-sm text-red-500 mt-1">
                  {{ multiplierErrors[key] }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="action-buttons">
        <button 
          @click="showTotpModalWithAction('multiplier')" 
          class="save-button"
          :disabled="isUpdatingMultiplier"
        >
          <span class="button-icon">{{ isUpdatingMultiplier ? '⌛' : '💾' }}</span>
          {{ isUpdatingMultiplier ? 'Updating...' : 'Update Multiplier' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

// State management
const data = ref(null);
const filteredData = ref(null);
const account = ref(route.params.username);
const loading = ref(false);
const error = ref(null);
const selectedStat = ref("sum");
const portfolioValue = ref('');
const portfolioError = ref('');
const isSaving = ref(false);
const isUpdatingPortfolio = ref(false);
const hasUnsavedChanges = ref(false);
const live_clients = ref({});
const client_multiplier = ref({});
const modalAction = ref(''); 

// Client multiplier state
const multiplierErrors = ref({});
const isUpdatingMultiplier = ref(false);

// TOTP Modal state
const showTotpModal = ref(false);
const totpCode = ref('');
const totpError = ref('');

// New state for features selection
const selectedFeatures = ref([]);
const isAllSelected = ref(false);

// Modified computed property with null checks
const featuresOptionsWithAll = computed(() => {
  if (!data.value || !data.value.baskets) {
    return [];
  }
  
  return [
    { 
      label: isAllSelected.value ? 'Remove All' : 'All', 
      value: 'all' 
    },
    ...data.value.baskets.map(feature => ({
      label: feature,
      value: feature
    }))
  ];
});

// Modified handler with null checks
const handleFeatureChange = (value) => {
  if (!data.value || !data.value.baskets) return;
  if (value.includes('all')) {
    if (isAllSelected.value) {
      // Deselect all features
      selectedFeatures.value = [];
      isAllSelected.value = false;
      client_multiplier.value = {};  // Clear the client_multiplier
    } else {
      // Select all features
      selectedFeatures.value = data.value.baskets;
      isAllSelected.value = true;
      
      // Update client_multiplier with existing values or 0
      const updatedMultiplier = {};
      data.value.baskets.forEach(basket => {
        updatedMultiplier[basket] = client_multiplier.value[basket] || 0;
      });
      client_multiplier.value = updatedMultiplier;
    }
  } else {
    // Normal selection handling
    selectedFeatures.value = value.filter(feature => feature !== 'all');
    isAllSelected.value = selectedFeatures.value.length === data.value.baskets.length;

    // Update client_multiplier to only include selected features
    const updatedMultiplier = {};
    selectedFeatures.value.forEach(feature => {
      updatedMultiplier[feature] = client_multiplier.value[feature] || 0;
    });
    client_multiplier.value = updatedMultiplier;
  }
  hasUnsavedChanges.value = true;
};

const showTotpModalWithAction = (action) => {
  modalAction.value = action;
  showTotpModal.value = true;
  totpCode.value = '';
  totpError.value = '';
};

const cancelTotpModal = () => {
  showTotpModal.value = false;
  modalAction.value = '';
  totpCode.value = '';
  totpError.value = '';
};

const handleTotpSubmit = async () => {
  switch (modalAction.value) {
    case 'portfolio':
      await updatePortfolioValue();
      break;
    case 'multiplier':
      await updateMultiplier();
      break;
  }
};



const hasErrors = computed(() => {
  if (!filteredData.value) return false;
  return filteredData.value.some(row => row.errors && Object.keys(row.errors).length > 0);
});

// API calls with enhanced error handling
const fetchData = async (endpoint, stateRef) => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("Authentication required. Please log in again.");

    const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

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

// Data fetching with retry mechanism
const fetchMarginData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    await fetchData("MarginData", data);
    if (!data.value) throw new Error("Failed to fetch margin data");
    console.log("data is:",data.value)
    
    filteredData.value = data.value?.params?.[account.value] ?? [];
    portfolioValue.value = data.value["pf"][account.value];
    live_clients.value = data.value["live_clients"];
    
    
    // Find the key
    const matchingKey = Object.keys(live_clients.value).find(
      key => live_clients.value[key].user_id === account.value
    );
    
    // Initialize client_multiplier
    client_multiplier.value = live_clients.value[matchingKey]?.client_multiplier || {};
    
    // Initialize selected features based on existing client_multiplier
    if (data.value.baskets) {
      selectedFeatures.value = Object.keys(client_multiplier.value);
      isAllSelected.value = selectedFeatures.value.length === data.value.baskets.length;
    }
    
    hasUnsavedChanges.value = false;
  } catch (err) {
    error.value = err.message;
    console.error("Error fetching margin data:", err);
  } finally {
    loading.value = false;
  }
};

// Validation functions
const validatePortfolioValue = () => {
  const value = Number(portfolioValue.value);
  
  if (isNaN(value)) {
    portfolioError.value = 'Please enter a valid number';
    return false;
  }
  
  if (value < 0) {
    portfolioError.value = 'Value cannot be negative';
    return false;
  }
  portfolioError.value = ''; 
  hasUnsavedChanges.value = true;
  return true;
};
const validateMultiplier = (key) => {
  const value = Number(client_multiplier.value[key]);
  
  multiplierErrors.value[key] = '';
  
  if (isNaN(value) || value === '' ) {
    multiplierErrors.value[key] = 'Please enter a valid number';
    return false;
  }
  if (value < 0) {
    multiplierErrors.value[key] = 'Multiplier cannot be negative';
    return false;
  }
  hasUnsavedChanges.value = true;
  return true;
}

const validateField = (row, field) => {
  if (!row.errors) row.errors = {};
  const value = Number(row[field]);
  
  if (isNaN(value)) {
    row.errors[field] = 'Invalid number';
    return;
  }
  switch (field) {
    case 'qtylimit':
    case 'cvlimit' :
    case 'factor1':
    case 'factor2': 
      if (value < 0 ) {
        row.errors[field] = 'Must be Above 0';
      } else {
        delete row.errors[field];
      }
      break;
  }
  hasUnsavedChanges.value = true;
};


// Update functions
const updatePortfolioValue = async () => {
  if (!validatePortfolioValue()) return;

  const gg=Object.keys(data.value['params'][account.value][0])
  const filteredArr = filteredData.value.map(obj => 
        Object.fromEntries(
            Object.entries(obj).filter(([key]) => 
                gg.includes(key)
            )
        )
  );

  isUpdatingPortfolio.value = true;
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("Authentication required");

    const response = await fetch(`https://production2.swancapital.in/UpdatePortfolioValue`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        totp_code: totpCode.value,
        account: account.value, 
        portfolioValue: Number(portfolioValue.value),
        params: filteredArr
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'An error occurred');
    }

    alert("Portfolio value updated successfully!");
    showTotpModal.value = false;
    totpCode.value = '';

  } catch (err) {
    alert(`Error updating portfolio value: ${err.message}`);
    totpError.value = err.message;
    console.error("Error updating portfolio value:", err.message);
  } finally {
    isUpdatingPortfolio.value = false;
  }
};

const updateMultiplier = async () => {
  const ErrorMultiplier = Object.keys(client_multiplier.value).some(key => !validateMultiplier(key));
  if (ErrorMultiplier) return;
  
  isUpdatingMultiplier.value = true;
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("Authentication required");

    const response = await fetch(`https://production2.swancapital.in/UpdateClientMultiplier`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        account: account.value,
        client_multiplier: client_multiplier.value,
        totp_code: totpCode.value
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || data.message || 'An error occurred');
    }

    // Close modal and clear TOTP code
    showTotpModal.value = false;
    totpCode.value = '';

    alert("Client multiplier updated successfully!");
    hasUnsavedChanges.value = false;

    // Optionally refresh data
    await fetchMarginData();
  } catch (err) {
    alert(`Error updating client multiplier: ${err.message}`);
    console.error("Error updating client multiplier:", err.message);
  } finally {
    isUpdatingMultiplier.value = false;
  }
};

// Enhanced cancel functionality
const confirmCancel = () => {
  if (hasUnsavedChanges.value) {
    if (confirm("You have unsaved changes. Are you sure you want to cancel?")) {
      cancelChanges();
    }
  } else {
    cancelChanges();
  }
};

const cancelChanges = () => {

  router.push("/marginUpdate");
};



// Statistics computation
const computeStat = (field) => {
  if (!filteredData.value || filteredData.value.length === 0) return "-";

  const values = filteredData.value.map((row) => Number(row[field])).filter(val => !isNaN(val));
  if (values.length === 0) return "-";

  switch (selectedStat.value) {
    case "sum":
      return values.reduce((acc, val) => acc + val, 0).toFixed(2);
    case "avg":
      return (values.reduce((acc, val) => acc + val, 0) / values.length).toFixed(2);
    case "max":
      return Math.max(...values).toFixed(2);
    case "min":
      return Math.min(...values).toFixed(2);
    default:
      return "-";
  }
};

// Lifecycle hooks
onMounted(() => {
  fetchMarginData();
});
</script>
<style scoped>

/* Select Container Styles */
.select-container {
  margin-bottom: 1.5rem;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid rgba(229, 231, 235, 0.5);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.select-container :deep(.ant-select) {
  width: 100%;
}

.select-container :deep(.ant-select-selector) {
  border-radius: 6px !important;
  border: 1px solid #d1d5db !important;
  min-height: 38px !important;
}

.select-container :deep(.ant-select-selector:hover) {
  border-color: #3b82f6 !important;
}

.select-container :deep(.ant-select-focused .ant-select-selector) {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
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

.cancel-button2 {
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

.cancel-button2:hover:not(:disabled) {
  background-color: #4b5563;
}



.modal-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}
.error-text {
  color: #ef4444;
  font-size: 14px;
  margin-top: 4px;
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

/* Transitions */
.modal-overlay {
  transition: opacity 0.2s ease;
}

.modal-content {
  transition: transform 0.2s ease;
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

.data-fetch-container {
  min-height: 100vh;
  padding: 1.75rem;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: #f8fafc;
}

.header {
  position: relative;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(229, 231, 235, 0.5);
  border-radius: 14px;
  padding: 1.75rem;
  text-align: center;
  transition: all 0.15s ease;
}

.account-heading {
  font-size: 1.5rem;
  color: #475569;
  font-weight: 600;
  margin-bottom: 1.25rem;
}

.portfolio-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.portfolio-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.portfolio-input-group {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid rgba(229, 231, 235, 0.5);
  border-radius: 10px;
  padding: 0.5rem;
  transition: all 0.15s ease;
  gap: 0.5rem;
}

.portfolio-input-group:focus-within {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.currency-symbol {
  font-size: 1rem;
  color: #64748b;
  padding: 0 0.5rem;
}

.portfolio-input {
  width: 150px;
  border: none;
  outline: none;
  font-size: 1rem;
  color: #1e293b;
  font-weight: 500;
  padding: 0.375rem;
  background: transparent;
}

.update-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.update-button:hover {
  background: #e2e8f0;
  color: #2563eb;
}

.content-wrapper {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(229, 231, 235, 0.5);
  border-radius: 14px;
  padding: 1.75rem;
  margin-top: 1.75rem;
}

/* Table styles matching sidebar theme */
.table-container {
  border: 1px solid rgba(229, 231, 235, 0.5);
  border-radius: 10px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}

.editable-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid rgba(229, 231, 235, 0.5);
  border-radius: 8px;
  font-size: 0.875rem;
  color: #475569;
  transition: all 0.15s ease;
}

.editable-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

/* Action buttons matching sidebar theme */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.75rem;
  padding-top: 1.75rem;
  border-top: 1px solid rgba(229, 231, 235, 0.5);
}

.save-button,
.cancel-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid rgba(229, 231, 235, 0.5);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.save-button {
  background: #2563eb;
  color: white;
}

.save-button:hover {
  background: #1d4ed8;
}

.cancel-button {
  background: #ef4444;
  color: white;
}

.cancel-button:hover {
  background: #dc2626;
}

/* Stats dropdown matching sidebar theme */
.stat-dropdown {
  padding: 0.75rem 1.25rem;
  border: 1px solid rgba(229, 231, 235, 0.5);
  border-radius: 10px;
  background: white;
  color: #475569;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.stat-dropdown:hover {
  border-color: #2563eb;
}

.stat-label {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .data-fetch-container {
    padding: 1rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .portfolio-input-group {
    width: 100%;
    max-width: 300px;
  }

  .modal-content {
    width: 95%;
    padding: 16px;
  }
  .select-container {
    padding: 0.75rem;
  }

  .data-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }

  .editable-input {
    min-width: 100px;
  }
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error States */
.error-input {
  border-color: #ef4444 !important;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner,
  .modal-overlay,
  .modal-content {
    animation: none;
    transition: none;
  }
}

/* Print Styles */
@media print {
  .data-fetch-container {
    background: white;
    padding: 0;
  }

  .action-buttons,
  .update-button,
  .portfolio-input-group button {
    display: none;
  }

  .content-wrapper {
    box-shadow: none;
    border: none;
    padding: 0;
  }

  .table-container {
    border: none;
  }

  .data-table th,
  .data-table td {
    border: 1px solid #e5e7eb;
  }
}
</style>