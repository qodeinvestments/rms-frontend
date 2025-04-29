<template>
  <div class="admin-container">

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
            class="cancel-button"
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
            <td>{{ user.account_access.join(', ') }}</td>
            <td>{{ user.features.join(', ') }}</td>
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
              <i class="fas fa-trash-alt"
                 @click="showTotpModalWithAction('deleteid',user)" 
                 title="Delete User"
                 style="cursor: pointer;"
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
            <input v-model="editingUser.username" type="text" disabled />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input v-model="editingUser.password" type="text" :disabled="updateLoading" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="editingUser.email" type="email" :disabled="updateLoading" />
          </div>
          <div class="form-group">
            <label>Role</label>
            <select v-model="editingUser.role" :disabled="updateLoading" class="form-select">
              <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
            </select>
          </div>
          <div class="form-group" v-if="editingUser.role !== 'Admin'">
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
            />
          </div>

          <!-- Account Percentages Section -->
          <div v-if="editingUser.role === 'Client'" class="percentage-section">
            <label>Account Percentages</label>

            <!-- Search box -->
            <input
              v-model="percentageSearch"
              type="text"
              placeholder="Search accounts..."
              class="percentage-search"
              :disabled="updateLoading"
            />

            <!-- Scrollable list -->
            <div class="percentage-list">
              <div
                v-for="item in filteredAccountPercentages"
                :key="item.name"
                class="percentage-item"
              >
                <span class="percentage-label">{{ item.name }}</span>
                <div class="percentage-inner-list">
                    <input
                      v-model.number="item.percentage"
                      type="number"
                      min="0"
                      max="100"
                      class="percentage-input"
                      :disabled="updateLoading"
                    />
                    <input
                      v-model="item.startDate"
                      type="date"
                      class="date-input"
                      :disabled="updateLoading"
                    />
                    <input
                      v-model="item.endDate"
                      type="date"
                      class="date-input"
                      :disabled="updateLoading"
                    />
                    <button
                        type="button"
                        @click="removeAccountPercentage(item.name)"
                        class="remove-percentage-button"
                        :disabled="updateLoading"
                      >
                        Remove
                    </button>
                </div>
               
               
              </div>
            </div>
          </div>

          <div class="form-group" v-if="editingUser.role !== 'Admin'">
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
            />
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="cancel-button" :disabled="updateLoading">
            Cancel
          </button>
          <button @click="saveChanges" class="save-button" :disabled="updateLoading">
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
const showTotpModal = ref(false);
const totpCode = ref("");
const totpError = ref("");
const modalAction = ref("");
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
const accountPercentages = ref([]);
const percentageSearch = ref('');
const selectedFeatures = ref([]);
const roles = ref([]);
const features = ref([]);
const isaccountAllSelected = ref(false);
const isfeatureAllSelected = ref(false);


// Show TOTP Modal with action
const showTotpModalWithAction = (action,data) => {
  modalAction.value = {"action":action,"data":data};
  showTotpModal.value = true;
  totpCode.value = "";
  totpError.value = "";
};

// Cancel TOTP Modal
const cancelTotpModal = () => { 
  showTotpModal.value = false;
  modalAction.value = "";
  totpCode.value = "";
  totpError.value = "";
};


// TOTP Submit Handler
const handleTotpSubmit = async () => {

  try {
  switch (modalAction.value['action']) {
    case "deleteid":
      await deleteUser(modalAction.value['data']);
      break;
    }
  } catch (error) {
    console.error("TOTP submission error:", error);
    totpError.value = "An unexpected error occurred. Please try again.";
  } finally {

  }
};


// Sync percentages & dates with selected accounts
function updateAccountPercentages() {
  accountPercentages.value = accountPercentages.value.filter(item =>
    selectedAccounts.value.includes(item.name)
  );
  // selectedAccounts.value.forEach(acc => {
  //   if (!accountPercentages.value.find(i => i.name === acc)) {
  //     accountPercentages.value.push({ name: acc, percentage: 100, startDate: '', endDate: '' });
  //   }
  // });
  accountPercentages.value=editingUser.value['account_percentages'] || [];
}

const accountOptionsWithAll = computed(() => [
  { label: isaccountAllSelected.value ? 'Remove All' : 'All', value: 'all' },
  ...accounts.value.map(a => ({ label: a, value: a }))
]);
const featuresOptionsWithAll = computed(() => [
  { label: isfeatureAllSelected.value ? 'Remove All' : 'All', value: 'all' },
  ...features.value.map(f => ({ label: f, value: f }))
]);

const handleAccountChange = value => {
  if (value.includes('all')) {
    if (isaccountAllSelected.value) {
      selectedAccounts.value = [];
      isaccountAllSelected.value = false;
    } else {
      selectedAccounts.value = [...accounts.value];
      isaccountAllSelected.value = true;
    }
  } else {
    selectedAccounts.value = value.filter(v => v !== 'all');
    isaccountAllSelected.value = selectedAccounts.value.length === accounts.value.length;
  }
  updateAccountPercentages();
};

function removeAccountPercentage(name) {
  selectedAccounts.value = selectedAccounts.value.filter(a => a !== name);
  updateAccountPercentages();
}

const handleFeatureChange = value => {
  if (value.includes('all')) {
    if (isfeatureAllSelected.value) {
      selectedFeatures.value = [];
      isfeatureAllSelected.value = false;
    } else {
      selectedFeatures.value = [...features.value];
      isfeatureAllSelected.value = true;
    }
  } else {
    selectedFeatures.value = value.filter(v => v !== 'all');
    isfeatureAllSelected.value = selectedFeatures.value.length === features.value.length;
  }
};

const filteredAccountPercentages = computed(() =>

  accountPercentages.value.filter(item => item.name.toLowerCase().includes(percentageSearch.value.toLowerCase()))
);

const openEditModal = user => {
  editingUser.value = { ...user };
  editingIndex.value = users.value.findIndex(u => u.email === user.email);
  selectedAccounts.value = [...(user.account_access || [])];
  updateAccountPercentages();
  selectedFeatures.value = [...(user.features || [])];
  updateError.value = null;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  editingUser.value = null;
  editingIndex.value = -1;
  selectedAccounts.value = [];
  updateError.value = null;
};

const fetchData = async (endpoint, stateRef) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');
    const res = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    stateRef.value = endpoint === 'getAccounts' ? Object.keys(data) : data || [];
  } catch (err) {
    console.error(`Error fetching ${endpoint}:`, err.message);
  }
};

const saveChanges = async () => {
  if (selectedAccounts.value.length === 0 && editingUser.value.role !== 'Admin') {
    alert('Accounts cannot be empty');
    return;
  }
  updateLoading.value = true;
  updateError.value = null;
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');
    const updatedUser = {
      ...editingUser.value,
      account_access: selectedAccounts.value,
      features: selectedFeatures.value,
      account_percentages: accountPercentages.value
    };
    const res = await fetch('https://production2.swancapital.in/editUser', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedUser)
    });
    if (!res.ok) throw new Error(await res.text());
    users.value[editingIndex.value] = updatedUser;
    closeModal();
    alert('User updated successfully!');
    window.location.reload();
  } catch (err) {
    updateError.value = `Error updating user: ${err.message}`;
    alert(updateError.value);
  } finally {
    updateLoading.value = false;
  }
};

const fetchUsers = () => fetchData('users', users);
const fetchAccounts = () => fetchData('getAccounts', accounts);
const fetchRoles = () => fetchData('getRoles', roles);
const fetchFeatures = () => fetchData('getFeatures', features);

const deleteUser = async user => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');
    const res = await fetch('https://production2.swancapital.in/deleteUser', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({"user":user,"totpCode":totpCode.value})
    });
    if (!res.ok) throw new Error(await res.text());
    alert(`User ${user.email} deleted successfully.`);
    window.location.reload();
  } catch (err) {
    alert(`Error deleting user: ${err.message}`);
    console.error(err);
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
.percentage-section {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 12px;
  margin: 16px 0;
  background-color: #fafafa;
}

/* Search input styling */
.percentage-search {
  width: 100%;
  padding: 8px 12px;
  margin-bottom: 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

/* Column layout with fixed height */
.percentage-list {
  max-height: 150px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-right: 4px;
}

.percentage-inner-list{
  display: flex;
  gap: 20px;
  padding-right: 4px;
}

/* Each row: full width */
.percentage-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background-color: #fff;
  
}

.percentage-label {
  flex: 3;
  font-weight: 500;
}

.percentage-input {
  flex: 2;
  min-width: 80px;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  text-align: right;
}

.remove-percentage-button {
  flex: 1;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
}
.remove-percentage-button:hover {
  background-color: #dc2626;
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
  max-width: 1200px;
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