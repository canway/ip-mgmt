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

from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from home_application.celery_tasks import create_by_ip_net, create_ip_by_ip_nets
from home_application.enums import IP_CHILD_MANAGEMENT, IP_SUBNET_TITLE
from home_application.exceptions import IPPoolCreateException
from home_application.ip_net.ip_net_filter import DataFilter
from home_application.ip_net.serializers import IpNetSerializer
from home_application.ip_net.tools import check_ip_net_normal, create_ip_net
from home_application.mixins import ApiGenericMixin
from home_application.models import CustomAttr, IpNet, IpPools, Ips, OperationLog, Settings
from home_application.utilities.export_helper.excel_export import format_data_and_export_excel


class IpNetList(ApiGenericMixin, viewsets.ModelViewSet):
    queryset = IpNet.objects.all().order_by("-id")
    serializer_class = IpNetSerializer
    search_fields = [
        "name",
        "ip_net",
        "ip_pool__name",
        "create_by",
        "update_by",
        "description",
        "remark",
    ]
    filter_class = DataFilter

    def create(self, request, *args, **kwargs):
        params = request.data.copy()
        username = request.user.username
        params["create_by"] = username
        params["update_by"] = username
        ip_nets = list(IpNet.objects.all().values_list("ip_net", flat=True))
        try:
            check_ip_net_normal(ip_nets, params["ip_net"], params["gateway"], params["dns"])
        except IPPoolCreateException as e:
            return JsonResponse({"result": False, "message": str(e)})
        serializer = self.get_serializer(data=params)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        ip_net = IpNet.objects.get(id=serializer.data["id"])
        create_by_ip_net.delay(ip_net, username)
        OperationLog.objects.create(
            operate_type=OperationLog.ADD,
            operate_obj=IP_CHILD_MANAGEMENT,
            operator=username,
            operate_detail=json.dumps(request.data),
            result=True,
        )
        return JsonResponse({"result": True})

    @action(methods=["POST"], detail=False)
    def batch_create(self, request, *args, **kwargs):
        ip_nets = request.data.get("ip_net", [])
        username = request.user.username
        ip_pool = IpPools.objects.get(id=ip_nets[0]["ip_pool"])
        exist_ip_net = list(IpNet.objects.all().values_list("ip_net", flat=True))
        add_ip_nets, error_msgs = create_ip_net(ip_nets, ip_pool, username, exist_ip_net)
        if len(error_msgs) == len(ip_nets):
            return JsonResponse({"result": False, "message": "，".join(error_msgs)})
        current_net_list = list(ip_pool.ipnet_set.all().values_list("id", flat=True))
        with transaction.atomic():
            IpNet.objects.bulk_create(add_ip_nets, batch_size=100)
            OperationLog.objects.create(
                operate_type=OperationLog.ADD,
                operate_obj=IP_CHILD_MANAGEMENT,
                operator=request.user.username,
                operate_detail=json.dumps(request.data),
                result=True,
            )
        net_list = IpNet.objects.filter(ip_pool_id=ip_pool).exclude(id__in=current_net_list)
        create_ip_by_ip_nets.delay(net_list)
        if error_msgs:
            return JsonResponse({"result": False, "message": "\n".join(error_msgs)})
        return JsonResponse({"result": True})

    @staticmethod
    def delete_by_ip_net(ip_net_id):
        deleted_ips = Ips.objects.filter(ip_net_id=ip_net_id).filter(is_cmdb_sync=False)
        deleted_ips.update(gateway="", dns="", bk_cloud_id=None)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        can_delete = obj.can_delete()
        if not can_delete:
            result = {"result": False, "message": "子网下还存在已分配或待回收的IP，不允许删除"}
        else:
            instance = self.get_object()
            self.perform_destroy(instance)
            self.delete_by_ip_net(obj.id)
            result = {"result": True, "message": "删除成功"}
            OperationLog.objects.create(
                operate_type=OperationLog.DELETE,
                operate_obj=IP_CHILD_MANAGEMENT,
                operator=request.user.username,
                operate_detail=json.dumps(request.data),
                result=True,
            )
        return JsonResponse(result)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        params = request.data
        params["create_by"] = request.user.username
        params["update_by"] = request.user.username
        ip_nets = list(IpNet.objects.exclude(id=instance.id).values_list("ip_net", flat=True))
        try:
            check_ip_net_normal(ip_nets, params["ip_net"], params["gateway"], params["dns"])
        except IPPoolCreateException as e:
            return JsonResponse({"result": False, "message": str(e)})
        serializer = self.get_serializer(instance, data=params)
        if not serializer.is_valid():
            return JsonResponse({"result": False, "message": "参数效验不通过"})
        self.perform_update(serializer)
        OperationLog.objects.create(
            operate_type=OperationLog.MODIFY,
            operate_obj=IP_CHILD_MANAGEMENT,
            operator=request.user.username,
            operate_detail=json.dumps(request.data),
            result=True,
        )
        return JsonResponse({"result": True})

    @action(methods=["get"], detail=False)
    def export_excel(self, request):
        return_dict = self.list(request)
        detail = list(return_dict.data)
        filename = "IP子网"
        title = IP_SUBNET_TITLE
        operate_obj = IP_CHILD_MANAGEMENT
        operate_detail = json.dumps(request.data)
        username = request.user.username
        attr_type = CustomAttr.TET_WORK_SEGMENT
        return format_data_and_export_excel(title, detail, filename, attr_type, operate_obj, username, operate_detail)

    @action(methods=["get"], detail=False)
    def get_ip_net_summary(self, request):
        return_dict = self.list(request)
        ip_net_threshold = float(Settings.objects.get(key="ip_net_threshold").value) * 100
        detail = list(return_dict.data)
        result_list = [
            {
                "id": item["id"],
                "name": item["name"],
                "ip_net": item["ip_net"],
                "order": float(item["usage_rate"].replace("%", "")),
                "over_threshold": float(item["usage_rate"].replace("%", "")) > ip_net_threshold,
                "usage_rate": item["usage_rate"],
                "used_count": item["used_count"],
            }
            for item in detail
        ]
        result_list.sort(key=lambda i: i["order"], reverse=True)
        total = len(result_list)
        used = 0
        for ip_net in result_list:
            if ip_net["used_count"] > 0:
                used = used + 1
        result_list = result_list[:5]
        return JsonResponse(
            {"result": True, "data": {"top_5": result_list, "total": total, "used": used}, "message": ""}
        )
