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
    <div class="monitor-navigation">
        <bk-navigation
            :header-title="nav.id"
            :side-title="nav.title"
            :default-open="true"
            @toggle="handleToggle">
            <!-- 左侧菜单头部icon插槽  -->
            <template slot="side-icon">
                <img :src="src" class="cw-logo" alt="嘉为蓝鲸">
            </template>
            <!-- 右侧头部插槽 -->
            <template slot="header">
                <div class="monitor-navigation-header">
                    <div class="header-title">
                        {{nav.name}}
                    </div>
                    <bk-select v-if="comShow" class="header-select is-left" v-model="header.bizId" :clearable="false" searchable>
                        <bk-option v-for="option in header.selectList"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <bk-popover v-if="comShow" theme="light navigation-message" :arrow="false" offset="-150, 5" trigger="mouseenter" :tippy-options="{ 'hideOnClick': false }">
                        <div class="header-mind is-left">
                            <svg style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg">
                                <path d="M32,56c-1.3,0-2.6-0.6-3.4-1.6h-4.5c0.5,1.5,1.4,2.7,2.6,3.7c3.1,2.5,7.5,2.5,10.6,0c1.2-1,2.1-2.3,2.6-3.7h-4.5C34.6,55.4,33.3,56,32,56z"></path>
                                <path d="M53.8,49.1L50,41.5V28c0-8.4-5.8-15.7-14-17.6V8c0-2.2-1.8-4-4-4s-4,1.8-4,4v2.4c-8.2,1.9-14,9.2-14,17.6v13.5l-3.8,7.6c-0.3,0.6-0.3,1.3,0.1,1.9c0.4,0.6,1,1,1.7,1h40c0.7,0,1.3-0.4,1.7-1C54,50.4,54.1,49.7,53.8,49.1z"></path>
                            </svg>
                            <span class="header-mind-mark is-left"></span>
                        </div>
                        <template slot="content">
                            <div class="monitor-navigation-message">
                                <h5 class="message-title">消息中心</h5>
                                <ul class="message-list">
                                    <li class="message-list-item" v-for="(item,index) in message.list" :key="index">
                                        <span class="item-message">{{item.message}}</span>
                                        <span class="item-date">{{item.date}}</span>
                                    </li>
                                </ul>
                                <div class="message-footer">进入消息中心</div>
                            </div>
                        </template>
                    </bk-popover>
                    <div v-if="comShow" class="header-help is-left">
                        <svg class="bk-icon" style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg">
                            <path d="M32,4C16.5,4,4,16.5,4,32c0,3.6,0.7,7.1,2,10.4V56c0,1.1,0.9,2,2,2h13.6C36,63.7,52.3,56.8,58,42.4S56.8,11.7,42.4,6C39.1,4.7,35.6,4,32,4z M31.3,45.1c-1.7,0-3-1.3-3-3s1.3-3,3-3c1.7,0,3,1.3,3,3S33,45.1,31.3,45.1z M36.7,31.7c-2.3,1.3-3,2.2-3,3.9v0.9H29v-1c-0.2-2.8,0.7-4.4,3.2-5.8c2.3-1.4,3-2.2,3-3.8s-1.3-2.8-3.3-2.8c-1.8-0.1-3.3,1.2-3.5,3c0,0.1,0,0.1,0,0.2h-4.8c0.1-4.4,3.1-7.4,8.5-7.4c5,0,8.3,2.8,8.3,6.9C40.5,28.4,39.2,30.3,36.7,31.7z"></path>
                        </svg>
                    </div>
                    <bk-popover theme="light navigation-message" :arrow="false" offset="-20, 10" placement="bottom-start" :tippy-options="{ 'hideOnClick': false }">
                        <div class="header-user is-left">
                            {{userData.username}}
                        </div>
                    </bk-popover>
                </div>
            </template>
            <!-- 左侧menu插槽  -->
            <template slot="menu">
                <menu-list :menu-list="menuList"
                    :default-active="$route.meta.hasOwnProperty('fatherName') ? $route.meta.fatherName : $route.name"
                    :toggle-active="nav.toggle"
                    @nav-click="handleNavItemClick"
                    @select="handleSelect"
                ></menu-list>
            </template>
            <div class="monitor-navigation-content">
                <keep-alive>
                    <transition name="fade" mode="out-in">
                        <router-view v-if="$route.meta.keepAlive" />
                    </transition>
                </keep-alive>
                <transition name="fade" mode="out-in">
                    <router-view v-if="!$route.meta.keepAlive" />
                </transition>
            </div>
        </bk-navigation>
    </div>
</template>

<script>
    /**
     * @comopnent 主布局组件
     * @props {
     *   menuList:[] 菜单数据集合
     * }
     */
    import menuList from '../menu'
    export default {
        name: 'layout-index',
        components: {
            menuList
        },
        props: {
            menuList: {
                type: Array,
                default: () => {
                    return []
                },
                require: true
            }
        },
        data() {
            return {
                nav: {
                    id: 'Home',
                    name: '首页',
                    submenuActive: false,
                    title: 'IP管理中心'
                },
                src: window.siteUrl + 'sys/get_logo/?random=' + Math.random(),
                comShow: false,
                header: {
                    selectList: [],
                    active: 2,
                    bizId: 1
                },
                message: {
                    list: []
                },
                user: {
                    list: [
                        {
                            name: 'IP申请',
                            path: '/apply/ip'
                        }
                    ]
                },
                userData: {}
            }
        },
        watch: {
            '$route'(to) {
                this.nav.name = to.meta.title
            }
        },
        created() {
            this.loginUser()
        },
        mounted() {
            this.nav.name = this.$route.meta.title
        },
        methods: {
            async loginUser() {
                const res = await this.$api.homeInfo()
                if (res.result) {
                    this.userData = res.data
                    this.$store.commit('setUserInfo', res.data)
                }
            },
            handleSelect({id}) {
                this.nav.id = id
            },
            handleNavItemClick(item) {
                if (this.$route.name !== item.name) {
                    this.nav.name = item.meta.title
                    this.$router.push({
                        path: item.path
                    })
                }
            },
            handleToggle(v) {
                this.nav.toggle = v
            }
        }
    }
</script>

<style scoped>
.cw-logo {
    width: 32px;
    height: 32px;
}
</style>
