<!-- src/components/TimeTable.vue -->
<template>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Time</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="row in tableData" :key="row.id">
                <td>{{ row.id }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.time }}</td>
            </tr>
        </tbody>
    </table>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { useTable } from '@tanstack/vue-table';

export default {
    name: 'TimeTable',
    setup() {
        // Initial data for the table
        const data = ref([
            { id: 1, name: 'Alice' },
            { id: 2, name: 'Bob' },
        ]);

        // Function to update the time column
        const updateTime = () => {
            data.value = data.value.map((row) => ({
                ...row,
                time: new Date().toLocaleTimeString(),
            }));
        };

        // Update the time every second
        let interval;
        onMounted(() => {
            updateTime();
            interval = setInterval(updateTime, 1000);
        });

        onUnmounted(() => {
            clearInterval(interval);
        });

        return {
            tableData: data,
        };
    },
};
</script>