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

from home_application.models import IpNet, IpPools, Ips


class IpPoolsSerializer(serializers.ModelSerializer):
    ip_net = serializers.SerializerMethodField()
    ip_count = serializers.SerializerMethodField()
    usage_rate = serializers.SerializerMethodField()
    used_count = serializers.SerializerMethodField()
    reserve_ip_count = serializers.SerializerMethodField()
    net_count = serializers.SerializerMethodField()

    class Meta:
        model = IpPools
        fields = "__all__"

    def __init__(self, instance=None, data=empty, **kwargs):
        super(IpPoolsSerializer, self).__init__(instance=instance, data=data, **kwargs)
        if isinstance(instance, IpPools):
            ip_pool_ids = [instance.id]
        else:
            ip_pool_ids = [i.id for i in instance]
        self.ip_net_list = list(
            IpNet.objects.filter(ip_pool_id__in=ip_pool_ids).values(
                "id", "ip_pool_id", "ip_net", "bk_cloud_id", "gateway", "dns", "vlan_id", "custom_attr"
            )
        )
        self.ip_list = list(
            Ips.objects.filter(ip_net_id__in=[i["id"] for i in self.ip_net_list]).values(
                "ip_net__ip_pool_id", "allocate_status", "reserve_status"
            )
        )

    def get_ip_net(self, obj):
        return [i for i in self.ip_net_list if i["ip_pool_id"] == obj.id]

    def get_net_count(self, obj):
        return len([i for i in self.ip_net_list if i["ip_pool_id"] == obj.id])

    def get_ip_count(self, obj):
        ip_list = [i for i in self.ip_list if i["ip_net__ip_pool_id"] == obj.id]
        total_count = len(ip_list)
        available_count = len(
            [i for i in ip_list if i["allocate_status"] == Ips.NO_DISTRIBUTION and not i["reserve_status"]]
        )
        return "{}/{}".format(available_count, total_count)

    def get_used_count(self, obj):
        ip_list = [i for i in self.ip_list if i["ip_net__ip_pool_id"] == obj.id]
        used_count = len([i for i in ip_list if i["allocate_status"] == Ips.DISTRIBUTION])
        return used_count

    def get_reserve_ip_count(self, obj):
        ip_list = [i for i in self.ip_list if i["ip_net__ip_pool_id"] == obj.id]
        reserve_ips = len([i for i in ip_list if i["reserve_status"]])
        return reserve_ips

    def get_usage_rate(self, obj):
        ip_list = [i for i in self.ip_list if i["ip_net__ip_pool_id"] == obj.id]
        total_ip = len(ip_list)
        used_ip = len([i for i in ip_list if i["allocate_status"] != Ips.NO_DISTRIBUTION])
        if total_ip == 0:
            return "0.00%"
        return "{:.2f}%".format((used_ip / total_ip) * 100)
