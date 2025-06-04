<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
    message: {
        type: String,
        required: true
    }
})

const isHovered = ref(false)
const tooltipRef = ref(null)
const containerRef = ref(null)

const checkPosition = () => {
    if (!tooltipRef.value || !containerRef.value) return
    
    const tooltip = tooltipRef.value
    const container = containerRef.value
    const rect = container.getBoundingClientRect()
    
    // If there's not enough space above (less than 200px), show below
    if (rect.top < 200) {
        tooltip.style.bottom = 'auto'
        tooltip.style.top = '100%'
        tooltip.style.marginBottom = '0'
        tooltip.style.marginTop = '8px'
    } else {
        tooltip.style.bottom = '100%'
        tooltip.style.top = 'auto'
        tooltip.style.marginBottom = '8px'
        tooltip.style.marginTop = '0'
    }
}

onMounted(() => {
    window.addEventListener('scroll', checkPosition)
    window.addEventListener('resize', checkPosition)
})
</script>

<template>
    <div class="info-icon-container" ref="containerRef">
        <div 
            class="info-icon"
            @mouseenter="() => { isHovered = true; checkPosition() }"
            @mouseleave="isHovered = false"
        >
            <i class="fas fa-info-circle"></i>
        </div>
        
        <!-- Tooltip -->
        <div 
            v-if="isHovered" 
            class="tooltip"
            ref="tooltipRef"
            @mouseenter="isHovered = true"
            @mouseleave="isHovered = false"
        >
            <div class="tooltip-content">
                {{ message }}
            </div>
        </div>
    </div>
</template>

<style scoped>
.info-icon-container {
    position: relative;
    display: inline-block;
    margin-left: 8px;
}

.info-icon {
    cursor: pointer;
    color: #666;
    transition: all 0.3s ease;
    font-size: 16px;
    padding: 4px;
}

.info-icon:hover {
    color: #1890ff;
    transform: scale(1.1);
}

.tooltip {
    position: absolute;
    z-index: 1000;
    left: 50%;
    transform: translateX(-50%);
}

.tooltip-content {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    color: #2c3e50;
    padding: 12px 16px;
    border-radius: 8px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
    line-height: 1.5;
    max-width: 400px;
    min-width: 300px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.8);
    font-weight: 450;
    letter-spacing: -0.01em;
    white-space: normal;
    word-wrap: break-word;
}
</style> 