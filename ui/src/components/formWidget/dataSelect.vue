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
            v-model="valueTxt"
            style="width: 100%;"
            @change="onchange"
            :loading="loading"
            :disabled="disabled"
            :placeholder="placeholder"
            :remote-method="attr.remote && toRemoteSearch">
            <bk-option v-for="option in dataOptions"
                :key="option.id"
                :id="option.id"
                :name="option.name">
            </bk-option>
        </bk-select>
    </div>
</template>

<script>
    /**
     * @comopnent 下拉选择器公用组件
     * @props {
     *   value 组件值
     *   defaultValue 默认值
     *   disabled 是否禁用
     *   attr 属性值 {initFlag: 是否初始值获取， true:若有defaultName(回显值)，则无需请求后台，push进数组即可}
     * }
     */
    import debounce from 'lodash/debounce'
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
            this.toFetchData = debounce(this.toFetchData, 800)
            return {
                valueTxt: null,
                loading: false,
                dataOptions: [],
                currentItem: {},
                // 第一页数据缓存
                originalData: []
            }
        },
        watch: {
            value: {
                handler(newVal) {
                    this.valueTxt = newVal || this.defaultValue
                }
            }
        },
        created() {
            this.valueTxt = this.value || this.defaultValue
            // 是否开始动态数据加载功能
            if (!this.attr.remote) {
                this.dataOptions = this.attr.options
            } else {
                this.toFetchData('', 1)
            }
        },
        methods: {
            onchange(newValue) {
                if (this.isCurrent(newValue)) {
                    this.currentItem = {...this.isCurrent(newValue)}
                }
                this.$emit('change', newValue)
            },
            isCurrent(id) {
                return this.dataOptions.find(item => item.id === id)
            },
            toRemoteSearch(query) {
                if (query) {
                    this.toFetchData(query)
                } else {
                    this.dataOptions = [...this.originalData]
                    if (Object.keys(this.currentItem).length > 0 && !this.isCurrent(this.currentItem['id'])) {
                        this.dataOptions.unshift(this.currentItem)
                    }
                }
            },
            async toFetchData(query, init) {
                this.loading = true
                if (!this.attr['url']) return false
                try {
                    const res = await this.$api[this.attr['url']]({
                        name: query,
                        page_size: 10
                    })
                    if (res.result) {
                        this.dataOptions = res.data.results
                        if (init) {
                            this.originalData = res.data.results
                            let same = true
                            if (this.attr.defaultOption && res.data.count > 10) {
                                for (let i = 0; i < this.originalData.length; i++) {
                                    if (this.originalData[i].id === this.attr.defaultOption.id) {
                                        same = true
                                        break
                                    }
                                }
                            }
                            if (!same) this.originalData.unshift(this.attr.defaultOption)
                        }
                    } else {
                        this.dataOptions = []
                    }
                } finally {
                    this.loading = false
                    if (this.valueTxt && this.attr['initFlag']) {
                        this.initData()
                    }
                }
            },
            initData() {
                const _id = this.valueTxt
                const _current = this.dataOptions.find(item => item.id === _id)
                if (!_current) {
                    if (this.attr['defaultName']) {
                        const _default = [{name: this.attr['defaultName'], id: _id}]
                        this.dataOptions = [...this.dataOptions, ..._default]
                    } else {
                        if (!this.attr['detailUrl']) return false
                        this.$api[this.attr['detailUrl']]({
                            id: _id
                        }).then(_res => {
                            this.dataOptions.unshift(_res)
                        })
                    }
                }
            }
        }
    }
</script>
