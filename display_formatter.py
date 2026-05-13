#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List


class DisplayFormatter:
    """显示格式化类"""

    @staticmethod
    def print_network_info(info: Dict):
        """
        打印网络信息

        Args:
            info: 网络信息字典
        """
        if 'error' in info:
            print(f"{info['error']}")
            return

        print("" + "="*60)
        print("网络信息".center(60))
        print("="*60)
        print(f"IP地址:        {info['ip_address']}")
        print(f"子网掩码:      {info['subnet_mask']}")
        print(f"CIDR前缀:      /{info['cidr']}")
        print(f"网络地址:      {info['network_address']}")
        print(f"广播地址:      {info['broadcast_address']}")
        print(f"首个主机地址:  {info['first_host']}")
        print(f"最后主机地址:  {info['last_host']}")
        print(f"总主机数:      {info['total_hosts']}")
        print(f"可用主机数:    {info['usable_hosts']}")
        print(f"IP地址类别:    {info['ip_class']}")
        print(f"IP地址类型:    {info['ip_type']}")
        print(f"私有IP:        {'是' if info['is_private'] else '否'}")
        print(f"回环地址:      {'是' if info['is_loopback'] else '否'}")
        print(f"组播地址:      {'是' if info['is_multicast'] else '否'}")
        print(f"保留地址:      {'是' if info['is_reserved'] else '否'}")
        print("="*60)

    @staticmethod
    def print_subnet_details(details: Dict):
        """
        打印子网详细信息

        Args:
            details: 子网详细信息字典
        """
        print("" + "="*60)
        print("子网详细信息".center(60))
        print("="*60)
        print(f"网络地址:      {details['network_address']}")
        print(f"广播地址:      {details['broadcast_address']}")
        print(f"主机范围:      {details['host_range']}")
        print(f"总主机数:      {details['total_hosts']}")
        print(f"可用主机数:    {details['usable_hosts']}")
        print(f"子网掩码:      {details['subnet_mask']}")
        print(f"CIDR前缀:      /{details['cidr']}")
        print(f"通配符掩码:    {details['wildcard_mask']}")
        print(f"二进制掩码:    {details['binary_mask']}")
        print(f"二进制网络:    {details['binary_network']}")
        print(f"二进制广播:    {details['binary_broadcast']}")
        print("="*60)

    @staticmethod
    def print_subnets_list(subnets: List[Dict]):
        """
        打印子网列表

        Args:
            subnets: 子网信息列表
        """
        print("" + "="*80)
        print("子网划分结果".center(80))
        print("="*80)
        print(f"{'序号':<6}{'网络地址':<18}{'广播地址':<18}{'子网掩码':<18}{'可用主机数':<10}")
        print("-"*80)

        for subnet in subnets:
            print(f"{subnet['subnet_number']:<6}"
                  f"{subnet['network_address']:<18}"
                  f"{subnet['broadcast_address']:<18}"
                  f"{subnet['subnet_mask']:<18}"
                  f"{subnet['usable_hosts']:<10}")

        print("="*80)

    @staticmethod
    def print_vlsm_results(subnets: List[Dict]):
        """
        打印VLSM划分结果

        Args:
            subnets: VLSM子网信息列表
        """
        print("" + "="*100)
        print("VLSM子网划分结果".center(100))
        print("="*100)
        print(f"{'子网名称':<15}{'网络地址':<18}{'广播地址':<18}{'子网掩码':<18}"
              f"{'需求主机':<10}{'可用主机':<10}{'利用率':<10}")
        print("-"*100)

        for subnet in subnets:
            utilization = (subnet['allocated_hosts'] / subnet['usable_hosts'] * 100) if subnet['usable_hosts'] > 0 else 0
            print(f"{subnet['name']:<15}"
                  f"{subnet['network_address']:<18}"
                  f"{subnet['broadcast_address']:<18}"
                  f"{subnet['subnet_mask']:<18}"
                  f"{subnet['allocated_hosts']:<10}"
                  f"{subnet['usable_hosts']:<10}"
                  f"{utilization:.1f}%")

        print("="*100)

    @staticmethod
    def print_supernet_info(info: Dict):
        """
        打印超网信息

        Args:
            info: 超网信息字典
        """
        print("" + "="*60)
        print("超网信息".center(60))
        print("="*60)
        print(f"超网地址:      {info['supernet_address']}")
        print(f"超网掩码:      {info['supernet_mask']}")
        print(f"CIDR前缀:      /{info['supernet_cidr']}")
        print(f"广播地址:      {info['broadcast_address']}")
        print(f"总主机数:      {info['total_hosts']}")
        print(f"可用主机数:    {info['usable_hosts']}")
        print(f"包含的网络:")
        for network in info['included_networks']:
            print(f"  - {network}")
        print("="*60)

    @staticmethod
    def print_ip_position(position: Dict):
        """
        打印IP地址在子网中的位置信息

        Args:
            position: IP位置信息字典
        """
        print("" + "="*60)
        print("IP地址位置信息".center(60))
        print("="*60)
        print(f"IP地址:        {position['ip']}")
        print(f"位置:          {position['position']}")
        print(f"是否可用:      {'是' if position['is_usable'] else '否'}")
        print(f"网络地址:      {position['network_address']}")
        print(f"广播地址:      {position['broadcast_address']}")
        print("="*60)

    @staticmethod
    def print_optimal_subnet(info: Dict):
        """
        打印最优子网建议

        Args:
            info: 最优子网信息字典
        """
        print("" + "="*60)
        print("最优子网建议".center(60))
        print("="*60)
        print(f"需求主机数:    {info['required_hosts']}")
        print(f"推荐CIDR:      /{info['recommended_cidr']}")
        print(f"推荐子网掩码:  {info['recommended_mask']}")
        print(f"总主机数:      {info['total_hosts']}")
        print(f"可用主机数:    {info['usable_hosts']}")
        print(f"浪费主机数:    {info['waste']}")
        print("="*60)

    @staticmethod
    def print_menu():
        """打印主菜单"""
        print("" + "="*60)
        print("IP地址合法性检测及子网判断程序".center(60))
        print("="*60)
        print("请选择功能:")
        print("1. 验证IP地址并显示网络信息")
        print("2. 判断两个IP地址是否在同一子网")
        print("3. 子网划分")
        print("4. VLSM子网划分")
        print("5. 查找最优子网")
        print("6. 计算超网")
        print("0. 退出程序")
        print("="*60)

    @staticmethod
    def print_error(message: str):
        """
        打印错误信息

        Args:
            message: 错误信息
        """
        print(f"{message}")

    @staticmethod
    def print_success(message: str):
        """
        打印成功信息

        Args:
            message: 成功信息
        """
        print(f"{message}")
