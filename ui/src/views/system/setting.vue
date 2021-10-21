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
    <div class="wrapper">
        <div class="content-wrapper logo-set">
            <h2>Logo设置</h2>
            <div>
                <div style="float: left;">
                    <bk-upload
                        :files="file"
                        :theme="'picture'"
                        :with-credentials="true"
                        :custom-request="handleUpload"
                        :handle-res-code="handleRes"
                        :multiple="false"
                        :url="'0'"
                        v-if="showUpload"
                    ></bk-upload>
                </div>
                <div style="float: left;margin-left: 46px; display: flex; align-items: center; height: 100px;">
                    <bk-button :theme="'primary'" :title="'确认上传'" style="margin-right: 8px;" @click="uploadLogo"
                        :loading="isConfirm2" :disabled="!fileParams">确认上传
                    </bk-button>
                    <bk-button :theme="'default'" :title="'恢复默认'" style="margin-right: 8px;" @click="initLogo">恢复默认
                    </bk-button>
                    <bk-icon type="info-circle-shape" style="color: #3A84FF;" />
                    <span style="margin-left: 10px;">仅支持上传png、jpg、svg或jpeg格式的图片、图片宽高比接近1:1最佳</span>
                </div>
            </div>
        </div>
        <div class="content-wrapper system-set" v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <h2>系统设置</h2>
            <bk-form :label-width="200" :model="formData" ref="formData">
                <bk-form-item label="IP在线状态检测周期(天)" desc="IP地址在线检测的周期设置" :desc-type="'icon'">
                    <bk-input :clearable="true" type="number" v-model="formData.ping_check" class="input-form"
                        :disabled="!isEdit"></bk-input>
                </bk-form-item>
                <bk-form-item label="IP异常规则启用" :property="'name'">
                    <div style="display: flex;transform: translateX(20px) translateY(-10px);">
                        <div style="margin-right: 20px;">
                            <div style="margin-top: 10px;">
                                <bk-checkbox v-model="rule.rule1" :disabled="!isEdit">未分配但在线</bk-checkbox>
                            </div>
                            <div style="margin-top: 10px;">
                                <bk-checkbox v-model="rule.rule2" :disabled="!isEdit">已分配但离线超过时限</bk-checkbox>
                            </div>
                            <div style="margin-top: 10px;">
                                <bk-checkbox v-model="rule.rule6" :disabled="!isEdit">未分配但CMDB中存在</bk-checkbox>
                            </div>
                        </div>
                    </div>
                </bk-form-item>
                <bk-form-item>
                    <bk-button :theme="'primary'" :title="'修改'" v-if="!isEdit" @click="toEdit"
                        style="margin-left: 20px;">修改
                    </bk-button>
                    <bk-button :theme="'primary'" :title="'确认'" v-if="isEdit" @click.stop.prevent="submit"
                        :loading="isConfirm" style="margin-left: 20px;">确认
                    </bk-button>
                    <bk-button :title="'取消'" v-if="isEdit" @click="onCancel">取消</bk-button>
                </bk-form-item>
            </bk-form>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'system-setting',
        data() {
            return {
                showUpload: true,
                limit: 1,
                file: [
                    {
                        name: '',
                        status: 'done',
                        url: window.siteUrl + 'sys/get_logo/?random=' + Math.random()
                    }
                ],
                fileParams: null,
                isEdit: false,
                isConfirm: false,
                isConfirm2: false,
                formData: {
                    ip_net_threshold: '',
                    ip_offline: '',
                    ip_pool_threshold: '',
                    ip_release: '',
                    ip_remind: '',
                    ping_check: '',
                    abnormal_rules: []
                },
                ipPoolThreshold: '',
                ipNetThreshold: '',
                files: '',
                loading: false,
                rule: {
                    rule1: false,
                    rule2: false,
                    rule3: false,
                    rule4: false,
                    rule5: false,
                    rule6: false
                }
            }
        },
        mounted() {
            this.fetchData()
        },
        methods: {
            handleRes(response) {
                if (response.id) {
                    return true
                }
                return false
            },
            async fetchData() {
                this.loading = true
                try {
                    const res = await this.$api.searchSys()
                    if (res.result) {
                        for (const item of res.data.results) {
                            if (item.key === 'abnormal_rules') {
                                this.formData.abnormal_rules = item.extra
                                for (const item of this.formData.abnormal_rules) {
                                    this.rule[item.rule_code] = item.enabled
                                }
                            } else {
                                this.formData[item.key] = item.value
                            }
                        }
                        this.ipPoolThreshold = this.formData.ip_pool_threshold * 100
                        this.ipNetThreshold = this.formData.ip_net_threshold * 100
                    } else {
                        this._errorMessage(res.message)
                    }
                } finally {
                    this.loading = false
                }
            },
            submit() {
                this.isConfirm = true
                for (const item of this.formData.abnormal_rules) {
                    item.enabled = this.rule[item.rule_code]
                }
                this.formData.ip_pool_threshold = this.ipPoolThreshold / 100
                this.formData.ip_net_threshold = this.ipNetThreshold / 100
                this.$refs.formData.validate().then(async validator => {
                    try {
                        const res = await this.$api.updateSys(this.formData)
                        if (res.result) {
                            this._successMessage('更新成功')
                            this.fetchData()
                            this.isEdit = false
                        } else {
                            this._errorMessage(res.message)
                        }
                    } finally {
                        this.isConfirm = false
                    }
                })
            },
            toEdit() {
                this.isEdit = true
                this.editForm = JSON.parse(JSON.stringify(this.formData))
            },
            onCancel() {
                this.formData = JSON.parse(JSON.stringify(this.editForm))
                this.isEdit = false
            },
            fileToBase64(file) {
                const reader = new FileReader()
                reader.readAsDataURL(file)
                return new Promise((resolve, reject) => {
                    reader.onload = function(e) {
                        if (this.result) {
                            resolve(this.result)
                        } else {
                            reject(new Error('转换预览图片失败'))
                        }
                    }
                })
            },
            handleUpload(el) {
                this.fileParams = el.fileObj.origin
                this.fileToBase64(el.fileObj.origin).then(res => {
                    this.file = [
                        {
                            name: 'image.png',
                            status: 'done',
                            url: res
                        }
                    ]
                    this.showUpload = false
                    this.$nextTick(() => {
                        this.showUpload = true
                    })
                })
            },
            uploadLogo() {
                const config = {
                    headers: {'Content-Type': 'multipart/form-data'}
                }
                const filetypearry = ['png', 'jpg', 'svg', 'jpeg']
                if ((this.fileParams.size / 1024 / 1024) < 50) {
                    let isqualified = true
                    for (let a = 0; a < filetypearry.length; a++) {
                        const finName = this.fileParams.name.split('.').slice(-1).toString()
                        if (filetypearry[a] === finName) {
                            isqualified = false
                            this.fileData = new FormData()
                            this.fileData.append('file', this.fileParams)
                            this.fileData.append('flag', true)
                            this.isConfirm2 = true
                            this.$api.updateLogo(this.fileData, config).then(res => {
                                if (res.result) {
                                    this._successMessage('上传成功')
                                    setTimeout(() => {
                                        window.location.reload()
                                    }, 80)
                                } else {
                                    this._errorMessage(res.message)
                                }
                            }).finally(() => {
                                this.isConfirm2 = false
                            })
                            break
                        }
                    }
                    if (isqualified) {
                        this.$message.error('请上传支持的文件格式(png,jpg,svg,jpeg)')
                    }
                } else {
                    this.$message.error('请上传50M大小以内的文件！')
                }
            },
            initLogo() {
                this.$bkInfo({
                    title: '确定恢复默认吗?',
                    confirmLoading: true,
                    confirmFn: async() => {
                        try {
                            const res = await this.$api.updateLogo()
                            if (res.result) {
                                this._successMessage('恢复成功')
                                window.location.reload()
                                return true
                            } else {
                                this._errorMessage(res.message)
                                return true
                            }
                        } catch (e) {
                            return false
                        }
                    }
                })
            }
        }
    }
</script>

<style scoped lang="scss">
    .wrapper {
        padding: 20px 10px;

        .logo-set {
            height: 170px;
        }

        .system-set {
            height: 570px;
            margin-top: 20px;

            .input-form {
                width: 640px;
                margin-left: 20px;
            }

            .input-form2 {
                width: 200px;
                margin-left: 20px;
            }
        }

        .content-wrapper {
            background: #fff;
            padding: 20px;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
            border-radius: 2px;
            box-sizing: border-box;
            color: #63656E;
            letter-spacing: 0;

            h2 {
                margin: 0 0 15px 0;
                font-size: 14px;
                line-height: 22px;
                font-weight: 600;
            }
        }
    }

    /deep/ .bk-form .bk-label {
        padding-right: 0 !important;
    }
</style>
