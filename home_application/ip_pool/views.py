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
from calendar import datetime
from datetime import timedelta

import xlrd
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from home_application.celery_tasks import create_ip_by_ip_pool
from home_application.enums import IP_ADDRESS_POOL_MANAGEMENT, IP_POOL_EXPORT_TEMPLATE_TITLE, IP_POOL_PART_TITLE
from home_application.exceptions import IPPoolCreateException
from home_application.ip_net.tools import create_ip_net, delete_ip_net, update_ip_net
from home_application.ip_pool.excel_import_helper import ExcelImport
from home_application.ip_pool.ip_pool_filter import IpPoolFilterSet
from home_application.ip_pool.serializers import IpPoolsSerializer
from home_application.mixins import ApiGenericMixin
from home_application.models import CustomAttr, IpNet, IpPoolEventLog, IpPools, OperationLog, Settings
from home_application.utilities.export_helper.excel_export import make_excel


class IpPoolsViewSet(ApiGenericMixin, ModelViewSet):
    queryset = IpPools.objects.all().order_by("-id")
    serializer_class = IpPoolsSerializer
    search_fields = [
        "name",
        "create_by",
        "update_by",
        "description",
        "remark",
    ]
    filter_class = IpPoolFilterSet

    def retrieve(self, request, *args, **kwargs):
        ip_pool_instance = self.get_object()
        ip_pool_instance.ipnet_set.all()
        serializer = self.get_serializer(ip_pool_instance)
        return JsonResponse({"result": True, "data": serializer.data})

    def create(self, request, *args, **kwargs):
        pool_name = request.data.get("name", "")
        is_exist = IpPools.objects.filter(name=pool_name).exists()
        if is_exist:
            return JsonResponse({"result": False, "message": "存在同名IP地址池，请检查后输入！"})
        ip_nets = request.data.get("ip_net", [])
        exist_ip_net = list(IpNet.objects.all().values_list("ip_net", flat=True))
        username = request.user.username
        with transaction.atomic():
            ip_pool = IpPools.objects.create(
                name=pool_name,
                create_by=username,
                description=request.data.get("description", ""),
                remark=request.data.get("remark", ""),
                status=IpPools.WAITING_ENABLE,
                custom_attr=request.data.get("customAttr", {}),
            )
            add_ip_nets, error_msgs = create_ip_net(ip_nets, ip_pool, username, exist_ip_net)
            if len(error_msgs) == len(ip_nets):
                ip_pool.delete()
                return JsonResponse({"result": False, "message": "，".join(error_msgs)})
            IpNet.objects.bulk_create(add_ip_nets, batch_size=100)
            OperationLog.objects.create(
                operate_type=OperationLog.ADD,
                operate_obj=IP_ADDRESS_POOL_MANAGEMENT,
                operator=username,
                operate_detail=json.dumps(request.data),
                result=True,
            )
        create_ip_by_ip_pool.delay(ip_pool)
        if error_msgs:
            return JsonResponse({"result": False, "message": "\n".join(error_msgs)})
        return JsonResponse({"result": True})

    def update(self, request, *args, **kwargs):
        params = request.data
        try:
            ip_pool = self.update_ip_pool(params, request)
        except IPPoolCreateException as e:
            return JsonResponse({"result": False, "message": str(e)})
        ip_nets = params.get("ip_net", [])
        error_message = self.update_net_by_pool(ip_nets, ip_pool, request.user.username, params)
        create_ip_by_ip_pool.delay(ip_pool)
        if error_message:
            return JsonResponse({"result": False, "message": "\n".join(error_message)})
        return JsonResponse({"result": True})

    @staticmethod
    def update_net_by_pool(ip_nets, ip_pool, username, params):
        add_list = [i for i in ip_nets if not i.get("id")]
        update_list = [i for i in ip_nets if i.get("id")]
        ip_net_ids = [i["id"] for i in update_list]
        exist_ip_net = list(IpNet.objects.exclude(ip_pool_id=ip_pool.id).values_list("ip_net", flat=True))
        ip_net_deleted = IpNet.objects.filter(ip_pool_id=ip_pool.id).exclude(id__in=ip_net_ids).values("ip_net", "id")
        db_update_list = list(IpNet.objects.filter(id__in=ip_net_ids))
        db_update_map = {i.id: i for i in db_update_list}
        del_ip_net_ids, delete_msgs = delete_ip_net(ip_pool, list(ip_net_deleted))  # 删除旧子网
        ip_net_instance_list, update_msgs = update_ip_net(update_list, db_update_map, exist_ip_net)  # 更新子网
        add_ip_nets, add_msgs = create_ip_net(add_list, ip_pool, username, exist_ip_net)  # 添加新子网
        error_msgs = add_msgs + delete_msgs + update_msgs
        update_params = ["bk_cloud_id", "gateway", "dns", "custom_attr", "vlan_id"]  # noqa
        with transaction.atomic():
            IpNet.objects.filter(id__in=del_ip_net_ids).delete()
            IpNet.objects.bulk_update(ip_net_instance_list, update_params, batch_size=80)
            if add_ip_nets:
                IpNet.objects.bulk_create(add_ip_nets, batch_size=100)
            OperationLog.objects.create(
                operate_type=OperationLog.MODIFY,
                operate_obj=IP_ADDRESS_POOL_MANAGEMENT,
                operator=username,
                operate_detail=json.dumps(params),
                result=True,
            )
        return error_msgs

    def update_ip_pool(self, params, request):
        ip_pool = self.get_object()
        is_exist = IpPools.objects.filter(name=params["name"]).exclude(id=ip_pool.id).exists()
        if is_exist:
            raise IPPoolCreateException("存在同名IP地址池，请检查后输入！")
        ip_pool.name = params.get("name", "")
        ip_pool.update_by = request.user.username
        ip_pool.description = params.get("description", "")
        ip_pool.remark = params.get("remark", "")
        ip_pool.status = params.get("status", "")
        ip_pool.custom_attr = params.get("customAttr", {})
        ip_pool.save()
        return ip_pool

    def destroy(self, request, *args, **kwargs):
        ip_pool = self.get_object()
        if ip_pool.can_delete():
            OperationLog.objects.create(
                operate_type=OperationLog.DELETE,
                operate_obj=IP_ADDRESS_POOL_MANAGEMENT,
                operator=request.user.username,
                operate_detail="删除地址池，详情：{}".format(json.dumps(model_to_dict(ip_pool))),
                result=True,
            )
            ip_pool.delete()
            return JsonResponse({"result": True, "message": "删除成功"})
        return JsonResponse({"result": False, "message": "删除失败，地址池下还存在正在使用或者待回收的IP"})

    @action(methods=["get"], detail=False)
    def export_excel(self, request):
        return_dict = self.list(request)
        detail = list(return_dict.data)
        filename = "IP地址池"
        data_key, to_excel_data = self.format_excel_data(detail)
        OperationLog.objects.create(
            operate_type=OperationLog.EXEC,
            operate_obj=IP_ADDRESS_POOL_MANAGEMENT,
            operator=request.user.username,
            operate_detail=json.dumps(request.data),
            result=True,
        )
        try:
            return make_excel(data_key, filename, to_excel_data)
        except Exception as e:
            OperationLog.objects.create(
                operate_type=OperationLog.EXEC,
                operate_obj=IP_ADDRESS_POOL_MANAGEMENT,
                operator=request.user.username,
                operate_detail=json.dumps(request.data),
                result=False,
            )
            return JsonResponse({"result": False, "message": str(e)})

    @staticmethod
    def format_excel_data(detail):
        custom_attrs = dict(CustomAttr.objects.filter(type="ip_pool").values_list("name", "display_name"))
        title = dict(IP_POOL_PART_TITLE, **custom_attrs)
        to_excel_data = [title]
        for data in detail:
            cus_map = {i["name"]: i.get("value", "") for i in data["custom_attr"]}
            for attr in custom_attrs.keys():
                data[attr] = cus_map.get(attr, "")
            to_excel_data.append(data)
        data_key = list(title.keys())
        return data_key, to_excel_data

    @action(methods=["get"], detail=False)
    def download_template(self, request):
        filename = "IP地址池导出模板"
        custom_attrs = CustomAttr.objects.filter(type__in=[CustomAttr.TET_WORK_SEGMENT, CustomAttr.IP_POOL]).values(
            "name", "required", "display_name"
        )
        title = IP_POOL_EXPORT_TEMPLATE_TITLE
        for cus in custom_attrs:
            required_msg = "[必填]" if cus["required"] else ""
            title.setdefault(cus["name"], f"{required_msg}{cus['display_name']}({cus['name']})")
        to_excel_data = [title]
        data_key = list(title.keys())
        try:
            return make_excel(data_key, filename, to_excel_data)
        except Exception as e:
            logging.exception(e)
            return JsonResponse({"result": False, "message": str(e)})

    @action(methods=["post"], detail=False)
    def import_ip_pool(self, request):
        # 获取前端提交的excel文件
        import_file = request.FILES.get("file")
        wb = xlrd.open_workbook(filename=None, file_contents=import_file.read())
        # 获取excel文件的第一个sheet
        table = wb.sheets()[0]
        # 设置表头
        excel_import_client = ExcelImport(table, request.user.username)
        message = excel_import_client.import_excel_data()
        if not message:
            return JsonResponse({"result": True})
        return JsonResponse({"result": False, "message": message})

    @action(methods=["get"], detail=False)
    def get_ip_pool_summary(self, request):
        return_dict = self.list(request)
        detail = list(return_dict.data)
        ip_pool_threshold = float(Settings.objects.get(key="ip_pool_threshold").value) * 100
        result_list = [
            {
                "id": item["id"],
                "name": item["name"],
                "order": float(str(item["usage_rate"]).replace("%", "")),
                "over_threshold": float(str(item["usage_rate"]).replace("%", "")) > ip_pool_threshold,
                "usage_rate": item["usage_rate"],
                "used_count": item["used_count"],
            }
            for item in detail
        ]
        result_list.sort(key=lambda i: i["order"], reverse=True)
        used = 0
        total = len(result_list)
        for ip_pool in result_list:
            if ip_pool["used_count"] > 0:
                used = used + 1
        result_list = result_list[:5]
        return JsonResponse({"result": True, "data": {"top_5": result_list, "total": total, "used": used}})

    @action(methods=["get"], detail=False)
    def get_usage_rate_event(self, request):
        date_now = datetime.datetime.now()
        start_date = request.GET.get("start", date_now + timedelta(days=-10))
        end_date = request.GET.get("end", date_now)
        ip_pool_id = request.GET.get("ip_pool_id", 0)
        events = list(
            IpPoolEventLog.objects.filter(
                when_time__gt=start_date, when_time__lte=end_date, ip_pool_id=ip_pool_id
            ).values()
        )
        return JsonResponse({"result": True, "data": events})
