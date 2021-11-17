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
            <advanced-search :form-widgets="getFormWidget" @submit="handleAdvancedSearch"></advanced-search>
            <div class="operation-container">
                <div>
                    <bk-button :title="'新增IP'" @click="$refs['offlineWhiteDialog'].showDialog()">
                        新增IP
                    </bk-button>
                    <bk-button :title="'批量剔除'" @click="batchDelete">
                        批量删除
                    </bk-button>
                    <bk-button :title="'导出Excel'" @click="toExport" v-if="copyData.length > 0">
                        导出Excel
                    </bk-button>
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
                <template slot="operation" slot-scope="record">
                    <bk-popconfirm
                        trigger="click"
                        title="确认删除该名单？"
                        content="删除操作无法撤回，请谨慎操作！"
                        @confirm="toDelete(record.scope)">
                        <bk-button class="mr10" theme="primary" text>删除</bk-button>
                    </bk-popconfirm>
                </template>
            </common-table>
        </div>
        <add-offlineWhite ref="offlineWhiteDialog" @submit="fetchData"></add-offlineWhite>
    </div>
</template>

<script>
    import searchInput from '@/components/searchInput'
    import commonTable from '@/components/table/comTable'
    import advancedSearch from '@/components/popover/advancedSearch'
    import addOfflineWhite from './addOfflineWhite'

    export default {
        name: 'home',
        components: {
            commonTable,
            searchInput,
            advancedSearch,
            addOfflineWhite
        },
        data() {
            return {
                addIpVisible: false,
                searchValue: '',
                copyData: [],
                columns: [
                    {
                        label: '操作',
                        key: 'operation',
                        width: '60px',
                        scopedSlots: { customRender: 'operation' }
                    }
                ],
                // 分配状态的颜色字典
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
                        attr: {
                            minWidth: '100px'
                        },
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
                        attr: {
                            minWidth: '100px'
                        },
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
                        key: 'ip_net',
                        label: 'IP子网',
                        attr: {
                            minWidth: '150px'
                        },
                        conditionAttr: {
                            widget: 'ip-net-select',
                            placeholder: '请选择子网',
                            label: '子网',
                            custom: true,
                            name: 'ip_net',
                            attr: {
                                nameKey: 'ip_pool',
                                remote: true,
                                filterable: true,
                                searchable: true,
                                popperAppendToBody: false,
                                clearable: true,
                                url: 'search_ip_net',
                                detailUrl: 'poolNetDetail',
                                initFlag: true
                            }
                        }
                    },
                    {
                        key: 'bk_cloud_id',
                        label: '云区域',
                        attr: {
                            minWidth: '100px'
                        },
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入云区域',
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
                        attr: {
                            minWidth: '100px'
                        },
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
                        attr: {
                            minWidth: '100px'
                        },
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
                        attr: {
                            minWidth: '100px'
                        },
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
                        key: 'create_at',
                        label: '添加时间',
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
                    }
                ],
                // 高级搜索面板的条件配置数据
                formWidgets: [],
                // 批量修改的数据
                formData: {
                    name: ''
                },
                loading: false,
                // 搜索条件的缓存数据
                searchParams: {}
            }
        },
        computed: {
            getFormWidget() {
                const newWidgets = this.formWidgets.concat()
                // 处理新的数组变量
                newWidgets.pop()
                return newWidgets
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
            const stateColumns = this.$store.state.product.tableColumns.ip_offline
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
            this.formWidgets = [...adnvancedWidget]
            this.fetchData()
        },
        methods: {
            async fetchData(params = {}) {
                this.loading = true
                try {
                    const res = await this.$api.search_offlineWhite({
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
                this.pagination.limit = limit
                this.pagination.current = 1
                this.fetchData()
            },
            handleAdvancedSearch(params) {
                Object.keys(params).forEach(item => {
                    if (item === 'create_at') {
                        if (params[item][0] && params[item][1]) {
                            params[item + '__gte'] = this.$moment(params[item][0]).format('YYYY-MM-DD hh:mm:ss')
                            params[item + '__lte'] = this.$moment(params[item][1]).format('YYYY-MM-DD hh:mm:ss')
                            delete params[item]
                        } else {
                            delete params[item]
                        }
                    }
                    if (!params[item]) {
                        delete params[item]
                    }
                })
                this.pagination.current = 1
                this.searchParams = {...params}
                this.fetchData({...params})
            },
            // 批量剔除
            async batchDelete() {
                if (this.selectedRows.length === 0) {
                    this._warnMessage('请先选择要剔除离线白名单的Ip')
                    return false
                }
                const idList = []
                for (const item of this.selectedRows) {
                    idList.push(item.id)
                }
                const res = await this.$api.delete_multi_offlineWhite({
                    ip_ids: idList
                })
                if (res.result) {
                    this._successMessage('删除成功')
                    this.onSearch()
                } else {
                    this._errorMessage(res.message)
                }
            },
            async toDelete(scope) {
                const res = await this.$api.delete_single_offlineWhite({
                    id: scope.id
                })
                if (res.result) {
                    this._successMessage('删除成功')
                    if (this.pagination.current > 1 && this.copyData.length === 1) {
                        this.pagination.current--
                    }
                    this.fetchData()
                } else {
                    this._errorMessage(res.message)
                }
            },
            handleSettingChange(datas, columns) {
                this.formWidgets = [...datas]
                // vuex缓存表格头设置的信息
                this.$store.commit('setTableColumns', {column: columns, key: 'ip_offline'})
            },
            onSearch(value) {
                this.searchParams = {search: value}
                this.pagination.current = 1
                this.fetchData({
                    search: value
                })
            },
            // 导出excel
            toExport() {
                let _params = ''
                Object.keys(this.searchParams).forEach(item => {
                    _params = _params + `&${item}=${this.searchParams[item]}`
                })
                const url = window.siteUrl + 'offline_except/export_excel/?page=1&page_size=-1' + _params
                window.open(url)
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
</style>
