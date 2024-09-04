<script setup>
import { onMounted, ref, provide, watch } from 'vue'
import { RouterView } from 'vue-router'
import SideBar from './components/SideBar.vue'
import Toast from './components/Toast.vue'

const sideBarState = ref(false)
const toastConfig = ref({
  show: false,
  message: '',
  type: 'info'
})

const ChangeSideBarState = (data) => {
  sideBarState.value = data
}

const triggerToast = (message, type = 'info') => {
  toastConfig.value = {
    show: true,
    message,
    type
  }
}

const hideToast = () => {
  toastConfig.value.show = false
}

const book = ref({})
const past_time_client = ref(0)
const client_latency = ref(0)
const max_client_latency = ref(0)

const handleMessage = (message) => {
  try {
    if (message === undefined) return;
    book.value['time'] = message["time"]

    if (book.value['Order_Errors']) {
      for (const key in book.value['Order_Errors']) {
        if (book.value['Order_Errors'][key].length != message['Order_Errors'][key].length) {
          triggerToast('New Error in Order', 'error')
        }
      }
    }

    book.value['Order_Errors'] = message['Order_Errors']

    if (book.value['Pulse_Errors']) {
      for (const key in book.value['Pulse_Errors']) {
        if (book.value['Pulse_Errors'][key].length != message['Pulse_Errors'][key].length) {
          triggerToast('New Error in ' + key, 'error')
        }
      }

    }
    book.value['Pulse_Errors'] = message['Pulse_Errors']

  } catch (error) {
    console.error('Error parsing event data or updating data:', error);
  }
}

const connectToSSE = () => {
  const socket = new WebSocket('wss://production.swancapital.in/errorLogs');

  socket.onmessage = (event) => {
    if (event.data === 'ping') {
      socket.send('pong')
    } else {
      const message = JSON.parse(event.data);
      let ar2 = message["time"];
      if (past_time_client.value === 0) past_time_client.value = ar2;
      if (past_time_client.value != 0) {
        let date1 = new Date(past_time_client.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
        let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
        let diffInMs = date2 - date1;
        let diffInSeconds = diffInMs / 1000;
        client_latency.value = diffInSeconds;
        max_client_latency.value = Math.max(max_client_latency.value, client_latency.value)
        past_time_client.value = ar2;
      }

      handleMessage(message)
    }
  }
  socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event.reason)
  }

  socket.onopen = () => {
    console.log('WebSocket connection opened')
  }
  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
};

onMounted(() => {
  connectToSSE();
})

provide('triggerToast', triggerToast)
provide('book', book.value)
</script>

<template>
  <div class="pageLayout">
    <SideBar @State="ChangeSideBarState" class="sideBar" />
    <Toast v-if="toastConfig.show" :message="toastConfig.message" :type="toastConfig.type" @close="hideToast" />
    <RouterView :class="sideBarState ? 'content' : 'content2'" />
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
</style>