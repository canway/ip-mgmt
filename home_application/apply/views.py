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

from django.db import transaction
from django.forms.models import model_to_dict
from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet

from home_application.apply.filter import ApplyFilter
from home_application.apply.serializers import ApplySerializer
from home_application.mixins import ApiGenericMixin
from home_application.models import Apply, IpNet, IpPools, Ips


class ApplyViewSet(ApiGenericMixin, ModelViewSet):
    # 序列化
    queryset = Apply.objects.all().order_by("-id")
    serializer_class = ApplySerializer
    filter_class = ApplyFilter

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        params = request.data
        username = request.user.username or ""
        apply = Apply.create_apply(params, username)
        result, ips = self.format_ips(apply, params)
        if not result:
            return JsonResponse({"result": False, "message": "当前子网没有足够的可用ip！"})
        Ips.objects.filter(ip__in=ips).update(
            reserve_status=True,
            expired_at=apply.expired_time,
            allocate_way=apply.apply_way,
            business_system=apply.business_system,
            owner=apply.apply_person,
            remark=apply.apply_reason,
            member=params.get("member", ""),
        )
        if apply.apply_way.upper() != Apply.MANUAL:
            self.set_apply_by_manual(apply, ips, params, username)
        return JsonResponse({"result": True, "message": "申请成功！"})

    @staticmethod
    def set_apply_by_manual(apply, ips, params, username):
        ip_pool = IpPools.objects.get(id=params["apply_ip_pool"])
        ip_net = IpNet.objects.get(id=params["apply_ip_net"])
        Ips.objects.filter(ip__in=ips).update(
            allocate_status=Ips.DISTRIBUTION,
            reserve_status=False,
            allocate_at=datetime.datetime.now(),
        )
        apply.auditor = username
        apply.audit_time = datetime.datetime.now()
        apply.apply_status = Apply.APPROVAL
        apply.saved_ips = {
            "ip_pool": model_to_dict(ip_pool),
            "sub_net_work": model_to_dict(ip_net),
            "ip_list": ips,
        }
        apply.save()

    @staticmethod
    def format_ips(apply, params):
        if params.get("apply_ip_count"):
            ip_list = list(
                Ips.objects.filter(
                    ip_net_id=params["apply_ip_net"],
                    allocate_status=Ips.NO_DISTRIBUTION,
                    reserve_status=False,
                )
                .values_list("ip", flat=True)
                .order_by("id")
            )
            if len(ip_list) < int(params["apply_ip_count"]):
                return False, []
            ips = ip_list[: int(params["apply_ip_count"])]
        else:
            ips = list(
                Ips.objects.filter(
                    ip_net_id=params["apply_ip_net"],
                    allocate_status=Ips.NO_DISTRIBUTION,
                    reserve_status=False,
                    id__in=apply.apply_ips,
                ).values_list("ip", flat=True)
            )
        return True, ips
