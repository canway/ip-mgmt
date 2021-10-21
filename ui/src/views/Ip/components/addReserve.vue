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
        :width="540"
        :is-show.sync="visible"
        :quick-close="false">
        <div slot="header">
            新增保留
        </div>
        <div
            slot="content"
            class="add-distribute-wrapper">
            <bk-form
                :label-width="145"
                :model="formData"
                :rules="rules"
                ref="reserveForm">
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
                    :property="'ip_net'">
                    <ip-net-select
                        :disabled="false" v-model="formData.ip_net"
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
                        @change="netChange"
                    ></ip-net-select>
                </bk-form-item>
                <bk-form-item
                    label="待分配IP"
                    :required="true"
                    :property="'ips'">
                    <bk-input type="textarea"
                        :rows="6"
                        v-model="formData.ips"
                        placeholder="多个不连续IP用英文逗号隔开，连续IP中间用横杠连接，如：1.1.1.1,2.2.2.2,3.3.3.3-3.3.3.10（IP必须在这个子网内，点击确定将进行检测）">
                    </bk-input>
                </bk-form-item>
                <bk-form-item
                    label="云区域"
                    :property="'vlan_id'">
                    <bk-input
                        v-model="formData.vlan_id"
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
                    label="备注"
                    :property="'reason'">
                    <bk-input type="textarea"
                        v-model="formData.reason"
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
    export default {
        name: 'add-distribute',
        components: {
            dataSelect,
            ipNetSelect
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
                    ip_net: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    ips: [
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
                    ip_net: '',
                    ips: '',
                    reason: ''
                },
                isConfirm: false,
                ipNetDefaultOption: {},
                ipPoolDefaultOption: {}
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
                    const ips = []
                    item.ipOption.forEach(item => {
                        ips.push(item.ip)
                    })
                    this.formData = {
                        apply_ip_pool: item.ip_pool_id,
                        ip_net: item.ip_net,
                        ips: ips.join(','),
                        reason: ''
                    }
                } else {
                    this.formData = {
                        apply_ip_pool: '',
                        ip_net: '',
                        ips: '',
                        reason: ''
                    }
                }
                this.netSelectChange()
                this.$nextTick(() => {
                    this.settingPosition()
                })
                this.visible = true
            },
            netSelectChange(record) {
                const _list = ['bk_cloud_id', 'gateway', 'dns', 'vlan_id']
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
            netChange() {
                this.$set(this.formData, 'ips', '')
            },
            submitData() {
                this.isConfirm = true
                this.$refs.reserveForm.validate().then(validator => {
                    const formData = JSON.parse(JSON.stringify(this.formData))
                    // 检测IP是否在子网下
                    this.$api.ip_check({
                        ip_net: formData['ip_net'],
                        ips: formData['ips'].split(',')
                    }).then(res => {
                        if (res.result) {
                            this._successMessage('保留成功')
                            // 新增保留
                            this.$api.ip_reserve({
                                ip_net: formData['ip_net'],
                                remark: formData['reason'],
                                ips: formData['ips'].split(','),
                                is_reserve: true
                            }).then(resContext => {
                                if (resContext.result) {
                                    this.$emit('ok-confirm', true)
                                    this.visible = false
                                }
                            })
                        } else {
                            this._errorMessage(res.message)
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
