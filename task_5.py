# задание 5 (пингую яндекс)
import subprocess

args = ['ping', 'yandex.ru']
subproc_args = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in subproc_args.stdout:
    print(line)
    print(line.decode('utf-8'))
