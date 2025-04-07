<template>
  <div class="p-6  ">
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
       
      >
        <!-- Modal Container -->
        <div class="bg-white w-11/12 md:w-2/3 lg:w-1/2 p-4 rounded shadow-lg relative">
          <!-- Close button (optional) -->
          <button
            class="absolute top-2 right-4 font-bold text-2xl leading-none"
            @click="closeModal"
          >
            &times;
          </button>

          <!-- Render OptionChain inside the modal -->
          <OptionChain @symbolSelected="handleSymbolSelected" />
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

.modal-content {
  transition: transform 0.2s ease;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .loader {
    animation: none;
  }
  
  .modal-overlay,
  .modal-content {
    transition: none;
  }
}
</style>



