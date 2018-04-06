import socket
import select
import settings
import collections
import json
import optparse
from jim import JSONRequest, JSONResponse

# Request-объект - используется для преобразования "сырых" данных (байтов) в python-объект
# получаем ip и порт из командной строки, аргументами -i, -p
parser = optparse.OptionParser()

parser.add_option('-a', '--ip', action="store", dest="ip", help="query string", default="127.0.0.1")

parser.add_option('-p', '--port', action="store", dest="port", help="query string", default="7778")

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
                # Сохраняем запрос на сервере
                self._requests.append(j_receive.body)

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
