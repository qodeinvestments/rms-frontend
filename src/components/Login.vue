<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Welcome to Qode RMS Dashboard</h2>
      <p class="subtitle">Sign in to continue to your dashboard</p>
      
      <!-- Microsoft OAuth Button -->
      <button @click="handleMicrosoftOAuth" class="microsoft-oauth-button">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 8px;">
          <rect x="2" y="2" width="9" height="9" fill="#F35325"/>
          <rect x="13" y="2" width="9" height="9" fill="#81BC06"/>
          <rect x="2" y="13" width="9" height="9" fill="#05A6F0"/>
          <rect x="13" y="13" width="9" height="9" fill="#FFBA08"/>
        </svg>
        Sign in with Microsoft
      </button>
    </div>
  </div>
</template>

<script setup>
import { msalInstance, loginRequest } from '../msal';

// Handle Microsoft OAuth login
const handleMicrosoftOAuth = async () => {
  try {
    // Ensure MSAL is initialized
    await msalInstance.initialize();
    
    console.log('Starting Microsoft OAuth login with redirect...');
    
    // Use redirect flow instead of popup - works more reliably
    await msalInstance.loginRedirect(loginRequest);
    
  } catch (error) {
    console.error('Microsoft OAuth error:', error);
    alert(`Microsoft login failed: ${error.message || 'Unknown error'}`);
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  width: 100%;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #ffffff;
  padding: 20px;
}

.login-card {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  width: 100%;
  max-width: 450px;
  text-align: center;
}

h2 {
  color: #1f2937;
  margin-bottom: 0.5rem;
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.2;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 2.5rem;
  font-size: 1rem;
  line-height: 1.5;
}

.microsoft-oauth-button {
  width: 100%;
  padding: 0.875rem 1.5rem;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.microsoft-oauth-button:hover {
  background-color: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}

.microsoft-oauth-button:active {
  transform: translateY(0);
}

.microsoft-oauth-button:focus {
  outline: none;
  ring: 2px solid #3b82f6;
  ring-offset: 2px;
}
</style>