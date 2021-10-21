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
    <div class="table-container">
        <bk-table
            :max-height="maxHeight"
            :data="data"
            ref="table"
            :outer-border="false"
            :header-border="false"
            @select="onselect"
            @select-all="selectAll"
            @selection-change="selectChange"
            :pagination="pagination"
            @page-change="handlePageChange"
            @page-limit-change="limitChange"
            @filter-change="filterChange"
            @sort-change="sortChange"
        >
            <bk-table-column v-if="selectColumn.visible" type="selection" width="60" :fixed="selectColumn.fixed"></bk-table-column>
            <bk-table-column v-if="orderColumn.visible" type="index" label="序号" width="60" :fixed="orderColumn.fixed"></bk-table-column>
            <bk-table-column
                v-for="item in setting.selectFields"
                :key="item.key"
                :width="item.width"
                :label="item.label"
                v-bind="item.attr"
                :align="item.align || 'left'"
                :prop="item.key"
                :column-key="item.key"
                :sortable="item.sortable"
                :filters="item.filters"
                :filter-method="columnFilterMethod"
                :filter-multiple="item.filterMultiple">
                <template slot-scope="props">
                    <template v-if="item.scopedSlots">
                        <slot :name="item.scopedSlots.customRender" :scope="props.row"></slot>
                    </template>
                    <span v-else>{{ props.row[item.key] || (props.row[item.key] === 0 ? props.row[item.key] : '--')}}</span>
                </template>
            </bk-table-column>
            <bk-table-column type="setting" v-if="settingsFields && settingsFields.length > 0">
                <bk-table-setting-content
                    :fields="setting.fields"
                    :selected="setting.selectFields"
                    :max="setting.max"
                    value-key="key"
                    :size="setting.size"
                    @setting-change="handleSettingChange">
                </bk-table-setting-content>
            </bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    /**
     * @comopnent 表格组件
     * @props {
     *   columns:[] 表头数据配置 :scopedSlots: { customRender: 'name' }渲染的模板
     *   data:显示的数据
     *   pagination:分页 { current:当前页,count:总数,limit:每页的数量 }
     *   selectColumn:{visible:true(是否开启行选项功能) , fixed:true(是否开启定位) }
     *   orderColumn:{visible:true(是否开启行选项功能) , fixed:true(是否开启定位) }
     *   settingsFields:[]
     * }
     */
    export default {
        name: 'table-component',
        props: {
            data: {
                type: Array,
                default: () => [],
                require: true
            },
            columns: {
                type: Array,
                default: () => [],
                require: true
            },
            pagination: {
                type: Object,
                default: () => {}
            },
            settingsFields: {
                type: Array,
                default: () => []
            },
            selectColumn: {
                type: Object,
                default: () => {
                    return {
                        visible: false,
                        fixed: false
                    }
                }
            },
            orderColumn: {
                type: Object,
                default: () => {
                    return {
                        visible: false,
                        fixed: false
                    }
                }
            }
        },
        data() {
            return {
                setting: {
                    fields: [],
                    selectFields: [],
                    size: 'small'
                },
                topDistance: 0,
                maxHeight: 'auto'
            }
        },
        mounted() {
            this.setting.selectFields = this.columns
            this.setting.fields = this.settingsFields || []
            // 计算表格的最高高度
            // 表格相对于版面或由offsetTop属性指定的父坐标的计算顶端位置
            this.topDistance = parseInt(this.$refs.table.$el.offsetTop)
            this.maxHeight = window.innerHeight - this.topDistance - 52 - 20
            window.onresize = () => {
                return (() => {
                    this.settingPosition()
                    this.maxHeight = window.innerHeight - this.topDistance - 52 - 20
                })()
            }
        },
        methods: {
            // 过滤字段触发方法
            columnFilterMethod(value, row, column) {
                const property = column.property
                return row[property] === value
            },
            // 勾选数据行的 Checkbox 时触发的事件
            onselect(selection, row) {
                this.$emit('select', selection, row)
            },
            // 用户手动勾选全选 Checkbox 时触发的事件
            selectAll(selection) {
                this.$emit('select-all', selection)
            },
            // 当选择项发生变化时会触发该事件
            selectChange(selection) {
                this.$emit('selection-change', selection)
            },
            // 切换表格分页时会触发的事件
            handlePageChange(page) {
                this.$emit('page-change', page)
            },
            // 切换表格每页显示条数时会触发的事件
            limitChange(limit) {
                this.$emit('page-limit-change', limit)
            },
            handleSettingChange({ fields, size }) {
                this.setting.size = size
                const newsFields = []
                const selectedFields = this.columns
                fields.forEach(item => {
                    const currentIndex = selectedFields.find(field => field.key === item.key)
                    if (currentIndex) {
                        newsFields.push(currentIndex)
                        return
                    }
                    newsFields.push(item)
                })
                // 取数组最后一个数
                const [first] = [...selectedFields].reverse()
                if (first.key === 'operation') {
                    newsFields.push(first)
                }
                this.setting.selectFields = [...newsFields]
                this.setting.selectFields = [...this.setting.selectFields]
                // 构造高级搜索的数据配置
                const adnvancedWidget = this.setting.selectFields.map(item => {
                    return {
                        name: item.key,
                        label: item.label,
                        ...item.conditionAttr
                    }
                })
                this.$emit('handleSettingChange', adnvancedWidget, this.setting.selectFields)
            },
            // 表格的筛选条件发生变化的时候触发
            filterChange(key) {
                this.$emit('filter-change', key)
            },
            // 表格的排序条件发生变化的时候会触发
            sortChange({ column, prop, order }) {
                this.$emit('sort-change', { column, prop, order })
            }
        }
    }
</script>

<style scoped lang="scss">
.table-container {
    background: #fff;
    border: 1px solid #dfe0e5;
}
/deep/ .bk-table::before {
    height: 0;
}
/deep/ .setting-title {
    text-align: right;
    > label {
        float: left !important;
    }
}
/deep/.bk-table-scrollable-x {
    .bk-table-body-wrapper {
        &::-webkit-scrollbar {
            /*滚动条整体样式*/
            width: 10px;  /*高宽分别对应横竖滚动条的尺寸*/
            height: 8px;
            border: none;
        }
        &::-webkit-scrollbar-thumb {
            /*滚动条里面小方块*/
            border-radius: 10px;
            box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
            background: #D2D2D2;
        }
        &::-webkit-scrollbar-track {
            /*滚动条里面轨道*/
            border-radius: 15px;
            background: #ededed;
        }
    }
}
.bk-table-setting-content {
    /deep/ .content-title {
        padding-bottom: 5px;
        margin-bottom: 10px;
        border-bottom: 1px solid #eee;
    }
    /deep/ .content-line-height {
        display: none;
    }
    /deep/ .content-options {
        button {
            border-radius: 2px;
            min-width: 60px;
            letter-spacing: 2px;
        }
    }
}
/deep/ .bk-table-fixed {
    th {
        border: none !important;
    }
}
/deep/ .bk-table::before {
    height: 0;
}
/deep/ .bk-table-body {
    tr:last-child {
        td {
            //border-bottom: 0px;
        }
    }
}
/deep/ .bk-table-column-setting {
    border-left: 0;
}
</style>
