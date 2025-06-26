<template>
    <div class="login-container">
      <div class="login-card">
        <h2>Login</h2>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="username">Username</label>
            <input
              v-model="username"
              type="text"
              id="username"
              placeholder="Enter your username"
              required
            />
          </div>
  
          <div class="form-group">
            <label for="password">Password</label>
            <input
              v-model="password"
              type="password"
              id="password"
              placeholder="Enter your password"
              required
            />
          </div>
  
          <button type="submit" class="login-button">Login</button>
        </form>
        
        <!-- Sign Up Button -->
        <button @click="handleSignUp" class="signup-button">
          Don't have an account? Sign Up
        </button>
        
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
  import { ref } from 'vue';
  import { msalInstance, loginRequest } from '../msal';
  import { API_BASE_URL, WS_BASE_URL } from '../config/url'

  const loginUser = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();
      if (data.success) {
        // Store user info and token separately for clarity
        localStorage.setItem('access_token', data.access_token); // Store the token separately
        
        alert('Login successful!');
        window.location.reload(); // Refresh the page after login success
      } else {
        alert(data.detail);
      }
    } catch (error) {
      console.error('Error during login:', error);
      alert('Error during login. Please try again.');
    }
  };
  
  // Define the state using ref
  const username = ref('');
  const password = ref('');
  
  // Define emit for emitting events
  const emit = defineEmits(['toggleForm']);
  
  // Handle login logic
  const handleLogin = async () => {
    if (username.value && password.value) {
      try {
        await loginUser(username.value, password.value);
        // Handle successful login
      } catch (error) {
        alert('Error during login. Please check your credentials.');
      }
    } else {
      alert('Please fill in both fields.');
    }
  };
  
  // Emit event for sign up
  const handleSignUp = () => {
    emit('toggleForm');
  };
  
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
    background-color: #f5f5f5;
    padding: 20px;
  }
  
  .login-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  h2 {
    text-align: center;
    color: #333;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #374151;
    font-weight: 500;
  }
  
  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    transition: border-color 0.15s ease-in-out;
  }
  
  input:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }
  
  .login-button,
  .signup-button {
    width: 100%;
    padding: 0.75rem;
    border: none;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.15s ease-in-out;
  }
  
  .login-button {
    background-color: #3b82f6;
    color: white;
    margin-bottom: 1rem;
  }
  
  .login-button:hover {
    background-color: #2563eb;
  }
  
  .signup-button {
    background-color: #10b981;
    color: white;
  }
  
  .signup-button:hover {
    background-color: #059669;
  }
  
  .microsoft-oauth-button {
    width: 100%;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 0.375rem;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    background-color: #2F2F2F;
    color: white;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: background 0.15s;
    box-sizing: border-box;
  }
  
  .microsoft-oauth-button:hover {
    background-color: #0078D4;
  }
  
  .microsoft-oauth-button svg {
    flex-shrink: 0;
  }
  
  @media (max-width: 640px) {
    .login-card {
      padding: 1.2rem;
      max-width: 95vw;
    }
  
    input,
    .login-button,
    .signup-button,
    .microsoft-oauth-button {
      padding: 0.65rem 0.7rem;
      font-size: 0.95rem;
    }
  
    h2 {
      font-size: 1.2rem;
    }
  }
  
  /* Additional enhancements */
  input::placeholder {
    color: #9ca3af;
  }
  
  .form-group:last-of-type {
    margin-bottom: 1.5rem;
  }
  
  /* Add smooth transition for all interactive elements */
  button, input {
    transition: all 0.2s ease-in-out;
  }
  
  input:hover {
    border-color: #94a3b8;
  }
  
  .login-card {
    transition: transform 0.2s ease-in-out;
  }
  
  .login-card:hover {
    transform: translateY(-2px);
  }
  
  /* Add focus styles for better accessibility */
  button:focus {
    outline: none;
    box-shadow: 0 0 0 2px #3b82f6;
  }
  
  /* Error state styles */
  input.error {
    border-color: #ef4444;
  }
  
  .error-message {
    color: #ef4444;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  </style>