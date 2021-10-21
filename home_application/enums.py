# -*- coding: utf-8 -*-
"""
This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. jackliu, 15927493530
This file is part of IP Management Center.
IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
"""  # noqa
from home_application.models import Apply, Ips

APPLY_WAY_DICT = dict(Apply.APPLY_WAY)
ALLOCATE_STATUS_DICT = dict(Ips.ALLOCATE_STATUS)

IP_CHILD_MANAGEMENT = "IP子网管理"
IP_ADDRESS_MANAGEMENT = "IP地址管理"
IP_ADDRESS_POOL_MANAGEMENT = "IP地址池管理"

UNASSIGNED_ONLINE = "rule1"
ASSIGNED_EXCEEDED_TIME = "rule2"
UNASSIGNED_BUT_EXISTS_CMDB = "rule6"
RULE_CODE = (
    (UNASSIGNED_ONLINE, "未分配但在线"),
    (ASSIGNED_EXCEEDED_TIME, "已分配但离线超过时限"),
    (UNASSIGNED_BUT_EXISTS_CMDB, "未分配但CMDB中存在"),
)

# 离线IP地址title
OFFLINE_IP_ADDRESS_TITLE = {
    "remark": "备注",
    "offline_days": "离线时间",
    "ip_pool": "地址池名称",
    "ip_net": "IP子网",
    "name": "名称",
    "description": "描述",
    "ip": "ip",
    "allocate_at": "分配时间",
    "expired_at": "过期时间",
    "allocate_status": "分配状态",
    "allocate_way": "分配方式",
    "offline_at": "离线时间",
    "scan_at": "扫描时间",
    "online_status": "在线状态",
    "reserve_status": "保留状态",
    "business_system": "业务系统",
    "is_cmdb_sync": "是否是cmdb同步",
    "recycle_waiting_days": "回收等待天数",
    "owner": "所属者",
    "bk_cloud_id": "云区域ID",
    "gateway": "网关",
    "dns": "DNS服务器",
}

# IP地址title
IP_ADDRESS_TITLE = {
    "ip_pool": "地址池名称",
    "ip_net_name": "IP子网",
    "name": "名称",
    "description": "描述",
    "remark": "备注",
    "ip": "ip",
    "allocate_at": "分配时间",
    "expired_at": "过期时间",
    "allocate_status": "分配状态",
    "allocate_way": "分配方式",
    "offline_at": "离线时间",
    "scan_at": "扫描时间",
    "online_status": "在线状态",
    "reserve_status": "保留状态",
    "business_system": "业务系统",
    "is_cmdb_sync": "是否是cmdb同步",
    "recycle_waiting_days": "回收等待天数",
    "owner": "所属者",
    "bk_cloud_id": "云区域ID",
    "gateway": "网关",
    "dns": "DNS服务器",
}

# 导入IP分配模板title
IMPORT_IP_ASSIGNMENT_TEMPLATE_TITLE = {
    "pool_name": "IP地址池名称(pool_name)",
    "ip_net": "[必填]IP子网(ip_net)",
    "apply_ips": "[必填]待分配IP(apply_ips)，多个用,隔开",
    "business_system": "业务系统(business_system)",
    "owner": "运维人员(owner)",
    "expired_at": "[必填]过期时间(expired_at)，如2021-01-01",
    "remark": "申请理由(remark)",
}

# 异常IP地址title
ABNORMAL_IP_ADDRESS_TITLE = {
    "abnormal_code": "异常编码",
    "remark": "备注",
    "offline_days": "离线时间",
    "ip_pool": "地址池名称",
    "ip_net": "IP子网",
    "name": "名称",
    "description": "描述",
    "ip": "ip",
    "allocate_at": "分配时间",
    "expired_at": "过期时间",
    "allocate_status": "分配状态",
    "allocate_way": "分配方式",
    "offline_at": "离线时间",
    "scan_at": "扫描时间",
    "online_status": "在线状态",
    "reserve_status": "保留状态",
    "business_system": "业务系统",
    "is_cmdb_sync": "是否是cmdb同步",
    "recycle_waiting_days": "回收等待天数",
    "owner": "所属者",
    "bk_cloud_id": "云区域ID",
    "gateway": "网关",
    "dns": "DNS服务器",
}

# IP子网title
IP_SUBNET_TITLE = {
    "ip_pool_name": "地址池名称",
    "ip_net": "IP子网",
    "bk_cloud_id": "云区域",
    "gateway": "网关",
    "dns": "DNS服务器",
    "vlan_id": "VLAN ID",
    "ip_count": "IP数",
    "reserve_ip_count": "保留IP数",
    "usage_rate": "使用率",
}

# IP地址池部分title
IP_POOL_PART_TITLE = {
    "name": "地址池名称",
    "net_count": "子网数量",
    "ip_count": "IP数",
    "reserve_ip_count": "保留IP数",
    "usage_rate": "使用率",
    "create_by": "添加者",
    "create_at": "添加时间",
}

# IP地址池导出模板title
IP_POOL_EXPORT_TEMPLATE_TITLE = {
    "name": "[必填]地址池名称(pool_name)",
    "ip_net": "[必填]IP子网(ip_net)",
    "bk_cloud_id": "[必填]云区域(bk_cloud_id)",
    "gateway": "[必填]网关(gateway)",
    "dns": "[必填]dns(dns)",
    "description": "描述(description)",
    "remark": "备注(remark)",
    "VLANID": "VLANID(vlan_id)",
}
