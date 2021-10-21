/**
* This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
* Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
* Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. dengyuliu, 15927493530
* This file is part of IP management center.
* IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
* IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
*/
// 全局mixins
export const globalMixins = {
    methods: {
        // 根据表单内容调整底部按钮的位置
        settingPosition() {
            const slider = document.getElementsByClassName('bk-sideslider-wrapper')[0]
            const content = document.getElementsByClassName('bk-sideslider-content')[0]
            const footer = document.getElementsByClassName('bk-sideslider-footer')[0]
            if (slider && content && footer) {
                if (slider.offsetHeight - 114 > content.offsetHeight) {
                    footer.style.backgroundColor = 'transparent'
                    footer.style.paddingLeft = '125px'
                } else {
                    footer.style.backgroundColor = '#fafbfd'
                    footer.style.paddingLeft = '0'
                }
            }
        },
        _warnMessage(message, delay = 3000) {
            this.$bkMessage({
                message,
                delay,
                theme: 'warning'
            })
        },
        _errorMessage(message, delay = 3000) {
            this.$bkMessage({
                message,
                delay,
                theme: 'error'
            })
        },
        _successMessage(message, delay = 3000) {
            this.$bkMessage({
                message,
                delay,
                theme: 'success'
            })
        }
    }
}
