#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IP地址工具模块
提供IP地址转换、计算等工具函数
"""

from typing import List, Tuple


def ip_to_int(ip: str) -> int:
    """
    将点分十进制IP地址转换为整数

    Args:
        ip: 点分十进制IP地址

    Returns:
        int: 整数形式的IP地址
    """
    octets = [int(x) for x in ip.split('.')]
    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]


def int_to_ip(ip_int: int) -> str:
    """
    将整数IP地址转换为点分十进制

    Args:
        ip_int: 整数形式的IP地址

    Returns:
        str: 点分十进制IP地址
    """
    return '.'.join([
        str((ip_int >> 24) & 0xff),
        str((ip_int >> 16) & 0xff),
        str((ip_int >> 8) & 0xff),
        str(ip_int & 0xff)
    ])


def cidr_to_mask(cidr: int) -> str:
    """
    将CIDR前缀长度转换为子网掩码

    Args:
        cidr: CIDR前缀长度(0-32)

    Returns:
        str: 点分十进制子网掩码
    """
    mask = 0xffffffff << (32 - cidr) & 0xffffffff
    return int_to_ip(mask)


def mask_to_cidr(mask: str) -> int:
    """
    将子网掩码转换为CIDR前缀长度

    Args:
        mask: 点分十进制子网掩码

    Returns:
        int: CIDR前缀长度
    """
    mask_int = ip_to_int(mask)
    return bin(mask_int).count('1')


def is_valid_mask(mask: str) -> bool:
    """
    检查子网掩码是否有效

    Args:
        mask: 点分十进制子网掩码

    Returns:
        bool: 是否有效
    """
    try:
        mask_int = ip_to_int(mask)
        binary_str = bin(mask_int)[2:].zfill(32)
        # 有效的子网掩码应该是连续的1后面跟着连续的0
        return '01' not in binary_str
    except:
        return False


def calculate_network_address(ip: str, mask: str) -> str:
    """
    计算网络地址

    Args:
        ip: IP地址
        mask: 子网掩码

    Returns:
        str: 网络地址
    """
    ip_int = ip_to_int(ip)
    mask_int = ip_to_int(mask)
    network_int = ip_int & mask_int
    return int_to_ip(network_int)


def calculate_broadcast_address(network: str, mask: str) -> str:
    """
    计算广播地址

    Args:
        network: 网络地址
        mask: 子网掩码

    Returns:
        str: 广播地址
    """
    network_int = ip_to_int(network)
    mask_int = ip_to_int(mask)
    broadcast_int = network_int | (~mask_int & 0xffffffff)
    return int_to_ip(broadcast_int)


def calculate_host_range(network: str, mask: str) -> Tuple[str, str]:
    """
    计算可用主机地址范围

    Args:
        network: 网络地址
        mask: 子网掩码

    Returns:
        Tuple[str, str]: (首个主机地址, 最后主机地址)
    """
    network_int = ip_to_int(network)
    mask_int = ip_to_int(mask)
    broadcast_int = calculate_broadcast_address(network, mask)
    broadcast_int = ip_to_int(broadcast_int)

    cidr = mask_to_cidr(mask)

    if cidr == 32:
        return network, network
    elif cidr == 31:
        return network, int_to_ip(broadcast_int)
    else:
        first_host = network_int + 1
        last_host = broadcast_int - 1
        return int_to_ip(first_host), int_to_ip(last_host)


def calculate_subnet_capacity(cidr: int) -> Tuple[int, int]:
    """
    计算子网容量

    Args:
        cidr: CIDR前缀长度

    Returns:
        Tuple[int, int]: (总主机数, 可用主机数)
    """
    host_bits = 32 - cidr
    if host_bits == 0:
        return 1, 1
    elif host_bits == 1:
        return 2, 0
    else:
        total = 2 ** host_bits
        return total, total - 2


def get_ip_class(ip: str) -> str:
    """
    获取IP地址类别

    Args:
        ip: IP地址

    Returns:
        str: IP地址类别(A/B/C/D/E)
    """
    first_octet = int(ip.split('.')[0])
    if first_octet < 128:
        return 'A'
    elif first_octet < 192:
        return 'B'
    elif first_octet < 224:
        return 'C'
    elif first_octet < 240:
        return 'D (组播)'
    else:
        return 'E (保留)'


def is_private_ip(ip: str) -> bool:
    """
    判断是否是私有IP地址

    Args:
        ip: IP地址

    Returns:
        bool: 是否是私有IP
    """
    octets = [int(x) for x in ip.split('.')]
    # 10.0.0.0/8
    if octets[0] == 10:
        return True
    # 172.16.0.0/12
    if octets[0] == 172 and 16 <= octets[1] <= 31:
        return True
    # 192.168.0.0/16
    if octets[0] == 192 and octets[1] == 168:
        return True
    return False


def is_loopback_ip(ip: str) -> bool:
    """
    判断是否是回环地址

    Args:
        ip: IP地址

    Returns:
        bool: 是否是回环地址
    """
    return ip.startswith('127.')


def is_multicast_ip(ip: str) -> bool:
    """
    判断是否是组播地址

    Args:
        ip: IP地址

    Returns:
        bool: 是否是组播地址
    """
    first_octet = int(ip.split('.')[0])
    return 224 <= first_octet < 240


def is_reserved_ip(ip: str) -> bool:
    """
    判断是否是保留地址

    Args:
        ip: IP地址

    Returns:
        bool: 是否是保留地址
    """
    first_octet = int(ip.split('.')[0])
    return first_octet >= 240


def get_ip_type(ip: str) -> str:
    """
    获取IP地址类型

    Args:
        ip: IP地址

    Returns:
        str: IP地址类型
    """
    if is_loopback_ip(ip):
        return '回环地址'
    elif is_private_ip(ip):
        return '私有地址'
    elif is_multicast_ip(ip):
        return '组播地址'
    elif is_reserved_ip(ip):
        return '保留地址'
    else:
        return '公网地址'
