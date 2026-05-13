#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from ip_validator import IPValidator
from network_calculator import NetworkCalculator
from subnet_divider import SubnetDivider
from display_formatter import DisplayFormatter
from ip_utils import (
    ip_to_int,
    int_to_ip,
    cidr_to_mask,
    calculate_network_address
)


class IPValidatorApp:
    """IP地址验证应用程序类"""

    def __init__(self):
        self.validator = IPValidator()
        self.formatter = DisplayFormatter()

    def run(self):
        """运行应用程序"""
        self.formatter.print_menu()

        while True:
            try:
                choice = input("请输入选项(0-6): ").strip()

                if choice == '0':
                    print("程序已退出")
                    break
                elif choice == '1':
                    self.validate_and_show_info()
                elif choice == '2':
                    self.check_same_subnet()
                elif choice == '3':
                    self.divide_subnets()
                elif choice == '4':
                    self.vlsm_divide()
                elif choice == '5':
                    self.find_optimal_subnet()
                elif choice == '6':
                    self.calculate_supernet()
                else:
                    self.formatter.print_error("无效的选项，请重新输入")

                print("" + "-"*60 + "")

            except KeyboardInterrupt:
                print("程序已退出")
                break
            except Exception as e:
                self.formatter.print_error(f"发生错误: {str(e)}")

    def validate_and_show_info(self):
        """验证IP地址并显示网络信息"""
        print("支持两种输入格式:")
        print("1. 点分十进制+子网掩码: 192.168.1.1 255.255.255.0")
        print("2. CIDR形式: 192.168.1.1/24")

        ip_input = input("请输入IP地址: ").strip()

        is_valid, ip, mask, cidr = self.validator.validate_ip_input(ip_input)

        if is_valid:
            self.formatter.print_success("IP地址格式正确")

            # 创建网络计算器并获取信息
            calculator = NetworkCalculator(ip, mask, cidr)
            info = calculator.get_network_info()

            # 显示网络信息
            self.formatter.print_network_info(info)

            # 显示子网详细信息
            details = calculator.get_subnet_details()
            self.formatter.print_subnet_details(details)
        else:
            self.formatter.print_error(self.validator.get_error_message())

    def check_same_subnet(self):
        """检查两个IP地址是否在同一子网"""
        print("请输入第一个IP地址（带子网掩码）:")
        print("支持格式: 192.168.1.1 255.255.255.0 或 192.168.1.1/24")

        first_ip = input("第一个IP地址: ").strip()
        is_valid, ip, mask, cidr = self.validator.validate_ip_input(first_ip)

        if not is_valid:
            self.formatter.print_error(self.validator.get_error_message())
            return

        calculator = NetworkCalculator(ip, mask, cidr)

        second_ip = input("第二个IP地址: ").strip()

        # 验证第二个IP地址
        if '/' in second_ip:
            ip_part = second_ip.split('/')[0].strip()
        elif ' ' in second_ip:
            ip_part = second_ip.split()[0].strip()
        else:
            ip_part = second_ip.strip()

        is_valid2, _, _, _ = self.validator.validate_ip_input(ip_part + ' ' + mask)

        if not is_valid2:
            self.formatter.print_error(self.validator.get_error_message())
            return

        # 检查是否在同一子网
        position = calculator.get_ip_position_in_subnet(ip_part)
        self.formatter.print_ip_position(position)

        if position['is_usable']:
            self.formatter.print_success(f"{ip_part} 与 {ip} 在同一子网")
        else:
            self.formatter.print_error(f"{ip_part} 与 {ip} 不在同一子网")

    def divide_subnets(self):
        """子网划分"""
        print("请输入要划分的网络地址（CIDR格式）:")
        print("例如: 192.168.1.0/24")

        network_input = input("网络地址: ").strip()

        if '/' not in network_input:
            self.formatter.print_error("请使用CIDR格式，例如: 192.168.1.0/24")
            return

        network, cidr_str = network_input.split('/')
        cidr = int(cidr_str)

        new_cidr = input(f"请输入新的CIDR前缀长度（当前: /{cidr}）: ").strip()

        try:
            new_cidr = int(new_cidr)
            if new_cidr <= cidr:
                self.formatter.print_error(f"新的CIDR前缀长度必须大于当前CIDR前缀长度({cidr})")
                return
        except ValueError:
            self.formatter.print_error("CIDR前缀长度必须是数字")
            return

        divider = SubnetDivider(network, cidr)
        subnets = divider.divide_subnets(new_cidr)

        self.formatter.print_subnets_list(subnets)

    def vlsm_divide(self):
        """VLSM子网划分"""
        print("请输入要划分的网络地址（CIDR格式）:")
        print("例如: 192.168.1.0/24")

        network_input = input("网络地址: ").strip()

        if '/' not in network_input:
            self.formatter.print_error("请使用CIDR格式，例如: 192.168.1.0/24")
            return

        network, cidr_str = network_input.split('/')
        cidr = int(cidr_str)

        print("请输入子网需求（格式: 子网名称 主机数量）")
        print("例如: 办公区 50")
        print("输入 'done' 完成输入")

        requirements = []
        while True:
            req_input = input("子网需求: ").strip()
            if req_input.lower() == 'done':
                break

            parts = req_input.split()
            if len(parts) != 2:
                self.formatter.print_error("格式错误，请使用: 子网名称 主机数量")
                continue

            try:
                hosts = int(parts[1])
                if hosts <= 0:
                    self.formatter.print_error("主机数量必须大于0")
                    continue
                requirements.append({'name': parts[0], 'hosts': hosts})
            except ValueError:
                self.formatter.print_error("主机数量必须是数字")

        if not requirements:
            self.formatter.print_error("没有输入任何子网需求")
            return

        divider = SubnetDivider(network, cidr)
        subnets = divider.vlsm_divide(requirements)

        self.formatter.print_vlsm_results(subnets)

    def find_optimal_subnet(self):
        """查找最优子网"""
        hosts_input = input("请输入需要的主机数量: ").strip()

        try:
            required_hosts = int(hosts_input)
            if required_hosts <= 0:
                self.formatter.print_error("主机数量必须大于0")
                return
        except ValueError:
            self.formatter.print_error("主机数量必须是数字")
            return

        # 使用一个默认网络来计算
        divider = SubnetDivider("10.0.0.0", 8)
        optimal = divider.find_optimal_subnet(required_hosts)

        self.formatter.print_optimal_subnet(optimal)

    def calculate_supernet(self):
        """计算超网"""
        print("请输入要计算超网的网络地址列表（CIDR格式）")
        print("例如: 192.168.1.0/24")
        print("输入 'done' 完成输入")

        networks = []
        while True:
            network_input = input("网络地址: ").strip()
            if network_input.lower() == 'done':
                break

            if '/' not in network_input:
                self.formatter.print_error("请使用CIDR格式，例如: 192.168.1.0/24")
                continue

            network, cidr_str = network_input.split('/')
            networks.append(network)

        if len(networks) < 2:
            self.formatter.print_error("至少需要输入2个网络地址")
            return

        # 使用第一个网络作为基准
        divider = SubnetDivider(networks[0], 24)
        supernet_info = divider.get_supernet_info(networks)

        self.formatter.print_supernet_info(supernet_info)


def main():
    """主函数"""
    app = IPValidatorApp()
    app.run()


if __name__ == "__main__":
    main()
