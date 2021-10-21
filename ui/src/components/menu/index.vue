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
    <bk-navigation-menu
        ref="menu"
        @select="toSelect"
        :default-active="defaultActive"
        :toggle-active="toggleActive"
    >
        <template v-for="item in menuList">
            <bk-navigation-menu-item
                v-if="!item.meta.hidden"
                :key="item.meta.title"
                :has-child="item.children && !!item.children.length"
                @click="handleNavItemClick(item)"
                :group="item.group"
                :icon="item.meta.icon"
                :url="item.path"
                :id="item.name">
                <span>{{item.meta.title}}</span>
                <div slot="child">
                    <template v-for="child in item.children">
                        <bk-navigation-menu-item
                            :key="child.meta.title"
                            v-if="!child.meta.hidden"
                            :id="child.name"
                            :url="child.path"
                            @click="handleNavItemClick(child)"
                            :default-active="child.active">
                            <span>{{child.meta.title}}</span>
                        </bk-navigation-menu-item>
                    </template>
                </div>
            </bk-navigation-menu-item>
        </template>
    </bk-navigation-menu>
</template>

<script>
    /**
     * @comopnent 导航栏菜单组件
     * @props {
     *   menuList:[] 菜单数据集合,
     *   defaultActive:'默认当前的菜单名'
     *   toggleActive:'左侧导航栏在伸缩时子级菜单是否一起展开和收回'
     * }
     */
    export default {
        name: 'menu-component',
        props: {
            defaultActive: {
                type: String,
                default: '',
                require: true
            },
            menuList: {
                type: Array,
                default: () => {
                    return []
                },
                require: true
            },
            toggleActive: {
                type: Boolean,
                default: false
            }
        },
        methods: {
            toSelect(id, item) {
                this.$emit('select', {id, item})
            },
            handleNavItemClick(item) {
                this.$emit('nav-click', item)
            }
        }
    }
</script>
