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
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from home_application import views
from home_application.apply.views import ApplyViewSet
from home_application.custom_attributes.views import CustomAttrViewSet
from home_application.ip.views import IpViewSet
from home_application.ip_abnormal.views import IpAbnormal
from home_application.ip_net.views import IpNetList
from home_application.ip_pool.views import IpPoolsViewSet
from home_application.offline_except.views import OfflineExceptViewSet
from home_application.sys_management.open_url import urlpatterns as open_api_url
from home_application.sys_management.views import Cmdb, CmdbPeri, MakeSync, OpeLog, Setting, SyncRecord

urlpatterns = [
    url(r"^$", views.home),
    url(r"^login_info/$", views.login_info),
    url(r"^cmdb/period/$", CmdbPeri.as_view()),
    url(r"^make_sync/(?P<pk>\d+)/$", MakeSync.as_view()),
    url(r"^open/$", views.get_ip_pool),
]

routers = DefaultRouter(trailing_slash=True)
routers.register(r"ip_pool", IpPoolsViewSet, basename="ip_pool_views")
routers.register(r"offline_except", OfflineExceptViewSet)
routers.register(r"ip", IpViewSet, basename="ip_views")
routers.register(r"ip_net", IpNetList, basename="ip_net_views")
routers.register(r"ip_abnormal", IpAbnormal, basename="ip_ipAbnormal_views")
routers.register(r"custom_attr", CustomAttrViewSet, basename="custom_attr_views")
routers.register(r"apply", ApplyViewSet, basename="apply_views")
routers.register(r"cmdb", Cmdb, basename="cmdb_views")
routers.register(r"sync_record", SyncRecord, basename="sync_record")
routers.register(r"operation_log", OpeLog, basename="operation_log")
routers.register(r"sys", Setting, basename="settings_views")
urlpatterns += routers.urls
urlpatterns += open_api_url
