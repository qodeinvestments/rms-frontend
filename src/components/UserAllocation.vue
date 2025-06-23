<template>
    <div class="px-8 py-8 pageContainer">
        <h1 class="page-title">User PnL Allocation</h1>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
            <div class="loader"></div>
            <p>Loading allocation data...</p>
        </div>

        <!-- Error State -->
        <div v-if="error" class="error-message">
            {{ error }}
            <button @click="fetchAllocationData" class="retry-button">Retry</button>
        </div>

        <!-- Table -->
        <div v-if="!loading && !error && allocationData.length" class="table-container">
            <TanStackTestTable 
                title="User Allocation" 
                :data="allocationData" 
                :columns="columns" 
                :hasColor="['Actual MTM','Abhinav','Ashwin','Darshana','Nilesh','Prahlad','Settlement Price']"
                :navigateTo="[]" 
                :showPagination="true"
                :showPin="true"
            />
        </div>

        <!-- No Data State -->
        <div v-if="!loading && !error && !allocationData.length" class="no-data">
            No allocation data available
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import TanStackTestTable from './TanStackTestTable.vue';
import { createColumnHelper } from '@tanstack/vue-table';
import { API_BASE_URL, WS_BASE_URL } from '../config/url'
// State management
const allocationData = ref([]);
const loading = ref(false);
const error = ref(null);

// Column definitions
const columnHelper = createColumnHelper();

const columns = [
    columnHelper.accessor('Date', {
        header: 'Date',
        cell: info => {
            const date = new Date(info.getValue());
            return date.toLocaleDateString();
        },
    }),
    columnHelper.accessor('Actual MTM', {
        header: 'Actual MTM',
        cell: info => {
            const value = info.getValue();
            return typeof value === 'number' ? value.toFixed(2) : value;
        },
    }),
    columnHelper.accessor('Settlement Price', {
        header: 'Settlement Price',
        cell: info => {
            const value = info.getValue();
            return typeof value === 'number' ? value.toFixed(2) : value;
        },
    }),
    columnHelper.accessor('Abhinav', {
        header: 'Abhinav',
        cell: info => {
            const value = info.getValue();
            return typeof value === 'number' ? value.toFixed(2) : value;
        },
    }),
    columnHelper.accessor('Ashwin', {
        header: 'Ashwin',
        cell: info => {
            const value = info.getValue();
            return typeof value === 'number' ? value.toFixed(2) : value;
        },
    }),
    columnHelper.accessor('Darshana', {
        header: 'Darshana',
        cell: info => {
            const value = info.getValue();
            return typeof value === 'number' ? value.toFixed(2) : value;
        },
    }),
    columnHelper.accessor('Nilesh', {
        header: 'Nilesh',
        cell: info => {
            const value = info.getValue();
            return typeof value === 'number' ? value.toFixed(2) : value;
        },
    }),
    columnHelper.accessor('Prahlad', {
        header: 'Prahlad',
        cell: info => {
            const value = info.getValue();
            return typeof value === 'number' ? value.toFixed(2) : value;
        },
    }),
];

// Fetch allocation data
const fetchAllocationData = async () => {
    try {
        loading.value = true;
        error.value = null;
        
        const token = localStorage.getItem('access_token');
        if (!token) throw new Error('User not authenticated');

        const response = await fetch(`${API_BASE_URL}userpnl`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Failed to fetch allocation data');
        
        const data = await response.json();
        
        // Transform the data if needed
        allocationData.value = Array.isArray(data) ? data.map(item => ({
            'Date': item.Date || item.date || item.timestamp,
            'Actual MTM': item['Actual MTM'] || item.actual_mtm || 0,
            'Settlement Price': item['Settlement Price'] || item.settlement_price || 0, 
            'Abhinav': item.Abhinav || 0,
            'Ashwin': item.Ashwin || 0,
            'Darshana': item.Darshana || 0,
            'Nilesh': item.Nilesh || 0,
            'Prahlad': item.Prahlad || 0
        })) : [];
    } catch (err) {
        error.value = err.message;
        console.error('Error fetching allocation data:', err);
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchAllocationData();
});
</script>

<style scoped>
.pageContainer {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.page-title {
    font-size: 28px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 32px;
    text-align: center;
}

.table-container {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    margin-top: 24px;
}

.loading-state {
    text-align: center;
    padding: 48px;
    color: #6b7280;
}

.loader {
    border: 4px solid #f3f3f3;
    border-radius: 50%;
    border-top: 4px solid #3b82f6;
    width: 48px;
    height: 48px;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error-message {
    background-color: #fee2e2;
    border: 1px solid #ef4444;
    color: #dc2626;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.retry-button {
    background-color: #dc2626;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.retry-button:hover {
    background-color: #b91c1c;
}

.no-data {
    text-align: center;
    padding: 48px;
    color: #6b7280;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

@media (max-width: 640px) {
    .pageContainer {
        padding: 16px;
    }

    .page-title {
        font-size: 24px;
        margin-bottom: 24px;
    }
}

/* Add styles for number formatting */
:deep(.positive-value) {
    color: #059669;
}

:deep(.negative-value) {
    color: #dc2626;
}

/* Add styles for the table cells */
:deep(.table-cell) {
    text-align: right;
    font-family: 'Inter', monospace;
}

:deep(.date-cell) {
    text-align: left;
}
</style> 