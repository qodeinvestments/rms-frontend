<script setup>
import { onMounted, ref, provide, watch, computed } from 'vue'
import { RouterView } from 'vue-router'
import SideBar from './components/SideBar.vue'
import Toast from './components/Toast.vue'
import Login from './components/Login.vue'
import Signup from './components/Signup.vue'
import { API_BASE_URL, WS_BASE_URL } from './config/url'
const sideBarState = ref(false)
const sidebarfeatures = ref([])
const toastConfig = ref({
  show: false,
  message: '',
  type: 'info'
})
const isLoading = ref(true)

const fetchData = async (endpoint, stateRef) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      isLoggedIn.value = false;
      return;
    }
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    
    if (res.status === 401) {
      // Token is invalid or expired
      localStorage.removeItem('access_token');
      isLoggedIn.value = false;
      return;
    }
    
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    if (endpoint === 'sidebar-features') {
      // Use the role and pages directly from the response
      stateRef.value = data;
      console.log('Sidebar features (role and pages):', stateRef.value);
    } else {
      stateRef.value = endpoint === 'getAccounts' ? Object.keys(data) : data || [];
    }
  } catch (err) {
    console.error(`Error fetching ${endpoint}:`, err.message);
    if (err.message.includes('401')) {
      isLoggedIn.value = false;
    }
  }
};

const ChangeSideBarState = (data) => {
  sideBarState.value = data
}

const triggerToast = (message, type = 'info') => {

  // Get current time
  const now = new Date();
  const hour = now.getHours();    // 0-23 (e.g., 15 = 3 PM)
  const minute = now.getMinutes(); // 0-59

  // Check if after 9:00 AM AND before 3:30 PM
  const withinBusinessHours = 
    (hour > 9 || (hour === 9 && minute >= 0)) && 
    (hour < 15 || (hour === 15 && minute < 30));

    console.log(withinBusinessHours,"  is the withinbusinesshours")
  if (withinBusinessHours) {
   
    toastConfig.value = {
      show: true,
      message,
      type
    }
  }



}

const hideToast = () => {
  toastConfig.value.show = false
}


const showloginorSignup = ref(false)
const isLoggedIn = ref(false) // Add a ref to track login state

const toggleForm = () => {
  showloginorSignup.value = !showloginorSignup.value;
}
const checkLoginStatus = async () => {
  try {
    const isValid = await validateToken();
    isLoggedIn.value = isValid;
  } finally {
    isLoading.value = false;
  }
};

const validateToken = async () => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      isLoggedIn.value = false;
      return false;
    }

    const response = await fetch(`${API_BASE_URL}validate-token`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      // Token is invalid or expired
      localStorage.removeItem('access_token');
      isLoggedIn.value = false;
      return false;
    }

    return true;
  } catch (error) {
    console.error('Token validation error:', error);
    localStorage.removeItem('access_token');
    isLoggedIn.value = false;
    return false;
  }
};

const book = ref({})
const past_time_client = ref(0)
const client_latency = ref(0)
const max_client_latency = ref(0)

const handleMessage = (message) => {
  try {
    if (message === undefined) return;
    book.value['time'] = message['time'];

    if (book.value['Pulse_Errors']) {
      for (const key in book.value['Pulse_Errors']) {
        if (book.value['Pulse_Errors'][key].length != message['Pulse_Errors'][key].length) {
          triggerToast('New Error in ' + key, 'error')
        }
      }
    }
    book.value['Pulse_Errors'] = message['Pulse_Errors']

    // Update New_Order_Errors handling
    if (message['New_Order_Errors']) {
      book.value['New_Order_Errors'] = message['New_Order_Errors']
    }

  } catch (error) {
    console.error('Error parsing event data or updating data:', error);
  }
}

const connectToSSE = () => {
  const token = localStorage.getItem('access_token'); // Retrieve the access token
    if (!token ) {
        if(isLoggedIn.value)alert('User not authenticated To Get Errors');
        return;
    }
    
  const socket = new WebSocket(`${WS_BASE_URL}errorLogs`);

  socket.onmessage = (event) => {
    if (event.data === 'ping') {
      socket.send('pong')
    } else {
      const message = JSON.parse(event.data);
      let ar2 = message["time"];
      if (past_time_client.value === 0) past_time_client.value = ar2;
      // if (past_time_client.value != 0) {
      //   let date1 = new Date(past_time_client.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      //   let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
      //   let diffInMs = date2 - date1;
      //   let diffInSeconds = diffInMs / 1000;
      //   client_latency.value = diffInSeconds;
      //   max_client_latency.value = Math.max(max_client_latency.value, client_latency.value)
      //   past_time_client.value = ar2;
      // }

      handleMessage(message)
    }
  }
  socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event.reason)
  }

  socket.onopen = () => {
   
    const authMessage = JSON.stringify({ token });
    socket.send(authMessage);
    console.log('WebSocket connection opened')
  }
  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
};

const fetchSidebarFeatures = () => fetchData('sidebar-features', sidebarfeatures);

onMounted(async () => {
  await checkLoginStatus(); // Make this async
  if (isLoggedIn.value) {
    connectToSSE();
    fetchSidebarFeatures();
  }
})

provide('triggerToast', triggerToast)
provide('book', book.value)
provide('newOrderErrors', computed(() => book.value?.New_Order_Errors || []))



</script>

<template>
  <div class="pageLayout">
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
    </div>
    <template v-else>
      <Signup v-if="!isLoggedIn && showloginorSignup" @toggleForm="toggleForm" />
      <Login v-if="!isLoggedIn && !showloginorSignup" @toggleForm="toggleForm" />

      <SideBar v-if="isLoggedIn" @State="ChangeSideBarState" :sidebarfeatures="sidebarfeatures" class="sideBar" />
      <Toast v-if="toastConfig.show && isLoggedIn" :message="toastConfig.message" :type="toastConfig.type" @close="hideToast" />
     
      <RouterView v-if="isLoggedIn" :class="sideBarState ? 'content' : 'content2'" />
    </template>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');

body {
  margin: 0;
  font-family: "Inter", sans-serif;
  width: 100%;
  height: 100%;
}

.pageLayout {
  display: flex;
  height: 100%;
}

.sideBar {
  position: fixed;
  width: fit-content;
  height: 100%;
}

.content {
  margin-left: 100px;
  width: calc(100% - 100px);
  height: 100%;
  transition: all 0.3s;
}

.content2 {
  margin-left: 250px;
  width: calc(100% - 250px);
  height: 100%;
  transition: all 0.3s;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background-color: #ffffff;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>