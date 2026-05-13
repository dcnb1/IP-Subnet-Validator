#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络计算模块
负责计算网络相关信息，如网络地址、广播地址、主机范围等
"""

from typing import Dict, List
from ip_utils import (
    calculate_network_address,
    calculate_broadcast_address,
    calculate_host_range,
    calculate_subnet_capacity,
    get_ip_class,
    is_private_ip,
    is_loopback_ip,
    is_multicast_ip,
    is_reserved_ip,
    get_ip_type
)


class NetworkCalculator:
    """网络计算类"""

    def __init__(self, ip: str, mask: str, cidr: str):
        """
        初始化网络计算器

        Args:
            ip: IP地址
            mask: 子网掩码
            cidr: CIDR前缀长度
        """
        self.ip = ip
        self.mask = mask
        self.cidr = cidr

    def get_network_info(self) -> Dict:
        """
        获取完整的网络信息

        Returns:
            Dict: 包含所有网络信息的字典
        """
        # 计算网络地址
        network_address = calculate_network_address(self.ip, self.mask)

        # 计算广播地址
        broadcast_address = calculate_broadcast_address(network_address, self.mask)

        # 计算主机地址范围
        first_host, last_host = calculate_host_range(network_address, self.mask)

        # 计算子网容量
        total_hosts, usable_hosts = calculate_subnet_capacity(int(self.cidr))

        # 获取IP地址类别
        ip_class = get_ip_class(self.ip)

        # 获取IP地址类型
        ip_type = get_ip_type(self.ip)

        return {
            'ip_address': self.ip,
            'subnet_mask': self.mask,
            'cidr': self.cidr,
            'network_address': network_address,
            'broadcast_address': broadcast_address,
            'first_host': first_host,
            'last_host': last_host,
            'total_hosts': total_hosts,
            'usable_hosts': usable_hosts,
            'ip_class': ip_class,
            'ip_type': ip_type,
            'is_private': is_private_ip(self.ip),
            'is_loopback': is_loopback_ip(self.ip),
            'is_multicast': is_multicast_ip(self.ip),
            'is_reserved': is_reserved_ip(self.ip)
        }

    def get_subnet_summary(self) -> str:
        """
        获取子网摘要信息

        Returns:
            str: 格式化的子网摘要
        """
        info = self.get_network_info()
        return f"{info['network_address']}/{self.cidr}"

    def is_ip_in_subnet(self, ip: str) -> bool:
        """
        判断给定的IP地址是否在当前子网中

        Args:
            ip: 要检查的IP地址

        Returns:
            bool: 是否在子网中
        """
        network_address = calculate_network_address(self.ip, self.mask)
        target_network = calculate_network_address(ip, self.mask)
        return network_address == target_network

    def get_subnet_details(self) -> Dict:
        """
        获取子网详细信息

        Returns:
            Dict: 包含子网详细信息的字典
        """
        info = self.get_network_info()
        return {
            'network_address': info['network_address'],
            'broadcast_address': info['broadcast_address'],
            'host_range': f"{info['first_host']} - {info['last_host']}",
            'total_hosts': info['total_hosts'],
            'usable_hosts': info['usable_hosts'],
            'subnet_mask': info['subnet_mask'],
            'cidr': info['cidr'],
            'wildcard_mask': self._calculate_wildcard_mask(),
            'binary_mask': self._mask_to_binary(),
            'binary_network': self._ip_to_binary(info['network_address']),
            'binary_broadcast': self._ip_to_binary(info['broadcast_address'])
        }

    def _calculate_wildcard_mask(self) -> str:
        """计算通配符掩码"""
        octets = [255 - int(x) for x in self.mask.split('.')]
        return '.'.join(map(str, octets))

    def _mask_to_binary(self) -> str:
        """将子网掩码转换为二进制表示"""
        octets = self.mask.split('.')
        return '.'.join([format(int(octet), '08b') for octet in octets])

    def _ip_to_binary(self, ip: str) -> str:
        """将IP地址转换为二进制表示"""
        octets = ip.split('.')
        return '.'.join([format(int(octet), '08b') for octet in octets])

    def get_ip_position_in_subnet(self, ip: str) -> Dict:
        """
        获取IP地址在子网中的位置信息

        Args:
            ip: 要检查的IP地址

        Returns:
            Dict: 包含位置信息的字典
        """
        info = self.get_network_info()
        network_address = info['network_address']
        broadcast_address = info['broadcast_address']

        if ip == network_address:
            position = '网络地址'
            is_usable = False
        elif ip == broadcast_address:
            position = '广播地址'
            is_usable = False
        elif self.is_ip_in_subnet(ip):
            position = '主机地址'
            is_usable = True
        else:
            position = '不在子网内'
            is_usable = False

        return {
            'ip': ip,
            'position': position,
            'is_usable': is_usable,
            'network_address': network_address,
            'broadcast_address': broadcast_address
        }
