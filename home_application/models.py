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

from django.db import models
from django_mysql.models import JSONField


class Model(models.Model):
    """
    基础属性，一般模型都带有
    """

    name = models.CharField("名称", max_length=200, null=True, blank=True)
    create_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    update_at = models.DateTimeField("更新时间", auto_now=True, null=True)
    create_by = models.CharField("创建人", max_length=100, null=True, blank=True)
    update_by = models.CharField("修改人", max_length=100, null=True, blank=True)
    description = models.CharField("描述", max_length=500, null=True, blank=True)
    remark = models.CharField("备注", max_length=500, null=True, blank=True)

    class Meta:
        abstract = True


class IpPools(Model):
    """ip地址池"""

    WAITING_ENABLE = "1"
    ENABLED = "2"
    DISABLED = "3"
    DELETED = "4"
    POOL_STATUS = (
        (WAITING_ENABLE, "waiting_enable"),
        (ENABLED, "enabled"),
        (DISABLED, "disabled"),
        (DELETED, "deleted"),
    )

    name = models.CharField("名称", max_length=200, unique=True, default="")
    status = models.CharField("程序池状态", max_length=100, choices=POOL_STATUS, default=None)
    custom_attr = JSONField("自定义属性", null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def can_delete(self):
        ip_nets = self.ipnet_set.all()
        for ip_net in ip_nets:
            if not ip_net.can_delete():
                return False
        return True


class IpNet(Model):
    """子网段"""

    bk_cloud_id = models.IntegerField("云区域ID", null=True, blank=True)
    gateway = models.CharField("网关", max_length=100, null=True, blank=True)
    dns = models.CharField("DNS", max_length=100, null=True, blank=True)
    ip_net = models.CharField("网段", max_length=100)
    vlan_id = models.CharField("VLAN ID", max_length=100, null=True, blank=True)
    ip_pool = models.ForeignKey(IpPools, on_delete=models.CASCADE)
    business_system = models.CharField("业务系统", max_length=100, null=True, blank=True)
    owner = models.CharField("运维人员", max_length=100, null=True, blank=True)
    custom_attr = JSONField("自定义属性", null=True, blank=True)

    class Meta:
        ordering = ["-id"]

    def can_delete(self):
        return not self.ips_set.filter(allocate_status__in=[Ips.DISTRIBUTION, Ips.WAIT_RECOVERY]).exists()


class Ips(Model):
    """IP模型"""

    NO_DISTRIBUTION = "1"
    DISTRIBUTION = "2"
    WAIT_RECOVERY = "3"
    RECYCLED = "4"
    ALLOCATE_STATUS = ((NO_DISTRIBUTION, "未分配"), (DISTRIBUTION, "已分配"), (WAIT_RECOVERY, "待回收"), (RECYCLED, "已回收"))

    ip = models.CharField("ip", max_length=100)
    allocate_at = models.DateTimeField("分配时间", null=True, blank=True)
    expired_at = models.DateTimeField("过期时间", null=True, blank=True)
    allocate_status = models.CharField("分配状态", max_length=100, choices=ALLOCATE_STATUS)
    allocate_way = models.CharField("分配方式", max_length=100, null=True, blank=True)
    offline_at = models.DateTimeField("离线时间", null=True, blank=True)
    scan_at = models.DateTimeField("扫描时间", null=True, blank=True)
    online_status = models.BooleanField("在线状态", default=False)
    reserve_status = models.BooleanField("保留状态", default=False)
    business_system = models.CharField("业务系统", max_length=100, null=True, blank=True)
    is_cmdb_sync = models.BooleanField("是否来自于CMDB同步", default=False)
    recycle_waiting_days = models.IntegerField("回收等待天数", default=0)
    owner = models.CharField("ip所属者", max_length=100, null=True, blank=True)
    ip_net = models.ForeignKey(IpNet, on_delete=models.SET_NULL, null=True, blank=True)
    # 允许IP的云区域，网关，和dns跟子网的不一样
    bk_cloud_id = models.IntegerField("云区域ID", null=True, blank=True)
    gateway = models.CharField("网关", max_length=100, null=True, blank=True)
    dns = models.CharField("DNS", max_length=100, null=True, blank=True)
    custom_attr = JSONField("自定义属性", null=True, blank=True)
    member = models.CharField("运维人员", default="", max_length=200)


class IpPoolEventLog(models.Model):
    SUMMARY = "summary"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EVENT_TYPE = ((SUMMARY, "每日统计"), (CREATE, "创建"), (UPDATE, "更新"), (DELETE, "删除"))
    event_type = models.CharField(max_length=100, choices=EVENT_TYPE)
    when_time = models.DateTimeField(auto_now_add=True)
    ip_pool = models.ForeignKey(IpPools, on_delete=models.CASCADE)
    event = JSONField("事件详情", null=True, blank=True)


class AbnormalIp(models.Model):
    """
    异常IP，异常类型是确定的
    未分配但在线:每次扫描IP时会更新IP的在线离线状态，搜索数据库状态为未分配且状态在线的即可拿到这些异常IP，确认异常则将此记录从异常清单去除，但第二天还是会再次提醒
    已分配但离线超过时限：查数据库状态为已分配的IP且状态为离线的且离线时间超过限制的，确认异常则将此记录从异常清单去除，但第二天还是会再次提醒
    CMDB无此IP记录：上次拉取CMDB时还有此IP，这次拉取时就没有了，这种算异常，确认异常则清掉本地IP的来自于CMDB字段
    CMDB同步属性变动：CMDB属性映射了且点了冲突检测的，属性变化就触发这类异常，确认异常时CMDB属性覆盖Saas的属性
    本地无此IP但CMDB中存在：IP管理SaaS按理应规划了所有的IP，如果在CMDB同步时发现要同步过来的IP在本地没有则触发报错，确认异常则创建IP，子网和地址池先置为null
    未分配但CMDB中存在：CMDB同步时，从CMDB同步过来的IP在IP管理Saas中标记为未分配的，视为异常。确认异常则正常执行下一步，将Saas中IP置为已分配
    """

    UNASSIGNED_ONLINE = "1"
    ASSIGNED_EXCEEDED_TIME = "2"
    CMDB_NO_IP = "3"
    CMDB_ATTR_CHANGE = "4"
    NO_IP_BUT_EXISTS_CMDB = "5"
    UNASSIGNED_BUT_EXISTS_CMDB = "6"
    ABNORMAL_CODE = (
        (UNASSIGNED_ONLINE, "未分配但在线"),
        (ASSIGNED_EXCEEDED_TIME, "已分配但离线超过时限"),
        (CMDB_NO_IP, "CMDB无此IP记录"),
        (CMDB_ATTR_CHANGE, "CMDB同步属性变动"),
        (NO_IP_BUT_EXISTS_CMDB, "本地无此IP但CMDB中存在"),
        (UNASSIGNED_BUT_EXISTS_CMDB, "未分配但CMDB中存在"),
    )
    create_at = models.DateTimeField("创建时间", auto_now_add=True, null=True, blank=True)
    abnormal_code = models.CharField("异常编码", max_length=100, choices=ABNORMAL_CODE)
    remark = models.TextField("备注，描述", null=True, blank=True)
    checked = models.BooleanField("是否确认", null=True, default=False)
    ip = models.ForeignKey(Ips, on_delete=models.CASCADE, null=True)


class OfflineExcept(models.Model):
    """
    离线白名单
    """

    create_at = models.DateTimeField("创建时间", auto_now_add=True)
    create_by = models.CharField("创建者", max_length=100)
    ip = models.ForeignKey(Ips, on_delete=models.CASCADE)
    remark = models.CharField("备注", max_length=500)


class Apply(Model):
    """IP申请单"""

    API = "API"
    MANUAL = "MANUAL"
    ADMIN = "ADMIN"
    APPLY_WAY = ((API, "API申请"), (MANUAL, "网页申请"), (ADMIN, "管理员直接分配"))

    NEW = "new"
    RENEW = "renew"
    APPLY_TYPE = ((NEW, "IP申请"), (RENEW, "续约申请"))

    AUDITING = "auditing"
    REJECT = "reject"
    APPROVAL = "approval"
    SUBMITTING = "submiting"
    APPLY_STATUS = ((AUDITING, "待审核"), (REJECT, "已拒绝"), (APPROVAL, "已通过"), (SUBMITTING, "待提交"))

    expired_time = models.DateTimeField("过期时间")
    apply_way = models.CharField("申请方式", max_length=100, choices=APPLY_WAY)
    apply_type = models.CharField("申请类型", max_length=100, choices=APPLY_TYPE)
    apply_status = models.CharField("申请单状态", max_length=100, choices=APPLY_STATUS)
    auditor = models.CharField("审核人", max_length=100)
    audit_time = models.DateTimeField("审核时间", null=True, blank=True)
    apply_ip_pool = models.ForeignKey(IpPools, null=True, on_delete=models.SET_NULL)
    apply_ip_net = models.ForeignKey(IpNet, default=None, null=True, on_delete=models.SET_NULL)
    apply_ips = JSONField("申请的IP", null=True, blank=True)
    apply_ip_count = models.IntegerField("申请IP数量", default=0, null=True, blank=True)
    apply_person = models.CharField("申请人", max_length=100, null=True, blank=True)
    apply_reason = models.CharField("申请理由", max_length=500, null=True, blank=True)
    business_system = models.CharField("业务系统", max_length=100, null=True, blank=True)
    refuse_reason = models.CharField("拒绝理由", max_length=500, null=True, blank=True)
    saved_ips = JSONField("申请的IP留存", null=True, blank=True)

    # 申请的IP保存为以下类型
    # {
    #     "id": int
    #     "ip_pool": int,
    #     "sub_net_work": int,
    #     "ip_list": ['192.168.0.1']
    # }
    @classmethod
    def create_apply(cls, params, username):
        return cls.objects.create(
            expired_time=params.get("expired_time", ""),
            apply_way=params.get("apply_way", "MANUAL"),
            apply_type=params.get("apply_type", "new"),
            apply_status=params.get("apply_status", "auditing"),
            apply_ip_pool_id=params["apply_ip_pool"],
            apply_ip_net_id=params["apply_ip_net"],
            apply_ips=params.get("apply_ips", []),
            apply_ip_count=params.get("apply_ip_count", None),
            apply_person=params.get("apply_person", username),
            apply_reason=params.get("apply_reason", ""),
            business_system=params.get("business_system", ""),
        )


class CmdbSync(Model):
    """
    cmdb的同步模型
    """

    model_id = models.CharField("模型ID", max_length=100)
    create_by = models.CharField("创建者", max_length=100, default="")
    priority = models.IntegerField("优先级")
    bk_cloud_id = models.CharField("云区域ID", max_length=100, null=True, blank=True)
    ip = models.CharField("ip", max_length=100)
    sync = models.BooleanField(default=False)
    attribute_map = JSONField("字段映射", null=True, blank=True)

    class Meta:
        ordering = ["-id"]

    # 字段映射的样例
    # [
    #     {
    #         "ipam_attr": "",
    #         "cmdb_attr": "",
    #         "is_cmdb_enum": true / false,
    #         "check_conflict": true / false
    #     }
    # ]


class CmdbSyncRecord(models.Model):
    """
    cmdb的同步记录
    """

    SYNC_FAIL = "0"
    SYNC_SUCCESS = "1"
    SYNCING = "2"
    SYNC_STATUS = (("0", "同步失败"), ("1", "同步成功"), ("2", "同步中"))
    sync_at = models.DateTimeField("同步时间", auto_now_add=True, null=True)
    complete_at = models.DateTimeField("同步结束时间", null=True, blank=True)
    old_info = JSONField("同步前信息", null=True, blank=True)
    new_info = JSONField("同步后信息", null=True, blank=True)
    sync_status = models.CharField("同步状态", max_length=100, choices=SYNC_STATUS, null=True, blank=True)
    cmdb_sync = models.ForeignKey(CmdbSync, on_delete=models.CASCADE)
    ip = models.ForeignKey(Ips, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-id"]


class CustomAttr(models.Model):
    """自定义属性"""

    IP_POOL = "ip_pool"
    TET_WORK_SEGMENT = "tetwork_segment"
    IPS = "ips"
    CUSTOM_TYPE = (
        (IP_POOL, "IP地址池自定义属性"),
        (TET_WORK_SEGMENT, "子网自定义属性"),
        (IPS, "ip自定义属性"),
    )
    type = models.CharField("适用类型", max_length=100, choices=CUSTOM_TYPE)
    name = models.CharField("名称", max_length=200, unique=True)
    display_name = models.CharField("显示名称", max_length=100)
    create_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    create_by = models.CharField("创建人", max_length=100, null=True, blank=True)
    required = models.BooleanField("是否必填")
    description = models.CharField("描述", max_length=500, null=True, blank=True)

    class Meta:
        ordering = ["-id"]


class OperationLog(models.Model):
    """
    操作日志
    """

    ADD = "add"
    MODIFY = "modify"
    EXEC = "exec"
    DELETE = "delete"
    OPERATE_TYPE = (
        (ADD, "新增"),
        (MODIFY, "修改"),
        (EXEC, "执行"),
        (DELETE, "删除"),
    )
    operate_date = models.DateTimeField("操作时间", auto_now_add=True)
    operate_type = models.CharField("操作类型", max_length=100, choices=OPERATE_TYPE)
    operate_obj = models.CharField("操作对象", max_length=100, null=True, blank=True)
    operator = models.CharField("操作者", max_length=100)
    operate_detail = models.TextField("操作详情")
    result = models.BooleanField("操作结果")

    class Meta:
        ordering = ["-id"]


class SystemGroup(models.Model):
    class Meta:
        verbose_name = "系统用户分组"

    name = models.CharField("分组名称", max_length=64, unique=True)
    desc = models.CharField("分组描述", max_length=128, default="", blank=True)
    can_modify = models.BooleanField("是否可以修改", default=True)
    created_time = models.DateTimeField("添加时间", auto_now_add=True)
    modified_time = models.DateTimeField("修改时间", auto_now=True)

    def get_ins_summary(self):
        return "{}[分组名称: {}]".format(self._meta.verbose_name, self.name)

    def add_group_member(self, user_id_list):
        """添加分组成员"""
        system_user_group_relation_create_list = [
            SystemUserGroupRelation(system_user_id=user_id, system_group_id=self.id) for user_id in user_id_list
        ]
        SystemUserGroupRelation.objects.bulk_create(system_user_group_relation_create_list, batch_size=100)

    def modify_group_member(self, user_id_list):
        """修改分组成员"""
        self.systemuser_set.clear()
        self.add_group_member(user_id_list)


class SystemUser(models.Model):
    class Meta:
        verbose_name = "系统用户"

    bk_username = models.CharField("用户名称", max_length=64, unique=True)
    qq = models.CharField("qq账号", max_length=20, default="")
    bk_role = models.SmallIntegerField("用户角色")
    phone = models.CharField("电话号码", max_length=20)
    wx_userid = models.CharField("微信ID", max_length=64, default="")
    email = models.CharField("邮箱地址", max_length=64)
    chname = models.CharField("中文名称", max_length=64)
    created_time = models.DateTimeField("添加时间", auto_now_add=True)
    modified_time = models.DateTimeField("修改时间", auto_now=True)
    system_groups = models.ManyToManyField(SystemGroup, verbose_name="人员分组", through="SystemUserGroupRelation")

    def get_ins_summary(self):
        return "{}[用户名称: {}, 中文名称: {}]".format(self._meta.verbose_name, self.bk_username, self.chname)


class SystemUserGroupRelation(models.Model):
    """组与用户关联"""

    system_user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    system_group = models.ForeignKey(SystemGroup, on_delete=models.CASCADE)


class Settings(models.Model):
    """
    配置项
    一般的用key-value对就行
    特殊的用extra记录
    """

    key = models.CharField(verbose_name="设置项", max_length=128, unique=True)
    value = models.TextField(verbose_name="设置值", null=True, blank=True)
    desc = models.CharField(verbose_name="设置描述", max_length=255, null=True, blank=True)
    extra = JSONField(verbose_name="扩展", null=True, blank=True)

    class Meta:
        ordering = ["-id"]
