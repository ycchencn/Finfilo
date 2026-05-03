<script setup>

import { FilterMatchMode, FilterOperator } from '@primevue/core/api';
import { onBeforeMount, reactive, ref } from 'vue';
import axios from 'axios';

const customers1 = ref(null);
const filters1 = ref(null);
const loading1 = ref(null);

function getProfitSeverity(profit) {
    if (profit > 0){
        return 'success';
    }
    return 'danger';
}

onBeforeMount(() => {
    axios.get('/api/backtest_tasks').then(response => {
        customers1.value = response.data;
        loading1.value = false;
    });
    initFilters1();
});

function initFilters1() {
    filters1.value = {
        global: { value: null, matchMode: FilterMatchMode.CONTAINS },
        stock_code: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
    };
}

function formatCurrency(value) {
    return value.toLocaleString('zh-EN', { style: 'currency', currency: 'CNY' });
}

</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">Filtering</div>
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
            <template #empty> No data found. </template>
            <template #loading> Loading customers data. Please wait. </template>
            <Column field="stock_code" filterField="stock_code" header="Stock Code" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ data.stock_code }} - {{ data.stock_name }}
                </template>
            </Column>
            <Column header="Start Value" filterField="start_value" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ formatCurrency(data.start_value) }}
                </template>
            </Column>
            <Column header="End Value" filterField="end_value" :showFilterMatchModes="false" :filterMenuStyle="{ width: '14rem' }" style="min-width: 14rem">
                <template #body="{ data }">
                    {{ formatCurrency(data.end_value) }}
                </template>
            </Column>
            <Column header="Profit" filterField="date" dataType="numeric" style="min-width: 10rem">
                <template #body="{ data }">
                    <Tag :value="formatCurrency(data.profit)" :severity="getProfitSeverity(data.profit)" />
                </template>
            </Column>
            <Column header="Max Drawdown" field="status" :filterMenuStyle="{ width: '14rem' }" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ data.max_drawdown }} %
                </template>
            </Column>
            <Column header="Annualized Return" :showFilterMatchModes="false" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ (data.annualized_return * 100).toFixed(2) }} %
                </template>
            </Column>
            <Column header="Calmar Ratio" filterField="balance" dataType="numeric" style="min-width: 10rem">
                <template #body="{ data }">
                     <Rating :modelValue="data.calmar_ratio" readonly />
                </template>
            </Column>
            <Column field="verified" header="Period" dataType="boolean" bodyClass="text-center" style="min-width: 8rem">
                <template #body="{ data }">
                    {{ data.start_date }} ~ {{ data.end_date }}
                </template>
            </Column>
            <Column field="verified" header="BackTest Date" dataType="boolean" bodyClass="text-center" style="min-width: 8rem">
                <template #body="{ data }">
                    {{ data.created_at }}
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
