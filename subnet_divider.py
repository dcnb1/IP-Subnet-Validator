#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
子网划分模块
负责子网划分、VLSM计算等高级功能
"""

from typing import List, Dict, Tuple
from ip_utils import (
    ip_to_int,
    int_to_ip,
    cidr_to_mask,
    mask_to_cidr,
    calculate_network_address,
    calculate_broadcast_address,
    calculate_host_range,
    calculate_subnet_capacity
)


class SubnetDivider:
    """子网划分类"""

    def __init__(self, network: str, cidr: int):
        """
        初始化子网划分器

        Args:
            network: 网络地址
            cidr: CIDR前缀长度
        """
        self.network = network
        self.cidr = cidr
        self.mask = cidr_to_mask(cidr)

    def divide_subnets(self, new_cidr: int) -> List[Dict]:
        """
        将网络划分为更小的子网

        Args:
            new_cidr: 新的CIDR前缀长度（必须大于当前CIDR）

        Returns:
            List[Dict]: 子网信息列表
        """
        if new_cidr <= self.cidr:
            raise ValueError(f"新的CIDR前缀长度({new_cidr})必须大于当前CIDR前缀长度({self.cidr})")

        if new_cidr > 32:
            raise ValueError("CIDR前缀长度不能超过32")

        # 计算子网数量
        subnet_bits = new_cidr - self.cidr
        num_subnets = 2 ** subnet_bits

        # 计算每个子网的大小
        subnet_size = 2 ** (32 - new_cidr)

        # 起始网络地址的整数值
        network_int = ip_to_int(self.network)

        subnets = []
        for i in range(num_subnets):
            # 计算子网网络地址
            subnet_network_int = network_int + (i * subnet_size)
            subnet_network = int_to_ip(subnet_network_int)

            # 计算子网掩码
            subnet_mask = cidr_to_mask(new_cidr)

            # 计算广播地址
            subnet_broadcast = calculate_broadcast_address(subnet_network, subnet_mask)

            # 计算主机范围
            first_host, last_host = calculate_host_range(subnet_network, subnet_mask)

            # 计算子网容量
            total_hosts, usable_hosts = calculate_subnet_capacity(new_cidr)

            subnets.append({
                'subnet_number': i + 1,
                'network_address': subnet_network,
                'broadcast_address': subnet_broadcast,
                'subnet_mask': subnet_mask,
                'cidr': new_cidr,
                'first_host': first_host,
                'last_host': last_host,
                'total_hosts': total_hosts,
                'usable_hosts': usable_hosts
            })

        return subnets

    def vlsm_divide(self, requirements: List[Dict]) -> List[Dict]:
        """
        使用VLSM（可变长子网掩码）进行子网划分

        Args:
            requirements: 子网需求列表，每个元素包含：
                         - name: 子网名称
                         - hosts: 需要的主机数量

        Returns:
            List[Dict]: 分配的子网信息列表
        """
        # 按主机数量从大到小排序
        sorted_reqs = sorted(requirements, key=lambda x: x['hosts'], reverse=True)

        allocated_subnets = []
        current_network_int = ip_to_int(self.network)
        remaining_bits = 32 - self.cidr

        for req in sorted_reqs:
            # 计算所需的主机位数
            host_bits = 0
            while (2 ** host_bits - 2) < req['hosts']:
                host_bits += 1

            # 计算新的CIDR
            new_cidr = 32 - host_bits

            # 检查是否有足够的地址空间
            if new_cidr < self.cidr:
                raise ValueError(f"子网 '{req['name']}' 需要的主机数({req['hosts']})超过了网络容量")

            if new_cidr < self.cidr:
                new_cidr = self.cidr

            # 计算子网大小
            subnet_size = 2 ** (32 - new_cidr)

            # 计算子网网络地址
            subnet_network_int = current_network_int
            subnet_network = int_to_ip(subnet_network_int)

            # 计算子网掩码
            subnet_mask = cidr_to_mask(new_cidr)

            # 计算广播地址
            subnet_broadcast = calculate_broadcast_address(subnet_network, subnet_mask)

            # 计算主机范围
            first_host, last_host = calculate_host_range(subnet_network, subnet_mask)

            # 计算子网容量
            total_hosts, usable_hosts = calculate_subnet_capacity(new_cidr)

            allocated_subnets.append({
                'name': req['name'],
                'required_hosts': req['hosts'],
                'network_address': subnet_network,
                'broadcast_address': subnet_broadcast,
                'subnet_mask': subnet_mask,
                'cidr': new_cidr,
                'first_host': first_host,
                'last_host': last_host,
                'total_hosts': total_hosts,
                'usable_hosts': usable_hosts,
                'allocated_hosts': req['hosts']
            })

            # 更新当前网络地址到下一个子网的起始位置
            current_network_int += subnet_size

        return allocated_subnets

    def get_supernet_info(self, networks: List[str]) -> Dict:
        """
        计算多个网络的超网信息

        Args:
            networks: 网络地址列表

        Returns:
            Dict: 超网信息
        """
        if not networks:
            raise ValueError("网络列表不能为空")

        # 将所有网络地址转换为整数
        network_ints = [ip_to_int(net) for net in networks]

        # 找出所有网络地址的共同前缀
        common_prefix = 0
        for bit in range(32, 0, -1):
            mask = 0xffffffff << (32 - bit) & 0xffffffff
            first_network = network_ints[0] & mask
            if all((net & mask) == first_network for net in network_ints):
                common_prefix = bit
                break

        # 计算超网地址
        supernet_mask = cidr_to_mask(common_prefix)
        supernet_network = calculate_network_address(networks[0], supernet_mask)

        # 计算超网广播地址
        supernet_broadcast = calculate_broadcast_address(supernet_network, supernet_mask)

        # 计算超网容量
        total_hosts, usable_hosts = calculate_subnet_capacity(common_prefix)

        return {
            'supernet_address': supernet_network,
            'supernet_mask': supernet_mask,
            'supernet_cidr': common_prefix,
            'broadcast_address': supernet_broadcast,
            'total_hosts': total_hosts,
            'usable_hosts': usable_hosts,
            'included_networks': networks
        }

    def find_optimal_subnet(self, required_hosts: int) -> Dict:
        """
        找到满足主机需求的最优子网

        Args:
            required_hosts: 需要的主机数量

        Returns:
            Dict: 最优子网信息
        """
        # 计算所需的主机位数
        host_bits = 0
        while (2 ** host_bits - 2) < required_hosts:
            host_bits += 1

        # 计算新的CIDR
        new_cidr = 32 - host_bits

        # 计算子网掩码
        subnet_mask = cidr_to_mask(new_cidr)

        # 计算子网容量
        total_hosts, usable_hosts = calculate_subnet_capacity(new_cidr)

        return {
            'required_hosts': required_hosts,
            'recommended_cidr': new_cidr,
            'recommended_mask': subnet_mask,
            'total_hosts': total_hosts,
            'usable_hosts': usable_hosts,
            'waste': usable_hosts - required_hosts
        }
