<script setup>

import { FilterMatchMode, FilterOperator } from '@primevue/core/api';
import { onBeforeMount, reactive, ref } from 'vue';
import axios from 'axios';
const news = ref(null);
const filters1 = ref(null);
const loading1 = ref(null);
const filters_topic = ref('*');

onBeforeMount(() => {

});

</script>

<template>

</template>

<style scoped>

</style>
