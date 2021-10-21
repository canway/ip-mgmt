/**
* This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
* Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
* Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. dengyuliu, 15927493530
* This file is part of IP management center.
* IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
* IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
*/
/**
 * @file 替换 asset css 中的 STATIC_URL，__webpack_public_path__ 没法解决 asset 里静态资源的 url
 * @author
 */

const path = require('path')

class ReplaceTemplateStaticUrlPlugin {
    apply(compiler, callback) {
        // emit: 在生成资源并输出到目录之前
        compiler.hooks.emit.tapAsync('ReplaceCSSStaticUrlPlugin', (compilation, callback) => {
            const assets = Object.keys(compilation.assets)
            const assetsLen = assets.length
            for (let i = 0; i < assetsLen; i++) {
                const fileName = assets[i]
                if (path.basename(fileName) === 'index.prod.html') {
                    const asset = compilation.assets[fileName]
                    const minifyFileContent = asset.source().toString().replace(
                        /.\/static\//g,
                        () => '{{STATIC_URL}}'
                    )
                    console.log(path.basename(fileName))
                    // 设置输出资源
                    compilation.assets[fileName] = {
                        // 返回文件内容
                        source: () => minifyFileContent,
                        // 返回文件大小
                        size: () => Buffer.byteLength(minifyFileContent, 'utf8')
                    }
                }
            }

            callback()
        })
    }
}

module.exports = ReplaceTemplateStaticUrlPlugin
