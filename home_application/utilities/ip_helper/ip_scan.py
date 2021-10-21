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
import queue
import socket
import sys
import threading

import psutil

from blueapps.utils.logger import logger


def get_nic():
    nic_name = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == "127.0.0.1":
                nic_name.append(k)
    return nic_name


def ping_win(dest_addr, ping_timeout, count):
    try:
        ping_cmd = "ping {} -n {} -w {} >nul 2>nul".format(dest_addr, count, ping_timeout * 1000)
        res = os.system(ping_cmd)
        if res == 0:
            return dest_addr
    except Exception as e:
        logger.exception(e)
        return None


def ping_lin(dest_addr, ping_timeout, count):
    try:
        ping_shell = "ping {} -c {} -w {}".format(dest_addr, count, ping_timeout)
        res = os.system(ping_shell)
        if res == 0:
            return dest_addr
    except Exception as e:
        logger.exception(e)
        return None


def test_ping(dest_addr, ping_timeout, count):
    if sys.platform == "win32":
        return ping_win(dest_addr, ping_timeout, count)
    return ping_lin(dest_addr, ping_timeout, count)


def test_arping(dest_addr, arping_timeout, count, nic):
    try:
        arping_shell = "arping {} -c {} -w {} -I {}".format(dest_addr, count, arping_timeout, nic)
        res = os.system(arping_shell)
        if res == 0:
            return dest_addr
    except Exception as e:
        logger.exception(e)
        return None


def test_port(dst, port, port_timeout):
    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli_sock.settimeout(port_timeout)
    try:
        indicator = cli_sock.connect_ex((dst, port))
        if indicator:
            raise Exception("connect port error")
        return dst
    except Exception as e:
        logger.exception(e)
    finally:
        cli_sock.close()


class IPScan(object):
    """
    参数：
        ping_timeout    -- ping超时，默认3秒
        port_timeout    -- port超时，默认5秒
        ports      -- 默认扫描端口列表，数据类型为list
        count      -- ping扫描次数
    """

    nic_list = get_nic()

    def __init__(self, ping_timeout=2, port_timeout=2, count=2, ports=None):
        if ports is None:
            ports = [22, 3389]
        self.ping_timeout = ping_timeout
        self.port_timeout = port_timeout
        self.count = count
        self.ports = ports
        self.ip_set = set()

    def ping_scan(self, ping_q, port_q):
        while not ping_q.empty():
            dst_addr = ping_q.get()
            if dst_addr not in self.ip_set:
                ip = test_ping(dst_addr, self.ping_timeout, self.count)
                if ip:
                    self.ip_set.add(ip)
                else:
                    for port in self.ports:
                        port_q.put((dst_addr, port))
            ping_q.task_done()

    def arping_scan(self, arp_q):
        while not arp_q.empty():
            arg = arp_q.get()
            dst_addr = arg[0]
            nic_name = arg[1]
            if dst_addr not in self.ip_set:
                ip = test_arping(dst_addr, self.ping_timeout, self.count, nic_name)
                if ip:
                    self.ip_set.add(ip)
            arp_q.task_done()

    def port_scan(self, port_q, arp_q):
        while not port_q.empty():
            arg = port_q.get()
            dst_addr = arg[0]
            port = arg[1]
            if dst_addr not in self.ip_set:
                ip = test_port(dst_addr, port, self.port_timeout)
                if ip:
                    self.ip_set.add(ip)
                else:
                    for nic in self.nic_list:
                        arp_q.put((dst_addr, nic))
            port_q.task_done()

    def net_scan(self, ip_pool):
        ping_q = queue.Queue()
        arp_q = queue.Queue()
        port_q = queue.Queue()
        thread_list = [None] * 20
        for ip in ip_pool:
            ping_q.put(item=ip)
        for i in thread_list:
            tp = threading.Thread(
                target=self.ping_scan,
                args=(
                    ping_q,
                    port_q,
                ),
            )
            tp.start()
        ping_q.join()
        for i in thread_list:
            tpo = threading.Thread(
                target=self.port_scan,
                args=(
                    port_q,
                    arp_q,
                ),
            )
            tpo.start()
        port_q.join()
        if sys.platform != "win32":
            for i in thread_list:
                ta = threading.Thread(target=self.arping_scan, args=(arp_q,))
                ta.start()
            arp_q.join()
        return self.ip_set
