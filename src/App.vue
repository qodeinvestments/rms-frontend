<script>
import { RouterView } from 'vue-router'
import SideBar from './components/SideBar.vue';


export default {
  components: {
    SideBar
  },
  data() {
    return {
      sideBarState: false

    }
  },
  methods: {
    ChangeSideBarState(data) {
      this.sideBarState = data;
    }
  },

}
</script>


<template>
  <div class="pageLayout">
    <SideBar @State="ChangeSideBarState($event)" class="sideBar" />
    <router-view :class="sideBarState ? 'content' : 'content2'" />
  </div>
</template>

<style scoped>
body {
  margin: 0;
  /* Ensure body has no margin */
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
  /* Adjust the width as needed */
  height: 100%;
  /* Adjust the background color as needed */
}

.content {
  margin-left: 100px;
  /* Same as sideBar width */
  width: calc(100% - 100px);
  /* Adjust to fill the remaining space */
  height: 100%;
  transition: all 0.3s;
}

.content2 {
  margin-left: 250px;
  /* Same as sideBar width */
  width: calc(100% - 250px);
  /* Adjust to fill the remaining space */
  height: 100%;
  transition: all 0.3s;
}
</style>
