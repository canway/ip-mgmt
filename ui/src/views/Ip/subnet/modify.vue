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
        :is-show.sync="status"
        :width="540"
        @shown="onVisibleChange"
        @hidden="onVisibleChange"
        :quick-close="false">
        <div slot="header">
            {{ currentId ? '编辑IP子网' : '新增IP子网' }}
        </div>
        <div
            slot="content"
            class="slider-content-wrapper">
            <bk-form
                :label-width="170"
                :model="formData"
                :rules="rules"
                ref="ipModifyForm">
                <p class="title">
                    <span>地址池信息</span>
                </p>
                <bk-form-item
                    label="名称"
                    :icon-offset="30"
                    :required="true"
                    :property="'ip_pool'"
                    :rules="rules.ip_pool">
                    <component
                        :is="addressPool.widget"
                        v-model="formData.ip_pool"
                        :placeholder="addressPool.placeholder"
                        :default-value="addressPool.defaultValue"
                        :attr="addressPool.attr"
                    ></component>
                </bk-form-item>
                <p class="title">
                    <span>子网信息</span>
                </p>
                <div v-if="formData.formList.length > 0">
                    <div
                        :key="index"
                        v-for="(item, index) in formData.formList"
                        style="margin-bottom: 20px;">
                        <div class="close-icon" v-if="index >= 1 && !currentId">
                            <bk-icon type="close" @click="delParams(index)" />
                        </div>
                        <bk-form-item
                            :icon-offset="30"
                            :required="true"
                            :label="'网段' + (index + 1)"
                            :property="'formList.' + index + '.ip_net'"
                            :rules="rules.ip_net">
                            <bk-input
                                v-model="item.ip_net"
                                :disabled="getDisabled"
                                placeholder="如:192.168.1.0/24">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            :icon-offset="50"
                            label="云区域"
                            :required="true"
                            :property="'formList.' + index + '.bk_cloud_id'"
                            :rules="rules.bk_cloud_id">
                            <bk-input
                                v-model="item.bk_cloud_id"
                                type="number"
                                :min="0"
                                placeholder="默认为0">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            :icon-offset="30"
                            label="网关"
                            :required="true"
                            :property="'formList.' + index + '.gateway'"
                            :rules="rules.gateway">
                            <bk-input
                                v-model="item.gateway"
                                placeholder="请输入网关">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            :icon-offset="30"
                            label="DNS服务器"
                            :required="true"
                            :property="'formList.' + index + '.dns'"
                            :rules="rules.dns">
                            <bk-input
                                v-model="item.dns"
                                placeholder="请输入DNS服务器">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            :icon-offset="30"
                            label="VLAN ID"
                            :property="'formList.' + index + '.vlan_id'">
                            <bk-input type="number"
                                v-model="item.vlan_id"></bk-input>
                        </bk-form-item>
                        <template v-for="(attr, j) in segmentAttr">
                            <bk-form-item
                                :icon-offset="30"
                                :key="j"
                                :required="attr.required"
                                :label="attr.display_name"
                                :rules="rules[attr.name]"
                                :property="'formList.' + index + '.' + attr.name">
                                <bk-input
                                    v-model="item[attr.name]"
                                    placeholder="请输入自定义属性值">
                                </bk-input>
                            </bk-form-item>
                        </template>
                    </div>
                </div>
                <div class="add-container" @click="addParams" v-if="!currentId">
                    <bk-icon type="plus-circle" />
                    <span>添加子网</span>
                </div>
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
                保存
            </bk-button>
            <bk-button
                ext-cls="mr5"
                theme="default"
                title="取消"
                @click="status = false">
                取消
            </bk-button>
        </div>
    </bk-sideslider>
</template>

<script>
    import dataSelect from '@/components/formWidget/dataSelect'
    export default {
        name: 'address-pool-side-slider',
        components: {
            dataSelect
        },
        model: {
            props: 'value',
            event: 'change'
        },
        props: {
            value: {
                type: Boolean,
                default: false
            },
            currentItem: {
                type: Object,
                default: () => {}
            },
            // 子网自定义属性
            segmentAttr: {
                type: Array,
                default: () => []
            }
        },
        data() {
            return {
                formData: {
                    ip_pool: '',
                    formList: [{
                        ip_net: '',
                        bk_cloud_id: '',
                        gateway: '',
                        dns: '',
                        vlan_id: ''
                    }]
                },
                rules: {
                    ip_pool: [
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
                        },
                        {
                            regex: /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\/([1-9]|[1-2][0-9]|3[0-2])$/,
                            message: '请输入正确网段',
                            trigger: 'blur'
                        }
                    ],
                    bk_cloud_id: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    gateway: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        },
                        {
                            min: 3,
                            message: function(val) {
                                return `${val}不能小于3个字符`
                            },
                            trigger: 'blur'
                        },
                        {
                            regex: /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/,
                            message: '请输入正确的网关',
                            trigger: 'blur'
                        }
                    ],
                    dns: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        },
                        {
                            regex: /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/,
                            message: '请输入正确的网关',
                            trigger: 'blur'
                        }
                    ]
                },
                status: false,
                isConfirm: false,
                currentId: '',
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
                        detailUrl: 'poolDetail',
                        initFlag: true // 是否需要请求初始值
                    }
                },
                segementAttrObj: {}
            }
        },
        computed: {
            getDisabled() {
                let flag = false
                if (this.currentId) {
                    flag = true
                }
                return flag
            }
        },
        watch: {
            value: {
                handler(newVal) {
                    this.status = newVal
                    if (!this.status) return false
                    this.currentId = this.currentItem['id'] || ''
                    // 编辑数据
                    this.currentId ? this.getDetailData() : this.formData = JSON.parse(JSON.stringify(this.currentItem))
                    this.$nextTick(() => {
                        this.settingPosition()
                    })
                }
            }
        },
        mounted() {
            this.getCustomAttr()
        },
        methods: {
            onVisibleChange() {
                this.$emit('change', this.status)
            },
            getCustomAttr() {
                if (this.segmentAttr.length === 0) return false
                this.customAttrRule(this.segmentAttr)
                this.segementAttrObj = {}
                this.segmentAttr.forEach(item => {
                    this.segementAttrObj[item.name] = ''
                })
                const IpNet = JSON.parse(JSON.stringify(this.formData.formList))
                this.formData.formList = IpNet.map(item => {
                    return { ...item, ...this.segementAttrObj }
                })
            },
            // 根据自定义属性添加表单的校验信息
            customAttrRule(data) {
                // 添加校验项
                data.forEach(ele => {
                    if (ele.required) {
                        this.rules[ele.name] = [{
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }]
                    }
                })
            },
            addParams() {
                this.formData.formList.push({
                    ip_net: '',
                    bk_cloud_id: '0',
                    gateway: '',
                    dns: '',
                    vlan_id: ''
                })
                this.$nextTick(() => {
                    this.settingPosition()
                })
            },
            delParams(index) {
                this.formData.formList.splice(index, 1)
                this.$nextTick(() => {
                    this.settingPosition()
                })
            },
            submitData() {
                this.isConfirm = true
                this.$refs.ipModifyForm.validate().then(validator => {
                    // 子网自定义属性结构 custom_attr: [{name: '', value: ''}]
                    const IpNet = JSON.parse(JSON.stringify(this.formData.formList))
                    IpNet.forEach(ipItem => {
                        const netCustomAttr = []
                        this.segmentAttr.forEach(attr => {
                            netCustomAttr.push({
                                name: attr.name,
                                value: ipItem[attr.name]
                            })
                            delete ipItem[attr.name]
                        })
                        ipItem['custom_attr'] = netCustomAttr
                    })
                    const params = IpNet.map(item => {
                        return {...item, ip_pool: this.formData.ip_pool}
                    })
                    if (!this.currentId) {
                        this.commonFetch({
                            ip_net: [...params]
                        }, 'add_ip_pool')
                    } else {
                        this.commonFetch({
                        ...params[0]
                        }, 'update_ip_pool')
                    }
                }, validator => {
                    this.isConfirm = false
                })
            },
            commonFetch(params = {}, url) {
                this.$api[url]({...params}).then(res => {
                    if (res.result) {
                        this._successMessage(this.currentId ? '修改成功' : '新增成功')
                        this.$emit('ok', this.currentId ? 'edit' : 'add')
                    } else {
                        this._errorMessage(res.message)
                    }
                }).finally(() => {
                    this.isConfirm = false
                })
            },
            // 获取修改地址池的详细信息
            getDetailData() {
                const _formData = {}
                const _currentItem = this.currentItem
                if (this.currentItem.custom_attr) {
                    this.currentItem.custom_attr.forEach(item => {
                        _currentItem[item.name] = item.value
                    })
                }
                _formData['formList'] = [{...this.currentItem}]
                const {ip_pool: ipPool, ip_pool_name: ipPoolName} = this.currentItem
                _formData['ip_pool'] = ipPool
                _formData['ip_pool_name'] = ipPoolName
                this.formData = {..._formData}
                this.addressPool.attr['defaultName'] = this.formData['ip_pool_name'] || ''
            }
        }
    }
</script>

<style scoped lang="scss">
    /deep/ .bk-label {
        width: 145px !important;
    }
    .bk-form-content {
        margin-left: 145px !important;
    }
    .bk-form-control {
        transform: translateX(-25px);
    }
    /deep/ .select_wrapper {
        transform: translateX(-25px);
    }
    .slider-content-wrapper {
        .title {
            text-align: left;
            margin-left: 24px;
        }
        .close-icon {
            text-align: left;
            margin-left: 24px;
            color: #979BA5;
            i {
                cursor: pointer;
            }
            &:hover {
                color: #3A84FF;
            }
        }
        .add-container {
            text-align: left;
            margin: 0 0 20px 145px;
            color: #3A84FF;
            font-size: 14px;
            cursor: pointer;
            i {
                color: #3A84FF;
                font-size: 18px !important;
            }
            span {
                font-size: 14px;
            }
        }
    }
</style>
