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
import json
import logging

from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from home_application.enums import ABNORMAL_IP_ADDRESS_TITLE
from home_application.ip_abnormal.filters import AbnormalIpFilterSet
from home_application.ip_abnormal.serializers import IpAbnormalIpsSerializer
from home_application.mixins import ApiGenericMixin
from home_application.models import AbnormalIp, CustomAttr, Ips, OfflineExcept
from home_application.utilities.export_helper.excel_export import export_excel_data


class IpAbnormal(ApiGenericMixin, viewsets.ModelViewSet):
    queryset = AbnormalIp.objects.all()
    serializer_class = IpAbnormalIpsSerializer
    search_fields = [
        "ip__name",
        "ip__ip",
        "ip__ip_net__ip_pool__name",
        "ip__ip_net__ip_net",
        "ip__create_by",
        "ip__update_by",
        "ip__description",
    ]
    filter_class = AbnormalIpFilterSet

    @action(methods=["POST"], detail=False)
    def confirm(self, request, *args, **kwargs):
        params = request.data
        ip_ids = params.get("abnormal_ips", [])
        abnormal_ips = AbnormalIp.objects.filter(
            id__in=ip_ids,
            abnormal_code__in=[AbnormalIp.CMDB_NO_IP, AbnormalIp.CMDB_ATTR_CHANGE],
        )
        update_list = []
        update_ip_list = []
        error_list = []
        for abnormal_ip in abnormal_ips:
            if abnormal_ip.abnormal_code == AbnormalIp.CMDB_NO_IP:
                abnormal_ip.ip.is_cmdb_sync = False
                abnormal_ip.ip.allocate_status = Ips.WAIT_RECOVERY
                abnormal_ip.ip.remark = "CMDB已无此IP记录，删除cmdb标记！"
                update_list.append(abnormal_ip)
                update_ip_list.append(abnormal_ip.ip)
            else:
                """CMDB同步属性变动"""
                try:
                    ip_attrs = json.loads(abnormal_ip.remark)
                    for key, value in ip_attrs:
                        setattr(abnormal_ip, key, value)
                    update_list.append(abnormal_ip)
                except Exception as e:
                    error_list.append(str(e))
        with transaction.atomic():
            Ips.objects.bulk_update(update_ip_list, ["is_cmdb_sync", "allocate_status", "remark"], batch_size=100)
            AbnormalIp.objects.bulk_update(update_list, ["abnormal_code", "remark", "checked"], batch_size=100)
            AbnormalIp.objects.filter(id__in=ip_ids).exclude(
                abnormal_code__in=[AbnormalIp.CMDB_NO_IP, AbnormalIp.CMDB_ATTR_CHANGE]
            ).delete()
        return JsonResponse({"result": len(error_list) == 0, "message": "\n".join(error_list)})

    @action(methods=["POST"], detail=False)
    def add_offline_except(self, request):
        ip_list = set(request.data.get("ip_list", []))
        all_offline_except = list(OfflineExcept.objects.all().values_list("ip_id", flat=True))
        instance_list = [
            OfflineExcept(ip_id=i, create_by=request.user.username) for i in ip_list if i not in all_offline_except
        ]
        OfflineExcept.objects.bulk_create(instance_list, batch_size=100)
        return JsonResponse({"result": True})

    @action(methods=["get"], detail=False)
    def export_excel(self, request):
        return_dict = self.list(request)
        detail = list(return_dict.data)
        filename = "异常IP地址"
        custom_attrs = CustomAttr.objects.filter(type=CustomAttr.IPS)
        title = ABNORMAL_IP_ADDRESS_TITLE
        try:
            return export_excel_data(custom_attrs, detail, filename, title)
        except Exception as e:
            logging.exception(e)
            return JsonResponse({"result": False, "message": str(e)})
