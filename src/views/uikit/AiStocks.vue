<script setup>

import { FilterMatchMode, FilterOperator } from '@primevue/core/api';
import { onBeforeMount, reactive, ref } from 'vue';
import axios from 'axios';

const customers1 = ref(null);
const filters1 = ref(null);
const loading1 = ref(null);

onBeforeMount(() => {
    axios.get('/api/v1/watch_list').then(response => {
        customers1.value = response.data;
        loading1.value = false;
    });
    initFilters1();
});

function initFilters1() {
    filters1.value = {
        global: { value: null, matchMode: FilterMatchMode.CONTAINS },
        stock_code: {
            operator: FilterOperator.AND,
            constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }]
        }
    };
}

</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">AI自选股 - 每周自动更新热门板块头部上市公司</div>
        <DataTable
            :value="customers1"
            :paginator="true"
            :rows="25"
            dataKey="id"
            :rowHover="true"
            filterDisplay="menu"
            :loading="loading1"
            :globalFilterFields="['name', 'country.name', 'representative.name', 'balance', 'status']"
            showGridlines
        >
            <template #header>
                <div class="flex justify-between">
                    <Button type="button" icon="pi pi-filter-slash" label="Clear" outlined @click="clearFilter()" />
                    <IconField>
                        <InputIcon>
                            <i class="pi pi-search" />
                        </InputIcon>
                        <InputText v-model="filters1['global'].value" placeholder="Keyword Search" />
                    </IconField>
                </div>
            </template>
            <template #empty> No data found.</template>
            <template #loading> Loading customers data. Please wait.</template>
            <Column field="stock_code" filterField="stock_code" header="Stock Code" style="min-width: 12rem">
                <template #body="{ data }">
                    <a :href="'https://www.iwencai.com/unifiedwap/result?w=' + data.stock_code" target="_blank"><Tag :value="data.stock_code" severity="info" /></a> <br/> {{ data.stock_name }}
                </template>
            </Column>
            <Column header="行业板块" filterField="end_value" :showFilterMatchModes="false"
                    :filterMenuStyle="{ width: '14rem' }" style="min-width: 14rem">
                <template #body="{ data }">
                    <Tag :value="data.topic" severity="success" /> <br/> {{ data.desc }}
                </template>
            </Column>
            <Column field="verified" header="自动创建于" dataType="boolean" bodyClass="text-center"
                    style="min-width: 8rem">
                <template #body="{ data }">
                    {{ data.created_at }}
                </template>
            </Column>
            <Column field="verified" header="策略追踪" dataType="boolean" bodyClass="text-center" style="min-width: 8rem">
                <template #body="{ data }">
                    <ToggleSwitch v-model="checked" />
                </template>
            </Column>
            <Column field="verified" header="操作" dataType="boolean" bodyClass="text-center" style="min-width: 8rem">
                <template #body="{ data }">
                    <Button label="设置" severity="secondary" />
                </template>
            </Column>
        </DataTable>
    </div>

</template>

<style scoped lang="scss">
:deep(.p-datatable-frozen-tbody) {
    font-weight: bold;
}

:deep(.p-datatable-scrollable .p-frozen-column) {
    font-weight: bold;
}
</style>
