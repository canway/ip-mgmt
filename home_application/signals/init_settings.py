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

from home_application.enums import ASSIGNED_EXCEEDED_TIME, RULE_CODE, UNASSIGNED_BUT_EXISTS_CMDB, UNASSIGNED_ONLINE
from home_application.models import Settings

RULE_CODE_DICT = dict(RULE_CODE)


def init_setting():
    if Settings.objects.all().count() == 0:
        setting_list = [
            Settings(key="ip_pool_threshold", value=0.85, desc="IP地址池告警阈值", extra=None),
            Settings(key="ip_offline", value=25, desc="IP离线阈值", extra=None),
            Settings(key="ping_check", value=25, desc="P在线状态检测周期", extra=None),
            Settings(
                key="abnormal_rules",
                value=13,
                desc="异常IP规则",
                extra=[
                    {
                        "enabled": True,
                        "rule_code": UNASSIGNED_ONLINE,
                        "rule_description": RULE_CODE_DICT[UNASSIGNED_ONLINE],
                    },
                    {
                        "enabled": True,
                        "rule_code": ASSIGNED_EXCEEDED_TIME,
                        "rule_description": RULE_CODE_DICT[ASSIGNED_EXCEEDED_TIME],
                    },
                    {
                        "enabled": True,
                        "rule_code": UNASSIGNED_BUT_EXISTS_CMDB,
                        "rule_description": RULE_CODE_DICT[UNASSIGNED_BUT_EXISTS_CMDB],
                    },
                ],
            ),
            Settings(key="ip_net_threshold", value=0.85, desc="IP子网告警阈值", extra=None),
            Settings(key="system_logo", value=None, desc="系统默认Logo", extra=None),
            Settings(key="logo_content_type", value="image/png", desc="系统默认Logo类型", extra=None),
            Settings(key="cmdb_sync_status", value="false", desc="cmdb同步状态", extra=None),
        ]
        Settings.objects.bulk_create(setting_list)


def init_all(**kwargs):
    init_setting()
