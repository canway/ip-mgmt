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
    <bk-dialog v-model="visible"
        theme="primary"
        class="modifyDialog"
        :mask-close="false"
        :header-position="'left'"
        title="新增IP">
        <bk-form
            :label-width="80"
            :model="formData"
            :rules="rules"
            ref="offlineForm">
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
                        detailUrl: 'poolDetail'
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
                        detailUrl: 'poolNetDetail'
                    }"
                    @row-change="netSelectChange"
                ></ip-net-select>
            </bk-form-item>
            <bk-form-item
                label="IP"
                :required="true"
                :property="'ip_list'">
                <bk-input type="textarea"
                    :rows="6"
                    v-model="formData.ip_list"
                    placeholder="多个不连续IP用英文逗号隔开，连续IP中间用横杠连接，如：1.1.1.1,2.2.2.2,3.3.3.3-3.3.3.10（IP必须在这个子网内，点击确定将进行检测）">
                </bk-input>
            </bk-form-item>
        </bk-form>
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
    </bk-dialog>
</template>

<script>
    import dataSelect from '@/components/formWidget/dataSelect'
    import ipNetSelect from '@/components/formWidget/ipNetSelect'
    export default {
        name: 'add-offline-white',
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
                            message: '必选项',
                            trigger: 'blur'
                        }
                    ],
                    ip_net: [
                        {
                            required: true,
                            message: '必选项',
                            trigger: 'blur'
                        }
                    ],
                    ip_list: [
                        {
                            required: true,
                            message: '必选项',
                            trigger: 'blur'
                        }
                    ]
                },
                formData: {},
                addressPool: {
                    widget: 'data-select',
                    placeholder: '请选择地址池',
                    attr: {
                        remote: true,
                        filterable: true,
                        searchable: true,
                        popperAppendToBody: false,
                        clearable: true,
                        url: 'searchPool',
                        detailUrl: 'poolDetail'
                    }
                },
                isConfirm: false
            }
        },
        methods: {
            showDialog() {
                this.visible = true
                this.formData = {
                    ip_pool: '',
                    ip_net: '',
                    ip_list: ''
                }
                this.$nextTick(() => {
                    setTimeout(() => {
                        const bodyHeight = document.body.clientHeight
                        const contentHeight = document.getElementsByClassName('bk-dialog-content')[0].offsetHeight
                        if (contentHeight === 0) return false
                        const dialog = document.getElementsByClassName('bk-dialog')[0]
                        if (contentHeight < bodyHeight) {
                            const TOP = parseInt((bodyHeight - contentHeight) / 2)
                            dialog.style.top = TOP + 'px'
                        } else {
                            dialog.style.top = 50 + 'px'
                        }
                    }, 50)
                })
            },
            submitData() {
                this.isConfirm = true
                this.$refs.offlineForm.validate().then(validator => {
                    const _formData = JSON.parse(JSON.stringify(this.formData))
                    // 检测IP是否在子网下
                    this.$api.ip_check({
                        ip_net: _formData['ip_net'],
                        ip_list: _formData['ip_list'].split(',')
                    }).then(res => {
                        if (res.result) {
                            this.$api.add_offlineWhite({
                                ip_net: _formData['ip_net'],
                                ip_list: _formData['ip_list'].split(',')
                            }).then(res => {
                                if (res.result) {
                                    this.$bkMessage({
                                        theme: 'success',
                                        message: res.message
                                    })
                                    this.$emit('submit')
                                    this.visible = false
                                } else {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: res.message
                                    })
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
            }
        }
    }
</script>

<style scoped lang="scss">
/deep/ .bk-sideslider-footer {
    position: absolute;
    bottom: 0;
    left: 0;
}
.add-distribute-wrapper {
    padding: 15px 25px 15px 0;
}
</style>
