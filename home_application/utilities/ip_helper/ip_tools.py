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
import IPy
import ipaddr
from IPy import IP, IPint

from blueapps.utils.logger import logger


def format_ip_range_to_ip(dst):
    ipx = dst.split("-")

    def ip_to_num(x):
        return sum(256 ** i * int(j) for i, j in enumerate(x.split(".")[::-1]))

    def num_to_ip(x):
        return ".".join([str(x // (256 ** i) % 256) for i in range(3, -1, -1)])

    ip = [
        num_to_ip(i)
        for i in range(ip_to_num(ipx[0]), ip_to_num(ipx[1]) + 1)
        if not ((i + 1) % 256 == 0 or i % 256 == 0)
    ]
    return ip


def is_ipv4(ip: str):
    """
    检查ip是否合法
    :param: ip ip地址
    :return: True 合法 False 不合法
    """
    ip_array = ip.split(".")
    if len(ip_array) != 4:
        return False
    try:
        for x in ip_array:
            if not 0 <= int(x) <= 255:
                return False
    except ValueError:
        return False
    return True


def dns_error(dns):
    try:
        IP(dns)
    except (ValueError, TypeError) as e:
        logger.exception(e)
        return True
    return False


def gateway_error(ipnet, gateway):
    try:
        gateway = IPint(gateway).int()
        ips = IPint(ipnet)
        return gateway not in range(ips.__getitem__(0), ips.__getitem__(-1)) or gateway == ips.__getitem__(0)
    except ValueError:
        return False


def check_net_cover(exist_ip_net, ip_net_check):
    try:
        new_ip_net = IP(ip_net_check)
        for ip_net in exist_ip_net:
            if_cover = new_ip_net.overlaps(IP(ip_net))
            if if_cover:
                return False
        return True
    except ValueError:
        return False


def check_ip_net(net):
    try:
        ip_net = IP(net).strNormal()
        return ip_net
    except ValueError:
        return ipv4_check(net)


def ipv4_check(net):
    try:
        net_mask = ipaddr.IPv4Network(net).netmask
        net_work = ipaddr.IPv4Network(net).network
        ip_net = IP(str(net_work)).make_net(str(net_mask))
        return ip_net
    except ValueError:
        raise ValueError("输入的子网段:{} 格式不正确，请输入类似 192.168.1.0/24 结构的值".format(net))


def get_ip_range(dst):
    if "-" in str(dst):
        return format_ip_range_to_ip(dst)
    ip = IPy.IP(dst)
    return ip
