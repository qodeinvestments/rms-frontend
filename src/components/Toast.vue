<template>
    <Transition name="toast-fade" @after-enter="playSound" @after-leave="stopSound">
        <div v-if="isVisible" class="toast" :class="type">
            {{ message }}
            <button @click="hide" class="close-btn">&times;</button>
        </div>
    </Transition>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";

// Define props
const props = defineProps({
    message: {
        type: String,
        required: true
    },
    type: {
        type: String,
        default: "info",
        validator: (value) => ["info", "success", "warning", "error"].includes(value)
    }
});

// Emit event when toast is closed
const emit = defineEmits(["close"]);

// Toast visibility state
const isVisible = ref(false);

// Load the sound
let alertSound;
onMounted(() => {
    alertSound = new Audio("/alarm.mp3"); // ✅ Ensure file is in public/
    alertSound.load();
});

// Function to play the sound **after the toast is visible**
const playSound = () => {
    if (alertSound) {
        console.log("🔊 Playing sound...");
        alertSound.play().catch((err) => console.error("Error playing sound:", err));
    }
};

// Function to stop the sound **after the toast disappears**
const stopSound = () => {
    if (alertSound) {
        console.log("🔇 Stopping sound...");
        alertSound.pause();
        alertSound.currentTime = 0; // ✅ Reset to the start
    }
};

// Function to show the toast
const show = () => {
    isVisible.value = true;
};

// Function to hide the toast
const hide = () => {
    isVisible.value = false;
    emit("close");
};

// Watch for changes in the message prop
watch(() => props.message, () => {
    show();
});

// Show the toast initially when mounted
onMounted(() => {
    if (props.message) {
        show();
    }
});
</script>


<style scoped>
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 10px 20px;
    border-radius: 4px;
    color: white;
    font-weight: bold;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer; /* Ensures user clicks on toast */
}

.close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
    margin-left: 10px;
}

.info {
    background-color: #2196F3;
}

.success {
    background-color: #4CAF50;
}

.warning {
    background-color: #FFC107;
}

.error {
    background-color: #F44336;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
    transition: opacity 0.3s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
    opacity: 0;
}
</style>