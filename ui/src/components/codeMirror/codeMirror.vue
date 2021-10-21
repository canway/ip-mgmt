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
    <div id="codeMirror">
        <codemirror style="height: auto;" v-model="codeData" :options="cmOptions"></codemirror>
    </div>
</template>

<script>
    import { codemirror } from 'vue-codemirror'
    import 'codemirror/lib/codemirror.css'
    import 'codemirror/mode/javascript/javascript.js'
    import 'codemirror/mode/python/python.js'
    import 'codemirror/theme/base16-dark.css'
    import 'codemirror/theme/base16-light.css'
    import 'codemirror/theme/monokai.css'
    import 'codemirror/addon/edit/closebrackets.js'
    import 'codemirror/mode/clike/clike.js'
    import 'codemirror/addon/edit/matchbrackets.js'
    import 'codemirror/addon/comment/comment.js'
    import 'codemirror/addon/dialog/dialog.js'
    import 'codemirror/addon/dialog/dialog.css'
    import 'codemirror/addon/search/searchcursor.js'
    import 'codemirror/addon/search/search.js'
    import 'codemirror/keymap/emacs.js'

    export default {
        /**
         * 参考: https://codemirror.net/
         * @param {string} code 展示代码
         * @param {string} mode 代码类型(js和python) 'text/javascript' 和 'text/x-python'
         * @param {string} theme 编码区风格 'base16-dark', 'base16-light', 'monokai'
         * 更多支持语言和风格请参考官方文档，引入即可
         * */
        name: 'c-w-code-mirror',
        components: {
            codemirror
        },
        props: {
            code: {
                type: String,
                default: ''
            },
            mode: {
                type: String,
                default: 'text/javascript'
            },
            theme: {
                type: String,
                default: 'base16-dark'
            }
        },
        data() {
            return {
                codeData: this.code,
                cmOptions: {
                    tabSize: 4,
                    mode: this.mode,
                    theme: this.theme,
                    lineNumbers: true,
                    line: true,
                    lineWrapping: true, // 代码折叠
                    foldGutter: true,
                    matchBrackets: true, // 括号匹配
                    autoCloseBrackets: true,
                    styleActiveLine: true,
                    keyMap: 'emacs'
                }
            }
        },
        watch: {
            codeData() {
                this.$emit('changeData', this.codeData)
            }
        }
    }
</script>
