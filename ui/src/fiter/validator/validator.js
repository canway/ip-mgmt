/**
* This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
* Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
* Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. dengyuliu, 15927493530
* This file is part of IP management center.
* IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
* IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
*/
// 表单验证
import Vue from 'vue'
import VeeValidate, {Validator} from 'vee-validate'
import VueI18n from 'vue-i18n'
import zh_CN from 'vee-validate/dist/locale/zh_CN'

// 国际化
Vue.use(VueI18n)
const i18n = new VueI18n({
    locale: 'zh_CN'
})

// 自定义validate
const Dictionary = {
    zh_CN: {
        messages: {
            required: field => '请输入' + field
        },
        attributes: {
            name: '账号'
        }
    }
}

// 自定义validate error 信息
Validator.localize(Dictionary)

// 自定义表单
Validator.extend('phone', {
    messages: {
        zh_CN: field => field + '必须是11位手机号码',
    },
    validate: value => {
        return value.length == 11 && /^((13|14|15|17|18)[0-9]{1}\d{8})$/.test(value)
    }
})

Vue.use(VeeValidate, {
    i18n,
    i18nRootKey: 'validation',
    dictionary: {
        zh_CN
    },
    fieldsBagName: 'fieldBags' // fields重命名，和ElementUI冲突
})
