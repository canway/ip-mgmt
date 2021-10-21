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
import os

from config import RUN_VER

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 预发布环境
RUN_MODE = "STAGING"

# 只对预发布环境日志级别进行配置，可以在这里修改
# from blueapps.conf.log import set_log_level # noqa
# LOG_LEVEL = "ERROR"
# LOGGING = set_log_level(locals())

# 预发布环境数据库可以在这里配置

DATABASES.update(  # noqa
    {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("BKAPP_DB_NAME", ""),  # 数据库名
            "USER": os.getenv("BKAPP_DB_USERNAME", ""),  # 数据库用户
            "PASSWORD": os.getenv("BKAPP_DB_PASSWORD", ""),  # 数据库密码
            "HOST": os.getenv("BKAPP_DB_HOST", ""),  # 数据库主机
            "PORT": os.getenv("BKAPP_DB_PORT", "3306"),  # 数据库端口
        },
    }
)  # noqa
