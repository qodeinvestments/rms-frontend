<template>
  <!-- Previous template code remains the same -->
  <div class="container">
    <div class="sidebar" :class="sidebarState ? 'active' : ''" ref="targetElement">
      <div class="menu-btn" @click="toggleSideBar()">
        <i class="ph-bold ph-caret-left"></i>
      </div>
      
      <div class="head">
        <div class="user-img">
          <img src="../assets/swan_capital.jpeg" alt="Swan Capital Logo" class="logo-image">
        </div>
      </div>

      <div class="nav">
        <div class="menu">
          <p class="title" :class="sidebarState ? 'align-center' : ''">Main Menu</p>
          <ul>
            <li :class="selected === 'Dashboard' ? 'active' : ''" @click="changeSelected('Dashboard')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-house-simple"></i>
                <span class="text">Dashboard</span>
              </a>
            </li>
            
            <li :class="selected === 'Errors' ? 'active' : ''" @click="changeSelected('Errors')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-warning-circle"></i>
                <span class="text">Errors</span>
              </a>
            </li>

            <li :class="selected === 'KeyDBLogs' ? 'active' : ''" @click="changeSelected('KeyDBLogs')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-database"></i>
                <span class="text">KeyDB Logs</span>
              </a>
            </li>

            <li :class="selected === 'DataVisualizer' ? 'active' : ''" @click="changeSelected('DataVisualizer')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-chart-line"></i>
                <span class="text">Data Visualizer</span>
              </a>
            </li>

            <li :class="selected === 'SignalBook' ? 'active' : ''" @click="changeSelected('SignalBook')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-book"></i>
                <span class="text">Signal Book</span>
              </a>
            </li>

            <li :class="selected === 'ServerData' ? 'active' : ''" @click="changeSelected('ServerData')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-server"></i>
                <span class="text">Server Data</span>
              </a>
            </li>
          </ul>
        </div>

        <div class="menu">
          <p class="title" :class="sidebarState ? 'align-center' : ''">Settings</p>
          <ul>
            <li :class="selected === 'Settings' ? 'active' : ''" @click="changeSelected('Settings')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-gear"></i>
                <span class="text">Settings</span>
              </a>
            </li>
            
            <li :class="selected === 'AdminPanel' ? 'active' : ''" @click="changeSelected('AdminPanel')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-shield"></i>
                <span class="text">Admin Panel</span>
              </a>
            </li>

            <li :class="selected === 'MarginUpdate' ? 'active' : ''" @click="changeSelected('MarginUpdate')">
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-trending-up"></i>
                <span class="text">Margin Update</span>
              </a>
            </li>
          </ul>
        </div>

        <div class="menu">
          <p class="title" :class="sidebarState ? 'align-center' : ''">Account</p>
          <ul>
            <li>
              <a href="#" class="nav-link">
                <i class="icon ph-bold ph-question"></i>
                <span class="text">Help</span>
              </a>
            </li>
            
            <li>
              <a href="#" class="nav-link logout" @click="logout">
                <i class="icon ph-bold ph-sign-out"></i>
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
// Previous script code remains the same
import { useRouter } from 'vue-router';

export default {
  data() {
    return {
      sidebarState: false,
      selected: '',
      navigateMap: {
        'Dashboard': '/',
        'Errors': '/errors',
        'KeyDBLogs': '/keydblogs',
        'DataVisualizer': '/visualize',
        'SignalBook': '/signalbook',
        'ServerData': '/serverData',
        'AdminPanel': '/adminPanel',
        'MarginUpdate': '/marginUpdate'
      }
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token');
      alert('You have been logged out.');
      window.location.reload();
    },
    toggleSideBar() {
      this.sidebarState = !this.sidebarState;
      this.$emit("State", this.sidebarState);
    },
    changeSelected(val) {
      this.selected = val;
      this.$router.push(this.navigateMap[val]);
    },
    handleClickOutside(event) {
      const targetElement = this.$refs.targetElement;
      if (!targetElement || !targetElement.contains(event.target)) {
        this.selected = '';
      }
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
/* Base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.container {
  width: 100%;
  min-height: 100vh;
  height: 100%;
  z-index: 1000;
}





/* Sidebar main styles */
.sidebar {
  width: 256px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  padding: 1.75rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(229, 231, 235, 0.5);
}

.sidebar.active {
  width: 100px;
}

/* Header styles */
.head {
  display: flex;
  justify-content: center;
  padding-bottom: 1.75rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}

.user-img {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

/* Menu button styles */
.menu-btn {
  position: absolute;
  right: -16px;
  top: 28px;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: white;
  border: 1px solid rgba(229, 231, 235, 0.5);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.menu-btn:hover {
  background: #f8fafc;
  transform: scale(1.05);
}

.menu-btn i {
  font-size: 1.25rem;
  transition: transform 0.3s ease;
  color: #64748b;
}

.sidebar.active .menu-btn i {
  transform: rotate(180deg);
}

/* Navigation styles */
.nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* Menu title styles */
.menu .title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

.align-center {
  text-align: center;
}

/* Navigation link styles */
.nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  border-radius: 10px;
  color: #475569;
  transition: all 0.3s ease;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
}

.nav-link:hover {
  background: #f8fafc;
  color: #0f172a;
}

.nav-link .icon {
  font-size: 1.5rem;
  min-width: 1.5rem;
}

.nav-link .text {
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.01em;
}

/* Active state styles */
li.active .nav-link {
  background: #f1f5f9;
  color: #2563eb;
  font-weight: 600;
}

/* Menu section styles */
.menu:not(:last-child) {
  padding-bottom: 1.25rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}

/* Logout button styles */
.logout {
  color: #ef4444;
}

.logout:hover {
  background: #fef2f2;
  color: #dc2626;
}

/* Hover effects */
.nav-link {
  position: relative;
  overflow: hidden;
}

.nav-link::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #2563eb;
  transition: width 0.3s ease;
}

.nav-link:hover::after {
  width: 100%;
}

/* Collapsed state tooltip */
.sidebar.active .nav-link:hover::before {
  content: attr(data-tooltip);
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background: #1e293b;
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  white-space: nowrap;
  z-index: 1000;
  margin-left: 1rem;
}

/* Responsive styles */
@media (max-width: 768px) {
  .sidebar {
    width: 280px;
  }
  
  .sidebar.active {
    width: 88px;
  }
  
  .nav-link {
    padding: 0.75rem 1rem;
  }
  
  .nav-link .text {
    font-size: 0.9375rem;
  }
  
  .menu-btn {
    width: 28px;
    height: 28px;
    right: -14px;
  }
}

/* Animation for menu items */
.nav-link {
  transform: translateX(0);
  transition: transform 0.3s ease, background 0.3s ease, color 0.3s ease;
}

/* Collapsed state animations */
.sidebar.active .nav-link {
  transform: translateX(-8px);
}

.sidebar.active .nav-link:hover {
  transform: translateX(-4px);
}

.sidebar.active .nav-link .text {
  opacity: 0;
  width: 0;
}

.sidebar.active .menu .title {
  opacity: 0;
}
</style>