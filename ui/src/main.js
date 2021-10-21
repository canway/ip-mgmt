/**
* This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
* Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
* Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. dengyuliu, 15927493530
* This file is part of IP management center.
* IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
* IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
*/
import Vue from 'vue'
import App from './App'
import router from './router'
import axios from 'axios'

// 引入MagicBox
import bkMagic from 'bk-magic-vue'

// 几何图
import Echarts from 'echarts'
// 引用API文件
import api from './api/index'
// 时间格式化插件
import moment from 'moment'
// filter统一引入
import './fiter/index.js'
// 公共方法
import './controller/func/common.js'
// 统一样式引入
import './assets/index'
// 全量引入 bk-magic-vue 样式
import 'bk-magic-vue/dist/bk-magic-vue.min.css'
// 引入自定义组件
import Component from './components/index.js'
// vuex
import store from './store/index'
import 'jquery'

// 全局混入
import { globalMixins } from '@/common/mixins.js'
Vue.mixin(globalMixins)

Vue.use(bkMagic)
Vue.use(Echarts)
Vue.use(Component)
Vue.prototype.$echarts = Echarts
Vue.prototype.$moment = moment
// 将API方法绑定到全局
Vue.prototype.$http = axios
Vue.prototype.$api = api
const headTheme = 'light' // 选择 light 或 blue
Vue.prototype.headTheme = headTheme

/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    store,
    components: {App},
    data() {
        return {
            website: ''
        }
    },
    template: '<App/>'
})
