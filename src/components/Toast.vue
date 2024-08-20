<template>
    <Transition name="toast-fade">
        <div v-if="isVisible" class="toast" :class="type">
            {{ message }}
            <button @click="hide" class="close-btn">&times;</button>
        </div>
    </Transition>
</template>

<script setup>
import { ref, onMounted, defineProps, watch } from 'vue'

const props = defineProps({
    message: {
        type: String,
        required: true
    },
    type: {
        type: String,
        default: 'info',
        validator: (value) => ['info', 'success', 'warning', 'error'].includes(value)
    }
})

const isVisible = ref(false)

const show = () => {
    isVisible.value = true
}

const hide = () => {
    isVisible.value = false
}

onMounted(() => {
    show()
})

// Reshow the toast if the message changes
watch(() => props.message, () => {
    show()
})
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