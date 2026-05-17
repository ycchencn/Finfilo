<script setup>
import { ref } from 'vue';

import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        label: '市场监控',
        items: [
            {
                label: '事件驱动',
                icon: 'pi pi-fw pi-wave-pulse',
                to: '/market/news_flow'
            },
            {
                label: 'ETF洞察',
                icon: 'pi pi-fw pi-cloud-download',
                to: '/market/etf_insight'
            },
        ]
    },
    {
        label: '投资组合',
        items: [
            {
                label: '关注清单',
                icon: 'pi pi-fw pi-palette',
                to: '/user/watch_list'
            },
            {
                label: '股票池',
                icon: 'pi pi-fw pi-clone',
                to: '/quant/stock_monitor'
            }
        ]
    },
    {
        label: '量化模型',
        items: [
            {
                label: '量化策略',
                icon: 'pi pi-fw pi-microchip-ai',
                to: '/quant/portfolio_list'
            },
            {
                label: '量化回测',
                icon: 'pi pi-fw pi-clone',
                to: '/quant/stock_monitor'
            }
        ]
    },
    {
        label: '系统设置',
        items: [
            {
                label: '智能体',
                icon: 'pi pi-fw pi-wave-pulse',
                to: '/market/sector_sentiment'
            },
            {
                label: '系统日志',
                icon: 'pi pi-fw pi-stopwatch',
                to: '/system/system_log'
            },
            {
                label: 'API文档',
                icon: 'pi pi-fw pi-twitch',
                url: 'https://0wikvr2f6a.apifox.cn/',
                target: '_blank'
            }
        ]
    }
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
