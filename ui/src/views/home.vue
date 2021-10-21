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
    <div class="home-wrapper">
        <bk-container :col="12" :gutter="20" :margin="0">
            <bk-row>
                <bk-col :span="7">
                    <bk-row>
                        <bk-col :span="3.5">
                            <!-- IP地址池使用率TOP5  -->
                            <div class="content-wrapper content" v-bkloading="{ isLoading: loading.pool, zIndex: 10 }">
                                <div class="ip-used-percent">
                                    <h2 class="font-color-grey">IP地址池使用率TOP5</h2>
                                    <ul v-if="poolObj.top_5" class="hover-color">
                                        <li v-for="(item,index) in poolObj.top_5"
                                            :key="index"
                                            @click="toRoutePool(item)"
                                            :class="[(index < 2 && 'orange')]">
                                            <span>
                                                <i v-if="index < 2" class="icon iconfont">&#xe6e5;</i>
                                                <i v-else class="radius"></i>
                                                <em>{{ index + 1 }}</em>
                                            </span>
                                            {{ item.name }}
                                            <b>{{ item.usage_rate }}</b>
                                        </li>
                                    </ul>
                                    <ul v-else>
                                        <bk-exception class="exception-wrap-item exception-part" type="empty" scene="part">
                                            <span>
                                                池子空了，快来
                                                <a style="color: #3A84FF;" @click="toRouter('/Ip/addressPool')">创建</a>
                                            </span>
                                        </bk-exception>
                                    </ul>
                                </div>
                                <div class="used-count" style="cursor: pointer;" @click="toRouter('/Ip/addressPool')">
                                    <div class="number">
                                        <h2 class="font-color-grey">{{ poolObj.used || 0 }}<span> / {{ poolObj.total || 0 }}</span></h2>
                                        <p>IP地址池使用数/总数</p>
                                    </div>
                                    <div class="sharp">
                                        <img src="@/assets/base/img/pool.png">
                                    </div>
                                </div>
                            </div>
                        </bk-col>
                        <bk-col :span="3.5">
                            <div class="content-wrapper content" v-bkloading="{ isLoading: loading.net, zIndex: 10 }">
                                <div class="ip-used-percent ip-net-used">
                                    <h2 class="font-color-grey">IP子网使用率（超阈值）</h2>
                                    <ul class="ip-used-ul" v-if="netObj.top_5">
                                        <li v-for="(item,index) in netObj.top_5"
                                            :key="index"
                                            :class="[(index < 2 && 'orange')]">
                                            {{ item.ip_net }}
                                            <b>{{ item.usage_rate }}</b>
                                        </li>
                                    </ul>
                                    <ul v-else>
                                        <bk-exception class="exception-wrap-item exception-part" type="empty" scene="part">
                                            <span>
                                                暂无子网超阈值
                                            </span>
                                        </bk-exception>
                                    </ul>
                                </div>
                                <div class="used-count" style="cursor: pointer;" @click="toRouter('/Ip/subnet')">
                                    <div class="number">
                                        <h2 class="font-color-grey">{{ netObj.used || 0 }}<span> / {{ netObj.total || 0 }}</span></h2>
                                        <p>IP子网使用数/总数</p>
                                    </div>
                                    <div class="sharp">
                                        <span class="icon iconfont icon-mianxingtubiao-zuzhiguanli" style="color: #3A84FF; font-size: 34px;"></span>
                                    </div>
                                </div>
                            </div>
                        </bk-col>
                    </bk-row>
                </bk-col>
                <bk-col :span="5">
                    <div class="total-status">
                        <div class="used-count common-container"
                            style="cursor: pointer;" @click="toRouter('/Ip/abnormal')"
                            v-bkloading="{ isLoading: loading.abnormal, zIndex: 10 }">
                            <div class="number">
                                <h2 class="font-color-grey">{{ abnormalObj.count || 0 }}</h2>
                                <p>异常IP数量</p>
                            </div>
                            <div class="sharp red">
                                <img src="@/assets/base/img/unusual.png">
                            </div>
                        </div>
                        <!-- IP分配情况 -->
                        <div class="distribute-solution common-container" v-bkloading="{ isLoading: loading.allocate, zIndex: 10 }">
                            <h2 class="font-color-grey">IP分配情况</h2>
                            <!-- <div id="echarts"></div> -->
                            <bk-container :col="12">
                                <bk-row>
                                    <bk-col :span="7">
                                        <div id="echarts"></div>
                                    </bk-col>
                                    <bk-col :span="4" style="padding: 0;">
                                        <div class="echarts-right-length">
                                            <div v-for="(item, index) in allocateBtnData"
                                                :key="index + 'allocateBtnData'"
                                                @click="changeEchartData(item, index, item.isActive)"
                                                @mousemove="changeEchart(index)"
                                                :class="item.isActive ? 'color-grey' : ''">
                                                <div class="length-title"><span :class="item.isActive ? 'icon-grey' : pieColor[item.status]">{{ item.name }}</span></div>
                                                <div class="length-count"><span>{{ item.count }}</span></div>
                                            </div>
                                        </div>
                                    </bk-col>
                                </bk-row>
                            </bk-container>
                        </div>
                    </div>
                </bk-col>
            </bk-row>
            <bk-row>
                <bk-col :span="7">
                    <div class="bottom-content ip-resource-pool" v-bkloading="{ isLoading: loading.lineChart, zIndex: 10 }">
                        <h2 class="font-color-grey">
                            IP资源池使用率趋势
                            <component
                                :is="addressPool.widget"
                                style="width: 150px;"
                                v-model="ipPoolId"
                                @change="initUsedData()"
                                :placeholder="addressPool.placeholder"
                                :default-value="addressPool.defaultValue"
                                :attr="addressPool.attr"
                            ></component>
                        </h2>
                        <template v-if="rateData.length === 0">
                            <bk-exception class="exception-wrap-item exception-part" type="empty" scene="part">
                                <span>
                                    暂无该地址池的使用趋势
                                </span>
                            </bk-exception>
                        </template>
                        <div id="lineCharts" v-show="rateData.length > 0"></div>
                    </div>
                </bk-col>
                <bk-col :span="5">
                    <div class="bottom-content" v-bkloading="{ isLoading: loading.record, zIndex: 10 }">
                        <div class="header">
                            <h2 class="font-color-grey">最近IP申请记录</h2>
                            <ul>
                                <li :class="(active === 0 && 'active')" @click="active = 0">全部</li>
                                <li :class="(active === 1 && 'active')" @click="active = 1;toTab()">我审批</li>
                            </ul>
                        </div>
                        <div class="list-container">
                            <ul>
                                <template v-if="active === 0">
                                    <li v-for="(item, index) in recordData" :key="index">
                                        <div class="list-info">
                                            <p>{{ item.apply_person }}，数量{{item.apply_ip_count || item.apply_ips.length}}</p>
                                            <span>{{ item.create_at }}</span>
                                        </div>
                                        <span :style="{ color: statusColor[item.apply_status], backgroundColor: statusBgColor[item.apply_status] }">
                                            {{ statusObj[item.apply_status] }}
                                        </span>
                                    </li>
                                    <div v-if="recordData.length === 0">
                                        <bk-exception class="exception-wrap-item exception-part" type="empty" scene="part">
                                            <span>
                                                暂无数据
                                            </span>
                                        </bk-exception>
                                    </div>
                                </template>
                                <template v-else>
                                    <li v-for="(item, index) in approveData" :key="index">
                                        <div class="list-info">
                                            <p>{{ item.name }}</p>
                                            <span>{{ item.audit_time }}</span>
                                        </div>
                                        <span :style="{ color: statusColor[item.apply_status] }">
                                            {{ statusObj[item.apply_status] }}
                                        </span>
                                    </li>
                                    <div v-if="approveData.length === 0">
                                        <bk-exception class="exception-wrap-item exception-part" type="empty" scene="part">
                                            <span>
                                                暂无数据
                                            </span>
                                        </bk-exception>
                                    </div>
                                </template>
                            </ul>
                        </div>
                    </div>
                </bk-col>
            </bk-row>
        </bk-container>
    </div>
</template>

<script>
    import dataSelect from '@/components/formWidget/dataSelect'

    export default {
        name: 'home',
        components: {
            dataSelect
        },
        data() {
            return {
                loading: {
                    pool: false,
                    net: false,
                    abnormal: false,
                    allocate: false,
                    record: false,
                    lineChart: true
                },
                poolObj: {},
                netObj: {},
                abnormalObj: {},
                allocateBtnData: [],
                allocateData: [],
                active: 0,
                statusColor: {
                    auditing: '#ff9c01',
                    reject: '#ea3636',
                    approval: '#2dcb56',
                    submiting: '#ff9c01'
                },
                statusBgColor: {
                    auditing: '#ffe8c3',
                    reject: '#ffdddd',
                    approval: '#dcffe2',
                    submiting: '#ffe8c3'
                },
                statusObj: {
                    auditing: '待审核',
                    reject: '已拒绝',
                    approval: '已通过',
                    submiting: '待提交'
                },
                recordData: [],
                approveData: [],
                ipPoolId: '',
                addressPool: {
                    widget: 'data-select',
                    placeholder: '请选择地址池',
                    attr: {
                        remote: true,
                        filterable: true,
                        searchable: true,
                        popperAppendToBody: false,
                        clearable: true,
                        url: 'searchPool',
                        detailUrl: 'poolDetail',
                        initFlag: true // 是否需要请求初始值
                    }
                },
                rateData: ['1'],
                dataIndex: 0,
                myChart: '',
                pieColor: {
                    '已分配': 'allocated',
                    '未分配': 'unallocated',
                    '待回收': 'to-recycled',
                    '已回收': 'ecycled'
                },
                option: {},
                lengthIndex: 0
            }
        },
        created() {
            // ip地址池使用率top5
            this.fetchCommonData('get_ip_pool_summary', 'poolObj', 'pool')
            // IP子网使用率（超阈值）
            this.fetchCommonData('get_ip_net_summary', 'netObj', 'net')
            // 异常IP数量
            this.fetchCommonData('search_ip_abnormal', 'abnormalObj', 'abnormal')
            // 最近IP申请记录
            this.fetchRecordData()
        },
        mounted() {
            this.initData()
        },
        methods: {
            async fetchCommonData(url, data, name) {
                this.loading[name] = true
                try {
                    const res = await this.$api[url]()
                    if (res.result) {
                        this[data] = res.data
                        if (name === 'pool') {
                            this.ipPoolId = this.poolObj.top_5 && this.poolObj.top_5.length > 0 ? this.poolObj.top_5[0].id : ''
                            if (this.ipPoolId) {
                                this.initUsedData()
                            } else {
                                this.loading['lineChart'] = false
                            }
                        }
                    } else {
                        this[data] = {}
                        this.loading['lineChart'] = false
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading[name] = false
                }
            },
            async fetchRecordData(params = {}) {
                this.loading.record = true
                try {
                    const res = await this.$api.search_apply_list({
                    ...params
                    })
                    if (res.result) {
                        if (this.active === 0) {
                            this.recordData = res.data.results
                        } else {
                            this.approveData = res.data.results
                        }
                    } else {
                        if (this.active === 0) {
                            this.recordData = []
                        } else {
                            this.approveData = []
                        }
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading.record = false
                }
            },
            toTab() {
                if (this.approveData.length > 0) return false
                this.fetchRecordData({
                    auditor: this.$store.state.user.userInfo.username
                })
            },
            async initData() {
                this.loading.allocate = true
                const _this = this
                try {
                    const res = await this.$api.get_ip_summary()
                    if (res.result) {
                        const _data = res.data
                        this.allocateData = _data.map((item, index) => {
                            return {...item, name: item.status, value: item.count}
                        })
                        this.allocateBtnData = JSON.parse(JSON.stringify(this.allocateData))
                        this.allocateBtnData.forEach(item => {
                            item.pieColor = this.pieColor[item.status]
                        })
                        this.myChart = this.$echarts.init(document.getElementById('echarts'))
                        // 指定图表的配置项和数据
                        this.option = {
                            tooltip: {
                                show: false,
                                trigger: 'item'
                            },
                            legend: {
                                show: false,
                                orient: 'vertical',
                                align: 'left',
                                itemWidth: 8,
                                itemHeight: 8,
                                itemGap: 15,
                                icon: 'circle',
                                formatter: function(name) {
                                    const current = _this.allocateData.find(item => item.name === name)
                                    return '{a|' + name + '}{b|' + current['count'] + '}'
                                },
                                textStyle: {
                                    rich: {
                                        a: {
                                            verticalAlign: 'right',
                                            fontSize: 12,
                                            align: 'left',
                                            width: 60
                                        },
                                        b: {
                                            fontSize: 12,
                                            align: 'right',
                                            width: 50,
                                            fontWeight: 900
                                        }
                                    }
                                }
                            },
                            series: [
                                {
                                    type: 'pie',
                                    radius: ['55%', '80%'],
                                    center: ['50%', '50%'],
                                    avoidLabelOverlap: false,
                                    legendHoverLink: false,
                                    left: 0,
                                    itemStyle: {
                                        borderRadius: 0,
                                        borderColor: '#fff',
                                        borderWidth: 2,
                                        normal: {
                                            color: function(params) {
                                                const colors = {
                                                    '已分配': '#7FABF4',
                                                    '未分配': '#7ED4B2',
                                                    '待回收': '#E9B76E',
                                                    '已回收': '#9DB1CE'
                                                }
                                                return colors[params.name]
                                            }
                                        }
                                    },
                                    label: {
                                        show: false,
                                        position: 'center'
                                    },
                                    emphasis: {
                                        label: {
                                            show: true,
                                            formatter: (params) => {
                                                return '{p|' + params.percent + '%}' + '\n{nm|' + params.name + '}'
                                            },
                                            rich: {
                                                p: {
                                                    color: '#63656E',
                                                    fontSize: '20',
                                                    backgroundColor: 'white'
                                                },
                                                nm: {
                                                    fontSize: '14',
                                                    backgroundColor: 'white'
                                                }
                                            }
                                        }
                                    },
                                    labelLine: {
                                        show: false
                                    },
                                    data: this.allocateData
                                }
                            ]
                        }
                        // 使用刚指定的配置项和数据显示图表。
                        this.myChart.setOption(this.option)
                        this.myChart.dispatchAction({type: 'highlight', seriesIndex: 0, dataIndex: 0})
                        this.myChart.on('legendselectchanged', (e) => {
                            this.dataIndex = 0
                            for (const i in e.selected) {
                                if (e.selected[i] === true) {
                                    this.allocateData.forEach((item, index) => {
                                        if (item.name === i) {
                                            this.dataIndex = index
                                        }
                                    })
                                    break
                                }
                            }
                            for (const i in this.allocateData) {
                                this.myChart.dispatchAction({type: 'downplay', seriesIndex: 0, dataIndex: i})
                            }
                            // 高亮第一个显示的元素
                            this.myChart.dispatchAction({type: 'highlight', seriesIndex: 0, dataIndex: this.dataIndex})
                        })
                        this.myChart.on('mouseover', (e) => {
                            if (e.dataIndex !== this.lengthIndex) {
                                this.myChart.dispatchAction({type: 'downplay', seriesIndex: 0, dataIndex: this.lengthIndex})
                            }
                            for (let i = 0; i < this.allocateData.length; i++) {
                                if (this.allocateData[i].name === e.name) {
                                    if (i !== this.dataIndex) {
                                        this.myChart.dispatchAction({type: 'downplay', seriesIndex: 0, dataIndex: this.dataIndex})
                                    }
                                    break
                                }
                            }
                        })
                        this.myChart.on('mouseout', (e) => {
                            for (const i in this.allocateData) {
                                this.myChart.dispatchAction({type: 'downplay', seriesIndex: 0, dataIndex: i})
                            }
                            this.myChart.dispatchAction({type: 'highlight', seriesIndex: 0, dataIndex: this.dataIndex})
                        })
                        window.addEventListener('resize', function() {
                            this.myChart.resize()
                        })
                    } else {
                        this.allocateData = []
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading.allocate = false
                }
            },
            initUsedData() {
                this.loading['lineChart'] = true
                const _data = {time: [], value: []}
                this.$api.get_usage_rate_event({
                    ip_pool_id: this.ipPoolId
                }).then(res => {
                    if (res.result) {
                        const _arr = res.data
                        this.rateData = JSON.parse(JSON.stringify(_arr))
                        _arr.splice(0, 10).forEach(item => {
                            _data.time.push(item.when_time.replace('T', ' ').substring(5, 15))
                            _data.value.push(Number(item.event.usage_rate.replace('%', '')))
                        })
                        const lineChart = this.$echarts.init(document.getElementById('lineCharts'))
                        // 指定图表的配置项和数据
                        const option = {
                            tooltip: {
                                trigger: 'axis',
                                axisPointer: {
                                    type: 'cross'
                                }
                            },
                            grid: {
                                top: 20
                            },
                            xAxis: {
                                type: 'category',
                                boundaryGap: false,
                                axisLabel: {
                                    margin: 15,
                                    interval: 0,
                                    rotate: -30
                                },
                                nameTextStyle: {
                                    color: function(value, index) {
                                        return '#A7A7A7'
                                    },
                                    fontSize: 12
                                },
                                data: _data.time
                            },
                            yAxis: {
                                type: 'value',
                                axisLine: {
                                    show: false
                                },
                                axisLabel: {
                                    formatter: '{value} %'
                                },
                                axisPointer: {
                                    snap: true
                                }
                            },
                            visualMap: {
                                show: false,
                                dimensions: 2,
                                pieces: [{
                                    lte: 60,
                                    gt: 0,
                                    color: '#5E97F7'
                                }, {
                                    gt: 60,
                                    lte: 80,
                                    color: 'red'
                                }]
                            },
                            series: [
                                {
                                    name: '使用率',
                                    type: 'line',
                                    symbol: 'circle',
                                    smooth: true,
                                    data: _data.value,
                                    markLine: {
                                        itemStyle: {
                                            color: 'rgba(255, 173, 177, 0.4)'
                                        },
                                        data: [{
                                            type: 'max',
                                            value: 10
                                        }]
                                    }
                                }
                            ]
                        }
                        // 使用刚指定的配置项和数据显示图表。
                        lineChart.setOption(option)
                        window.addEventListener('resize', function() {
                            lineChart.resize()
                        })
                    } else {
                        this.rateData = []
                    }
                }).finally(() => {
                    this.loading.lineChart = false
                })
            },
            toRoutePool(item) {
                this.$router.push({
                    path: '/Ip/addressPool',
                    query: {name: item.name}
                })
            },
            toRouter(url) {
                this.$router.push({
                    path: url
                })
            },
            changeEchartData(item, index, isActive) {
                const _temp = {...item, isActive: !isActive}
                this.$set(this.allocateBtnData, index, _temp)
                // 活动的数据项
                const unActiveArr = []
                this.allocateBtnData.forEach(item => {
                    if (!item.isActive) {
                        unActiveArr.push(item.status)
                    }
                })
                if (unActiveArr.length === 0) {
                    this.allocateData = []
                } else {
                    this.allocateData = []
                    for (let i = 0; i < unActiveArr.length; i++) {
                        for (let j = 0; j < this.allocateBtnData.length; j++) {
                            if (this.allocateBtnData[j].status === unActiveArr[i]) {
                                this.allocateData.push(this.allocateBtnData[j])
                            }
                        }
                    }
                }
                this.option.series[0].data = this.allocateData
                this.myChart.setOption(this.option)
                this.myChart.dispatchAction({type: 'highlight', seriesIndex: 0, dataIndex: 0})
            },
            changeEchart(index) {
                this.lengthIndex = index > this.allocateData.length - 1 ? this.allocateData.length - 1 : index
                for (const i in this.allocateData) {
                    this.myChart.dispatchAction({type: 'downplay', seriesIndex: 0, dataIndex: i})
                }
                this.myChart.dispatchAction({type: 'highlight', seriesIndex: 0, dataIndex: this.lengthIndex})
            }
        }
    }
</script>

<style scoped lang="scss">
.home-wrapper {
    padding: 20px 10px;
    .bk-grid-row {
        .bk-grid-col {
            .content {
                background: #fff;
            }
        }
    }
    .common-container {
        width: 100%;
        height: 100px;
        padding: 15px 20px !important;
        box-sizing: border-box;
        background: #fff;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
        border-radius: 2px;
        &:hover {
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.2);
        }
    }
    .content-wrapper {
        padding: 20px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
        border-radius: 2px;
        .ip-used-percent {
            width: 100%;
            height: 240px;
            box-sizing: border-box;
            color: #63656E;
            letter-spacing: 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #DDE4EB;
            h2 {
                margin: 0 0 15px 0;
                font-size: 14px;
                line-height: 22px;
                font-weight: 600;
            }
            ul {
                li {
                    font-size: 12px;
                    margin-bottom: 20px;
                    vertical-align: middle;
                    height: 18px;
                    line-height: 18px;
                    cursor: pointer;
                    span {
                        display: inline-block;
                        position: relative;
                        vertical-align: middle;
                        text-align: center;
                        width: 18px;
                        height: 18px;
                        em {
                            display: block;
                            font-style: normal;
                            color: #fff;
                            position: absolute;
                            top: 0;
                            left: 31.5%;
                            font-size: 12px;
                            line-height: 16px;
                        }
                    }
                    i {
                        font-size: 18px;
                        display: inline-block;
                        &.radius {
                            width: 15px;
                            height: 15px;
                            background: #699DF4;
                            border-radius: 50%;
                        }
                    }
                    b {
                        float: right;
                        font-weight: normal;
                        color: #63656E;
                    }
                    &.orange {
                        em {
                            left: 30%;
                        }
                        i {
                            color: #FF9C01;
                        }
                        b {
                            color: #FF9C01;
                        }
                    }
                    &:last-child {
                        margin-bottom: 0;
                    }
                }
            }
            .hover-color {
                li:hover {
                    color: #699DF4;
                }
            }
            &.ip-net-used {
                li {
                    cursor: inherit;
                }
            }
        }
        .ip-used-ul {
            width: 100%;
            height: 175px;
            margin: 0 auto;
            overflow: hidden;
            padding-right: 6px;
            overflow-y: scroll;
            li {
                font-size: 12px;
                margin-bottom: 20px;
                vertical-align: middle;
                height: 18px;
                line-height: 18px;
                span {
                    display: inline-block;
                    position: relative;
                    vertical-align: middle;
                    text-align: center;
                    width: 18px;
                    height: 18px;
                    em {
                        display: block;
                        font-style: normal;
                        color: #fff;
                        position: absolute;
                        top: 0;
                        left: 33%;
                        font-size: 12px;
                        line-height: 18px;
                    }
                }
                i {
                    font-size: 18px;
                    display: inline-block;
                    &.radius {
                        width: 15px;
                        height: 15px;
                        background: #699DF4;
                        border-radius: 50%;
                    }
                }
                b {
                    float: right;
                    font-weight: normal;
                }
                &.orange {
                    em {
                        left: 30%;
                    }
                    i {
                        color: #FF9C01;
                    }
                    b {
                        color: #FF9C01;
                    }
                }
            }
            &::-webkit-scrollbar {
                /*滚动条整体样式*/
                width: 6px;  /*高宽分别对应横竖滚动条的尺寸*/
                height: 3px;
                border: none;
            }
            &::-webkit-scrollbar-thumb {
                /*滚动条里面小方块*/
                border-radius: 30px;
                background: transparent;
            }
            &::-webkit-scrollbar-track {
                /*滚动条里面轨道*/
                border-radius: 30px;
                background: transparent;
            }
            &:hover {
                &::-webkit-scrollbar-thumb {
                    background: rgba(186, 198, 204, .6);
                    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
                }
            }
        }
    }
    .used-count {
        width: 100%;
        height: 105px;
        display: flex;
        padding: 20px 10px 0 10px;
        .number {
            flex: 1;
            h2 {
                margin: 0;
                color: #63656E;
                font-size: 24px;
                line-height: 36px;
                span {
                    font-size: 16px;
                    font-weight: normal;
                }
            }
            p {
                color: #979BA5;
                margin: 5px 0;
            }
        }
        .sharp {
            width: 60px;
            height: 60px;
            line-height: 74px;
            text-align: center;
            background-color: #E1ECFF;
            clip-path: polygon(45% 1.33975%, 46.5798% 0.60307%, 48.26352% 0.15192%, 50% 0%, 51.73648% 0.15192%, 53.4202% 0.60307%, 55% 1.33975%, 89.64102% 21.33975%, 91.06889% 22.33956%, 92.30146% 23.57212%, 93.30127% 25%, 94.03794% 26.5798%, 94.48909% 28.26352%, 94.64102% 30%, 94.64102% 70%, 94.48909% 71.73648%, 94.03794% 73.4202%, 93.30127% 75%, 92.30146% 76.42788%, 91.06889% 77.66044%, 89.64102% 78.66025%, 55% 98.66025%, 53.4202% 99.39693%, 51.73648% 99.84808%, 50% 100%, 48.26352% 99.84808%, 46.5798% 99.39693%, 45% 98.66025%, 10.35898% 78.66025%, 8.93111% 77.66044%, 7.69854% 76.42788%, 6.69873% 75%, 5.96206% 73.4202%, 5.51091% 71.73648%, 5.35898% 70%, 5.35898% 30%, 5.51091% 28.26352%, 5.96206% 26.5798%, 6.69873% 25%, 7.69854% 23.57212%, 8.93111% 22.33956%, 10.35898% 21.33975%);
            &.red {
                background: #FFDDDD;
                margin-top: 8px;
            }
        }
        &:hover {
            .sharp {
                -webkit-animation: tada .6s .1s ease both;
                -moz-animation: tada .6s .1s ease both;
                @-webkit-keyframes tada {
                    0% {
                        -webkit-transform: scale(1);
                    }
                    10%, 20% {
                        -webkit-transform: scale(0.9) rotate(-3deg);
                    }
                    30%, 50%, 70%, 90% {
                        -webkit-transform: scale(1.1) rotate(3deg);
                    }
                    40%, 60%, 80% {
                        -webkit-transform: scale(1.1) rotate(-3deg);
                    }
                    100% {
                        -webkit-transform: scale(1) rotate(0);
                    }
                }
            }
        }
    }
    .distribute-solution {
        margin-top: 20px;
        color: #63656E;
        font-size: 14px;
        height: 260px;
        h2 {
            margin: 0 0 15px 0;
            font-size: 14px;
            line-height: 22px;
            font-weight: 600;
        }
        #echarts {
            width: 70%;
            height: 190px;
        }
        .echarts-right-length {
            height: 120px;
            margin-top: 50px;
            .length-title {
                width: 40%;
                display: inline-block;
                position: relative;
                span::before {
                    content: " ";
                    position: absolute;
                    left: -14px;
                    top: 10px;
                    width: 10px;
                    height: 10px;
                    border-radius: 5px;
                }
                .allocated::before {
                    background-color: #7FABF4;
                }
                .unallocated::before {
                    background-color: #7ED4B2;
                }
                .to-recycled::before {
                    background-color: #E9B76E;
                }
                .ecycled::before {
                    background-color: #9DB1CE;
                }
                .icon-grey::before {
                    background-color: #dcdee5;
                }
            }
            .length-count {
                width: 40%;
                display: inline-block;
                text-align: right;
                font-weight: bold;
            }
            span {
                font-size: 12px;
                line-height: 28px;
                cursor: pointer;
            }
            .color-grey {
                color: #dcdee5;
            }
        }
    }
    .bottom-content {
        margin-top: 20px;
        padding: 20px;
        height: 350px;
        background: #fff;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
        border-radius: 2px;
        h2 {
            margin: 0 0 15px 0;
            font-size: 14px;
            line-height: 22px;
            font-weight: 600;
            color: #63656E;
            .select-wrapper {
                float: right;
                margin-top: -5px;
            }
        }
        #lineCharts {
            width: 100%;
            height: 280px;
        }
        .header {
            display: flex;
            color: #63656E;
            h2 {
                flex: 1;
            }
            ul {
                margin-right: 10px;
                li {
                    float: left;
                    list-style: none;
                    padding: 3px 12px;
                    border: 1px solid #C4C6CC;
                    cursor: pointer;
                    &.active {
                        color: #3A84FF;
                        background: #E1ECFF;
                        border: 1px solid #3A84FF;
                    }
                    &:first-child {
                        border-top-left-radius: 3px;
                        border-bottom-left-radius: 3px;
                    }
                    &:last-child {
                        border-left: none;
                        border-top-right-radius: 3px;
                        border-bottom-right-radius: 3px;
                    }
                }
            }
            span {
                color: #3A84FF;
                line-height: 25px;
                cursor: pointer;
            }
        }
        .list-container {
            color: #63656E;
            height: 260px;
            margin-top: 10px;
            overflow-y: hidden;
            ul {
                list-style: none;
                li {
                    display: flex;
                    margin-bottom: 10px;
                    padding: 5px;
                    box-sizing: border-box;
                    vertical-align: middle;
                    align-items: center;
                    >span {
                        border-radius: 2px;
                        height: 25px;
                        line-height: 25px;
                        padding: 0 10px;
                        &.success {
                            background: #FEEBEA;
                            color: #EA3536;
                        }
                        &.fail {
                            background: #E4FAF0;
                            color: #14A568;
                        }
                    }
                    .list-info {
                        flex: 1;
                        p {
                            font-size: 13px;
                            margin: 0 0 5px 0;
                            letter-spacing: 1px;
                        }
                        span {
                            color: #C4C6CC;
                            font-size: 12px;
                        }
                    }
                    &:hover {
                        background: #fafbfd;
                    }
                }
            }
            &::-webkit-scrollbar {
                /*滚动条整体样式*/
                width: 6px;  /*高宽分别对应横竖滚动条的尺寸*/
                height: 3px;
                border: none;
            }
            &::-webkit-scrollbar-thumb {
                /*滚动条里面小方块*/
                border-radius: 30px;
                box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
                background: rgba(186, 198, 204, .6);
            }
            &::-webkit-scrollbar-track {
                /*滚动条里面轨道*/
                border-radius: 30px;
                background: transparent;
            }
            &:hover {
                overflow-y: auto;
            }
            /deep/ .part-img {
                margin-top: 9.5%;
            }
        }
    }
    .ip-resource-pool {
        /deep/ .part-img {
            margin-top: 9%;
        }
    }
    .font-color-grey {
        color: #313238 !important;
        font-weight: 900;
        span {
            color: #63656E !important;
        }
    }
}
</style>
