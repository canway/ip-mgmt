# -*- coding: utf-8 -*-
"""
校验 requirements 是否符合要求
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import re
import sys
import traceback
from io import open

# 禁止安装的 SDK
FORBIDDEN_SDK = ["request"]
# 最低版本要求，版本号的每一段都必须是数字
MIN_VERSION = {"Django": "1.8.1"}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPERATOR_REG = re.compile(r"[=><]+")

coding = "utf-8"
try:
    # py2
    reload(sys)
    sys.setdefaultencoding("utf-8")
except NameError:
    # py3
    coding = "utf-8"


def not_less_version(version, min_version):
    """
    :summary: 判断 version >= min_version
    :param version:
    :param min_version:
    :return:
    """
    version_list = version.split(".")
    min_version_list = min_version.split(".")
    for index in range(min(len(version_list), len(min_version_list))):
        if int(version_list[index]) < int(min_version_list[index]):
            return False
        if int(version_list[index]) > int(min_version_list[index]):
            return True
    return True


def sdk_match_version(sdk_info):
    """
    :param sdk_info: ("Django", "==", "1.8.11") or ("Django", None, None)
    :return:
    """
    sdk_name, operator, sdk_version = sdk_info[0], sdk_info[1], sdk_info[2]
    if sdk_name not in MIN_VERSION:
        return True, None

    sdk_min_version = MIN_VERSION[sdk_name]
    error_message = "SDK: {sdk_name} does not match min version: {version}".format(
        sdk_name=sdk_name, version=sdk_min_version
    )
    if "<" in operator:
        return False, error_message
    if not not_less_version(sdk_version, sdk_min_version):
        return False, error_message

    return True, None


def read_requirements():
    req_path = os.path.join(BASE_DIR, "requirements.txt")
    if not os.path.exists(req_path):
        return []

    requirements = []
    with open(req_path, "r", encoding=coding) as req_file:
        for line in req_file:
            line = line.strip()
            # 空行 或 注释
            if not line or line.startswith("#"):
                continue
            if re.findall(OPERATOR_REG, line):
                operator = re.findall(OPERATOR_REG, line)[0]
                sdk_info = line.split(operator)
                requirements.append((sdk_info[0], operator, sdk_info[1]))
            else:
                requirements.append((line, None, None))
    return requirements


def main():
    try:
        requirements = read_requirements()
        for sdk_info in requirements:
            if sdk_info[0] in FORBIDDEN_SDK:
                print("SDK: is not safe, which should not be installed" % sdk_info[0])
                return 1
            match_result = sdk_match_version(sdk_info)
            if not match_result[0]:
                print(match_result[1])
                return 1

        return 0
    except Exception as e:
        traceback.print_exc()
        print("Unexpected exception occurred: %s" % e)
        return 1


if __name__ == "__main__":
    exit(main())
