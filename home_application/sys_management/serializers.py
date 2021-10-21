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
from django_filters import rest_framework as filters
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from home_application.models import CmdbSync, CmdbSyncRecord, OperationLog, Settings


class CmdbSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmdbSync
        fields = "__all__"

    def create(self, validated_data):
        validated_data["create_by"] = self.context["request"].user.username
        if CmdbSync.objects.filter(model_id=validated_data.get("model_id")).exists():
            raise ValidationError(f"模型[{validated_data.get('model_id')}]已存在！")
        return super(CmdbSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data["update_by"] = self.context["request"].user.username
        if CmdbSync.objects.filter(model_id=validated_data.get("model_id")).exclude(id=self.instance.id).exists():
            raise ValidationError(f"模型[{validated_data.get('model_id')}]已存在！")
        for i in validated_data["attribute_map"]:
            if i["ipam_attr"] in ["ip", "bk_cloud_id"]:
                validated_data[i["ipam_attr"]] = i["cmdb_attr"]
        return super(CmdbSerializer, self).update(instance, validated_data)


class SyncRecordSerializer(serializers.ModelSerializer):
    create_by = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    ip_address = serializers.SerializerMethodField()

    class Meta:
        model = CmdbSyncRecord
        fields = "__all__"

    @staticmethod
    def get_create_by(instance: CmdbSyncRecord):
        return instance.cmdb_sync.create_by

    @staticmethod
    def get_model_name(instance: CmdbSyncRecord):
        return instance.cmdb_sync.name

    @staticmethod
    def get_ip_address(instance: CmdbSyncRecord):
        return instance.ip.ip


class SyncRecordSearch(filters.FilterSet):
    start_time = filters.DateFilter(field_name="sync_at", lookup_expr="gte")
    end_time = filters.DateFilter(field_name="sync_at", lookup_expr="lte")
    model = filters.CharFilter(field_name="cmdb_sync__name")

    class Meta:
        model = CmdbSyncRecord
        fields = ["model", "sync_status", "start_time", "end_time"]


class CmdbSearch(filters.FilterSet):
    model_id = filters.CharFilter(field_name="model_id", lookup_expr="icontains")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    bk_cloud_id = filters.CharFilter(field_name="bk_cloud_id", lookup_expr="icontains")
    ip = filters.CharFilter(field_name="ip", lookup_expr="icontains")

    class Meta:
        model = CmdbSync
        fields = ["model_id", "name", "bk_cloud_id", "ip"]


class OperationLogSerializer(serializers.ModelSerializer):
    start_time = filters.DateFilter(field_name="operate_date", lookup_expr="gte")
    end_time = filters.DateFilter(field_name="operate_date", lookup_expr="lte")

    class Meta:
        model = OperationLog
        fields = "__all__"


class OperationLogSearch(filters.FilterSet):
    start_time = filters.DateFilter(field_name="operate_date", lookup_expr="gte")
    end_time = filters.DateFilter(field_name="operate_date", lookup_expr="lte")
    operator = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = OperationLog
        fields = ["operator", "operate_type", "start_time", "end_time"]


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = "__all__"
