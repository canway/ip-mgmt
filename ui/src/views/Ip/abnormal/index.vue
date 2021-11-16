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
    <div class="table—wrapper">
        <div class="header-table-operation">
            <search-input
                v-model="searchValue"
                :placeholder="'请输入关键字搜索'"
                @search="onSearch">
            </search-input>
            <!-- 更多查询 -->
            <advanced-search
                :form-widgets="formWidgets"
                @submit="handleAdvancedSearch">
            </advanced-search>
            <div class="operation-container">
                <div>
                    <bk-button :title="'导出'" @click="toExport" v-if="copyData.length > 0">
                        导出Excel
                    </bk-button>
                    <bk-dropdown-menu trigger="click" @show="dropdownShow" @hide="dropdownHide" ref="dropdown">
                        <div class="dropdown-trigger-btn" style="padding-left: 19px;" slot="dropdown-trigger">
                            <span>更多操作</span>
                            <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                        </div>
                        <ul class="bk-dropdown-list" slot="dropdown-content">
                            <li><a href="javascript:;" @click="confirmNormal">确认异常</a></li>
                            <li><a href="javascript:;" @click="confirmOffline">加入离线白名单</a></li>
                        </ul>
                    </bk-dropdown-menu>
                </div>
            </div>
        </div>
        <div v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <common-table
                :data="copyData"
                :columns="columns"
                :select-column="{ visible: true, fixed: true }"
                :order-column="{ visible: false, fixed: false }"
                @selection-change="selectChange"
                :settings-fields="settingsFields"
                :pagination="pagination"
                @handleSettingChange="handleSettingChange"
                @page-change="handlePageChange"
                @page-limit-change="limitChange"
            >
                <template slot="status" slot-scope="record">
                    <span
                        class="radius-tip"
                        :style="{ background: statusColorObj[record.scope.allocate_status] }">
                    </span>
                    {{ statusObj[record.scope.allocate_status] }}
                </template>
                <template slot="online_status" slot-scope="record">
                    <span
                        :style="{ color: record.scope.online_status ? '#14A568' : '#FF5656' }">
                        {{record.scope.online_status ? '在线' : '离线'}}
                    </span>
                </template>
                <template slot="abnormal_code" slot-scope="record">
                    <span>
                        {{ abnormalObj[record.scope.abnormal_code] }}
                    </span>
                </template>
                <template slot="operation">
                    <bk-button class="mr10" theme="primary" text>重置</bk-button>
                </template>
            </common-table>
        </div>
        <!--  批量收回对话框   -->
        <batch-recycle ref="batchRecycle" :selected="selectedRows"></batch-recycle>
        <!--  新增分配抽屉栏  -->
        <add-distribute ref="distributeDialog"></add-distribute>
    </div>
</template>

<script>
    import searchInput from '@/components/searchInput'
    import commonTable from '@/components/table/comTable'
    import advancedSearch from '@/components/popover/advancedSearch'
    import batchRecycle from '../components/batchRecycle'
    import addDistribute from '../components/addDistribute'

    export default {
        name: 'home',
        components: {
            commonTable,
            searchInput,
            advancedSearch,
            batchRecycle,
            addDistribute
        },
        data() {
            return {
                copyData: [],
                columns: [],
                searchValue: '',
                loading: false,
                statusColorObj: {
                    '2': '#91B6F5',
                    '1': '#7ED4B2',
                    '4': '#9DB1CE',
                    '3': '#E9B76E'
                },
                statusObj: {
                    '1': '未分配',
                    '2': '已分配',
                    '3': '待回收',
                    '4': '已回收'
                },
                abnormalObj: {
                    '1': '未分配但在线',
                    '2': '已分配但离线超过时限',
                    '3': 'CMDB无此IP记录',
                    '4': 'CMDB同步属性变动',
                    '5': '本地无此IP但CMDB中存在',
                    '6': '未分配但CMDB中存在'
                },
                selectedRows: [],
                pagination: {
                    current: 1,
                    count: 3,
                    limit: 10
                },
                // 动态表头的数据集合
                settingsFields: [
                    {
                        key: 'ip',
                        label: 'IP地址',
                        disabled: true,
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入IP地址',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        key: 'ip_pool',
                        label: '地址池名称',
                        conditionAttr: {
                            widget: 'data-select',
                            label: '地址池',
                            custom: true,
                            name: 'ip_pool',
                            placeholder: '请输入地址池',
                            attr: {
                                clearable: true,
                                remote: true,
                                filterable: true,
                                searchable: true,
                                popperAppendToBody: false,
                                url: 'searchPool',
                                detailUrl: 'poolDetail',
                                initFlag: true
                            }
                        }
                    },
                    {
                        key: 'offline_at',
                        label: '离线时间',
                        attr: {
                            minWidth: '160px',
                            showOverflowTooltip: true
                        },
                        conditionAttr: {
                            widget: 'date-picker',
                            placeholder: '请选择...',
                            attr: {
                                style: { width: '100%' },
                                transfer: true,
                                clearable: true,
                                type: 'daterange',
                                shortcutClose: true,
                                useShortcutText: false,
                                shortcuts: [
                                    {
                                        text: '今天',
                                        value() {
                                            const end = new Date()
                                            const start = new Date()
                                            return [start, end]
                                        }
                                    },
                                    {
                                        text: '近7天',
                                        value() {
                                            const end = new Date()
                                            const start = new Date()
                                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                                            return [start, end]
                                        }
                                    },
                                    {
                                        text: '近15天',
                                        value() {
                                            const end = new Date()
                                            const start = new Date()
                                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 15)
                                            return [start, end]
                                        }
                                    },
                                    {
                                        text: '近30天',
                                        value() {
                                            const end = new Date()
                                            const start = new Date()
                                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                                            return [start, end]
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        key: 'offline_days',
                        label: '离线天数',
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入离线天数',
                            attr: {
                                clearable: true,
                                type: 'number',
                                min: 0
                            }
                        }
                    },
                    {
                        key: 'gateway',
                        label: '网关',
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入网关',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        key: 'dns',
                        label: 'DNS服务器',
                        conditionAttr: {
                            widget: 'input',
                            label: 'DNS',
                            placeholder: '请输入DNS服务器',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        key: 'allocate_status',
                        label: '分配状态',
                        scopedSlots: { customRender: 'status' },
                        conditionAttr: {
                            widget: 'data-select',
                            custom: true,
                            placeholder: '请选择相关数据',
                            size: 'small',
                            defaultValue: [],
                            attr: {
                                searchable: false,
                                multiple: false,
                                popperAppendToBody: false,
                                clearable: true,
                                options: [
                                    {
                                        id: '1',
                                        name: '未分配'
                                    },
                                    {
                                        id: '2',
                                        name: '已分配'
                                    },
                                    {
                                        id: '3',
                                        name: '待回收'
                                    },
                                    {
                                        id: '4',
                                        name: '已回收'
                                    }
                                ]
                            }
                        }
                    },
                    {
                        key: 'online_status',
                        label: '在线状态',
                        scopedSlots: { customRender: 'online_status' },
                        conditionAttr: {
                            widget: 'data-select',
                            custom: true,
                            placeholder: '请选择相关数据',
                            size: 'small',
                            defaultValue: [],
                            attr: {
                                searchable: false,
                                multiple: false,
                                popperAppendToBody: false,
                                clearable: true,
                                options: [
                                    {
                                        id: 1,
                                        name: '在线'
                                    },
                                    {
                                        id: 0,
                                        name: '离线'
                                    }
                                ]
                            }
                        }
                    },
                    {
                        key: 'abnormal_code',
                        label: '异常原因',
                        scopedSlots: { customRender: 'abnormal_code' },
                        attr: {
                            showOverflowTooltip: true
                        },
                        conditionAttr: {
                            widget: 'data-select',
                            custom: true,
                            placeholder: '请选择异常原因',
                            size: 'small',
                            defaultValue: [],
                            attr: {
                                searchable: false,
                                multiple: false,
                                popperAppendToBody: false,
                                clearable: true,
                                options: [
                                    {
                                        id: '1',
                                        name: '未分配但在线'
                                    },
                                    {
                                        id: '2',
                                        name: '已分配但离线超过时限'
                                    },
                                    {
                                        id: '3',
                                        name: 'CMDB无此IP记录'
                                    },
                                    {
                                        id: '4',
                                        name: 'CMDB同步属性变动'
                                    },
                                    {
                                        id: '5',
                                        name: '本地无此IP但CMDB中存在'
                                    },
                                    {
                                        id: '6',
                                        name: '未分配但CMDB中存在'
                                    }
                                ]
                            }
                        }
                    }
                ],
                // 高级搜索面板的条件配置数据
                formWidgets: [],
                // 批量修改的数据
                formData: {
                    name: ''
                },
                // 搜索条件的缓存数据
                searchParams: {},
                isDropdownShow: false
            }
        },
        watch: {
            searchValue(newV) {
                if (!newV) {
                    this.onSearch()
                }
            }
        },
        created() {
            this.fetchData()
            const stateColumns = this.$store.state.product.tableColumns.ip_abnormal
            if (stateColumns.length > 0) {
                this.columns = [...stateColumns]
            } else {
                this.columns = this.settingsFields.slice(0, 7).concat(this.columns)
            }
            const adnvancedWidget = this.columns.map(item => {
                return {
                    name: item.key,
                    label: item.label,
                    ...item.conditionAttr
                }
            })
            const _arr = ['offline_days']
            this.formWidgets = adnvancedWidget.filter(data => !_arr.includes(data.name))
        },
        methods: {
            async fetchData(params = {}) {
                this.loading = true
                try {
                    const res = await this.$api.search_ip_abnormal({
                        page: this.pagination.current,
                        page_size: this.pagination.limit,
                        ...this.searchParams,
                        ...params
                    })
                    if (res.result) {
                        const _data = res.data.results
                        this.copyData = _data.map(item => {
                            delete item['ip']
                            return {...item['ip_obj'], ...item}
                        })
                        this.pagination.count = res.data.count
                    } else {
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading = false
                }
            },
            selectChange(selection) {
                this.selectedRows = selection
            },
            handlePageChange(page) {
                this.pagination.current = page
                this.fetchData()
            },
            limitChange(limit) {
                this.pagination.current = 1
                this.pagination.limit = limit
                this.fetchData()
            },
            onSearch(value) {
                this.searchParams = {search: value}
                this.pagination.current = 1
                this.fetchData({
                    search: value
                })
            },
            handleAdvancedSearch(params) {
                Object.keys(params).forEach(item => {
                    if (item === 'offline_at') {
                        if (params[item][0] && params[item][1]) {
                            params['ip__' + item + '__gte'] = this.$moment(params[item][0]).format('YYYY-MM-DD HH:mm:ss')
                            params['ip__' + item + '__lte'] = this.$moment(params[item][1]).format('YYYY-MM-DD HH:mm:ss')
                            delete params[item]
                        } else {
                            delete params[item]
                        }
                    }
                    if (!params[item] && params[item] !== 0) {
                        delete params[item]
                    }
                })
                this.searchParams = {...params}
                this.fetchData({...params})
            },
            // 批量回收的触发事件
            handleRecycle() {
                if (this.selectedRows.length === 0) {
                    this._warnMessage('请先选择要回收的IP地址')
                    return false
                }
                this.$refs.batchRecycle.showDialog()
            },
            // 确认异常触发事件
            confirmNormal() {
                if (this.selectedRows.length === 0) {
                    this._warnMessage('请先选择确认为异常的IP')
                    return false
                }
                const idList = []
                for (const item of this.selectedRows) {
                    idList.push(item.id)
                }
                this.$bkInfo({
                    title: '确认将该异常从清单中清除吗？',
                    subTitle: '如该异常仍存在，将在下一次周期检测时重新纳入异常清单中。',
                    confirmLoading: true,
                    confirmFn: async() => {
                        try {
                            const res = await this.$api.confirm_ip_abnormal({abnormal_ips: idList})
                            if (res.result) {
                                this._successMessage('确认成功')
                                this.onSearch()
                                return true
                            } else {
                                this._errorMessage(res.message)
                                return true
                            }
                        } catch (e) {
                            return false
                        }
                    }
                })
            },
            // 确认异常触发事件
            confirmOffline() {
                if (this.selectedRows.length === 0) {
                    this._warnMessage('请先选择加入离线白名单的IP')
                    return false
                }
                this.$bkInfo({
                    width: 500,
                    title: '确认将这些IP加入离线白名单吗？',
                    confirmLoading: true,
                    confirmFn: async() => {
                        try {
                            const ipList = this.selectedRows.map(i => { return i.ip_obj.id })
                            const res = await this.$api.add_offline_except({ip_list: ipList})
                            if (res.result) {
                                this._successMessage('加入离线白名单成功')
                                this.onSearch()
                                return true
                            } else {
                                this._errorMessage(res.message)
                                return true
                            }
                        } catch (e) {
                            return false
                        }
                    }
                })
            },
            // 点击显示弹出层的统一触发事件
            handleVisible(name) {
                this.$refs[name].showDialog()
            },
            handleSettingChange(copyData, columns) {
                const _arr = ['offline_days']
                this.formWidgets = copyData.filter(data => !_arr.includes(data.name))
                // vuex缓存表格头设置的信息
                this.$store.commit('setTableColumns', {column: columns, key: 'ip_abnormal'})
            },
            // 导出excel
            toExport() {
                let _params = ''
                Object.keys(this.searchParams).forEach(item => {
                    _params = _params + `&${item}=${this.searchParams[item]}`
                })
                const url = window.siteUrl + 'ip_abnormal/export_excel/?page=1&page_size=-1' + _params
                window.open(url)
            },
            // 下拉菜单操作
            dropdownShow() {
                this.isDropdownShow = true
            },
            dropdownHide() {
                this.isDropdownShow = false
            },
            triggerHandler() {
                this.$refs.dropdown.hide()
            }
        }
    }
</script>

<style scoped lang="scss">
.radius-tip {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
}
.dropdown-trigger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #c4c6cc;
    height: 32px;
    line-height: 32px;
    min-width: 68px;
    border-radius: 2px;
    padding: 0 15px;
    color: #63656E;
    font-size: 14px;
    background-color: #FFF;
}
.dropdown-trigger-btn.bk-icon {
    font-size: 18px;
}
.dropdown-trigger-btn .bk-icon {
    font-size: 22px;
}
.dropdown-trigger-btn:hover {
    cursor: pointer;
    border-color: #979ba5;
}
/deep/ .bk-dropdown-content {
    overflow: visible !important;
    .bk-dropdown-list {
        margin-top: -5px;
    }
}
/deep/ .bk-dropdown-menu .bk-dropdown-list > li {
    background-color: #fff;
    border-left: 1px solid #ccc;
    border-right: 1px solid #ccc;
}
/deep/ .bk-dropdown-menu .bk-dropdown-list > li:first-child {
    background-color: #fff;
    border: 1px solid #ccc;
    border-bottom: none;
    border-top: none;
}
/deep/ .bk-dropdown-menu .bk-dropdown-list > li:last-child {
    background-color: #fff;
    border-bottom: 1px solid #ccc;
}
</style>
