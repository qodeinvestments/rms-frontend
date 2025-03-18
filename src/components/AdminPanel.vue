<template>
    <div class="admin-container">
      <h1 class="admin-title">User Management</h1>
  
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loader"></div>
        <p>Loading users...</p>
      </div>
  
      <!-- Error State -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="fetchUsers" class="retry-button">Retry</button>
      </div>
  
      <!-- Users Table -->
      <div v-if="!loading && !error" class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Password</th>
              <th>Email</th>
              <th>Role</th>
              <th>Account Access</th>
              <th>Features</th>
              <th>Actions</th>
              <th>Delete</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in users" :key="index">
              <td>{{ user.username }}</td>
              <td>{{ user.password }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.role }}</td>
              <td>{{ user['account_access'].join(', ') }}</td>
              <td>{{ user['features'].join(', ') }}</td>
              <td>
                <button 
                  @click="openEditModal(user)"
                  class="edit-button"
                  :disabled="updateLoading"
                >
                  {{ updateLoading && editingIndex === index ? 'Saving...' : 'Edit' }}
                </button>
              </td>
              <td class="icon-cell">
                <i 
                    class="icon ph-bold ph-trash" 
                    @click="deleteUser(user)"
                    style="cursor: pointer;" 
                    title="Delete User"
                ></i>
                </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- Edit Modal -->
      <div v-if="showModal" class="modal-overlay">
        <div class="modal-content">
          <h2 class="modal-title">Edit User</h2>
          
          <!-- Edit Form Error -->
          <div v-if="updateError" class="error-message">
            {{ updateError }}
          </div>
  
          <div class="form-container">
            <div class="form-group">
              <label>Username</label>
              <input 
                v-model="editingUser.username"
                type="text"
                disabled
              >
            </div>
            <div class="form-group">
              <label>Password</label>
              <input 
                v-model="editingUser.password"
                type="text"
                :disabled="updateLoading"
              >
            </div>
            
  
            <div class="form-group">
              <label>Email</label>
              <input 
                v-model="editingUser.email"
                type="email"
                :disabled="updateLoading"
              >
            </div>
            <div class="form-group">
                <label>Role</label>
                <select 
                    v-model="editingUser.role" 
                    :disabled="updateLoading" 
                    class="form-select"
                >
                    <option v-for="role in roles" :key="role" :value="role">
                    {{ role }}
                    </option>
                </select>
            </div>
            <div class="form-group" v-if="editingUser.role != 'Admin'">
                <label>Account Access</label>
                <a-select
                    v-model:value="selectedAccounts"
                    mode="multiple"
                    placeholder="Select Accounts"
                    style="width: 100%"
                    :options="accountOptionsWithAll"
                    :maxTagCount="3"
                    @change="handleAccountChange"
                    :disabled="updateLoading" 
                ></a-select>
            </div>
            <div class="form-group" v-if="editingUser.role != 'Admin'">
                <label>Features</label>
                <a-select
                    v-model:value="selectedFeatures"
                    mode="multiple"
                    placeholder="Select Features"
                    style="width: 100%"
                    :options="featuresOptionsWithAll"
                    :maxTagCount="3"
                    @change="handleFeatureChange"
                    :disabled="updateLoading" 
                ></a-select>
            </div>

          </div>
  
          <div class="modal-actions">
            <button 
              @click="closeModal"
              class="cancel-button"
              :disabled="updateLoading"
            >
              Cancel
            </button>
            <button 
              @click="saveChanges"
              class="save-button"
              :disabled="updateLoading"
            >
              {{ updateLoading ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
<script setup>
import { ref, computed, onMounted } from 'vue';

// State management
const users = ref([]);
const loading = ref(false);
const error = ref(null);
const showModal = ref(false);
const editingUser = ref(null);
const editingIndex = ref(-1);
const updateLoading = ref(false);
const updateError = ref(null);
const accounts = ref([]);
const selectedAccounts = ref([]);
const selectedFeatures = ref([]);
const roles = ref([])
const features = ref([])
// "All" Label State
const isaccountAllSelected = ref(false);
const isfeatureAllSelected = ref(false);

// Add "All" or "Remove All" option dynamically
const accountOptionsWithAll = computed(() => [
  { label: isaccountAllSelected.value ? 'Remove All' : 'All', value: 'all' },
  ...accounts.value.map(account => ({
    label: account,
    value: account,
  })),
]);


const featuresOptionsWithAll = computed(() => [
  { label: isfeatureAllSelected.value ? 'Remove All' : 'All', value: 'all' },
  ...features.value.map(account => ({
    label: account,
    value: account,
  })),
]);

// Handle selection change
const handleAccountChange = (value) => {
  if (value.includes('all')) {
    if (isaccountAllSelected.value) {
      // Deselect all accounts
      selectedAccounts.value = [];
      isaccountAllSelected.value = false;
    } else {
      // Select all accounts
      selectedAccounts.value = accounts.value;
      isaccountAllSelected.value = true;
    }
  } else {
    // Normal selection handling
    selectedAccounts.value = value.filter(account => account !== 'all');
    isaccountAllSelected.value = selectedAccounts.value.length === accounts.value.length;
  }
};


const handleFeatureChange = (value) => {
  if (value.includes('all')) {
    if (isfeatureAllSelected.value) {
      // Deselect all accounts
      selectedFeatures.value = [];
      isfeatureAllSelected.value = false;
    } else {
      // Select all accounts
      selectedFeatures.value = features.value;
      isfeatureAllSelected.value = true;
    }
  } else {
    // Normal selection handling
    selectedFeatures.value = value.filter(account => account !== 'all');
    isfeatureAllSelected.value = selectedFeatures.value.length === features.value.length;

  }
};



const openEditModal = (user) => {
  editingUser.value = { ...user };
  editingIndex.value = users.value.findIndex(u => u.email === user.email);
  updateError.value = null;
  showModal.value = true;
  selectedAccounts.value = user['account_access'] || []; // Pre-fill selected accounts in modal
  selectedFeatures.value= user['features'] || []; // Pre-fill selected features in modal
};

// Close modal
const closeModal = () => {
  showModal.value = false;
  editingUser.value = null;
  editingIndex.value = -1;
  updateError.value = null;
  selectedAccounts.value = [];
};



const fetchData = async (endpoint, stateRef) => {
  try {
    const access_token = localStorage.getItem('access_token');
    if (!access_token) throw new Error('User not authenticated');
    const token = access_token;

    const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`, // Include the Bearer token
        'Content-Type': 'application/json',
      },
    });
    if (response.ok) {
      const data = await response.json();
      stateRef.value = endpoint === 'getAccounts' ? Object.keys(data) : (data || []);
    } else {
      const errorMessage = await response.text();
      console.error("API Error:", errorMessage);
      throw new Error(`Error fetching ${endpoint}: ${errorMessage}`);
    }
  } catch (err) {
    console.error(`Error fetching ${endpoint}:`, err.message);
  }
};


// Save Changes
const saveChanges = async () => {
  if (selectedAccounts.value.length === 0 && editingUser.value.role != 'Admin') {
    alert("Accounts cannot be empty");
    return;
  }

  updateLoading.value = true;
  updateError.value = null;

  try {
    // Retrieve the access token from localStorage
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    // Prepare data for API
    const updatedUser = {
      ...editingUser.value,
      'account_access': selectedAccounts.value,
      'features': selectedFeatures.value, // Add this line
    };

    const response = await fetch('https://production2.swancapital.in/editUser', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Include the Bearer token
      },
      body: JSON.stringify(updatedUser),
    });

    if (response.ok) {
      users.value[editingIndex.value] = { ...updatedUser }; // Update local table
      closeModal();
      alert('User updated successfully!');
      window.location.reload(); // Refresh the page on success
    } else {
      const errorMessage = await response.text(); // Get detailed error message
      updateError.value = `Error updating user: ${errorMessage}`;
      alert(updateError.value); // Optional: Alert the error message
    }
  } catch (error) {
    updateError.value = `An error occurred: ${error.message}`;
    alert(updateError.value); // Optional: Alert the error message
  } finally {
    updateLoading.value = false;
  }
};


// Usage:
const fetchUsers = () => fetchData('users', users);
const fetchAccounts = () => fetchData('getAccounts', accounts);
const fetchRoles = () => fetchData('getRoles', roles);
const fetchFeatures= () => fetchData('getFeatures', features);



const deleteUser = async (user) => {
  try {
    // Retrieve the access token from localStorage
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    const response = await fetch('https://production2.swancapital.in/deleteUser', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Include the Bearer token
      },
      body: JSON.stringify(user), // Serialize the user object
    });

    if (response.ok) {
      console.log(`User ${user.email} deleted successfully.`);
      alert(`User ${user.email} deleted successfully.`);
      location.reload(); // Reload the page on success
    } else {
      const errorMessage = await response.text(); // Get the detailed error message
      alert(`Error deleting user: ${errorMessage}`);
      console.error('Error deleting user:', response.statusText);
    }
  } catch (error) {
    alert("Error deleting user. Please try again.");
    console.error('Error deleting user:', error.message);
  }
};


onMounted(async () => {
  await fetchUsers();
  await fetchAccounts();
  await fetchRoles();
  await fetchFeatures();
});
</script>

  
<style scoped>
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
  overflow-x: auto; /* Enable horizontal scroll for small screens */
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: auto; /* Ensures columns resize dynamically */
  min-width: 1000px; /* Prevents layout breaking for smaller content */
}

.admin-table th {
  background-color: #f3f4f6;
  padding: 12px 16px;
  text-align: center;
  font-weight: 600;
  color: #4b5563;
  border-bottom: 2px solid #e5e7eb;
  white-space: nowrap; /* Prevent header text wrapping */
}

.admin-table td {
  padding: 12px 16px;
  color: #1f2937;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle; /* Centers content vertically */
  text-align: center; /* Centers text in all columns */
  word-wrap: break-word; /* Allows wrapping of long text */
  word-break: break-word;
  max-width: 200px; /* Adjust as needed for text overflow */
}

.admin-table tr:hover {
  background-color: #f9fafb;
}

/* Features Column Styling */
.admin-table td.features-column {
  max-width: 300px; /* Limit the column width */
  text-align: left; /* Align text to the left */
  overflow: hidden;
  text-overflow: ellipsis; /* Adds ellipsis for overflow */
  white-space: nowrap; /* Prevent wrapping */
}

/* Button Styles */
.edit-button, .save-button, .cancel-button {
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  padding: 8px 16px;
  transition: background-color 0.2s;
}

.edit-button {
  background-color: #3b82f6;
}

.edit-button:hover {
  background-color: #2563eb;
}

.save-button {
  background-color: #10b981;
}

.save-button:hover {
  background-color: #059669;
}

.cancel-button {
  background-color: #6b7280;
  margin-right: 8px;
}

.cancel-button:hover {
  background-color: #4b5563;
}

.icon-cell {
  text-align: center;
  vertical-align: middle;
}

.icon {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;
  cursor: pointer;
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
  width: 100%;
  max-width: 600px;
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

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

/* Loading State */
.loading-state {
  text-align: center;
  padding: 40px;
  color: #666;
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