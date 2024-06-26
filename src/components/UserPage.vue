<template>
  <div class="userPage">
    <h1>Hello my name is {{ name }}</h1>

  </div>
</template>

<script>
export default {
  data() {
    return {
      name: 'Testing'
    }
  },
  created() {
    this.name = this.$route.params.username
  }
}
</script>

<style scoped>
.userPage {
  color: black;
}
</style>
