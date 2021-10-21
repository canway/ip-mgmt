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
from django.db import transaction

from home_application.celery_tasks import create_by_ip_nets
from home_application.enums import IP_ADDRESS_POOL_MANAGEMENT
from home_application.models import CustomAttr, IpNet, IpPools, OperationLog
from home_application.utilities.ip_helper.ip_tools import check_net_cover, dns_error, gateway_error


class ExcelImport(object):
    def __init__(self, table, username):
        self.table = table
        self.username = username
        self.pool_custom_attrs = list(CustomAttr.objects.filter(type=CustomAttr.IP_POOL).values_list("name", flat=True))
        self.net_custom_attrs = list(
            CustomAttr.objects.filter(type=CustomAttr.TET_WORK_SEGMENT).values_list("name", flat=True)
        )
        self.key_map = self.get_export_head(table.row_values(0))
        self.ip_net_map = {i.ip_net: i for i in IpNet.objects.all()}
        self.exist_nets = list(self.ip_net_map.keys())
        self.ip_pool_map = {i.name: i for i in IpPools.objects.all()}
        self.add_ip_pool_map = {}
        self.add_pools = []
        self.table_exist_pools = []
        self.net_pool_map = {}
        self.add_nets = []
        self.table_exist_nets = []
        self.data_exception = []

    def get_export_head(self, row_values):
        self.key_map = {}
        key_list = ["pool_name", "ip_net", "bk_cloud_id", "gateway", "dns", "vlan_id", "remark", "description"]
        for col_index in range(0, len(row_values)):
            key = row_values[col_index].split("(")[1].strip(")")
            if key in key_list:
                self.key_map[key] = col_index
            else:
                for pool_name in self.pool_custom_attrs:
                    if key == pool_name:
                        self.key_map[pool_name] = col_index
                for net_name in self.net_custom_attrs:
                    if key == net_name:
                        self.key_map[net_name] = col_index
        return self.key_map

    def import_excel_data(self):
        rows = self.table.nrows
        for row in range(1, rows):
            row_data = self.table.row_values(row)
            if (
                gateway_error(row_data[self.key_map["ip_net"]], row_data[self.key_map["gateway"]])
                or dns_error(row_data[self.key_map["dns"]])
                or not check_net_cover(self.exist_nets, row_data[self.key_map["ip_net"]])
            ):
                self.data_exception.append(str(row + 1))
                continue
            temp_pool = self.import_pool_data(row_data)
            if temp_pool is None:
                continue
            self.import_ip_net_data(temp_pool, row_data)
        self.set_import_data_to_db()
        add_net_list = IpNet.objects.filter(ip_net__in=[i.ip_net for i in self.add_nets])
        create_by_ip_nets.delay(add_net_list, self.username)
        return self.structure_message()

    def set_import_data_to_db(self):
        pool_name_list = [i.name for i in self.add_pools]
        with transaction.atomic():
            IpPools.objects.bulk_create(self.add_pools, batch_size=100)
            new_ip_pool_map = dict(IpPools.objects.filter(name__in=self.net_pool_map.keys()).values_list("name", "id"))
            for pool_name, net_list in self.net_pool_map.items():
                for net_obj in net_list:
                    net_obj.ip_pool_id = new_ip_pool_map[pool_name]
                self.add_nets.extend(net_list)
            IpNet.objects.bulk_create(self.add_nets, batch_size=100)
            OperationLog.objects.create(
                operate_type=OperationLog.ADD,
                operate_obj=IP_ADDRESS_POOL_MANAGEMENT,
                operator=self.username,
                operate_detail="从excel文件导入IP地址池:{}".format("、".join(pool_name_list)),
                result=True,
            )

    def import_ip_net_data(self, temp_pool, row_data):
        custom_n = [{"name": cus, "value": row_data[self.key_map[cus]]} for cus in self.net_custom_attrs]
        ip_net = row_data[self.key_map["ip_net"]]
        if ip_net in self.ip_net_map:
            self.table_exist_nets.append(ip_net)
            return
        if not check_net_cover(self.exist_nets, row_data[self.key_map["ip_net"]]):
            return
        temp_net = IpNet(
            ip_net=ip_net,
            bk_cloud_id=row_data[self.key_map["bk_cloud_id"]],
            gateway=row_data[self.key_map["gateway"]],
            dns=row_data[self.key_map["dns"]],
            vlan_id=row_data[self.key_map["vlan_id"]],
            custom_attr=custom_n,
        )
        if not temp_pool.id:
            self.net_pool_map.setdefault(temp_pool.name, []).append(temp_net)
        else:
            temp_net.ip_pool_id = temp_pool.id
            self.add_nets.append(temp_net)
        self.exist_nets.append(temp_net.ip_net)

    def import_pool_data(self, row_data):
        custom_p = [{"name": cus, "value": row_data[self.key_map[cus]]} for cus in self.pool_custom_attrs]
        pool_name = row_data[self.key_map["pool_name"]]
        if pool_name in self.ip_pool_map:
            temp_pool = self.ip_pool_map[pool_name]
        else:
            if pool_name in self.add_ip_pool_map:
                temp_pool = self.add_ip_pool_map[pool_name]
            else:
                temp_pool = IpPools(
                    name=row_data[self.key_map["pool_name"]],
                    status=IpPools.WAITING_ENABLE,
                    create_by=self.username,
                    update_by=self.username,
                    custom_attr=custom_p,
                )
                self.add_pools.append(temp_pool)
                self.add_ip_pool_map[pool_name] = temp_pool
        return temp_pool

    def structure_message(self):
        data_exception = ""
        table_exist_nets = ""
        table_exist_pools = ""
        if self.data_exception:
            data_exception = "第{}行数据异常请检查网关和DNS是否规范\n".format(",".join(self.data_exception))
        if self.table_exist_pools:
            table_exist_pools = "已经存在IP地址池{}\n".format(",".join(self.table_exist_pools))
        if self.table_exist_nets:
            table_exist_nets = "已经存在子网段{}\n".format(",".join(self.table_exist_nets))
        message = data_exception + table_exist_pools + table_exist_nets
        return message or "导入成功！"
