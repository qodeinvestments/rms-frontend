<template>
  <div class="container" v-if="sidebarfeatures['pages']">
    <div class="sidebar " :class="sidebarState ? 'active' : ''" ref="targetElement">
      <div class="menu-btn" @click="toggleSideBar()">
        <i class="fas fa-chevron-left"></i>
      </div>
      <div class="sidebar-content">
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
              <li :class="selected=='Dashboard'?'active':''" @click="changeSelected('Dashboard')" v-if="sidebarfeatures['pages'].includes('Dashboard')">
                <a href="#">
                  <i class="icon fas fa-home"></i>
                  <span class="text">Dashboard</span>
                </a>
              </li>
              <li :class="[
                selected === 'Errors' ? 'active' : '',
                hasNewOrderErrors ? 'has-errors' : ''
              ]" @click="changeSelected('Errors')" v-if="sidebarfeatures['pages'].includes('Errors')">
                <a href="#">
                  <i class="icon fas fa-exclamation-triangle"></i>
                  <span class="text">Errors</span>
                  <span v-if="hasNewOrderErrors" class="error-indicator"></span>
                </a>
              </li>
              <li :class="selected == 'KeyDBLogs' ? 'active' : ''" @click="changeSelected('KeyDBLogs')" v-if="sidebarfeatures['pages'].includes('KeyDBLogs')">
                <a href="#">
                  <i class="icon fas fa-database"></i>
                  <span class="text">KeyDBLogs</span>
                </a>
              </li>
              <li :class="selected == 'DataVisualizer' ? 'active' : ''" @click="changeSelected('DataVisualizer')" v-if="sidebarfeatures['pages'].includes('DataVisualizer')">
                <a href="#">
                  <i class="icon fas fa-chart-bar"></i>
                  <span class="text">Data Visualizer</span>
                </a>
              </li>
              <li :class="selected == 'SignalBook' ? 'active' : ''" @click="changeSelected('SignalBook')" v-if="sidebarfeatures['pages'].includes('SignalBook')">
                <a href="#">
                  <i class="icon fas fa-book-open"></i>
                  <span class="text">SignalBook</span>
                </a>
              </li>
              <li :class="selected == 'ServerData' ? 'active' : ''" @click="changeSelected('ServerData')" v-if="sidebarfeatures['pages'].includes('ServerData')">
                <a href="#">
                  <i class="icon fas fa-server"></i>
                  <span class="text">Server Data</span>
                </a>
              </li>
              <li :class="selected == 'LivePositions' ? 'active' : ''" @click="changeSelected('LivePositions')" v-if="sidebarfeatures['pages'].includes('LivePositions')">
                <a href="#">
                  <i class="icon fas fa-chart-line"></i>
                  <span class="text">Live Positions </span>
                </a>
              </li>
              <li :class="selected == 'OpenTrades' ? 'active' : ''" @click="changeSelected('OpenTrades')" v-if="sidebarfeatures['pages'].includes('OpenTrades')">
                <a href="#">
                  <i class="icon fas fa-exchange-alt"></i>
                  <span class="text">Overnight Trades </span>
                </a>
              </li>
              <li :class="selected == 'SlippageUserPage' ? 'active' : ''" @click="changeSelected('SlippageUserPage')" v-if="sidebarfeatures['pages'].includes('SlippageUserPage')">
                <a href="#">
                  <i class="icon fas fa-percent"></i>
                  <span class="text">Slippage User Page </span>
                </a>
              </li>
              <li :class="selected == 'UserStrategyVar' ? 'active' : ''" @click="changeSelected('UserStrategyVar')" v-if="sidebarfeatures['pages'].includes('UserStrategyVar')">
                <a href="#">
                  <i class="icon fas fa-calculator"></i>
                  <span class="text"> User Strategy Var </span>
                </a>
              </li>
              <li :class="selected == 'DailyLogsTable' ? 'active' : ''" @click="changeSelected('DailyLogsTable')" v-if="sidebarfeatures['pages'].includes('DailyLogsTable')">
                <a href="#">
                  <i class="icon fas fa-calendar-day"></i>
                  <span class="text"> Daily Logs Table </span>
                </a>
              </li>
              <li :class="selected == ' VarSimulator' ? 'active' : ''" @click="changeSelected('VarSimulator')" v-if="sidebarfeatures['pages'].includes('VarSimulator')">
                <a href="#">
                  <i class="icon fas fa-sliders-h"></i>
                  <span class="text">  Var Simulator </span>
                </a>
              </li>
              <li :class="selected == 'ClientPage' ? 'active' : ''" @click="changeSelected('ClientPage')" v-if="sidebarfeatures['pages'].includes('ClientPage')">
                <a href="#">
                  <i class="icon fas fa-user-friends"></i>
                  <span class="text">  PNL Summary </span>
                </a>
              </li>
              
            </ul>
          </div>
          <div  v-if="sidebarfeatures['role']=='Admin' || sidebarfeatures['role']=='Super Admin'"
          
          class="menu">
            <p class="title">Settings</p>
            <ul>
              <li 
               v-if="sidebarfeatures['pages'].includes('Settings')"
              >
                <a href="#">
                  <i class="icon fas fa-cog"></i>
                  <span class="text">Settings</span>
                </a>
              </li>
              <li
              v-if="sidebarfeatures['pages'].includes('AdminPanel')"
              :class="selected == 'AdminPanel' ? 'active' : ''" @click="changeSelected('AdminPanel')">
                <a href="#">
                  <i class="icon fas fa-user-shield"></i>
                  <span class="text">Admin Panel</span>
                </a>
              </li>
              <li 
               v-if="sidebarfeatures['pages'].includes('MarginUpdate')"
              :class="selected == 'MarginUpdate' ? 'active' : ''" @click="changeSelected('MarginUpdate')">
                <a href="#">
                  <i class="icon fas fa-balance-scale"></i>
                  <span class="text">Margin Update</span>
                </a>
              </li>
              <li 
                v-if="sidebarfeatures['pages'].includes('PositionManagement')"
                :class="selected == 'PositionManagement' ? 'active' : ''"
                @click="changeSelected('PositionManagement')"
              >
                <a href="#">
                  <i class="icon fas fa-chart-line"></i>
                  <span class="text">Position Management</span>
                </a>
              </li>
              <li 
                v-if="sidebarfeatures['pages'].includes('ServerDrive')"
                :class="selected == 'ServerDrive' ? 'active' : ''"
                @click="changeSelected('ServerDrive')"
              >
                <a href="#">
                  <i class="icon fas fa-chart-line"></i>
                  <span class="text">Server Drive</span>
                </a>
              </li>

              <li 
                v-if="sidebarfeatures['pages'].includes('MarketHoliday')"
                :class="selected == 'MarketHoliday' ? 'active' : ''"
                @click="changeSelected('MarketHoliday')"
              >
                <a href="#">
                  <i class="icon fas fa-calendar-xmark"></i>
                  <span class="text">Market Holidays</span>
                </a>
              </li>
            </ul>
          </div>
        
        </div>
        <div class="menu account-menu">
          <p class="title">Account</p>
          <ul>
            <li>
              <a href="#">
                <i class="icon fas fa-question-circle"></i>
                <span class="text">Help</span>
              </a>
            </li>
            <li>
              <a href="#" @click="logout">
                <i class="icon fas fa-sign-out-alt"></i>
                <span class="text">Logout</span>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
import { inject, computed } from 'vue';

export default {
  props: {
    sidebarfeatures: {
      type: Object,
      required: true,
      default: () => ({
        pages: [],
        role: ''
      })
    }
  },
  setup() {
    const newOrderErrors = inject('newOrderErrors')
    
    const hasNewOrderErrors = computed(() => {
      return newOrderErrors.value && newOrderErrors.value.length > 0
    })

    return {
      hasNewOrderErrors
    }
  },
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
        'AdminPanel': '/adminPanel',
        'MarginUpdate':'/marginUpdate',
        'PositionManagement':'/positionmanagement',
        'MarketHoliday':'/market-holidays',
        'LivePositions': '/livepositions',
        'OpenTrades':'/opentrades',
        'SlippageUserPage':'/slippageUserPage',
        'UserStrategyVar':'/userstrategyvar',
        'DailyLogsTable':'/dailylogs',
        'VarSimulator':'/varsimulator',
        'ClientPage':'/clientpage',
        'ServerDrive':'/server-drive'
      }

    }
  },
  methods: {
    logout() {
      // Clear the session or localStorage data
      localStorage.removeItem('access_token');
      alert('You have been logged out.');
      window.location.reload(); // Refresh the page after login success
    },
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
  width: 256px;
  height: 100vh;
  position: relative;
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.05),
      rgba(32, 32, 32, 0.1),
      rgba(255, 255, 255, 0.05));
  background-blend-mode: overlay;
  transition: all 0.3s ease-in-out;
  backdrop-filter: blur(20px) saturate(250%);
  -webkit-backdrop-filter: blur(20px) saturate(250%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow:
    inset 0 0 8px rgba(255, 255, 255, 0.2),
    0 4px 10px rgba(0, 0, 0, 0.3);
}

.sidebar-content {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Custom scrollbar styles */
.sidebar-content::-webkit-scrollbar {
  width: 5px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
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
  color: black;
  text-decoration: none;
  padding: 12px 8px;
  border-radius: 8px;
  transition: all 0.3s;
}

.menu ul li > a:hover,
.menu ul li.active > a {
  color: #000;
  background-color: #fff;
}

.menu ul li .icon {
  font-size: 20px;
}

.menu ul li .text {
  flex: 1;
}

.menu:not(:last-child) {
  padding-bottom: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #f6f6f6;
}

.menu .title {
  font-size: 10px;
  font-weight: 500;
  color: black;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.menu-btn {
  position: absolute;
  right: -14px;
  top: 24px;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: black;
  border: 2px solid #f6f6f6;
  background-color: #fff;
  z-index: 1;
}

.menu-btn:hover i {
  color: black;
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

.sidebar.active .menu.title {
  text-align: center;
}

.sidebar.active .menu > ul > li > a {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar.active .menu > ul > li > a .text {
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

.sidebar.active .menu > ul > li > a .text::after {
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

.sidebar.active .menu > ul > li > a:hover .text {
  left: 50px;
  opacity: 1;
  visibility: visible;
  transition: all 0.3s;
}

.account-menu {
  margin-top: auto;
}
/* restore the FA font for any element using the FA classes */
.fas,
.fa-solid,
.far,
.fa-regular,
.fab,
.fa-brands {
  font-family: "Font Awesome 6 Free" !important;
  font-weight: 900; /* for solid icons (.fas / .fa-solid) */
}
.icon.fas {
  font-family: "Font Awesome 6 Free" !important;
  font-weight: 900;
}

/* Add new styles for error indicator */
.has-errors .nav-link {
  position: relative;
}

.error-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  background-color: #ef4444;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Adjust the collapsed state to show the indicator */
.sidebar.active .error-indicator {
  right: 4px;
  top: 4px;
}

/* Make sure the indicator is visible in both expanded and collapsed states */
.sidebar.active .nav-link {
  padding-right: 24px;
}
</style>