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
from ast import literal_eval
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from home_application.apply.views import ApplyViewSet
from home_application.ip_net.views import IpNetList
from home_application.ip_pool.views import IpPoolsViewSet


def login_csrf_exempt(view_func):
    def wrapped_view(request, *args, **kwargs):
        request.user.username = "api"
        return view_func(request, *args, **kwargs)

    wrapped_view.login_exempt = True
    wrapped_view.csrf_exempt = True
    return wraps(view_func)(wrapped_view)


@login_csrf_exempt
def get_ip_pool(request):
    """获取地址池"""
    try:
        return IpPoolsViewSet.as_view({"get": "list"})(request)
    except BaseException as e:
        logging.exception(e)
        return JsonResponse({"result": False, "message": str(e), "data": []})


@login_csrf_exempt
def get_ip_net(request):
    """获取子网"""
    try:
        return IpNetList.as_view({"get": "list"})(request)
    except BaseException as e:
        logging.exception(e)
        return JsonResponse({"result": False, "message": str(e), "data": []})


@require_http_methods(["POST"])
@login_csrf_exempt
def apply_ip(request):
    """申请IP
    请求参数：
            {
            "expired_time":"2021-06-26",
            "apply_ip_pool":"1",
            "apply_ip_net":"1",
            "apply_ips":"",
            "apply_ip_count":"23",
            "apply_person":"zhangsan",
            "apply_reason":"申请来用",
            "business_system":"营销"
        }
    """
    try:
        params = literal_eval(request.body.decode(encoding="utf-8"))
        params["apply_way"] = "api"
        params["apply_type"] = "new"
        request._body = json.dumps(params).encode(encoding="utf-8")
        return ApplyViewSet.as_view({"post": "create"})(request)
    except BaseException as e:
        logging.exception(e)
        return JsonResponse({"result": False, "message": str(e), "data": []})
