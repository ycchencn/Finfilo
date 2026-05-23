<script setup>
import { useLayout } from '@/layout/composables/layout';
import AppConfigurator from './AppConfigurator.vue';
import router from "@/router";

const { toggleMenu, toggleDarkMode, isDarkTheme } = useLayout();

const toggleTrading = () => {
    router.push({path: '/quant/trading_terminal'});
};

</script>

<template>
    <div class="layout-topbar">
        <div class="layout-topbar-logo-container">
<!--            <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">-->
<!--                <i class="pi pi-bars"></i>-->
<!--            </button>-->
        </div>

        <div class="layout-topbar-actions">
            <div class="layout-topbar-menu hidden lg:block">
                <div class="layout-topbar-menu-content">
<!--                    <button type="button" class="layout-topbar-action" @click="toggleDarkMode()">-->
<!--                        <i class="pi pi-calendar"></i>-->
<!--                        <span>Calendar</span>-->
<!--                    </button>-->
                    <Chip label="Terminal" icon="pi pi-twitch" @click="toggleTrading()" style="cursor: pointer" />
                </div>
            </div>
        </div>
    </div>
</template>
