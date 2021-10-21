/**
* This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
* Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
* Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. dengyuliu, 15927493530
* This file is part of IP management center.
* IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
* IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
*/
import {get, post, deletes, put, reUrl} from '../axiosconfig/axiosconfig'

export default {
    // 查询IP地址池
    searchPool: function(params) {
        return get(reUrl + 'ip_pool/', params)
    },
    // IP地址池详情
    poolDetail: function(params) {
        return get(reUrl + `ip_pool/${params.id}/`)
    },
    // 新增地址池
    modify_ip_pool: function(params) {
        return put(reUrl + `ip_pool/${params.id}/`, params)
    },
    // 编辑地址池
    create_ip_pool: function(params) {
        return post(reUrl + 'ip_pool/', params)
    },
    // 删除地址池
    delete_ip_pool: function(params) {
        return deletes(reUrl + `ip_pool/${params.id}/`)
    },
    // 查询IP子网
    search_ip_net: function(params) {
        return get(reUrl + 'ip_net/', params)
    },
    // IP子网详情
    poolNetDetail: function(params) {
        return get(reUrl + `ip_net/${params.id}/`)
    },
    // 新增IP子网
    add_ip_pool: function(params) {
        return post(reUrl + 'ip_net/batch_create/', params)
    },
    // 修改IP子网
    update_ip_pool: function(params) {
        return put(reUrl + `ip_net/${params.id}/`, params)
    },
    // 删除IP子网
    delete_ip_net: function(params) {
        return deletes(reUrl + `ip_net/${params.id}/`)
    },
    // 查询ip
    search_ip: function(params) {
        return get(reUrl + 'ip/', params)
    },
    // ip检测
    status_check: function(params) {
        return get(reUrl + 'ip/status_check/', params)
    },
    // IP:批量修改
    ip_batch_update: function(params) {
        return post(reUrl + 'ip/batch_update/', params)
    },
    // IP:批量回收
    ip_recycle: function(params) {
        return post(reUrl + 'ip/recycle/', params)
    },
    // IP:新增分配
    ip_apply: function(params) {
        return post(reUrl + 'apply/', params)
    },
    // IP:检测IP是否在子网下
    ip_check: function(params) {
        return post(reUrl + 'ip/check_ip/', params)
    },
    // IP:新增保留
    ip_allocation: function(params) {
        return post(reUrl + 'ip/import_ip_allocation/', params)
    },
    // IP:新增保留
    ip_reserve: function(params) {
        return post(reUrl + 'ip/batch_reserve/', params)
    },
    // 搜索离线白名单
    search_offlineWhite: function(params) {
        return get(reUrl + 'offline_except/', params)
    },
    // 新增ip到离线白名单
    add_offlineWhite: function(params) {
        return post(reUrl + 'offline_except/add/', params)
    },
    // 删除单个离线白名单
    delete_single_offlineWhite: function(params) {
        return deletes(reUrl + `offline_except/${params.id}/`)
    },
    // 删除多个离线白名单
    delete_multi_offlineWhite: function(params) {
        return post(reUrl + 'offline_except/delete/', params)
    },
    // 搜索异常IP清单
    search_ip_abnormal: function(params) {
        return get(reUrl + 'ip_abnormal/', params)
    },
    // 添加到离线白名单
    add_offline_except: function(params) {
        return post(reUrl + 'ip_abnormal/add_offline_except/', params)
    },
    // 确认异常IP清单
    confirm_ip_abnormal: function(params) {
        return post(reUrl + 'ip_abnormal/confirm/', params)
    },
    // 导入子网/地址池
    import_ip_pool: function(params) {
        return post(reUrl + 'ip_pool/import_ip_pool/', params)
    }
}
