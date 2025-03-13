<template>
    <div class="admin-container">
      <!-- Card-like container for the content -->
      <div class="admin-card">
        <h1 class="admin-title">Performance Data</h1>
  
        <!-- Actions Section -->
        <div class="actions-section">
          <div class="search-container">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search..." 
              class="search-input"
            />
          </div>
  
          <!-- Date Filter Section (no apply button) -->
          <div class="date-filter-container">
            <div class="date-input-group">
              <label>Start Date:</label>
              <input type="date" v-model="startDate" class="date-input" />
            </div>
            <div class="date-input-group">
              <label>End Date:</label>
              <input type="date" v-model="endDate" class="date-input" />
            </div>
          </div>
        </div>
  
        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loader"></div>
          <p>Loading Performance Data...</p>
        </div>
        
        <!-- Error State -->
        <div v-if="error" class="error-message">
          {{ error }}
          <button @click="fetchPerformanceData" class="retry-button">Retry</button>
        </div>
        
        <!-- Performance Data Table -->
        <div v-if="!loading && !error && allColumns.length > 0" class="table-container">
          <table class="admin-table">
            <thead>
              <!-- Summary Row (fixed) -->
              <tr class="sum-row">
                <th 
                    v-for="column in allColumns" 
                    :key="'sum-' + column"
                    :class="column !== 'Date' ? (columnSums[column] > 0 ? 'positive-value' : (columnSums[column] < 0 ? 'negative-value' : '')) : ''"
                >
                    {{ column === 'Date' ? '' : formatPercentage(columnSums[column] || 0) }}
                </th>
              </tr>

              <!-- Header Row (clickable for sorting) -->
              <tr class="sum-row">
                <th 
                  v-for="column in allColumns" 
                  :key="'header-' + column" 
                  @click="sortByColumn(column)"
                  class="sortable-header"
                >
                  {{ column }}
                  <span v-if="sortColumn === column && sortOrder === 'asc'"> ▲</span>
                  <span v-else-if="sortColumn === column && sortOrder === 'desc'"> ▼</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in sortedFilteredPerformanceData" :key="index">
                <td 
                  v-for="column in allColumns" 
                  :key="`${index}-${column}`"
                  :class="getPerformanceClass(column === 'Date' ? row.date : row[column])"
                >
                  {{ column === 'Date' ? formatDate(row.date) : formatPercentage(row[column]) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  
  // State management
  const loading = ref(false);
  const error = ref(null);
  const performanceData = ref([]);
  const otherdata = ref([]);
  const searchQuery = ref('');
  const startDate = ref('');
  const endDate = ref('');
  
  // Sorting state
  const sortColumn = ref(null); // The current sorted column (e.g., 'Maverick Fund' or 'Date')
  const sortOrder = ref(null);  // 'asc', 'desc', or null
  
  // --- Sample Data ---
  // (In a real scenario, your API returns data with a "Date" key)
  const sampleData = [
    { Date: '11-02-2025', 'Maverick Fund': -5.022643569, 'Kavan Marwadi Prop': -0.11257554 },
    { Date: '13-03-2025', 'Maverick Fund': 0, 'Kavan Marwadi Prop': -0.06686624 },
    { Date: '12-03-2025', 'Maverick Fund': 0, 'Kavan Marwadi Prop': -0.018489654 }
  ];
  
  // allColumns: Returns an array with "Date" as the first header, then the other keys.
  const allColumns = computed(() => {
    if (performanceData.value.length === 0) return [];
    // Our data now only has a "date" property (lowercase) for the date
    return ['Date', ...Object.keys(performanceData.value[0]).filter(key => key !== 'date')];
  });
  
  // columnSums: Compute the sum for each numeric column (skip date)
  const columnSums = computed(() => {
    const sums = {};
    filteredPerformanceData.value.forEach(row => {
      for (const key in row) {
        if (key === 'date') continue;
        const num = parseFloat(row[key]);
        if (!isNaN(num)) {
          sums[key] = (sums[key] || 0) + num;
        }
      }
    });
    return sums;
  });
  
  // filteredPerformanceData: Filter data by search and date
  const filteredPerformanceData = computed(() => {
    let filtered = [...performanceData.value];
    
    // Apply search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      filtered = filtered.filter(row => {
        return Object.entries(row).some(([key, val]) => {
          if (key === 'date') {
            return (row.date || '').toLowerCase().includes(query);
          }
          return val.toString().toLowerCase().includes(query);
        });
      });
    }
    
    // Apply date filter if both startDate and endDate are provided
    if (startDate.value && endDate.value) {
      const start = toMidnightLocal(startDate.value);
      const end = toMidnightLocal(endDate.value);
      filtered = filtered.filter(row => {
        const rowDate = parseRowDate(row.date);
        if (!rowDate) return false;
        return rowDate >= start && rowDate <= end;
      });
    }
    
    return filtered;
  });
  
  // sortedFilteredPerformanceData: Sort filtered data based on sortColumn and sortOrder
  const sortedFilteredPerformanceData = computed(() => {
    let data = [...filteredPerformanceData.value];
    if (sortColumn.value && sortOrder.value) {
      data.sort((a, b) => {
        if (sortColumn.value === 'Date') {
          const dateA = parseRowDate(a.date);
          const dateB = parseRowDate(b.date);
          return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA;
        } else {
          const valA = parseFloat(a[sortColumn.value]);
          const valB = parseFloat(b[sortColumn.value]);
          if (isNaN(valA) || isNaN(valB)) return 0;
          return sortOrder.value === 'asc' ? valA - valB : valB - valA;
        }
      });
    }
    return data;
  });
  
  // sortByColumn: Toggle sort order on column header click
  function sortByColumn(col) {
    if (sortColumn.value !== col) {
      sortColumn.value = col;
      sortOrder.value = 'asc';
    } else {
      if (sortOrder.value === 'asc') {
        sortOrder.value = 'desc';
      } else if (sortOrder.value === 'desc') {
        sortColumn.value = null;
        sortOrder.value = null;
      } else {
        sortOrder.value = 'asc';
      }
    }
  }
  
  // --- Helper Functions ---
  
  // Convert 'YYYY-MM-DD' string to Date at local midnight
  function toMidnightLocal(dateStr) {
    const d = new Date(dateStr);
    d.setHours(0, 0, 0, 0);
    return d;
  }
  
  // Parse a row's date (assumed to be "YYYY-MM-DD")
  function parseRowDate(dateStr) {
    if (!dateStr) return null;
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    d.setHours(0, 0, 0, 0);
    return d;
  }
  
  // Format date for display (convert "YYYY-MM-DD" to "DD-MM-YYYY")
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const [year, month, day] = dateStr.split('-');
    return `${day}-${month}-${year}`;
  };
  
  // Format numeric values as percentages
  const formatPercentage = (value) => {
    const numericValue = parseFloat(value);
    if (isNaN(numericValue)) return '0.0000%';
    return numericValue.toFixed(4) + '%';
  };
  
  // Get CSS class based on value
  const getPerformanceClass = (value) => {
    return value < 0 ? 'negative-value' : value > 0 ? 'positive-value' : '';
  };
  
  // --- Data Fetching Functions ---
  
  // Fetch performance data: simulate API call and map raw data to use "date" property only.
  const fetchPerformanceData = async () => {
    loading.value = true;
    error.value = null;
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      // Suppose the API returns an array of objects with "Date" key.
      // Uncomment the next line to use sampleData:
      // otherdata.value = sampleData;
      // Map each item: remove the original "Date" key and add a new "date" property.
      const raw = otherdata.value;
      performanceData.value = raw.map(item => {
        const { Date, ...rest } = item; // remove the original Date property
        return {
          ...rest,
          date: Date, // new property "date"
        };
      });
    } catch (err) {
      error.value = err.message || 'Failed to fetch performance data';
      console.error('Error fetching performance data:', err);
    } finally {
      loading.value = false;
    }
  };
  
  // Generic fetch function
  const fetchData = async (endpoint, stateRef) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('User not authenticated');
      const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        const errorMessage = await response.text();
        throw new Error(`Error fetching ${endpoint}: ${errorMessage}`);
      }
      const data = await response.json();
      stateRef.value = data || [];
    } catch (err) {
      error.value = err.message;
      console.error(`Error fetching ${endpoint}:`, err.message);
    }
  };
  
  // Fetch slippage data and assign to otherdata
  const fetchSlippage = () => fetchData('getuserSlippage', otherdata);
  
  // --- Lifecycle ---
  
  onMounted(async () => {
    await fetchSlippage();
    console.log('Slippage response:', otherdata.value);
    await fetchPerformanceData();
    // Set default date range based on performanceData dates
    if (performanceData.value.length > 0) {
      const dateValues = performanceData.value.map(row => parseRowDate(row.date));
      const minDate = new Date(Math.min(...dateValues));
      const maxDate = new Date(Math.max(...dateValues));
      startDate.value = `${minDate.getFullYear()}-${String(minDate.getMonth() + 1).padStart(2, '0')}-${String(minDate.getDate()).padStart(2, '0')}`;
      endDate.value = `${maxDate.getFullYear()}-${String(maxDate.getMonth() + 1).padStart(2, '0')}-${String(maxDate.getDate()).padStart(2, '0')}`;
    }
  });
  </script>
  
  <style scoped>
  /* Container styling */
  .admin-container {
    padding: 20px;
    min-height: 100vh;
    background: #f9fafb;
    box-sizing: border-box;
  }
  
  /* Card-like container */
  .admin-card {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .admin-title {
    margin-bottom: 20px;
    font-size: 24px;
    font-weight: 600;
    color: #111827;
  }
  
  /* Actions section */
  .actions-section {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .search-container {
    flex: 1;
    min-width: 200px;
  }
  .search-input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    transition: border 0.2s;
  }
  .search-input:focus {
    outline: none;
    border-color: #4c86f9;
  }
  
  .date-filter-container {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
  }
  .date-input-group {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .date-input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    transition: border 0.2s;
  }
  .date-input:focus {
    outline: none;
    border-color: #4c86f9;
  }
  
  /* Loading state */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 0;
  }
  .loader {
    border: 5px solid #f3f3f3;
    border-top: 5px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin-bottom: 15px;
  }
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  /* Error message */
  .error-message {
    padding: 15px;
    background-color: #ffecec;
    color: #ff6b6b;
    border-radius: 6px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .retry-button {
    padding: 8px 16px;
    background-color: #ff6b6b;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
  .retry-button:hover {
    background-color: #e55c5c;
  }
  
  /* Table container with scrolling */
  .table-container {
    margin-top: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    max-height: 600px;
    overflow-x: auto;
    overflow-y: auto;
  }
  
  /* Table styling */
  .admin-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
  }
  
  /* Make the summary (sum) row fixed (sticky) */
  .admin-table thead .sum-row {
    position: sticky;
    top: 0;
    background-color: #f3f4f6;
    z-index: 2;
    text-align: center;
  }

  
  /* Header row (sortable) can scroll normally */
  .admin-table thead .header-row {
    background-color: #f3f4f6;
    z-index: 1;
  }
  
  .admin-table th,
  .admin-table td {
    white-space: nowrap;
    padding: 12px 15px;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .admin-table thead th {
    border-bottom: 2px solid #e5e7eb;
  }
  
  .admin-table tbody tr:hover {
    background-color: #f9fafb;
  }
  
  /* Sortable header styling */
  .sortable-header {
    cursor: pointer;
  }
  
  /* Positive/negative styling */
  .positive-value {
    color: #16a34a;
    font-weight: 500;
  }
  .negative-value {
    color: #dc2626;
    font-weight: 500;
  }
  .admin-table td {
  text-align: center;
}
  </style>
  