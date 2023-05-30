# задание 5 (пингую ютуб)
import subprocess

args = ['ping', 'youtube.com']

subproc_args = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in subproc_args.stdout:
    print(line)
    print(line.decode('utf-8'))