<template>
  <div class="admin-container">
    <h1 class="admin-title">Position Management</h1>

    <!-- Actions Section -->
    <div class="actions-section">
      <div class="search-container">
        <i class="fas fa-search search-icon"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search users..." 
          class="search-input"
        />
      </div>
    </div>

    <!-- Password Verification Modal -->
    <div v-if="showPasswordModal" class="modal-overlay">
      <div class="modal-content">
        <h2 class="modal-title">{{ modalType === 'position' ? 'Square Off Positions' : 'Square Off Broker Positions' }}</h2>
        <div class="warning-banner">
          <i class="fas fa-exclamation-triangle warning-icon"></i>
          <p class="warning-text">Warning: This action will square off all {{ modalType === 'position' ? 'positions' : 'broker positions' }} for the selected user.</p>
        </div>
        <div class="form-group">
          <label>First Password</label>
          <input 
            type="password" 
            v-model="firstPassword"
            placeholder="Enter first password"
            class="form-input"
            :class="{ 'input-error': passwordError }"
            @input="passwordError = ''"
          />
        </div>
        <div class="form-group">
          <label>Second Password</label>
          <input 
            type="password" 
            v-model="secondPassword"
            placeholder="Enter second password"
            class="form-input"
            :class="{ 'input-error': passwordError }"
            @input="passwordError = ''"
          />
        </div>
        <span v-if="passwordError" class="error-text">{{ passwordError }}</span>
        <div class="modal-actions">
          <button 
            @click="closePasswordModal" 
            class="cancel-button"
          >
            Cancel
          </button>
          <button 
            @click="handleSquareOff" 
            class="submit-button"
            :disabled="!firstPassword || !secondPassword"
          >
            Confirm Square Off
          </button>
        </div>
      </div>
    </div>

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
            <th @click="sortByUsername" class="sortable-column">
              Username
              <span v-if="sortKey === 'username'" class="sort-icon">
                {{ sortOrder === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in sortedUsers" :key="index">
            <td>{{ user.username }}</td>
            <td class="action-buttons">
              <button 
                @click="openPasswordModal('position', user)"
                class="action-button position-button"
                :disabled="updateLoading"
              >
                <i class="fas fa-chart-line"></i>
                Square Off Positions
              </button>
              <button 
                @click="openPasswordModal('broker', user)"
                class="action-button broker-button"
                :disabled="updateLoading"
              >
                <i class="fas fa-exchange-alt"></i>
                Square Off Broker Positions
              </button>
              <button
                @click="goToMarginUpdate(user)"
                class="action-button margin-update-button"
              >
                <i class="fas fa-balance-scale"></i>
                Margin Update
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

// State management
const users = ref([]);
const loading = ref(false);
const error = ref(null);
const updateLoading = ref(false);
const searchQuery = ref('');
const showPasswordModal = ref(false);
const firstPassword = ref('');
const secondPassword = ref('');
const passwordError = ref('');
const modalType = ref('');
const selectedUser = ref(null);

// Sorting state
const sortKey = ref('username');
const sortOrder = ref('asc');

// Sort function
const sortByUsername = () => {
  if (sortKey.value === 'username') {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = 'username';
    sortOrder.value = 'asc';
  }
};

// Filtered and sorted users
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value;
  
  return users.value.filter(user => 
    user.username.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const sortedUsers = computed(() => {
  return [...filteredUsers.value].sort((a, b) => {
    if (!a?.username || !b?.username) {
      console.warn('Invalid user data detected:', { a, b });
      return 0;
    }
    const aValue = a.username.toLowerCase();
    const bValue = b.username.toLowerCase();
    
    return sortOrder.value === 'asc' 
      ? aValue.localeCompare(bValue)
      : bValue.localeCompare(aValue);
  });
});

const openPasswordModal = (type, user) => {
  modalType.value = type;
  selectedUser.value = user;
  showPasswordModal.value = true;
  firstPassword.value = '';
  secondPassword.value = '';
  passwordError.value = '';
};

const closePasswordModal = () => {
  showPasswordModal.value = false;
  modalType.value = '';
  selectedUser.value = null;
  firstPassword.value = '';
  secondPassword.value = '';
  passwordError.value = '';
};

const handleSquareOff = async () => {
  if (!firstPassword.value || !secondPassword.value) {
    passwordError.value = 'Please enter both passwords';
    return;
  }

  try {
    updateLoading.value = true;
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    const response = await fetch(`https://production2.swancapital.in/squareOffPositions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: selectedUser.value.username,
        first_password: firstPassword.value,
        second_password: secondPassword.value,
        type:modalType.value
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to square off positions');
    }

    alert(`Successfully squared off ${modalType.value === 'position' ? 'positions' : 'broker positions'} for ${selectedUser.value.username}`);
    closePasswordModal();
  } catch (err) {
    passwordError.value = err.message;
  } finally {
    updateLoading.value = false;
  }
};

const fetchUsers = async () => {
  try {
    loading.value = true;
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    const response = await fetch('https://production2.swancapital.in/getUsers', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) throw new Error('Failed to fetch users');
    
    const data = await response.json();
    if (!Array.isArray(data)) {
      throw new Error('Invalid user data received from server');
    }
    users.value = data.filter(user => user && typeof user === 'object' && user.username);
  } catch (err) {
    error.value = err.message;
    console.error('Error fetching users:', err);
  } finally {
    loading.value = false;
  }
};

const router = useRouter();

const goToMarginUpdate = (user) => {
  if (user && user.username) {
    router.push(`/marginupdatecheck/${user.username}`);
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.admin-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-title {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 32px;
  text-align: center;
}

.actions-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.search-container {
  position: relative;
  flex: 0 1 300px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 36px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background-color: white;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.table-container {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th {
  background-color: #f8fafc;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #4b5563;
  border-bottom: 2px solid #e5e7eb;
}

.admin-table td {
  padding: 16px;
  color: #1f2937;
  border-bottom: 1px solid #e5e7eb;
}

.admin-table tr:hover {
  background-color: #f8fafc;
}

.sortable-column {
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-icon {
  font-size: 0.8em;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.admin-table td.action-buttons {
  text-align: right;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.position-button {
  background-color: #3b82f6;
  color: white;
}

.position-button:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.broker-button {
  background-color: #10b981;
  color: white;
}

.broker-button:hover:not(:disabled) {
  background-color: #059669;
  transform: translateY(-1px);
}

.margin-update-button {
  background-color: #f59e42;
  color: white;
}

.margin-update-button:hover:not(:disabled) {
  background-color: #d97706;
  transform: translateY(-1px);
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

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 8px;
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
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.input-error {
  border-color: #ef4444;
}

.error-text {
  color: #ef4444;
  font-size: 14px;
  margin-top: 4px;
  display: block;
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

.loading-state {
  text-align: center;
  padding: 48px;
  color: #6b7280;
}

.loader {
  border: 4px solid #f3f3f3;
  border-radius: 50%;
  border-top: 4px solid #3b82f6;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #dc2626;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.retry-button {
  background-color: #dc2626;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background-color: #b91c1c;
}

@media (max-width: 640px) {
  .admin-container {
    padding: 16px;
  }

  .action-buttons {
    flex-direction: column;
  }

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