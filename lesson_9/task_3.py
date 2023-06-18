from tabulate import tabulate
from task_2 import host_range_ping


def host_range_ping_tab(ip_address):
    res = host_range_ping(ip_address)
    print(tabulate([res], headers='keys', tablefmt='pipe', stralign='center'))


if __name__ == "__main__":
    host_range_ping_tab('192.168.1.7')
