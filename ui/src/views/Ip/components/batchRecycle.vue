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
    <bk-dialog v-model="visible" title="批量回收"
        class="recycleDialog"
        :mask-close="!isConfirm"
        :show-mask="true"
        :draggable="false"
        :header-position="'left'"
        :width="480"
        :auto-close="false"
        :loading="isConfirm"
        @confirm="onConfirm">
        <div class="content-row">
            <label>已选择IP</label>
            <div class="ip-list">
                <p v-for="(item, index) in selectedRow" :key="index">
                    <span>{{ item.ip }}</span>
                    <bk-icon type="close" @click="toRemove(item)" />
                </p>
            </div>
        </div>
        <div class="content-row">
            <label>回收等待期</label>
            <div class="recycle-day">
                <bk-input :clearable="true"
                    type="number"
                    :min="1"
                    style="width: 70%;"
                    :precision="0"
                    v-model="numberInputValue">
                </bk-input>
                <span>天</span>
            </div>
        </div>
    </bk-dialog>
</template>

<script>
    export default {
        name: 'batch-recycle',
        props: {
            selected: {
                type: Array,
                default: () => {
                }
            }
        },
        data() {
            return {
                visible: false,
                selectedRow: [],
                numberInputValue: 15,
                isConfirm: false
            }
        },
        mounted() {
        },
        methods: {
            showDialog() {
                this.visible = true
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
                    this.selectedRow = JSON.parse(JSON.stringify(this.selected)) || []
                })
            },
            async onConfirm() {
                this.isConfirm = true
                const _selectedIds = []
                this.selectedRow.forEach(row => {
                    _selectedIds.push(row.id)
                })
                try {
                    const res = await this.$api.ip_recycle({
                        selected_ids: _selectedIds,
                        waiting_days: this.numberInputValue
                    })
                    if (res.result) {
                        this._successMessage('回收成功')
                        this.$emit('ok-recycle', true)
                        this.visible = false
                    } else {
                        this._errorMessage(res.message)
                        this.visible = false
                    }
                } finally {
                    this.isConfirm = false
                }
            },
            toRemove(item) {
                const _select = this.selectedRow
                this.selectedRow = _select.filter((row) => item.id !== row.id)
            }
        }
    }
</script>

<style scoped lang="scss">
    .content-row {
        display: flex;
        margin-bottom: 15px;

        label {
            width: 100px;
        }

        > div {
            flex: 1;

            &.ip-list {
                max-height: 200px;
                overflow-y: auto;
                background: #FAFBFD;
                box-sizing: border-box;
                padding: 0;

                p {
                    margin: 0 0 5px 0;
                    padding: 5px 10px;
                    position: relative;

                    i {
                        position: absolute;
                        right: 3px;
                        top: 30%;
                        display: none;
                    }

                    &:hover {
                        background: #E1ECFF;
                        cursor: pointer;

                        i {
                            color: #3A84FF;
                            display: inline-block;
                        }
                    }
                }
            }
        }
    }
</style>
