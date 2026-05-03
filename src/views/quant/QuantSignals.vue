<script setup>

import ConfirmDialog from 'primevue/confirmdialog';
import { onBeforeMount, ref } from 'vue';
import axios from 'axios';
import { formatCurrency } from '@/utils/function';

const portfolios = ref();
const loading1 = ref(null);

onBeforeMount(() => {
    axios.get('/api/v1/investment_portfolios').then(response => {
        portfolios.value = response.data
    });
});

</script>

<template>
    <ConfirmDialog></ConfirmDialog>
    <div class="card">
        <DataTable
            tableStyle="font-size:12px"
            :value="portfolios"
            :rows="25"
            dataKey="id"
            :showGridlines="false"
            :rowHover="true"
            filterDisplay="menu"
            :loading="loading1"
            :globalFilterFields="['name']"
            :size="'large'"
            showGridlines
        >
            <template #header>
                <div class="flex flex-col md:flex-row items-center justify-between gap-3 w-full">
                    <!-- 左侧：下拉框 -->
                    <div class="w-full md:w-auto">
                        <span class="font-semibold">交易信号</span>
                    </div>
                    <!-- 右侧：按钮 + 搜索框 -->
                    <div class="flex flex-wrap items-center gap-2 w-full md:w-auto justify-end md:justify-start">
                        <Button
                            type="button"
                            icon="pi pi-plus"
                            size="small"
                            label="添加策略"
                            class="whitespace-nowrap"
                        />
                    </div>
                </div>
            </template>
            <template #empty> No data found.</template>
            <template #loading> Loading customers data. Please wait.</template>
            <Column field="name" filterField="name" header="策略名">
                <template #body="{ data }">
                    {{ data.name }}
                </template>
            </Column>
            <Column field="name" filterField="name" header="仓位" style="min-width: 8rem">
                <template #body="{ data }">
                    <ProgressBar :value="(data.summary?.position_ratio * 100).toFixed(2)"></ProgressBar>
                </template>
            </Column>
            <Column field="name" filterField="name" header="今日收益">
                <template #body="{ data }">
                    <span class="font-mono"
                      :class="{
                      'text-red-600': data.summary.daily_pnl_change > 0,
                      'text-green-600': data.summary.daily_pnl_change < 0,
                    }">
                        {{ formatCurrency(data.summary.daily_pnl_change, true) }}
                        ({{ (data.summary.daily_pnl_change / data.summary.total_assets * 100).toFixed(2) }}%)
                    </span>
                </template>
            </Column>
            <Column field="name" filterField="name" header="总资产" class="font-mono">
                <template #body="{ data }">
                    {{ formatCurrency(data.summary.total_assets) }}
                </template>
            </Column>
            <Column field="name" filterField="name" header="浮动盈亏" class="font-mono">
                <template #body="{ data }">
                    <span
                      :class="{
                      'text-red-600': data.summary.total_unrealized_pnl > 0,
                      'text-green-600': data.summary.total_unrealized_pnl < 0,
                    }">{{ formatCurrency(data.summary.total_unrealized_pnl, true) }}
                    </span>
                </template>
            </Column>
            <Column field="name" filterField="name" header="可用资金" class="font-mono">
                <template #body="{ data }">
                    {{ formatCurrency(data.current_cash) }}
                </template>
            </Column>
            <Column field="name" filterField="name" header="持仓个股">
                <template #body="{ data }">
                    {{ data.assets.length }}
                </template>
            </Column>
            <Column field="name" filterField="name" header="操作">
                <template #body="{ data }">
                    <router-link
                        class="text-blue-500"
                        :to="{ name: 'portfolio_view', params: { portfolio_id: data.portfolio_id } }">查看
                    </router-link>
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
