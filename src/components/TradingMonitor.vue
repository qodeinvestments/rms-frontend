<!-- TradingPositions.vue -->
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import * as XLSX from 'xlsx';

const tradingData = ref({});
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const prefixQuery = ref(''); // New prefix search query
const sortConfig = ref({ key: '', direction: '' });

// Sorting function
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

const copyToClipboard = () => {
  // Get visible columns and transform them for the trading positions table
  const headerRow = [
    'System Tag',
    'Symbol',
    'Strategy Type',
    'Time',
    ...uniqueUsers.value
  ].join('\t');
  
  // Create data rows
  const dataRows = filteredAndSortedData.value
    .map(row => {
      const values = [
        row.systemtag,
        row.symbol,
        row.strategyType,
        row.timing,
        ...uniqueUsers.value.map(user => {
          const value = row[user];
          return value ? value.toLocaleString() : '-';
        })
      ];
      return values.join('\t');
    })
    .join('\n');
  
  // Combine headers and data
  const clipboardText = `${headerRow}\n${dataRows}`;
  
  // Copy to clipboard
  navigator.clipboard.writeText(clipboardText)
    .then(() => {
      
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
  return match ? match[1] : null;
};

// Modified tableData computed
const tableData = computed(() => {
  return Object.entries(tradingData.value).map(([uid, data]) => {
    const positions = Object.entries(data.positions).map(([symbol, userPositions]) => {
      const timing = data.timing[symbol] ?? "";
      return {
        uid,
        systemtag: data.systemtag,
        type: extractTrailingNumber(data.systemtag), // Will work with any string ending in numbers
        symbol,
        strategyType: data.strategyType,
        timing: timing,
        ...Object.fromEntries(uniqueUsers.value.map(user => [user, userPositions[user] || 0]))
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

onMounted(() => {
  fetchTradingData();
});
let refreshInterval;
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>

<!-- Template Section -->
<template>
  <div class="trading-positions-container">
    <div class="panel">
      <!-- Header Section -->
      <div class="panel-header">
        <div class="title-section">
          <h2 class="title">Trading Positions</h2>
          <span class="subtitle">Live market positions tracker</span>
        </div>
        
        <!-- Controls Section -->
        <div class="controls-section">
        <!-- Search Boxes -->
          <div class="search-container">
            <div class="search-wrapper">
              <input
                v-model="prefixQuery"
                type="text"
                placeholder="Prefix search..."
                class="search-input prefix-search"
              />
              <span class="search-icon">🔍P</span>
            </div>
            <div class="search-wrapper">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Contains search..."
                class="search-input"
              />
              <span class="search-icon">🔍C</span>
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
            <button 
              @click="copyToClipboard"
              class="action-button csv-button"
              :disabled="loading || !filteredAndSortedData.length"
            >
              <span class="button-icon">📋</span>
              Copy
            </button>
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
      <div v-else-if="filteredAndSortedData.length" class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th @click="toggleSort('systemtag')" 
                  class="th-fixed sortable"
                  :class="{ 'active-sort': sortConfig.key === 'systemtag' }">
                System Tag
                <span class="sort-icon">{{ getSortIcon('systemtag') }}</span>
              </th>
              <th @click="toggleSort('type')" 
                  class="th-fixed sortable"
                  :class="{ 'active-sort': sortConfig.key === 'type' }">
                      Type
                  <span class="sort-icon">{{ getSortIcon('type') }}</span>
              </th>
              <th @click="toggleSort('symbol')" 
                  class="th-fixed sortable"
                  :class="{ 'active-sort': sortConfig.key === 'symbol' }">
                Symbol
                <span class="sort-icon">{{ getSortIcon('symbol') }}</span>
              </th>
              <th @click="toggleSort('strategyType')" 
                  class="th-fixed sortable"
                  :class="{ 'active-sort': sortConfig.key === 'strategyType' }">
                Strategy Type
                <span class="sort-icon">{{ getSortIcon('strategyType') }}</span>
              </th>
              <th @click="toggleSort('timing')" 
                  class="th-fixed sortable"
                  :class="{ 'active-sort': sortConfig.key === 'timing' }">
                Time
                <span class="sort-icon">{{ getSortIcon('timing') }}</span>
              </th>
              <th v-for="user in uniqueUsers" 
                  :key="user" 
                  @click="toggleSort(user)"
                  class="th-user sortable"
                  :class="{ 'active-sort': sortConfig.key === user }">
                {{ user }}
                <span class="sort-icon">{{ getSortIcon(user) }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in filteredAndSortedData" 
                :key="index"
                class="data-row">
              <td class="td-fixed uid-cell">{{ row.systemtag }}</td>
              <td class="td-fixed type-cell">
                <span class="type-badge">{{ row.type }}</span>
              </td>
              <td class="td-fixed symbol-cell">{{ row.symbol }}</td>
              <td class="td-fixed type-cell">
                <span class="strategy-type-badge">{{ row.strategyType }}</span>
              </td>
              <td class="td-fixed time-cell">
                <span class="time-badge">{{ row.timing }}</span>
              </td>
              <td v-for="user in uniqueUsers" 
                  :key="user" 
                  class="td-user"
                  :class="{'value-negative': row[user] < 0, 'value-positive': row[user] > 0}">
                {{ row[user] ? row[user].toLocaleString() : '-' }}
              </td>
            </tr>
          </tbody>
        </table>
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

.search-container {
  display: flex;
  gap: 1rem;
  flex-grow: 1;
  max-width: 64rem;
}


.trading-positions-container {
  padding: 1.5rem;
  min-height: 100vh;
  background: linear-gradient(145deg, #f9fafb, #f3f4f6);
  font-family: 'Inter', sans-serif;
}

/* Panel Styles */
.panel {
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  overflow: hidden;
}

/* Header Styles */
.panel-header {
  padding: 2rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  background: linear-gradient(to bottom, white, #f8fafc);
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

/* Search Bar Styles */
.search-wrapper {
  flex: 1;
}


.prefix-search {
  border-color: rgba(99, 102, 241, 0.4);
}

.prefix-search:hover {
  border-color: rgba(99, 102, 241, 0.6);
}

.prefix-search:focus {
  border-color: rgb(99, 102, 241);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
}

/* Update responsive design for search container */
@media (max-width: 768px) {
  .search-container {
    flex-direction: column;
    width: 100%;
  }
  
  .search-wrapper {
    width: 100%;
  }
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
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.search-input:hover {
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
  background: white;
}

.search-icon {
  position: absolute;
  left: 1.2rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 1.2rem;
  pointer-events: none;
  transition: all 0.3s ease;
}

/* Controls Section Styles */
.controls-section {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  padding: 0 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

/* Action Button Styles */
.action-button {
  padding: 0.875rem 1.5rem;
  border-radius: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.type-badge {
  background: linear-gradient(135deg, #ddd6fe, #ede9fe);
  color: #5b21b6;
  font-weight: 600;
  padding: 0.4rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  letter-spacing: 0.02em;
  box-shadow: 0 2px 4px rgba(91, 33, 182, 0.05);
  display: inline-block;
}

.excel-button {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.csv-button {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
}

.refresh-button {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

/* Table Styles */
.table-container {
  margin: 1rem;
  border-radius: 0.8rem;
  background: white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: transparent;
}

/* Sorting Styles */
.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
  padding-right: 2.5rem !important;
  transition: all 0.2s ease;
}

.sortable:hover {
  background: linear-gradient(145deg, #e2e8f0, #f1f5f9);
}

.sort-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.sortable:hover .sort-icon {
  opacity: 1;
}

.active-sort {
  background: linear-gradient(145deg, #e2e8f0, #f1f5f9) !important;
  color: #2563eb !important;
}

.active-sort .sort-icon {
  opacity: 1;
  color: #2563eb;
}

/* Table Header Styles */
.data-table th {
  background: linear-gradient(145deg, #f8fafc, #f1f5f9);
  padding: 1.2rem 1rem;
  font-weight: 600;
  color: #1e293b;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 0.05em;
  position: sticky;
  top: 0;
  z-index: 10;
  transition: all 0.2s ease;
}

/* Table Cell Styles */
.td-fixed {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
  position: sticky;
  left: 0;
  background-color: white;
  text-align: center !important;
  font-size: 1.05rem;
  display: table-cell;
  vertical-align: middle;
}

.td-user {
  font-family: 'IBM Plex Mono', monospace;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: center;
  white-space: nowrap;
  font-weight: 600;
  font-size: 1.1rem;
  font-feature-settings: "tnum" 1;
  letter-spacing: 0.02em;
  background: white;
  transition: all 0.2s ease;
}

/* Value Styling */
.value-positive {
  color: #059669;
  font-weight: 600;
  background: linear-gradient(135deg, #d1fae5, #ecfdf5);
  border-radius: 0.4rem;
  padding: 0.5rem 1rem;
  box-shadow: 0 2px 4px rgba(5, 150, 105, 0.1);
}

.value-negative {
  color: #dc2626;
  font-weight: 600;
  background: linear-gradient(135deg, #fee2e2, #fef2f2);
  border-radius: 0.4rem;
  padding: 0.5rem 1rem;
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.1);
}

/* Badge Styles */
.strategy-type-badge {
  background: linear-gradient(135deg, #e0f2fe, #bae6fd);
  color: #0369a1;
  font-weight: 600;
  padding: 0.4rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  letter-spacing: 0.02em;
  box-shadow: 0 2px 4px rgba(3, 105, 161, 0.05);
  display: inline-block;
}

.time-badge {
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  color: #475569;
  font-weight: 600;
  padding: 0.4rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  letter-spacing: 0.02em;
  box-shadow: 0 2px 4px rgba(71, 85, 105, 0.05);
  display: inline-block;
}

/* Symbol Cell Styles */
.symbol-cell {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1.1rem;
  color: #1e293b;
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, #f1f5f9, #f8fafc);
  border-radius: 0.6rem;
  padding: 0.6rem 1.2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  text-align: center;
  transition: all 0.2s ease;
  font-feature-settings: "tnum" 1;
}

.data-row:hover .symbol-cell {
  background: linear-gradient(135deg, #e2e8f0, #f1f5f9);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  transform: scale(1.02);
  border-color: #cbd5e1;
}

/* Status Message Styles */
.error-message {
  margin: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  color: #b91c1c;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
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
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.1);
}

.loading-text {
  color: #64748b;
  font-weight: 500;
  font-size: 1.1rem;
}

/* No Data State Styles */
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #94a3b8;
  gap: 1.5rem;
}

.no-data-icon {
  font-size: 3rem;
}

.no-data-text {
  font-size: 1.2rem;
  font-weight: 500;
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
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

/* Row Hover Effects */
.data-row {
  transition: all 0.3s ease;
}

.data-row:hover {
  background: linear-gradient(145deg, rgba(248, 250, 252, 0.5), rgba(241, 245, 249, 0.5));
  transform: scale(1.002);
}

/* Button Hover Effects */
.action-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(59, 130, 246, 0.2);
}

.excel-button:hover:not(:disabled) {
  box-shadow: 0 6px 15px rgba(16, 185, 129, 0.2);
}

.csv-button:hover:not(:disabled) {
  box-shadow: 0 6px 15px rgba(34, 197, 94, 0.2);
}

.action-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

/* Responsive Design */
@media (max-width: 768px) {
  .panel-header {
    padding: 1.5rem;
  }

  .title {
    font-size: 1.75rem;
  }

  .controls-section {
    flex-direction: column;
    gap: 1rem;
  }

  .search-wrapper {
    width: 100%;
  }

  .action-buttons {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .refresh-button {
    grid-column: span 2;
  }

  .sortable {
    padding-right: 2rem !important;
  }

  .sort-icon {
    right: 0.5rem;
  }
}

/* Print Styles */
@media print {
  .trading-positions-container {
    padding: 0;
    background: none;
  }

  .panel {
    box-shadow: none;
    border: none;
  }

  .controls-section,
  .action-buttons,
  .search-wrapper {
    display: none;
  }

  .data-table {
    font-size: 10pt;
  }

  .value-positive,
  .value-negative {
    background: none;
    box-shadow: none;
  }
}
</style>