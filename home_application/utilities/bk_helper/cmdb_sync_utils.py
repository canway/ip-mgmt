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
import copy
import datetime
import json

from home_application.models import AbnormalIp, CmdbSync, CmdbSyncRecord, Ips


class CMDBSync(object):
    def __init__(self, sync_obj: CmdbSync, client, ip_map: {}, enable_rule, sync_map):
        self.sync_obj = sync_obj
        self.client = client
        self.attr_dist = self.format_attr()
        self.ip_map = ip_map
        self.enable_rule = enable_rule
        self.delete_abnormal_ips = []
        self.add_abnormal_ips = []
        self.update_ip_list = []
        self.add_ip_list = []
        self.sync_list = []
        self.sync_list_without_ip_id = {}
        self.sync_map = copy.deepcopy(sync_map)
        self.sync_map.pop(sync_obj.id)

    def start_sync(self):
        attr_kwargs = {"bk_obj_id": self.sync_obj.model_id, "condition": {"bk_property_type": "enum"}}
        enum_res = self.client.cc.search_object_attribute(attr_kwargs)
        enum_map = {}
        for i in enum_res["data"]:
            enum_map[i["bk_property_id"]] = {x["id"]: x["name"] for x in i["option"]}
        cmdb_attr = [i["cmdb_attr"] for i in self.attr_dist.values()]
        if self.sync_obj.model_id != "host":
            kwargs = {"bk_obj_id": self.sync_obj.model_id, "fields": {self.sync_obj.model_id: cmdb_attr}}
            method_name = "search_inst"
            limit = 200
        else:
            kwargs = {"bk_supplier_account": "0", "fields": cmdb_attr}
            method_name = "list_hosts_without_biz"
            limit = 500
        self.sync_ip_list(enum_map, kwargs, method_name, limit)
        AbnormalIp.objects.filter(ip__ip__in=self.delete_abnormal_ips).delete()
        self.set_cmdb_no_ip_status()
        AbnormalIp.objects.bulk_create(self.add_abnormal_ips, batch_size=100)
        Ips.objects.bulk_create(self.add_ip_list, batch_size=100)
        self._update_sync_list()
        fields = ["gateway", "dns", "custom_attr", "is_cmdb_sync", "allocate_status"]
        Ips.objects.bulk_update(self.update_ip_list, fields, batch_size=100)
        CmdbSyncRecord.objects.bulk_create(self.sync_list, batch_size=100)

    def _update_sync_list(self):
        new_ip_map = dict(Ips.objects.filter(ip__in=[i.ip for i in self.add_ip_list]).values_list("ip", "id"))
        for ip, sync_recode in self.sync_list_without_ip_id.items():
            sync_recode.ip_id = new_ip_map[ip]
            self.sync_list.append(sync_recode)

    def set_cmdb_no_ip_status(self):
        error_ips = filter(lambda x: x.is_cmdb_sync, self.ip_map.values())
        error_ip_ids = set(map(lambda x: x.id, error_ips))
        CmdbSyncRecord.objects.filter(cmdb_sync_id=self.sync_obj.id, ip_id__in=error_ip_ids).delete()
        all_sync_ip_ids = []
        for i in self.sync_map.values():
            all_sync_ip_ids.extend(i)
        delete_ip_ids = error_ip_ids - set(all_sync_ip_ids)
        Ips.objects.filter(id__in=delete_ip_ids).update(allocate_status=Ips.NO_DISTRIBUTION)

    def format_attr(self):
        attribute_map = self.sync_obj.attribute_map
        while not isinstance(attribute_map, list):
            attribute_map = json.loads(attribute_map)
        attribute_map_dist = {i["ipam_attr"]: i for i in attribute_map}
        for i in ["bk_cloud_id", "gateway", "dns"]:
            if i in attribute_map_dist:
                continue
            cloud_data = {"cmdb_attr": i, "is_cmdb_enum": False, "check_conflict": True}
            attribute_map_dist.setdefault(i, cloud_data)
        return attribute_map_dist

    def sync_ip_list(self, enum_map, kwargs, method_name, limit):
        current = 1
        get_next = True
        current_count = 0
        attr_list = [i for i in self.attr_dist.keys() if i not in ["ip", "bk_cloud_id", "gateway", "dns"]]
        exist_ips = [""]
        while get_next:
            kwargs["page"] = {"start": (current - 1) * limit, "limit": limit}
            client_method = getattr(self.client.cc, method_name)
            res = client_method(kwargs)
            if (not res["result"]) or (not res["data"]["count"]) or (not len(res["data"]["info"])):
                return
            current_count += len(res["data"]["info"])
            get_next = current_count < res["data"]["count"]
            current += 1
            for inst in res["data"]["info"]:
                ip = inst.get(self.attr_dist["ip"]["cmdb_attr"]) or ""
                if ip in exist_ips:
                    continue
                exist_ips.append(ip)
                self.format_one_inst_data(ip, attr_list, enum_map, inst)

    def format_one_inst_data(self, ip, attr_list, enum_map, inst):
        bk_cloud_id = inst.get(self.attr_dist["bk_cloud_id"]["cmdb_attr"], 0)
        gateway = inst.get(self.attr_dist["gateway"]["cmdb_attr"], "")
        dns = inst.get(self.attr_dist["dns"]["cmdb_attr"], "")
        ip_obj = self.ip_map.pop(ip, None)
        if not ip_obj:
            ip_obj = Ips(
                allocate_status=Ips.DISTRIBUTION,
                online_status=True,
                is_cmdb_sync=True,
                ip=ip,
                bk_cloud_id=bk_cloud_id,
                gateway=gateway,
                dns=dns,
            )
            self.add_ip_list.append(ip_obj)
            self.create_new_sync_recode(ip_obj, inst, attr_list, enum_map, gateway, dns)
            return
        self.delete_abnormal_ips.append(ip)
        self.sync_ip_custom_attr(ip_obj, inst, attr_list, enum_map, gateway, dns)

    def create_new_sync_recode(self, ip_obj: Ips, inst, attr_list, enum_map, gateway, dns):
        now = datetime.datetime.now()
        sync_record = CmdbSyncRecord(sync_at=now, cmdb_sync_id=self.sync_obj.id)
        custom_attrs = []
        for attr in attr_list:
            attr_value = inst.get(self.attr_dist[attr]["cmdb_attr"])
            if attr_value and self.attr_dist[attr]["is_cmdb_enum"] and attr in enum_map:
                attr_value = enum_map.get(attr, {}).get(attr_value, "")
            custom_attrs.append({"name": attr, "value": attr_value})
        new_info = {
            "ip": ip_obj.ip,
            "bk_cloud_id": ip_obj.bk_cloud_id,
            "gateway": gateway,
            "dns": dns,
            "custom_attr": custom_attrs,
        }
        sync_record.sync_status = CmdbSyncRecord.SYNC_SUCCESS
        sync_record.complete_at = datetime.datetime.now()
        sync_record.old_info = {}
        sync_record.new_info = new_info
        self.sync_list_without_ip_id[ip_obj.ip] = sync_record

    def sync_ip_custom_attr(self, ip_obj: Ips, inst, attr_list, enum_map, gateway, dns):
        now = datetime.datetime.now()
        sync_record = CmdbSyncRecord(
            sync_at=now,
            sync_status=CmdbSyncRecord.SYNCING,
            cmdb_sync_id=self.sync_obj.id,
            ip_id=ip_obj.id,
        )
        custom_attrs, conflict_flag = self.compare_attr_value(attr_list, enum_map, inst, ip_obj)
        if conflict_flag:
            self.set_error_sync_recode(custom_attrs, dns, gateway, ip_obj, sync_record)
            return
        old_info = {
            "ip": ip_obj.ip,
            "bk_cloud_id": ip_obj.bk_cloud_id,
            "gateway": ip_obj.gateway,
            "dns": ip_obj.dns,
            "custom_attr": ip_obj.custom_attr,
        }
        new_info = {
            "ip": ip_obj.ip,
            "bk_cloud_id": ip_obj.bk_cloud_id,
            "gateway": gateway,
            "dns": dns,
            "custom_attr": custom_attrs,
        }

        if ip_obj.allocate_status == Ips.NO_DISTRIBUTION:
            ip_obj.allocate_status = Ips.DISTRIBUTION
            if self.enable_rule:
                self.create_abnormal_ip(ip_obj, gateway, dns, custom_attrs, AbnormalIp.UNASSIGNED_BUT_EXISTS_CMDB)
        self.update_ip_obj(ip_obj, gateway, dns, custom_attrs)
        self.set_success_recode(sync_record, old_info, new_info)

    def set_success_recode(self, sync_record, old_info, new_info):
        sync_record.sync_status = CmdbSyncRecord.SYNC_SUCCESS
        sync_record.complete_at = datetime.datetime.now()
        sync_record.old_info = old_info
        sync_record.new_info = new_info
        self.sync_list.append(sync_record)

    def update_ip_obj(self, ip_obj, gateway, dns, custom_attrs):
        ip_obj.gateway = gateway if gateway else ip_obj.gateway
        ip_obj.dns = dns if dns else ip_obj.dns
        ip_obj.custom_attr = custom_attrs
        ip_obj.is_cmdb_sync = True
        self.update_ip_list.append(ip_obj)

    def compare_attr_value(self, attr_list, enum_map, inst, ip_obj):
        custom_attrs = []
        conflict_flag = False
        for attr in attr_list:
            attr_value = inst.get(self.attr_dist[attr]["cmdb_attr"])
            # 处理枚举类型
            if attr_value and self.attr_dist[attr]["is_cmdb_enum"] and attr in enum_map:
                attr_value = enum_map.get(attr, {}).get(attr_value, "")
            custom_attrs.append({"name": attr, "value": attr_value})
            # 冲突检测
            if self.attr_dist[attr]["check_conflict"]:
                ip_attr_dist = {i["name"]: i["value"] for i in ip_obj.custom_attr}
                if ip_attr_dist[self.attr_dist[attr]["cmdb_attr"]] != attr_value:
                    conflict_flag = True
        return custom_attrs, conflict_flag

    def set_error_sync_recode(self, custom_attrs, dns, gateway, ip_obj, sync_record):
        self.create_abnormal_ip(ip_obj, gateway, dns, custom_attrs, AbnormalIp.CMDB_ATTR_CHANGE)
        sync_record.sync_status = CmdbSyncRecord.SYNC_FAIL
        sync_record.old_info = "同步取消"
        sync_record.new_info = "冲突检测失败"
        self.sync_list.append(sync_record)

    def create_abnormal_ip(self, ip_obj, gateway, dns, custom_attrs, code):
        remark = json.dumps(
            {
                "ip": ip_obj.ip,
                "bk_cloud_id": ip_obj.bk_cloud_id,
                "gateway": gateway,
                "dns": dns,
                "custom_attr": custom_attrs,
            }
        )
        abnormal_ip = AbnormalIp(ip_id=ip_obj.id, abnormal_code=code, remark=remark)
        self.add_abnormal_ips.append(abnormal_ip)
