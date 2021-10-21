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
import datetime

from django.forms.models import model_to_dict
from rest_framework import serializers

from home_application.models import OfflineExcept


class OfflineExceptSerializer(serializers.ModelSerializer):
    ip_obj = serializers.SerializerMethodField()
    offline_days = serializers.SerializerMethodField()
    ip_pool = serializers.SerializerMethodField()
    ip_net = serializers.SerializerMethodField()

    @staticmethod
    def get_ip_obj(obj):
        ip_obj = model_to_dict(obj.ip)
        try:
            ip_obj["ip_pool"] = obj.ip.ip_net.ip_pool.name
        except AttributeError:
            ip_obj["ip_pool"] = ""
        return ip_obj

    @staticmethod
    def get_ip_net(obj):
        if obj.ip.ip_net:
            return obj.ip.ip_net.ip_net
        return ""

    @staticmethod
    def get_ip_pool(obj):
        if obj.ip.ip_net:
            return obj.ip.ip_net.ip_pool.name
        return ""

    @staticmethod
    def get_offline_days(obj):
        return (
            (datetime.datetime.now() - obj.ip.offline_at).days if not obj.ip.online_status and obj.ip.offline_at else 0
        )

    class Meta:
        model = OfflineExcept
        fields = "__all__"
