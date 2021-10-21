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
import json

import xlrd
from django.db.models import Count
from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from blueapps.account.models import logger
from home_application.celery_tasks import check_ip_list
from home_application.enums import (
    ALLOCATE_STATUS_DICT,
    IP_ADDRESS_MANAGEMENT,
    IP_ADDRESS_TITLE,
    IMPORT_IP_ASSIGNMENT_TEMPLATE_TITLE,
)
from home_application.exceptions import ExcelFormatError
from home_application.ip.ip_filters import IpFilterSet
from home_application.ip.serializers import IpSerializer
from home_application.mixins import ApiGenericMixin
from home_application.models import CustomAttr, IpNet, Ips, OperationLog, Settings
from home_application.utilities.export_helper.excel_export import make_excel, format_data_and_export_excel
from home_application.utilities.ip_helper.ip_tools import format_ip_range_to_ip, is_ipv4


class IpViewSet(ApiGenericMixin, ModelViewSet):
    queryset = Ips.objects.all()
    serializer_class = IpSerializer
    search_fields = [
        "name",
        "ip",
        "ip_net__ip_pool__name",
        "ip_net__ip_net",
        "create_by",
        "update_by",
        "description",
        "remark",
    ]
    filter_class = IpFilterSet

    @action(methods=["GET"], detail=False)
    def status_check(self, request, *args, **kwargs):
        ips = request.GET["ips"]
        check_ip_list(set(ips.split(",")))
        return JsonResponse({"result": True})

    @action(methods=["POST"], detail=False)
    def batch_reserve(self, request, *args, **kwargs):
        params = request.data
        username = request.user.username
        ip_list = {i for i in params["ips"] if i}
        self.format_ip_obj(params["ip_net"], params["remark"], username, ip_list)
        OperationLog.objects.create(
            operate_type=OperationLog.MODIFY,
            operate_obj=IP_ADDRESS_MANAGEMENT,
            operator=request.user.username,
            operate_detail=json.dumps(request.data),
            result=True,
        )
        return JsonResponse({"result": True})

    @staticmethod
    def format_ip_obj(ip_net_id, remark, username, reserve_ips):
        fields = ["reserve_status", "update_at", "update_by", "remark"]
        total_result = []
        real_ip_list = {i for i in reserve_ips if "-" not in i}
        need_change_ips = reserve_ips - real_ip_list
        for ip in need_change_ips:
            ips = set(format_ip_range_to_ip(ip))
            real_ip_list.update(ips)
        date_now = datetime.datetime.now()
        ip_list = Ips.objects.filter(ip__in=real_ip_list, ip_net_id=ip_net_id)
        for real_ip in ip_list:
            if real_ip.reserve_status:
                continue
            real_ip.reserve_status = True
            real_ip.update_at = date_now
            real_ip.update_by = username
            real_ip.remark = remark if not real_ip.remark else "{},{}".format(real_ip.remark, remark)
            total_result.append(real_ip)
        Ips.objects.bulk_update(total_result, fields, batch_size=100)

    @action(methods=["POST"], detail=False)
    def check_ip(self, request, *args, **kwargs):
        params = request.data
        ip_net_id = params.get("ip_net", 0)
        reserve_ips = params.get("ips", [])
        ip_list = list(Ips.objects.filter(ip_net_id=ip_net_id).values_list("ip", flat=True).distinct())
        msg_list, total_result = self.check_ip_exists(ip_list, {i for i in reserve_ips if i})
        error_message = "\n".join(msg_list)
        result = not msg_list
        return JsonResponse({"result": result, "data": total_result, "message": error_message})

    @staticmethod
    def check_ip_exists(ip_list, reserve_ips):
        msg_list = []
        total_result = []
        real_ip_list = {i for i in reserve_ips if "-" not in i}
        need_change_ips = reserve_ips - real_ip_list
        for ip in need_change_ips:
            try:
                ips = set(format_ip_range_to_ip(ip))
            except ValueError:
                msg = "{} 不是有效的IP范围表达式".format(ip)
                msg_list.append(msg)
            else:
                real_ip_list.update(ips)
        for ip in real_ip_list:
            if ip in ip_list:
                continue
            msg = "找不到IP:{0},或者IP:{0}不在网段内".format(ip)
            total_result.append({"result": False, "data": ip, "message": msg})
            msg_list.append(msg)
        return msg_list, total_result

    @action(methods=["POST"], detail=False)
    def batch_update(self, request, *args, **kwargs):
        params = request.data
        selected_ids = params.get("selected_ids", [])
        res = []
        fields = ["gateway", "dns", "reserve_status", "business_system", "description"]
        ip_list = Ips.objects.filter(id__in=selected_ids)
        cus_attrs = list(CustomAttr.objects.filter(type=CustomAttr.IPS).values_list("name", flat=True))
        for real_ip in ip_list:
            for field in fields:
                if not params.get(field):
                    continue
                setattr(real_ip, field, params[field])
            if params.get("expired_at") and real_ip.expired_at:
                real_ip.expired_at = datetime.datetime.strptime(params["expired_at"], "%Y-%m-%d")
            custom_attr_map = {i["name"]: i["value"] for i in real_ip.custom_attr}
            for att in cus_attrs:
                if not (att in params and params.get(att)):
                    continue
                custom_attr_map[att] = params[att]
            real_ip.custom_attr = [{"name": k, "value": v} for k, v in custom_attr_map.items()]
            res.append(real_ip)
        Ips.objects.bulk_update(res, fields + ["expired_at", "custom_attr"], batch_size=100)
        OperationLog.objects.create(
            operate_type=OperationLog.MODIFY,
            operate_obj=IP_ADDRESS_MANAGEMENT,
            operator=request.user.username,
            operate_detail=json.dumps(request.data),
            result=True,
        )
        return JsonResponse({"result": True, "message": "OK"})

    @action(methods=["POST"], detail=False)
    def recycle(self, request, *args, **kwargs):
        params = request.data
        selected_ids = params.get("selected_ids", [])
        has_warn = Ips.objects.filter(id__in=selected_ids).exclude(allocate_status=Ips.DISTRIBUTION).exists()
        if has_warn:
            return JsonResponse({"result": False, "message": "回收失败，待回收列表包含不是已分配状态的IP"})
        waiting_days = params.get("waiting_days", None)
        if not waiting_days:
            waiting_days = Settings.objects.get(key="recycle_waiting_days").value
        Ips.objects.filter(id__in=selected_ids).update(
            allocate_status=Ips.WAIT_RECOVERY,
            update_by=request.user.username,
            recycle_waiting_days=waiting_days,
        )
        OperationLog.objects.create(
            operate_type=OperationLog.EXEC,
            operate_obj=IP_ADDRESS_MANAGEMENT,
            operator=request.user.username,
            operate_detail="批量回收IP，详情：{}".format(json.dumps(request.data)),
            result=True,
        )
        return JsonResponse({"result": True})

    @action(methods=["get"], detail=False)
    def export_excel(self, request):
        return_dict = self.list(request)
        detail = list(return_dict.data)
        filename = "IP地址"
        title = IP_ADDRESS_TITLE
        operate_detail = json.dumps(request.data)
        attr_type = CustomAttr.IPS
        operate_obj = IP_ADDRESS_MANAGEMENT
        username = request.user.username
        return format_data_and_export_excel(title, detail, filename, attr_type, operate_obj, username, operate_detail)

    @action(methods=["post"], detail=False)
    def import_ip_allocation(self, request):
        # 获取前端提交的excel文件
        import_file = request.FILES.get("file")
        wb = xlrd.open_workbook(filename=None, file_contents=import_file.read())
        # 获取excel文件的第一个sheet
        table = wb.sheets()[0]
        rows = table.nrows
        # 设置表头
        row_values = table.row_values(0)
        head_dict = self.get_export_head(row_values)
        ip_net_map = dict(IpNet.objects.all().values_list("ip_net", "id"))
        ip_list = Ips.objects.all()
        ip_map = {f"{i.ip}-{i.ip_net_id}": i for i in ip_list}
        errors, update_list = self.format_excel_data(head_dict, ip_map, ip_net_map, rows, table)
        attr_list = ["remark", "business_system", "owner", "expired_at", "allocate_status", "allocate_at"]
        Ips.objects.bulk_update(update_list, attr_list, batch_size=100)
        OperationLog.objects.create(
            operate_type=OperationLog.EXEC,
            operate_obj=IP_ADDRESS_MANAGEMENT,
            operator=request.user.username,
            operate_detail="导入IP分配",
            result=True,
        )
        return JsonResponse({"result": True, "message": "\n".join(errors)})

    def format_excel_data(self, head_dict, ip_map, ip_net_map, rows, table):
        update_list = []
        errors = []
        now = datetime.datetime.now()
        for row in range(1, rows):
            try:
                row_values = table.row_values(row)
                ip_net = row_values[head_dict["ip_net"]]
                if ip_net not in ip_net_map:
                    errors.append(f"子网【{ip_net}】不存在")
                    continue
                ip_net_id = ip_net_map.get(ip_net)
                apply_ips = row_values[head_dict["apply_ips"]].strip().split(",")
                for temp_ip in apply_ips:
                    try:
                        real_ip = self.format_excel_ip(temp_ip, ip_net, ip_net_id, ip_map, row_values, head_dict, now)
                    except ExcelFormatError as err:
                        errors.append(str(err))
                    else:
                        update_list.append(real_ip)
            except BaseException as e:
                errors.append(str(e))
        return errors, update_list

    @staticmethod
    def format_excel_ip(temp_ip, ip_net, ip_net_id, ip_map, row_values, head_dict, now):
        if not is_ipv4(temp_ip):
            raise ExcelFormatError(f"IP【{temp_ip}】不合法")
        real_ip = ip_map.get(f"{temp_ip}-{ip_net_id}")
        if not real_ip:
            raise ExcelFormatError(f"子网【{ip_net}】下不存在IP【{temp_ip}】")
        if real_ip.reserve_status or real_ip.allocate_status != Ips.NO_DISTRIBUTION:
            raise ExcelFormatError(f"IP【{temp_ip}】处于保留状态或者不可分配装状态")
        real_ip.remark = row_values[head_dict["remark"]]
        real_ip.business_system = row_values[head_dict["business_system"]]
        real_ip.owner = row_values[head_dict["owner"]]
        try:
            real_ip.expired_at = datetime.datetime.strptime(row_values[head_dict["expired_at"]], "%Y-%M-%d")
        except ValueError:
            raise ExcelFormatError(f"IP【{temp_ip}】的过期时间【{row_values[head_dict['expired_at']]}】格式不对")
        real_ip.allocate_status = Ips.DISTRIBUTION
        real_ip.allocate_at = now
        return real_ip

    @staticmethod
    def get_export_head(row_values):
        head_dict = {}
        key_list = ["pool_name", "ip_net", "apply_ips", "business_system", "owner", "expired_at", "remark"]
        for col_index in range(0, len(row_values)):
            key = row_values[col_index].split("(")[1].strip(")")
            if key in key_list:
                head_dict[key] = col_index
        return head_dict

    @action(methods=["get"], detail=False)
    def download_template(self, request):
        try:
            filename = "导入IP分配模板"
            title = IMPORT_IP_ASSIGNMENT_TEMPLATE_TITLE
            to_excel_data = [title]
            data_key = list(title.keys())
            return make_excel(data_key, filename, to_excel_data)
        except BaseException as e:
            logger.exception(e)
            return JsonResponse({"result": False, "data": [], "message": str(e)})

    @action(methods=["get"], detail=False)
    def get_ip_summary(self, request):
        # 对allocate_status分组查询
        items = (
            Ips.objects.values("allocate_status").annotate(c=Count("allocate_status")).values("allocate_status", "c")
        )
        allocate_status_count_dict = {}
        total_count = 0
        for item in items:
            total_count += item["c"]
            allocate_status_count_dict[item["allocate_status"]] = item["c"]
        used = allocate_status_count_dict.get(Ips.DISTRIBUTION, 0)
        not_used = allocate_status_count_dict.get(Ips.NO_DISTRIBUTION, 0)
        recycling = allocate_status_count_dict.get(Ips.WAIT_RECOVERY, 0)
        recycled = allocate_status_count_dict.get(Ips.RECYCLED, 0)
        result = [
            {
                "status": ALLOCATE_STATUS_DICT[Ips.DISTRIBUTION],
                "count": used,
                "ratio": "{:.2f}%".format((used / total_count) * 100 if total_count != 0 else 0),
            },
            {
                "status": ALLOCATE_STATUS_DICT[Ips.NO_DISTRIBUTION],
                "count": not_used,
                "ratio": "{:.2f}%".format((not_used / total_count) * 100 if total_count != 0 else 0),
            },
            {
                "status": ALLOCATE_STATUS_DICT[Ips.WAIT_RECOVERY],
                "count": recycling,
                "ratio": "{:.2f}%".format((recycling / total_count) * 100 if total_count != 0 else 0),
            },
            {
                "status": ALLOCATE_STATUS_DICT[Ips.RECYCLED],
                "count": recycled,
                "ratio": "{:.2f}%".format((recycled / total_count) * 100 if total_count != 0 else 0),
            },
        ]
        return JsonResponse({"result": True, "data": result, "message": ""})
