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
    <bk-sideslider
        :is-show.sync="visible"
        :width="540"
        :quick-close="false">
        <div slot="header">
            新增分配
        </div>
        <div
            slot="content"
            class="add-distribute-wrapper">
            <bk-form
                :label-width="145"
                :model="formData"
                :rules="rules"
                ref="distributeForm">
                <bk-form-item
                    label="地址池"
                    :required="true"
                    :property="'apply_ip_pool'">
                    <data-select
                        :disabled="false" v-model="formData.apply_ip_pool"
                        :placeholder="'请选择地址池'"
                        :attr="{
                            remote: true,
                            filterable: true,
                            searchable: true,
                            popperAppendToBody: false,
                            clearable: true,
                            url: 'searchPool',
                            detailUrl: 'poolDetail',
                            defaultOption: ipPoolDefaultOption
                        }"
                    ></data-select>
                </bk-form-item>
                <bk-form-item
                    label="子网"
                    :required="true"
                    :property="'apply_ip_net'">
                    <ip-net-select
                        :disabled="false" v-model="formData.apply_ip_net"
                        :placeholder="'请选择子网'"
                        :form-data="formData"
                        :attr="{
                            nameKey: 'apply_ip_pool',
                            remote: true,
                            filterable: true,
                            searchable: true,
                            popperAppendToBody: false,
                            clearable: true,
                            url: 'search_ip_net',
                            detailUrl: 'poolNetDetail',
                            defaultOption: ipNetDefaultOption
                        }"
                        @row-change="netSelectChange"
                    ></ip-net-select>
                </bk-form-item>
                <bk-form-item
                    label="待分配IP"
                    :required="true"
                    :property="'apply_ips'">
                    <ip-select
                        :disabled="false" v-model="formData.apply_ips"
                        :placeholder="'请选择IP'"
                        :form-data="formData"
                        :attr="{
                            nameKey: 'apply_ip_net',
                            remote: true,
                            multiple: true,
                            filterable: true,
                            searchable: true,
                            popperAppendToBody: false,
                            clearable: true,
                            allocateStatus: 1,
                            url: 'search_distribute_ip',
                            defaultOption: ipDefaultOption
                        }"
                        @row-change="ipSelectChange"
                    ></ip-select>
                </bk-form-item>
                <bk-form-item
                    label="云区域"
                    :property="'bk_cloud_id'">
                    <bk-input
                        v-model="formData.bk_cloud_id"
                        :disabled="true"
                        placeholder="请输入云区域">
                    </bk-input>
                </bk-form-item>
                <bk-form-item
                    label="网关"
                    :property="'gateway'">
                    <bk-input
                        v-model="formData.gateway"
                        :disabled="true"
                        placeholder="请输入网关">
                    </bk-input>
                </bk-form-item>
                <bk-form-item
                    label="DNS服务器"
                    :property="'dns'">
                    <bk-input
                        v-model="formData.dns"
                        :disabled="true"
                        placeholder="请输入DNS服务器">
                    </bk-input>
                </bk-form-item>
                <bk-form-item
                    label="VLAN ID"
                    :property="'vlan_id'">
                    <bk-input
                        v-model="formData.vlan_id"
                        :disabled="true"
                        placeholder="请输入VLAN ID">
                    </bk-input>
                </bk-form-item>
                <bk-form-item
                    label="业务系统"
                    :property="'business_system'">
                    <bk-input
                        v-model="formData.business_system"
                        placeholder="请输入业务系统">
                    </bk-input>
                </bk-form-item>
                <bk-form-item
                    label="运维人员"
                    :property="'member'">
                    <bk-input
                        v-model="formData.member"
                        placeholder="请输入运维人员">
                    </bk-input>
                </bk-form-item>
                <bk-form-item
                    label="过期时间"
                    :required="true"
                    :property="'expired_time'">
                    <bk-date-picker placeholder="请选择" :timer="false"
                        v-model="formData.expired_time"
                        :disabled="false" :transfer="true"
                        style="width: 100%;">
                    </bk-date-picker>
                </bk-form-item>
                <bk-form-item
                    label="备注"
                    :required="true"
                    :property="'apply_reason'">
                    <bk-input type="textarea"
                        v-model="formData.apply_reason"
                        placeholder="请输入">
                    </bk-input>
                </bk-form-item>
            </bk-form>
        </div>
        <div slot="footer">
            <bk-button
                ext-cls="mr5"
                theme="primary"
                title="保存"
                :loading="isConfirm"
                @click.stop.prevent="submitData"
                style="margin-left: 24px;">
                确定
            </bk-button>
            <bk-button
                ext-cls="mr5"
                theme="default"
                title="取消"
                @click="visible = false">
                取消
            </bk-button>
        </div>
    </bk-sideslider>
</template>

<script>
    import dataSelect from '@/components/formWidget/dataSelect'
    import ipNetSelect from '@/components/formWidget/ipNetSelect'
    import ipSelect from '@/components/formWidget/ipSelect'
    export default {
        name: 'add-distribute',
        components: {
            dataSelect,
            ipNetSelect,
            ipSelect
        },
        data() {
            return {
                visible: false,
                rules: {
                    apply_ip_pool: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    apply_ip_net: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    apply_ips: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    expired_time: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    apply_reason: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ]
                },
                formData: {
                    apply_ip_pool: '',
                    apply_ip_net: '',
                    apply_ips: [],
                    expired_time: '',
                    apply_reason: ''
                },
                isConfirm: false,
                apply_ips: [],
                ipPoolDefaultOption: {},
                ipNetDefaultOption: {},
                ipDefaultOption: {}
            }
        },
        methods: {
            showDialog(item) {
                if (item) {
                    this.ipNetDefaultOption = {
                        id: item.ip_net,
                        ip_net: item.ip_net_name
                    }
                    this.ipPoolDefaultOption = {
                        id: item.ip_pool_id,
                        name: item.ip_pool
                    }
                    this.ipDefaultOption = item.ipOption
                    const ids = []
                    this.ipDefaultOption.forEach(item => {
                        ids.push(item.id)
                    })
                    this.apply_ips = ids
                    this.formData = {
                        apply_ip_pool: item.ip_pool_id,
                        apply_ip_net: item.ip_net,
                        apply_ips: ids,
                        expired_time: '',
                        apply_reason: ''
                    }
                } else {
                    this.formData = {
                        apply_ip_pool: '',
                        apply_ip_net: '',
                        apply_ips: [],
                        expired_time: '',
                        apply_reason: ''
                    }
                }
                this.netSelectChange()
                this.$nextTick(() => {
                    this.settingPosition()
                })
                this.visible = true
            },
            netSelectChange(record) {
                const _list = ['bk_cloud_id', 'gateway', 'dns', 'vlan_id', 'business_system', 'owner']
                if (record) {
                    _list.forEach(list => {
                        this.formData[list] = record[list]
                    })
                    return false
                }
                _list.forEach(list => {
                    this.formData[list] = ''
                })
            },
            ipSelectChange(record) {
                const _data = []
                record.forEach(item => {
                    _data.push(item.id)
                })
                this.apply_ips = [..._data]
            },
            submitData() {
                this.isConfirm = true
                this.$refs.distributeForm.validate().then(validator => {
                    const formData = JSON.parse(JSON.stringify(this.formData))
                    formData['expired_time'] = this.$moment(formData['expired_time']).format('YYYY-MM-DD hh:mm:ss')
                    this.$api.ip_apply({
                        apply_ip_pool: formData['apply_ip_pool'],
                        apply_ip_net: formData['apply_ip_net'],
                        apply_ips: this.apply_ips,
                        apply_way: 'ADMIN',
                        business_system: formData['business_system'],
                        member: formData['member'],
                        expired_time: formData['expired_time'],
                        apply_reason: formData['apply_reason']
                    }).then(res => {
                        if (res.result) {
                            this._successMessage('分配成功')
                            this.$emit('ok-confirm', true)
                            this.visible = false
                        } else {
                            this._errorMessage(res.message)
                            this.visible = false
                        }
                    }).finally(() => {
                        this.isConfirm = false
                    })
                }, validator => {
                    this.isConfirm = false
                })
            }
        }
    }
</script>

<style scoped lang="scss">
.add-distribute-wrapper {
    padding: 15px 25px 15px 0;
}
</style>
