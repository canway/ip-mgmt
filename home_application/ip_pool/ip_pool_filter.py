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

from django_filters.rest_framework import OrderingFilter, filters
from django_filters.rest_framework.filterset import FilterSet

from home_application.models import IpPools


class IpPoolFilterSet(FilterSet):
    sort = OrderingFilter(
        fields=(
            "id",
            "create_at",
            "update_at",
            "name",
        )
    )
    name = filters.CharFilter(lookup_expr="icontains")
    create_by = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = IpPools
        fields = {
            "update_at": ["gte", "lte"],
            "create_at": ["gte", "lte"],
        }
