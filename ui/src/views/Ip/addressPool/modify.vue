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
            {{ type === 'detail' ? '地址池信息' : currentId ? '编辑地址池' : '新增地址池' }}
            <span class="icon iconfont icon-changyongtubiao-bianji edit-icon" @click="toModify"
                v-if="type === 'detail'"></span>
        </div>
        <div
            slot="content"
            class="slider-content-wrapper">
            <bk-form
                :label-width="170"
                :model="formData"
                :rules="rules"
                ref="validateForm">
                <p class="title">
                    <span>地址池信息</span>
                </p>
                <bk-form-item
                    label="名称"
                    :icon-offset="30"
                    :required="true"
                    :property="'name'"
                    :rules="rules['name']">
                    <bk-input
                        :disabled="isDisabled"
                        v-model="formData.name"
                        placeholder="请输入地址池名称">
                    </bk-input>
                </bk-form-item>
                <template v-for="(attr, current) in customAttr">
                    <bk-form-item
                        :key="current"
                        :icon-offset="30"
                        :required="attr.required"
                        :label="attr.display_name"
                        :rules="rules[attr.name]"
                        :property="formData[attr.name + '']">
                        <bk-input
                            :disabled="isDisabled"
                            v-model="formData[attr.name]"
                            :placeholder="'请输入' + attr.display_name">
                        </bk-input>
                    </bk-form-item>
                </template>
                <bk-divider style="width:calc(100% - 50px);left:25px !important;margin:2em 0"></bk-divider>
                <p class="title">
                    <span>子网信息</span>
                </p>
                <div v-if="formData.ip_net && formData.ip_net.length > 0">
                    <div
                        :key="index"
                        v-for="(item, index) in formData.ip_net"
                        style="margin-bottom: 20px">
                        <div class="close-icon">
                            <bk-icon type="close" @click="delParams(index)" />
                        </div>
                        <bk-form-item
                            :required="true"
                            :icon-offset="30"
                            :label="'网段' + (index + 1)"
                            :property="'ip_net.' + index + '.ip_net'"
                            :rules="rules.ip_net">
                            <bk-input
                                v-model="item.ip_net"
                                :disabled="getDisabled && (IpNetLength > index) && item.ip_net !== '' || isDisabled"
                                placeholder="如:192.168.1.0/24">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            label="云区域"
                            :icon-offset="50"
                            :required="true"
                            :property="'ip_net.' + index + '.bk_cloud_id'"
                            :rules="rules.bk_cloud_id">
                            <bk-input
                                :disabled="isDisabled"
                                v-model="item.bk_cloud_id"
                                type="number"
                                :min="0"
                                placeholder="默认为0">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            label="网关"
                            :icon-offset="30"
                            :required="true"
                            :property="'ip_net.' + index + '.gateway'"
                            :rules="rules.gateway">
                            <bk-input
                                :disabled="isDisabled"
                                v-model="item.gateway"
                                placeholder="请输入网关">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            label="DNS服务器"
                            :required="true"
                            :icon-offset="30"
                            :property="'ip_net.' + index + '.dns'"
                            :rules="rules.dns">
                            <bk-input
                                :disabled="isDisabled"
                                v-model="item.dns"
                                placeholder="请输入DNS服务器">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            label="VLAN ID"
                            :icon-offset="30"
                            :property="'ip_net.' + index + '.vlan_id'">
                            <bk-input :disabled="isDisabled"
                                type="number"
                                :min="0"
                                v-model="item.vlan_id"></bk-input>
                        </bk-form-item>
                        <template v-for="(attr, j) in segmentAttr">
                            <bk-form-item
                                :icon-offset="30"
                                :key="j"
                                :required="attr.required"
                                :label="attr.display_name"
                                :rules="rules[attr.name]"
                                :property="'ip_net.' + index + '.' + attr.name">
                                <bk-input
                                    :disabled="isDisabled"
                                    v-model="item[attr.name]"
                                    :placeholder="'请输入' + attr.display_name">
                                </bk-input>
                            </bk-form-item>
                        </template>
                    </div>
                </div>
                <div class="add-container" @click="addParams" v-if="!isDisabled">
                    <bk-icon type="plus-circle" />
                    <span>添加子网</span>
                </div>
            </bk-form>
        </div>
        <div slot="footer" v-if="!isDisabled">
            <bk-button
                ext-cls="mr5"
                theme="primary"
                title="保存"
                :loading="isConfirm"
                @click.stop.prevent="submitData"
                style="margin-left: 24px">
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
    export default {
        name: 'address-pool-side-slider',
        model: {
            props: 'value',
            event: 'change'
        },
        props: {
            type: {
                type: String,
                default: ''
            },
            value: {
                type: Boolean,
                default: false
            },
            currentItem: {
                type: Object,
                default: () => {}
            },
            // 地址池自定义属性
            customAttr: {
                type: Array,
                default: () => []
            },
            // 子网自定义属性
            segmentAttr: {
                type: Array,
                default: () => []
            }
        },
        data() {
            return {
                currentId: '',
                IpNetLength: 0,
                formData: {
                    name: '',
                    ip_net: [{
                        ip_net: '',
                        bk_cloud_id: '0',
                        gateway: '',
                        dns: '',
                        vlan_id: ''
                    }]
                },
                rules: {
                    name: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'change'
                        }
                    ],
                    ip_net: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'change'
                        },
                        {
                            regex: /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\/([1-9]|[1-2][0-9]|3[0-2])$/,
                            message: '请输入正确网段',
                            trigger: 'change'
                        }
                    ],
                    bk_cloud_id: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'change'
                        }
                    ],
                    gateway: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'change'
                        },
                        {
                            min: 3,
                            message: function(val) {
                                return `${val}不能小于3个字符`
                            },
                            trigger: 'change'
                        },
                        {
                            regex: /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/,
                            message: '请输入正确的网关',
                            trigger: 'change'
                        }
                    ],
                    dns: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'change'
                        },
                        {
                            regex: /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/,
                            message: '请输入正确的dns服务器',
                            trigger: 'change'
                        }
                    ]
                },
                status: false,
                isConfirm: false,
                // 子网自定属性map集合
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
            },
            isDisabled() {
                return this.type === 'detail'
            }
        },
        watch: {
            value: {
                handler(newVal) {
                    this.status = newVal
                    if (!this.status) return false
                    this.currentId = this.currentItem['id'] || ''
                    // 编辑数据
                    this.currentId ? this.getData() : this.formData = JSON.stringify(this.currentItem) && JSON.parse(JSON.stringify(this.currentItem))
                    this.$nextTick(() => {
                        this.settingPosition()
                        if (!this.currentId) {
                            this.getCustomAttr()
                        }
                    })
                }
            }
        },
        methods: {
            onVisibleChange() {
                this.$emit('change', this.status)
            },
            /*
                获取地址池和子网的自定义属性
                type:("ip_pool", "IP地址池自定义属性"), ("tetwork_segment", "子网自定义属性"), ("ips", "ip自定义属性")
            */
            getCustomAttr() {
                if (this.customAttr.length === 0) return false
                this.customAttrRule(this.customAttr)
                this.customAttr.forEach(item => {
                    this.formData[item.name] = ''
                })
                if (this.segmentAttr.length === 0) return false
                this.customAttrRule(this.segmentAttr)
                this.segementAttrObj = {}
                this.segmentAttr.forEach(item => {
                    this.segementAttrObj[item.name] = ''
                })
                const IpNet = JSON.parse(JSON.stringify(this.formData.ip_net))
                this.formData.ip_net = IpNet.map(item => {
                    return {...item, ...this.segementAttrObj}
                })
            },
            // 根据自定义属性添加表单的校验信息
            customAttrRule(data) {
                // 加校验项
                data.forEach(ele => {
                    if (ele.required) {
                        this.rules[ele.name] = [{
                            required: true,
                            message: '必填项',
                            trigger: 'change'
                        }]
                    }
                })
                this.rules = {...this.rules}
            },
            getData() {
                this.getCustomAttr()
                this.formData = {
                    ...this.currentItem
                }
                console.log(this.formData)
                if (this.currentItem.custom_attr && Array.isArray(this.currentItem.custom_attr)) {
                    this.currentItem.custom_attr.forEach(item => {
                        this.formData[item.name] = item.value
                    })
                }
                const IpNet = JSON.stringify(this.formData.ip_net) && JSON.parse(JSON.stringify(this.formData.ip_net))
                if (IpNet) {
                    this.IpNetLength = IpNet.length
                    this.formData.ip_net = IpNet.map(item => {
                        const attrObj = {}
                        if (item.custom_attr && Array.isArray(item.custom_attr)) {
                            item.custom_attr.forEach(attrItem => {
                                attrObj[attrItem.name] = attrItem.value
                            })
                        }
                        return {...item, ...attrObj}
                    })
                }
            },
            addParams() {
                this.formData.ip_net.push({
                    ip_net: '',
                    bk_cloud_id: '0',
                    gateway: '',
                    dns: '',
                    vlan_id: '',
                    ...this.segementAttrObj
                })
                this.$nextTick(() => {
                    this.settingPosition()
                })
            },
            delParams(index) {
                if (this.formData.ip_net.length <= 1) {
                    this._errorMessage('地址池至少需要一个子网！')
                    return
                }
                this.formData.ip_net.splice(index, 1)
                this.$nextTick(() => {
                    this.settingPosition()
                })
            },
            submitData() {
                this.isConfirm = true
                const _this = this
                if (_this.formData.ip_net.length === 0) {
                    this._errorMessage('地址池至少需要一个子网！')
                    return
                }
                this.$nextTick(() => {
                    this.$refs.validateForm.validate().then(validator => {
                        if (this.currentId) {
                            this.commonFetch('modify_ip_pool')
                        } else {
                            this.commonFetch('create_ip_pool')
                        }
                    }, validator => {
                        this.isConfirm = false
                    })
                })
            },
            commonFetch(url) {
                // 自定义属性结构 customAttr: [{name: '', value: ''}]
                const _formData = JSON.parse(JSON.stringify(this.formData))
                const customAttr = []
                this.customAttr.forEach(item => {
                    customAttr.push({
                        name: item.name,
                        value: _formData[item.name]
                    })
                    delete _formData[item.name]
                })
                _formData['customAttr'] = customAttr
                // 子网自定义属性结构 custom_attr: [{name: '', value: ''}]
                const IpNet = JSON.parse(JSON.stringify(_formData.ip_net))
                IpNet.forEach(ipItem => {
                    const netCustomAttr = []
                    this.segmentAttr.forEach(attr => {
                        netCustomAttr.push({
                            name: attr.name,
                            value: ipItem[attr.name]
                        })
                    })
                    ipItem['custom_attr'] = netCustomAttr
                })
                _formData.ip_net = [...IpNet]
                this.$api[url]({
                    ..._formData
                }).then(res => {
                    if (res.result) {
                        if (res.message !== '') {
                            this._errorMessage(res.message)
                            if (!this.currentId) {
                                this.$emit('ok', 'add')
                            }
                        } else {
                            this._successMessage(this.currentId ? '修改成功' : '新增成功')
                            this.$emit('ok', this.currentId ? 'edit' : 'add')
                        }
                    } else {
                        this._errorMessage(res.message)
                    }
                }).finally(() => {
                    this.isConfirm = false
                })
            },
            toModify() {
                this.$emit('click-edit', true)
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
    width: 100%;
    box-sizing: border-box;

    .title {
        text-align: left;
        margin-left: 24px;

        span {
            display: inline-block;
            font-weight: 600;
            color: #63656E;
        }
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

.edit-icon {
    display: inline-block;
    font-size: 28px;
    vertical-align: middle;
    cursor: pointer
}
</style>
