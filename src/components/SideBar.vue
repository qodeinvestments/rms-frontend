<template>
  <div class="container">
    <div class="sidebar " :class="sidebarState ? 'active' : ''" ref="targetElement">
      <div class="menu-btn" @click="toggleSideBar()">
        <i class="ph-bold ph-caret-left"></i>
      </div>
      <div class="head">
        <div class="user-img">
          <img src="../assets/swan_capital.jpeg" alt="">
        </div>
        <!-- <div class="user-details">
          <p class="name"> Swan Capital</p>
        </div> -->
      </div>
      <div class="nav">
        <div class="menu">
          <p class="title" :class="sidebarState === true ? 'aligncenter' : ''">main</p>
          <ul>
            <li :class="selected == 'Dashboard' ? 'active' : ''" @click="changeSelected('Dashboard')">
              <a href="#">
                <i class="icon ph-bold ph-house-simple"></i>
                <span class="text">Dashboard</span>
              </a>
            </li>
            <!-- <li>
              <a href="#" :class="selected == 'Audience' ? 'active' : ''" @click="changeSelected('Audience')">
                <i class="icon ph-bold ph-user"></i>
                <span class="text">Audience</span>
                <i class="arrow ph-bold ph-caret-down"></i>
              </a>
              <ul class="sub-menu" v-show="selected === 'Audience' && showoptions">
                <li :class="selectedsubCat == 'Users' ? 'active' : ''" @click="changeSelectedSubCat('Users')">
                  <a href="#">
                    <span class="text">Users</span>
                  </a>
                </li>
                <li :class="selectedsubCat == 'Subscribers' ? 'active' : ''"
                  @click="changeSelectedSubCat('Subscribers')">
                  <a href="#">
                    <span class="text">Subscribers</span>
                  </a>
                </li>
              </ul>
            </li> -->
            <li :class="selected == 'Errors' ? 'active' : ''" @click="changeSelected('Errors')">
              <a href="#">
                <i class="icon ph-bold ph-file-text"></i>
                <span class="text">Errors</span>
              </a>
            </li>
            <li :class="selected == 'KeyDBLogs' ? 'active' : ''" @click="changeSelected('KeyDBLogs')">
              <a href="#">
                <i class="icon ph-bold ph-calendar-blank"></i>
                <span class="text">KeyDBLogs</span>
              </a>
            </li>
            <li :class="selected == 'DataVisualizer' ? 'active' : ''" @click="changeSelected('DataVisualizer')">
              <a href="#">
                <i class="icon ph-bold ph-calendar-blank"></i>
                <span class="text">Data Visualizer</span>
              </a>
            </li>
            <li :class="selected == 'SignalBook' ? 'active' : ''" @click="changeSelected('SignalBook')">
              <a href="#">
                <i class="icon ph-bold ph-calendar-blank"></i>
                <span class="text">SignalBook</span>
              </a>
            </li>
            <li :class="selected == 'ServerData' ? 'active' : ''" @click="changeSelected('ServerData')">
              <a href="#">
                <i class="icon ph-bold ph-calendar-blank"></i>
                <span class="text">Server Data</span>
              </a>
            </li>
            <!-- <li>
              <a href="#" :class="selected == 'Income' ? 'active' : ''" @click="changeSelected('Income')">
                <i class="icon ph-bold ph-chart-bar"></i>
                <span class="text">Income</span>
                <i class="arrow ph-bold ph-caret-down"></i>
              </a>
              <ul class="sub-menu" v-show="selected === 'Income' && showoptions">
                <li :class="selectedsubCat == 'Earnings' ? 'active' : ''" @click="changeSelectedSubCat('Earnings')">
                  <a href="#">
                    <span class="text">Earnings</span>
                  </a>
                </li>
                <li :class="selectedsubCat == 'Funds' ? 'active' : ''" @click="changeSelectedSubCat('Funds')">
                  <a href="#">
                    <span class="text">Funds</span>
                  </a>
                </li>
                <li :class="selectedsubCat == 'Declines' ? 'active' : ''" @click="changeSelectedSubCat('Declines')">
                  <a href="#">
                    <span class="text">Declines</span>
                  </a>
                </li>
                <li :class="selectedsubCat == 'Payouts' ? 'active' : ''" @click="changeSelectedSubCat('Payouts')">
                  <a href="#">
                    <span class="text">Payouts</span>
                  </a>
                </li>
              </ul>
            </li> -->

          </ul>
        </div>
        <div class="menu">
          <p class="title">Settings</p>
          <ul>
            <li>
              <a href="#">
                <i class="icon ph-bold ph-gear"></i>
                <span class="text">Settings</span>
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div class="menu">
        <p class="title">Account</p>
        <ul>
          <li>
            <a href="#">
              <i class="icon ph-bold ph-info"></i>
              <span class="text">Help</span>
            </a>
          </li>
          <li>
            <a href="#">
              <i class="icon ph-bold ph-sign-out"></i>
              <span class="text">Logout</span>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';

export default {
  data() {
    return {
      sidebarState: false,
      selected: '',
      selectedsubCat: '',
      showoptions: false,
      togglesubCategory: ['Audience', 'Income'],
      navigateMap: {
        'Dashboard': '/',
        'Errors': '/errors',
        "KeyDBLogs": '/keydblogs',
        'DataVisualizer': '/visualize',
        'SignalBook': '/signalbook',
        'ServerData': '/serverData',
      }

    }
  },
  methods: {
    toggleSideBar() {
      this.sidebarState = !this.sidebarState;
      this.showoptions = false;
      this.$emit("State", this.sidebarState);
    },
    changeSelected(val) {
      if (this.selected === val) this.showoptions = !this.showoptions;
      else {
        this.showoptions = true;
        this.selectedsubCat = '';
      }
      this.selected = val;
      this.$router.push(this.navigateMap[val]);

    },
    changeSelectedSubCat(val) {
      this.selectedsubCat = val;
      if (this.sidebarState) this.showoptions = false;
    },
    handleClickOutside(event) {

      const targetElement = this.$refs.targetElement;
      if (targetElement === null) {
        this.selected = '';
      }
      else if (!targetElement.contains(event.target)) {
        console.log("clicked outside")

        this.selected = '';
      }
      else console.log("clicked inside")
    },
  },
  mounted() {
    document.addEventListener("click", this.handleClickOutside);
  },

  beforeDestroy() {
    document.removeEventListener("click", this.handleClickOutside);
  },

}
</script>


<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
}



.aligncenter {
  text-align: center;
}

.container {
  width: 100%;
  min-height: 100vh;
  height: 100%;
  z-index: 1000;
}

.sidebar {
  position: relative;
  width: 256px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: #4E47E5;
  padding: 24px;
  /* border-radius: 30px; */
  transition: all 0.3s;
}

.sidebar .head {
  display: flex;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f6f6f6;
  align-items: center;
  justify-content: center;
}

.user-img {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  overflow: hidden;
}

.user-img img {
  width: 100%;
  object-fit: cover;
}

.user-details .title,
.menu .title {
  font-size: 10px;
  font-weight: 500;
  color: #fff;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.user-details {
  display: flex;
  justify-content: center;
  align-items: center;
}

.user-details .name {
  font-size: 14px;
  font-weight: 500;
}

.nav {
  flex: 1;
}

.menu ul li {
  position: relative;
  list-style: none;
  margin-bottom: 5px;
}

.menu ul li a {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  text-decoration: none;
  padding: 12px 8px;
  border-radius: 8px;
  transition: all 0.3s;
}

.menu ul li>a:hover,
.menu ul li.active>a {
  color: #000;
  background-color: #fff;
  ;
}

.menu ul li .icon {
  font-size: 20px;
}

.menu ul li .text {
  flex: 1;
}

.menu ul li .arrow {
  font-size: 14px;
  transition: all 0.3s;
}

.menu ul li.active .arrow {
  transform: rotate(180deg);
}

.menu .sub-menu {
  /* display: none; */
  margin-left: 20px;
  padding-left: 20px;
  padding-top: 5px;
  border-left: 1px solid #f6f6f6;
}

.menu .sub-menu li a {
  padding: 10px 8px;
  font-size: 12px;
}

.menu:not(:last-child) {
  padding-bottom: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #f6f6f6;
}

.menu-btn {
  position: absolute;
  right: -14px;
  top: 3.5%;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  border: 2px solid #f6f6f6;
  background-color: #4E47E5;
}

.menu-btn:hover i {
  color: #fff;
}

.menu-btn i {
  transition: all 0.3s;
}

.sidebar.active {
  width: 92px;
}

.sidebar.active .menu-btn i {
  transform: rotate(180deg);
}

.sidebar.active .user-details {
  display: none;
}

.sidebar.active .menu.title {
  text-align: center;
}

.sidebar.active .menu ul li .arrow {
  display: none;
}

.sidebar.active .menu>ul>li>a {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar.active .menu>ul>li>a .text {
  position: absolute;
  left: 70px;
  top: 50%;
  transform: translateY(-50%);
  padding: 10px;
  border-radius: 4px;
  color: #fff;
  background-color: #000;
  opacity: 0;
  visibility: hidden;
}

.sidebar.active .menu>ul>li>a .text::after {
  content: "";
  position: absolute;
  left: -5px;
  top: 20%;
  width: 20px;
  height: 20px;
  border-radius: 2px;
  background-color: #000;
  transform: rotate(45deg);
  z-index: -1;
}

.sidebar.active .menu>ul>li>a:hover .text {
  left: 50px;
  opacity: 1;
  visibility: visible;

  transition: all 0.3s;
}

.sidebar.active .menu .sub-menu {
  position: absolute;
  top: 0;
  left: 20px;
  width: 200px;
  border-radius: 20px;
  padding: 10px 20px;
  border: 1px solid #f6f6f6;
  background-color: #4E47E5;
  box-shadow: 0px 10px 8px rgba(0, 0, 0, 0.1);
}
</style>
