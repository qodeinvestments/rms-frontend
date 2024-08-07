<template>
    <div>
        <label v-if="label" :for="selectId">{{ label }}</label>
        <select :id="selectId" v-model="selectedValue" @change="handleChange">
            <option v-for="option in options" :key="option" :value="option">
                {{ option }}
            </option>
        </select>
    </div>
</template>

<script>
export default {
    name: "CustomSelect",
    props: {
        options: {
            type: Array,
            required: true,
            default: () => [],
        },
        modelValue: {
            type: [String, Number],
            default: '',
        },
        label: {
            type: String,
            default: '',
        },
        selectId: {
            type: String,
            default: () => `select-${Math.random().toString(36).substr(2, 9)}`,
        },
    },
    emits: ['update:modelValue'],
    data() {
        return {
            selectedValue: this.modelValue,
        };
    },
    watch: {
        modelValue(newValue) {
            this.selectedValue = newValue;
        },
    },
    methods: {
        handleChange(event) {
            this.$emit('update:modelValue', this.selectedValue);
        },
    },
};
</script>

<style scoped>
select {
    padding: 8px;
    font-size: 16px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}
</style>