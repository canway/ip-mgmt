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
    <bk-dialog v-model="visible" title="导入地址池或子网"
        class="importDialog"
        :mask-close="false"
        :show-mask="true"
        :draggable="false"
        :loading="loading"
        :header-position="'left'"
        :width="480"
        :auto-close="false"
        @confirm="onConfirm">
        <div class="upload-wrapper">
            <bk-upload
                :tip="'只允许上传csv,xlsx的文件'"
                :with-credentials="true"
                :custom-request="handleUpload"
                :limit="1"
                :ext-cls="'upload-wrapper'"
                :url="'0'"
                :accept="'.csv, .xlsx'"
            ></bk-upload>
            <span class="template-file" @click="toDownload">模板文件.xlsx</span>
        </div>
        <p v-if="file" class="file-list-wrapper">
            {{file.name}}
            <i class="bk-icon icon-close" @click="handleClose"></i>
        </p>
    </bk-dialog>
</template>

<script>
    export default {
        name: 'import-distribute',
        data() {
            return {
                visible: false,
                file: null,
                loading: false
            }
        },
        methods: {
            showDialog() {
                this.visible = true
            },
            onConfirm() {
                this.loading = true
                if (!this.file) {
                    this._warnMessage('请先选择文件再上传')
                    this.loading = false
                    return false
                }
                const _formData = new FormData()
                _formData.append('file', this.file)
                this.$api.import_ip_pool(_formData).then(res => {
                    if (res.result) {
                        this.$emit('ok-confirm', true)
                        this._successMessage('导入成功')
                        this.visible = false
                    } else {
                        this._errorMessage(res.message)
                        this.visible = false
                    }
                }).catch(() => {
                    this._errorMessage('导入失败,请稍后再试')
                }).finally(() => {
                    this.loading = false
                })
            },
            handleUpload(el) {
                this.file = el.fileObj.origin
            },
            handleClose() {
                this.file = ''
            },
            toDownload() {
                const url = window.siteUrl + 'ip_pool/download_template/'
                window.open(url)
            }
        }
    }
</script>

<style scoped lang="scss">
/deep/ .bk-upload.draggable .file-wrapper {
    background: #FAFBFD;
}
/deep/.upload-wrapper {
    .all-file {
        display: none;
    }
}
.upload-wrapper {
    position: relative;
    .template-file {
        cursor: pointer;
        color: #3A84FF;
        font-size: 14px;
        position: absolute;
        bottom: 0;
        right: 0;
    }
}
.file-list-wrapper {
    margin-top: 15px;
    font-size: 12px;
    color: #3A84FF;
    width: 100%;
    position: relative;
    >i {
        color: #3A84FF;
        position: absolute;
        right: 3px;
        top: 3px;
        cursor: pointer;
    }
}
/deep/ .bk-dialog-body {
    position: relative;
}
</style>
