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
    <div class="select_wrapper">
        <bk-select v-bind="attr"
            ref="bkSelect"
            v-model="valueTxt"
            style="width: 100%;"
            @change="onchange"
            @toggle="onToggle"
            :loading="loading"
            :disabled="disabled"
            display-tag
            :placeholder="placeholder"
            :remote-method="attr.remote && toRemoteSearch">
            <bk-option v-for="option in dataOptions"
                :key="option.id"
                :id="option.id"
                :name="option.ip">
            </bk-option>
        </bk-select>
    </div>
</template>

<script>
    /**
     * @comopnent 下拉选择器公用组件
     * @props {
     *   value 组件值
     *   attr 属性值 {initFlag: 是否初始值获取， true:若有defaultName(回显值)，则无需请求后台，push进数组即可； nameKey：关联上级数据的key值，通过formData获取相关的数据值, allocateStatus: ip的分配状态}
     * }
     */
    import _ from 'lodash'

    export default {
        name: 'data-select',
        model: {
            props: 'value',
            event: 'change'
        },
        props: {
            value: {
                type: [Array, String, Number]
            },
            placeholder: {
                type: String,
                default: ''
            },
            size: {
                type: String,
                default: 'small'
            },
            defaultValue: {
                type: [Array, String, Number],
                require: true
            },
            formData: {
                type: Object,
                default: () => {}
            },
            attr: {
                type: Object,
                default: () => {},
                require: true
            },
            disabled: {
                type: Boolean,
                default: false
            }
        },
        data() {
            this.toFetchData = _.debounce(this.toFetchData, 800)
            return {
                valueTxt: null,
                loading: false,
                dataOptions: [],
                originData: [],
                remoteSearchQuery: []
            }
        },
        computed: {
            // 子网关联地址池数据的获取
            getPoolInfo() {
                if (this.attr['nameKey']) {
                    return this.formData[this.attr['nameKey']]
                } else {
                    return ''
                }
            }
        },
        watch: {
            value: {
                handler(newVal) {
                    this.valueTxt = newVal || this.defaultValue
                }
            },
            getPoolInfo: {
                handler(value) {
                    this.attr['multiple'] ? this.valueTxt = [] : this.valueTxt = ''
                    if (value) {
                        this.toFetchData()
                    } else {
                        this.dataOptions = []
                    }
                }
            }
        },
        created() {
            this.valueTxt = this.value || this.defaultValue
            // 是否开始动态数据加载功能
            if (!this.attr.remote) {
                this.dataOptions = this.attr.options
            }
            if (this.getPoolInfo) {
                this.toFetchData()
            }
        },
        methods: {
            // 获取当前选择框数据,拼凑成选项
            getSelection() {
                const selectedName = this.$refs.bkSelect.selectedName.split(',')
                const selectedId = this.$refs.bkSelect.selected
                const selectedData = []
                selectedId.forEach((item, index) => {
                    const optionItem = {
                        id: item,
                        ip: selectedName[index]
                    }
                    selectedData.push(optionItem)
                })
                return selectedData
            },
            onchange(newValue) {
                this.$emit('change', newValue)
                if (this.attr['multiple']) {
                    const _current = this.dataOptions.filter(item => newValue.includes(item.id))
                    this.currentItem = _current
                    this.$emit('row-change', _current)
                }
            },
            onToggle(open) {
                if (!open) {
                    const addOptions = this.getSelection().filter(item => !this.originData.some(ele => ele.id === item.id))
                    this.dataOptions = addOptions.concat(this.originData)
                }
            },
            toRemoteSearch(query) {
                this.remoteSearchQuery.push(query)
                this.loading = true
                if (!this.attr['url']) return false
                this.$api[this.attr['url']]({
                    ip: query,
                    ip_net: this.getPoolInfo,
                    allocate_status: this.attr.allocateStatus || ''
                }).then(res => {
                    if (res.result) {
                        // 取最后一次请求的数据进行处理
                        if (this.remoteSearchQuery[this.remoteSearchQuery.length - 1] === query) {
                            const addOptions = this.getSelection().filter(item => !res.data.results.some(ele => ele.id === item.id))
                            this.dataOptions = addOptions.concat(res.data.results)
                            this.remoteSearchQuery = []
                        }
                    } else {
                        this.dataOptions = []
                    }
                }).finally(() => {
                    this.loading = false
                })
            },
            async toFetchData() {
                this.loading = true
                if (!this.attr['url']) return false
                try {
                    const res = await this.$api[this.attr['url']]({
                        ip_net: this.getPoolInfo,
                        allocate_status: this.attr.allocateStatus || ''
                    })
                    if (res.result) {
                        this.originData = res.data.results
                        const addOption = this.originData.filter(item => !this.valueTxt.includes(item.id))
                        this.dataOptions = this.attr.defaultOption.concat(addOption)
                    } else {
                        this.dataOptions = []
                    }
                } finally {
                    this.loading = false
                }
            }
        }
    }
</script>
