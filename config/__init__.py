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

from __future__ import absolute_import

import os
from urllib.parse import urlparse

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app

__all__ = ["celery_app", "RUN_VER", "APP_CODE", "SECRET_KEY", "BK_URL", "BASE_DIR", "APP_ID", "BK_PAAS_DOMAIN"]


# app 基本信息


def get_env_or_raise(key):
    """Get an environment variable, if it does not exist, raise an exception"""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            'Environment variable "{}" not found, you must set this variable to run this application.'.format(key)
        )
    return value


# 应用 ID
APP_ID = APP_CODE = os.getenv("APP_ID", "")
# 应用用于调用云 API 的 Secret
APP_TOKEN = SECRET_KEY = os.getenv("APP_TOKEN", "")

# SaaS运行版本，如非必要请勿修改
RUN_VER = "open"
# 蓝鲸SaaS平台URL，例如 http://paas.bking.com
BK_PAAS_HOST = os.getenv("BK_PAAS_HOST", "")
BK_URL = os.getenv("BK_URL", BK_PAAS_HOST)
BK_PAAS_DOMAIN = urlparse(BK_PAAS_HOST).hostname

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.split(PROJECT_PATH)[0]
