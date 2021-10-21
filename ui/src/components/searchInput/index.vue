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
    <div class="header-search-input">
        <bk-input
            :placeholder="placeholder"
            :right-icon="!isShow ? '' : 'bk-icon icon-search'"
            v-model="textValue"
            @enter="onSearch"
            @focus="onFocus"
            @blur="onBlur"
            @change="onChange"
            @right-icon-click="onSearch">
        </bk-input>
        <bk-icon v-if="!isShow && textValue" type="close-circle-shape" @click="onClear" />
    </div>
</template>

<script>
    export default {
        name: 'com-input',
        model: {
            props: 'value',
            event: 'change'
        },
        props: {
            value: {
                type: String
            },
            placeholder: {
                type: String,
                default: ''
            }
        },
        data() {
            return {
                isShow: false,
                textValue: ''
            }
        },
        watch: {
            value: {
                handler(value) {
                    this.textValue = value
                }
            }
        },
        mounted() {
            this.textValue = this.value
        },
        methods: {
            onFocus() {
                setTimeout(() => {
                    this.isShow = true
                }, 300)
            },
            onBlur() {
                setTimeout(() => {
                    this.isShow = false
                }, 300)
            },
            onChange(value) {
                this.$emit('change', this.textValue)
            },
            onSearch() {
                this.$emit('search', this.textValue)
            },
            onClear() {
                this.textValue = ''
                this.$emit('change', this.textValue)
            }
        }
    }
</script>

<style scoped lang="scss">
.header-search-input {
    width: 300px;
    display: inline-block;
    position: relative;
    .bk-input-text {
        width: 100%;
    }
    /deep/ i {
        cursor: pointer;
    }
    >i {
        position: absolute;
        right: 10px;
        top: 10px;
        color: #c8cadb;
    }
}
</style>
