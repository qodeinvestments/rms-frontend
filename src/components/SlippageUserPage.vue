<template>
    <div class="admin-container">
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
                  <template v-if="column === 'Date'">
                    Weight Sum
                  </template>
                  <template v-else>
                    {{ formatWeightSum(columnSums[`${column}_weight_sum`] || 0) }}
                  </template>
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
  
        <!-- a-select to choose which users to display on the chart -->
        <a-select
          v-model:value="selectedChartUsers"
          mode="multiple"
          placeholder="Select Users for Chart"
          style="width: 100%; margin-top: 20px;"
          :options="chartUserOptions"
          @change="updateChartSeries"
        />
  
        <!-- Lightweight Chart Container -->
        <div ref="chartContainerRef" class="chart-container"></div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch ,onUnmounted} from 'vue';
  import { createChart } from 'lightweight-charts';
  import { API_BASE_URL, WS_BASE_URL } from '../config/url'
  // ----- State Management -----
  const loading = ref(false);
  const error = ref(null);
  const performanceData = ref([]);
  const otherdata = ref([]);
  const searchQuery = ref('');
  const startDate = ref('');
  const endDate = ref('');
  
  // Sorting state
  const sortColumn = ref(null);
  const sortOrder = ref(null);
  
  // ----- Sample Data -----
  // (In a real scenario, your API returns data with a "Date" key)
  const sampleData = [
    { Date: '11-02-2025', 'Maverick Fund': -5.022643569, 'Kavan Marwadi Prop': -0.11257554 },
    { Date: '13-03-2025', 'Maverick Fund': 0, 'Kavan Marwadi Prop': -0.06686624 },
    { Date: '12-03-2025', 'Maverick Fund': 0, 'Kavan Marwadi Prop': -0.018489654 }
  ];
  
  // ----- Computed Properties -----
  // allColumns: Build header with "Date" first then the other keys (excluding weight columns)
  const allColumns = computed(() => {
    if (performanceData.value.length === 0) return [];
    const columns = ['Date'];
    const nonWeightColumns = Object.keys(performanceData.value[0])
      .filter(key => key !== 'date' && !key.endsWith('weight'));
    return [...columns, ...nonWeightColumns];
  });
  
  // Add this function to your script setup section
const sortByColumn = (column) => {
  // If clicking on the same column, cycle through sort orders: asc -> desc -> null
  if (sortColumn.value === column) {
    if (sortOrder.value === 'asc') {
      sortOrder.value = 'desc';
    } else if (sortOrder.value === 'desc') {
      sortOrder.value = null;
      sortColumn.value = null;
    } else {
      sortOrder.value = 'asc';
    }
  } else {
    // If clicking on a new column, start with ascending order
    sortColumn.value = column;
    sortOrder.value = 'asc';
  }
};



  // columnSums: Calculate sums for both regular and weight columns
  const columnSums = computed(() => {
    const sums = {};
    filteredPerformanceData.value.forEach(row => {
      for (const key in row) {
        if (key === 'date') continue;
        const num = parseFloat(row[key]);
        if (!isNaN(num)) {
          // For regular columns
          if (!key.endsWith('weight')) {
            sums[key] = (sums[key] || 0) + num;
          }
          // For weight columns
          if (key.endsWith('weight')) {
            const baseKey = key.replace('weight', '');
            sums[`${baseKey}_weight_sum`] = (sums[`${baseKey}_weight_sum`] || 0) + num;
          }
        }
      }
    });
    return sums;
  });
  
  // filteredPerformanceData: Filter data by search and date.
  const filteredPerformanceData = computed(() => {
    let filtered = [...performanceData.value];
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      filtered = filtered.filter(row =>
        Object.entries(row).some(([key, val]) =>
          key === 'date'
            ? (row.date || '').toLowerCase().includes(query)
            : val.toString().toLowerCase().includes(query)
        )
      );
    }
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
  
  // sortedFilteredPerformanceData: Apply sorting to filtered data.
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
  
  // ----- a-select for Chart Users -----
  // chartUserOptions: Options for the a-select (all columns except Date).
  const chartUserOptions = computed(() =>
    allColumns.value.filter(col => col !== 'Date').map(col => ({
      value: col,
      label: col,
    }))
  );
  
  // v-model for a-select: which user columns are selected to display in the chart.
  const selectedChartUsers = ref([]);
  
  // ----- Chart Setup -----
  const chartContainerRef = ref(null);
  let chart;
  let seriesMap = {}; // key: user column, value: series object
  
  // A palette of colors to assign to each series.
  const colorPalette = ['#FF6633', '#FF33FF', '#00B3E6', '#E6B333', '#3366E6', '#999966', '#99FF99', '#B34D4D', '#80B300', '#809900'];
  
  // Initialize the chart.
  function initChart() {
    chart = createChart(chartContainerRef.value, {
      width: chartContainerRef.value.clientWidth,
      height: 300,
      layout: {
        backgroundColor: '#ffffff',
        textColor: '#333',
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });
    // Set default: show all users (columns except Date).
    selectedChartUsers.value = chartUserOptions.value.map(option => option.value);
    updateChartSeries();
    updateChartData();
  }
  
  // updateChartSeries: Rebuild seriesMap based on selectedChartUsers.
  function updateChartSeries() {
    // Remove series not selected.
    Object.keys(seriesMap).forEach(key => {
      if (!selectedChartUsers.value.includes(key)) {
        chart.removeSeries(seriesMap[key]);
        delete seriesMap[key];
      }
    });
    // Add series for newly selected users.
    selectedChartUsers.value.forEach((col, index) => {
      if (!seriesMap[col]) {
        const color = colorPalette[index % colorPalette.length];
        seriesMap[col] = chart.addLineSeries({
          title: col,
          color: color,
        });
      }
    });
    updateChartData();
  }
  
  // updateChartData: Update each series with data points from sortedFilteredPerformanceData.
  function updateChartData() {
    const data = sortedFilteredPerformanceData.value;
    // For each selected user column, update its series.
    selectedChartUsers.value.forEach(col => {
      if (seriesMap[col]) {
        let seriesData = data.map(row => ({
          time: row.date, // "YYYY-MM-DD" format is accepted by lightweight-charts.
          value: parseFloat(row[col]) || 0,
        }));
        // Sort data points by time.
        seriesData.sort((a, b) => new Date(a.time) - new Date(b.time));
        seriesMap[col].setData(seriesData);
      }
    });
  }
  
  // Watch the sorted & filtered data to update the chart.
  watch(sortedFilteredPerformanceData, () => {
    if (chart) updateChartData();
  });
  
  // Watch for changes in selectedChartUsers to update chart series.
  watch(selectedChartUsers, () => {
    if (chart) updateChartSeries();
  });
  
  // Update chart width on window resize.
  window.addEventListener('resize', () => {
    if (chart && chartContainerRef.value) {
      chart.applyOptions({ width: chartContainerRef.value.clientWidth });
    }
  });
  
  // ----- Helper Functions -----
  
  // Convert a 'YYYY-MM-DD' string to Date at local midnight.
  function toMidnightLocal(dateStr) {
    const d = new Date(dateStr);
    d.setHours(0, 0, 0, 0);
    return d;
  }
  
  // Parse a row's date string (assumed "YYYY-MM-DD").
  function parseRowDate(dateStr) {
    if (!dateStr) return null;
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    d.setHours(0, 0, 0, 0);
    return d;
  }
  
  // Format date for display ("YYYY-MM-DD" → "DD-MM-YYYY")
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const [year, month, day] = dateStr.split('-');
    return `${day}-${month}-${year}`;
  };
  
  // Format a numeric value as a percentage.
  const formatPercentage = (value) => {
    const numericValue = parseFloat(value);
    if (isNaN(numericValue)) return '0.0000%';
    return numericValue.toFixed(4) + '%';
  };
  
  // Add this new formatting function after formatPercentage
  const formatWeightSum = (value) => {
    const numericValue = parseFloat(value);
    if (isNaN(numericValue)) return '0.0000';
    return numericValue.toFixed(4);
  };
  
  // Return a CSS class based on value.
  const getPerformanceClass = (value) => {
    return value < 0 ? 'negative-value' : value > 0 ? 'positive-value' : '';
  };
  
  // ----- Data Fetching Functions -----
  
  // Fetch performance data: simulate API call and map raw data to use "date" property.
  const fetchPerformanceData = async () => {
    loading.value = true;
    error.value = null;
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      // Uncomment the next line to use sampleData instead of API data:
      // otherdata.value = sampleData;
      const raw = otherdata.value;
      performanceData.value = raw.map(item => {
        const { Date, ...rest } = item; // Remove original "Date"
        return { ...rest, date: Date }; // Use new property "date"
      });
    } catch (err) {
      error.value = err.message || 'Failed to fetch performance data';
      console.error('Error fetching performance data:', err);
    } finally {
      loading.value = false;
    }
  };
  
  const fetchData = async (endpoint, stateRef) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('User not authenticated');
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
  
  // ----- Lifecycle -----
  
  onMounted(async () => {
    document.title = 'Slippage User Page';
    await fetchSlippage();
    console.log('Slippage response:', otherdata.value);
    await fetchPerformanceData();
    if (performanceData.value.length > 0) {
      const dateValues = performanceData.value.map(row => parseRowDate(row.date));
      const minDate = new Date(Math.min(...dateValues));
      const maxDate = new Date(Math.max(...dateValues));
      startDate.value = `${minDate.getFullYear()}-${String(minDate.getMonth() + 1).padStart(2, '0')}-${String(minDate.getDate()).padStart(2, '0')}`;
      endDate.value = `${maxDate.getFullYear()}-${String(maxDate.getMonth() + 1).padStart(2, '0')}-${String(maxDate.getDate()).padStart(2, '0')}`;
    }
    initChart();
  });
  onUnmounted(() => {
    document.title = 'Vite App'

})
  </script>
  
  <style scoped>
  .admin-container {
    padding: 20px;
    min-height: 100vh;
    background: #f9fafb;
    box-sizing: border-box;
  }
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
  .table-container {
    margin-top: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    max-height: 600px;
    overflow-x: auto;
    overflow-y: auto;
  }
  .admin-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
  }
  .admin-table thead .sum-row {
    position: sticky;
    top: 0;
    background-color: #f3f4f6;
    z-index: 2;
    text-align: center;
  }
  .admin-table thead .header-row {
    background-color: #f3f4f6;
    z-index: 1;
    cursor: pointer;
  }
  .admin-table th,
  .admin-table td {
    white-space: nowrap;
    padding: 12px 15px;
    border-bottom: 1px solid #e5e7eb;
    text-align: center;
  }
  .admin-table thead th {
    border-bottom: 2px solid #e5e7eb;
  }
  .admin-table tbody tr:hover {
    background-color: #f9fafb;
  }
  .sortable-header {
    cursor: pointer;
  }
  .chart-container {
    width: 100%;
    height: 300px;
    margin-top: 20px;
  }
  .positive-value {
    color: #16a34a;
    font-weight: 500;
  }
  .negative-value {
    color: #dc2626;
    font-weight: 500;
  }

  /* Freeze (sticky) the first column in both header and body rows */
.admin-table thead th:first-child {
  position: sticky;
  left: 0;
  z-index: 2; /* Higher z-index so it stays above body cells */
  background-color: #f3f4f6; /* Or use your header background color */
}

.admin-table tbody td:first-child {
  position: sticky;
  left: 0;
  z-index: 1;
  background-color: #ffffff; /* Usually match your table background */
}
  </style>
  