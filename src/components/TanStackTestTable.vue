<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router';
const router = useRouter();
import {
    useVueTable,
    FlexRender,
    getCoreRowModel,
    getPaginationRowModel,
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

const checkNavigate = (data) => {
    if (props.navigateTo[data.id.substring(2)]) {
        let link = props.navigateTo[data.id.substring(2)] + data.getValue()
        router.push(link);
    }
}

// Create a ref for the data to make it reactive
const data = ref(props.data)

// Watch the prop `data` and update the reactive `data` variable
watch(() => props.data, (newData) => {
    data.value = newData
}, { immediate: true })


const sorting = ref([])
const filter = ref('')

// Initialize the table using the useVueTable hook
const table = useVueTable({
    get data() {
        return data.value
    },
    columns: props.columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
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

const handleMouseWheel = (event) => {
    const container = document.querySelector('.table-container');
    if (event.deltaY !== 0) {
        container.scrollLeft += event.deltaY;
        event.preventDefault();
    }
}

onMounted(() => {
    const container = document.querySelector('.table-container');
    container.addEventListener('wheel', handleMouseWheel);
})

onUnmounted(() => {
    const container = document.querySelector('.table-container');
    container.removeEventListener('wheel', handleMouseWheel);
})

</script>

<template>
    <div class="px-4 sm:px-6 lg:px-8 pb-8 bg-white drop-shadow-sm">
        <div class="mt-8 flow-root">
            <div class="my-4">
                <input type="text" class="border border-gray-400 rounded px-2 py-2" placeholder="Search"
                    v-model="filter" v-if="showPagination" />
            </div>
            <div class="table-container -mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
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
                            <tr v-for="row in table.getRowModel().rows" :key="row.id">
                                <td v-for="(cell, index) in row.getVisibleCells()" :key="cell.id"
                                    class="maxwidth150 break-words whitespace-normal px-3 py-4 text-sm text-black-600"
                                    :class="{
                                        'sticky-column': index === 0,
                                        'red': cell.getValue() < 0 && hasColor.includes(cell.id.substring(2)),
                                        'green': cell.getValue() > 0 && hasColor.includes(cell.id.substring(2)),
                                        'redbackground': hasRowcolor && hasRowcolor.arrayValues.includes(cell.row.original[hasRowcolor.columnName]),
                                        'greenbackground': hasRowcolor && !(hasRowcolor.arrayValues.includes(cell.row.original[hasRowcolor.columnName]))
                                    }" @click="checkNavigate(cell)">
                                    <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="mt-8" v-if="showPagination">
                Page {{ table.getState().pagination.pageIndex + 1 }} of
                {{ table.getPageCount() }} -
                {{ table.getFilteredRowModel().rows.length }} results
            </div>
            <div class="mt-8 space-x-4" v-if="showPagination">
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="table.setPageSize(5)">
                    Page Size 5
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="table.setPageSize(10)">
                    Page Size 10
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="table.setPageSize(20)">
                    Page Size 20
                </button>
            </div>
            <div class="space-x-4 mt-8" v-if="showPagination">
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="table.setPageIndex(0)">
                    First page
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="table.setPageIndex(table.getPageCount() - 1)">
                    Last page
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="!table.getCanPreviousPage()" @click="table.previousPage()">
                    Prev page
                </button>
                <button class="border border-gray-300 rounded px-2 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="!table.getCanNextPage()" @click="table.nextPage()">
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
    background-color: rgb(255, 215, 215);
}

.greenbackground {
    background-color: rgb(217, 246, 217);
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

.sticky-header:nth-child(1) {
    left: 0px;
    /* Adjust as per the width of the first column */
}

.table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
</style>
