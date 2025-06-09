<!-- App.vue -->
<script setup>
import { onMounted, ref ,onUnmounted} from 'vue';
import Histogram from './Histogram.vue';
import OHLCChart from './OHLCCHART.vue';
import TanStackTestTable from './TanStackTestTable.vue'
import { columns } from '../components/TableVariables/DataVisualizer.js'; 

const WS7L = ref([]);
const WS8L = ref([]);
const signal_delay = ref([]);
const chartData = ref([]);
const isLoading = ref(false);
const error = ref(null);

const fetchClientDetails = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await fetch('https://production2.swancapital.in/lagsData');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    
    WS7L.value = data.WS7L;
    WS8L.value = data.WS8L;
    signal_delay.value = data.signal_delay;
  } catch (error) {
    console.error('Error fetching client details:', error);
    error.value = 'Failed to fetch lag data. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

const postData = async (endpoint, payload, stateRef) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    const response = await fetch(`https://production2.swancapital.in/${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error posting to ${endpoint}: ${errorMessage}`);
    }

    const data = await response.json();
    if (stateRef) {
      stateRef.value = data || [];
    }
    
    return data;
  } catch (err) {
    error.value = err.message;
    console.error(`Error posting to ${endpoint}:`, err.message);
    throw err;
  }
};

const chartDatafetch = (data) => postData('Psar', data, chartData);

const fetchDiffData = (data) => {
  chartDatafetch(data);
}

onMounted(() => {
  document.title = 'Visualizer';
  fetchClientDetails();
  chartDatafetch({symbol: 'NIFTY', timeframe: '5m', indicators: []});
});
onUnmounted(() => {
    document.title = 'Vite App'

})
</script>

<template>
    <div class="dashboard-container">
      <header class="dashboard-header">
        <h1 class="dashboard-title">Market Analysis Dashboard</h1>
        <button @click="fetchClientDetails" class="refresh-button" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          <span v-else>Refresh Data</span>
        </button>
      </header>
  
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
  
      <div class="dashboard-content">
       
  
        <div v-if="signal_delay.length > 0" class="dashboard-card">
          <h2 class="card-title">Signal Delay</h2>
          <Histogram :dataArray="signal_delay" />
        </div>
  
        <div class="dashboard-card">
          <OHLCChart 
            :data="chartData['Data']" 
            :verticalLineTime="chartData['verticalLineTime']"
            :title="chartData['title']"
            @submit-config="fetchDiffData($event)" 
          />
        </div>
        <div class="my-8" v-if="chartData['table']">
          
            <TanStackTestTable title="PsarTable" :data="chartData['table']" :columns="columns" :hasColor="[]"
                :navigateTo="[]" :showPagination=true :showPin="true"/>
        </div>
      </div>
    </div>
  </template>
  
  <style scoped>
  .dashboard-container {
    min-height: 100vh;
    background-color: #f8fafc;
    padding: 2rem;
  }
  
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  
  .dashboard-title {
    font-size: 1.875rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
  }
  
  .dashboard-content {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .dashboard-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    padding: 1.5rem;
    width: 100%;
    transition: transform 0.2s ease;
  }
  
  .dashboard-card:hover {
    transform: translateY(-2px);
  }
  
  .refresh-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    background-color: #2962FF;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 120px;
  }
  
  .refresh-button:hover {
    background-color: #1E4BD8;
  }
  
  .refresh-button:disabled {
    background-color: #94A3B8;
    cursor: not-allowed;
  }
  
  .card-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 1rem 0;
  }
  
  .error-message {
    background-color: #FEE2E2;
    border: 1px solid #FCA5A5;
    color: #DC2626;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }
  
  .loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #ffffff;
    border-top: 2px solid transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  @media (max-width: 1024px) {
    .dashboard-container {
      padding: 1rem;
    }
  
    .dashboard-title {
      font-size: 1.5rem;
    }
  }
  
  @media (max-width: 640px) {
    .dashboard-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }
  
    .refresh-button {
      width: 100%;
    }
  
    .dashboard-container {
      padding: 0.75rem;
    }
  
    .dashboard-card {
      padding: 1rem;
    }
  }
  
  /* Font settings */
  html {
    font-family: 'Poppins', system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  ::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }
  
  ::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }
  </style>