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
                <bk-search-select clearable :data="getConditionData"
                    :show-condition="false"
                    v-model="searchParams"
                    style="width: 400px;background: #fff;margin-right: 16px;"
                    @search="onSearch"
                    @clear="onSearch"
                    :show-popover-tag-change="true">
                </bk-search-select>
                <span>开始时间：</span>
                <bk-date-picker v-model="startTime" :placeholder="'选择日期'" @change="onSearch"
                    style="width: 180px;margin-right: 16px;"></bk-date-picker>
                <span>结束时间：</span>
                <bk-date-picker v-model="endTime" :placeholder="'选择日期'" @change="onSearch"
                    style="width: 180px;margin-right: 16px;"></bk-date-picker>
            </div>
        </div>
        <div v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <common-table
                :data="dataList"
                :columns="columns"
                :order-column="{ visible: false, fixed: false }"
                :pagination="pagination"
                @page-change="handlePageChange"
                @page-limit-change="limitChange">
                <template slot="sync_status" slot-scope="record">
                    {{ statusObj[record.scope.sync_status] }}
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
            title="同步记录详情">
        </batch-modify>
    </div>
</template>

<script>
    import commonTable from '@/components/table/comTable'
    import batchModify from '@/components/modify'

    export default {
        name: 'simul-record-manage',
        components: {
            commonTable,
            batchModify
        },
        data() {
            return {
                startTime: '',
                endTime: '',
                searchParams: [],
                data: [
                    {
                        name: '模型',
                        id: 'sync_model'
                    },
                    {
                        name: '状态',
                        id: 'sync_status',
                        children: [
                            {
                                name: '同步失败',
                                id: '0'
                            },
                            {
                                name: '同步成功',
                                id: '1'
                            },
                            {
                                name: '同步中',
                                id: '2'
                            }
                        ]
                    }
                ],
                recordDialog: {
                    visible: false,
                    title: '同步记录详情'
                },
                statusObj: {
                    '0': '同步失败',
                    '1': '同步成功',
                    '2': '同步中'
                },
                // 批量修改的数据
                formData: {
                    model: '',
                    create_by: '',
                    start_time: '',
                    end_time: '',
                    status: ''
                },
                dataList: [],
                columns: [
                    {
                        label: '模型',
                        key: 'model_name',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: 'IP',
                        key: 'ip_address',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '创建者',
                        key: 'create_by',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '开始时间',
                        key: 'sync_at',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '结束时间',
                        key: 'complete_at',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '状态',
                        key: 'sync_status',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        },
                        scopedSlots: {customRender: 'sync_status'}
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
                // 批量修改的表单配置数据
                batchWidgets: [
                    {
                        widget: 'input',
                        name: 'model_name',
                        label: '模型',
                        required: false,
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'create_by',
                        label: '创建者',
                        required: false,
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'sync_at',
                        label: '开始时间',
                        placeholder: '请选择...',
                        attr: {
                            style: {width: '100%'},
                            transfer: true,
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'complete_at',
                        label: '结束时间',
                        required: false,
                        attr: {
                            clearable: true
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'old_info',
                        label: '同步前信息',
                        required: false,
                        attr: {
                            clearable: true,
                            type: 'textarea'
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'new_info',
                        label: '同步后信息',
                        required: false,
                        attr: {
                            clearable: true,
                            type: 'textarea'
                        },
                        disabled: true
                    },
                    {
                        widget: 'input',
                        name: 'sync_status_name',
                        label: '状态',
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
        computed: {
            getConditionData() {
                const _data = JSON.parse(JSON.stringify(this.data))
                const _result = []
                _data.forEach(item => {
                    const _current = this.searchParams.find(ele => ele.id === item.id)
                    if (!_current) {
                        _result.push({...item})
                    }
                })
                return _result
            }
        },
        mounted() {
            this.fetchData()
        },
        methods: {
            handlePageChange(page) {
                this.pagination.current = page
                this.fetchData()
            },
            limitChange(limit) {
                this.pagination.limit = limit
                this.fetchData()
            },
            // 查询同步记录
            async fetchData(params = {}) {
                this.loading = true
                // page:页数, page_size:每页数
                try {
                    const res = await this.$api.searchSyncRecord({
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
            onSearch() {
                const timer = setTimeout(() => {
                    const params = {
                        model: this.getDataDetail('sync_model'),
                        sync_status: this.getDataDetail('sync_status'),
                        end_time: this.endTime !== '' ? this.$moment(this.endTime).format('YYYY-MM-DD') : this.endTime,
                        start_time: this.startTime !== '' ? this.$moment(this.startTime).format('YYYY-MM-DD') : this.startTime,
                        page: this.pagination.current,
                        page_size: this.pagination.limit
                    }
                    this.fetchData(params)
                    clearTimeout(timer)
                }, 0)
            },
            getDataDetail(type) {
                const current = this.searchParams.find(item => item.id === type)
                if (current && current['values']) {
                    return current['values'][0].id
                } else {
                    return ''
                }
            },
            // 查看详情
            async batchDetail(scope) {
                this.formData = this.$Copy(scope)
                this.formData.old_info = JSON.stringify(this.formData.old_info)
                this.formData.new_info = JSON.stringify(this.formData.new_info)
                this.formData.sync_status_name = this.statusObj[scope.sync_status]
                this.batchModifyVisible = true
            }
        }
    }
</script>
