<script setup>

import { FilterMatchMode, FilterOperator } from '@primevue/core/api';
import { computed, onBeforeMount, ref } from 'vue';
import { getProfitSeverity, getMarketByCode } from '@/utils/function.js';
import axios from 'axios';

const customers1 = ref(null);
const filters1 = ref(null);
const loading1 = ref(null);
const first = computed(() => currentPage * 25);
const page_storage_key = 'quant_record_current_page'
let currentPage = ref(0);

function onPageChange(event) {
    currentPage = event.page;
    localStorage.setItem(page_storage_key, currentPage);
}

onBeforeMount(() => {
    let savedPage = localStorage.getItem(page_storage_key);
    if (savedPage) {
        currentPage = parseInt(savedPage, 10);
    } else {
        currentPage = 0
    }
    axios.get('/api/v1/backtest_tasks').then(response => {
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
        <div class="font-semibold text-xl mb-4">回测记录</div>
        <DataTable
            tableStyle="font-size:12px"
            :first="first"
            @page="onPageChange"
            :value="customers1"
            :paginator="true"
            :rows="25"
            dataKey="id"
            :rowHover="true"
            filterDisplay="menu"
            :loading="loading1"
            :globalFilterFields="['stock_code']"
            showGridlines
            :filters="filters1"
        >
            <template #header>
                <div class="flex justify-end">
                    <Button type="button" icon="pi pi-filter-slash" class="m-1" label="提交回测任务"  />
                    <IconField class="m-1">
                        <InputIcon>
                            <i class="pi pi-search" />
                        </InputIcon>
                        <InputText v-model="filters1['global'].value" placeholder="Keyword Search" />
                    </IconField>
                </div>
            </template>
            <template #empty> No data found. </template>
            <template #loading> Loading customers data. Please wait. </template>
            <Column header="期初资金" filterField="start_value" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ formatCurrency(data.start_value) }}
                </template>
            </Column>
            <Column header="期末资金" filterField="end_value" :showFilterMatchModes="false" :filterMenuStyle="{ width: '14rem' }" style="min-width: 14rem">
                <template #body="{ data }">
                    {{ formatCurrency(data.end_value) }}
                </template>
            </Column>
            <Column header="利润" filterField="date" dataType="numeric" style="min-width: 10rem">
                <template #body="{ data }">
                    <Tag :value="formatCurrency(data.profit)" :severity="getProfitSeverity(data.profit)" />
                </template>
            </Column>
            <Column header="最大回撤" field="status" :filterMenuStyle="{ width: '14rem' }">
                <template #body="{ data }">
                    {{ (data.max_drawdown).toFixed(2) }} %
                </template>
            </Column>
            <Column header="年化收益" :showFilterMatchModes="false">
                <template #body="{ data }">
                    {{ (data.annualized_return * 100).toFixed(2) }} %
                </template>
            </Column>
            <Column header="卡玛比率" filterField="balance" dataType="numeric">
                <template #body="{ data }">
                     <Rating :modelValue="data.calmar_ratio" readonly />
                </template>
            </Column>
            <Column field="verified" header="回撤周期" dataType="boolean" bodyClass="text-center" style="min-width: 8rem">
                <template #body="{ data }">
                    {{ data.start_date }} ~ {{ data.end_date }}
                </template>
            </Column>
            <Column field="verified" header="日期" dataType="boolean" bodyClass="text-center" style="min-width: 8rem">
                <template #body="{ data }">
                    {{ data.created_at }}
                </template>
            </Column>
            <Column field="verified" header="操作" dataType="boolean" bodyClass="text-center">
                <template #body="{ data }">
                    <Button as="router-link" :to="{ name: 'backtest_detail', params: { id: data.backtest_id, stock_code: data.stock_code }}" icon="pi pi-chart-scatter" variant="text" rounded aria-label="Filter" />
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
