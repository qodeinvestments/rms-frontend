<template>
  <div class="margin-update-container">
    <div class="page-header">
      <h1 class="page-title">Margin Update</h1>
      <div class="user-badge">
        <i class="fas fa-user-circle"></i>
        <span>{{ username }} </span>
      </div>
    </div>
    <!-- Strategy Selection -->
    <div class="strategy-section glass-card">
      <div class="section-header">
        <h2 class="section-title">
          <i class="fas fa-layer-group"></i>
          Select Strategies
        </h2>
        <p class="section-subtitle">Choose one or more strategies to update margin settings</p>
      </div>
      <a-select
        v-model:value="selectedStrategies"
        mode="multiple"
        placeholder="Select Strategies"
        class="strategy-select"
        :options="strategyOptions"
        :maxTagCount="3"
        @change="handleStrategyChange"
      >
        <template #suffixIcon>
          <i class="fas fa-chevron-down"></i>
        </template>
      </a-select>
    </div>

    <!-- Strategy Settings -->
    <TransitionGroup 
      name="strategy-list" 
      tag="div" 
      class="strategy-settings"
      v-if="selectedStrategies.length > 0"
    >
      <div 
        v-for="strategy in selectedStrategies" 
        :key="strategy" 
        class="strategy-card glass-card"
      >
        <div class="strategy-header">
          <h3 class="strategy-title">
            <i class="fas fa-chart-line"></i>
            {{ strategy }}
          </h3>
          <button 
            class="remove-strategy"
            @click="removeStrategy(strategy)"
            title="Remove strategy"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <!-- Date Selection Type -->
        <div class="date-type-selector">
          <a-radio-group 
            v-model:value="strategySettings[strategy].dateType" 
            @change="handleDateTypeChange(strategy)"
            class="date-type-radio"
          >
            <a-radio value="all">
              <i class="fas fa-calendar-check"></i>
              All Days
            </a-radio>
            <a-radio value="range">
              <i class="fas fa-calendar-week"></i>
              Range
            </a-radio>
            <a-radio value="days">
              <i class="fas fa-calendar-day"></i>
              Specific Days
            </a-radio>
          </a-radio-group>
        </div>

        <!-- Range Selection -->
        <Transition name="fade">
          <div v-if="strategySettings[strategy].dateType === 'range'" class="range-selector">
            <div class="range-inputs">
              <div class="range-input">
                <label>
                  <i class="fas fa-arrow-right"></i>
                  Start Day
                </label>
                <a-select
                  v-model:value="strategySettings[strategy].rangeStart"
                  class="day-select"
                  @change="validateRange(strategy)"
                >
                  <a-select-option v-for="day in weekDays" :key="day" :value="day">
                    {{ day }}
                  </a-select-option>
                </a-select>
              </div>
              <div class="range-input">
                <label>
                  <i class="fas fa-arrow-left"></i>
                  End Day
                </label>
                <a-select
                  v-model:value="strategySettings[strategy].rangeEnd"
                  class="day-select"
                  :disabled="!strategySettings[strategy].rangeStart"
                  @change="validateRange(strategy)"
                >
                  <a-select-option 
                    v-for="day in availableEndDays(strategy)" 
                    :key="day" 
                    :value="day"
                  >
                    {{ day }}
                  </a-select-option>
                </a-select>
              </div>
            </div>
          </div>
        </Transition>

        <!-- Specific Days Selection -->
        <Transition name="fade">
          <div v-if="strategySettings[strategy].dateType === 'days'" class="days-selector">
            <a-select
              v-model:value="strategySettings[strategy].selectedDays"
              mode="multiple"
              placeholder="Select Days"
              class="days-select"
              :options="weekDays.map(day => ({ label: day, value: day }))"
            >
              <template #suffixIcon>
                <i class="fas fa-calendar-alt"></i>
              </template>
            </a-select>
          </div>
        </Transition>

        <!-- Error Message -->
        <Transition name="fade">
          <div v-if="strategySettings[strategy].error" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ strategySettings[strategy].error }}
          </div>
        </Transition>
      </div>
    </TransitionGroup>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button 
        @click="handleSave" 
        class="save-button"
        :disabled="!isValid || isSaving"
      >
        <i class="fas" :class="isSaving ? 'fa-spinner fa-spin' : 'fa-save'"></i>
        {{ isSaving ? 'Saving...' : 'Save Changes' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const username = computed(() => route.params.username);

// State management
const strategies = ref([]);
const selectedStrategies = ref([]);
const isSaving = ref(false);
const isLoading = ref(false);
const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

// Strategy settings state
const strategySettings = ref({});

// Computed properties
const strategyOptions = computed(() => 
  strategies.value.map(strategy => ({ label: strategy, value: strategy }))
);

const isValid = computed(() => {
  return selectedStrategies.value.every(strategy => {
    const settings = strategySettings.value[strategy];
    if (!settings) return false;

    switch (settings.dateType) {
      case 'all':
        return true;
      case 'range':
        return settings.rangeStart && settings.rangeEnd && !settings.error;
      case 'days':
        return settings.selectedDays && settings.selectedDays.length > 0;
      default:
        return false;
    }
  });
});

// Transform settings to required format
const transformSettings = (settings) => {
  switch (settings.dateType) {
    case 'all':
      return {
        type: 'all',
        value: ''
      };
    case 'range':
      return {
        type: 'range',
        value: {
          start: settings.rangeStart,
          end: settings.rangeEnd
        }
      };
    case 'days':
      return {
        type: 'specific_days',
        value: settings.selectedDays
      };
    default:
      return null;
  }
};

// Methods
const initializeStrategySettings = (strategy, existingSettings = null) => {
  if (existingSettings) {
    // Convert backend format to component format
    switch (existingSettings.type) {
      case 'all':
        strategySettings.value[strategy] = {
          dateType: 'all',
          rangeStart: null,
          rangeEnd: null,
          selectedDays: [],
          error: null
        };
        break;
      case 'range':
        strategySettings.value[strategy] = {
          dateType: 'range',
          rangeStart: existingSettings.value.start,
          rangeEnd: existingSettings.value.end,
          selectedDays: [],
          error: null
        };
        break;
      case 'specific_days':
        strategySettings.value[strategy] = {
          dateType: 'days',
          rangeStart: null,
          rangeEnd: null,
          selectedDays: existingSettings.value,
          error: null
        };
        break;
    }
  } else {
    strategySettings.value[strategy] = {
      dateType: 'all',
      rangeStart: null,
      rangeEnd: null,
      selectedDays: [],
      error: null
    };
  }
};

const handleStrategyChange = (value) => {
  // Initialize settings for newly selected strategies
  value.forEach(strategy => {
    if (!strategySettings.value[strategy]) {
      initializeStrategySettings(strategy);
    }
  });

  // Remove settings for deselected strategies
  Object.keys(strategySettings.value).forEach(strategy => {
    if (!value.includes(strategy)) {
      delete strategySettings.value[strategy];
    }
  });
};

const handleDateTypeChange = (strategy) => {
  const settings = strategySettings.value[strategy];
  settings.error = null;
  
  // Reset values when changing date type
  settings.rangeStart = null;
  settings.rangeEnd = null;
  settings.selectedDays = [];
};

const availableEndDays = (strategy) => {
  const settings = strategySettings.value[strategy];
  if (!settings.rangeStart) return weekDays;
  
  const startIndex = weekDays.indexOf(settings.rangeStart);
  return weekDays.slice(startIndex + 1);
};

const validateRange = (strategy) => {
  const settings = strategySettings.value[strategy];
  if (!settings.rangeStart || !settings.rangeEnd) {
    settings.error = null;
    return;
  }

  const startIndex = weekDays.indexOf(settings.rangeStart);
  const endIndex = weekDays.indexOf(settings.rangeEnd);

  if (endIndex <= startIndex) {
    settings.error = 'End day must be after start day';
    settings.rangeEnd = null;
  } else {
    settings.error = null;
  }
};

const fetchStrategies = async () => {
  try {
    isLoading.value = true;
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    const response = await fetch(`https://production2.swancapital.in/getBasket`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) throw new Error('Failed to fetch strategies');
    
    const data = await response.json();
    strategies.value = data;
  } catch (error) {
    console.error('Error fetching strategies:', error);
    // Handle error appropriately
  } finally {
    isLoading.value = false;
  }
};

const fetchExistingSettings = async () => {
  try {
    isLoading.value = true;
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    const response = await fetch(`https://production2.swancapital.in/marginUpdateCheckDetails`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: username.value })
    });

    if (!response.ok) throw new Error('Failed to fetch existing settings');
    
    const data = await response.json();
    
    // Set selected strategies and their settings
    if (data && Object.keys(data).length > 0) {
      selectedStrategies.value = Object.keys(data);
      selectedStrategies.value.forEach(strategy => {
        initializeStrategySettings(strategy, data[strategy]);
      });
    }
  } catch (error) {
    console.error('Error fetching existing settings:', error);
    // Handle error appropriately
  } finally {
    isLoading.value = false;
  }
};

const handleSave = async () => {
  if (!isValid.value || isSaving.value) return;

  try {
    isSaving.value = true;
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');

    // Transform the data to the required format
    const transformedStrategies = selectedStrategies.value.reduce((acc, strategy) => {
      acc[strategy] = transformSettings(strategySettings.value[strategy]);
      return acc;
    }, {});

    const payload = {
      username: username.value,
      strategies: transformedStrategies
    };

    const response = await fetch('https://production2.swancapital.in/updateMarginSettings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error('Failed to save margin settings');

    // Show success message or handle success appropriately
    alert('Margin settings updated successfully');
  } catch (error) {
    console.error('Error saving margin settings:', error);
    // Handle error appropriately
  } finally {
    isSaving.value = false;
  }
};

const removeStrategy = (strategy) => {
  selectedStrategies.value = selectedStrategies.value.filter(s => s !== strategy);
  delete strategySettings.value[strategy];
};

onMounted(async () => {
  if (username.value) {
    await Promise.all([
      fetchStrategies(),
      fetchExistingSettings()
    ]);
  }
});
</script>

<style scoped>
.margin-update-container {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f8fc 0%, #f1f4f9 100%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(59, 130, 246, 0.1);
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  background: linear-gradient(135deg, #1f2937 0%, #4b5563 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  color: #4b5563;
  font-weight: 500;
}

.user-badge i {
  color: #3b82f6;
}

.glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05),
              0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05),
              0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title i {
  color: #3b82f6;
}

.section-subtitle {
  color: #6b7280;
  margin: 0;
  font-size: 14px;
}

.strategy-section {
  padding: 32px;
  margin-bottom: 32px;
}

.strategy-select {
  width: 100%;
}

.strategy-select :deep(.ant-select-selector) {
  border-radius: 8px !important;
  border: 2px solid #e5e7eb !important;
  padding: 12px !important;
  transition: all 0.2s ease !important;
}

.strategy-select :deep(.ant-select-selector:hover) {
  border-color: #3b82f6 !important;
}

.strategy-settings {
  display: grid;
  gap: 24px;
  margin-top: 24px;
}

.strategy-card {
  padding: 24px;
  position: relative;
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.strategy-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.strategy-title i {
  color: #3b82f6;
}

.remove-strategy {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.remove-strategy:hover {
  background: #fee2e2;
  color: #ef4444;
}

.date-type-selector {
  margin-bottom: 24px;
}

.date-type-radio :deep(.ant-radio-wrapper) {
  margin-right: 24px;
  font-size: 15px;
}

.date-type-radio :deep(.ant-radio-wrapper) i {
  margin-right: 8px;
  color: #3b82f6;
}

.range-selector {
  margin-top: 20px;
}

.range-inputs {
  display: flex;
  gap: 24px;
  margin-top: 12px;
}

.range-input {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.range-input label {
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  display: flex;
  align-items: center;
  gap: 6px;
}

.range-input label i {
  color: #3b82f6;
}

.day-select {
  width: 100%;
}

.days-selector {
  margin-top: 20px;
}

.days-select {
  width: 100%;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 2px solid rgba(59, 130, 246, 0.1);
}

.save-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 15px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}

.save-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3);
}

.save-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Animations */
.strategy-list-enter-active,
.strategy-list-leave-active {
  transition: all 0.3s ease;
}

.strategy-list-enter-from,
.strategy-list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .margin-update-container {
    padding: 24px 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .strategy-section {
    padding: 24px 16px;
  }

  .range-inputs {
    flex-direction: column;
    gap: 16px;
  }

  .strategy-card {
    padding: 20px 16px;
  }

  .date-type-radio :deep(.ant-radio-wrapper) {
    display: block;
    margin-bottom: 12px;
  }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c5c5c5;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 