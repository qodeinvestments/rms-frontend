<template>
    <div class="warningsignal-container text-sm font-semibold">
        <div class="signal-container">
            <p class="textContainer"> Strategy :</p>
            <span :class="signals.pulse_run_strats ? 'greensignal' : 'redsignal'"></span>
        </div>
        <div class="signal-container">
            <p class="textContainer"> Web Socket 3 :</p>
            <span :class="signals.pulse_web_socket3 ? 'greensignal' : 'redsignal'"></span>
        </div>
        <div class="signal-container">
            <p class="textContainer"> Web Socket 4 :</p>
            <span :class="signals.pulse_web_socket4 ? 'greensignal' : 'redsignal'"></span>
        </div>
        <div class="signal-container">
            <p class="textContainer">BackEnd Connection :</p>
            <span :class="signals['backendConnection'] ? 'greensignal' : 'redsignal'"></span>
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
    }
});

const { signals } = toRefs(props);

// watch(signals, (newSignals) => {
//     // React to changes in the signals prop if needed
// }, { immediate: true });
</script>

<style>
.warningsignal-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-content: center;
    width: 100%;
    margin-top: 40px;
    gap: 10px;
}

.signal-container {
    display: flex;
    justify-content: flex-end;
    align-content: flex-end;
    margin-right: 20px;
    gap: 20px;
}

.textContainer {
    display: flex;
    align-items: center;
    justify-content: center;
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
