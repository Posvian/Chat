import subprocess
from ipaddress import ip_address
from subprocess import Popen, PIPE


def host_ping(ip_list):
    res = {'Доступные ip': '', 'Недоступные ip': ''}
    for ip in ip_list:
        try:
            ip = ip_address(ip)
        except ValueError:
            pass

        process = Popen(['ping', str(ip), '-c', '1', '-W' '1'], shell=False, stdout=PIPE)
        process.wait()
        if process.returncode == 0:
            print(f'{ip} - доступен')
            res['Доступные ip'] += f'{str(ip)}\n'
        else:
            print(f'{ip} - недоступен')
            res['Недоступные ip'] += f'{str(ip)}\n'
    return res


if __name__ == '__main__':
    my_ip_list = ['youtube.com', 'google.com', '192.168.0.101']
    host_ping(my_ip_list)


