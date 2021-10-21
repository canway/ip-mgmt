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
from home_application.exceptions import IPPoolCreateException
from home_application.models import IpNet, Ips
from home_application.utilities.ip_helper.ip_tools import check_ip_net, check_net_cover, dns_error, gateway_error


def check_ip_net_normal(exist_ip_net, ip_net, gateway, dns):
    try:
        new_ip_net = check_ip_net(ip_net)
    except ValueError:
        raise IPPoolCreateException("{} 不是正确的IP子网".format(ip_net))
    if not check_net_cover(exist_ip_net, new_ip_net):
        raise IPPoolCreateException("子网段:{}跟当前已有子网段有重叠部分，请检查！".format(ip_net))
    if gateway_error(ip_net, gateway):
        raise IPPoolCreateException("网关:{}不合法".format(gateway))
    if dns_error(dns):
        raise IPPoolCreateException("dns:{} 不合法".format(dns))
    if new_ip_net in exist_ip_net or ip_net in exist_ip_net:
        raise IPPoolCreateException("该IP子网 {}已经存在".format(ip_net))


def create_by_ip_pool(exist_ip_net, **kwargs):
    ip_net = kwargs.get("ip_net")
    check_ip_net_normal(exist_ip_net, ip_net, kwargs["gateway"], kwargs["dns"])
    ip_net_instance = IpNet(**kwargs)
    return ip_net_instance


def update_by_ip_pool(db_update_map, exist_ip_net, **kwargs):
    ip_net = kwargs.get("ip_net")
    check_ip_net_normal(exist_ip_net, ip_net, kwargs["gateway"], kwargs["dns"])
    ip_net_obj = db_update_map.get(kwargs["id"])
    ip_net_obj.ip_net = ip_net
    ip_net_obj.bk_cloud_id = kwargs["bk_cloud_id"]
    ip_net_obj.gateway = kwargs["gateway"]
    ip_net_obj.dns = kwargs["dns"]
    ip_net_obj.custom_attr = kwargs["custom_attr"]
    ip_net_obj.vlan_id = kwargs["vlan_id"]
    return ip_net_obj


def create_ip_net(ip_nets, ip_pool, username, exist_ip_net):
    error_message = []
    ip_net_instance_list = []
    for item in ip_nets:
        param = {
            "bk_cloud_id": item.get("bk_cloud_id", ""),
            "gateway": item.get("gateway", ""),
            "dns": item.get("dns", ""),
            "ip_net": item.get("ip_net", ""),
            "vlan_id": item.get("vlan_id", ""),
            "custom_attr": item.get("custom_attr", {}),
            "ip_pool_id": ip_pool.id,
            "create_by": username,
            "description": item.get("description", ""),
            "remark": item.get("remark", ""),
        }
        try:
            ip_net_obj = create_by_ip_pool(exist_ip_net, **param)
        except IPPoolCreateException as e:
            error_message.append(str(e))
        else:
            exist_ip_net.append(ip_net_obj.ip_net)
            ip_net_instance_list.append(ip_net_obj)
    return ip_net_instance_list, error_message


def update_ip_net(update_list, db_update_map, exist_ip_net):
    error_message = []
    ip_net_instance_list = []
    for ip_net in update_list:
        try:
            ip_net_obj = update_by_ip_pool(db_update_map, exist_ip_net, **ip_net)
        except IPPoolCreateException as e:
            error_message.append(str(e))
        else:
            ip_net_instance_list.append(ip_net_obj)
            exist_ip_net.append(ip_net_obj.ip_net)

    return ip_net_instance_list, error_message


def delete_ip_net(ip_pool, del_ip_nets: list):
    error_messages = []
    exclude_ip_nets = list(
        Ips.objects.filter(
            allocate_status__in=[Ips.DISTRIBUTION, Ips.WAIT_RECOVERY],
            ip_net__ip_pool_id=ip_pool.id,
        )
        .values_list("ip_net_id", flat=True)
        .distinct()
    )
    delete_message = "子网【{}】下还存在已分配或待回收的IP，不允许删除"
    del_ip_net_ids = []
    for ip_net in del_ip_nets:
        if ip_net["ip_net"] in exclude_ip_nets:
            error_messages.append(delete_message.format(ip_net["ip_net"]))
        else:
            del_ip_net_ids.append(ip_net["id"])
    return del_ip_net_ids, error_messages
