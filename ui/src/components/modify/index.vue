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
        @shown="onVisibleChange"
        @hidden="onVisibleChange"
        :quick-close="false">
        <div slot="header">
            {{ title }}
        </div>
        <div
            slot="content"
            :class="['slider-content-wrapper',(isEdit && 'edit-content-wrapper')]">
            <bk-form
                :label-width="125"
                :model="datas"
                :rules="rules"
                ref="modifyForm">
                <bk-form-item v-for="(item, index) in widgets"
                    :label="item.label"
                    :required="item.required"
                    :property="item.name"
                    :key="index">
                    <component v-if="!item.custom" :is="'bk-' + item.widget"
                        v-model="datas[item.name]"
                        :placeholder="item.placeholder"
                        :size="item.size"
                        v-bind="item.attr"
                        :disabled="item.disabled"
                    ></component>
                    <component v-if="item.custom" :is="item.widget"
                        v-model="datas[item.name]"
                        :placeholder="item.placeholder"
                        :default-value="item.defaultValue"
                        :size="item.size"
                        :attr="item.attr"
                        :disabled="item.disabled"
                    ></component>
                    <span v-if="isEdit" class="icon iconfont icon-changyongtubiao-bianji edit-icon" @click="toEdit(item)"></span>
                </bk-form-item>
            </bk-form>
        </div>
        <div slot="footer" style="background-color: transparent !important;" v-if="isShowFooter">
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
                @click="visible = false">
                取消
            </bk-button>
        </div>
    </bk-sideslider>
</template>

<script>
    /**
     * @comopnent 表格公用组件
     * @props {
     *   formData:{} 表单值
     *   formWidgets:[{
     *          widget： 表单控件的属性值：如：input，date-picker
     *          label: 标签值
     *          required: 是否必填
     *          name: key值
     *          placeholder: 空白提示
     *          disabled： 是否禁用
     *          attr: {}  //支持该控件下的属性值
     *   }] 表单数据配置
     *   rules:{} 参考magicbox的属性值
     *   isEdit:Boolean 是否启用编辑按钮
     *   title： 抽屉的标题
     *   isShowFooter： 是否展示确认和取消按钮
     *   submitLoading： 加载loading状态
     * }
     */
    import dataSelect from '@/components/formWidget/dataSelect'
    export default {
        name: 'modify-components',
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
            title: {
                type: String,
                default: '',
                required: true
            },
            formData: {
                type: Object,
                default: () => {}
            },
            formWidgets: {
                type: Array,
                default: () => [],
                required: true
            },
            rules: {
                type: Object,
                default: () => {}
            },
            isEdit: {
                type: Boolean,
                default: false
            },
            isShowFooter: {
                type: Boolean,
                default: true
            },
            submitLoading: {
                type: Boolean,
                default: false
            }
        },
        data() {
            return {
                datas: {},
                widgets: [],
                visible: false,
                isConfirm: false,
                currentId: ''
            }
        },
        watch: {
            value: {
                handler(newVal) {
                    this.visible = newVal
                    if (!this.visible) return false
                    this.currentId = this.formData['id'] || ''
                    if (this.isEdit) {
                        this.widgets = this.widgets.map(item => {
                            return {...item, disabled: true}
                        })
                    }
                    this.datas = this.formData || {}
                    this.$nextTick(() => {
                        this.settingPosition()
                    })
                }
            },
            submitLoading: {
                handler(value) {
                    this.isConfirm = value
                },
                immediate: true
            }

        },
        mounted() {
            this.datas = this.formData || {}
            this.widgets = this.formWidgets
        },
        methods: {
            onVisibleChange() {
                this.$emit('change', this.visible)
            },
            toEdit(item) {
                item.disabled = !item.disabled
            },
            submitData() {
                this.isConfirm = true
                this.$refs.modifyForm.validate().then(validator => {
                    if (this.isEdit) {
                        const _data = {}
                        this.widgets.forEach(item => {
                            if (!item.disabled) {
                                _data[item.name] = this.datas[item.name]
                            }
                        })
                        if (Object.keys(_data).length === 0) {
                            this.isConfirm = false
                            return false
                        }
                        this.$emit('submit', _data)
                    } else {
                        this.$emit('submit', this.datas)
                    }
                }, validator => {
                    this.isConfirm = false
                })
            }
        }
    }
</script>

<style scoped lang="scss">
.slider-content-wrapper {
    padding: 15px 20px;
    box-sizing: border-box;
    /deep/ .bk-form-content {
        position: relative;
    }
}
.edit-content-wrapper {
    /deep/ .bk-form-content {
        padding-right: 20px !important;
        >i {
            position: absolute;
            right: 0;
            top: 30%;
            cursor: pointer;
            color: #63656E;
            &:hover {
                color: #3A84FF;
            }
        }
        .bk-date-picker {
            width: 90% !important;
            display: inline-block;
        }
        .select_wrapper {
            width: 90%;
            display: inline-block;
        }
        .bk-form-control {
            width: 90%;
        }
    }
}
.edit-icon {
    display: inline-block;
    font-size: 28px;
    vertical-align: middle;
    &:hover {
        color: #3A84FF;
    }
}
</style>
