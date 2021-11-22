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
                    <bk-button @click="handleVisible()">
                        导入
                    </bk-button>
                    <bk-button :title="'添加子网'" @click="toModify()">
                        添加子网
                    </bk-button>
                    <bk-button :title="'导出Excel'" @click="toExport" v-if="datas.length > 0">
                        导出Excel
                    </bk-button>
                </div>
            </div>
        </div>
        <div v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <common-table
                :data="datas"
                :columns="columns"
                :select-column="{ visible: false, fixed: true }"
                :order-column="{ visible: false, fixed: false }"
                :pagination="pagination"
                :settings-fields="settingsFields"
                @handleSettingChange="handleSettingChange"
                @sort-change="handleSortChange"
                @page-change="handlePageChange"
                @page-limit-change="limitChange"
            >
                <template slot="percent" slot-scope="record">
                    {{record.scope.usedPercent}}%
                </template>
                <template slot="operation" slot-scope="record">
                    <bk-button class="mr10" theme="primary" text @click="toModify(record.scope)">修改</bk-button>
                    <bk-popconfirm
                        trigger="click"
                        title="确认删除该地址池吗？"
                        content="删除操作无法撤回，请谨慎操作！"
                        @confirm="toDelete(record.scope)">
                        <bk-button class="mr10" theme="primary" text>删除</bk-button>
                    </bk-popconfirm>
                </template>
            </common-table>
        </div>
        <!--  编辑地址池  -->
        <edit-address-pool v-model="modifyVisible"
            :current-item="currentItem"
            :segment-attr="segmentAttr"
            @ok="modifyIpNetSuccess">
        </edit-address-pool>
        <!--  导入对话框   -->
        <import-dialog ref="importDialog"
            @ok-confirm="fetchData"></import-dialog>
    </div>
</template>

<script>
    import searchInput from '@/components/searchInput'
    import commonTable from '@/components/table/comTable'
    import advancedSearch from '@/components/popover/advancedSearch'
    import editAddressPool from './modify'
    import importDialog from '../components/import'
    export default {
        name: 'home',
        components: {
            commonTable,
            searchInput,
            advancedSearch,
            editAddressPool,
            importDialog
        },
        data() {
            return {
                loading: false,
                importLoading: false,
                searchValue: '',
                datas: [],
                columns: [
                    {
                        label: '操作',
                        key: 'operation',
                        width: '100px',
                        scopedSlots: { customRender: 'operation' }
                    }
                ],
                pagination: {
                    current: 1,
                    count: 3,
                    limit: 10
                },
                sort: {
                    prop: 'create_at',
                    order: 'descending'
                },
                formWidgets: [],
                settingsFields: [
                    {
                        label: '地址池名称',
                        key: 'ip_pool_name',
                        align: 'left',
                        sortable: true,
                        attr: {
                            minWidth: '110px'
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
                        label: 'ip子网',
                        key: 'ip_net',
                        align: 'left',
                        attr: {
                            minWidth: '150px'
                        },
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入ip子网',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        label: '云区域',
                        key: 'bk_cloud_id',
                        align: 'right',
                        attr: {
                            minWidth: '90px'
                        },
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入云区域',
                            attr: {
                                clearable: true,
                                min: 0,
                                type: 'number'
                            }
                        }
                    },
                    {
                        label: '网关',
                        key: 'gateway',
                        align: 'left',
                        attr: {
                            minWidth: '120px'
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
                        label: 'DNS服务器',
                        key: 'dns',
                        align: 'left',
                        attr: {
                            minWidth: '120px'
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
                        label: 'IP数（可分配/有效数）',
                        key: 'ip_count',
                        attr: {
                            minWidth: '160px'
                        },
                        align: 'left'
                    },
                    {
                        label: '保留IP数',
                        key: 'reserve_ip_count',
                        align: 'right'
                    },
                    {
                        label: '添加时间',
                        key: 'create_at',
                        align: 'left',
                        sortable: true,
                        attr: {
                            minWidth: '150px'
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
                modifyVisible: false,
                currentItem: {},
                // 子网自定义属性
                segmentAttr: [],
                searchParams: {},
                customAttrNames: []
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
            const stateColumns = this.$store.state.product.tableColumns.ip_net
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
            const _arr = ['ip_count', 'reserve_ip_count']
            this.formWidgets = adnvancedWidget.filter(data => !_arr.includes(data.name))
        },
        mounted() {
            this.fetchData()
            this.getCustomAttr()
        },
        methods: {
            async fetchData(params = {}) {
                this.loading = true
                // page:页数, page_size:每页数
                try {
                    let sort = this.getProp()
                    if (sort === null || sort === undefined) {
                        sort = 'create_at'
                    }
                    const res = await this.$api.search_ip_net({
                        ...this.searchParams,
                        ...params,
                        page: this.pagination.current,
                        page_size: this.pagination.limit,
                        sort: this.sort.order === 'ascending' ? sort : '-' + sort
                    })
                    if (res.result) {
                        this.pagination.count = res.data.count
                        res.data.results.forEach(item => {
                            item.custom_attr.forEach(attr => {
                                item[attr.name] = attr.value
                            })
                        })
                        this.datas = res.data.results
                    } else {
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading = false
                }
            },
            getProp() {
                return this.sort.prop === 'ip_pool_name' ? 'ip_pool__name' : this.sort.prop
            },
            async getCustomAttr() {
                const res = await this.$api.searchCustom({
                    type: 'tetwork_segment'
                })
                if (res.result) {
                    this.segmentAttr = res.data.results
                    res.data.results.forEach(item => {
                        this.settingsFields.push({
                            label: item.display_name,
                            key: item.name,
                            align: 'left',
                            attr: {
                                minWidth: '100px'
                            },
                            conditionAttr: {
                                widget: 'input',
                                placeholder: `请输入${item.display_name}`,
                                attr: {
                                    clearable: true
                                }
                            }
                        })
                        this.customAttrNames.push(item.name)
                    })
                    const adnvancedWidget = this.columns.map(item => {
                        return {
                            name: item.key,
                            label: item.label,
                            ...item.conditionAttr
                        }
                    })
                    const _arr = ['ip_count', 'reserve_ip_count', ...this.customAttrNames]
                    this.formWidgets = adnvancedWidget.filter(item => !_arr.includes(item.name))
                } else {
                    this.segmentAttr = []
                }
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
            handleSettingChange(datas, columns) {
                const _arr = ['ip_count', 'reserve_ip_count', ...this.customAttrNames]
                this.formWidgets = datas.filter(data => !_arr.includes(data.name))
                // vuex缓存表格头设置的信息
                this.$store.commit('setTableColumns', {column: columns, key: 'ip_net'})
            },
            handleAdvancedSearch(params) {
                Object.keys(params).forEach(item => {
                    if (item === 'create_at' || item === 'update_at') {
                        if (params[item][0] && params[item][1]) {
                            params[item + '__gte'] = this.$moment(params[item][0]).format('YYYY-MM-DD HH:mm:ss')
                            params[item + '__lte'] = this.$moment(params[item][1]).format('YYYY-MM-DD HH:mm:ss')
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
            handleSortChange({ column, prop, order }) {
                this.sort.prop = prop
                this.sort.order = order
                this.fetchData()
            },
            // 点击编辑地址池触发事件
            toModify(record) {
                this.modifyVisible = true
                if (record) {
                    this.currentItem = {...record}
                } else {
                    this.currentItem = {
                        ip_pool: '',
                        formList: [{
                            ip_net: '',
                            bk_cloud_id: '0',
                            gateway: '',
                            dns: '',
                            vlan_id: ''
                        }]
                    }
                }
            },
            modifyIpNetSuccess(type) {
                if (type === 'add') {
                    this.pagination.current = 1
                }
                this.modifyVisible = false
                this.fetchData()
            },
            // 点击删除地址池触发事件
            async toDelete(record) {
                const res = await this.$api.delete_ip_net({id: record.id})
                if (res.result) {
                    this._successMessage(res.message)
                    if (this.pagination.current > 1 && this.datas.length === 1) {
                        this.pagination.current--
                    }
                    this.fetchData()
                } else {
                    this._errorMessage(res.message)
                }
            },
            handleVisible() {
                this.$refs.importDialog.showDialog()
            },
            // 导出excel
            toExport() {
                let _params = ''
                Object.keys(this.searchParams).forEach(item => {
                    _params = _params + `&${item}=${this.searchParams[item]}`
                })
                const url = window.siteUrl + 'ip_net/export_excel/?page=1&page_size=-1' + _params
                window.open(url)
            }
        }
    }
</script>

<style scoped lang="scss">
.file-upload-wrapper {
    width: 68px;
    height: 32px;
    position: relative;
    display: inline-block;
    >input {
        opacity: 0;
        position: absolute;
        top: 0;
        left: 0;
    }
}
</style>
