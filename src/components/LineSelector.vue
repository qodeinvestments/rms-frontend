<template>
    <div class="line-selector">
        <h3>Select Lines to Display</h3>
        <input type="text" v-model="searchQuery" placeholder="Search lines..." class="search-input">
        <div class="line-options-container">
            <div v-for="(line, index) in filteredLines" :key="index" class="line-option">
                <input type="checkbox" :id="'line-' + index" :value="index" v-model="selectedLines"
                    @change="updateChart">
                <label :for="'line-' + index">{{ line }}</label>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'LineSelector',
    props: {
        lines: {
            type: Array,
            required: true
        },
        visibleLines: {
            type: Array,
            required: true
        }
    },
    data() {
        return {
            selectedLines: [],
            searchQuery: ''
        }
    },
    computed: {
        filteredLines() {
            if (!this.searchQuery) return this.lines;
            const query = this.searchQuery.toLowerCase();
            return this.lines.filter(line => line.toLowerCase().includes(query));
        }
    },
    watch: {
        visibleLines: {
            handler(newVisibleLines) {
                this.selectedLines = newVisibleLines;
            },
            immediate: true
        }
    },
    methods: {
        updateChart() {
            this.$emit('update-visibility', this.selectedLines)
        }
    }
}
</script>

<style scoped>
.line-selector {
    margin-top: 20px;
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 5px;
    background-color: #f9f9f9;
}

.search-input {
    width: 100%;
    padding: 8px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.line-options-container {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid #eee;
    padding: 5px;
}

.line-option {
    margin: 10px 0;
}

input[type="checkbox"] {
    margin-right: 10px;
}

label {
    cursor: pointer;
}
</style>