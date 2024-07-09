<template>
    <div class="hello-notification">
        Hello
    </div>
</template>

<script>
export default {
    name: 'Toast',
};
</script>

<style scoped>
.hello-notification {
    position: fixed;
    bottom: 10px;
    right: 10px;
    background-color: #f0f0f0;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    z-index: 1000;
}
</style>