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
from home_application.exceptions import RequestFileTypeError


class UploadFileCheck(object):
    def __init__(self, file_obj):
        self.file_obj = file_obj

    def _check_mime_type(self, correct_mime_type):
        # 限制文件MIME Type
        if self.file_obj.content_type not in correct_mime_type:
            raise RequestFileTypeError()

    def _check_file_name(self, end_rule=None):
        # 限制文件后缀
        if end_rule:
            file_name = self.file_obj.name.strip('"')
            if not file_name.endswith(end_rule):
                raise RequestFileTypeError()

    def template_file_check(self):
        """监控模板检查"""
        self._check_mime_type(["application/xml", "text/xml"])
        self._check_file_name(end_rule="xml")

    def image_file_check(self):
        """图片文件检查"""
        self._check_mime_type(["image/png", "image/jpeg", "image/svg+xml"])
        self._check_file_name(end_rule=("jpg", "jpeg", "png", "svg"))
