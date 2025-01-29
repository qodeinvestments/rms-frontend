<script setup>
import { ref, watchEffect, onMounted, onUnmounted ,computed} from 'vue'
import { useRouter } from 'vue-router';
const router = useRouter();
import {
    useVueTable,
    FlexRender,
    getCoreRowModel,
    getSortedRowModel,
    getFilteredRowModel,
} from '@tanstack/vue-table'
import * as XLSX from 'xlsx';

const copyToClipboard = () => {
    // Get visible columns and clean up their headers
    const visibleColumns = table.getVisibleLeafColumns()
    
    // Clean up header names by removing the '() =>' prefix and quotes
    const headerRow = visibleColumns
        .map(column => {
            const headerText = column.columnDef.header
            if (typeof headerText === 'function') {
                // If header is a function that returns a string, execute it
                return headerText().replace(/^'|'$/g, '') // Remove quotes if present
            } else if (typeof headerText === 'string') {
                // If it's already a string, just return it
                return headerText
            }
            // Fallback
            return column.id
        })
        .join('\t')
    
    // Create data rows
    const dataRows = table.getFilteredRowModel().rows
        .map(row => {
            return visibleColumns
                .map(column => {
                    const value = row.getValue(column.id)
                    // Format numbers using the existing formatIndianNumber function
                    return typeof value === 'number' 
                        ? formatIndianNumber(value)
                        : value ?? 'N/A'
                })
                .join('\t')
        })
        .join('\n')
    
    // Combine headers and data
    const clipboardText = `${headerRow}\n${dataRows}`
    
    // Copy to clipboard
    navigator.clipboard.writeText(clipboardText)
        .then(() => {
            alert('Table copied to clipboard!')
        })
        .catch(err => {
            console.error('Failed to copy table:', err)
            alert('Failed to copy table to clipboard')
        })
}


const download = (type) => {
    const file_name = props.title + '.' + type
    const data = props.data
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(data);
    XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
    XLSX.writeFile(wb, file_name);
}


// Define the props
const props = defineProps({
    data: {
        type: Array,
        required: true
    },
    showPin:{
        type:Boolean,
        required:false
    },
    title: {
        type: String,
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
const toggleAllColumns = (value) => {
  table.toggleAllColumnsVisible(value)
}

const isAllColumnsVisible = computed(() => {
  return table.getIsAllColumnsVisible()
})

// Custom pagination state
const currentPage = ref(0)
const pageSize = ref(10)

// Add this after your existing refs
const columnVisibility = ref({})

// Modify your table initialization to include column visibility state
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
    get columnVisibility() {
      return columnVisibility.value
    }
  },
  onSortingChange: updaterOrValue => {
    sorting.value =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(sorting.value)
        : updaterOrValue
  },
  onColumnVisibilityChange: updaterOrValue => {
    columnVisibility.value =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(columnVisibility.value)
        : updaterOrValue
  },
})

// Computed properties for pagination
const pageCount = ref(0)
const rows = ref([])

// Add this after the existing imports
// Add after imports
const formatIndianNumber = (value) => {
    if (value === null || value === undefined || value === '') return value;

    const num = Number(value);
    if (isNaN(num)) return value;

    // Handle the negative sign
    const isNegative = num < 0;
    const absoluteNum = Math.abs(num);

    // Format to 2 decimal places first
    const formattedDecimal = absoluteNum.toFixed(2);
    const [integerPart, decimalPart] = formattedDecimal.split('.');
    
    const lastThree = integerPart.slice(-3);
    const remaining = integerPart.slice(0, -3);

    const withCommas = remaining
        ? remaining.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree
        : lastThree;

    // Decimal part is now always present due to toFixed(2)
    const formattedNumber = `${withCommas}.${decimalPart}`;

    // Add back the negative sign if necessary
    return isNegative ? `-${formattedNumber}` : formattedNumber;
};


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
    <div>
        <p class="table-heading">{{ title }}</p>
        <div class="px-4 sm:px-6 lg:px-8 pb-8 bg-white drop-shadow-sm">
            <div v-if="showPin" class="column-visibility-controls mb-4 border rounded-md p-4">
                <div class="mb-2 border-b pb-2">
                    <label class="flex items-center">
                        <input
                        type="checkbox"
                        :checked="isAllColumnsVisible"
                        @change="e => toggleAllColumns(e.target.checked)"
                        class="mr-2"
                        />
                        <span>Toggle All</span>
                    </label>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                    <div v-for="column in table.getAllLeafColumns()" :key="column.id">
                        <label class="flex items-center">
                        <input
                            type="checkbox"
                            :checked="column.getIsVisible()"
                            @change="column.toggleVisibility()"
                            class="mr-2"
                        />
                        <span>{{ column.id }}</span>
                        </label>
                    </div>
                </div>
            </div>

            <div class="mt-8 flow-root">
                <div class="my-4 headingContainer">
                    <input type="text" class="border border-gray-400 rounded px-2 py-2" placeholder="Search"
                        v-model="filter" v-if="showPagination" />
                    <button @click="download('csv')"
                        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                        Download CSV
                    </button>
                    <button @click="download('xlsx')"
                        class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                        Download Excel
                    </button>
                    <button 
                        @click="copyToClipboard"
                        class="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">
                        Copy to Clipboard
                    </button>
                </div>

                <div class="table-container -mx-4 -my-2 overflow-x-auto overflow-y-auto sm:-mx-6 lg:-mx-8">
                    <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                        <table class="min-w-full divide-y divide-gray-300">
                            <thead>
                                <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
                                    <th v-for="header in headerGroup.headers" :key="header.id" scope="col"
                                        class="whitespace-nowrap px-3 py-3.5 text-left text-sm font-semibold text-gray-900 borderright textcenter"
                                        :class="{
                                            'cursor-pointer select-none': header.column.getCanSort(),
                                            'sticky-header': header.index === 0,
                                        }" @click="header.column.getToggleSortingHandler()?.($event)">
                                        <FlexRender :render="header.column.columnDef.header"
                                            :props="header.getContext()" />
                                        {{ { asc: ' ↑', desc: '↓' }[header.column.getIsSorted()] }}
                                    </th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
                                <tr v-for="row in rows" :key="row.id">
                                    <td v-for="(cell, index) in row.getVisibleCells()" :key="cell.id"
                                        class="maxwidth150 minwidhth100 break-words whitespace-normal px-3 py-4 text-sm text-black-600 textcenter"
                                        :class="{
                                            'sticky-column': index === 0,
                                            'red': cell.getValue() < 0 && hasColor.includes(cell.id.split('_').slice(1).join('_')),
                                            'green': cell.getValue() > 0 && hasColor.includes(cell.id.split('_').slice(1).join('_')),
                                            'cursorpointer': tellnav(cell)
                                        }" @click="checkNavigate(cell)">
                                        <template v-if="cell.getValue() !== undefined">
                                            {{ typeof cell.getValue() === 'number' ? formatIndianNumber(cell.getValue())
                                            : cell.getValue() }}
                                        </template>

                                        <template v-else>
                                            N/A
                                        </template>
                                    </td>
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
                    <button
                        class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        @click="setPageSize(5)">
                        Page Size 5
                    </button>
                    <button
                        class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        @click="setPageSize(10)">
                        Page Size 10
                    </button>
                    <button
                        class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        @click="setPageSize(20)">
                        Page Size 20
                    </button>
                </div>
                <div class="space-x-4 mt-8" v-if="showPagination">
                    <button
                        class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        @click="currentPage = 0">
                        First page
                    </button>
                    <button
                        class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        @click="currentPage = pageCount - 1">
                        Last page
                    </button>
                    <button
                        class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        :disabled="currentPage === 0" @click="previousPage">
                        Prev page
                    </button>
                    <button
                        class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        :disabled="currentPage === pageCount - 1" @click="nextPage">
                        Next page
                    </button>
                </div>
            </div>
        </div>
    </div>

</template>

<style scoped>
.colorcontainer {
    background: pink;
}
/* Add these styles to your existing <style> section */
.column-visibility-controls {
  background-color: white;
  border-color: #e5e7eb;
}

.column-visibility-controls label {
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.column-visibility-controls input[type="checkbox"] {
  cursor: pointer;
}
.red {
    color: red;
}

.textcenter {
    text-align: center;
}

.table-heading {
    font-size: 22px;
    font-weight: 600;
    margin-left: 30px;
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
    transition: all 0.2s ease;
}

.cursorpointer:hover {
    text-decoration: underline;
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
.minwidhth100{
    min-width: 100px;
}

.maxwidth150 {
   
    max-width: 180px;
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

.headingContainer {
    display: flex;
    gap: 10px;
    align-content: flex-end;

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


</style>
