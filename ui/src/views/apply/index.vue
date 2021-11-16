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
    <div class="apply-manage-wrapper table—wrapper">
        <div class="header-table-operation">
            <bk-search-select
                clearable
                style="width: 420px;"
                :data="searchValueData"
                placeholder="请输入搜索项名搜索"
                :show-condition="false"
                @search="onSearch"
                @clear="onSearch"
                v-model="searchValue">
            </bk-search-select>
        </div>
        <div v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <common-table
                :data="copyData"
                :columns="finishColumns"
                :select-column="{ visible: false, fixed: true }"
                :order-column="{ visible: false, fixed: false }"
                :pagination="pagination"
                @page-change="handlePageChange"
                @page-limit-change="limitChange">
                <template slot="apply_type" slot-scope="record">
                    <span>{{ applyType[record.scope.apply_type] || '--' }}</span>
                </template>
                <template slot="apply_way" slot-scope="record">
                    <span>{{ applyWay[record.scope.apply_way] || '--'}}</span>
                </template>
                <template slot="apply_status" slot-scope="record">
                    <span>{{ applyStatus[record.scope.apply_status] || '--' }}</span>
                </template>
            </common-table>
        </div>
        <approve-dialog ref="approveDialog"></approve-dialog>
    </div>
</template>

<script>
    import commonTable from '@/components/table/comTable'
    export default {
        name: 'apply-manage',
        components: {
            commonTable
        },
        data() {
            return {
                applyWay: {
                    API: 'API申请',
                    MANUAL: '网页申请',
                    ADMIN: '管理员直接分配'
                },
                applyStatus: {
                    auditing: '待审核',
                    reject: '已拒绝',
                    approval: '已通过',
                    submiting: '待提交'
                },
                applyType: {
                    new: 'IP申请',
                    renew: '续约申请'
                },
                searchValueData: [
                    {
                        name: '申请人',
                        id: 'apply_person',
                        placeholder: '请输入申请人'
                    },
                    {
                        name: '业务系统',
                        id: 'business_system',
                        placeholder: '请输入业务系统'
                    },
                    {
                        name: 'IP',
                        id: 'ip',
                        placeholder: '请输入IP',
                        validate(values, item) {
                            const validate = (values || []).reduce((ret, cur) => {
                                ret = ret && /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/.test(cur.name)
                                return ret
                            }, true)
                            return !validate ? '格式错误: 请输入正确的IP格式' : true
                        }
                    }
                ],
                searchValue: [],
                loading: false,
                panels: [
                    { name: '未完申请', count: 0 },
                    { name: '已完申请', count: 2 }
                ],
                active: '未完申请',
                copyData: [],
                columns: [
                    {
                        label: '申请类型',
                        key: 'apply_type'
                    },
                    {
                        label: '申请单号',
                        key: 'apply_number',
                        attr: {
                            minWidth: '125px'
                        }
                    },
                    {
                        label: '业务系统',
                        key: 'business_system'
                    },
                    {
                        label: 'ip地址',
                        key: 'ips',
                        attr: {
                            minWidth: '125px'
                        }
                    },
                    {
                        label: '云区域',
                        key: 'bk_cloud_id',
                        align: 'right'
                    },
                    {
                        label: '过期时间',
                        key: 'expired_time',
                        attr: {
                            minWidth: '150px'
                        }
                    },
                    {
                        label: '申请人',
                        key: 'create_by'
                    },
                    {
                        label: '申请理由',
                        key: 'apply_reason',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '操作',
                        key: 'operation',
                        width: '100px',
                        scopedSlots: { customRender: 'operation' }
                    }
                ],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                finishColumns: [
                    {
                        label: '申请类型',
                        key: 'apply_type',
                        scopedSlots: { customRender: 'apply_type' }
                    },
                    {
                        label: '申请方式',
                        key: 'apply_way',
                        scopedSlots: { customRender: 'apply_way' },
                        attr: {
                            minWidth: '125px'
                        }
                    },
                    {
                        label: '业务系统',
                        key: 'business_system'
                    },
                    {
                        label: 'ip地址',
                        key: 'applied_ips',
                        attr: {
                            minWidth: '125px',
                            showOverflowTooltip: true
                        }
                    },
                    {
                        label: '过期时间',
                        key: 'expired_time',
                        attr: {
                            minWidth: '150px'
                        }
                    },
                    {
                        label: '申请人',
                        key: 'apply_person'
                    },
                    {
                        label: '申请时间',
                        key: 'create_at',
                        attr: {
                            minWidth: '150px'
                        }
                    },
                    {
                        label: '状态',
                        key: 'apply_status',
                        scopedSlots: { customRender: 'apply_status' }
                    }
                ]
            }
        },
        mounted() {
            this.fetchData()
        },
        methods: {
            // 列表数据请求
            async fetchData() {
                this.loading = true
                try {
                    const res = await this.$api.search_apply_list({
                        page: this.pagination.current,
                        page_size: this.pagination.limit
                    })
                    if (res.result) {
                        this.copyData = res.data.results
                        this.pagination.count = res.data.count
                    } else {
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading = false
                }
            },
            // 查询自定义属性
            onSearch() {
                const timer = setTimeout(() => {
                    this.pagination.current = 1
                    const params = {
                        page: this.pagination.current,
                        page_size: this.pagination.limit,
                        ip: this.getDataDetail('ip'),
                        business_system: this.getDataDetail('business_system'),
                        apply_person: this.getDataDetail('apply_person')
                    }
                    this.loading = true
                    this.$api.search_apply_list(params).then(res => {
                        if (res.result) {
                            this.copyData = res.data.results
                            this.pagination.count = res.data.count
                        } else {
                            this._errorMessage(res.message)
                        }
                        this.loading = false
                    })
                    clearTimeout(timer)
                }, 0)
            },
            getDataDetail(type) {
                const current = this.searchValue.find(item => item.id === type)
                if (current && current['values']) {
                    return current['values'][0].id
                } else {
                    return ''
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
            }
        }
    }
</script>

<style scoped lang="scss">
.search-select-wrap {
    background: #fff;
}
.panel-icon,
.panel-name,
.panel-count {
    display: inline-block;
    vertical-align: middle;
    margin: 0 3px;
}
.panel-count {
    min-width: 16px;
    height: 16px;
    padding: 0 4px;
    line-height: 16px;
    border-radius: 8px;
    text-align: center;
    font-style: normal;
    font-size: 12px;
    color: #fff;
    background-color: #C4C6CC;
}
/deep/ .bk-tab-section {
    padding: 15px 0 0;
    background: #fff;
}
/deep/.table-container {
    border: none !important;
    border-top: 1px solid #dfe0e5 !important;
}
.status-agree {
    position: relative;
    width: 60px;
    height: 30px;
    line-height: 30px;
    display: block;
    &::before {
        content: "";
        position: absolute;
        width: 4px;
        height: 15px;
        background: #2DCB56;
        left: -8px;
        top: 8px;
        border-radius: 10px;
    }
}
.status-fail {
    position: relative;
    width: 60px;
    height: 30px;
    line-height: 30px;
    display: block;
    &::before {
        content: "";
        position: absolute;
        width: 4px;
        height: 15px;
        left: -8px;
        top: 8px;
        background: #EA3636;
        border-radius: 10px;
    }
}
</style>
