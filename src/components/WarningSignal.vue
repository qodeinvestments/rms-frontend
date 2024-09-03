<template>
    <div class="warningsignal-container text-sm font-semibold">
        <div class="signal-container" v-for="(value, key) in filteredSignals()" :key="key">
            <div class="textContainer"> {{ key }} </div>
            <span :class="value ? 'greensignal' : 'redsignal'"></span>
        </div>
        <div class="signal-container">
            <p class="textContainer">User Error :</p>
            <span :class="userAnd ? 'greensignal' : 'redsignal'"></span>
        </div>
        <div class="signal-container" @click="gotomispospage">
            <p class="textContainer">Position Mismatch :</p>
            <span :class="calculate_position_mismatch() ? 'greensignal' : 'redsignal'"></span>

        </div>
        <div class="signal-container">
            <p class="textContainer">FrontToBack Latency :</p>
            <span>{{ latency }}</span>
        </div>
        <div class="signal-container">
            <p class="textContainer"> FrontToBack Max Latency :</p>
            <span>{{ max_latency }}</span>
        </div>
    </div>
</template>

<script setup>

import { watch } from 'vue';
import { toRefs } from 'vue';
import { ref } from 'vue'
import { useRouter } from 'vue-router';
const userAnd = ref(true)
const router = useRouter();

const gotomispospage = () => {
    router.push('/posmismatch'); // Use the router instance from useRouter
};

const filteredSignals = () => {
    const val = Object.fromEntries(
        Object.entries(props.signals).filter(([key, value]) => {
            return !key.startsWith('pulse_trader_xts') && !key.startsWith('pulse_trader_zerodha') && !key.startsWith('position_mismatch');
        })
    );
    const user = Object.fromEntries(
        Object.entries(props.signals).filter(([key, value]) => {
            return key.startsWith('pulse_trader_xts') || key.startsWith('pulse_trader_zerodha');
        })
    );
    let and = true;
    for (let key in user) {
        and = and & user[key];
    }
    userAnd.value = and;
    return val;
}
const props = defineProps({
    signals: {
        type: Object,
        required: true,
    },
    latency: {
        type: Number,
        required: true
    },
    max_latency: {
        type: Number,
        required: true
    },
});
const { signals } = toRefs(props);
const calculate_position_mismatch = () => {
    const val = props.signals.position_mismatch;;
    let tell = true;
    let ans = [];
    for (const v in val) {
        if (val.hasOwnProperty(v)) {
            tell = tell && (Object.keys(val[v]).length === 0);
            if (Object.keys(val[v]).length !== 0) {
                ans.push({ [v]: val[v] });
            }
        }
    }
    return tell;
}
const route = useRouter();


// watch(signals, (newSignals) => {
//     // React to changes in the signals prop if needed
// }, { immediate: true });
</script>

<style>
.warningsignal-container {
    display: grid;
    grid-template-rows: repeat(3, 1fr);
    grid-template-columns: repeat(3, 1fr);
    grid-column-gap: 30px;
    grid-row-gap: 15px;
    margin-right: 30px;
}

.signal-container {
    display: flex;
    justify-content: flex-start;
    align-content: flex-start;

}

.textContainer {
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    width: 100%;
    white-space: nowrap;
}

.greensignal {
    background: green;
    border: 1px solid green;
    width: 30px;
    height: 30px;
}

.redsignal {
    background: red;
    border: 1px solid red;
    width: 30px;
    height: 30px;
}
</style>
