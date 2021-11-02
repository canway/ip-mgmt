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
                    <bk-button :title="'导出'" @click="toExport" v-if="datas.length > 0">
                        导出
                    </bk-button>
                    <bk-button :title="'导出'" @click="batchCheck" :disabled="batchCheckDisable">
                        批量检测
                    </bk-button>
                    <bk-button :title="'导出'" @click="batchModify">
                        批量修改
                    </bk-button>
                    <bk-dropdown-menu trigger="click" @show="dropdownShow" @hide="dropdownHide" ref="dropdown">
                        <div class="dropdown-trigger-btn" style="padding-left: 19px;" slot="dropdown-trigger">
                            <span>更多操作</span>
                            <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                        </div>
                        <ul class="bk-dropdown-list" slot="dropdown-content">
                            <li><a href="javascript:;" @click="handleRecycle">批量回收</a></li>
                            <li><a href="javascript:;" @click="handleVisible('importDialog')">导入分配</a></li>
                            <li><a href="javascript:;" @click="handleVisible('distributeDialog')">新增分配</a></li>
                            <li><a href="javascript:;" @click="handleVisible('reserveDialog')">新增保留</a></li>
                        </ul>
                    </bk-dropdown-menu>
                </div>
            </div>
        </div>
        <div v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <common-table
                :data="datas"
                :columns="columns"
                :select-column="{ visible: true, fixed: true }"
                :order-column="{ visible: false, fixed: false }"
                @selection-change="selectChange"
                :settings-fields="settingsFields"
                :pagination="pagination"
                @handleSettingChange="handleSettingChange"
                @sort-change="handleSortChange"
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
                <template slot="reserve_status" slot-scope="record">
                    <span
                        :style="{ color: record.scope.reserve_status ? '#14A568' : '#FF5656' }">
                        {{record.scope.reserve_status ? '保留' : '未保留'}}
                    </span>
                </template>
                <template slot="operation" slot-scope="record">
                    <bk-button class="mr10" theme="primary" text @click="ipCheck(record.scope)"
                        :disabled="record.scope.checking">立即检测
                    </bk-button>
                </template>
            </common-table>
        </div>
        <!--  批量修改抽屉栏   -->
        <batch-modify :is-edit="true"
            :form-data="formData"
            v-model="batchModifyVisible"
            :form-widgets="batchWidgets"
            title="IP地址批量修改"
            :submit-loading="isConfirm"
            @submit="toComfirmModify">
        </batch-modify>
        <!--  批量收回对话框   -->
        <batch-recycle ref="batchRecycle"
            :selected="selectedRows"
            @ok-recycle="fetchData">
        </batch-recycle>
        <!--  导入分配对话框   -->
        <import-dialog ref="importDialog"
            @ok-confirm="fetchData"></import-dialog>
        <!--  新增分配抽屉栏  -->
        <add-distribute ref="distributeDialog"
            @ok-confirm="fetchData"></add-distribute>
        <!--  新增保留抽屉栏  -->
        <add-reserve ref="reserveDialog"
            @ok-confirm="fetchData"></add-reserve>
    </div>
</template>

<script>
    import advancedSearch from '@/components/popover/advancedSearch'
    import searchInput from '@/components/searchInput'
    import commonTable from '@/components/table/comTable'
    import batchModify from '@/components/modify'
    import batchRecycle from './components/batchRecycle'
    import addDistribute from './components/addDistribute'
    import importDialog from './components/import_ips'
    import addReserve from './components/addReserve'

    export default {
        name: 'home',
        components: {
            advancedSearch,
            commonTable,
            searchInput,
            batchModify,
            batchRecycle,
            addDistribute,
            importDialog,
            addReserve
        },
        data() {
            return {
                loading: false,
                searchValue: '',
                datas: [],
                columns: [{
                    label: '状态检测',
                    key: 'operation',
                    width: '100px',
                    scopedSlots: {customRender: 'operation'}
                }],
                checking: false,
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
                sort: {
                    prop: 'create_at',
                    order: 'descending'
                },
                // 动态表头的数据集合
                settingsFields: [
                    {
                        label: 'IP地址',
                        key: 'ip',
                        disabled: true,
                        attr: {
                            minWidth: '125px'
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
                        label: '地址池名称',
                        key: 'ip_pool',
                        disabled: true,
                        attr: {
                            minWidth: '120px'
                        },
                        sortable: true,
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
                        label: 'IP子网',
                        key: 'ip_net_name',
                        disabled: true,
                        attr: {
                            minWidth: '125px'
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
                        label: '云区域',
                        key: 'bk_cloud_id',
                        align: 'right',
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入云区域',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        label: '网关',
                        key: 'gateway',
                        attr: {
                            minWidth: '125px'
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
                        attr: {
                            minWidth: '125px'
                        },
                        conditionAttr: {
                            widget: 'input',
                            label: 'DNS',
                            placeholder: '请输入DNS',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        label: '分配状态',
                        key: 'allocate_status',
                        scopedSlots: {customRender: 'status'},
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
                        label: '在线状态',
                        key: 'online_status',
                        scopedSlots: {customRender: 'online_status'},
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
                                        id: 2,
                                        name: '离线'
                                    }
                                ]
                            }
                        }
                    },
                    {
                        label: '保留状态',
                        key: 'reserve_status',
                        scopedSlots: {customRender: 'reserve_status'},
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
                                        name: '保留'
                                    },
                                    {
                                        id: 2,
                                        name: '未保留'
                                    }
                                ]
                            }
                        }
                    },
                    {
                        label: '业务系统',
                        key: 'business_system',
                        attr: {
                            minWidth: '125px'
                        },
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入业务系统',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        label: '运维人员',
                        key: 'member',
                        attr: {
                            minWidth: '125px'
                        },
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入运维人员',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        label: '分配时间',
                        key: 'allocate_at',
                        align: 'left',
                        attr: {
                            minWidth: '130px'
                        },
                        conditionAttr: {
                            widget: 'date-picker',
                            placeholder: '请选择...',
                            attr: {
                                style: {width: '100%'},
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
                        label: '离线时间',
                        key: 'offline_at',
                        align: 'left',
                        attr: {
                            minWidth: '130px'
                        },
                        conditionAttr: {
                            widget: 'date-picker',
                            placeholder: '请选择...',
                            attr: {
                                style: {width: '100%'},
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
                        label: '描述',
                        key: 'description',
                        align: 'left',
                        sortable: true,
                        attr: {
                            minWidth: '130px',
                            showOverflowTooltip: true
                        },
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入描述',
                            attr: {
                                clearable: true
                            }
                        }
                    },
                    {
                        label: '过期时间',
                        key: 'expired_at',
                        align: 'left',
                        attr: {
                            minWidth: '130px'
                        },
                        conditionAttr: {
                            widget: 'date-picker',
                            placeholder: '请选择...',
                            attr: {
                                style: {width: '100%'},
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
                        label: '扫描时间',
                        key: 'scan_at',
                        align: 'left',
                        attr: {
                            minWidth: '130px'
                        },
                        conditionAttr: {
                            widget: 'date-picker',
                            placeholder: '请选择...',
                            attr: {
                                style: {width: '100%'},
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
                        label: '备注',
                        key: 'remark',
                        attr: {
                            minWidth: '125px'
                        },
                        conditionAttr: {
                            widget: 'input',
                            placeholder: '请输入备注',
                            attr: {
                                clearable: true
                            }
                        }
                    }
                ],
                // 高级搜索面板的条件配置数据
                formWidgets: [],
                // 批量修改的数据
                formData: {
                    gateway: '',
                    dns: '',
                    offline_at: '',
                    reserve_status: 1,
                    description: ''
                },
                isConfirm: false,
                // 批量修改的表单配置数据
                batchWidgets: [
                    {
                        widget: 'input',
                        name: 'gateway',
                        label: '网关',
                        required: false,
                        placeholder: '请输入网关',
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'dns',
                        label: 'DNS服务器',
                        required: false,
                        placeholder: '请输入DNS服务器',
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'date-picker',
                        name: 'offline_at',
                        label: '过期时间',
                        placeholder: '请选择...',
                        attr: {
                            style: {width: '100%'},
                            transfer: true,
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'data-select',
                        name: 'reserve_status',
                        label: '保留状态',
                        custom: true,
                        placeholder: '请选择相关数据',
                        size: 'small',
                        attr: {
                            searchable: false,
                            multiple: false,
                            popperAppendToBody: false,
                            clearable: true,
                            options: [{
                                          id: 1,
                                          name: '保留'
                                      },
                                      {
                                          id: 2,
                                          name: '未保留'
                                      }]
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'business_system',
                        label: '业务系统',
                        required: false,
                        placeholder: '请输入业务系统',
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'description',
                        label: '描述',
                        required: false,
                        placeholder: '请输入描述',
                        attr: {
                            clearable: true,
                            type: 'textarea'
                        },
                        disabled: true
                    }
                ],
                // 批量修改抽屉展示状态
                batchModifyVisible: false,
                customAttr: [],
                // 搜索条件的缓存数据
                searchParams: {},
                isDropdownShow: false,
                batchCheckDisable: false,
                customAttrNames: []
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
            const stateColumns = this.$store.state.product.tableColumns.ip
            if (stateColumns.length > 0) {
                this.columns = [...stateColumns]
            } else {
                this.columns = this.settingsFields.slice(0, 8).concat(this.columns)
            }
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
                    const res = await this.$api.search_ip({
                        ...this.searchParams,
                        ...params,
                        page: this.pagination.current,
                        page_size: this.pagination.limit,
                        sort: this.sort.order === 'ascending' ? sort : '-' + sort
                    })
                    if (res.result) {
                        this.pagination.count = res.data.count
                        this.datas = res.data.results || []
                        this.datas.forEach(item => {
                            item.expired_at = item.expired_at && item.expired_at.split(' ')[0]
                            item.custom_attr.forEach(attr => {
                                item[attr.name] = attr.value
                            })
                        })
                    } else {
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading = false
                }
            },
            getProp() {
                return this.sort.prop === 'ip_pool' ? 'ip_net__ip_pool__name' : this.sort.prop
            },
            async getCustomAttr() {
                const res = await this.$api.searchCustom({
                    type: 'ips'
                })
                if (res.result) {
                    this.customAttr = res.data.results
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
                        this.batchWidgets.push({
                            widget: 'input',
                            name: item.name,
                            label: item.display_name,
                            required: false,
                            placeholder: `请输入${item.display_name}`,
                            attr: {
                                clearable: true
                            },
                            disabled: true
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
                    const _arr = ['operation', ...this.customAttrNames]
                    this.formWidgets = adnvancedWidget.filter(item => !_arr.includes(item.name))
                } else {
                    this.customAttr = []
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
                    const _times = ['allocate_at', 'offline_at', 'expired_at', 'scan_at']
                    if (_times.includes(item)) {
                        if (params[item][0] && params[item][1]) {
                            params[item + '__gte'] = this.$moment(params[item][0]).format('YYYY-MM-DD HH:mm:ss')
                            params[item + '__lte'] = this.$moment(params[item][1]).format('YYYY-MM-DD HH:mm:ss')
                            delete params[item]
                        } else {
                            delete params[item]
                        }
                    }
                    if (!params[item] && params[item] !== 0) {
                        delete params[item]
                    }
                    if (item === 'online_status') {
                        params[item] = params[item] === 1
                    }
                    if (item === 'reserve_status') {
                        params[item] = params[item] === 1
                    }
                })
                this.pagination.current = 1
                this.searchParams = {...params}
                this.fetchData({...params})
            },
            handleSettingChange(datas, columns) {
                const _arr = ['operation', ...this.customAttrNames]
                this.formWidgets = datas.filter(item => !_arr.includes(item.name))
                // vuex缓存表格头设置的信息
                this.$store.commit('setTableColumns', {column: columns, key: 'ip'})
            },
            handleSortChange({column, prop, order}) {
                this.sort.prop = prop
                this.sort.order = order
                this.fetchData()
            },
            // 批量修改
            batchModify() {
                if (this.selectedRows.length === 0) {
                    this._warnMessage('请先选择要修改的IP地址')
                    return false
                }
                this.batchModifyVisible = true
                this.formData = {
                    gateway: '',
                    dns: '',
                    offline_at: '',
                    reserve_status: 1,
                    description: ''
                }
            },
            // 确认批量修改的触发事件
            async toComfirmModify(data) {
                this.isConfirm = true
                if (data['gateway'] && !this.isValidateGateway(data['gateway'])) {
                    this._warnMessage('请输入正确的网关')
                    setTimeout(() => {
                        this.isConfirm = false
                    }, 500)
                    return false
                }
                if (data['dns'] && !this.isValidateGateway(data['dns'])) {
                    this._warnMessage('请输入正确的DNS服务器')
                    setTimeout(() => {
                        this.isConfirm = false
                    }, 500)
                    return false
                }
                if (data['offline_at']) {
                    data['offline_at'] = this.$moment(data['offline_at']).format('YYYY-MM-DD hh:mm:ss')
                }
                if (data['reserve_status']) {
                    data['reserve_status'] = data['reserve_status'] === 1
                }
                const _selectedIds = []
                this.selectedRows.forEach(row => {
                    _selectedIds.push(row.id)
                })
                try {
                    const res = await this.$api.ip_batch_update({
                        selected_ids: _selectedIds,
                        ...data
                    })
                    if (res.result) {
                        this._successMessage('更新成功')
                        this.batchModifyVisible = false
                        this.fetchData()
                    } else {
                        this._errorMessage(res.message)
                        this.batchModifyVisible = false
                    }
                } finally {
                    this.isConfirm = false
                }
            },
            // 网关和dns服务器的校验
            isValidateGateway(str) {
                const reg = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/
                return reg.test(str)
            },
            // 批量回收的触发事件
            handleRecycle() {
                if (this.selectedRows.length === 0) {
                    this._warnMessage('请先选择要回收的IP地址')
                    return false
                } else {
                    for (let i = 0; i < this.selectedRows.length; i++) {
                        if (this.selectedRows[i].allocate_status === '1') {
                            this._warnMessage('存在未分配的IP地址')
                            return false
                        }
                    }
                }
                this.$refs.batchRecycle.showDialog()
            },
            // 点击显示弹出层的统一触发事件
            handleVisible(name) {
                if (this.selectedRows.length > 0) {
                    const item = this.selectedRows[0]
                    const ipOption = []
                    for (let i = 0; i < this.selectedRows.length; i++) {
                        if (this.selectedRows[i].reserve_status && name === 'reserveDialog') {
                            this._warnMessage('存在已保留的IP地址')
                            return
                        }
                        if (this.selectedRows[i].allocate_status !== '1' && name === 'distributeDialog') {
                            this._warnMessage('只能操作未分配的IP地址')
                            return
                        }
                        if (this.selectedRows[i].ip_pool !== item.ip_pool || this.selectedRows[i].ip_net_name !== item.ip_net_name) {
                            this._warnMessage('IP必须同一地址池和子网')
                            return
                        }
                        ipOption.push({
                            id: this.selectedRows[i].id,
                            ip: this.selectedRows[i].ip
                        })
                    }
                    item.ipOption = ipOption
                    this.$refs[name].showDialog(item)
                } else {
                    this.$refs[name].showDialog()
                }
            },
            // 导出excel
            toExport() {
                let _params = ''
                Object.keys(this.searchParams).forEach(item => {
                    _params = _params + `&${item}=${this.searchParams[item]}`
                })
                const url = window.siteUrl + 'ip/export_excel/?page=1&page_size=-1' + _params
                window.open(url)
            },
            // 行立即检测按钮
            ipCheck(data) {
                this.$set(data, 'checking', true)
                this.$api.status_check({ips: data.ip}).then(res => {
                    if (res.result) {
                        this._successMessage('检测成功')
                        this.fetchData()
                    } else {
                        this._warnMessage('检测失败，请稍后重试')
                    }
                })
            },
            batchCheck() {
                const ips = []
                this.batchCheckDisable = true
                if (this.selectedRows.length > 0) {
                    this.selectedRows.forEach(item => {
                        ips.push(item.ip)
                    })
                    this.$api.status_check({ips: ips.join(',')}).then(res => {
                        if (res.result) {
                            this._successMessage('检测成功')
                            this.batchCheckDisable = false
                            this.fetchData()
                        } else {
                            this._warnMessage('检测失败，请稍后重试')
                        }
                    }, () => {
                        this.batchCheckDisable = false
                    })
                } else {
                    this.batchCheckDisable = false
                    this._warnMessage('请先选择要检测的IP地址')
                }
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
        border: 1px solid #dcdee5;
        border-top: none;
        border-bottom: none;
    }

    /deep/ .bk-dropdown-menu .bk-dropdown-list > li:first-child {
        border-bottom: none;
        border-top: none;
        border-top-right-radius: 2px;
        border-top-left-radius: 2px;
    }

    /deep/ .bk-dropdown-menu .bk-dropdown-list > li:last-child {
        border-bottom: 1px solid #dcdee5;
        border-bottom-right-radius: 2px;
        border-bottom-left-radius: 2px;
    }
</style>
