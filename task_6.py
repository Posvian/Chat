# Задание 6
with open('test_file.txt', 'r') as f:
    print(f)

file = open('test_file.txt', 'rb')
for line in file:
    line_decode = line.decode(encoding='utf-8')
    print(line_decode)