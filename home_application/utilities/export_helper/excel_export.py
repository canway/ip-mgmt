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
from io import BytesIO

import xlsxwriter
from django.http import HttpResponse, JsonResponse

from blueapps.utils.logger import logger
from home_application.models import CustomAttr, OperationLog


def make_excel(item_list, filename, excel_data):
    bio = BytesIO()
    workbook = xlsxwriter.Workbook(bio)
    worksheet = workbook.add_worksheet()
    header_format = workbook.add_format({"num_format": "@", "text_wrap": True, "valign": "vcenter", "indent": 1})
    cols_num = excel_data.__len__()
    rows_num = excel_data[0].keys().__len__()
    with_op = 20
    for col in range(cols_num):
        for row in range(rows_num):
            data = excel_data[col][item_list[row]]
            worksheet.set_column(col, row, with_op)
            if type(data) == dict:
                worksheet.write(col, row, data["name"], header_format)
                worksheet.data_validation(col, row, col, row, {"validate": "list", "source": data["list"]})
            else:
                worksheet.write(col, row, data, header_format)
    workbook.close()
    bio.seek(0)
    response = HttpResponse(bio.getvalue(), content_type="APPLICATION/OCTET-STREAM")
    file_name = "attachment; filename={}.xlsx".format(filename.encode("utf-8").decode("ISO-8859-1"))
    response["Content-Disposition"] = file_name
    return response


def export_excel_data(custom_attrs, detail, filename, title):
    custom_attr_map = dict(custom_attrs.values_list("name", "display_name"))
    title.update(custom_attr_map)
    to_excel_data = [title]
    exclude_key = ["remark", "offline_days", "ip_pool", "ip_net", "abnormal_code"]
    update_keys = [i for i in title.keys() if i not in exclude_key]
    for data in detail:
        ip_obj = data["ip_obj"]
        update_data = {i: ip_obj.get(i, "") for i in update_keys}
        data.update(update_data)
        cus_map = {i["name"]: i.get("value", "") for i in ip_obj["custom_attr"]}
        cus_dict = {i: cus_map.get(i, "") for i in custom_attr_map.keys()}
        data.update(cus_dict)
        to_excel_data.append(data)
    data_key = list(title.keys())
    return make_excel(data_key, filename, to_excel_data)


def format_data_and_export_excel(title, detail, filename, attr_type, operate_obj, username, operate_detail):
    custom_attr_map = dict(CustomAttr.objects.filter(type=attr_type).values_list("name", "display_name"))
    title.update(custom_attr_map)
    to_excel_data = [title]
    for data in detail:
        cus_map = {i["name"]: i.get("value", "") for i in data["custom_attr"]}
        for attr in custom_attr_map.keys():
            data[attr] = cus_map.get(attr, "")
        to_excel_data.append(data)
    data_key = list(title.keys())
    log = OperationLog(
        operate_type=OperationLog.EXEC,
        operate_obj=operate_obj,
        operator=username,
        operate_detail=operate_detail,
        result=True,
    )
    try:
        result = make_excel(data_key, filename, to_excel_data)
    except Exception as e:
        logger.exception(e)
        result = JsonResponse({"result": False, "message": str(e)})
        log.result = False
    log.save()
    return result
