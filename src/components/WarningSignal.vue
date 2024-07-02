<template>
    <div class="warningsignal-container text-sm font-semibold">
        <div class="signal-container">
            <p class="textContainer"> DataBase :</p>
            <span :class="signals[0] === 1 ? 'greensignal' : 'redsignal'"></span>
        </div>
        <div class="signal-container">
            <p class="textContainer"> Order Management :</p>
            <span :class="signals[0] === 1 ? 'greensignal' : 'redsignal'"></span>
        </div>
        <div class="signal-container">
            <p class="textContainer"> Broker Connection :</p>
            <span :class="signals[0] === 1 ? 'greensignal' : 'redsignal'"></span>
        </div>

    </div>

</template>

<script setup>

import { ref } from 'vue'
const signals = ref([1, 1, 1]);
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