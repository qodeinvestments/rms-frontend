<template>
    <div class="nav-container">
        <div v-for="(p, index) in navColumns" :key="index" class="nav-item" @click="handleClick(p, index)">
            <p>{{ p }}</p>
        </div>
    </div>
</template>

<script setup>
import { ref, watchEffect, onMounted, onUnmounted } from 'vue'

// Define the props
const props = defineProps({
    navColumns: {
        type: Array,
        required: true
    }
})

// Define the emit function
const emit = defineEmits(['column-clicked'])

// Handle click event
const handleClick = (item, index) => {
    emit('column-clicked', { item, index })
}
</script>
<style scoped>
.nav-container {
    display: flex;
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    align-items: center;
    justify-content: space-around;
}

.nav-item {
    cursor: pointer;
    padding: 10px 20px;
    border-radius: 5px;
    transition: background-color 0.3s, color 0.3s;
}

.nav-item:hover {
    background-color: #007bff;
    color: white;
}

.nav-item p {
    margin: 0;
}
</style>
