/**
* This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
* Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
* Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. dengyuliu, 15927493530
* This file is part of IP management center.
* IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
* IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
*/
import axios from 'axios'

axios.defaults.baseURL = window.siteUrl
axios.defaults.withCredentials = true
axios.defaults.timeout = 200000
axios.defaults.crossDomain = true

axios.interceptors.request.use((config) => {
    config.headers['X-Requested-With'] = 'XMLHttpRequest'
    const name = window.CSRF_COOKIE_NAME || 'csrftoken'
    let cookieValue = window.CSRFTOKEN
    if (cookieValue === '' && document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    config.headers['X-CSRFToken'] = cookieValue
    return config
})

axios.interceptors.response.use(response => {
    if (response.status === 502) {
        return {
            code: response.status,
            message: '平台接口异常',
            result: false
        }
    }
    if (response.status > 300 || response.status < 200) {
        return {
            code: response.status,
            message: response.data.message,
            result: false
        }
    }
    return response.data
}, error => {
    return {
        code: 500,
        message: error.response.data.message,
        error: error,
        result: false
    }
})

// 发送请求 (接口路径，参数，请求配置)
export function post(url, params, config) {
    return new Promise((resolve, reject) => {
        axios.post(url, params, config).then(
            res => {
                resolve(res)
            },
            err => {
                reject(err)
            }
        )
            .catch(err => {
                reject(err)
            })
    })
}

export function get(url, params, config) {
    return new Promise((resolve, reject) => {
        axios.get(url, {
            params: params,
            config: config
        })
            .then(res => {
                resolve(res)
            })
            .catch(err => {
                reject(err)
            })
    })
}

export function put(url, params, config) {
    return new Promise((resolve, reject) => {
        axios.put(url, params, config).then(
            res => {
                resolve(res)
            },
            err => {
                reject(err)
            }
        )
            .catch(err => {
                reject(err)
            })
    })
}

export function deletes(url, params, config) {
    return new Promise((resolve, reject) => {
        axios.delete(url, {
            params: params,
            config: config
        })
            .then(res => {
                resolve(res)
            })
            .catch(err => {
                reject(err)
            })
    })
}

export function patch(url, params = {}) {
    return new Promise((resolve, reject) => {
        axios.patch(url, params)
            .then(res => {
                resolve(res)
            })
            .catch(err => {
                reject(err)
            })
    })
}
export const reUrl = ''
