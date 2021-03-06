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

from home_application.models import OfflineExcept


class OfflineExceptFilterSet(FilterSet):
    sort = OrderingFilter(
        fields=(
            "id",
            "ip__allocate_time",
            "ip__expired_time",
            "ip__offline_time",
            "ip__scan_time",
            "create_at",
            "ip__update_at",
            "ip__allocate_status",
            "ip__online_status",
            "ip__reserve_status",
            "ip__gateway",
            "ip__dns",
            "ip__ip_net__ip_pool__name",
        )
    )
    ip = filters.CharFilter(field_name="ip__ip", lookup_expr="icontains")
    ip_pool = filters.CharFilter(field_name="ip__ip_net__ip_pool_id")
    ip_net = filters.CharFilter(field_name="ip__ip_net_id")
    bk_cloud_id = filters.NumberFilter(field_name="ip__bk_cloud_id")
    gateway = filters.CharFilter(field_name="ip__gateway", lookup_expr="icontains")
    dns = filters.CharFilter(field_name="ip__dns", lookup_expr="icontains")
    allocate_status = filters.CharFilter(field_name="ip__allocate_status")

    class Meta:
        model = OfflineExcept
        fields = {
            "ip__allocate_at": ["gte", "lte"],
            "ip__expired_at": ["gte", "lte"],
            "ip__offline_at": ["gte", "lte"],
            "ip__scan_at": ["gte", "lte"],
            "create_at": ["gte", "lte"],
            "ip__update_at": ["gte", "lte"],
        }
