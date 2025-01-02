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
              <th>Email</th>
              <th>Role</th>
              <th>Account Access</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in users" :key="index">
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.role }}</td>
              <td>{{ user['Account Access'].join(', ') }}</td>
              <td>
                <button 
                  @click="openEditModal(user)"
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
              <input 
                v-model="editingUser.role"
                type="text"
                :disabled="updateLoading"
              >
            </div>
  
            <div class="form-group">
              <label>Account Access</label>
              <input 
                v-model="accountAccessString"
                type="text"
                placeholder="Enter comma-separated values"
                :disabled="updateLoading"
              >
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
  import { ref, onMounted } from 'vue'
  
  // State management
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)
  const showModal = ref(false)
  const editingUser = ref(null)
  const editingIndex = ref(-1)
  const updateLoading = ref(false)
  const updateError = ref(null)


  const openEditModal = (user) => {
    editingUser.value = { ...user }
    editingIndex.value = users.value.findIndex(u => u.email === user.email)
    updateError.value = null
    showModal.value = true
  }
  
  // Close modal
  const closeModal = () => {
    showModal.value = false
    editingUser.value = null
    editingIndex.value = -1
    updateError.value = null
  }
  

  

  onMounted(async () => {
    try {
      const response = await fetch('https://api.swancapital.in/users');
      if (response.ok) {
        const data = await response.json();
        console.log("data from api is:", data)
        users.value = data || [];
      } else {
        console.error('Error fetching accounts:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  });
  </script>
  
  <style scoped>
 .admin-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 24px;
}

/* Table Styles */
.table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.admin-table th {
  background-color: #f9fafb;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #4b5563;
  border-bottom: 1px solid #e5e7eb;
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
.edit-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.edit-button:hover {
  background-color: #2563eb;
}

.save-button {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.save-button:hover {
  background-color: #059669;
}

.cancel-button {
  background-color: #6b7280;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 8px;
  transition: background-color 0.2s;
}

.cancel-button:hover {
  background-color: #4b5563;
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
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
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

.form-group input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  color: #1f2937;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

/* Loading and Error States (already present in your code) */
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
  </style>