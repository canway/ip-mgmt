/**
* This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
* Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
* Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. dengyuliu, 15927493530
* This file is part of IP management center.
* IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
* IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
*/
import {deletes, get, patch, post, put, reUrl} from '../axiosconfig/axiosconfig'

export default {
    // 获取自定义属性
    searchCustom: function(params) {
        return get(reUrl + 'custom_attr/', params)
    },
    // 修改自定义属性
    editCustom: function(params) {
        return put(reUrl + `custom_attr/${params.id}/`, params)
    },
    // 新增自定义属性
    addCustom: function(params) {
        return post(reUrl + 'custom_attr/', params)
    },
    // 删除自定义属性
    deleteCustom: function(params) {
        return deletes(reUrl + `custom_attr/${params.id}/`, params)
    },
    // 获取CMDB同步模型
    searchCMDB: function(params) {
        return get(reUrl + 'cmdb/', params)
    },
    // 获取CMDB选择模型详情
    selectCMDBAttr: function(params) {
        return post(reUrl + 'cmdb/choice_attr/', params)
    },
    // 获取CMDB选择模型
    selectCMDB: function(params) {
        return get(reUrl + 'cmdb/choice_model/', params)
    },
    // 获取CMDB属性映射
    getCMDBMap: function(params) {
        return get(reUrl + `cmdb/${params.id}/get_attr/`, params)
    },
    // 修改CMDB属性映射
    updateCMDBMap: function(params) {
        return patch(reUrl + `cmdb/${params.id}/`, params)
    },
    // 新增CMDB模型
    addCMDB: function(params) {
        return post(reUrl + 'cmdb/', params)
    },
    // 删除CMDB模型
    deleteCMDB: function(params) {
        return deletes(reUrl + `cmdb/${params.id}/`, params)
    },
    // 获取同步周期
    searchCMDBPeriod: function(params) {
        return get(reUrl + 'cmdb/period/', params)
    },
    // 设置同步周期
    setCMDBPeriod: function(params) {
        return post(reUrl + 'cmdb/period/', params)
    },
    // 手动同步
    makeSync: function(params) {
        return get(reUrl + `make_sync/${params.id}/`, params)
    },
    // 获取系统设置
    searchSys: function(params) {
        return get(reUrl + 'sys/', params)
    },
    // 更新系统设置
    updateSys: function(params) {
        return post(reUrl + 'sys/edit_sys_setting/', params)
    },
    // 更新logo
    updateLogo: function(params) {
        return post(reUrl + 'sys/update_logo/', params)
    },
    // 查询同步记录
    searchSyncRecord: function(params) {
        return get(reUrl + 'sync_record/', params)
    },
    // 查询同步记录详情
    searchSyncDetail: function(params) {
        return get(reUrl + `sync_record/${params.id}/`, params)
    },
    // 查询操作记录
    searchOperationRecord: function(params) {
        return get(reUrl + 'operation_log/', params)
    }
}
