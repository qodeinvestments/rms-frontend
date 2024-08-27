<template>
    <div class="nav-container">
        <div v-for="(p, index) in navColumns" :key="index" :class="selectedValue === p ? 'selectedValue-color' : ''"
            class="nav-item" @click="handleClick(p, index)">
            <div class="todayheading" v-if="colorPresent(p)">new</div>
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
    },
    colorColumns: {
        type: Array,
        required: true
    }
})
const colorPresent = (val) => {
    return props.colorColumns.includes(val)
}

const selectedValue = ref(props.navColumns[0]);
// Define the emit function
const emit = defineEmits(['column-clicked'])

// Handle click event
const handleClick = (item, index) => {
    emit('column-clicked', { item, index })
    selectedValue.value = item;
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

.selectedValue-color {
    color: #007bff;
}

.todayheading {
    position: absolute;
    bottom: -30%;
    font-size: 10px;
    color: red
}

.nav-item {
    position: relative;
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
