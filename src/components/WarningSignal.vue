<template>
    <div class="warningsignal-container">
        <div class="signal-container" v-for="(value, key) in filteredSignals()" :key="key">
            <div class="textContainer">{{ key }}</div>
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
            <span class="latency">{{ latency }}</span>
        </div>

        <div class="signal-container">
            <p class="textContainer">FrontToBack Max Latency :</p>
            <span class="latency">{{ max_latency }}</span>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const userAnd = ref(true);
const router = useRouter();

const gotomispospage = () => router.push('/posmismatch');

const toTitleCase = (str) =>
    str
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

const filteredSignals = () => {
    const val = Object.fromEntries(
        Object.entries(props.signals)
            .filter(([key]) =>
                !key.startsWith('pulse_trader_xts') &&
                !key.startsWith('pulse_trader_zerodha') &&
                !key.startsWith('position_mismatch')
            )
            .map(([key, value]) => [toTitleCase(key), value])
    );

    const user = Object.fromEntries(
        Object.entries(props.signals).filter(([key]) =>
            key.startsWith('pulse_trader_xts') ||
            key.startsWith('pulse_trader_zerodha')
        )
    );

    let and = true;
    for (let key in user) {
        and = and && user[key];
    }
    userAnd.value = and;

    return val;
};

const props = defineProps({
    signals: {
        type: Object,
        required: true,
    },
    latency: {
        type: Number,
        required: true,
    },
    max_latency: {
        type: Number,
        required: true,
    },
});

const calculate_position_mismatch = () => {
    const val = props.signals.position_mismatch;
    let tell = true;
    let ans = [];

    for (const v in val) {
        if (val.hasOwnProperty(v)) {
            tell = tell && Object.keys(val[v]).length === 0;
            if (Object.keys(val[v]).length !== 0) {
                ans.push({ [v]: val[v] });
            }
        }
    }
    return tell;
};
</script>

<style scoped>
p {
    margin: 0 !important;
}

.warningsignal-container {

    display: grid;
    grid-template-columns: repeat(3, 1fr);
    /* 3 containers per row */
    gap: 15px;
    padding: 20px;
    align-items: stretch;
    /* Ensure all containers stretch to the same height */
}

.signal-container {
    background: white !important;
    display: flex;
    gap: 20px;
    /* Stack text and signal vertically */
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 6px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;

    width: 100%;
    /* Full width */
    height: 100%;
    /* Ensures it stretches to match other containers */
    box-sizing: border-box;
}

.textContainer {
    display: flex;
    align-items: center;
    justify-content: center;
    /* Spacing between text and signal */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.latency {
    min-width: 80px;
}

.greensignal,
.redsignal {
    width: 30px;
    height: 30px;
    border-radius: 50%;
}

.greensignal {
    background-color: green;
    border: 1px solid green;
}

.redsignal {
    background-color: red;
    border: 1px solid red;
}
</style>