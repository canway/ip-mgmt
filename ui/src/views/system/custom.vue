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
                    style="width: 500px;background: #fff;"
                    @search="filterSearch"
                    @clear="filterSearch"
                    :show-popover-tag-change="true">
                </bk-search-select>
            </div>
            <div class="operation-container">
                <bk-button :title="'添加自定义属性'" @click="customDialog.visible = true, customDialog.title = '添加自定义属性'">添加自定义属性</bk-button>
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
                <template slot="type" slot-scope="record">
                    {{ typeObj[record.scope.type] }}
                </template>
                <template slot="required" slot-scope="record">
                    {{ requiredObj[record.scope.required] }}
                </template>
                <template slot="operation" slot-scope="record">
                    <bk-button class="mr10" theme="primary" text @click="toModify(record.scope)">修改</bk-button>
                    <bk-popconfirm
                        trigger="click"
                        title="确认删除该自定义属性吗？"
                        content="删除操作无法撤回，请谨慎操作！"
                        @confirm="toDelete(record.scope)">
                        <bk-button class="mr10" theme="primary" text>删除</bk-button>
                    </bk-popconfirm>
                </template>
            </common-table>
        </div>
        <bk-dialog v-model="customDialog.visible"
            theme="primary"
            :mask-close="false"
            :header-position="'left'"
            :title="customDialog.title"
            :auto-close="false">
            <bk-form :label-width="80" :model="formData" :rules="rules" ref="validateForm">
                <bk-form-item label="类型" :required="true" :property="'type'" :error-display-type="'normal'">
                    <bk-select :disabled="false" v-model="formData.type" style="width: 270px;"
                        ext-cls="select-custom"
                        ext-popover-cls="select-popover-custom">
                        <bk-option v-for="option in typeList"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="字段名称" :required="true" :property="'name'" :error-display-type="'normal'">
                    <bk-input v-model="formData.name" placeholder="请输入字段名称"></bk-input>
                </bk-form-item>
                <bk-form-item label="显示名称" :required="true" :property="'display_name'" :error-display-type="'normal'">
                    <bk-input v-model="formData.display_name" placeholder="请输入显示名称"></bk-input>
                </bk-form-item>
                <bk-form-item label="必填项" :required="true" :property="'required'" :error-display-type="'normal'">
                    <bk-radio-group v-model="formData.required">
                        <bk-radio :value="'是'">是</bk-radio>
                        <bk-radio :value="'否'">否</bk-radio>
                    </bk-radio-group>
                </bk-form-item>
                <bk-form-item label="备注" :property="'description'">
                    <bk-input v-model="formData.description" placeholder="请输入备注"></bk-input>
                </bk-form-item>
            </bk-form>
            <div slot="footer">
                <bk-button theme="primary" title="确定"
                    :loading="isConfirm" @click.stop.prevent="handleSubmit">确定</bk-button>
                <bk-button theme="default" title="取消" @click="customDialog.visible = false">取消</bk-button>
            </div>
        </bk-dialog>
    </div>
</template>

<script>
    import commonTable from '@/components/table/comTable'
    export default {
        name: 'custom-manage',
        components: {
            commonTable
        },
        data() {
            return {
                loading: false,
                searchParams: [],
                typeObj: {
                    'ip_pool': 'IP地址池自定义属性',
                    'tetwork_segment': '子网自定义属性',
                    'ips': 'ip自定义属性'
                },
                requiredObj: {
                    true: '是',
                    false: '否'
                },
                data: [
                    {
                        name: '类型',
                        id: 'type',
                        children: [
                            {
                                name: 'IP地址池自定义属性',
                                id: 'ip_pool'
                            },
                            {
                                name: '子网自定义属性',
                                id: 'tetwork_segment'
                            },
                            {
                                name: 'ip自定义属性',
                                id: 'ips'
                            }
                        ]
                    },
                    {
                        name: '字段名称',
                        id: 'name'
                    },
                    {
                        name: '显示名称',
                        id: 'display_name'
                    },
                    {

                        name: '必填项',
                        id: 'required',
                        children: [
                            {
                                name: '是',
                                id: 'true'
                            },
                            {
                                name: '否',
                                id: 'false'
                            }
                        ]
                    },
                    {
                        name: '备注',
                        id: 'description'
                    }
                ],
                customDialog: {
                    visible: false,
                    title: '添加自定义属性'
                },
                formData: {
                    type: '',
                    name: '',
                    display_name: '',
                    required: '是',
                    description: ''
                },
                dataList: [],
                typeList: [
                    {
                        id: 'ip_pool',
                        name: 'IP地址池自定义属性'
                    },
                    {
                        id: 'tetwork_segment',
                        name: '子网自定义属性'
                    },
                    {
                        id: 'ips',
                        name: 'ip自定义属性'
                    }
                ],
                columns: [
                    {
                        label: '类型',
                        key: 'type',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        },
                        scopedSlots: { customRender: 'type' }
                    },
                    {
                        label: '字段名称',
                        key: 'name',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '显示名称',
                        key: 'display_name',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '必填项',
                        key: 'required',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        },
                        scopedSlots: { customRender: 'required' }
                    },
                    {
                        label: '添加者',
                        key: 'create_by',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '添加时间',
                        key: 'create_at',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '备注',
                        key: 'description',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '操作',
                        key: 'operation',
                        scopedSlots: { customRender: 'operation' }
                    }
                ],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                rules: {
                    type: [
                        {
                            required: true,
                            message: '请选择类型',
                            trigger: 'change'
                        }
                    ],
                    name: [
                        {
                            required: true,
                            message: '请输入字段名称',
                            trigger: 'blur'
                        }
                    ],
                    display_name: [
                        {
                            required: true,
                            message: '请输入显示名称',
                            trigger: 'blur'
                        }
                    ]
                },
                isConfirm: false
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
        watch: {
            'customDialog.visible'() {
                if (!this.customDialog.visible) {
                    for (const i in this.formData) {
                        if (i === 'required') {
                            this.formData[i] = '是'
                        } else {
                            this.formData[i] = ''
                        }
                    }
                    this.customDialog.title = '添加自定义属性'
                }
            }
        },
        created() {
            this.onSearch()
        },
        methods: {
            handlePageChange(page) {
                this.pagination.current = page
                this.onSearch()
            },
            limitChange(limit) {
                this.pagination.limit = limit
                this.pagination.current = 1
                this.onSearch()
            },
            filterSearch() {
                this.pagination.current = 1
                this.onSearch()
            },
            // 查询自定义属性
            onSearch() {
                const timer = setTimeout(() => {
                    const params = {
                        page: this.pagination.current,
                        page_size: this.pagination.limit,
                        type: this.getDataDetail('type'),
                        name: this.getDataDetail('name'),
                        display_name: this.getDataDetail('display_name'),
                        required: this.getDataDetail('required'),
                        description: this.getDataDetail('description')
                    }
                    this.loading = true
                    this.$api.searchCustom(params).then(res => {
                        if (res.result) {
                            this.dataList = res.data.results
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
                const current = this.searchParams.find(item => item.id === type)
                if (current && current['values']) {
                    return current['values'][0].id
                } else {
                    return ''
                }
            },
            toModify(row) {
                this.customDialog.visible = true
                this.customDialog.title = '编辑自定义属性'
                this.formData = {...row}
                if (this.formData.required) {
                    this.formData.required = '是'
                } else {
                    this.formData.required = '否'
                }
            },
            toDelete(row) {
                const params = {
                    id: row.id
                }
                this.$api.deleteCustom(params).then(res => {
                    if (res.result) {
                        this.$bkMessage({
                            theme: 'success',
                            message: '删除成功'
                        })
                        if (this.pagination.current > 1 && this.dataList.length === 1) {
                            this.pagination.current--
                        }
                        this.onSearch()
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: '删除失败'
                        })
                    }
                })
            },
            handleSubmit() {
                this.$refs.validateForm.validate().then((valid) => {
                    if (valid) {
                        const params = {...this.formData}
                        if (params.required === '是') {
                            params.required = true
                        } else {
                            params.required = false
                        }
                        this.isConfirm = true
                        if (this.customDialog.title === '添加自定义属性') {
                            this.$api.addCustom(params).then(res => {
                                if (res.result) {
                                    this._successMessage('添加成功')
                                    this.onSearch()
                                    this.customDialog.visible = false
                                } else {
                                    this._errorMessage(res.message)
                                }
                                this.isConfirm = false
                            })
                        } else {
                            this.$api.editCustom(params).then(res => {
                                if (res.result) {
                                    this.$bkMessage({
                                        theme: 'success',
                                        message: '修改成功'
                                    })
                                    this.onSearch()
                                    this.customDialog.visible = false
                                } else {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: '修改失败'
                                    })
                                }
                            }).finally(() => {
                                this.isConfirm = false
                            })
                        }
                    }
                }, validator => {
                    this.isConfirm = false
                })
            }
        }
    }
</script>

<style scoped lang="scss">
    .bk-form-radio {
        margin-right: 16px;
    }
</style>
