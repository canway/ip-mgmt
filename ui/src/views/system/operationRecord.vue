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
    <div class="table—wrapper content">
        <div class="header-table-operation">
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 5px;">操作者</span>
                <bk-input :clearable="true" v-model="searchParams.operator"
                    style="width: 200px; margin-right: 16px;"></bk-input>
                <span style="margin-right: 5px;">操作类型</span>
                <bk-select :disabled="false" v-model="searchParams.operate_type"
                    style="width: 200px; background-color: #FFF; margin-right: 16px;"
                    ext-cls="select-custom"
                    ext-popover-cls="select-popover-custom">
                    <bk-option v-for="option in operationType"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                    </bk-option>
                </bk-select>
                <span style="margin-right: 5px;">时间范围</span>
                <bk-date-picker style="margin-right: 16px;" :placeholder="'选择日期范围'" :type="'daterange'"
                    v-model="dateRange"></bk-date-picker>
                <bk-button :title="'搜索'" style="margin-right: 8px;" @click="onSearch">搜索</bk-button>
                <bk-button :title="'重置'" class="mr10" @click="onSearch('clearn')">重置</bk-button>
            </div>
        </div>
        <div v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <common-table
                :data="dataList"
                :columns="columns"
                :order-column="{ visible: false, fixed: false }"
                :pagination="pagination"
                @page-change="handlePageChange"
                @page-limit-change="limitChange"
            >
                <template slot="operate_type" slot-scope="record">
                    {{ operateTypeObj[record.scope.operate_type] }}
                </template>
                <template slot="operation" slot-scope="record">
                    <bk-button class="mr10" theme="primary" text @click="batchDetail(record.scope)">详情</bk-button>
                </template>
            </common-table>
        </div>
        <!--  批量修改抽屉栏   -->
        <batch-modify :form-data="formData"
            :is-show-footer="false"
            v-model="batchModifyVisible"
            :form-widgets="batchWidgets"
            title="操作记录详情">
        </batch-modify>
    </div>
</template>

<script>
    import commonTable from '@/components/table/comTable'
    import batchModify from '@/components/modify'

    export default {
        name: 'operation-record-manage',
        components: {
            commonTable,
            batchModify
        },
        data() {
            return {
                dateRange: '',
                startTime: '',
                endTime: '',
                searchParams: {},
                operationType: [
                    {id: 'add', name: '新增'},
                    {id: 'modify', name: '修改'},
                    {id: 'exec', name: '执行'},
                    {id: 'delete', name: '删除'}
                ],
                operateTypeObj: {
                    'add': '新增',
                    'modify': '修改',
                    'exec': '执行',
                    'delete': '删除'
                },
                customDialog: {
                    visible: false,
                    title: '添加自定义属性'
                },
                dataList: [],
                columns: [
                    {
                        label: '操作人',
                        key: 'operator',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '操作对象',
                        key: 'operate_obj',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '操作类型',
                        key: 'operate_type',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        },
                        scopedSlots: {customRender: 'operate_type'}
                    },
                    {
                        label: '操作时间',
                        key: 'operate_date',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '操作概要',
                        key: 'operate_detail',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '操作',
                        key: 'operation',
                        width: '100px',
                        scopedSlots: {customRender: 'operation'}
                    }
                ],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                // 查询详情数据
                formData: {
                    operator: '',
                    operate_obj: '',
                    operate_type: '',
                    operate_date: '',
                    operate_detail: ''
                },
                // 批量修改的表单配置数据
                batchWidgets: [
                    {
                        widget: 'input',
                        name: 'operator',
                        label: '操作人',
                        required: false,
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'operate_obj',
                        label: '操作对象',
                        required: false,
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'operate_type',
                        label: '操作类型',
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'operate_date',
                        label: '操作时间',
                        required: false,
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'operate_detail',
                        label: '操作概要',
                        required: false,
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'operate_result',
                        label: '操作结果',
                        required: false,
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    }
                ],
                batchModifyVisible: false,
                loading: false
            }
        },
        watch: {
            dateRange: {
                handler(newV) {
                    this.startTime = newV[0] ? this.$moment(newV[0]).format('YYYY-MM-DD') : ''
                    this.endTime = newV[1] ? this.$moment(newV[1]).format('YYYY-MM-DD') : ''
                }
            }
        },
        mounted() {
            this.fetchData()
        },
        methods: {
            handlePageChange(page) {
                this.pagination.current = page
                const params = {
                    operator: this.searchParams.operator || '',
                    operate_type: this.searchParams.operate_type || '',
                    end_time: this.endTime,
                    start_time: this.startTime,
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }
                this.fetchData(params)
            },
            limitChange(limit) {
                this.pagination.limit = limit
                this.pagination.current = 1
                this.fetchData()
            },
            // 查询记录
            async fetchData(params = {}) {
                this.loading = true
                // page:页数, page_size:每页数
                try {
                    const res = await this.$api.searchOperationRecord({
                        page: this.pagination.current,
                        page_size: this.pagination.limit,
                        ...params
                    })
                    if (res.result) {
                        this.pagination.count = res.data.count
                        this.dataList = res.data.results
                    } else {
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading = false
                }
            },
            onSearch(type) {
                if (type === 'clearn') {
                    this.searchParams.operator = ''
                    this.searchParams.operate_type = ''
                    this.dateRange = ''
                    this.endTime = ''
                    this.startTime = ''
                }
                this.pagination.current = 1
                const params = {
                    operator: this.searchParams.operator || '',
                    operate_type: this.searchParams.operate_type || '',
                    end_time: this.endTime,
                    start_time: this.startTime,
                    page: this.pagination.current,
                    page_size: this.pagination.limit
                }
                this.fetchData(params)
            },
            // 查询详情
            async batchDetail(scope) {
                this.batchModifyVisible = true
                this.formData = scope
                this.formData.operate_result = scope.result ? '成功' : '失败'
            }
        }
    }
</script>
