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
import base64
import datetime
import json
import os
from json import loads

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.views import View
from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask
from djcelery.schedulers import DatabaseScheduler
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from blueking.component.shortcuts import get_client_by_user
from home_application.celery_tasks import cmdb_sync_task
from home_application.mixins import ApiGenericMixin
from home_application.models import CmdbSync, CmdbSyncRecord, CustomAttr, OperationLog, Settings
from home_application.sys_management.serializers import (
    CmdbSearch,
    CmdbSerializer,
    OperationLogSearch,
    OperationLogSerializer,
    SettingSerializer,
    SyncRecordSearch,
    SyncRecordSerializer,
)
from home_application.utilities.sys_helper.file_check import UploadFileCheck


class Cmdb(ApiGenericMixin, ModelViewSet):
    # 序列化
    queryset = CmdbSync.objects.all()
    serializer_class = CmdbSerializer
    search_fields = [
        "ip",
        "name",
        "model_id",
        "bk_cloud_id",
    ]
    filter_class = CmdbSearch

    @action(methods=["GET"], detail=False)
    def choice_model(self, request):
        """
        获取cmdb模型
        """
        client = get_client_by_user("admin")
        res = client.cc.search_objects()
        if not res["result"]:
            return JsonResponse(res)
        data = [{"name": i["bk_obj_name"], "model_id": i["bk_obj_id"]} for i in res["data"]]
        return JsonResponse({"result": True, "data": data})

    @action(methods=["POST"], detail=False)
    def choice_attr(self, request):
        """
        获取cmdb属性
        """
        client = get_client_by_user("admin")
        res = client.cc.search_object_attribute({"bk_obj_id": request.data["model"]})
        if not res["result"]:
            return JsonResponse(res)
        data = [{"bk_property_id": i["bk_property_id"], "bk_property_name": i["bk_property_name"]} for i in res["data"]]
        return JsonResponse({"result": True, "data": data})

    @action(methods=["GET"], detail=True)
    def get_attr(self, request, *args, **kwargs):
        """
        获取属性映射
        """
        sync_obj = self.get_object()
        client = get_client_by_user("admin")
        kwargs = {"bk_obj_id": sync_obj.model_id}
        res = client.cc.search_object_attribute(kwargs)
        if not res["result"]:
            return JsonResponse(res)
        attr_list = [
            {
                "bk_property_id": i["bk_property_id"],
                "bk_property_name": i["bk_property_name"],
                "is_cmdb_enum": i["bk_property_type"] == "enum",
            }
            for i in res["data"]
        ]
        # 获取IPS自定义属性
        custom_attr_data = list(
            CustomAttr.objects.filter(type=CustomAttr.IPS).values(
                bk_property_id=F("name"), bk_property_name=F("display_name")
            )
        )
        attribute_map = sync_obj.attribute_map
        default_attr_data = [
            {"bk_property_id": "ip", "bk_property_name": "ip地址"},
            {"bk_property_id": "bk_cloud_id", "bk_property_name": "云区域ID"},
            {"bk_property_id": "gateway", "bk_property_name": "网关"},
            {"bk_property_id": "dns", "bk_property_name": "DNS"},
        ]
        data = {
            "CMDB": attr_list,
            "IPAM": default_attr_data + custom_attr_data,
            "attribute_map": attribute_map,
        }
        return JsonResponse({"result": True, "data": data})


class CmdbPeri(View):  # noqa
    def get(self, request):  # noqa
        task_template = "home_application.sys_management.celery_tasks.cmdb_sync"
        try:
            peri_obj = PeriodicTask.objects.get(name=task_template)
            last_time = peri_obj.last_run_at
            time_num = int(IntervalSchedule.objects.get(id=peri_obj.interval_id).every) // 3600
            if time_num % 24 == 0:
                period = str(time_num // 24) + "d"
            else:
                period = str(time_num) + "h"
            return JsonResponse(
                {"result": True, "data": {"last_time": last_time, "period": period}, "message": ""}, safe=False
            )
        except Exception as e:
            return JsonResponse({"result": False, "data": "", "message": str(e)}, safe=False)

    def post(self, request):  # noqa
        data = loads(request.body)
        try:
            task_template = "home_application.sys_management.celery_tasks.cmdb_sync"
            # 新增最新周期任务
            every = int(data["period"][0:-1])
            if "d" in data["period"]:
                t = datetime.timedelta(days=every)
            else:
                t = datetime.timedelta(hours=every)
            schedule_dict = {"schedule": t, "args": [], "kwargs": None, "task": task_template, "enabled": 1}
            DatabaseScheduler.create_or_update_task(task_template, **schedule_dict)
            return JsonResponse({"result": True, "data": data, "message": None})
        except Exception as e:
            return JsonResponse({"result": False, "data": "", "message": str(e)})


class MakeSync(View):
    def get(self, request, pk):  # noqa
        sync_status = Settings.objects.get(key="cmdb_sync_status")
        if sync_status.value == "false":
            sync_obj = CmdbSync.objects.get(id=pk)
            cmdb_sync_task.delay([sync_obj])
            return JsonResponse({"result": True})
        return JsonResponse({"result": False, "message": "同步正在进行，请稍后重试！"})


class SyncRecord(ApiGenericMixin, ModelViewSet):
    # 序列化
    queryset = CmdbSyncRecord.objects.all()
    serializer_class = SyncRecordSerializer
    filter_class = SyncRecordSearch


class OpeLog(ApiGenericMixin, ModelViewSet):
    # 序列化
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    filter_class = OperationLogSearch


class Setting(ApiGenericMixin, ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingSerializer

    @action(methods=["POST"], detail=False)
    def update_logo(self, request):
        username = request.user.username
        file_obj = request.FILES.get("file", "")
        summary = "修改系统Logo"
        if not file_obj:
            default_logo_path = os.path.join(settings.PROJECT_ROOT, "static/img/ip-mgmt.png")
            with open(default_logo_path, "rb") as logo_file:
                img_base64 = base64.b64encode(logo_file.read()).decode("utf8")
            summary = "恢复默认系统Logo"
            content_type = "image/png"
        else:
            UploadFileCheck(file_obj).image_file_check()
            img_base64 = base64.b64encode(file_obj.read()).decode("utf8")
            content_type = file_obj.content_type
        Settings.objects.filter(key="system_logo").update(value=img_base64, desc="系统默认Logo")
        Settings.objects.filter(key="logo_content_type").update(value=content_type)
        OperationLog.objects.create(
            operator=username, operate_type=OperationLog.MODIFY, operate_obj="Logo", operate_detail=summary, result=True
        )
        return JsonResponse({"result": True})

    @action(methods=["GET"], detail=False)
    def get_logo(self, request):
        sys_value = Settings.objects.get(key="system_logo")
        logo_data = base64.b64decode(sys_value.value)
        content_type = Settings.objects.get(key="logo_content_type").value
        return HttpResponse(content=logo_data, content_type=content_type)

    @action(methods=["POST"], detail=False)
    def edit_sys_setting(self, request):
        json_data = request.data
        key_list = ["ping_check"]
        task_name_list = [f"home_application.celery_tasks.{i}" for i in key_list]
        setting_list = []
        crontab_list = []  # noqa
        all_settings = list(Settings.objects.filter(key__in=key_list + ["abnormal_rules"]))
        settings_map = {i.key: i for i in all_settings}
        date_now = datetime.datetime.now()
        task_list = list(PeriodicTask.objects.filter(name__in=task_name_list))
        schedule_map = {i.name: i.crontab for i in task_list}
        for key in key_list:
            if not json_data[key]:
                continue
            set_obj, cron_obj = self.update_settings(key, json_data[key], settings_map, schedule_map)
            setting_list.append(set_obj)
            crontab_list.append(cron_obj)
        if json_data["abnormal_rules"]:
            setting_obj = settings_map.get("abnormal_rules")
            setting_obj.value = json.dumps(json_data["abnormal_rules"])
            setting_obj.extra = json_data["abnormal_rules"]
            setting_list.append(setting_obj)
        with transaction.atomic():
            CrontabSchedule.objects.bulk_update(crontab_list, ["day_of_month"])
            PeriodicTask.objects.filter(name__in=task_name_list).update(date_changed=date_now)
            Settings.objects.bulk_update(setting_list, ["value", "extra"])
        return JsonResponse({"result": True})

    @staticmethod
    def update_settings(task_name, task_time, settings_map, schedule_map):
        schedule_obj = schedule_map.get(f"home_application.celery_tasks.{task_name}")
        schedule_obj.day_of_month = f"*/{task_time}"
        setting_obj = settings_map.get(task_name)
        setting_obj.value = task_time
        return setting_obj, schedule_obj

    @action(methods=["GET"], detail=False)
    def login_info(self, request):
        resp = JsonResponse(
            {
                "result": True,
                "data": {
                    "username": request.user.username,
                    "logout_url": settings.LOGOUT_URL,
                    "super": request.user.is_superuser,
                },
            }
        )
        return resp
