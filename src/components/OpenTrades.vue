



  <script setup>
  import { onMounted, onUnmounted, computed } from 'vue'
  import {
      FlexRender,
      getCoreRowModel,
      useVueTable,
      createColumnHelper,
  } from '@tanstack/vue-table'
  
  import { MyEnum } from '../Enums/Prefix.js';
  import { ref, watch } from 'vue'
  import TanStackTestTable from './TanStackTestTable.vue'
  import { columns } from '../components/TableVariables/OpenTrades.js'; 
  
  
  const signal_book_data = ref([])
  const uids = ref([])
  const basket = ref([])
  const isLoading = ref(false)
  const columnHelper = createColumnHelper()
 
  const past_time = ref(0)
  const selected_uid = ref('')
  
  // Add filter for checker status

  const error=ref("");
  const selectedUids = ref([]);
  const selectedBasketItems = ref([]);
  
  const filteredBasketOptions = computed(() => basket.value.filter(o => !selectedBasketItems.value.includes(o)));
  
  const filteredUids = computed(() => {
      if (selectedBasketItems.value.length === 0) {
          return uids.value;
      }
      return uids.value.filter(uid => selectedBasketItems.value.includes(uid.split('_')[0]));
  });
  
  const filteredOptions = computed(() => filteredUids.value.filter(o => !selectedUids.value.includes(o)));
  
  // Updated computed property for filtered signal_book_data with checker filter
  const filteredSignalBookData = computed(() => {
      let filteredData = signal_book_data.value;
    
      // Apply existing filters
      if (selectedUids.value.length > 0 || selectedBasketItems.value.length > 0) {
          filteredData = filteredData.filter(item => {
              const basketMatch = selectedBasketItems.value.length === 0 || selectedBasketItems.value.includes(item.uid.split('_')[0]);
              const uidMatch = selectedUids.value.length === 0 || selectedUids.value.includes(item.uid);
              return basketMatch && uidMatch;
          });
      }
      
      return filteredData;
  });


  const fetchData = async () => {
    try {
        isLoading.value = true
        error.value = ""
        const token = localStorage.getItem("access_token")
        if (!token) throw new Error("Authentication required. Please log in again.")

        const response = await fetch(
            `https://production2.swancapital.in/get_open_trades`,
            {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            }
        )

        if (response.status === 401) {
            localStorage.removeItem("access_token")
            router.push("/login")
            throw new Error("Session expired. Please log in again.")
        }

        if (!response.ok) {
            const errorMessage = await response.text()
            throw new Error(`Error: ${errorMessage}`)
        }

        const jsonData = await response.json()
        signal_book_data.value = Object.values(jsonData)
        uids.value = [...new Set(signal_book_data.value.map(item => item.uid))]
        basket.value = [...new Set(signal_book_data.value.map(item => item.uid.split('_')[0]))]
    } catch (err) {
        error.value = err.message
        console.error('Error fetching data:', err.message)
    } finally {
        isLoading.value = false
    }
}
  

  
  const showOnPage = ref('Positions')
  
  onMounted(() => {
    fetchData();
  })
  
  onUnmounted(() => {
  
  })
  
  // Watch for changes in selectedBasketItems
  watch(selectedBasketItems, (newSelectedBasketItems) => {
      console.log('Selected Basket items changed:', newSelectedBasketItems);
      // Reset UID selection when basket selection changes
      selectedUids.value = [];
  });
  

  </script>
  
  
  <template>
      <div class="px-8 py-8 pageContainer">
        <!-- Loading Overlay -->
        <div v-if="isLoading" class="loading-overlay">
            <div class="loading-content">
                <div class="spinner"></div>
                <p>Loading data...</p>
            </div>
        </div>


        <!-- Error State -->
        <div v-if="error" class="error">
            {{ error }}
            <button @click="fetchData" class="retry-button">
                Retry
            </button>
        </div>



         
  
          <div class="my-8" v-if="filteredSignalBookData.length">
            <div class="filter-controls">
              <!-- Basket multi-select component -->
              <a-select v-model:value="selectedBasketItems" mode="multiple" placeholder="Select Basket Items"
                  style="width: 100%; margin-bottom: 10px;"
                  :options="filteredBasketOptions.map(item => ({ value: item }))"></a-select>
  
              <!-- UID multi-select component -->
              <a-select v-model:value="selectedUids" mode="multiple" placeholder="Select UIDs" style="width: 100%; margin-bottom: 10px;"
                  :options="filteredOptions.map(item => ({ value: item }))"></a-select>
              

          </div>
              <!-- <p class="table-heading">Signal Book</p> -->
              <TanStackTestTable title="Overnight Trades" :data="filteredSignalBookData" :columns="columns" :hasColor="[]"
                  :navigateTo="[]" :showPagination=true :showPin="true"/>
          </div>
          <div v-else-if="!isLoading" class="no-data">
            No trades available
        </div>
      </div>
  </template>
  
<style scoped>
.container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
    min-height: 400px;
}

.filters-container {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}

.filter-section {
    flex: 1;
}

.filter-section h3 {
    margin-bottom: 8px;
    font-size: 16px;
    color: #374151;
}

.filter-select {
    width: 100%;
    padding: 8px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    min-height: 100px;
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.loading-content {
    text-align: center;
}

.loading-content p {
    margin-top: 1rem;
    color: #4b5563;
    font-size: 1.1rem;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 5px solid #f3f3f3;
    border-top: 5px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error {
    background-color: #fee2e2;
    border: 1px solid #ef4444;
    color: #dc2626;
    padding: 12px;
    border-radius: 6px;
    margin: 10px 0;
}

.retry-button {
    background-color: #dc2626;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    margin-top: 10px;
    cursor: pointer;
}

.retry-button:hover {
    background-color: #b91c1c;
}

.data-container {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.no-data {
    text-align: center;
    color: #666;
    padding: 20px;
}

/* Loading overlay animations */
.loading-overlay {
    animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.loading-content p {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
</style>