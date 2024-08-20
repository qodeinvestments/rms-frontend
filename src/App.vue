<script>
import { provide } from 'vue'
import { RouterView } from 'vue-router'
import SideBar from './components/SideBar.vue';
import Toast from './components/Toast.vue';

export default {
  components: {
    SideBar,
    Toast,
    RouterView
  },
  data() {
    return {
      sideBarState: false,
      showToast: false,
      toastMessage: '',
      toastType: 'info'
    }
  },
  methods: {
    ChangeSideBarState(data) {
      this.sideBarState = data;
    },
    triggerToast(message, type = 'info') {
      this.toastMessage = message;
      this.toastType = type;
      this.showToast = true;
    }

  },
  created() {
    provide('triggerToast', this.triggerToast);
  }
}
</script>

<template>
  <div class="pageLayout">
    <SideBar @State="ChangeSideBarState($event)" class="sideBar" />
    <Toast v-if="showToast" :message="toastMessage" :type="toastType" @close="showToast = false" />
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