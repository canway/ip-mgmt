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
            地址池详情
            <span class="icon iconfont icon-changyongtubiao-bianji edit-icon" @click="toModify"></span>
        </div>
        <div
            slot="content"
            class="slider-content-wrapper">
            <bk-form
                :label-width="150"
                :model="formData"
                ref="validateForm">
                <p class="title">
                    <span>地址池信息</span>
                </p>
                <bk-form-item
                    label="名称"
                    :icon-offset="30"
                    :required="true">
                    <bk-input
                        :disabled="true"
                        v-model="formData.name"
                        placeholder="请输入地址池名称">
                    </bk-input>
                </bk-form-item>
                <template v-for="(attr, current) in customAttr">
                    <bk-form-item
                        :key="current"
                        :icon-offset="30"
                        :required="attr.required"
                        :label="attr.display_name">
                        <bk-input
                            :disabled="true"
                            v-model="formData[attr.name]"
                            placeholder="请输入自定义属性值">
                        </bk-input>
                    </bk-form-item>
                </template>
                <bk-divider style="width: calc(100% - 25px);left: 25px !important;margin: 2em 0;"></bk-divider>
                <p class="title">
                    <span>子网信息</span>
                </p>
                <div v-if="formData.ip_net.length > 0">
                    <div
                        :key="index"
                        v-for="(item, index) in formData.ip_net"
                        style="margin-bottom: 20px;">
                        <bk-form-item
                            :required="true"
                            :icon-offset="30"
                            :label="'网段' + (index + 1)">
                            <bk-input
                                :disabled="true"
                                v-model="item.ip_net"
                                placeholder="如:192.168.1.0/24">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            label="云区域"
                            :icon-offset="30"
                            :required="true">
                            <bk-input
                                :disabled="true"
                                v-model="item.bk_cloud_id"
                                placeholder="默认为0">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            label="网关"
                            :icon-offset="30"
                            :required="true">
                            <bk-input
                                :disabled="true"
                                v-model="item.gateway"
                                placeholder="请输入网关">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item
                            label="DNS服务器"
                            :icon-offset="30"
                            :required="true">
                            <bk-input
                                :disabled="true"
                                v-model="item.dns"
                                placeholder="请输入DNS服务器">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item label="VLAN ID">
                            <bk-input v-model="item.vlan_id" :disabled="true"></bk-input>
                        </bk-form-item>
                        <template v-for="(attr, j) in segmentAttr">
                            <bk-form-item
                                :key="j"
                                :icon-offset="30"
                                :required="attr.required"
                                :label="attr.display_name">
                                <bk-input
                                    :disabled="true"
                                    v-model="item[attr.name]"
                                    placeholder="请输入自定义属性值">
                                </bk-input>
                            </bk-form-item>
                        </template>
                    </div>
                </div>
            </bk-form>
        </div>
    </bk-sideslider>
</template>

<script>
    export default {
        name: 'address-pool-detail',
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
                formData: {
                    name: '',
                    ip_net: [{
                        ip_net: '',
                        bk_cloud_id: '',
                        gateway: '',
                        dns: '',
                        vlan_id: ''
                    }]
                },
                status: false,
                // 子网自定属性map集合
                segementAttrObj: {}
            }
        },
        watch: {
            value: {
                handler(newVal) {
                    this.status = newVal
                    if (!this.status) return false
                    this.currentId = this.currentItem['id'] || ''
                    // 编辑数据
                    if (this.currentId) {
                        this.getData()
                    }
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
                // 获取地址池自定义属性数据
                if (this.customAttr.length === 0) return false
                this.customAttr.forEach(item => {
                    this.formData[item.name] = ''
                })
                // 获取子网自定义属性数据
                if (this.segmentAttr.length === 0) return false
                this.segementAttrObj = {}
                this.segmentAttr.forEach(item => {
                    this.segementAttrObj[item.name] = ''
                })
                const IpNet = JSON.parse(JSON.stringify(this.formData.ip_net))
                this.formData.ip_net = IpNet.map(item => {
                    return { ...item, ...this.segementAttrObj }
                })
            },
            getData() {
                if (this.customAttr.length === 0 || this.segmentAttr.length) {
                    this.getCustomAttr()
                }
                this.formData = {
                    ...this.currentItem
                }
                if (this.currentItem.custom_attr && Array.isArray(this.currentItem.custom_attr)) {
                    this.currentItem.custom_attr.forEach(item => {
                        this.formData[item.name] = item.value
                    })
                }
                const IpNet = JSON.parse(JSON.stringify(this.formData.ip_net))
                this.formData.ip_net = IpNet.map(item => {
                    const attrObj = {}
                    if (item.custom_attr && Array.isArray(item.custom_attr)) {
                        item.custom_attr.forEach(attrItem => {
                            attrObj[attrItem.name] = attrItem.value
                        })
                    }
                    return { ...item, ...attrObj }
                })
            },
            toModify() {
                this.$emit('click-edit', true)
            }
        }
    }
</script>

<style scoped lang="scss">
.icon-edit::before {
    color: #979BA5;
    margin-left: 10px;
}
.slider-content-wrapper {
    width: 100%;
    padding-right: 20px;
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
        margin: 0 0 20px 130px;
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
    cursor: pointer;
}
</style>
