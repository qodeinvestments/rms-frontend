<!-- TradingPositions.vue -->
<script setup>
import { ref, computed, onMounted ,watch} from 'vue';
import * as XLSX from 'xlsx';

// Add prop for number of sticky columns
const props = defineProps({
  stickyColumns: {
    type: Number,
    default: 1,
    validator: (value) => value >= 0
  }
});

const userSelectOptions = computed(() => {
  const totalUsers = filteredUsers.value.length;
  const allSelected = selectedUsers.value.length === totalUsers;

  const selectAllOption = {
    label: allSelected ? 'Deselect All' : 'Select All',
    value: '__ALL__'
  };

  // Sort filteredUsers alphabetically by label before combining
  const sortedUsers = [...filteredUsers.value].sort((a, b) =>
    a.label.localeCompare(b.label)
  );

  return [selectAllOption, ...sortedUsers];
});

function handleSelectChange(newValue) {
  // 1. Check if user clicked the special item
  if (newValue.includes('__ALL__')) {
    // Remove the special "__ALL__" item right away
    newValue = newValue.filter(item => item !== '__ALL__');

    // 2. Compare to see if we already have all real users selected
    const allUsers = filteredUsers.value.map(u => u.value);

    // If after removing __ALL__, we still have the same length as all users,
    // it means the user is trying to "deselect all".
    if (newValue.length === allUsers.length) {
      selectedUsers.value = [];
    } else {
      // Otherwise, let's select all users
      selectedUsers.value = [...allUsers];
    }
  } else {
    // 3. No special item was selected; just update the model
    selectedUsers.value = newValue;
  }
}

const tableContainerRef = ref(null);
const tradingData = ref({});
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const prefixQuery = ref('');
const sortConfig = ref({ key: '', direction: '' });
const showCopiedNotification = ref(false);
const selectedUsers = ref([]);  // Will hold selected users


const filteredUsers = computed(() => {
  return uniqueUsers.value.map(user => ({ label: user, value: user }));
});


// Helper function to determine if a column should be sticky
const isColumnSticky = (index) => index < props.stickyColumns;

const toggleSort = (key) => {
  if (sortConfig.value.key === key) {
    // Toggle direction if same key
    sortConfig.value.direction = sortConfig.value.direction === 'asc' ? 'desc' : 'asc';
  } else {
    // New key, default to ascending
    sortConfig.value.key = key;
    sortConfig.value.direction = 'asc';
  }
};

// Modified copyToClipboard to include PNL
const copyToClipboard = () => {
  const headerRow = [
    'System Tag',
    'Symbol',
    'Strategy Type',
    'Time',
    'Price',
    'LTP',
    ...selectedUsers.value.flatMap(user => [user, `${user} PNL`])
  ].join('\t');
  
  const dataRows = filteredAndSortedData.value
    .map(row => {
      const values = [
        row.systemtag,
        row.symbol,
        row.strategyType,
        row.timing,
        row.price,
        row.ltp,
        ...selectedUsers.value.flatMap(user => [
          row[user] ? row[user].toLocaleString() : '-',
          row[`${user}_pnl`] ? row[`${user}_pnl`].toLocaleString() : '-'
        ])
      ];
      return values.join('\t');
    })
    .join('\n');
  
  const clipboardText = `${headerRow}\n${dataRows}`;
  
  navigator.clipboard.writeText(clipboardText)
    .then(() => {
      showCopiedNotification.value = true;
      setTimeout(() => {
        showCopiedNotification.value = false;
      }, 2000);
    })
    .catch(err => {
      console.error('Failed to copy table:', err);
      alert('Failed to copy table to clipboard');
    });
};

const fetchTradingData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    const response = await fetch('https://production2.swancapital.in/live_strats', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error fetching positions: ${errorMessage}`);
    }

    const data = await response.json();
    tradingData.value = data || {};
  } catch (err) {
    error.value = err.message;
    console.error('Error fetching positions:', err.message);
  } finally {
    loading.value = false;
  }
};

// Get unique list of users across all positions
const uniqueUsers = computed(() => {
  const users = new Set();
  Object.values(tradingData.value).forEach(strategy => {
    Object.values(strategy.positions).forEach(position => {
      Object.keys(position).forEach(user => users.add(user));
    });
  });
  return Array.from(users);
});



// Extract trailing number from any string
const extractTrailingNumber = (str) => {
  if (!str) return null;
  
  // Match any numbers at the end of the string
  const match = str.match(/(\d+)$/);
  
  // Convert to number and return, otherwise return null
  return match ? parseInt(match[1], 10) : null;
};

// Modified tableData computed
const tableData = computed(() => {
  return Object.entries(tradingData.value).map(([uid, data]) => {
    const positions = Object.entries(data.positions).map(([symbol, userPositions]) => {
      const timing = data.timing[symbol] ?? "";
      const price = data.price[symbol] ?? -1;
      const ltp = data.ltp[symbol] ?? -1;
      const pnlData = data.pnl[symbol] ?? {};
      
      return {
        uid,
        systemtag: data.systemtag,
        type: extractTrailingNumber(data.systemtag),
        symbol,
        strategyType: data.strategyType,
        timing: timing,
        price: price,
        ltp: ltp,
        ...Object.fromEntries(uniqueUsers.value.map(user => [user, userPositions[user] || 0])),
        ...Object.fromEntries(uniqueUsers.value.map(user => [`${user}_pnl`, pnlData[user] || 0]))
      };
    });
    return positions;
  }).flat();
});

const filteredAndSortedData = computed(() => {
  let data = filteredTableData.value;
  
  if (sortConfig.value.key && sortConfig.value.direction) {
    data = [...data].sort((a, b) => {
      let aVal = a[sortConfig.value.key];
      let bVal = b[sortConfig.value.key];
      
      // Handle numeric sorting for user positions
      if (uniqueUsers.value.includes(sortConfig.value.key)) {
        aVal = Number(aVal) || 0;
        bVal = Number(bVal) || 0;
      }
      
      if (aVal === bVal) return 0;
      
      const direction = sortConfig.value.direction === 'asc' ? 1 : -1;
      return aVal > bVal ? direction : -direction;
    });
  }
  
  return data;
});

const filteredTableData = computed(() => {
  let data = tableData.value;
  
  // Apply prefix search first if exists
  if (prefixQuery.value) {
    const prefix = prefixQuery.value.toLowerCase();
    data = data.filter(row =>
      row.symbol.toLowerCase().startsWith(prefix) ||
      row.systemtag.toLowerCase().startsWith(prefix) ||
      row.strategyType.toLowerCase().startsWith(prefix)
    );
  }
  
  // Then apply regular search if exists
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    data = data.filter(row => 
      row.uid.toLowerCase().includes(query) ||
      row.symbol.toLowerCase().includes(query) ||
      row.systemtag.toLowerCase().includes(query) ||
      row.strategyType.toLowerCase().includes(query)
    );
  }
  
  return data;
});

const getSortIcon = (key) => {
  if (sortConfig.value.key !== key) return '↕️';
  return sortConfig.value.direction === 'asc' ? '↑' : '↓';
};

// Export functions remain the same
const exportToExcel = () => {
  // Create worksheet from the filtered data
  const ws = XLSX.utils.json_to_sheet(filteredTableData.value);
  
  // Create workbook and add the worksheet
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Trading Positions');
  
  // Generate file name with current date and time
  const now = new Date();
  const fileName = `trading_positions_${now.toISOString().split('T')[0]}.xlsx`;
  
  // Save file
  XLSX.writeFile(wb, fileName);
};

const exportToCSV = () => {
  // Create worksheet from the filtered data
  const ws = XLSX.utils.json_to_sheet(filteredTableData.value);
  
  // Create workbook and add the worksheet
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Trading Positions');
  
  // Generate file name with current date and time
  const now = new Date();
  const fileName = `trading_positions_${now.toISOString().split('T')[0]}.csv`;
  
  // Save file as CSV
  XLSX.writeFile(wb, fileName, { bookType: 'csv' });
};


watch(uniqueUsers, (newUsers) => {
  // Add any new users to selection
  const newUsersSet = new Set(newUsers);
  const selectedUsersSet = new Set(selectedUsers.value);
  
  newUsers.forEach(user => {
    if (!selectedUsersSet.has(user)) {
      selectedUsers.value.push(user);
    }
  });
  
  // Remove any selected users that no longer exist
  selectedUsers.value = selectedUsers.value.filter(user => newUsersSet.has(user));
});


onMounted(() => {
  fetchTradingData();
  // Initialize with all users selected by default
  selectedUsers.value = uniqueUsers.value;
});
</script>

<!-- Template Section -->
<template>
  <div class="trading-positions-container">
    <div class="panel">
      <!-- Header Section -->
      <div class="panel-header">
        <div class="title-section">
          <h2 class="title">Live Positions</h2>
          <span class="subtitle">Live market positions tracker</span>
        </div>
        
        <!-- Controls Section -->
        <div class="controls-section">
          <div class="user-select-container">
            <a-select
              v-model:value="selectedUsers"
              mode="multiple"
              style="width: 100%"
              placeholder="Select Users"
              :options="userSelectOptions"     
              @change="handleSelectChange"     
            >
            </a-select>
          </div>
          <!-- Search Boxes -->
          <div class="search-container">
            <div class="search-wrapper">
              <input
                v-model="prefixQuery"
                type="text"
                placeholder="Prefix search..."
                class="search-input prefix-search"
              />
              <span class="search-icon">🔍</span>
            </div>
            <div class="search-wrapper">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Contains search..."
                class="search-input"
              />
              <span class="search-icon">🔍</span>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="action-buttons">
            <button 
              @click="exportToExcel"
              class="action-button excel-button"
              :disabled="loading || !filteredAndSortedData.length"
            >
              <span class="button-icon">📊</span>
              XLSX
            </button>
            <button 
              @click="exportToCSV"
              class="action-button csv-button"
              :disabled="loading || !filteredAndSortedData.length"
            >
              <span class="button-icon">📄</span>
              CSV
            </button>
            <button 
              @click="fetchTradingData" 
              class="action-button refresh-button"
              :class="{ 'loading': loading }"
              :disabled="loading"
            >
              <span class="button-icon">🔄</span>
              {{ loading ? 'Refreshing...' : 'Refresh' }}
            </button>
            <div class="relative">
              <button 
                @click="copyToClipboard"
                class="action-button copy-button"
                :disabled="loading || !filteredAndSortedData.length"
              >
                <span class="button-icon">📋</span>
                Copy
              </button>
              <div v-if="showCopiedNotification" class="copied-notification">
                Copied!
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        <span class="error-icon">⚠️</span>
        {{ error }}
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <span class="loading-text">Loading trading positions...</span>
      </div>

      <!-- Data Table -->
      <div v-else-if="filteredAndSortedData.length" class="table-wrapper">
        <div 
          ref="tableContainerRef"
          class="table-container"
        >
        <table class="data-table">
      <thead>
        <tr>
          <!-- Previous headers remain the same until user columns -->
          <th @click="toggleSort('systemtag')" 
              :class="['sortable', { 'th-sticky': isColumnSticky(0) }]"
              :style="isColumnSticky(0) ? 'left: 0px' : ''">
            System Tag
            <span class="sort-icon">{{ getSortIcon('systemtag') }}</span>
          </th>
          
          <th @click="toggleSort('type')" 
              :class="['sortable', { 'th-sticky': isColumnSticky(1) }]"
              :style="isColumnSticky(1) ? 'left: 200px' : ''">
            Type
            <span class="sort-icon">{{ getSortIcon('type') }}</span>
          </th>
          
          <th @click="toggleSort('symbol')" 
              :class="['sortable', { 'th-sticky': isColumnSticky(2) }]"
              :style="isColumnSticky(2) ? 'left: 400px' : ''">
            Symbol
            <span class="sort-icon">{{ getSortIcon('symbol') }}</span>
          </th>

          <th @click="toggleSort('strategyType')" class="sortable">
            Strategy Type
            <span class="sort-icon">{{ getSortIcon('strategyType') }}</span>
          </th>
          
          <th @click="toggleSort('timing')" class="sortable">
            Time
            <span class="sort-icon">{{ getSortIcon('timing') }}</span>
          </th>
          
          <th @click="toggleSort('price')" class="sortable">
            Price
            <span class="sort-icon">{{ getSortIcon('price') }}</span>
          </th>
          
          <th @click="toggleSort('ltp')" class="sortable">
            LTP
            <span class="sort-icon">{{ getSortIcon('ltp') }}</span>
          </th>
          
          <!-- User columns with PNL -->
          <template v-for="user in selectedUsers" :key="user">
            <th @click="toggleSort(user)" class="sortable user-column">
              {{ user }}
              <span class="sort-icon">{{ getSortIcon(user) }}</span>
            </th>
            <th @click="toggleSort(`${user}_pnl`)" class="sortable pnl-column">
              {{ user }} PNL
              <span class="sort-icon">{{ getSortIcon(`${user}_pnl`) }}</span>
            </th>
          </template>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in filteredAndSortedData" :key="index" class="data-row">
          <!-- Previous cells remain the same until user columns -->
          <td :class="{ 'td-sticky': isColumnSticky(0) }"
              :style="isColumnSticky(0) ? 'left: 0px' : ''">
            {{ row.systemtag }}
          </td>
          
          <td :class="['type-cell', { 'td-sticky': isColumnSticky(1) }]"
              :style="isColumnSticky(1) ? 'left: 200px' : ''">
            <span class="type-badge">{{ row.type }}</span>
          </td>
          
          <td :class="['symbol-cell', { 'td-sticky': isColumnSticky(2) }]"
              :style="isColumnSticky(2) ? 'left: 400px' : ''">
            {{ row.symbol }}
          </td>

          <td class="type-cell">
            <span class="strategy-type-badge">{{ row.strategyType }}</span>
          </td>
          
          <td class="time-cell">
            <span class="time-badge">{{ row.timing }}</span>
          </td>
          
          <td class="price-cell">
            <span class="type-badge">{{ row.price }}</span>
          </td>
          
          <td class="ltp-cell">
            <span class="type-badge">{{ row.ltp }}</span>
          </td>

          <!-- User and PNL columns -->
          <template v-for="user in selectedUsers" :key="user">
            <td class="td-user"
                :class="{'value-negative': row[user] < 0, 'value-positive': row[user] > 0}">
              {{ row[user] ? row[user].toLocaleString() : '-' }}
            </td>
            <td class="td-pnl"
                :class="{'value-negative': row[`${user}_pnl`] < 0, 'value-positive': row[`${user}_pnl`] > 0}">
              {{ row[`${user}_pnl`] ? row[`${user}_pnl`].toLocaleString() : '-' }}
            </td>
          </template>
        </tr>
      </tbody>
  </table>
        </div>
      </div>

      <!-- No Data State -->
      <div v-else class="no-data">
        <span class="no-data-icon">📊</span>
        <p class="no-data-text">
          {{ searchQuery ? 'No matching positions found' : 'No trading positions found' }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Base styles */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Roboto+Mono:wght@500;600&family=JetBrains+Mono:wght@600;700&display=swap');

.trading-positions-container {
  padding: 1.5rem;
  height: 100vh;
  background: linear-gradient(145deg, #f9fafb, #f3f4f6);
  font-family: 'Inter', sans-serif;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Panel Styles */
.panel {
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Table wrapper and container styles */
.table-wrapper {
  margin: 1rem;
  border-radius: 0.8rem;
  background: white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
  position: relative;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.table-container {
  width: 100%;
  overflow: auto;
  position: relative;
  border-radius: 0.8rem;
  flex: 1;
  min-height: 0;
}

/* Sticky column styles */
.th-sticky {
  position: sticky !important;
  z-index: 20;
  background: linear-gradient(145deg, #f8fafc, #f1f5f9) !important;
  border-right: 1px solid #e2e8f0;
  white-space: nowrap;
  padding: 1rem 1.5rem;
}

.td-sticky {
  position: sticky !important;
  z-index: 10;
  background: white !important;
  border-right: 1px solid #e2e8f0;
  white-space: nowrap;
  padding: 1rem 1.5rem;
}

/* Header Styles */
.panel-header {
  padding: 2rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  background: linear-gradient(to bottom, white, #f8fafc);
  flex-shrink: 0;
}

.title-section {
  margin-bottom: 1.5rem;
  text-align: center;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b, #334155);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  color: #64748b;
}

/* Search Container Styles */
.search-container {
  display: flex;
  gap: 1rem;
  flex-grow: 1;
  max-width: 64rem;
}

.search-wrapper {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 1rem 1.25rem 1rem 3.2rem;
  border-radius: 1rem;
  border: 2px solid rgba(226, 232, 240, 0.6);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  font-size: 1rem;
  color: #1e293b;
  transition: all 0.3s ease;
}

.search-icon {
  position: absolute;
  left: 1.2rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 1.2rem;
  pointer-events: none;
}

/* Controls Section */
.controls-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 2rem;
}

.action-buttons {
  margin-top: 1rem;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}


/* Table Styles */
.data-table {
  width: max-content;
  min-width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

/* Regular column styles */
th, td {
  padding: 0.50rem 1.00rem;
  white-space: nowrap;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
}

/* Header row styles */
th {
  background: linear-gradient(145deg, #f8fafc, #f1f5f9);
  font-weight: 600;
  color: #1e293b;
  position: sticky;
  top: 0;
  z-index: 10;
}

/* User value cells */
.td-user {
  font-family: 'IBM Plex Mono', monospace;
  font-weight: 600;
  padding: 1rem 1.5rem;
}

.value-positive {
  color: #059669;
  background: linear-gradient(135deg, #d1fae5, #ecfdf5);
  border-radius: 0.4rem;
}

.value-negative {
  color: #dc2626;
  background: linear-gradient(135deg, #fee2e2, #fef2f2);
  border-radius: 0.4rem;
}

/* Badge styles */
.type-badge,
.strategy-type-badge,
.time-badge {
  padding: 0.4rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
  white-space: nowrap;
}

.type-badge {
  background: linear-gradient(135deg, #ddd6fe, #ede9fe);
  color: #5b21b6;
}

.strategy-type-badge {
  background: linear-gradient(135deg, #e0f2fe, #bae6fd);
  color: #0369a1;
}

.time-badge {
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  color: #475569;
}

/* Error and Loading States */
.error-message {
  margin: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  border-radius: 0.75rem;
  color: #b91c1c;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1.5rem;
}

.loading-spinner {
  width: 3.5rem;
  height: 3.5rem;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Action Buttons */
.action-button {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.excel-button {
  background: #10b981;
  color: white;
}

.csv-button {
  background: #22c55e;
  color: white;
}

.refresh-button {
  background: #3b82f6;
  color: white;
}

.copy-button {
  background: #6366f1;
  color: white;
}

/* Button states */
.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Sort icons */
.sort-icon {
  margin-left: 0.5rem;
  font-size: 0.8rem;
}

/* Copied notification */
.copied-notification {
  position: absolute;
  top: -2rem;
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  animation: fadeInOut 2s ease-in-out;
}

/* No Data State */
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1.5rem;
}

.no-data-icon {
  font-size: 3rem;
  color: #94a3b8;
}

.no-data-text {
  color: #64748b;
  font-size: 1.1rem;
}

/* Symbol cell */
.symbol-cell {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1.1rem;
  color: #1e293b;
  padding: 0.6rem 1.2rem;
  white-space: nowrap;
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0; }
  10%, 90% { opacity: 1; }
}

/* Scrollbar Styles */
.table-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Responsive Design */
@media (max-width: 768px) {
  .controls-section {
    flex-direction: column;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .action-buttons {
    width: 100%;
    grid-template-columns: repeat(2, 1fr);
    display: grid;
    gap: 0.75rem;
  }
  
  .refresh-button {
    grid-column: span 2;
  }
}

/* Additional styles for PNL columns */
.pnl-column {
  background: linear-gradient(145deg, #f1f5f9, #e2e8f0);
  font-weight: 600;
}

.td-pnl {
  font-family: 'IBM Plex Mono', monospace;
  font-weight: 600;
  padding: 1rem 1.5rem;
}

/* Modified spacing for user and PNL columns */
.user-column,
.pnl-column {
  padding: 0.75rem 1.25rem;
}


/* Add these to your style section */
.user-select-container {
  margin-top: 1rem;
  width: 100%;
  max-width: 64rem;
}

.ant-select {
  width: 100%;
}

.ant-select-selection {
  border-radius: 1rem;
  border: 2px solid rgba(226, 232, 240, 0.6);
  background: rgba(255, 255, 255, 0.9);
}

/* Modify the controls-section style */

</style>