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
import logging
from datetime import timedelta

from celery.schedules import crontab
from celery.task import periodic_task, task
from django.db import transaction

from blueking.component.shortcuts import get_client_by_user
from home_application.enums import ASSIGNED_EXCEEDED_TIME, UNASSIGNED_BUT_EXISTS_CMDB, UNASSIGNED_ONLINE
from home_application.models import (
    AbnormalIp,
    CmdbSync,
    CmdbSyncRecord,
    IpNet,
    IpPoolEventLog,
    IpPools,
    Ips,
    OperationLog,
    Settings,
)
from home_application.utilities.bk_helper.cmdb_sync_utils import CMDBSync
from home_application.utilities.ip_helper.ip_scan import IPScan
from home_application.utilities.ip_helper.ip_tools import get_ip_range

logger = logging.getLogger("celery")


@periodic_task(run_every=crontab(minute="0", hour="1", day_of_week="*"))
def ping_check():
    ips = Ips.objects.filter(ip_net__isnull=False).values_list("ip", flat=True).distinct()
    if not ips:
        return
    check_ip_list(set(ips))


def check_ip_list(ip_set=None):
    ip_scan = IPScan()
    try:
        scan_ips = ip_scan.net_scan(ip_set)
    except Exception as e:
        logger.exception(e)
        return
    online_ips = list(ip_set.intersection(scan_ips))
    offline_ips = list(ip_set.difference(scan_ips))
    date_now = datetime.datetime.now()
    Ips.objects.filter(ip__in=online_ips).update(scan_at=date_now, online_status=True)
    Ips.objects.filter(ip__in=offline_ips).update(scan_at=date_now, online_status=False)
    Ips.objects.filter(ip__in=offline_ips, offline_at__isnull=True).update(offline_at=date_now)


@task()
def create_ip_by_ip_pool(ip_pool: IpPools):
    ip_net_list = ip_pool.ipnet_set.all()
    for i in ip_net_list:
        create_by_ip_net(i)


@task()
def create_ip_by_ip_nets(ip_net_list):
    for i in ip_net_list:
        create_by_ip_net(i)


@task()
def create_by_ip_nets(ip_net_list, username="admin"):
    for i in ip_net_list:
        create_by_ip_net(i, username)


@task
def create_by_ip_net(ip_net: IpNet, username="admin"):
    child_ip = get_ip_range(ip_net.ip_net)
    try:
        add_ips, update_ips = update_or_create_ip_list_by_net(child_ip, ip_net)
        with transaction.atomic():
            Ips.objects.bulk_create(add_ips, batch_size=100)
            Ips.objects.bulk_update(update_ips, ["ip_net", "reserve_status"], batch_size=100)
            OperationLog.objects.create(
                operate_type=OperationLog.ADD,
                operate_obj="IP管理",
                operator=username,
                operate_detail="根据子网:{} 批量创建IP".format(ip_net.ip_net),
                result=True,
            )
    except Exception as e:
        logger.exception(e)


def update_or_create_ip_list_by_net(child_ip, ip_net):
    add_ips = []
    update_ips = []
    dns_list = ip_net.dns.split(",")
    ip_list = child_ip[1:-1]
    exist_ip = {i.ip: i for i in Ips.objects.filter(ip__in=ip_list)}
    for i in ip_list:
        ip = str(i)
        reserve_status = ip == ip_net.gateway or ip in dns_list
        if ip in exist_ip:
            ip_old = exist_ip[ip]
            ip_old.ip_net = ip_net
            ip_old.reserve_status = ip_old.reserve_status | reserve_status
            update_ips.append(ip_old)
        else:
            add_ips.append(
                Ips(
                    ip=ip,
                    ip_net=ip_net,
                    allocate_status=Ips.NO_DISTRIBUTION,
                    reserve_status=reserve_status,
                    custom_attr=[],
                    create_by=ip_net.create_by,
                    update_by=ip_net.update_by,
                    gateway=ip_net.gateway,
                    dns=ip_net.dns,
                    bk_cloud_id=ip_net.bk_cloud_id,
                    description="子网创建生成",
                )
            )
    return add_ips, update_ips


@task()
def cmdb_sync_task(sync_list):
    sync_status = Settings.objects.get(key="cmdb_sync_status")
    if sync_status.value != "false":
        return
    sync_status.value = "true"
    sync_status.save()
    client = get_client_by_user("admin")
    ip_list = list(Ips.objects.all())
    ip_map = {i.ip: i for i in ip_list}
    abnormal_rules = Settings.objects.get(key="abnormal_rules").extra
    if abnormal_rules:
        try:
            enable_rule = [rule for rule in abnormal_rules if rule["rule_code"] == UNASSIGNED_BUT_EXISTS_CMDB][0][
                "enabled"
            ]
        except Exception as e:
            logger.exception(e)
            enable_rule = False
    else:
        enable_rule = False
    sync_record = CmdbSyncRecord.objects.all().values_list("cmdb_sync_id", "ip__ip").order_by().distinct()
    sync_map = {}
    for sync_id, ip in sync_record:
        sync_map.setdefault(sync_id, set()).add(ip)
    try:
        for sync_obj in sync_list:
            sync_client = CMDBSync(sync_obj, client, ip_map, enable_rule, sync_map)
            sync_client.start_sync()
            new_ips = list(Ips.objects.filter(ip__in=[i.ip for i in sync_client.add_ip_list]))
            new_ip_map = {i.ip: i for i in new_ips}
            ip_map.update(new_ip_map)
    except Exception as e:
        logger.exception(e)
    sync_status.value = "false"
    sync_status.save()


@periodic_task(run_every=timedelta(days=1))
def cmdb_sync():
    sync_data = CmdbSync.objects.filter(sync=True)
    cmdb_sync_task(list(sync_data))


@periodic_task(run_every=timedelta(days=1))
def abnormal_check():
    abnormal_rules = Settings.objects.get(key="abnormal_rules").extra
    if not abnormal_rules:
        return
    rules = [
        i for i in abnormal_rules if i["rule_code"] in [UNASSIGNED_ONLINE, ASSIGNED_EXCEEDED_TIME] and i["enabled"]
    ]
    if not rules:
        return
    ip_list = []
    for rule in rules:
        if rule["rule_code"] == UNASSIGNED_ONLINE:
            # 未分配但在线
            rule_ip_list = list(
                Ips.objects.filter(allocate_status=Ips.NO_DISTRIBUTION, online_status=True).values_list("id", flat=True)
            )
            AbnormalIp.objects.filter(ip__ip__in=rule_ip_list).delete()
            ip_list.extend([AbnormalIp(abnormal_code=AbnormalIp.UNASSIGNED_ONLINE, ip_id=i) for i in rule_ip_list])
        elif rule["rule_code"] == ASSIGNED_EXCEEDED_TIME:
            # 已分配但离线超过时限
            ip_offline = int(Settings.objects.get(key="ip_offline").value)
            now = datetime.datetime.now()
            offline_time = now - datetime.timedelta(days=ip_offline)
            abnormal_ip = Ips.objects.filter(
                allocate_status=Ips.DISTRIBUTION, online_status=False, offline_at__lt=offline_time
            ).values("id", "ip", "offline_at")
            AbnormalIp.objects.filter(ip_id__in=[i["id"] for i in abnormal_ip]).delete()
            ip_list.extend(
                [
                    AbnormalIp(
                        abnormal_code=AbnormalIp.ASSIGNED_EXCEEDED_TIME,
                        ip=i["ip"],
                        remark="ip:{} 已离线{} 天".format(i["ip"], now - i["offline_at"]),
                    )
                    for i in abnormal_ip
                ]
            )
    if ip_list:
        AbnormalIp.objects.bulk_create(ip_list, batch_size=100)


def get_ip_pool_summary(ip_list):
    total_ip = len(ip_list)
    used_ip = len([i for i in ip_list if i["allocate_status"] != Ips.NO_DISTRIBUTION])
    available_count = len(
        [i for i in ip_list if i["allocate_status"] == Ips.NO_DISTRIBUTION and not i["reserve_status"]]
    )
    saved_count = len([i for i in ip_list if i["reserve_status"]])
    usage_rate = "{:.2f}%".format((used_ip / total_ip) * 100) if total_ip else "0%"
    return {
        "total_ip": total_ip,
        "used_ip": used_ip,
        "available_count": available_count,
        "saved_count": saved_count,
        "usage_rate": usage_rate,
    }


@periodic_task(run_every=crontab(minute="0", hour="0", day_of_week="*"))
def daily_ip_pool_summary():
    ip_pools = IpPools.objects.all().values_list("id", flat=True)
    ip_net_list = IpNet.objects.filter(ip_pool_id__in=ip_pools).values_list("id", flat=True)
    ip_list = Ips.objects.filter(ip_net_id__in=ip_net_list).values(
        "id", "ip_net__ip_pool_id", "allocate_status", "reserve_status"
    )
    log_list = []
    for pool_id in ip_pools:
        try:
            pool_ips = [i for i in ip_list if i["ip_net__ip_pool_id"] == pool_id]
            log_list.append(
                IpPoolEventLog(
                    ip_pool_id=pool_id,
                    event_type=IpPoolEventLog.SUMMARY,
                    event=get_ip_pool_summary(pool_ips),
                )
            )
        except Exception as e:
            logger.exception(e)
    IpPoolEventLog.objects.bulk_create(log_list, batch_size=100)
