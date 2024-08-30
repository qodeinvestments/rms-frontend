<script setup>
import { ref, watchEffect, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router';
const router = useRouter();
import {
    useVueTable,
    FlexRender,
    getCoreRowModel,
    getSortedRowModel,
    getFilteredRowModel,
} from '@tanstack/vue-table'

// Define the props
const props = defineProps({
    data: {
        type: Array,
        required: true
    },
    columns: {
        type: Array,
        required: true
    },
    hasColor: {
        type: Array,
        required: true
    },
    navigateTo: {
        type: Object,
        required: true
    },
    showPagination: {
        type: Boolean,
        required: true
    },
    hasRowcolor: {
        type: Object,
        required: false
    }
})

const tellnav = (data) => {
    return props.navigateTo[data.id.substring(2)];
}
const checkNavigate = (data) => {

    if (props.navigateTo[data.id.substring(2)]) {
        let link = props.navigateTo[data.id.substring(2)] + data.getValue()
        router.push(link);
    }
}

const sorting = ref([])
const filter = ref('')

// Custom pagination state
const currentPage = ref(0)
const pageSize = ref(5)

// Initialize the table using the useVueTable hook
const table = useVueTable({
    get data() {
        return props.data
    },
    columns: props.columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
        get sorting() {
            return sorting.value
        },
        get globalFilter() {
            return filter.value
        },
    },
    onSortingChange: updaterOrValue => {
        sorting.value =
            typeof updaterOrValue === 'function'
                ? updaterOrValue(sorting.value)
                : updaterOrValue
    },
})

// Computed properties for pagination
const pageCount = ref(0)
const rows = ref([])

watchEffect(() => {
    const filteredRows = table.getFilteredRowModel().rows
    const sortedRows = table.getSortedRowModel().rows
    const finalRows = sortedRows.length > 0 ? sortedRows : filteredRows

    pageCount.value = Math.ceil(finalRows.length / pageSize.value)
    const start = currentPage.value * pageSize.value
    const end = start + pageSize.value
    rows.value = finalRows.slice(start, end)
})

// Pagination methods
const nextPage = () => {
    if (currentPage.value < pageCount.value - 1) {
        currentPage.value++
    }
}

const previousPage = () => {
    if (currentPage.value > 0) {
        currentPage.value--
    }
}

const setPageSize = (size) => {
    pageSize.value = size
    currentPage.value = 0  // Reset to first page when changing page size
}

const handleMouseWheel = (event) => {
    const container = event.currentTarget;
    if (container) {
        container.scrollLeft += event.deltaY;
        event.preventDefault();
    }
}

onMounted(() => {
    const containers = document.querySelectorAll('.table-container');
    containers.forEach(container => {
        container.addEventListener('wheel', handleMouseWheel, { passive: false });
    });
})

onUnmounted(() => {
    const containers = document.querySelectorAll('.table-container');
    containers.forEach(container => {
        container.removeEventListener('wheel', handleMouseWheel);
    });
})

</script>

<template>
    <div class="px-4 sm:px-6 lg:px-8 pb-8 bg-white drop-shadow-sm">
        <div class="mt-8 flow-root">
            <div class="my-4">
                <input type="text" class="border border-gray-400 rounded px-2 py-2" placeholder="Search"
                    v-model="filter" v-if="showPagination" />
            </div>
            <div class="table-container -mx-4 -my-2 overflow-x-auto overflow-y-auto sm:-mx-6 lg:-mx-8">
                <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                    <table class="min-w-full divide-y divide-gray-300">
                        <thead>
                            <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
                                <th v-for="header in headerGroup.headers" :key="header.id" scope="col"
                                    class="whitespace-nowrap px-3 py-3.5 text-left text-sm font-semibold text-gray-900 borderright"
                                    :class="{
                                        'cursor-pointer select-none': header.column.getCanSort(),
                                        'sticky-header': header.index === 0,
                                    }" @click="header.column.getToggleSortingHandler()?.($event)">
                                    <FlexRender :render="header.column.columnDef.header" :props="header.getContext()" />
                                    {{ { asc: ' ↑', desc: '↓' }[header.column.getIsSorted()] }}
                                </th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            <tr v-for="row in rows" :key="row.id">
                                <td v-for="(cell, index) in row.getVisibleCells()" :key="cell.id"
                                    class="maxwidth150 break-words whitespace-normal px-3 py-4 text-sm text-black-600"
                                    :class="{
                                        'sticky-column': index === 0,
                                        'red': cell.getValue() < 0 && hasColor.includes(cell.id.split('_').slice(1).join('_')),
                                        'green': cell.getValue() > 0 && hasColor.includes(cell.id.split('_').slice(1).join('_')),
                                        'cursorpointer': tellnav(cell)
                                        // 'redbackground': hasRowcolor && hasRowcolor.arrayValues.includes(cell.row.original[hasRowcolor.columnName]),
                                        // 'greenbackground': hasRowcolor && !(hasRowcolor.arrayValues.includes(cell.row.original[hasRowcolor.columnName]))
                                    }" @click="checkNavigate(cell)">
                                    <template v-if="cell.getValue() !== undefined">
                                        <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
                                    </template>
                                    <template v-else>
                                        N/A
                                    </template>
                                </td>
                                <!-- <td v-for="(cell, index) in row.getVisibleCells()" :key="cell.id"
                                    class="maxwidth150 break-words whitespace-normal px-3 py-4 text-sm text-black-600"
                                    :class="{
                                        'sticky-column': index === 0,
                                        'red': cell.getValue() < 0 && hasColor.includes(cell.id.split('_').slice(1).join('_')),
                                        'green': cell.getValue() > 0 && hasColor.includes(cell.id.split('_').slice(1).join('_')),
                                        'redbackground': hasRowcolor && hasRowcolor.arrayValues.includes(cell.row.original[hasRowcolor.columnName]),
                                        'greenbackground': hasRowcolor && !(hasRowcolor.arrayValues.includes(cell.row.original[hasRowcolor.columnName]))
                                    }" @click="checkNavigate(cell)">
                                    <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
                                </td> -->
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="mt-8" v-if="showPagination">
                Page {{ currentPage + 1 }} of {{ pageCount }} -
                {{ table.getFilteredRowModel().rows.length }} results
            </div>
            <div class="mt-8 space-x-4" v-if="showPagination">
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="setPageSize(5)">
                    Page Size 5
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="setPageSize(10)">
                    Page Size 10
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="setPageSize(20)">
                    Page Size 20
                </button>
            </div>
            <div class="space-x-4 mt-8" v-if="showPagination">
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="currentPage = 0">
                    First page
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="currentPage = pageCount - 1">
                    Last page
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="currentPage === 0" @click="previousPage">
                    Prev page
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="currentPage === pageCount - 1" @click="nextPage">
                    Next page
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.colorcontainer {
    background: pink;
}

.red {
    color: red;
}

.green {
    color: rgb(80, 185, 80);
}

.redbackground {
    background-color: rgb(255, 215, 215) !important;
}

.greenbackground {
    background-color: rgb(217, 246, 217) !important;
}

.cursorpointer {
    cursor: pointer;
}

table {
    border-right: none;
    border-left: none;
}

::-webkit-scrollbar {
    width: 2px;
    height: 2px;
}

/* Track */
::-webkit-scrollbar-track {
    background: #f1f1f1;
}

/* Handle */
::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
    background: #555;
}

.borderright {
    border-right: none;
}

.backred {
    background: red;
}

.maxwidth150 {
    max-width: 150px;
}

.sticky-header {
    position: sticky;
    left: 0;
    z-index: 1;
    background: white;
}

.sticky-column {
    position: sticky;
    left: 0;
    z-index: 1;
}

.sticky-column:nth-child(1) {
    background: white;
}

.sticky-header:nth-child(1) {
    left: 0px;

    /* Adjust as per the width of the first column */
}

.table-container {
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    max-width: 100%;
    width: 100%;
}

/* Add a min-width to the table to ensure horizontal scrolling when needed */
table {
    min-width: 100%;
}
</style>
