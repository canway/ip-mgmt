<!--
This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. jackliu, 15927493530
This file is part of IP Management Center.
IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
-->
<template>
    <div id="app">
        <template v-if="$route.name && $route.name !== 'applyIp'">
            <top-layout :menu-list="menuList"></top-layout>
        </template>
        <template v-else>
            <keep-alive>
                <transition name="fade" mode="out-in">
                    <router-view v-if="$route.meta.keepAlive" />
                </transition>
            </keep-alive>
            <transition name="fade" mode="out-in">
                <router-view v-if="!$route.meta.keepAlive" />
            </transition>
        </template>
    </div>
</template>

<script>
    import topLayout from '@/components/layout'
    import {frameRouter} from '@/router/frameRouter'

    export default {
        name: 'index',
        components: {
            topLayout
        },
        created() {
            this.menuList = [...frameRouter]
        }
    }
</script>

<style lang="scss">
    @import "./assets/custom/css/cover.scss";
</style>
