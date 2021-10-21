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
from rest_framework import status
from rest_framework.response import Response

from home_application.constants import ResponseCodeStatus


class ApiGenericMixin(object):
    """API视图类通用函数"""

    permission_classes = ()

    def finalize_response(self, request, response, *args, **kwargs):
        """统一数据返回格式"""
        # 文件导出时response {HttpResponse}
        if not isinstance(response, Response):
            return response
        if response.data is None:
            response.data = {"result": True, "code": ResponseCodeStatus.OK, "message": "success", "data": []}
        elif isinstance(response.data, (list, tuple)):
            response.data = {
                "result": True,
                "code": ResponseCodeStatus.OK,
                "message": "success",
                "data": response.data,
            }
        elif isinstance(response.data, dict) and not ("code" in response.data and "result" in response.data):
            response.data = {
                "result": True,
                "code": ResponseCodeStatus.OK,
                "message": "success",
                "data": response.data,
            }
        if response.status_code == status.HTTP_204_NO_CONTENT and request.method == "DELETE":
            response.status_code = status.HTTP_200_OK

        return super(ApiGenericMixin, self).finalize_response(request, response, *args, **kwargs)


class ApiGatewayMixin(object):
    """对外开放API返回格式统一
    错误码返回规范为数字：
        正确：0
        错误：39XXXXX
    """

    permission_classes = ()

    def finalize_response(self, request, response, *args, **kwargs):
        """统一数据返回格式"""

        if not isinstance(response, Response):
            return response

        if response.data is None:
            response.data = {"result": True, "code": 0, "message": "success", "data": []}
        elif isinstance(response.data, (list, tuple)):
            response.data = {
                "result": True,
                "code": 0,
                "message": "success",
                "data": response.data,
            }
        elif isinstance(response.data, dict) and not ("code" in response.data and "result" in response.data):
            response.data = {
                "result": True,
                "code": 0,
                "message": "success",
                "data": response.data,
            }

        return super(ApiGatewayMixin, self).finalize_response(request, response, *args, **kwargs)
