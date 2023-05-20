# задание 1
print('TASK 2')

a = 'разработка'
b = 'сокет'
c = 'декоратор'
print(type(a), a)
print(type(b), b)
print(type(c), c)

a_unicode = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
b_unicode = '\u0441\u043e\u043a\u0435\u0442'
c_unicode = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
print(type(a_unicode), a_unicode)
print(type(b_unicode), b_unicode)
print(type(c_unicode), c_unicode)
# Задание 2
print('TASK 2')
my_vars = [b'class', b'function', b'method']
for var in my_vars:
    print(f'Tип: {type(var)}')
    print(f'Cодержимое: {var}')
    print(f'Длина: {len(var)}')

# Задание 3
print('TASK 3')

words = ['attribute', 'класс', 'функция', 'type']
for word in words:
    try:
        print(bytes(word, 'ascii'))
    except UnicodeEncodeError:
        print(f'Слово {word} не записать в байтовом типе')

# задание 4
print('TASK 4')

words = ['разработка', 'администрирование', 'protocol', 'standard']
for word in words:
    a = word.encode()
    print(a)
    b = a.decode()
    print(b)

