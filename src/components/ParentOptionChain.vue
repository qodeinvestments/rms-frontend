<template>
  <div class="p-6">
    <!-- Button to open the modal -->
    <button
      @click="showModal = true"
      class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
    >
      Open Option Chain Modal
    </button>

    <!-- Transition for modal fade in/out -->
    <transition name="fade">
      <!-- The Overlay (entire screen) -->
      <div
        v-if="showModal"
        class="modal-overlay"
        @click.self="closeModal"
      >
        <!-- Modal Container - Made larger to fill more screen space -->
        <div class="bg-white w-11/12 md:w-4/5 lg:w-4/5 xl:w-4/5 p-0 rounded-lg shadow-2xl relative max-h-screen flex flex-col">
          <!-- Modal Header with close button -->
          <div class="flex justify-between items-center p-4 border-b border-gray-200">
            <h2 class="text-xl font-bold text-gray-800">Options Chain</h2>
            <button
              class="text-gray-500 hover:text-gray-700 focus:outline-none"
              @click="closeModal"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Modal Content - Scrollable -->
          <div class="flex-grow overflow-auto p-4">
            <!-- Render OptionChain inside the modal with a class to maximize width -->
            <OptionChain @symbolSelected="handleSymbolSelected" class="option-chain-full-width" />
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import OptionChain from './OptionChain.vue' // Adjust path if necessary

const showModal = ref(false)

function closeModal() {
  showModal.value = false
}

function handleSymbolSelected(symbol) {
  console.log('Symbol selected from modal:', symbol)
  // Example: close the modal and do something with the symbol
  showModal.value = false
}
</script>

<style scoped>
/* Simple fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  transition: opacity 0.2s ease;
}

/* Transitions */
.modal-overlay {
  transition: opacity 0.2s ease;
}

/* Make sure the option chain component uses all available width */
:deep(.option-chain-full-width) {
  width: 100%;
}

/* Style the tables to fill the available space */
:deep(.option-chain-full-width .grid) {
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

:deep(.option-chain-full-width table) {
  width: 100%;
}

:deep(.option-chain-full-width .max-h-96) {
  max-height: 60vh; /* Make tables taller to show more content */
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .modal-overlay,
  .modal-content {
    transition: none;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  :deep(.option-chain-full-width .grid) {
    grid-template-columns: 1fr;
  }
}
</style>