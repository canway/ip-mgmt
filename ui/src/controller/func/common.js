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
// loading显示
Vue.prototype.$showLoading = function() {
    this.$Spin.show({
        render: (h) => {
            return h('div', [
                h('Icon', {
                    'class': 'demo-spin-icon-load',
                    props: {
                        type: 'ios-loading',
                        size: 18
                    }
                }),
                h('div', 'Loading')
            ])
        }
    })
}
// loading关闭
Vue.prototype.$CloseLoading = function() {
    this.$Spin.hide()
}
// 去重
Vue.prototype.$DupRem = function(list) {
    const newArr = []
    for (let i = 0; i < list.length; i++) {
        if (newArr.indexOf(list[i]) < 0) {
            newArr.push(list[i])
        }
    }
    return newArr
}
// 深拷贝
Vue.prototype.$Copy = function(data) {
    return JSON.parse(JSON.stringify(data))
}
// 时间格式转string
Vue.prototype.$TransTime = function(date) {
    const data = new Date(date)
    const sep = '-'
    const year = data.getFullYear()
    let month = data.getMonth() + 1
    let strDate = data.getDate()
    if (month >= 1 && month <= 9) {
        month = '0' + month
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = '0' + strDate
    }
    return year + sep + month + sep + strDate
}
// 时间管理  days:时间间隔 startDate:初始时间 type:返回时间格式,默认返回string格式（string or time）
Vue.prototype.$DateDisplay = function(days, type, startDate) {
    const end = startDate ? new Date(startDate) : new Date()
    const start = startDate ? new Date(startDate) : new Date()
    end.setTime(start.getTime() + 24 * 60 * 60 * 1000)
    start.setTime(start.getTime() - 3600 * 1000 * 24 * days)
    return {
        endTime: type === 'time' ? end : Vue.prototype.$TransTime(end),
        startTime: type === 'time' ? start : Vue.prototype.$TransTime(start)
    }
}
