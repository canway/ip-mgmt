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
            <search-input
                v-model="searchValue"
                :placeholder="'请输入模型名称'"
                @search="onSearch">
            </search-input>
            <div class="operation-container">
                <div>
                    <bk-button :title="'同步周期'" @click="setPeriod">
                        同步周期
                    </bk-button>
                    <bk-button :title="'新增模型'" @click="addModel">
                        新增模型
                    </bk-button>
                </div>
            </div>
        </div>
        <div v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <common-table
                :data="dataList"
                :columns="columns"
                :select-column="{ visible: false, fixed: false }"
                :order-column="{ visible: false, fixed: false }"
                :pagination="pagination"
                @page-change="handlePageChange"
                @page-limit-change="limitChange"
            >
                <template slot="sync" slot-scope="record">
                    {{ syncObject[record.scope.sync] }}
                </template>
                <template slot="operation" slot-scope="record">
                    <bk-button class="mr10" theme="primary" text @click="toSync(record.scope)">同步</bk-button>
                    <bk-button class="mr10" theme="primary" text @click="toMap(record.scope)">属性映射</bk-button>
                    <bk-popconfirm
                        trigger="click"
                        title="确认删除该名单？"
                        content="删除操作无法撤回，请谨慎操作！"
                        @confirm="toDelete(record.scope)">
                        <bk-button class="mr10" theme="primary" text>剔除</bk-button>
                    </bk-popconfirm>
                </template>
            </common-table>
        </div>
        <bk-dialog v-model="periodSettingVisible"
            theme="primary"
            :mask-close="false"
            :header-position="'left'"
            title="同步周期设置">
            <bk-form :label-width="80" :model="editPeriod" :rules="syncRules" ref="validateForm">
                <bk-form-item label="同步时间" :required="true" :property="'last_time'" :error-display-type="'normal'">
                    <bk-date-picker v-model="editPeriod.last_time" :placeholder="'选择日期时间'" :type="'datetime'"></bk-date-picker>
                </bk-form-item>
                <bk-form-item style="float: left; width: 180px;" label="同步周期" :required="true" :property="'period'" :error-display-type="'normal'">
                    <bk-input v-model="editPeriod.period"></bk-input>
                </bk-form-item>
                <bk-form-item style="float: left; width: 150px;" class="sync-period" label="" :property="'value'">
                    <div style="float: left;">
                        <bk-select :clearable="false" :disabled="false" v-model="editPeriod.value" style="width: 150px;margin-left: 10px;"
                            ext-cls="select-custom"
                            ext-popover-cls="select-popover-custom">
                            <bk-option v-for="option in periodList"
                                :key="option.id"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                </bk-form-item>
            </bk-form>
            <div slot="footer">
                <bk-button theme="primary" title="确定"
                    :loading="isConfirm" @click.stop.prevent="periodSubmit">确定</bk-button>
                <bk-button theme="default" title="取消" @click="periodSettingVisible = false">
                    取消
                </bk-button>
            </div>
        </bk-dialog>
        <bk-dialog v-model="modelVisible"
            theme="primary"
            :mask-close="false"
            :header-position="'left'"
            title="新增模型">
            <bk-form :label-width="130" :model="modelFormData" :rules="rules" ref="CMDBForm">
                <bk-form-item
                    label="选择模型"
                    :required="true"
                    :property="'model_id'"
                    :error-display-type="'normal'">
                    <bk-select :disabled="false" ref="modeSelect" v-model="modelFormData.model_id" style="width: 222px;"
                        ext-cls="select-custom"
                        ext-popover-cls="select-popover-custom"
                        @change="changeClick"
                        searchable>
                        <bk-option v-for="option in CMDBList"
                            :key="option.model_id"
                            :id="option.model_id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="指定IP字段" :required="true" :property="'ip'" :error-display-type="'normal'">
                    <bk-select :disabled="false" v-model="modelFormData.ip" style="width: 222px;"
                        ext-cls="select-custom"
                        ext-popover-cls="select-popover-custom"
                    >
                        <bk-option v-for="option in ipList"
                            :key="option.bk_property_id"
                            :id="option.bk_property_id"
                            :name="option.bk_property_name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="指定云区域字段" :property="'bk_cloud_id'">
                    <bk-select :disabled="false" v-model="modelFormData.bk_cloud_id" style="width: 222px;"
                        ext-cls="select-custom"
                        ext-popover-cls="select-popover-custom"
                    >
                        <bk-option v-for="option in cloudList"
                            :key="option.bk_property_id"
                            :id="option.bk_property_id"
                            :name="option.bk_property_name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="同步优先级" :required="true" :property="'priority'" :error-display-type="'normal'">
                    <bk-input v-model="modelFormData.priority" placeholder="仅支持数字，且优先级唯一"></bk-input>
                </bk-form-item>
                <bk-form-item label="启动同步" :required="true" :property="'sync'" :error-display-type="'normal'">
                    <bk-switcher v-model="modelFormData.sync"></bk-switcher>
                </bk-form-item>
            </bk-form>
            <div slot="footer">
                <bk-button theme="primary" title="确定"
                    :loading="isConfirm" @click.stop.prevent="modelSubmit">确定</bk-button>
                <bk-button theme="default" title="取消" @click="modelVisible = false">
                    取消
                </bk-button>
            </div>
        </bk-dialog>
        <bk-dialog v-model="mapVisible"
            theme="primary"
            :mask-close="false"
            :header-position="'left'"
            title="属性映射">
            <table style="text-align: center;">
                <tr>
                    <td></td>
                    <td width="100px">IPAM属性</td>
                    <td></td>
                    <td>CMDB属性</td>
                    <td>同步冲突检测</td>
                </tr>
                <tr v-for="(item, index) in mapList" :key="index">
                    <td style="text-align: right;">
                        <bk-icon type="minus-circle" @click="reduceMap(index)" v-if="index !== 0" />
                        <bk-icon type="plus-circle" @click="addMap(index)" />
                    </td>
                    <td>
                        <bk-select :disabled="false" v-model="item.ipam_attr" style="width: 100px;"
                            ext-cls="select-custom"
                            ext-popover-cls="select-popover-custom"
                            searchable>
                            <bk-option v-for="option in IPAMList"
                                :key="option.bk_property_id"
                                :id="option.bk_property_id"
                                :name="option.bk_property_id">
                            </bk-option>
                        </bk-select>
                    </td>
                    <td><bk-icon type="arrows-left" /></td>
                    <td>
                        <bk-select :disabled="false" v-model="item.cmdb_attr" style="width: 100px;"
                            ext-cls="select-custom"
                            ext-popover-cls="select-popover-custom"
                            searchable
                            @change="(newVaule) => CMDBClick(newVaule, item)">
                            <bk-option v-for="option in attrList"
                                :key="option.bk_property_id"
                                :id="option.bk_property_id"
                                :name="option.bk_property_name">
                            </bk-option>
                        </bk-select>
                    </td>
                    <td>
                        <bk-checkbox
                            v-model="item.check_conflict">
                        </bk-checkbox>
                    </td>
                </tr>
            </table>
            <div slot="footer">
                <bk-button theme="primary" title="保存"
                    :loading="isConfirm" @click.stop.prevent="mapSubmit">保存</bk-button>
                <bk-button theme="default" title="取消" @click="mapVisible = false">
                    取消
                </bk-button>
            </div>
        </bk-dialog>
    </div>
</template>

<script>
    import commonTable from '@/components/table/comTable'
    import searchInput from '@/components/searchInput'
    export default {
        name: 'c-m-d-b-manage',
        components: {
            commonTable,
            searchInput
        },
        data() {
            return {
                userDialog: {
                    visible: false,
                    title: '新增用户'
                },
                periodSettingVisible: false,
                modelVisible: false,
                periodFormData: {},
                editPeriod: {
                    last_time: '',
                    value: 'd',
                    period: ''
                },
                modelFormData: {
                    model_id: '',
                    priority: '',
                    sync: true,
                    ip: '',
                    bk_cloud_id: '',
                    attribute_map: [
                        {
                            ipam_attr: 'ip',
                            cmdb_attr: '',
                            is_cmdb_enum: false,
                            check_conflict: true
                        },
                        {
                            ipam_attr: 'bk_cloud_id',
                            cmdb_attr: '',
                            is_cmdb_enum: false,
                            check_conflict: true
                        }
                    ]
                },
                searchValue: '',
                periodList: [
                    {
                        id: 'd',
                        name: '天'
                    },
                    {
                        id: 'h',
                        name: '小时'
                    }
                ],
                cloudList: [],
                ipList: [],
                dataList: [],
                syncObject: {
                    true: '是',
                    false: '否'
                },
                CMDBList: [],
                attrList: [],
                columns: [
                    {
                        label: '模型名称',
                        key: 'name',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '模型ID',
                        key: 'model_id',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '同步优先级',
                        key: 'priority',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '云区域字段',
                        key: 'bk_cloud_id',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: 'IP字段',
                        key: 'ip',
                        align: 'left',
                        attr: {
                            minWidth: '100px'
                        }
                    },
                    {
                        label: '启动同步',
                        key: 'sync',
                        align: 'left',
                        attr: {
                            minWidth: '60px'
                        },
                        scopedSlots: { customRender: 'sync' }
                    },
                    {
                        label: '操作',
                        key: 'operation',
                        attr: {
                            minWidth: '170px'
                        },
                        scopedSlots: { customRender: 'operation' }
                    }
                ],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                IPAMList: [],
                rules: {
                    model_id: [
                        {
                            required: true,
                            message: '请选择模型',
                            trigger: 'change'
                        }
                    ],
                    ip: [
                        {
                            required: true,
                            message: '请选择指定IP字段',
                            trigger: 'change'
                        }
                    ],
                    priority: [
                        {
                            required: true,
                            message: '请输入同步优先级',
                            trigger: 'blur'
                        }
                    ]
                },
                syncRules: {
                    last_time: [
                        {
                            required: true,
                            message: '请选择同步时间',
                            trigger: 'change'
                        }
                    ],
                    period: [
                        {
                            required: true,
                            message: '请选择同步周期',
                            trigger: 'blur'
                        }
                    ]
                },
                loading: false,
                isConfirm: false,
                mapVisible: false,
                mapList: [],
                defaultList: [
                    {
                        ipam_attr: 'ip',
                        cmdb_attr: 'bk_host_innerip',
                        is_cmdb_enum: false,
                        check_conflict: true
                    },
                    {
                        ipam_attr: 'bk_cloud_id',
                        cmdb_attr: 'bk_cloud_id',
                        is_cmdb_enum: false,
                        check_conflict: true
                    },
                    {
                        ipam_attr: 'dns',
                        cmdb_attr: 'dns_serv',
                        is_cmdb_enum: false,
                        check_conflict: false
                    }
                ],
                mapId: null
            }
        },
        watch: {
            'periodSettingVisible'() {
                if (!this.periodSettingVisible) {
                    this.periodFormData = {}
                }
            },
            'modelVisible'() {
                if (!this.modelVisible) {
                    this.modelFormData = {
                        model_id: '',
                        priority: '',
                        sync: true,
                        ip: '',
                        bk_cloud_id: '',
                        attribute_map: [
                            {
                                ipam_attr: 'ip',
                                cmdb_attr: '',
                                is_cmdb_enum: false,
                                check_conflict: true
                            },
                            {
                                ipam_attr: 'bk_cloud_id',
                                cmdb_attr: '',
                                is_cmdb_enum: false,
                                check_conflict: true
                            }
                        ]
                    }
                }
            },
            'mapVisible'() {
                if (!this.mapVisible) {
                    this.mapList = []
                }
            },
            searchValue(newV) {
                if (!newV) {
                    this.onSearch()
                }
            }
        },
        created() {
            this.fetchData()
        },
        methods: {
            handlePageChange(page) {
                this.pagination.current = page
                this.fetchData()
            },
            limitChange(limit) {
                this.pagination.limit = limit
                this.pagination.current = 1
                this.fetchData()
            },
            // 查询模型
            async fetchData(params = {}) {
                this.loading = true
                try {
                    const res = await this.$api.searchCMDB({
                        page: this.pagination.current,
                        size: this.pagination.limit,
                        ...params
                    })
                    if (res.result) {
                        this.dataList = res.data.results
                        this.pagination.count = res.data.count
                    } else {
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading = false
                }
            },
            onSearch(value) {
                this.pagination.current = 1
                this.fetchData({
                    search: value
                })
            },
            async toDelete(row) {
                const res = await this.$api.deleteCMDB({id: row.id})
                if (res.result) {
                    this._successMessage('删除成功')
                    if (this.pagination.current > 1 && this.dataList.length === 1) {
                        this.pagination.current--
                    }
                    this.fetchData()
                } else {
                    this._errorMessage(res.message)
                }
            },
            async periodSubmit() {
                this.$refs.validateForm.validate().then((valid) => {
                    if (valid) {
                        this.isConfirm = true
                        this.periodFormData.last_time = this.editPeriod.last_time
                        this.periodFormData.period = this.editPeriod.period + this.editPeriod.value
                        this.$api.setCMDBPeriod(this.periodFormData).then(res => {
                            if (res.result) {
                                this._successMessage('设置同步周期成功')
                                this.fetchData()
                                this.periodSettingVisible = false
                            } else {
                                this._errorMessage(res.message)
                            }
                        }).finally(() => {
                            this.isConfirm = false
                        })
                    }
                }, validator => {
                    this.isConfirm = false
                })
            },
            modelSubmit() {
                this.modelFormData.attribute_map[0].cmdb_attr = this.modelFormData.ip
                this.modelFormData.attribute_map[1].cmdb_attr = this.modelFormData.bk_cloud_id
                this.modelFormData.name = this.$refs.modeSelect.selectedName
                this.isConfirm = true
                this.$refs.CMDBForm.validate().then((valid) => {
                    if (valid) {
                        this.$api.addCMDB(this.modelFormData).then(res => {
                            if (res.result) {
                                this._successMessage('新增成功')
                                this.fetchData()
                                this.modelVisible = false
                            } else {
                                this._errorMessage(res.message)
                            }
                        }).finally(() => {
                            this.isConfirm = false
                        })
                    }
                }, validator => {
                    this.isConfirm = false
                })
            },
            async toSync(row) {
                const res = await this.$api.makeSync({id: row.id})
                if (res.result) {
                    this._successMessage('手动同步成功')
                    this.fetchData()
                } else {
                    this._errorMessage(res.message)
                }
            },
            async changeClick(newValue) {
                const res = await this.$api.selectCMDBAttr({model: newValue})
                this.ipList = res.data
                this.cloudList = res.data
                this.modelFormData.ip = ''
                this.modelFormData.bk_cloud_id = ''
                this.modelFormData.priority = ''
            },
            async onSearchCMDB() {
                const res = await this.$api.selectCMDB()
                if (res.result) {
                    this.CMDBList = res.data
                }
            },
            addModel() {
                this.modelVisible = true
                this.onSearchCMDB()
            },
            reduceMap(index) {
                this.mapList.splice(index, 1)
            },
            addMap(index) {
                const item = {
                    ipam_attr: '',
                    cmdb_attr: '',
                    is_cmdb_enum: false,
                    check_conflict: false
                }
                this.mapList.splice(index + 1, 0, item)
            },
            async setPeriod() {
                this.periodSettingVisible = true
                const res = await this.$api.searchCMDBPeriod()
                if (res.result) {
                    this.periodFormData = res.data
                    this.editPeriod.last_time = this.periodFormData.last_time
                    this.editPeriod.period = parseInt(this.periodFormData.period)
                    this.editPeriod.value = this.periodFormData.period.charAt(this.periodFormData.period.length - 1)
                } else {
                    this._errorMessage(res.message)
                }
            },
            async toMap(row) {
                this.mapId = row.id
                this.mapVisible = true
                const res = await this.$api.getCMDBMap({id: row.id})
                if (res.result) {
                    this.IPAMList = res.data.IPAM
                    this.attrList = res.data.CMDB
                    if (res.data.attribute_map !== []) {
                        this.mapList = res.data.attribute_map
                    } else {
                        this.mapList = this.defaultList
                    }
                } else {
                    this._errorMessage(res.message)
                }
            },
            mapSubmit() {
                this.$api.updateCMDBMap({
                    id: this.mapId,
                    attribute_map: this.mapList
                }).then(res => {
                    if (res.result) {
                        this._successMessage('更新属性映射成功')
                        this.mapVisible = false
                        this.onSearch()
                    } else {
                        this._errorMessage(res.message)
                    }
                })
            },
            CMDBClick(newValue, item) {
                const _current = this.attrList.find(data => data.bk_property_id === newValue)
                item['is_cmdb_enum'] = _current['is_cmdb_enum']
            }
        }
    }
</script>

<style scoped lang="scss">
/deep/.sync-period {
    .bk-form-content {
        margin-left: 0 !important;
    }
}
</style>
