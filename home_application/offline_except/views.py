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
from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from home_application.enums import OFFLINE_IP_ADDRESS_TITLE
from home_application.mixins import ApiGenericMixin
from home_application.models import CustomAttr, Ips, OfflineExcept
from home_application.offline_except.filters import OfflineExceptFilterSet
from home_application.offline_except.serializers import OfflineExceptSerializer
from home_application.utilities.export_helper.excel_export import export_excel_data
from home_application.utilities.ip_helper.ip_tools import get_ip_range


class OfflineExceptViewSet(ApiGenericMixin, ModelViewSet):
    queryset = OfflineExcept.objects.all()
    serializer_class = OfflineExceptSerializer
    search_fields = [
        "ip__name",
        "ip__ip",
        "ip__ip_net__ip_pool__name",
        "ip__ip_net__ip_net",
        "ip__create_by",
        "ip__update_by",
        "ip__description",
        "remark",
    ]
    filter_class = OfflineExceptFilterSet

    @action(methods=["POST"], detail=False)
    def add(self, request):
        remark = request.data.get("remark", "")
        ip_filter_list = request.data.get("ip_list", [])
        ips = self.set_ip_list(ip_filter_list)
        ip_map = dict(Ips.objects.filter(ip__in=ips).values_list("ip", "id"))
        all_offline_ips = list(
            OfflineExcept.objects.filter(ip_id__in=list(ip_map.values())).values_list("ip__ip", flat=True).distinct()
        )
        instance_list = []
        errors = []
        for ip in ips:
            if ip not in all_offline_ips:
                ip_obj = self.format_offline_ip(ip_map, ip, remark)
                if ip_obj:
                    instance_list.append(ip_obj)
                    continue
            errors.append(ip)
        OfflineExcept.objects.bulk_create(instance_list, batch_size=100)
        if not errors:
            result = True
            message = "创建成功"
        else:
            result = False
            message = "{} 添加失败！可能原因：已添加白名单或IP表中不存在该IP".format(",".join(errors))
        return JsonResponse({"result": result, "message": message})

    @staticmethod
    def set_ip_list(ip_filter_list):
        range_ip_list = [i for i in ip_filter_list if "-" in i]
        ip_list = [i for i in ip_filter_list if "-" not in i]
        for i in range_ip_list:
            ip_list.extend(get_ip_range(i))
        ips = set(ip_list)
        return ips

    @staticmethod
    def format_offline_ip(ip_map, item, remark):
        ip_obj = ip_map.get(item)
        if not ip_obj:
            return None
        temp = OfflineExcept(remark=remark, ip_id=ip_obj)
        return temp

    @action(methods=["POST"], detail=False)
    def delete(self, request):
        ip_ids = request.data.get("ip_ids", [])
        OfflineExcept.objects.filter(id__in=ip_ids).delete()
        return JsonResponse({"result": True})

    @action(methods=["get"], detail=False)
    def export_excel(self, request):
        return_dict = self.list(request)
        detail = list(return_dict.data)
        filename = "离线IP地址"
        custom_attrs = CustomAttr.objects.filter(type=CustomAttr.IPS)
        title = OFFLINE_IP_ADDRESS_TITLE
        return export_excel_data(custom_attrs, detail, filename, title)
