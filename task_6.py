# Задание 6
from chardet import detect

def encode_convert():
    with open('test_file.txt', 'rb') as f:
        content_bytes = f.read()
    detected = detect(content_bytes)
    print(detected)
    encoding = detected['encoding']
    content_text = content_bytes.decode(encoding)
    with open('test.txt', 'w', encoding='utf-8') as f:
        f.write(content_text)


encode_convert()


with open('test.txt', encoding='utf-8') as f:
    content = f.read()
    print(content)
    