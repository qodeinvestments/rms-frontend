<template>
    <Transition name="toast-fade" @after-enter="handleEnter" @after-leave="handleLeave">
        <div v-if="isVisible" 
             class="toast" 
             :class="type">
            {{ message }}
            <button @click="hide" class="close-btn">&times;</button>
        </div>
    </Transition>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";

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
    },
    volume: {
        type: Number,
        default: 0.3,
        validator: (value) => value >= 0 && value <= 1
    }
});

const emit = defineEmits(["close"]);
const isVisible = ref(false);
const audio = ref(null);

onMounted(() => {
    // Initialize audio
    audio.value = new Audio('/alarm.mp3');
    audio.value.loop = false; // Play once
    audio.value.volume = props.volume;

    // Listen to visibility change event
    document.addEventListener("visibilitychange", handleVisibilityChange);
});

onBeforeUnmount(() => {
    if (audio.value) {
        audio.value.pause();
        audio.value.currentTime = 0;
    }
    document.removeEventListener("visibilitychange", handleVisibilityChange);
});

// Watch for volume changes
watch(() => props.volume, (newVolume) => {
    if (audio.value) {
        audio.value.volume = newVolume;
    }
});

const handleEnter = async () => {
    if (audio.value) {
        try {
            audio.value.currentTime = 0;
            await audio.value.play();

            // Stop audio after 2 seconds and close toast
            setTimeout(() => {
                hide();
            }, 2000); // 2 seconds
        } catch (error) {
            console.error('Error playing audio:', error);
        }
    }
};

const handleLeave = () => {
    if (audio.value) {
        audio.value.pause();
        audio.value.currentTime = 0;
    }
};

// Handle page visibility change
const handleVisibilityChange = async () => {
    if (document.hidden) {
        console.log("Tab is hidden, ensuring audio plays in the background.");
        if (audio.value && isVisible.value) {
            try {
                await audio.value.play();
            } catch (error) {
                console.error("Error playing audio when hidden:", error);
            }
        }
    }
};

// Function to show the toast
const show = () => {
    isVisible.value = true;
    handleEnter();
};

// Function to hide the toast
const hide = () => {
    isVisible.value = false;
    handleLeave();
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
    padding: 0 5px;
}

.close-btn:hover {
    opacity: 0.8;
}

.info {
    background-color: #2196F3;
}

.success {
    background-color: #4CAF50;
}

.warning {
    background-color: #FFC107;
    color: #333;
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