from ipaddress import ip_address
from task_1 import host_ping


def host_range_ping(first_ip_address, counter=5):
    last_octet = int(first_ip_address.split('.')[3])
    if last_octet + counter > 254:
        print(f'Последний октет не может быть больше 254, '
              f'уменьшите counter до {254-last_octet} с данным адресом')
    ip_address_list = [ip_address(first_ip_address)]
    for i in range(1, counter):
        new_ip = first_ip_address[:-1] + str(last_octet + i)
        new_ip = ip_address(new_ip)
        ip_address_list.append(new_ip)
    return host_ping(ip_address_list)


if __name__ == '__main__':
    host_range_ping('192.168.1.7')
