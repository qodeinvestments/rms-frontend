



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


  const fetchData = async (endpoint, stateRef) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("Authentication required. Please log in again.");
  
      const response = await fetch(
        `https://production2.swancapital.in/get_open_trades`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
  
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        router.push("/login");
        throw new Error("Session expired. Please log in again.");
      }
  
      if (!response.ok) {
        const errorMessage = await response.text();
        throw new Error(`Error: ${errorMessage}`);
      }
  
      const jsonData = await response.json();


      const data = jsonData;
      signal_book_data.value = Object.values(data)
      uids.value = [...new Set(signal_book_data.value.map(item => item.uid))];
      basket.value = [...new Set(signal_book_data.value.map(item => item.uid.split('_')[0]))];
     
      } catch (err) {
      error.value = err.message;
      console.error(`Error fetching ${endpoint}:`, err.message);
      throw err;
    }
  };

  

  
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

          <div class="filter-controls">
              <!-- Basket multi-select component -->
              <a-select v-model:value="selectedBasketItems" mode="multiple" placeholder="Select Basket Items"
                  style="width: 100%; margin-bottom: 10px;"
                  :options="filteredBasketOptions.map(item => ({ value: item }))"></a-select>
  
              <!-- UID multi-select component -->
              <a-select v-model:value="selectedUids" mode="multiple" placeholder="Select UIDs" style="width: 100%; margin-bottom: 10px;"
                  :options="filteredOptions.map(item => ({ value: item }))"></a-select>
              

          </div>
  
          <div class="my-8" v-if="filteredSignalBookData.length">
              <!-- <p class="table-heading">Signal Book</p> -->
              <TanStackTestTable title="Open Trades" :data="filteredSignalBookData" :columns="columns" :hasColor="[]"
                  :navigateTo="[]" :showPagination=true :showPin="true"/>
          </div>
      </div>
  </template>
  
  <style scoped>
  .a-select {
      margin-top: 20px;
      margin-bottom: 20px;
  }
  
  .pageContainer {
      height: 100%;
      display: flex;
      flex-direction: column;
  }
  
  
  .filter-controls {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 20px;
  }
  
  /* Custom button styling without hover effects and background colors */
  .custom-checker-btn {
      align-self: flex-start;
      padding: 8px 16px;
      border: 1px solid #d9d9d9;
      border-radius: 2px;
      cursor: pointer;
      transition: border-color 0.3s;
      background: none;
      font-size: 14px;
      color: rgba(0, 0, 0, 0.85);
  }
  
  .custom-checker-btn:focus {
      outline: none;
  }
  
  /* Simple border change to indicate active state */
  .custom-checker-btn:global(.active), 
  .custom-checker-btn:global([aria-pressed="true"]) {
      border-color: #1890ff;
      color: #1890ff;
  }
  
  .latencyvalue {
      font-weight: bold;
  }
  
  .LatencyTable {
      display: flex;
      width: 100;
      align-items: flex-end;
      justify-content: flex-end;
      padding: 20px;
      flex-direction: column;
  }
  
  .table-heading {
      font-size: 22px;
      font-weight: 600;
      margin-left: 30px;
  }
  
  html {
      /* font-family: poppins; */
      font-size: 14px;
  }
  </style>