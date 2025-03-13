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
              <input 
                type="date" 
                v-model="startDate" 
                class="date-input"
              />
            </div>
            <div class="date-input-group">
              <label>End Date:</label>
              <input 
                type="date" 
                v-model="endDate" 
                class="date-input"
              />
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
        <div 
          v-if="!loading && !error && columns.length > 0" 
          class="table-container"
        >
          <table class="admin-table">
            <thead>
              <tr>
                <th v-for="column in columns" :key="column">{{ column }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in filteredPerformanceData" :key="index">
                <td
                  v-for="column in columns"
                  :key="`${index}-${column}`"
                  :class="getPerformanceClass(row[column])"
                >
                  {{ column !== 'Date' ? formatPercentage(row[column]) : formatDate(row[column]) }}
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
  const columns = ref([]);
  const searchQuery = ref('');
  const startDate = ref('');
  const endDate = ref('');
  
  // Sample data - this would normally come from an API
  const sampleData = [
    { date: '11-02-2025', 'Maverick Fund': -5.022643569, 'Kavan Marwadi Prop': -0.11257554 },
    { date: '13-03-2025', 'Maverick Fund': 0, 'Kavan Marwadi Prop': -0.06686624 },
    { date: '12-03-2025', 'Maverick Fund': 0, 'Kavan Marwadi Prop': -0.018489654 }
  ];
  
  // Immediately filters based on search and date range if set
  const filteredPerformanceData = computed(() => {
    let filtered = [...performanceData.value];
    
    // Search filter
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
    
    // Date filter if startDate + endDate are selected
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
  
  // Helper: Convert 'YYYY-MM-DD' to a JS Date and set to local midnight
  function toMidnightLocal(dateStr) {
    const d = new Date(dateStr);
    d.setHours(0, 0, 0, 0);
    return d;
  }
  
  function parseRowDate(dateStr) {
    if (!dateStr) return null;
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    d.setHours(0, 0, 0, 0);
    return d;
  }
  
  // Format date for display (already "DD-MM-YYYY" if your API sends it that way)
  const formatDate = (dateStr) => {
    return dateStr;
  };
  
  // Helper function to format percentages
  const formatPercentage = (value) => {
    const numericValue = parseFloat(value);
    if (isNaN(numericValue)) return '0.0000%';
    return numericValue.toFixed(4) + '%';
  };
  
  // Helper function to get CSS class based on performance
  const getPerformanceClass = (value) => {
    return value < 0 ? 'negative-value' : value > 0 ? 'positive-value' : '';
  };
  
  // Extract columns
  const extractColumns = (data) => {
    if (!data || data.length === 0) return [];
    const firstRow = data[0];
    return Object.keys(firstRow).filter(key => key !== 'date');
  };
  
  // Example of fetching data, renaming "Date" -> "date"
  const fetchPerformanceData = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
  
      // Suppose the API returns an array of objects with "Date" key:
      // [ { "Date": "2025-02-11", "Maverick Fund": ... }, ... ]
      // Rename "Date" -> "date"
      const raw = otherdata.value;
      performanceData.value = raw.map(item => ({
        ...item,
        date: item.Date, 
      }));
  
      columns.value = extractColumns(performanceData.value);
    } catch (err) {
      error.value = err.message || 'Failed to fetch performance data';
    } finally {
      loading.value = false;
    }
  };
  
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
  
  const fetchSlippage = () => fetchData('getuserSlippage', otherdata);
  
  // Lifecycle
  onMounted(async () => {
    // Fetch real data from the endpoint
    await fetchSlippage();
    console.log('Slippage response:', otherdata.value);
    
    // Then fetch performance data
    await fetchPerformanceData();
    
    // Set default date range to cover all data
    if (performanceData.value.length > 0) {
      const dateValues = performanceData.value.map(row => parseRowDate(row.date));
      const minDate = new Date(Math.min(...dateValues));
      const maxDate = new Date(Math.max(...dateValues));
      
      // Format for <input type="date">
      startDate.value = `${minDate.getFullYear()}-${String(minDate.getMonth() + 1).padStart(2, '0')}-${String(minDate.getDate()).padStart(2, '0')}`;
      endDate.value = `${maxDate.getFullYear()}-${String(maxDate.getMonth() + 1).padStart(2, '0')}-${String(maxDate.getDate()).padStart(2, '0')}`;
    }
  });
  </script>
  
  <style scoped>
  /* 
    If your sidebar is fixed at ~240px wide, add margin-left so content doesn’t go behind it.
    Adjust as needed for your layout. 
  */
  .admin-container {
    padding: 20px;
    min-height: 100vh;
    background: #f9fafb; 
    box-sizing: border-box;
  }
  
  /* A card-like container for your content */
  .admin-card {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
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
  
  /* Actions section: flex layout with spacing */
  .actions-section {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: center;
    margin-bottom: 20px;
  }
  
  /* Search input styling */
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
  
  /* Date filter container styling */
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
  
  /* No filter button, so we removed that code */
  
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
  
  /* Error message styling */
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
  
  /* Retry button (same styling as filter-button) */
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
  
  /* Scrollable table container with horizontal + vertical scrolling */
  .table-container {
    margin-top: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    max-height: 600px;
    overflow-x: auto;  /* horizontal scroll for wide columns */
    overflow-y: auto;  /* vertical scroll for more rows */
  }
  
  /* Modern table styling with sticky header */
  .admin-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
  }
  
  /* Sticky header */
  .admin-table thead th {
    position: sticky;
    top: 0;
    background-color: #f3f4f6;
    text-align: left;
    font-weight: 600;
    padding: 12px 15px;
    border-bottom: 2px solid #e5e7eb;
    z-index: 1;
  }
  
  .admin-table th,
  .admin-table td {
    white-space: nowrap;
    padding: 12px 15px;
    border-bottom: 1px solid #e5e7eb;
  }
  
  /* Hover effect on rows */
  .admin-table tbody tr:hover {
    background-color: #f9fafb;
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
  </style>
  