"""
Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку
определенных данных из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый
«отчетный» файл в формате CSV. Для этого:
a. Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с
данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения
каждого параметра поместить в соответствующий список. Должно получиться четыре
списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же
функции создать главный список для хранения данных отчета — например, main_data
— и поместить в него названия столбцов отчета в виде списка: «Изготовитель
системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data (также для
каждого файла);
b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой
функции реализовать получение данных через вызов функции get_data(), а также
сохранение подготовленных данных в соответствующий CSV-файл;
c. Проверить работу программы через вызов функции write_to_csv().
"""
import csv

from chardet import detect
import re


def get_data(list_of_files):
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = []

    for i in list_of_files:
        with open(i, 'rb') as f:
            content_bytes = f.read()
        detected = detect(content_bytes)
        encoding = detected['encoding']
        content_text = content_bytes.decode(encoding)

        os_prod_list.append(re.findall(r'Изготовитель системы:\s*\S*', content_text)[0].split()[2])

        os_name = re.search(r'Название ОС:(\s*\S{1,}){4}', content_text).group(0).split(':')
        os_name_list.append(os_name[1].lstrip())

        os_code_list.append(re.findall(r'Код продукта:\s*\S*', content_text)[0].split()[2])

        os_type_list.append(re.findall(r'Тип системы:\s*\S*', content_text)[0].split()[2])

    column_names = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(column_names)

    for i in range(0, 3):
        data = [os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]]
        main_data.append(data)
    return main_data


def write_to_csv(list_of_files, link):
    data = get_data(list_of_files)
    with open(link, 'w') as f:
        f_writer = csv.writer(f)
        for row in data:
            f_writer.writerow(row)





if __name__ == '__main__':
    list_of_files = ['info_1.txt', 'info_2.txt', 'info_3.txt']
    write_to_csv(list_of_files, 'my.csv')