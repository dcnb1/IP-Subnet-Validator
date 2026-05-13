#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IP地址合法性检测及子网判断程序
支持点分十进制+子网掩码形式和CIDR形式
"""

import re
import sys
from typing import Tuple, Optional, List, Dict


class IPValidator:
    """IP地址验证和子网计算类"""

    def __init__(self):
        self.ip = ""
        self.mask = ""
        self.cidr = ""
        self.is_valid = False
        self.error_msg = ""

    def validate_ip_input(self, ip_input: str) -> bool:
        """
        验证IP地址输入（支持点分十进制+子网掩码和CIDR形式）

        Args:
            ip_input: 输入的IP地址字符串

        Returns:
            bool: 是否合法
        """
        self.error_msg = ""
        self.ip = ""
        self.mask = ""
        self.cidr = ""
        self.is_valid = False

        if not ip_input:
            self.error_msg = "错误：输入为空"
            return False

        # 判断是CIDR形式还是点分十进制+子网掩码形式
        if '/' in ip_input:
            return self._validate_cidr(ip_input)
        else:
            return self._validate_dotted_decimal(ip_input)

    def _validate_cidr(self, cidr_input: str) -> bool:
        """验证CIDR格式的IP地址"""
        try:
            parts = cidr_input.split('/')
            if len(parts) != 2:
                self.error_msg = "错误：CIDR格式不正确"
                return False

            ip_part = parts[0].strip()
            prefix_part = parts[1].strip()

            # 验证IP部分
            if not self._validate_ip_address(ip_part):
                return False

            # 验证前缀长度
            try:
                prefix = int(prefix_part)
                if prefix < 0 or prefix > 32:
                    self.error_msg = "错误：CIDR前缀长度必须在0-32之间"
                    return False
            except ValueError:
                self.error_msg = "错误：CIDR前缀必须是数字"
                return False

            self.ip = ip_part
            self.cidr = prefix_part
            self.mask = self._cidr_to_mask(prefix)
            self.is_valid = True
            return True

        except Exception as e:
            self.error_msg = f"错误：CIDR解析失败 - {str(e)}"
            return False

    def _validate_dotted_decimal(self, dotted_input: str) -> bool:
        """验证点分十进制+子网掩码格式的IP地址"""
        try:
            # 检查是否包含子网掩码
            if ' ' not in dotted_input:
                self.error_msg = "错误：缺少子网掩码"
                return False

            parts = dotted_input.split()
            if len(parts) != 2:
                self.error_msg = "错误：格式不正确，应为 'IP地址 子网掩码'"
                return False

            ip_part = parts[0].strip()
            mask_part = parts[1].strip()

            # 验证IP部分
            if not self._validate_ip_address(ip_part):
                return False

            # 验证子网掩码
            if not self._validate_mask(mask_part):
                return False

            self.ip = ip_part
            self.mask = mask_part
            self.cidr = str(self._mask_to_cidr(mask_part))
            self.is_valid = True
            return True

        except Exception as e:
            self.error_msg = f"错误：点分十进制解析失败 - {str(e)}"
            return False

    def _validate_ip_address(self, ip: str) -> bool:
        """验证IP地址格式"""
        # 检查输入不完整
        if not ip or ip.isspace():
            self.error_msg = "错误：IP地址为空"
            return False

        # 检查含有非法字符（只允许数字和.）
        if not re.match(r'^[\d.]+$', ip):
            self.error_msg = "错误：IP地址包含非法字符"
            return False

        # 检查有两个连续的.
        if '..' in ip:
            self.error_msg = "错误：IP地址包含连续的点"
            return False

        # 检查.的个数
        if ip.count('.') != 3:
            self.error_msg = "错误：IP地址应该包含3个点"
            return False

        # 检查每个字段
        octets = ip.split('.')
        for octet in octets:
            # 检查字段是否为空
            if not octet:
                self.error_msg = "错误：IP地址字段不完整"
                return False

            # 检查字段中的数字
            try:
                num = int(octet)
                if num < 0 or num > 255:
                    self.error_msg = f"错误：IP地址字段 {octet} 超出范围(0-255)"
                    return False
            except ValueError:
                self.error_msg = f"错误：IP地址字段 {octet} 不是有效的数字"
                return False

        return True

    def _validate_mask(self, mask: str) -> bool:
        """验证子网掩码格式"""
        # 检查基本格式
        if not self._validate_ip_address(mask):
            return False

        # 检查是否是有效的子网掩码
        octets = mask.split('.')
        binary_str = ''.join([format(int(octet), '08b') for octet in octets])

        # 有效的子网掩码应该是连续的1后面跟着连续的0
        if '01' in binary_str:
            self.error_msg = "错误：无效的子网掩码，必须是连续的1后面跟着连续的0"
            return False

        return True

    def _cidr_to_mask(self, cidr: int) -> str:
        """将CIDR前缀长度转换为子网掩码"""
        mask = 0xffffffff << (32 - cidr) & 0xffffffff
        return '.'.join([str((mask >> (8 * i)) & 0xff) for i in range(3, -1, -1)])

    def _mask_to_cidr(self, mask: str) -> int:
        """将子网掩码转换为CIDR前缀长度"""
        octets = mask.split('.')
        binary_str = ''.join([format(int(octet), '08b') for octet in octets])
        return binary_str.count('1')

    def get_network_info(self) -> Dict:
        """获取网络信息"""
        if not self.is_valid:
            return {'error': self.error_msg}

        ip_octets = [int(x) for x in self.ip.split('.')]
        mask_octets = [int(x) for x in self.mask.split('.')]

        # 计算网络地址
        network = [ip_octets[i] & mask_octets[i] for i in range(4)]
        network_address = '.'.join(map(str, network))

        # 计算广播地址
        broadcast = [network[i] | (~mask_octets[i] & 255) for i in range(4)]
        broadcast_address = '.'.join(map(str, broadcast))

        # 计算主机地址范围
        first_host = network.copy()
        last_host = broadcast.copy()

        # 如果子网掩码不是/32，则第一个可用主机地址是网络地址+1
        if int(self.cidr) < 32:
            first_host[3] += 1
            last_host[3] -= 1
            # 处理进位和借位
            for i in range(3, 0, -1):
                if first_host[i] > 255:
                    first_host[i] = 0
                    first_host[i-1] += 1
                if last_host[i] < 0:
                    last_host[i] = 255
                    last_host[i-1] -= 1

        first_host_address = '.'.join(map(str, first_host))
        last_host_address = '.'.join(map(str, last_host))

        # 计算子网容量
        host_bits = 32 - int(self.cidr)
        if host_bits == 0:
            total_hosts = 1
            usable_hosts = 1
        elif host_bits == 1:
            total_hosts = 2
            usable_hosts = 0
        else:
            total_hosts = 2 ** host_bits
            usable_hosts = total_hosts - 2  # 减去网络地址和广播地址

        # 判断IP地址类别
        first_octet = ip_octets[0]
        if first_octet < 128:
            ip_class = 'A'
        elif first_octet < 192:
            ip_class = 'B'
        elif first_octet < 224:
            ip_class = 'C'
        elif first_octet < 240:
            ip_class = 'D (组播)'
        else:
            ip_class = 'E (保留)'

        return {
            'ip_address': self.ip,
            'subnet_mask': self.mask,
            'cidr': self.cidr,
            'network_address': network_address,
            'broadcast_address': broadcast_address,
            'first_host': first_host_address,
            'last_host': last_host_address,
            'total_hosts': total_hosts,
            'usable_hosts': usable_hosts,
            'ip_class': ip_class,
            'is_private': self._is_private_ip(ip_octets)
        }

    def _is_private_ip(self, octets: List[int]) -> bool:
        """判断是否是私有IP地址"""
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

    def is_same_subnet(self, other_ip: str) -> Tuple[bool, str]:
        """
        判断另一个IP地址是否在同一个子网

        Args:
            other_ip: 另一个IP地址（可以是带子网掩码的完整形式或仅IP地址）

        Returns:
            Tuple[bool, str]: (是否在同一子网, 提示信息)
        """
        if not self.is_valid:
            return False, f"当前IP地址无效: {self.error_msg}"

        # 提取IP地址部分
        if '/' in other_ip:
            ip_part = other_ip.split('/')[0].strip()
        elif ' ' in other_ip:
            ip_part = other_ip.split()[0].strip()
        else:
            ip_part = other_ip.strip()

        # 验证IP地址
        if not self._validate_ip_address(ip_part):
            return False, f"另一个IP地址无效: {self.error_msg}"

        # 计算网络地址
        current_octets = [int(x) for x in self.ip.split('.')]
        mask_octets = [int(x) for x in self.mask.split('.')]
        other_octets = [int(x) for x in ip_part.split('.')]

        current_network = [current_octets[i] & mask_octets[i] for i in range(4)]
        other_network = [other_octets[i] & mask_octets[i] for i in range(4)]

        if current_network == other_network:
            return True, f"{ip_part} 与 {self.ip} 在同一子网 {self._get_network_address()}"
        else:
            return False, f"{ip_part} 与 {self.ip} 不在同一子网"

    def _get_network_address(self) -> str:
        """获取当前网络地址"""
        ip_octets = [int(x) for x in self.ip.split('.')]
        mask_octets = [int(x) for x in self.mask.split('.')]
        network = [ip_octets[i] & mask_octets[i] for i in range(4)]
        return '.'.join(map(str, network))


def print_network_info(info: Dict):
    """打印网络信息"""
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
    print(f"私有IP:        {'是' if info['is_private'] else '否'}")
    print("="*60)


def main():
    """主函数"""
    print("="*60)
    print("IP地址合法性检测及子网判断程序".center(60))
    print("="*60)
    print("支持两种输入格式:")
    print("1. 点分十进制+子网掩码: 192.168.1.1 255.255.255.0")
    print("2. CIDR形式: 192.168.1.1/24")
    print("输入 'q' 退出程序")

    validator = IPValidator()

    while True:
        try:
            ip_input = input("请输入IP地址: ").strip()

            if ip_input.lower() == 'q':
                print("程序已退出")
                break

            # 验证IP地址
            if validator.validate_ip_input(ip_input):
                print("✓ IP地址格式正确")
                # 显示网络信息
                info = validator.get_network_info()
                print_network_info(info)

                # 判断是否要比较另一个IP
                compare = input("是否要比较另一个IP地址是否在同一子网? (y/n): ").strip().lower()
                if compare == 'y':
                    other_ip = input("请输入另一个IP地址: ").strip()
                    is_same, msg = validator.is_same_subnet(other_ip)
                    print(f"{msg}")
            else:
                print(f"✗ {validator.error_msg}")

            print("" + "-"*60 + "")

        except KeyboardInterrupt:
            print("程序已退出")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    main()
