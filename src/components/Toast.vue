<template>
    <Transition name="toast-fade" @after-enter="handleEnter" @after-leave="handleLeave">
        <div v-if="isVisible" class="toast" :class="type">
            {{ message }}
            <button @click="hide" class="close-btn">&times;</button>
        </div>
    </Transition>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";

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

// Function to request notification permission
const requestNotificationPermission = async () => {
    if (!("Notification" in window)) {
        console.log("This browser does not support notifications");
        return;
    }

    let permission = Notification.permission;
    
    if (permission === "default") {
        try {
            permission = await Notification.requestPermission();
        } catch (error) {
            console.error("Error requesting permission:", error);
        }
    }
    
    console.log("Notification permission:", permission);
    if (permission !== "granted") {
        alert("Please enable notifications in your browser settings.");
    }
};

// Function to show Windows notification (Only Called Once)
const showWindowsNotification = async () => {
    if (!("Notification" in window) || Notification.permission !== "granted") {
        console.log("No notification permission");
        return;
    }

    if ("serviceWorker" in navigator) {
        navigator.serviceWorker.ready.then((reg) => {
            reg.showNotification("New Alert!", {
                body: props.message, // Use the toast message
                icon: "/favicon.ico",
                requireInteraction: true,  // Keeps notification visible
                silent: false, // Ensures sound plays
            });
        }).catch((err) => console.error("Error showing notification:", err));
    }
};

// Mount the component
onMounted(async () => {
    // Initialize audio
    audio.value = new Audio('/alarm.mp3');
    audio.value.loop = false;
    audio.value.volume = props.volume;

    // Request notification permission
    await requestNotificationPermission();

    // Add visibility change listener
    document.addEventListener("visibilitychange", handleVisibilityChange);
});

// Cleanup on unmount
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

// Function to handle toast enter
const handleEnter = async () => {
    // Play sound
    if (audio.value) {
        try {
            audio.value.currentTime = 0;
            await audio.value.play();
            
            // Auto close toast after 2 seconds
            setTimeout(() => {
                hide();
            }, 2000);
        } catch (error) {
            console.error('Error playing audio:', error);
        }
    }
};

// Function to handle toast leave
const handleLeave = () => {
    if (audio.value) {
        audio.value.pause();
        audio.value.currentTime = 0;
    }
};

// Handle page visibility change
const handleVisibilityChange = async () => {
    if (document.hidden && isVisible.value) {
        console.log("Tab is hidden, ensuring audio plays in the background.");
        
        await showWindowsNotification(); // Only one notification
        
        if (audio.value) {
            try {
                audio.value.currentTime = 0;
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

    // Show notification only once
    showWindowsNotification();
    
    // Play the alarm sound
    handleEnter();
};

// Function to hide the toast
const hide = () => {
    isVisible.value = false;
    handleLeave();
    emit("close");
};

// Watch for message updates (Only Trigger if it Actually Changes)
watch(() => props.message, (newMessage, oldMessage) => {
    if (newMessage && newMessage !== oldMessage) {
        show();
    }
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
