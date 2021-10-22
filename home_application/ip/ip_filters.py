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

from django_filters import OrderingFilter, filters
from django_filters.rest_framework.filterset import FilterSet

from home_application.models import Ips


class IpFilterSet(FilterSet):
    sort = OrderingFilter(
        fields=(
            "id",
            "allocate_time",
            "expired_time",
            "offline_time",
            "scan_time",
            "create_at",
            "update_at",
            "allocate_status",
            "online_status",
            "reserve_status",
            "gateway",
            "dns",
            "ip_net__ip_pool__name",
        )
    )
    ip = filters.CharFilter(lookup_expr="icontains")
    remark = filters.CharFilter(lookup_expr="icontains")
    member = filters.CharFilter(lookup_expr="icontains")
    business_system = filters.CharFilter(lookup_expr="icontains")
    gateway = filters.CharFilter(lookup_expr="icontains")
    dns = filters.CharFilter(lookup_expr="icontains")
    description = filters.CharFilter(lookup_expr="icontains")
    ip_pool = filters.CharFilter(field_name="ip_net__ip_pool_id")
    ip_net = filters.CharFilter(field_name="ip_net_id")

    class Meta:
        model = Ips
        fields = {
            "allocate_status": ["exact"],
            "online_status": ["exact"],
            "reserve_status": ["exact"],
            "bk_cloud_id": ["exact"],
            "allocate_at": ["gte", "lte"],
            "expired_at": ["gte", "lte"],
            "offline_at": ["gte", "lte"],
            "scan_at": ["gte", "lte"],
        }
