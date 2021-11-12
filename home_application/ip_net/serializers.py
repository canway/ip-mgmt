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
from rest_framework import serializers
from rest_framework.fields import empty

from home_application.models import IpNet, Ips


class IpNetSerializer(serializers.ModelSerializer):
    create_by = serializers.CharField(allow_blank=True, label="创建人", max_length=100, required=False)
    update_by = serializers.CharField(allow_blank=True, label="修改人", max_length=100, required=False)
    remark = serializers.CharField(allow_blank=True, allow_null=True, label="备注", max_length=500, required=False)
    name = serializers.CharField(allow_blank=True, allow_null=True, label="名称", max_length=200)
    description = serializers.CharField(allow_blank=True, allow_null=True, label="描述", max_length=500)
    custom_attr = serializers.JSONField(allow_null=True)
    vlan_id = serializers.CharField(allow_blank=True, label="VLAN ID", max_length=100)
    ip_count = serializers.SerializerMethodField()
    usage_rate = serializers.SerializerMethodField()
    ip_pool_name = serializers.SerializerMethodField()
    reserve_ip_count = serializers.SerializerMethodField()
    used_count = serializers.SerializerMethodField()

    class Meta:
        model = IpNet
        fields = "__all__"

    def __init__(self, instance=None, data=empty, **kwargs):
        super(IpNetSerializer, self).__init__(instance=instance, data=data, **kwargs)
        if isinstance(instance, IpNet):
            ip_net_ids = [instance.id]
        else:
            ip_net_ids = [i.id for i in instance]
        self.ip_list = Ips.objects.filter(ip_net_id__in=ip_net_ids)

    def get_ip_count(self, obj):
        total = 0
        available_count = 0
        for ip_obj in self.ip_list:
            if ip_obj.ip_net_id == obj.id:
                total += 1
                if ip_obj.allocate_status == Ips.NO_DISTRIBUTION and not ip_obj.reserve_status:
                    available_count += 1
        return "{}/{}".format(available_count, total)

    def get_used_count(self, obj):
        used_count = 0
        for ip_obj in self.ip_list:
            if ip_obj.ip_net_id == obj.id and ip_obj.allocate_status == Ips.DISTRIBUTION:
                used_count += 1
        return used_count

    def get_reserve_ip_count(self, obj):
        reserve_count = 0
        for ip_obj in self.ip_list:
            if ip_obj.ip_net_id == obj.id and ip_obj.reserve_status:
                reserve_count += 1
        return reserve_count

    def get_usage_rate(self, obj):
        total_ip = 0
        used_ip = 0
        for ip_obj in self.ip_list:
            if ip_obj.ip_net_id == obj.id:
                total_ip += 1
                if ip_obj.allocate_status != Ips.NO_DISTRIBUTION:
                    used_ip += 1
        if total_ip == 0:
            return "{:.2f}%".format(0)
        return "{:.2f}%".format((used_ip / total_ip) * 100)

    @staticmethod
    def get_ip_pool_name(obj):
        return obj.ip_pool.name
