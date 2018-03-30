import socket
import select
import settings
import collections
import json
import optparse

# Request-объект - используется для преобразования "сырых" данных (байтов) в python-объект


class JSONRequest:

    # Конструктор в качестве аргументов принимает исключительно "сырые" данные
    # Внутри конструктора "сырые" данные преобразуются в словарь
    def __init__(self, message_bytes):

        message_str = message_bytes.decode(settings.ENCODING)

        self._envelope = json.loads(message_str)

    @property
    def action(self):

        # Read only свойство action
        action = self._envelope.get('action')

        return action

    @property
    def headers(self):

        # Read only свойство headers
        # Свойство headers содержит дополнительные данные о запросе, например время его совершения
        headers = self._envelope.get('headers')

        for key, value in headers.items():
            yield key, value

    @property
    def body(self):

        # Read only свойство body
        # Свойство body содержит тело запроса
        body = self._envelope.get('body')

        return body


# Response-объект - используется для приведения python-объекта в байтовый вид (для генерации "сырых" данных)
class JSONResponse:

    # Конструктор в качестве аргументов принимает основные данные об ответе сервера
    def __init__(self, code, action, body, **headers):

        self._headers = headers

        self._action = action

        self._code = code

        self._body = body

    # Метод add_header - используется для добавления дополнительных
    # данных об товете сервера, например времени его совершения
    def add_header(self, key, value):

        self._headers.update({key: value})

    # Метод add_header - используется для удаления дополнительных данных
    #  об товете сервера, если во время его заполнения была допущена ошибка
    def remove_header(self, key):

        del self._headers[key]

    # Метод to_bytes - используется для преобразования данных об ответе сервера в байты
    def to_bytes(self):

        envelope = dict()

        envelope.update({'code': self._code})

        envelope.update({'action': self._action})

        envelope.update({'headers': self._headers})

        envelope.update({'body': self._body})

        data_str = json.dumps(envelope)

        return data_str.encode(settings.ENCODING)


# получаем ip и порт из командной строки, аргументами -i, -p
parser = optparse.OptionParser()

parser.add_option('-a', '--ip', action="store", dest="ip", help="query string", default="127.0.0.1")

parser.add_option('-p', '--port', action="store", dest="port", help="query string", default="7777")

options, args = parser.parse_args()


class EchoServer:

    def __init__(self):

        # Создаем список для хранения клиентских соединений
        self._connections = list()

        # Создаем список для хранения клиентских запросов
        self._requests = collections.deque()

        # Создаем экземпляр сокет соединения
        self._sock = socket.socket()

        # Связываем сокет соединение с хостом и портом сервера 
        self._sock.bind((options.ip, int(options.port)))

        # Ждем обращений клиентов 
        self._sock.listen(settings.CLIENTS_NUM)

        # Отпределяем время ожидания запроса клиента 
        self._sock.settimeout(settings.TIMEOUT)

    def connect(self):
        try:

            # Получаем подключение клиента
            client, address = self._sock.accept()

            # Сохраняем подключение клиента
            self._connections.append(client)

        except OSError:

            # Обрабатываем timeout сервера
            pass

    def read(self, client):
        try:
            # Получаем данные от клиента
            data = client.recv(settings.BUFFER_SIZE)
            # Если полученные данные не являются пустой строкой
            if data:
                j_receive = JSONRequest(data)
                # Приводим полученные данные к строковому виду
                str_data = j_receive.body

                # Сохраняем запрос на сервере
                self._requests.append(str_data)

        except ConnectionResetError:
            # В случае разрыва соединения с клиентом и наличии данного клиента в списке подключений
            if client in self._connections:
                # Удаляем соответствующего клиента из списка подключений
                self._connections.remove(client)

    def write(self, client, str_data):
        try:
            j_response = JSONResponse('code', 'action', str_data)
            # Отправляем данные на клиент
            client.send(j_response.to_bytes())
        except (ConnectionResetError, BrokenPipeError):
            # В случае разрыва соединения с клиентом и наличии данного клиента в списке подключений
            if client in self._connections:
                # Удаляем соответствующего клиента из списка подключений
                self._connections.remove(client)

    def mainloop(self):
        print("waiting for connection")
        try:
            while True:
                # Обрабатываем подключения к серверу
                self.connect()
                for client in self._connections:
                    # Сохраняем запрос клиента к серверу
                    self.read(client)
                    # Если клиентом были отправлены запросы к серверу
                    if self._requests:
                        # Извлекаем первый запрос
                        request = self._requests.popleft()
                        # Отправляем запрос слиенту
                        self.write(client, request)

        except KeyboardInterrupt:

            # Обрабатываем сочетание клавишь Ctrl+C
            pass


if __name__ == '__main__':
    server = EchoServer()

    server.mainloop()
