"""
Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий
сохранение данных в файле YAML-формата. Для этого:
a. Подготовить данные для записи в виде словаря, в котором первому ключу
соответствует список, второму — целое число, третьему — вложенный словарь, где
значение каждого ключа — это целое число с юникод-символом, отсутствующим в
кодировке ASCII (например, €);
b. Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
При этом обеспечить стилизацию файла с помощью параметра default_flow_style, а
также установить возможность работы с юникодом: allow_unicode = True;
c. Реализовать считывание данных из созданного файла и проверить, совпадают ли они
с исходными.
"""
import yaml
from yaml import SafeLoader

data_to_yaml = {
    'list': [1, 2, 3, 4],
    'number': 5,
    'dict': {
        'one': '1€',
        'two': '2€',
        'three': '3€'
    }
}

with open('file.yaml', 'w') as f:
    yaml.dump(data_to_yaml, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open('file.yaml', 'r') as f:
    content = yaml.load(f, Loader=SafeLoader)
    print(content)

print(data_to_yaml)