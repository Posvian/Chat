import dis


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        attributes = []

        for func in clsdict:
            try:
                result = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in result:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            attributes.append(i.argval)
        print(methods)
        if 'connect' in attributes:
            raise TypeError('Присутствует метод connect. Его использование недопустимо.')
        if not ('SOCK_STREAM' in methods and 'AF_INET' in methods):
            print(attributes)
            raise TypeError('Сокет инициализирован некорректно.')

        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        attributes = []

        for func in clsdict:
            try:
                result = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in result:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            attributes.append(i.argval)

        if 'accept' in methods or 'listen' in methods or 'socket' in methods:
            raise TypeError('Использование методов accept и listen недопустимо.')

        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Сокет инициализирован некорректно.')

        super().__init__(clsname, bases, clsdict)