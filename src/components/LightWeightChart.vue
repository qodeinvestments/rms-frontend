<script setup>
import { ref, watch, computed, onMounted, nextTick } from 'vue';
import LWChart from './LWChart.vue';

const props = defineProps({
    Chartdata: {
        type: Object,
        required: true,
    },
});

const chartOptions = ref({});
const data = ref(props.Chartdata);
const seriesOptions = ref([]);
const chartType = ref('line');
const lwChart = ref();

const getDataKeys = computed(() => Object.keys(data.value));

// Create a map to store colors for each key
const colorMap = ref(new Map());

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Debounced update function
const debouncedUpdateChart = debounce(() => {
    if (lwChart.value) {
        if (typeof lwChart.value.updateData === 'function') {
            lwChart.value.updateData(data.value);
        } else {
            // Fallback: force re-render if updateData is not available
            forceChartUpdate();
        }
    }
}, 300);

// Force chart update function
const forceChartUpdate = () => {
    nextTick(() => {
        if (lwChart.value) {
            lwChart.value.$forceUpdate();
        }
    });
};

watch(
    () => props.Chartdata,
    newData => {
        data.value = { ...newData }; // Create a new object reference
        updateSeriesOptions(false);
        debouncedUpdateChart();
    },
    { deep: true }
);

function randomColor() {
    return `rgb(${Math.round(Math.random() * 255)}, ${Math.round(Math.random() * 255)}, ${Math.round(Math.random() * 255)})`;
}

function updateSeriesOptions(regenerateColors = false) {
    seriesOptions.value = getDataKeys.value.map(key => {
        if (regenerateColors || !colorMap.value.has(key)) {
            colorMap.value.set(key, randomColor());
        }
        return {
            color: colorMap.value.get(key),
            title: key
        };
    });
}

const changeColors = () => {
    updateSeriesOptions(true);
    if (lwChart.value && typeof lwChart.value.updateOptions === 'function') {
        lwChart.value.updateOptions({ seriesOptions: seriesOptions.value });
    } else {
        forceChartUpdate();
    }
};

// Initial setup
onMounted(() => {
    updateSeriesOptions(true);
});
</script>
<template>
    <div class="chart-dashboard">
        <div class="chart-controls">
            <button 
                type="button" 
                @click="changeColors"
                class="control-button"
            >
                <span class="button-icon">🎨</span>
                Refresh Colors
            </button>
        </div>
        
        <div class="chart-wrapper">
            <div class="chart-container">
                <LWChart 
                    :type="chartType" 
                    :data="data" 
                    :autosize="true" 
                    :chart-options="chartOptions"
                    :series-options="seriesOptions" 
                    ref="lwChart" 
                />
            </div>
            
            <div class="legend-container">
                <div class="legend">
                    <div 
                        v-for="(option, index) in seriesOptions" 
                        :key="index" 
                        class="legend-item"
                    >
                        <div 
                            class="color-box" 
                            :style="{ backgroundColor: option.color }"
                        ></div>
                        <span class="legend-text">{{ option.title }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.chart-dashboard {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 14px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(229, 231, 235, 0.5);
    padding: 1.75rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chart-dashboard:hover {
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
}

.chart-controls {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1.75rem;
    padding-bottom: 1.75rem;
    border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}

.control-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    background: white;
    border: 1px solid rgba(229, 231, 235, 0.5);
    border-radius: 10px;
    color: #475569;
    font-weight: 500;
    font-size: 0.875rem;
    transition: all 0.3s ease;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.control-button:hover {
    background: #f8fafc;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    color: #2563eb;
}

.control-button:active {
    transform: translateY(0);
}

.button-icon {
    font-size: 1.25rem;
}

.chart-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
}

.chart-container {
    flex-grow: 1;
    min-height: 450px;
    border-radius: 10px;
    overflow: hidden;
    background: white;
    border: 1px solid rgba(229, 231, 235, 0.5);
}

.legend-container {
    padding: 1.25rem;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 10px;
    border: 1px solid rgba(229, 231, 235, 0.5);
    backdrop-filter: blur(8px);
}

.legend {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
    align-items: center;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    padding: 0.625rem 1rem;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    border: 1px solid rgba(229, 231, 235, 0.5);
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.legend-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: rgba(37, 99, 235, 0.2);
}

.color-box {
    width: 14px;
    height: 14px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.legend-text {
    font-size: 0.875rem;
    color: #475569;
    font-weight: 500;
    letter-spacing: 0.01em;
}

/* Responsive design */
@media (max-width: 768px) {
    .chart-dashboard {
        padding: 1.25rem;
    }
    
    .chart-controls {
        margin-bottom: 1.25rem;
        padding-bottom: 1.25rem;
    }
    
    .control-button {
        padding: 0.625rem 1rem;
        font-size: 0.813rem;
    }
    
    .chart-container {
        min-height: 380px;
    }
    
    .legend-container {
        padding: 1rem;
    }
    
    .legend {
        gap: 0.75rem;
    }
    
    .legend-item {
        padding: 0.5rem 0.875rem;
    }
    
    .color-box {
        width: 12px;
        height: 12px;
    }
    
    .legend-text {
        font-size: 0.813rem;
    }
}

/* Animation keyframes */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.legend-item {
    animation: fadeIn 0.3s ease-out forwards;
}

/* Stagger animation for legend items */
.legend-item:nth-child(n) {
    animation-delay: calc(0.1s * var(--i, 0));
}
</style>