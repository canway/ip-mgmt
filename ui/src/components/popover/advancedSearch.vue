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
    <div class="advanced-search-wrapper search-container">
        <bk-button :theme="'default'" class="mr10 ml10 more" :icon-right="visible ? 'angle-double-up' : 'angle-double-down'" @click="visible = !visible">
            高级搜索
        </bk-button>
        <div class="advanced-search-wrapper" v-if="visible">
            <bk-form form-type="inline" class="search-form"
                :model="ParamsData" :rules="rules"
                :label-width="100" ref="validateForm1">
                <bk-form-item v-for="(item, index) in formWidgets"
                    :label="item.label"
                    :required="item.required"
                    :property="item.name"
                    :key="index">
                    <component v-if="!item.custom" :is="'bk-' + item.widget"
                        v-model="ParamsData[item.name]"
                        :placeholder="item.placeholder"
                        :size="item.size"
                        v-bind="item.attr"
                    ></component>
                    <component v-if="item.custom" :is="item.widget"
                        :form-data="ParamsData"
                        v-model="ParamsData[item.name]"
                        :placeholder="item.placeholder"
                        :default-value="item.defaultValue"
                        :size="item.size"
                        :attr="item.attr"
                    ></component>
                </bk-form-item>
                <bk-form-item class="button-wrapper">
                    <bk-button theme="primary" title="提交" @click.stop.prevent="validate1" :loading="isChecking">查询</bk-button>
                    <bk-button theme="default" title="重置" @click.stop.prevent="clearError1">重置</bk-button>
                    <bk-button theme="default" title="取消" @click.stop.prevent="visible = false">关闭</bk-button>
                </bk-form-item>
            </bk-form>
        </div>
    </div>
</template>

<script>
    /**
     * @comopnent 高级查询
     * @props {
     *   条件数据配置
     *   formWidgets:[{
     *          widget： 表单控件的属性值：如：input，date-picker
     *          label: 标签值
     *          required: 是否必填
     *          name: key值
     *          placeholder: 空白提示
     *          disabled： 是否禁用
     *          attr: {}  //支持该控件下的属性值
     *   }]
     *   校验规则
     *     rules: {}  参考magicbox的属性值
     * }
     */
    import ipSelect from '../formWidget/ipSelect'
    import dataSelect from '../formWidget/dataSelect'
    import ipNetSelect from '../formWidget/ipNetSelect'

    export default {
        name: 'advanced-search',
        components: {
            ipSelect,
            dataSelect,
            ipNetSelect
        },
        props: {
            formWidgets: {
                type: Array,
                default: () => [],
                require: true
            },
            rules: {
                type: Object,
                default: () => {}
            }
        },
        data() {
            return {
                visible: false,
                isChecking: false,
                ParamsData: {}
            }
        },
        mounted() {
            // 弹窗阻止冒泡
            document.onclick = (e) => {
                if (e.target.className.includes('bk-option') || e.target.className.includes('bk-select')) return
                const Node = e.target.parentNode
                if (Node && (Node.className.includes('bk-date-picker') || Node.className.includes('bk-picker-panel-sidebar'))) return
                this.visible = false
            }
            const elementWrapper = document.getElementsByClassName('advanced-search-wrapper')
            elementWrapper[0].onclick = (e) => {
                // 取消事件冒泡
                if (e && e.stopPropagation) {
                    e.stopPropagation()
                } else if (window.event) {
                    window.event.cancelBubble = true
                }
            }
        },
        methods: {
            validate1() {
                this.isChecking = true
                this.$refs.validateForm1.validate().then(validator => {
                    this.$emit('submit', JSON.parse(JSON.stringify(this.ParamsData)))
                    this.isChecking = false
                    this.visible = false
                }, validator => {
                    this.isChecking = false
                })
            },
            clearError1() {
                this.$refs.validateForm1.clearError()
                this.ParamsData = {}
                this.$emit('submit', JSON.parse(JSON.stringify(this.ParamsData)))
                this.visible = false
            }
        }
    }
</script>

<style scoped lang="scss">
.search-container {
    width: auto;
    display: inline-block;
    .more {
        padding-right: 20px;
        padding-left: 8px;
        position: relative;
        i {
            font-size: 20px !important;
            position: absolute;
            right: 2px;
            top: 7px;
        }
    }
    .advanced-search-wrapper {
        width: 100%;
        height: auto;
        background: #fff;
        position: absolute;
        top: 52px;
        left: 0;
        z-index: 999;
        -webkit-box-shadow: 0 3px 6px 1px #dcdee5;
        box-shadow: 0 3px 6px 1px #dcdee5;
        box-sizing: border-box;
        padding: 10px;
    }
    /deep/.search-form {
        width: 100%;
        padding: 10px;
        box-sizing: border-box;
        .bk-form-item {
            display: inline-flex;
            width: 23.5%;
            margin-bottom: 25px;
            margin-left: 16px;
            .bk-label {
                width: 70px !important;
                padding: 0 8px 0 0;
                span {
                    display: inline-block;
                    width: 100%;
                    line-height: 32px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
            }
            .bk-form-content {
                width: 100%;
                flex: 1;
            }
        }
        .bk-form-item:nth-child(4n+1) {
            margin-left: 0 !important;
        }
        .button-wrapper {
            width: 100%;
            display: block;
            text-align: center;
            height: auto;
            overflow: hidden;
            margin: 20px 5px 0;
            button {
                margin-right: 8px;
            }
        }
    }
}
</style>
